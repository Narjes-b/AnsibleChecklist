import copy
import json

import pytest
import yaml

from ansibleguard.report import llm_explain as llm
from ansibleguard.report.llm_evidence import build_packet
from ansibleguard.report.llm_facts import contradiction, prompt_contract
from ansibleguard.report.llm_suggestions import _TaskDumper
from ansibleguard.symbol_index import build_repository_symbol_index


def packet(tmp_path, source, rule, line, **extra):
    (tmp_path / "tasks.yml").write_text(source)
    return build_packet({"file": "tasks.yml", "line": line, "rule_id": rule, **extra}, source.splitlines(),
                        lambda f: (tmp_path / f).read_text().splitlines(), lambda: build_repository_symbol_index(tmp_path))


def test_nested_sibling_start_is_never_previous_task(tmp_path):
    source = "- name: Wrapper\n  block:\n    - name: Previous\n      ansible.builtin.debug:\n        msg: harmless\n    - name: Actual\n      ansible.builtin.debug:\n        msg: '{{ api_token }}'\n      no_log: false\n"
    current = packet(tmp_path, source, "credential-log-exposure", 6)
    assert current["unit"]["start"] == 6 and "name: Previous" not in current["context"]
    assert current["predicate_check"]["assessment"] == "supported"
    previous = packet(tmp_path, source, "credential-log-exposure", 3)
    assert previous["unit"]["end"] == 5 and "name: Actual" not in previous["context"]


def test_same_line_sibling_tasks_are_unavailable_not_arbitrarily_bound(tmp_path):
    p = packet(tmp_path, "[{debug: {msg: first}}, {debug: {msg: second}}]", "credential-log-exposure", 1)
    assert not p["complete"] and "multiple tasks" in " ".join(p["missing"])


def test_visible_set_fact_has_use_and_definition_citations(tmp_path):
    source = "- name: Define\n  ansible.builtin.set_fact:\n    ServicePort: 8080\n- name: Use\n  ansible.builtin.debug:\n    msg: '{{ ServicePort }}'\n"
    p = packet(tmp_path, source, "unguarded-variable", 6, semantic_subject="variable:ServicePort")
    assert p["condition_hint"] == "unsupported"
    assert {c["line"] for c in p["decisive_citations"]} == {3, 6}
    assert any("HAS an established" in text for text in p["facts"])
    bad = {"summary": "ServicePort has no visible definition.", "reasoning": "No definition exists.", "evidence": p["decisive_citations"]}
    assert "denies" in contradiction(bad, p)


def test_effective_inherited_no_log_is_explicit_and_cited(tmp_path):
    p = packet(tmp_path, "- name: Block\n  no_log: true\n  block:\n    - name: Show\n      ansible.builtin.debug:\n        msg: '{{ service_password }}'\n", "credential-log-exposure", 4)
    assert {2, 6} <= {c["line"] for c in p["decisive_citations"]}
    assert any("Effective no_log is literal true" in f for f in p["facts"])
    assert any("does NOT erase registered" in f for f in p["facts"])
    bad = {"summary": "The task displays a password without effective no_log protection.", "reasoning": "", "evidence": p["decisive_citations"]}
    assert "denies" in contradiction(bad, p)


def test_unknown_tls_summary_cannot_assert_disabled_setting(tmp_path):
    p = packet(tmp_path, "- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: '{{ verify_tls }}'\n", "missing-validate-certs", 3)
    bad = {"summary": "The task disables TLS verification using verify_tls.", "reasoning": "It is unknown.", "evidence": p["decisive_citations"]}
    assert "unknown runtime" in contradiction(bad, p)
    bad["summary"] = p["summary_text"]
    assert contradiction(bad, p) is None


def test_numeric_mode_facts_preserve_yaml_integer_semantics(tmp_path):
    p = packet(tmp_path, "- name: Permissions\n  ansible.builtin.file:\n    path: /srv/x\n    state: directory\n    mode: 2750\n", "insecure-permissions", 5)
    assert any("decimal 2750, octal 5276" in f for f in p["facts"])
    assert p["permissions"][0]["world_writable"]


def test_prompt_contract_retains_decisive_facts_but_omits_opaque_audit_hashes(tmp_path):
    p = packet(tmp_path, "- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: false\n", "missing-validate-certs", 3)
    compact = prompt_contract(p)
    assert compact["summary_text"] == p["summary_text"] and compact["decisive_citations"] == p["decisive_citations"]
    assert "sha256" not in compact and "unit" not in compact


def test_generation_requires_decisive_citations_without_claiming_model_selection(tmp_path):
    p = packet(tmp_path, "- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: false\n", "missing-validate-certs", 3)
    token = llm._CALL_RECORD.set({"evidence_packet": p})
    try:
        schema = llm._request_generation_schema()
    finally:
        llm._CALL_RECORD.reset(token)
    assert schema["properties"]["evidence"]["enum"] == [p["decisive_citations"]]
    assert "backend-selected" in p["citation_policy"]


def test_module_redaction_unknown_does_not_become_decisive_unsupported(tmp_path):
    p = packet(tmp_path, "- name: Custom\n  custom.module:\n    password: '{{ service_password }}'\n", "credential-log-exposure", 1)
    assert not p["complete"] and "redaction" in " ".join(p["missing"])


def test_tag_list_normalization_is_lint_compatible():
    task = [{"name": "Tagged", "ansible.builtin.debug": {"msg": "hello"}, "tags": ["deployment"]}]
    text = yaml.dump(task, Dumper=_TaskDumper, sort_keys=False)
    assert "  tags:\n    - deployment\n" in text
    assert yaml.safe_load(text) == task


def test_scoped_question_does_not_repeat_contradicted_detector_accusation(tmp_path, monkeypatch):
    source = "- name: Protected\n  ansible.builtin.debug:\n    msg: '{{ service_password }}'\n  no_log: true\n"
    (tmp_path / "tasks.yml").write_text(source)
    captured = {}
    def model(host, name, system, user, timeout):
        captured["prompt"] = user
        p = llm._CALL_RECORD.get()["evidence_packet"]
        obj = {"assessment": "unsupported", "actionability": "not-assessed", "evidence": p["decisive_citations"],
               "missing_evidence": [], "summary": p["summary_text"], "reasoning": "It censors task result output.",
               "recommended_fix": None, "fixed_code_snippet": None, "confidence": "high", "limitations": None}
        return json.dumps(obj), .1, None
    monkeypatch.setattr(llm, "_call_ollama", model)
    telemetry = {}
    token = llm._CALL_RECORD.set(telemetry)
    try:
        result = llm.explain_occurrence({"file": "tasks.yml", "line": 3, "rule_id": "credential-log-exposure",
                                        "message": "ACCUSATION_WITHOUT_EFFECTIVE_PROTECTION"}, tmp_path)
    finally:
        llm._CALL_RECORD.reset(token)
    assert result["llm_status"] == "ok"
    assert "ACCUSATION_WITHOUT_EFFECTIVE_PROTECTION" not in captured["prompt"]
    assert telemetry["original_detector_message"] == "ACCUSATION_WITHOUT_EFFECTIVE_PROTECTION"
    assert "What effective output protection" in captured["prompt"]


def test_backend_summary_provenance_is_visible_and_reasoning_stays_ai_labeled(tmp_path):
    p = packet(tmp_path, "- name: Protected\n  ansible.builtin.debug:\n    msg: '{{ service_password }}'\n  no_log: true\n", "credential-log-exposure", 3)
    text = llm.assessment_text({"llm_status": "ok", "llm_assessment": "unsupported", "llm_evidence_packet": p,
                               "llm_explanation": p["summary_text"], "llm_why_in_this_context": "Model rationale remains unverified."})
    assert "Evidence summary (backend-authored)" in text
    assert "AI explanation (unverified): Model rationale" in text

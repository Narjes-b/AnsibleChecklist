import json
import os
from pathlib import Path

import pytest

from ansibleguard.report import llm_explain as llm
from ansibleguard.report.llm_evidence import build_packet
from ansibleguard.report.llm_runtime import source_identity, write_checkpoint, read_checkpoint
from ansibleguard.report.llm_suggestions import validate_suggestion
from ansibleguard.symbol_index import build_repository_symbol_index


def packet(root, source, rule="missing-validate-certs", line=3, **extra):
    (root / "tasks.yml").write_text(source)
    return build_packet({"file": "tasks.yml", "line": line, "rule_id": rule, **extra},
        source.splitlines(), lambda file: (root / file).read_text().splitlines(),
        lambda: build_repository_symbol_index(root))


TLS = "- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: false\n    url: https://example.invalid/a\n    dest: /tmp/a\n    mode: '0644'\n"


def test_complete_task_includes_distant_guard_and_excludes_next_task(tmp_path):
    source = TLS + "    headers:\n" + "".join(f"      x{i}: value\n" for i in range(20)) + "  when: enabled\n- name: Other\n  ansible.builtin.debug:\n    msg: other\n"
    result = packet(tmp_path, source)
    assert "when: enabled" in result["context"] and "name: Other" not in result["context"]
    assert result["complete"] and result["condition_hint"] == "supported"


def test_tls_argument_binding_ignores_same_named_task_variables(tmp_path):
    source = TLS.replace("    validate_certs: false\n", "") + "  vars:\n    validate_certs: false\n"
    result = packet(tmp_path, source)
    assert result["condition_hint"] is None and not result["complete"]


@pytest.mark.parametrize("mode,world,setgid", [("0644", False, False), ("2775", False, True), ("2777", True, True)])
def test_permission_evidence_reports_bits_and_existing_rule_predicate(tmp_path, mode, world, setgid):
    source = f"- name: Manage\n  ansible.builtin.file:\n    path: /srv/shared\n    state: directory\n    group: developers\n    mode: '{mode}'\n"
    result = packet(tmp_path, source, "insecure-permissions", 6)
    assert result["permissions"][0]["world_writable"] is world
    assert result["permissions"][0]["setgid"] is setgid
    assert result["condition_hint"] == ("supported" if world else "unsupported")
    assert result["predicate_check"]["kind"] == "static-permission-policy"
    assert result["contract_version"] == 5


def test_local_predicate_does_not_certify_opaque_logging_or_unsupported_action_shape(tmp_path):
    source = '- name: Display result\n  ansible.builtin.debug:\n    msg: "{{ result.stdout }}"\n  no_log: false\n'
    result = packet(tmp_path, source, "credential-log-exposure", 3)
    assert "predicate_check" not in result  # A previous task could make result sensitive.
    source = "- name: File\n  action:\n    module: ansible.builtin.file\n    path: /tmp/x\n    mode: '0777'\n"
    result = packet(tmp_path, source, "insecure-permissions", 5)
    assert "predicate_check" not in result


def test_direct_logging_check_uses_explicit_inherited_control_and_is_labeled_backend(tmp_path):
    source = '- name: Wrapper\n  no_log: false\n  block:\n    - name: Show\n      ansible.builtin.debug:\n        msg: "{{ api_token }}"\n'
    result = packet(tmp_path, source, "credential-log-exposure", 6)
    assert result["predicate_check"]["assessment"] == "supported"
    text = llm.assessment_text({"llm_status": "ok", "llm_assessment": "supported",
                                "llm_explanation": "The source displays a sensitive-looking name.", "llm_evidence_packet": result})
    assert "backend evidence contract" in text and "AI explanation (unverified)" in text
    assert "AI assessment" not in text


def test_failed_predicate_assembly_never_certifies_lines_omitted_from_the_prompt(tmp_path, monkeypatch):
    from ansibleguard.report import llm_evidence
    (tmp_path / "tasks.yml").write_text(TLS)
    def fail(*args):
        raise ValueError("cannot bind predicate")
    monkeypatch.setattr(llm_evidence, "_verify_local_predicate", fail)
    monkeypatch.setattr(llm, "_call_ollama", lambda *a, **k: pytest.fail("failed packet sent"))
    result = llm.explain_occurrence({"file": "tasks.yml", "line": 3, "rule_id": "insecure-permissions"}, tmp_path)
    assert result["llm_status"] == "insufficient-context"


def test_variable_name_in_plain_text_is_not_a_jinja_reference(tmp_path):
    result = packet(tmp_path, "- name: Mention ServicePort\n  ansible.builtin.debug:\n    msg: ServicePort\n",
                    "unguarded-variable", semantic_subject="variable:ServicePort")
    assert not result["complete"] and "case-sensitive variable reference" in result["missing"][0]


def test_outer_and_inner_guards_are_both_supplied(tmp_path):
    source = "- name: Wrapper\n  when: outer_enabled\n  block:\n    " + "\n    ".join(TLS.splitlines()) + "\n      when: inner_enabled\n"
    result = packet(tmp_path, source, line=4)
    assert "when: outer_enabled" in result["context"] and "when: inner_enabled" in result["context"]


def test_inherited_no_log_and_task_override_use_effective_nearest_setting(tmp_path):
    source = "- hosts: all\n  no_log: true\n  tasks:\n    - name: Secret\n      no_log: false\n      ansible.builtin.debug:\n        msg: '{{ password }}'\n"
    result = packet(tmp_path, source, "credential-log-exposure", 7)
    assert not any(d["relation"] == "inherited-no_log" for d in result["dependencies"])
    assert "no_log: false" in result["context"]
    inherited = packet(tmp_path, source.replace("      no_log: false\n", ""), "credential-log-exposure", 6)
    assert any(d["relation"] == "inherited-no_log" and d["start"] == 2 for d in inherited["dependencies"])


@pytest.mark.parametrize("source", [
    "- name: Duplicate\n  debug: {msg: one, msg: two}\n",
    "- &task {name: Original, debug: {msg: hi}}\n- *task\n",
    "- name: Tagged\n  debug: !unknown payload\n---\n- debug: hi\n",
])
def test_ambiguous_units_retain_missing_evidence(tmp_path, source):
    result = packet(tmp_path, source, line=1)
    assert not result["complete"] and result["missing"]


def test_same_name_in_unrelated_role_does_not_resolve_runtime_input(tmp_path):
    defaults = tmp_path / "roles/other/defaults"
    defaults.mkdir(parents=True)
    (defaults / "main.yml").write_text("ServicePort: 80\n")
    result = packet(tmp_path, '- name: Show\n  ansible.builtin.debug:\n    msg: "{{ ServicePort }}"\n',
                    "unguarded-variable", semantic_subject="variable:serviceport",
                    message="Variable 'ServicePort' is undefined")
    assert result["variable"]["name"] == "ServicePort"
    assert result["variable"]["visibility"] == "none"
    assert result["dependencies"] == [] and not result["complete"]


def test_scoped_defaults_have_exact_key_source_and_do_not_use_other_role(tmp_path):
    for role, value in [("app", 80), ("other", 90)]:
        folder = tmp_path / "roles" / role / "defaults"
        folder.mkdir(parents=True)
        (folder / "main.yml").write_text(f"ServicePort: {value}\n")
    tasks = tmp_path / "roles/app/tasks"
    tasks.mkdir()
    source = '- name: Show\n  ansible.builtin.debug:\n    msg: "{{ ServicePort }}"\n'
    (tasks / "main.yml").write_text(source)
    result = build_packet({"file": "roles/app/tasks/main.yml", "line": 3,
                          "rule_id": "unguarded-variable", "semantic_subject": "variable:ServicePort"},
        source.splitlines(), lambda file: (tmp_path / file).read_text().splitlines(),
        lambda: build_repository_symbol_index(tmp_path))
    assert result["variable"]["visibility"] == "must" and result["complete"]
    assert [d["file"] for d in result["dependencies"]] == ["roles/app/defaults/main.yml"]
    assert "ServicePort: 80" in result["context"] and "ServicePort: 90" not in result["context"]


def response(assessment, **extra):
    context = (llm._CALL_RECORD.get() or {}).get("evidence_packet") or {}
    return json.dumps({"assessment": assessment, "actionability": "not-assessed",
        "evidence": context.get("decisive_citations", [{"file": "tasks.yml", "line": 3}]),
        "missing_evidence": ["runtime input"] if assessment == "insufficient-evidence" else [],
        "summary": context.get("summary_text", "Review supplied facts."), "reasoning": "The source is limited.",
        "recommended_fix": None, "fixed_code_snippet": None,
        "confidence": "low", "limitations": "No deployment context.", **extra})


def test_backend_missing_evidence_rejects_model_false_certainty(tmp_path, monkeypatch):
    source = '- name: Show\n  ansible.builtin.debug:\n    msg: "{{ external_value }}"\n'
    (tmp_path / "tasks.yml").write_text(source)
    monkeypatch.setattr(llm, "_call_ollama", lambda *a, **k: (response("supported"), 0.1, None))
    result = llm.explain_occurrence({"file": "tasks.yml", "line": 3, "rule_id": "unguarded-variable",
                                   "semantic_subject": "variable:external_value"}, tmp_path)
    assert result["llm_status"] == "error" and "required backend evidence" in result["llm_error"]


def test_failed_suggestion_does_not_hide_valid_explanation(tmp_path, monkeypatch):
    (tmp_path / "tasks.yml").write_text(TLS)
    monkeypatch.setattr(llm, "_call_ollama", lambda *a, **k: (response("supported",
        actionability="actionable", recommended_fix="Disable all checks", fixed_code_snippet="broken: ["), 0.1, None))
    result = llm.explain_occurrence({"file": "tasks.yml", "line": 3, "rule_id": "missing-validate-certs"}, tmp_path)
    assert result["llm_status"] == "ok" and result["llm_suggested_fix"] is None
    assert result["llm_suggestion_validation"]["status"] == "withheld"


def test_suggestion_cannot_change_destination_or_drop_guard(tmp_path):
    source = TLS + "  when: enabled\n"
    context = packet(tmp_path, source)
    for replacement in [source.replace("/tmp/a", "/etc/passwd"), source.replace("  when: enabled\n", "")]:
        result = validate_suggestion(context, replacement.replace("validate_certs: false", "validate_certs: true"), source.splitlines())
        assert result["status"] == "withheld" and "only validate_certs" in result["reason"]


def test_valid_suggestion_runs_detector_and_offline_lint_without_editing_source(tmp_path, monkeypatch):
    from ansibleguard.report import llm_suggestions
    source = TLS
    context = packet(tmp_path, source)
    calls = []
    monkeypatch.setattr(llm_suggestions.shutil, "which", lambda name: "/fixture/ansible-lint")
    def run(command, **kwargs):
        calls.append((command, kwargs))
        assert "validate_certs: true" in Path(command[-1]).read_text()
        return type("Result", (), {"returncode": 0})()
    monkeypatch.setattr(llm_suggestions.subprocess, "run", run)
    result = validate_suggestion(context, source.replace("validate_certs: false", "validate_certs: true"), source.splitlines())
    assert result["status"] == "passed" and "targeted-detector-clear" in result["checks"]
    assert "--offline" in calls[0][0] and (tmp_path / "tasks.yml").read_text() == source


def test_source_identity_changes_for_runtime_files_and_ignores_checkpoint_dir(tmp_path):
    (tmp_path / "inventory").write_text("host1")
    checkpoint = tmp_path / "attempts"
    checkpoint.mkdir()
    first = source_identity(tmp_path, checkpoint)
    write_checkpoint(checkpoint, "abc", {"key": "abc", "result": {"llm_status": "ok"}})
    assert source_identity(tmp_path, checkpoint) == first
    assert read_checkpoint(checkpoint, "abc")["key"] == "abc"
    assert (checkpoint / "abc.json").stat().st_mode & 0o777 == 0o600
    (tmp_path / "inventory").write_text("host2")
    assert source_identity(tmp_path, checkpoint) != first


def test_resume_refuses_special_files_and_malformed_cached_results(tmp_path):
    if hasattr(os, "mkfifo"):
        os.mkfifo(tmp_path / "runtime-pipe")
        assert source_identity(tmp_path) is None
    (tmp_path / "bad.json").write_text('{"key":"bad","result":null}')
    assert read_checkpoint(tmp_path, "bad") is None


def test_resume_requires_source_model_prompt_and_occurrence_identity(tmp_path, monkeypatch):
    (tmp_path / "tasks.yml").write_text(TLS)
    checkpoint = tmp_path / "attempts"
    monkeypatch.setattr(llm.llm_runtime, "model_identity", lambda *a, **k: "digest-1")
    calls = []
    monkeypatch.setattr(llm, "explain_occurrence", lambda *a, **k: calls.append(k) or {"llm_status": "ok"})
    def run():
        items = [{"file": "tasks.yml", "line": 3, "rule_id": "missing-validate-certs"}]
        llm.enrich_occurrences_with_explanations(items, tmp_path, actionable_only=False, checkpoint_dir=checkpoint)
        return items[0]
    assert not run()["llm_resumed"]
    assert run()["llm_resumed"] and len(calls) == 1
    (tmp_path / "inventory").write_text("new runtime input")
    assert not run()["llm_resumed"] and len(calls) == 2
    monkeypatch.setattr(llm, "PROMPT_VERSION", "changed")
    assert not run()["llm_resumed"] and len(calls) == 3


def test_deadline_stops_subsequent_model_calls_and_clears_old_fields(tmp_path, monkeypatch):
    now = [0.0]
    monkeypatch.setattr(llm.time, "monotonic", lambda: now[0])
    def explain(*a, **kw):
        now[0] = 10.0
        return {"llm_status": "ok"}
    monkeypatch.setattr(llm, "explain_occurrence", explain)
    items = [{}, {"llm_suggested_fix": "stale"}]
    stats = llm.enrich_occurrences_with_explanations(items, tmp_path, actionable_only=False, budget=1)
    assert stats == {"attempted": 2, "ok": 1, "error": 1}
    assert items[1]["llm_status"] == "budget-exhausted" and "llm_suggested_fix" not in items[1]


def test_prompt_budget_refuses_oversize_without_network(monkeypatch):
    monkeypatch.setattr(llm, "_open_local", lambda *a, **k: pytest.fail("oversize prompt sent"))
    raw, _, error = llm._call_ollama(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, "system", "x" * 8000, 10)
    assert raw is None and "token budget" in error


def test_incomplete_generation_retains_raw_envelope_and_token_counts(monkeypatch):
    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self, limit):
            return json.dumps({"message": {"content": "partial answer"}, "done": True,
                               "done_reason": "length", "prompt_eval_count": 120, "eval_count": 1024}).encode()
    monkeypatch.setattr(llm, "_open_local", lambda *a, **k: Response())
    record = {}
    token = llm._CALL_RECORD.set(record)
    try:
        raw, _, error = llm._call_ollama(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, "system", "source", 5)
    finally:
        llm._CALL_RECORD.reset(token)
    assert raw is None and "incomplete" in error
    assert record["raw_response"] == "partial answer" and record["token_usage"]["eval_count"] == 1024
    assert "partial answer" in record["response_envelope"]


def test_required_missing_evidence_constrains_generation_without_mutating_base_schema(monkeypatch):
    captured = {}
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, limit): return b'{"message":{"content":"{}"},"done":true}'
    def request(req, timeout):
        captured.update(json.loads(req.data))
        return Response()
    monkeypatch.setattr(llm, "_open_local", request)
    record = {"evidence_packet": {"coverage": "specialized", "missing": ["runtime input contract"]}}
    token = llm._CALL_RECORD.set(record)
    try:
        llm._call_ollama(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, "system", "source", 5)
    finally:
        llm._CALL_RECORD.reset(token)
    fields = captured["format"]["properties"]
    assert fields["condition_state"]["enum"] == ["unknown"]
    assert fields["confidence"]["enum"] == ["low"]
    assert fields["fixed_code_snippet"] == {"type": "null"}
    assert "actionable" not in fields["actionability"]["enum"]
    assert llm.GENERATION_SCHEMA["properties"]["assessment"]["enum"] == list(llm.ASSESSMENTS)
    assert record["generation_schema_sha256"]


@pytest.mark.parametrize("assessment", ["supported", "unsupported"])
def test_verified_predicate_generation_is_explicitly_constrained(assessment):
    token = llm._CALL_RECORD.set({"evidence_packet": {"coverage": "specialized", "missing": [],
        "predicate_check": {"status": "verified", "assessment": assessment}}})
    try:
        schema = llm._request_generation_schema()
    finally:
        llm._CALL_RECORD.reset(token)
    assert schema["properties"]["condition_state"]["enum"] == [{v: k for k, v in llm.CONDITION_STATES.items()}[assessment]]
    assert schema["properties"]["missing_evidence"]["maxItems"] == 0
    if assessment == "unsupported":
        assert schema["properties"]["fixed_code_snippet"] == {"type": "null"}

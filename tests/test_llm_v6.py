import copy
import json

import pytest

from ansibleguard.report import llm_explain as llm
from ansibleguard.report.llm_facts import prompt_contract, contradiction, quoted_evidence
from tests.test_llm_v5 import packet
from scripts import requested_repair as requested


def test_permission_prompt_preserves_typed_bits(tmp_path):
    p = packet(tmp_path, "- name: File\n  ansible.builtin.file:\n    path: /srv/x\n    mode: 2750\n", "insecure-permissions", 4)
    value = prompt_contract(p)["parsed_permissions"][0]
    assert value["decimal"] == 2750 and value["octal"] == "5276" and value["world_write"]
    bad = {"summary": p["summary_text"], "reasoning": "The mode uses octal 2750 and is safe.", "evidence": p["decisive_citations"]}
    assert "parsed YAML" in contradiction(bad, p)
    bad["reasoning"] = "The integer is decimal 2750, not octal 2750; the parsed octal value is 5276."
    assert contradiction(bad, p) is None


def test_no_log_absence_is_retained_and_invented_usage_rejected(tmp_path):
    p = packet(tmp_path, "- name: Custom\n  custom.module:\n    password: '{{ service_password }}'\n", "credential-log-exposure", 1)
    assert prompt_contract(p)["output_control"]["state"] == "not-shown"
    bad = {"summary": p["summary_text"], "reasoning": "The backend facts indicate that no_log is used to hide output.", "evidence": p["decisive_citations"]}
    assert "invents" in contradiction(bad, p)
    bad["reasoning"] = "If no_log is used, it hides output; the supplied task does not show this setting."
    assert contradiction(bad, p) is None


def test_missing_mode_citation_carries_exact_complete_leaf(tmp_path):
    text = "- name: Write\n  ansible.builtin.template:\n    src: private.j2\n    dest: /srv/private.key\n- name: Other\n  ansible.builtin.debug:\n    msg: other\n"
    p = packet(tmp_path, text, "insecure-permissions", 1)
    catalog = {(p["file"], i + 1): line for i, line in enumerate(text.splitlines())}
    evidence = quoted_evidence(p["decisive_citations"], catalog, p)
    span = next(e["source_span"] for e in evidence if e.get("source_span"))
    assert span["start"] == 1 and span["end"] == 4
    assert span["quote"] == "\n".join(text.splitlines()[:4])
    assert "Other" not in span["quote"]


def test_scalar_command_cites_sensitive_reference_not_only_block_header(tmp_path):
    text = "- name: Install\n  ansible.builtin.command: >\n    installer\n    --api-key '{{ service_api_key }}'\n"
    p = packet(tmp_path, text, "credential-log-exposure", 1)
    assert 4 in {c["line"] for c in p["decisive_citations"]}


def test_window_request_does_not_require_nonexistent_backend_summary(tmp_path, monkeypatch):
    (tmp_path / "tasks.yml").write_text("- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: true\n")
    captured = {}
    def model(host, name, system, user, timeout):
        captured["system"] = system
        return json.dumps({"assessment": "unsupported", "actionability": "not-assessed", "evidence": [{"file": "tasks.yml", "line": 3}],
            "missing_evidence": [], "summary": "Validation is enabled.", "reasoning": "The literal value is true.",
            "recommended_fix": None, "fixed_code_snippet": None, "confidence": "high", "limitations": None}), .1, None
    monkeypatch.setattr(llm, "_call_ollama", model)
    result = llm.explain_occurrence({"file": "tasks.yml", "line": 3, "rule_id": "missing-validate-certs"}, tmp_path, evidence_mode="window")
    assert result["llm_status"] == "ok"
    assert "Copy summary_text" not in captured["system"] and "No backend" in captured["system"]


class Response:
    def __init__(self, value):
        self.value = json.dumps(value).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def read(self, maximum):
        return self.value[:maximum]


def tls(tmp_path):
    text = "- name: Fetch\n  ansible.builtin.get_url:\n    url: https://example.invalid/a\n    dest: /tmp/a\n    mode: '0644'\n    validate_certs: false\n"
    (tmp_path / "tasks.yml").write_text(text)
    return text, {"file": "tasks.yml", "line": 1, "rule_id": "missing-validate-certs"}


def test_local_requested_generator_sees_before_only_and_returns_actual_model_edit(tmp_path, monkeypatch):
    text, occurrence = tls(tmp_path)
    replacement = text.replace("validate_certs: false", "validate_certs: true")
    seen = {}
    monkeypatch.setattr(llm.llm_runtime, "model_identity", lambda *a, **k: "fixture")
    def open_request(request, timeout):
        payload = json.loads(request.data)
        before = json.loads(payload["messages"][1]["content"])
        assert before["before_task"].count("validate_certs: false") == 1
        assert "replacement_task" not in before and replacement not in payload["messages"][1]["content"]
        seen["payload"] = payload
        return Response({"done": True, "message": {"content": json.dumps({"replacement_task": replacement, "explanation": "Enable certificate checking."})}})
    monkeypatch.setattr(llm, "_open_local", open_request)
    result = requested.propose(tmp_path, occurrence, "enable-tls-verification", caller_intent="Authenticated endpoint required", generator="local-model")
    assert result["status"] == "proposal-ready" and result["snippet"] == replacement
    assert result["origin"].startswith("LLM-generated") and result["applied"] is False
    assert (tmp_path / "tasks.yml").read_text() == text
    assert seen["payload"]["format"]["required"] == ["replacement_task", "explanation"]


def test_local_generator_does_not_call_model_for_unknown_or_correct_source(tmp_path, monkeypatch):
    text, occurrence = tls(tmp_path)
    (tmp_path / "tasks.yml").write_text(text.replace("validate_certs: false", "validate_certs: true"))
    monkeypatch.setattr(requested, "generate_local", lambda *a, **k: pytest.fail("ineligible source reached model"))
    result = requested.propose(tmp_path, occurrence, "enable-tls-verification", caller_intent="fix", generator="local-model")
    assert result["status"] == "withheld"


def test_invalid_generated_edit_is_withheld_without_backend_fallback(tmp_path, monkeypatch):
    text, occurrence = tls(tmp_path)
    wrong = text.replace("/tmp/a", "/tmp/other").replace("validate_certs: false", "validate_certs: true")
    monkeypatch.setattr(requested, "generate_local", lambda *a, **k: ({"replacement_task": wrong, "explanation": "bad"}, {"raw_response": wrong}))
    result = requested.propose(tmp_path, occurrence, "enable-tls-verification", caller_intent="fix", generator="local-model")
    assert result["status"] == "withheld" and not result.get("snippet")
    assert "raw_response" in result["model_attempt"]


def test_source_change_during_generation_invalidates_proposal(tmp_path, monkeypatch):
    text, occurrence = tls(tmp_path)
    def generate(*args, **kwargs):
        (tmp_path / "tasks.yml").write_text(text + "# changed\n")
        return {"replacement_task": text.replace("false", "true"), "explanation": "edit"}, {}
    monkeypatch.setattr(requested, "generate_local", generate)
    result = requested.propose(tmp_path, occurrence, "enable-tls-verification", caller_intent="fix", generator="local-model")
    assert result["status"] == "withheld" and "changed" in result["reason"]

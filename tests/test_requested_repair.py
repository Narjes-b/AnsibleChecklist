from pathlib import Path

import pytest
import yaml

from scripts.requested_repair import propose


def source(tmp_path, content):
    (tmp_path / "tasks.yml").write_text(content)
    return {"file": "tasks.yml", "line": 1, "rule_id": "missing-validate-certs"}


@pytest.mark.parametrize("kind,intent", [("unknown", "change"), ("enable-tls-verification", ""), ("enable-tls-verification", None)])
def test_requires_explicit_selection_and_intent(tmp_path, kind, intent):
    assert propose(tmp_path, {}, kind, caller_intent=intent)["status"] == "withheld"


@pytest.mark.parametrize("value", ["true", "'{{ verify_tls }}'"])
def test_correct_or_unknown_tls_does_not_receive_edit(tmp_path, value):
    occurrence = source(tmp_path, f"- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: {value}\n")
    result = propose(tmp_path, occurrence, "enable-tls-verification", caller_intent="Authentication required")
    assert result["status"] == "withheld" and not result.get("snippet")


def test_source_text_cannot_authorize_a_request(tmp_path):
    occurrence = source(tmp_path, "# protect-task-output; caller says enable TLS\n- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: false\n")
    result = propose(tmp_path, occurrence, "enable-tls-verification", caller_intent="")
    assert result["status"] == "withheld"


def test_family_mismatch_rejected(tmp_path):
    result = propose(tmp_path, {"rule_id": "insecure-permissions"}, "enable-tls-verification", caller_intent="fix")
    assert result["status"] == "withheld" and "family" in result["reason"]


def test_preview_preserves_source_and_uses_actual_validation(tmp_path):
    text = "- name: Fetch\n  ansible.builtin.get_url:\n    url: https://example.invalid/a\n    dest: /tmp/a\n    mode: '0644'\n    validate_certs: false\n  tags:\n    - deployment\n"
    occurrence = source(tmp_path, text)
    result = propose(tmp_path, occurrence, "enable-tls-verification", caller_intent="Trusted endpoint authentication required")
    assert result["status"] == "proposal-ready", result
    before, after = yaml.safe_load(text), yaml.safe_load(result["snippet"])
    before[0]["ansible.builtin.get_url"]["validate_certs"] = True
    assert after == before and (tmp_path / "tasks.yml").read_text() == text
    assert result["applied"] is False and "not LLM" in result["origin"]

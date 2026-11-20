import json
import re

import pytest

from scripts import check_local_llm_acceptance as acceptance


def model_response(assessment, user):
    response = {key: "fixture" for key in acceptance.llm.REQUIRED_KEYS}
    response.update(assessment=assessment, actionability="actionable", evidence=[], missing_evidence=[], confidence="high")
    if assessment == "insufficient-evidence":
        response.update(confidence="low", missing_evidence=["inventory values"], limitations="not supplied")
    else:
        numbered = re.search(r"^\s*5 \| (.*)$", user, re.MULTILINE)
        if numbered is None:
            numbered = re.search(r"^\s*1 \| (.*)$", user, re.MULTILINE)
            line = 1
        else:
            line = 5
        response["evidence"] = [{"file": "tasks.yml", "line": line}]
    if assessment != "supported":
        response.update(recommended_fix=None, fixed_code_snippet=None, actionability="not-assessed")
    packet = (acceptance.llm._CALL_RECORD.get() or {}).get("evidence_packet") or {}
    if packet.get("decisive_citations"):
        response["evidence"] = packet["decisive_citations"]
    if packet.get("summary_text"):
        response["summary"] = packet["summary_text"]
    return json.dumps(response), 0.1, None


def run(tmp_path, **kwargs):
    return acceptance.run_cases(tmp_path / "results", model="fixture", host=acceptance.llm.DEFAULT_HOST,
                                timeout=5, budget=kwargs.pop("budget", 30), model_identity={"digest": "fixture"}, **kwargs)


def test_complete_driver_uses_integrated_contract_and_retains_all_cases(tmp_path, monkeypatch):
    def model(host, name, system, user, timeout):
        if "inventory_service_port" in user:
            assessment = "insufficient-evidence"
        elif "validate_certs: true" in user:
            assessment = "unsupported"
        else:
            assessment = "supported"
        return model_response(assessment, user)

    monkeypatch.setattr(acceptance.llm, "_call_ollama", model)
    records = run(tmp_path)
    assert len(records) == 4 and all(r["contract_expectation_met"] for r in records)
    manifest = json.loads((tmp_path / "results/acceptance-manifest.json").read_text())
    assert manifest["status"] == "completed" and manifest["model_calls"] == 3 and not manifest["pending_case_ids"]
    assert not manifest["eligible_for_performance_scoring"]
    assert len(manifest["output_sha256"]) == 4
    for record in records:
        for call in record["call_records"]:
            assert "expected_assessment" not in call["user_prompt"]


def test_schema_valid_semantic_mismatches_are_recorded_not_hidden(tmp_path, monkeypatch):
    monkeypatch.setattr(acceptance.llm, "_call_ollama", lambda h, m, s, u, t: model_response("supported", u))
    records = run(tmp_path)
    assert len(records) == 4
    assert [r["contract_expectation_met"] for r in records] == [True, False, False, True]
    assert records[1]["result"]["llm_status"] == "error"
    assert "contradicts" in records[1]["result"]["llm_error"]


def test_budget_exhaustion_retains_every_case_without_request(tmp_path, monkeypatch):
    monkeypatch.setattr(acceptance.llm, "_call_ollama", lambda *a, **k: pytest.fail("budget exhausted"))
    records = run(tmp_path, budget=1e-10)
    assert len(records) == 4 and all(r["result"]["llm_status"] == "budget-exhausted" for r in records)
    assert all(r["model_calls"] == 0 for r in records)


def test_interruption_leaves_reviewable_manifest_with_pending_ids(tmp_path, monkeypatch):
    def interrupted(*a, **k):
        raise RuntimeError("fixture interruption")
    monkeypatch.setattr(acceptance.llm, "_call_ollama", interrupted)
    with pytest.raises(RuntimeError, match="fixture interruption"):
        run(tmp_path)
    manifest = json.loads((tmp_path / "results/acceptance-manifest.json").read_text())
    assert manifest["status"] == "interrupted" and manifest["completed_cases"] == 0
    assert manifest["pending_case_ids"] == [case["case_id"] for case in acceptance.CASES]


def test_output_is_not_overwritten_and_nonlocal_endpoint_is_rejected(tmp_path):
    (tmp_path / "results").mkdir()
    with pytest.raises(FileExistsError):
        run(tmp_path)
    with pytest.raises(ValueError, match="local loopback"):
        acceptance.run_cases(tmp_path / "unused", model="fixture", host="https://example.com", timeout=5,
                             budget=30, model_identity={"digest": "fixture"})
    assert not (tmp_path / "unused").exists()

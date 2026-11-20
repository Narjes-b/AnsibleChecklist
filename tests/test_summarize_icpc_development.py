import json

import pytest

from ansibleguard.report.llm_evidence import digest
from scripts.summarize_icpc_development import summarize


def fixture_run(tmp_path):
    manifest = {"development": [{"case_id": "development-fixture", "family": "fixture",
                                "engineering_expectation": "insufficient-evidence"}],
                "evaluation": [{"case_id": "sealed-evaluation"}]}
    manifest["cases_sha256"] = digest([manifest["development"], manifest["evaluation"]])
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(manifest))
    run = tmp_path / "run"
    run.mkdir()
    (run / "run-manifest.json").write_text(json.dumps({"panel": "development", "status": "completed",
        "pending": [], "model_digest": "model", "cases_sha256": manifest["cases_sha256"]}))
    for mode in ("window", "scoped"):
        record = {"case_id": "development-fixture", "mode": mode, "model_digest": "model",
                  "prompt_version": "fixture", "cases_sha256": manifest["cases_sha256"],
                  "raw_response": json.dumps({"assessment": "insufficient-evidence"}),
                  "result": {"llm_status": "error", "llm_error": "citation invalid"}}
        if mode == "scoped":
            record["result"] = {"llm_status": "ok", "llm_assessment": "insufficient-evidence",
                                "llm_evidence_packet": {"coverage": "specialized", "missing": ["runtime input"]}}
        (run / f"development-fixture-{mode}.json").write_text(json.dumps(record))
    return path, run


def test_rejected_answer_stays_in_denominator_and_constrained_abstention_is_separate(tmp_path):
    path, run = fixture_run(tmp_path)
    result = summarize(path, run, tmp_path / "analysis")
    assert result["modes"]["window"]["selected"] == 1
    assert result["modes"]["window"]["raw_expectation_matches"] == 1
    assert result["modes"]["window"]["engineering_expectation_matches"] == 0
    assert result["modes"]["window"]["unanswered"] == 1
    assert result["modes"]["scoped"]["schema_constrained_abstentions"] == 1
    assert result["modes"]["scoped"]["engineering_expectation_matches"] == 1
    assert len(json.loads((tmp_path / "analysis/failures.json").read_text())) == 1


def test_changed_expectation_or_mixed_model_cannot_be_scored_silently(tmp_path):
    path, run = fixture_run(tmp_path)
    original = path.read_text()
    data = json.loads(original)
    data["development"][0]["engineering_expectation"] = "supported"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="checksum"):
        summarize(path, run, tmp_path / "bad")
    path.write_text(original)
    p = run / "development-fixture-scoped.json"
    record = json.loads(p.read_text())
    record["model_digest"] = "different-model"
    p.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="identities"):
        summarize(path, run, tmp_path / "bad-model")


def test_incomplete_or_wrong_panel_is_not_scored(tmp_path):
    path, run = fixture_run(tmp_path)
    p = run / "run-manifest.json"
    data = json.loads(p.read_text())
    for change in ({"status": "in-progress"}, {"panel": "evaluation"}):
        p.write_text(json.dumps({**data, **change}))
        with pytest.raises(ValueError, match="completed development"):
            summarize(path, run, tmp_path / "incomplete")

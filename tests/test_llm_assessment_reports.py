import csv
import json

import pytest

from ansibleguard.report import llm_explain
from ansibleguard.report.csv_writer import write_findings_to_csv
from ansibleguard.report.diff_report import _message_with_llm_suggestion
from ansibleguard.report.occurrences import build_occurrences, occurrence_findings
from ansibleguard.report.output_contract import write_occurrences_csv, write_occurrences_text
from ansibleguard.report.pr_annotations import annotation_command, render_markdown
from ansibleguard.report.sarif_writer import build_sarif
from ansibleguard.report.text_writer import write_findings_to_txt


@pytest.mark.parametrize("assessment", llm_explain.ASSESSMENTS)
def test_assessment_and_evidence_survive_every_reporting_path(tmp_path, assessment):
    occurrence = build_occurrences([{
        "provider": "ansibleguard", "rule_id": "missing-validate-certs", "file": "site.yml", "line": 1,
        "severity": "warning", "message": "Detector claim", "native_rule_id": "missing-validate-certs",
    }])[0]
    fields = {"llm_status": "ok", "llm_response_schema_version": 3, "llm_prompt_version": "local-review-v3",
              "llm_actionability": "actionable" if assessment == "supported" else "not-assessed",
              "llm_assessment": assessment, "llm_evidence": [{"file": "site.yml", "line": 1, "quote": "code"}],
              "llm_missing_evidence": ["role reachability"] if assessment == "insufficient-evidence" else [],
              "llm_citations_checked": True, "llm_explanation": "Evidence-based assessment", "llm_confidence": "low",
              "llm_suggested_fix": "Change configuration" if assessment == "supported" else None,
              "llm_fixed_code_snippet": None, "llm_disclaimer": llm_explain.LLM_DISCLAIMER}
    occurrence.update(fields)
    fields.update({"llm_evidence_packet": {"version": 1, "complete": False},
                   "llm_suggestion_validation": {"status": "not-proposed"},
                   "llm_token_usage": {"prompt_eval_count": 200}, "llm_model_digest": "fixture",
                   "llm_resume_key": "fixture-key", "llm_resumed": False,
                   "llm_explanation_contract": "free-prose", "llm_prose_origin": "Local model, unverified"})
    occurrence.update(fields)
    finding = occurrence_findings([occurrence])[0]
    assert all(finding[field] == fields[field] for field in llm_explain.ASSESSMENT_FIELDS)

    write_findings_to_csv([finding], tmp_path / "findings.csv")
    write_occurrences_csv([occurrence], tmp_path / "occurrences.csv")
    for path in (tmp_path / "findings.csv", tmp_path / "occurrences.csv"):
        with path.open() as stream:
            row = next(csv.DictReader(stream))
        assert row["llm_assessment"] == assessment and row["llm_response_schema_version"] == "3"
        assert json.loads(row["llm_evidence"]) == fields["llm_evidence"]
        assert json.loads(row["llm_missing_evidence"]) == fields["llm_missing_evidence"]

    result = build_sarif([finding], tmp_path)["runs"][0]["results"][0]
    assert all(result["properties"][field] == fields[field] for field in llm_explain.ASSESSMENT_FIELDS)
    assert "fixes" not in result  # Source quote checks never authorize a patch.
    write_findings_to_txt([finding], tmp_path / "findings.txt")
    write_occurrences_text([occurrence], tmp_path / "occurrences.txt")
    rendered = [(tmp_path / "findings.txt").read_text(), (tmp_path / "occurrences.txt").read_text(),
                annotation_command(occurrence), render_markdown([occurrence], 1), _message_with_llm_suggestion(occurrence)]
    for text in rendered:
        assert f"AI assessment (unverified): {assessment}" in text
        assert "Evidence-based assessment" in text and "unverified second opinion" in text
        if assessment == "supported":
            assert "Change configuration" in text
        if assessment == "insufficient-evidence":
            assert "role reachability" in text


@pytest.mark.parametrize("assessment", ["unsupported", "insufficient-evidence"])
def test_rendering_does_not_resurrect_an_old_fix_for_new_abstention(assessment):
    item = {"llm_status": "ok", "llm_assessment": assessment, "llm_explanation": "Unproven claim",
            "llm_suggested_fix": "STALE_EDIT_MUST_NOT_RENDER"}
    text = llm_explain.assessment_text(item)
    assert assessment in text and "STALE_EDIT_MUST_NOT_RENDER" not in text
    assert llm_explain.LLM_DISCLAIMER in text

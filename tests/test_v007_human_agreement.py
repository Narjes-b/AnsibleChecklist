import csv
import json
from pathlib import Path

import pytest

from scripts.v007_human_agreement import (
    ReviewerInputError,
    _agreement_metrics,
    compare_reviewers,
)
from scripts.v007_validation_pilot import (
    MASTER_COLUMNS,
    PILOT_CODEBOOK_INPUTS,
    REVIEWER_COLUMNS,
    REVIEWER_DECISION_COLUMNS,
    REVIEWER_VISIBLE_COLUMNS,
    sha256_bytes,
    sha256_file,
)


def test_nominal_agreement_statistics_match_hand_calculated_example():
    metrics = _agreement_metrics(
        ["positive", "negative", "uncertain", "positive"],
        ["positive", "positive", "uncertain", "negative"],
        ("positive", "negative", "uncertain", "unreviewable"),
    )

    assert metrics["n"] == 4
    assert metrics["raw_agreement"] == 0.5
    assert metrics["cohens_kappa"] == pytest.approx(0.2)
    assert metrics["gwets_ac1"] == pytest.approx(7 / 19)
    assert metrics["category_specific_agreement"]["positive"] == 0.5
    assert metrics["category_specific_agreement"]["negative"] == 0
    assert metrics["category_specific_agreement"]["uncertain"] == 1
    assert metrics["confusion_matrix_reviewer_a_rows_reviewer_b_columns"]["negative"]["positive"] == 1


def test_kappa_is_undefined_but_ac1_handles_unanimous_single_category():
    metrics = _agreement_metrics(["positive"] * 3, ["positive"] * 3, ("positive", "negative"))
    assert metrics["cohens_kappa"] is None
    assert metrics["gwets_ac1"] == 1


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _fixture(tmp_path: Path, *, blank: bool = False):
    validation_dir = tmp_path / "validation"
    codebooks = validation_dir / "codebooks"
    codebooks.mkdir(parents=True)
    (codebooks / "FAMILY_SECURITY.md").write_text(
        "## Reason codes\n\n`safeguard-present`, `other`.\n", encoding="utf-8"
    )
    for relative in PILOT_CODEBOOK_INPUTS:
        path = validation_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("Frozen fixture instruction.\n", encoding="utf-8")
    master = {column: "" for column in MASTER_COLUMNS}
    master.update({
        "sample_id": "V007PILOT-SECURITY-001",
        "occurrence_id": "occurrence-1",
        "review_family": "Security",
        "codebook_path": "codebooks/FAMILY_SECURITY.md",
        "repository": "org/repo",
        "commit_sha": "a" * 40,
        "path": "tasks/main.yml",
        "source_context": "frozen fixture context",
        "context_bundle_path": "samples/agreement-pilot/context/sample.md",
        "is_agreement_pilot": "true",
        "eligible_for_performance_scoring": "false",
    })
    master_path = validation_dir / "master.csv"
    _write_csv(master_path, MASTER_COLUMNS, [master])
    manifest_path = validation_dir / "samples/agreement-pilot/agreement-pilot-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    codebook_hashes = {
        relative: sha256_file(validation_dir / relative)
        for relative in PILOT_CODEBOOK_INPUTS
    }
    manifest_path.write_text(json.dumps({
        "row_count": 1,
        "eligible_for_performance_scoring": False,
        "source_commit": "source-commit",
        "script_commit": "generator-commit",
        "script_sha256": "generator-sha256",
        "inputs": {
            "pilot_codebooks_sha256": codebook_hashes,
            "pilot_codebook_bundle_sha256": sha256_bytes(json.dumps(
                codebook_hashes, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")),
        },
        "files": {"master.csv": {"sha256": sha256_file(master_path)}},
    }), encoding="utf-8")
    reviewer_rows = []
    for _reviewer in ("a", "b"):
        row = {column: master[column] for column in REVIEWER_VISIBLE_COLUMNS}
        row.update({column: "" for column in REVIEWER_DECISION_COLUMNS})
        if not blank:
            row.update({
                "semantic_label": "positive",
                "actionability_label": "actionable",
                "context_sufficient": "yes",
                "requires_external_context": "no",
                "external_context_type": "none",
                "reason_code": "safeguard-present",
                "evidence_notes": "The frozen source supports the rule condition.",
            })
        reviewer_rows.append(row)
    reviewer_a_path = tmp_path / "reviewer-a.csv"
    reviewer_b_path = tmp_path / "reviewer-b.csv"
    _write_csv(reviewer_a_path, REVIEWER_COLUMNS, [reviewer_rows[0]])
    _write_csv(reviewer_b_path, REVIEWER_COLUMNS, [reviewer_rows[1]])
    return validation_dir, master_path, reviewer_a_path, reviewer_b_path


def test_returned_files_are_validated_and_outputs_are_write_once(tmp_path):
    validation_dir, master, reviewer_a, reviewer_b = _fixture(tmp_path)
    before_a = reviewer_a.read_bytes()
    before_b = reviewer_b.read_bytes()
    output_dir = tmp_path / "handoff"

    report = compare_reviewers(validation_dir, master, reviewer_a, reviewer_b, output_dir)

    assert report["row_count"] == 1
    assert report["fields"]["semantic_label"]["cohens_kappa"] is None
    assert report["fields"]["semantic_label"]["gwets_ac1"] == 1
    assert report["any_decision_disagreement_count"] == 0
    assert reviewer_a.read_bytes() == before_a
    assert reviewer_b.read_bytes() == before_b
    assert (output_dir / "results/agreement-summary.json").is_file()
    assert (output_dir / "results/agreement-summary.csv").is_file()
    assert (output_dir / "adjudication/disagreements.csv").is_file()
    assert (output_dir / "HUMAN_AGREEMENT_REPORT.md").is_file()
    with pytest.raises(ReviewerInputError, match="refusing to overwrite"):
        compare_reviewers(validation_dir, master, reviewer_a, reviewer_b, output_dir)


def test_agreement_outputs_include_label_disagreement_for_human_adjudication(tmp_path):
    validation_dir, master, reviewer_a, reviewer_b = _fixture(tmp_path)
    with reviewer_b.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows[0].update({
        "semantic_label": "negative",
        "actionability_label": "not-applicable",
        "context_sufficient": "no",
        "reason_code": "other",
        "evidence_notes": "The required condition is absent.",
    })
    _write_csv(reviewer_b, REVIEWER_COLUMNS, rows)

    output_dir = tmp_path / "analysis"
    report = compare_reviewers(validation_dir, master, reviewer_a, reviewer_b, output_dir)

    assert report["semantic_label_disagreement_count"] == 1
    with (output_dir / "adjudication/disagreements.csv").open(encoding="utf-8", newline="") as stream:
        disagreements = list(csv.DictReader(stream))
    assert len(disagreements) == 1
    assert disagreements[0]["sample_id"] == "V007PILOT-SECURITY-001"
    assert "semantic_label" in disagreements[0]["different_fields"]


def test_blank_or_evidence_modified_reviewer_file_is_rejected(tmp_path):
    validation_dir, master, reviewer_a, reviewer_b = _fixture(tmp_path, blank=True)
    with pytest.raises(ReviewerInputError, match="required decision missing"):
        compare_reviewers(validation_dir, master, reviewer_a, reviewer_b)

    validation_dir, master, reviewer_a, reviewer_b = _fixture(tmp_path / "changed")
    with reviewer_a.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows[0]["path"] = "changed.yml"
    _write_csv(reviewer_a, REVIEWER_COLUMNS, rows)
    with pytest.raises(ReviewerInputError, match="frozen evidence changed"):
        compare_reviewers(validation_dir, master, reviewer_a, reviewer_b)


def test_codebook_changes_after_pilot_freeze_are_rejected(tmp_path):
    validation_dir, master, reviewer_a, reviewer_b = _fixture(tmp_path)
    (validation_dir / "codebooks/FAMILY_SECURITY.md").write_text(
        "## Reason codes\n\n`new-reason`.\n", encoding="utf-8"
    )
    with pytest.raises(ReviewerInputError, match="codebooks or reviewer instructions changed"):
        compare_reviewers(validation_dir, master, reviewer_a, reviewer_b)

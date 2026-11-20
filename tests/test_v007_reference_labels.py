import csv

from scripts import v007_assemble_reference_labels as assemble
from scripts import v007_label_comparison as comparison

REASONS = {"condition-present", "condition-absent"}


def row(**overrides):
    base = {
        "semantic_label": "positive", "actionability_label": "advisory", "context_sufficient": "yes",
        "requires_external_context": "no", "external_context_type": "none", "reason_code": "condition-present",
        "evidence_notes": "line 3", "reviewer_notes": "", "ai_confidence": "high", "bundle_issue": "none",
    }
    base.update(overrides)
    return base


def test_valid_row_has_no_problems():
    assert assemble.problems(row(), REASONS) == []


def test_each_rule_of_the_frozen_validator_is_enforced():
    assert assemble.problems(row(semantic_label="maybe"), REASONS)
    assert any("conflicts" in p for p in assemble.problems(row(semantic_label="negative", actionability_label="advisory"), REASONS))
    assert any("conflicts" in p for p in assemble.problems(row(semantic_label="positive", actionability_label="not-applicable"), REASONS))
    assert any("external_context_type must be" in p for p in assemble.problems(row(external_context_type="role caller"), REASONS))
    assert any("missing" in p for p in assemble.problems(row(requires_external_context="yes", external_context_type="none"), REASONS))
    assert any("evidence_notes" in p for p in assemble.problems(row(evidence_notes=""), REASONS))
    assert any("uncertainty" in p for p in assemble.problems(row(semantic_label="uncertain", actionability_label="uncertain"), REASONS))
    assert any("reason_code" in p for p in assemble.problems(row(reason_code="made-up"), REASONS))
    assert any("ai_confidence" in p for p in assemble.problems(row(ai_confidence="sure"), REASONS))


def test_comparison_reports_perfect_and_partial_agreement(tmp_path):
    def write(path, labels):
        with open(path, "w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["sample_id", "rule_id", "review_family", "semantic_label", "actionability_label", "evidence_notes"])
            for index, label in enumerate(labels):
                writer.writerow([f"S-{index}", "ansibleguard/x", "Security", label, "advisory", "n"])
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    write(a, ["positive", "negative", "positive", "uncertain"])
    write(b, ["positive", "negative", "negative", "uncertain"])
    pairs = [(x["semantic"], y["semantic"]) for x, y in zip(
        comparison.read_labels(a, "").values(), comparison.read_labels(b, "").values())]
    metrics = comparison.metrics(pairs, comparison.SEMANTIC_LABELS)
    assert metrics["raw_agreement"] == 0.75
    assert comparison.metrics([], comparison.SEMANTIC_LABELS) is None

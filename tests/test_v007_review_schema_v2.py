from pathlib import Path

from scripts.v007_review_schema_v2 import (
    COMMON_ACTIONABILITY, COMMON_SEMANTIC, V2_COLUMNS, build_blank, check_row, family_reasons, v2_family_file,
)

ROOT = Path(__file__).resolve().parents[1] / "study/validation-v007-human"


def good_row(**over):
    row = {"semantic_label": "positive", "actionability_label": "actionable", "context_sufficient": "yes",
           "requires_external_context": "no", "external_context_type": "none",
           "semantic_reason": "confirmed-defect", "actionability_reason": "fix-is-proportionate",
           "bundle_issue": "none", "evidence_notes": "line 4", "reviewer_notes": ""}
    row.update(over)
    return row


def reasons():
    return family_reasons(ROOT / "codebooks-v2/FAMILY_SECURITY_V2.md")


def test_good_row_passes():
    assert check_row(good_row(), reasons()) == []


def test_negative_requires_not_applicable_and_negative_reason():
    row = good_row(semantic_label="negative", actionability_label="not-applicable",
                   semantic_reason="safeguard-present", actionability_reason="not-applicable")
    assert check_row(row, reasons()) == []
    assert check_row({**row, "actionability_label": "advisory"}, reasons())
    assert check_row({**row, "semantic_reason": "confirmed-defect"}, reasons())


def test_unreviewable_needs_bundle_issue_and_notes():
    row = good_row(semantic_label="unreviewable", actionability_label="not-applicable",
                   semantic_reason="bundle-defect", actionability_reason="not-applicable")
    problems = check_row(row, reasons())
    assert any("bundle_issue" in p for p in problems) and any("reviewer_notes" in p for p in problems)
    assert check_row({**row, "bundle_issue": "truncated", "reviewer_notes": "listing cut at 120"}, reasons()) == []


def test_external_context_is_controlled():
    assert check_row(good_row(requires_external_context="yes", external_context_type="none"), reasons())
    assert check_row(good_row(requires_external_context="yes", external_context_type="free text"), reasons())
    assert check_row(good_row(requires_external_context="yes", external_context_type="ansible-version"), reasons()) == []


def test_every_family_file_has_all_reason_kinds():
    for path in sorted((ROOT / "codebooks-v2").glob("FAMILY_*_V2.md")):
        found = family_reasons(path)
        assert len(found["positive"]) > len(COMMON_SEMANTIC["positive"]), path.name
        assert found["negative"] - COMMON_SEMANTIC["negative"], path.name
        assert found["uncertain"] - COMMON_SEMANTIC["uncertain"], path.name


def test_common_sets_are_mirrored_in_the_codebook_text():
    text = (ROOT / "codebooks-v2/COMMON_V2.md").read_text(encoding="utf-8")
    for code in set().union(*COMMON_SEMANTIC.values()) | COMMON_ACTIONABILITY:
        assert f"`{code}`" in text, code


def test_build_blank_rewrites_codebook_and_keeps_visible_columns():
    from scripts.v007_validation_pilot import REVIEWER_VISIBLE_COLUMNS
    source = {c: "x" for c in REVIEWER_VISIBLE_COLUMNS}
    source["codebook_path"] = "codebooks/FAMILY_SECURITY.md"
    out = build_blank([source])[0]
    assert out["codebook_path"] == v2_family_file("codebooks/FAMILY_SECURITY.md") == "codebooks-v2/FAMILY_SECURITY_V2.md"
    assert list(out) == V2_COLUMNS and out["semantic_label"] == ""


def test_v2_family_file_is_idempotent():
    once = v2_family_file("codebooks/FAMILY_SECURITY.md")
    assert v2_family_file(once) == once == "codebooks-v2/FAMILY_SECURITY_V2.md"

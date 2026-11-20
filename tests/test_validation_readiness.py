from scripts.audit_validation_readiness import audit_ledger


def test_audit_ledger_separates_occurrence_precision_from_clean_files():
    rows = [
        {
            "project": "one/repo", "validation_unit": "occurrence",
            "reviewer_1_label": "true-positive", "reviewer_2_label": "true-positive",
            "consensus_label": "true-positive",
        },
        {
            "project": "two/repo", "validation_unit": "occurrence",
            "reviewer_1_label": "true-positive", "reviewer_2_label": "false-positive",
            "consensus_label": "false-positive",
        },
        {
            "project": "two/repo", "validation_unit": "clean-file-review",
            "reviewer_1_label": "true-positive", "reviewer_2_label": "true-positive",
            "consensus_label": "true-positive",
        },
    ]
    result = audit_ledger(rows, expected_repositories=3)
    assert result["occurrence_precision_unweighted"] == 0.5
    assert result["exact_reviewer_agreement_count"] == 2
    assert result["pre_reconciliation_disagreement_count"] == 1
    assert result["repositories_represented"] == 2
    assert "sample represents 2 of 3 expected repositories" in result["warnings"]


def test_blank_reviewer_labels_are_not_counted_as_agreement():
    rows = [
        {
            "project": "one/repo",
            "validation_unit": "occurrence",
            "reviewer_1_label": "",
            "reviewer_2_label": "",
            "consensus_label": "true-positive",
        }
    ]

    result = audit_ledger(rows)

    assert result["dual_reviewer_items"] == 0
    assert result["exact_reviewer_agreement_count"] == 0
    assert result["exact_reviewer_agreement_rate"] is None
    assert result["pre_reconciliation_disagreement_count"] == 0
    assert "one or more rows lack two independent reviewer labels" in result["warnings"]

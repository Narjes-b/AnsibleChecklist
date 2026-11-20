from scripts.summarize_fp_mechanisms import summarize


def test_fp_mechanism_summary_prefers_consensus_and_groups_evidence():
    summary = summarize([
        {
            "concept_id": "unguarded-variable", "provider": "ansibleguard",
            "consensus_label": "false-positive",
            "consensus_reason": "dynamic_include",
        },
        {
            "concept_id": "unguarded-variable", "provider": "ansibleguard",
            "adjudicated_label": "false-positive",
            "adjudicated_reason": "dynamic_include",
        },
        {
            "concept_id": "hardcoded-secret", "provider": "gitleaks",
            "consensus_label": "true-positive",
        },
    ])

    assert summary["reviewed_labels"] == 3
    assert summary["false_positives"] == 2
    assert summary["mechanisms"] == {"dynamic_include": 2}
    assert summary["by_concept"]["unguarded-variable"] == {"dynamic_include": 2}

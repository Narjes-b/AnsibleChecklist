from pathlib import Path
from parser_playbook import mainn
from smellsDetector import assess_code_smells, read_thresholds


def test_per_task_counters_accumulate_across_plays_not_reset(fixtures_dir, tmp_path, monkeypatch):
    """Regression test for a bug PROJECT_STATUS.md documented as open:
    large_task / long_task_name / inconsistent_naming_convention were
    claimed to reset to 0 at the top of each play's task loop, so the
    final playbook-level total would only ever reflect the LAST play
    processed, not the sum across all plays.

    This fixture has two separate plays, each with one task that trips
    all three per-task thresholds (LOC_task, task_name_len, special_chars)
    independently. If the bug is real, each final count would be 1
    (only the second play's task survives). If genuinely accumulating
    correctly, each should be 2 (both plays' tasks counted).
    """
    # Isolate this test from real external tools (gitleaks/ansible-lint) —
    # we're testing the aggregation logic here, not those integrations,
    # which already have their own dedicated tests.
    monkeypatch.setattr(
        "smellsDetector.scan_with_gitleaks_file_output", lambda *a, **kw: []
    )
    monkeypatch.setattr("smellsDetector.run_ansible_lint", lambda *a, **kw: [])

    fixture = fixtures_dir / "smells_two_plays_each_over_threshold.yml"
    metrics = mainn(str(fixture))
    thresholds = read_thresholds()

    txt_output = tmp_path / "Play_Level_Analysis.txt"
    result, findings, lint_results = assess_code_smells(metrics, thresholds, txt_output)

    playbook_metrics = result["playbook"]["metrics"]
    assert playbook_metrics["large_task"] == 2, (
        f"Expected 2 (both plays' oversized tasks counted), "
        f"got {playbook_metrics['large_task']} — reset-per-play bug may be real"
    )
    assert playbook_metrics["long_task_name"] == 2, (
        f"Expected 2, got {playbook_metrics['long_task_name']}"
    )
    assert playbook_metrics["inconsistent_naming_convention"] == 2, (
        f"Expected 2, got {playbook_metrics['inconsistent_naming_convention']}"
    )

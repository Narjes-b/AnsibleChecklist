from pathlib import Path


WORKFLOW = Path(".github/workflows/ansibleguard.yml")


def test_pr_workflow_uses_full_history_and_canonical_comparison():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "fetch-depth: 0" in text
    assert "ansibleguard-base/canonical/occurrences.json" in text
    assert "ansibleguard-head/canonical/occurrences.json" in text
    assert "--head-output ansibleguard-head" in text


def test_base_review_range_is_empty_and_comparison_failure_is_enforced_later():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert text.count(
        "ANSIBLEGUARD_BASE_SHA: ${{ github.event.pull_request.base.sha }}"
    ) == 2
    assert "ANSIBLEGUARD_HEAD_SHA: ${{ github.event.pull_request.base.sha }}" in text
    assert "continue-on-error: true" in text
    assert "ansibleguard-pr-decision.json || true" not in text
    assert "pull-request comparison did not produce a decision" in text


def test_pr_workflow_blocks_tool_errors_and_protects_fork_sarif_uploads():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'item["status"] == "tool-error"' in text
    assert "github.event.pull_request.head.repo.full_name == github.repository" in text
    assert "if-no-files-found: error" in text

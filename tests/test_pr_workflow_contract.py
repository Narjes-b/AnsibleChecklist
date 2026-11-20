from pathlib import Path


WORKFLOW = Path(".github/workflows/ansibleguard.yml")


def test_pr_workflow_uses_full_history_and_canonical_comparison():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "fetch-depth: 0" in text
    assert "ref: ${{ github.event.pull_request.head.sha || github.sha }}" in text
    assert "--base-results ansibleguard-base" in text
    assert "--head-results ansibleguard-head" in text
    assert "ansibleguard-head/diff/comparison.json" in text


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

    assert 'item["status"] in {"tool-error", "analysis-error"}' in text
    assert "github.event.pull_request.head.repo.full_name == github.repository" in text
    assert "github.event.repository.private == false" in text
    assert "vars.ANSIBLEGUARD_UPLOAD_SARIF == 'true'" in text
    assert "if-no-files-found: error" in text


def test_sarif_is_optional_and_push_scans_observe_the_existing_baseline():
    text = WORKFLOW.read_text(encoding="utf-8")

    sarif_step = text.split("- name: Upload actionable PR SARIF", 1)[1].split(
        "- name: Upload detailed reports", 1
    )[0]
    assert "continue-on-error: true" in sarif_step
    assert "Push scan completed in observe mode" in text


def test_pr_workflow_publishes_introduced_annotations_and_summary():
    text = WORKFLOW.read_text(encoding="utf-8")

    annotation_step = text.split(
        "- name: Publish introduced PR annotations", 1
    )[1].split("- name: Publish scan summary", 1)[0]
    assert "github.event_name == 'pull_request'" in annotation_step
    assert "hashFiles('ansibleguard-head/diff/comparison.json') != ''" in annotation_step
    assert "ansibleguard-pr-annotations ansibleguard-head/diff/comparison.json" in annotation_step
    assert "--limit 50" in annotation_step
    assert "--summary" not in annotation_step
    assert "ansibleguard-head/summary/run-summary.md" in text


def test_pr_workflow_uses_introduced_sarif_and_cancels_stale_runs():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "cancel-in-progress: true" in text
    assert "ansibleguard-head/diff/introduced-actionable.sarif" in text
    assert "category: ansibleguard-pr-actionable" in text
    assert "category: ansibleguard-full" in text


def test_pr_workflow_uses_supported_node24_actions_and_stable_check_name():
    text = WORKFLOW.read_text(encoding="utf-8")
    ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "name: AnsibleGuard / introduced findings" in text
    assert "actions/checkout@v6" in text
    assert "actions/setup-python@v6" in text
    assert "actions/upload-artifact@v6" in text
    assert "actions/checkout@v4" not in text + ci
    assert "actions/setup-python@v5" not in text + ci
    assert "actions/upload-artifact@v4" not in text + ci


def test_pr_workflow_reports_analysis_policy_and_sarif_status():
    text = WORKFLOW.read_text(encoding="utf-8")

    status_step = text.split(
        "- name: Publish GitHub integration status", 1
    )[1].split("- name: Upload detailed reports", 1)[0]
    assert "| Analysis health |" in status_step
    assert "| PR policy |" in status_step
    assert "| SARIF publication |" in status_step
    assert "artifact only (private repository has not opted into GitHub Code Security)" in status_step
    assert "artifact only (privileged upload is disabled for fork pull requests)" in status_step


def test_pr_summary_links_findings_to_the_exact_head_commit():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "ANSIBLEGUARD_SOURCE_URL:" in text
    assert "/blob/${{ github.event.pull_request.head.sha }}" in text

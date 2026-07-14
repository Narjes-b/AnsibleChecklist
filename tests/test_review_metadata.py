import subprocess

from ansibleguard.detectors.review_metadata import detect_project_review_smells
from ansibleguard.report.findings import build_findings_list


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _init_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "review@example.com")
    _git(repo, "config", "user.name", "Review Test")
    return repo


def test_git_review_metadata_detects_missing_review_artifacts(tmp_path):
    repo = _init_repo(tmp_path)
    _write(
        repo / "roles" / "web" / "defaults" / "main.yml",
        "# Copyright 2025 Example\nweb_port: 8080\n",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Initial role")

    _write(repo / "roles" / "web" / "defaults" / "main.yml", "web_port: 9090\n")
    _git(repo, "add", ".")
    _git(
        repo,
        "commit",
        "-q",
        "-m",
        "fix configuration behavior with a subject that is deliberately too long",
        "-m",
        "Depends-On: malformed-reference",
    )

    metrics = detect_project_review_smells(repo)
    assert metrics["missing_release_notes"] == 1
    assert metrics["missing_bug_references"] == 1
    assert metrics["invalid_depends_on_references"] == 1
    assert metrics["commit_message_format_issues"] == 1
    assert metrics["removed_copyright_notices"] == 1
    assert metrics["missing_test_updates"] == 1
    assert metrics["untested_override_changes"] == 1

    result = {
        "playbook": {
            "metrics": {"WarningUnusedIncludeVars": []},
            "plays": [],
        }
    }
    findings = build_findings_list(metrics, result, [], [], repo)
    rule_ids = {finding["rule_id"] for finding in findings}
    assert "commit-message-format" in rule_ids
    assert "removed-copyright-notice" in rule_ids
    assert any(
        finding["file"] == "roles/web/defaults/main.yml"
        for finding in findings
        if finding["rule_id"] == "removed-copyright-notice"
    )


def test_git_review_metadata_accepts_complete_change(tmp_path):
    repo = _init_repo(tmp_path)
    _write(repo / "roles" / "web" / "defaults" / "main.yml", "web_port: 8080\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Initial role")

    _write(repo / "roles" / "web" / "defaults" / "main.yml", "web_port: 9090\n")
    _write(repo / "tests" / "test_web.yml", "---\nweb_port: 9090\n")
    _write(repo / "releasenotes" / "notes" / "web-port.yml", "---\nfixes: []\n")
    _git(repo, "add", ".")
    _git(
        repo,
        "commit",
        "-q",
        "-m",
        "Fix web port",
        "-m",
        "Closes-Bug: #1234\n\nDepends-On: I0123456789abcdef0123456789abcdef01234567",
    )

    metrics = detect_project_review_smells(repo)
    assert all(
        value == 0 for key, value in metrics.items() if not key.endswith("_details")
    )

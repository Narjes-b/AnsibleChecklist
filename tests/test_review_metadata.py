import subprocess

from ansibleguard.detectors.review_metadata import detect_project_review_smells
from ansibleguard.report.findings import build_findings_list


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _git_output(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


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


def test_git_review_metadata_checks_the_complete_pr_range(tmp_path, monkeypatch):
    repo = _init_repo(tmp_path)
    _write(repo / "README.md", "base\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Initial state")
    base = _git_output(repo, "rev-parse", "HEAD")

    _write(repo / "roles" / "web" / "tasks" / "main.yml", "- debug: msg=hello\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Fix role behavior")
    _write(repo / "README.md", "latest documentation\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Update documentation")
    head = _git_output(repo, "rev-parse", "HEAD")

    monkeypatch.setenv("ANSIBLEGUARD_BASE_SHA", base)
    monkeypatch.setenv("ANSIBLEGUARD_HEAD_SHA", head)
    metrics = detect_project_review_smells(repo)

    assert metrics["missing_release_notes"] == 1
    assert metrics["missing_test_updates"] == 1
    assert metrics["missing_bug_references"] == 1
    assert metrics["missing_bug_references_details"][0]["commit"] != head


def _two_commit_repo(tmp_path):
    repo = _init_repo(tmp_path)
    _write(repo / "roles" / "web" / "defaults" / "main.yml", "web_port: 8080\n")
    _write(repo / "roles" / "db" / "tasks" / "main.yml", "- name: db\n  ansible.builtin.debug:\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Initial roles")
    _write(repo / "roles" / "web" / "defaults" / "main.yml", "web_port: 9090\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "fix web port")
    return repo


def test_shallow_snapshot_does_not_treat_the_whole_tree_as_the_change(tmp_path):
    origin = _two_commit_repo(tmp_path)
    clone = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth=1", f"file://{origin}", str(clone)],
        check=True,
        capture_output=True,
    )
    assert _git_output(clone, "rev-parse", "--is-shallow-repository") == "true"

    metrics = detect_project_review_smells(clone)

    assert metrics["missing_release_notes"] == 0
    assert metrics["missing_test_updates"] == 0
    assert metrics["untested_override_changes"] == 0
    assert metrics["removed_copyright_notices"] == 0
    assert "were not evaluated" in metrics["review_range_unavailable"]
    # Message-only rules still use the exact head commit message.
    assert metrics["missing_bug_references"] == 1


def test_root_commit_keeps_its_full_tree_review_range(tmp_path):
    repo = _init_repo(tmp_path)
    _write(repo / "roles" / "web" / "defaults" / "main.yml", "web_port: 8080\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Initial role")

    metrics = detect_project_review_smells(repo)

    assert "review_range_unavailable" not in metrics
    assert metrics["missing_release_notes"] == 1


def test_ansible_collection_changelog_fragment_is_a_release_note(tmp_path):
    repo = _two_commit_repo(tmp_path)
    _write(repo / "roles" / "web" / "defaults" / "main.yml", "web_port: 7070\n")
    _write(repo / "changelogs" / "fragments" / "web-port.yml", "minor_changes:\n  - web port\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Change web port")

    assert detect_project_review_smells(repo)["missing_release_notes"] == 0


def test_root_changelog_document_is_a_release_note(tmp_path):
    repo = _two_commit_repo(tmp_path)
    _write(repo / "galaxy.yml", "version: 1.0.1\n")
    _write(repo / "CHANGELOG.md", "# 1.0.1\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Release")

    assert detect_project_review_smells(repo)["missing_release_notes"] == 0


def test_yaml_named_changes_is_not_a_release_note(tmp_path):
    repo = _two_commit_repo(tmp_path)
    _write(repo / "roles" / "web" / "vars" / "changes.yml", "web_mode: blue\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Add web mode")

    assert detect_project_review_smells(repo)["missing_release_notes"] == 1


def test_kubernetes_manifest_change_is_not_ansible_configuration(tmp_path):
    repo = _two_commit_repo(tmp_path)
    _write(
        repo / "cluster" / "apps" / "deployment.yaml",
        "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\n",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Add deployment")

    metrics = detect_project_review_smells(repo)

    assert metrics["missing_release_notes"] == 0
    assert metrics["missing_test_updates"] == 0


def test_merge_commit_messages_are_not_judged(tmp_path, monkeypatch):
    repo = _two_commit_repo(tmp_path)
    base = _git_output(repo, "rev-parse", "HEAD")
    _git(repo, "checkout", "-q", "-b", "side")
    _write(repo / "docs" / "notes.txt", "note\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Add notes")
    _git(repo, "checkout", "-q", "-")
    _git(repo, "merge", "-q", "--no-ff", "side", "-m",
         "Merge branch 'side' of https://example.invalid/a/very/long/remote/path into main")
    monkeypatch.setenv("ANSIBLEGUARD_BASE_SHA", base)

    assert detect_project_review_smells(repo)["commit_message_format_issues"] == 0


def test_other_tool_yaml_is_not_ansible_configuration(tmp_path):
    repo = _two_commit_repo(tmp_path)
    _write(repo / "kubernetes" / "emqx" / "kustomizeconfig.yaml", "nameReference:\n  - kind: Secret\n")
    _write(repo / "docker-compose.yml", "services:\n  web:\n    image: nginx\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Tweak deployment tooling")

    metrics = detect_project_review_smells(repo)

    assert metrics["missing_release_notes"] == 0
    assert metrics["missing_test_updates"] == 0

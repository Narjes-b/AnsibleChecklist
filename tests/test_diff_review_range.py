"""``ansibleguard diff`` reviews exactly the base..head range."""

import json
import subprocess

import pytest

from ansibleguard.cli import _diff_main


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _items(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else payload.get("items", [])


@pytest.mark.parametrize("parallel", [False, True])
def test_local_diff_reviews_whole_pr_range_and_not_the_base(tmp_path, parallel):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
    _write(repo / "roles/web/defaults/main.yml", "---\nweb_port: 8080\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Initial role")
    _git(repo, "checkout", "-q", "-b", "feature")
    _write(repo / "roles/web/defaults/main.yml", "---\nweb_port: 9090\n")
    _git(repo, "commit", "-qam", "Change port")
    # The last commit only adds a changelog fragment; the PR range as a whole
    # still changes defaults without a test.
    _write(repo / "changelogs/fragments/port.yml", "minor_changes:\n  - port\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Add changelog fragment")
    output = tmp_path / "out"

    args = [str(repo), "--base", "main", "--head", "feature", "--profile", "review-range",
            "--policy", "observe", "-o", str(output)]
    if parallel:
        args.append("--parallel-base-head")
    try:
        _diff_main(args)
    except SystemExit as exc:
        assert exc.code in (0, None)

    head_rules = {item["rule_id"] for item in _items(output / "head/findings.json")}
    assert "untested-override-change" in head_rules
    assert "missing-test-update" in head_rules
    assert "missing-release-note" not in head_rules
    assert all(
        "changelogs/" not in str(item.get("file", ""))
        for item in _items(output / "head/findings.json")
    )
    # The base side is not a review range of its own.
    assert _items(output / "base/findings.json") == []
    assert _items(output / "diff/fixed.json") == []

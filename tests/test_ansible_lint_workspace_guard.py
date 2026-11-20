"""ansible-lint must never modify the tree it scans."""

import shutil
import subprocess
from pathlib import Path

import pytest

from ansibleguard.external.ansible_lint import (
    _restore_workspace,
    _snapshot_workspace,
    scan_with_ansible_lint,
)

FLOW_SEQUENCE = """---
- name: Healthcheck
  hosts: all
  tasks:
    - name: Show test
      ansible.builtin.debug:
        msg:
          [
            CMD,
            wget,
            -O,
          ]
"""


def test_snapshot_restores_rewritten_yaml_and_removes_lint_artifacts(tmp_path):
    playbook = tmp_path / "site.yml"
    playbook.write_text(FLOW_SEQUENCE, encoding="utf-8")
    (tmp_path / "keep_cache" / "__pycache__").mkdir(parents=True)
    backup = tmp_path.parent / f"{tmp_path.name}-backup"
    backup.mkdir()
    snapshot, existing = _snapshot_workspace(tmp_path, backup)

    playbook.write_text("rewritten: true\n", encoding="utf-8")
    (tmp_path / ".ansible" / "collections").mkdir(parents=True)
    (tmp_path / "library" / "__pycache__").mkdir(parents=True)
    (tmp_path / "site.tmp.yml").write_text("x: 1\n", encoding="utf-8")

    record = _restore_workspace(tmp_path, snapshot, existing)

    assert playbook.read_text(encoding="utf-8") == FLOW_SEQUENCE
    assert record["restored_files"] == ["site.yml"]
    assert record["removed_artifacts"] == [".ansible/", "library/__pycache__/", "site.tmp.yml"]
    assert (tmp_path / "keep_cache" / "__pycache__").is_dir()


@pytest.mark.slow
@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_project_write_list_does_not_modify_scanned_repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".ansible-lint.yml").write_text("write_list:\n  - all\n", encoding="utf-8")
    (repo / "site.yml").write_text(FLOW_SEQUENCE, encoding="utf-8")
    for args in (["init", "-q"], ["add", "."],
                 ["-c", "user.email=t@example.invalid", "-c", "user.name=t", "commit", "-qm", "init"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)

    result = scan_with_ansible_lint(repo)

    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
        check=True, capture_output=True, text=True,
    ).stdout
    assert status == "", status
    assert Path(repo / "site.yml").read_text(encoding="utf-8") == FLOW_SEQUENCE
    assert "workspace_guard" in result.metadata


def test_new_files_inside_preexisting_lint_cache_are_removed(tmp_path):
    kept = tmp_path / ".ansible" / "roles" / "kept.yml"
    kept.parent.mkdir(parents=True)
    kept.write_text("kept: true\n", encoding="utf-8")
    backup = tmp_path.parent / f"{tmp_path.name}-backup"
    backup.mkdir()
    snapshot, existing = _snapshot_workspace(tmp_path, backup)

    new_module = tmp_path / ".ansible" / "collections" / "ns" / "plugins" / "x.py"
    new_module.parent.mkdir(parents=True)
    new_module.write_text("x = 1\n", encoding="utf-8")
    (tmp_path / ".ansible" / "roles" / "new.txt").write_text("n\n", encoding="utf-8")

    record = _restore_workspace(tmp_path, snapshot, existing)

    assert kept.read_text(encoding="utf-8") == "kept: true\n"
    assert not (tmp_path / ".ansible" / "collections").exists()
    assert not (tmp_path / ".ansible" / "roles" / "new.txt").exists()
    assert ".ansible/collections/" in record["removed_artifacts"]

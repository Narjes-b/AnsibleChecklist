"""Tests for clone_study_repositories.py's failed-clone cleanup.

Previously, a failed `git clone` had no cleanup path at all -- the
partial destination directory was left behind, and a subsequent retry
would fail with "destination exists and is not an empty directory"
instead of actually retrying. This matters once collection runs at
real scale, where some clones (large/oddly-structured repositories)
are expected to fail occasionally.
"""
from pathlib import Path
import subprocess

import pytest

from scripts.clone_study_repositories import _clone_or_update


def test_failed_clone_removes_partial_destination(tmp_path, monkeypatch):
    row = {"project": "example/repo", "opendev_url": "https://example.invalid/repo.git"}
    repos_dir = tmp_path / "repositories"

    def fake_run(args, cwd=None):
        # Simulate git creating a partial directory before failing --
        # this is what a real MAX_PATH failure leaves behind.
        destination = Path(args[-1])
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "partial_file.txt").write_text("incomplete", encoding="utf-8")
        raise subprocess.CalledProcessError(returncode=128, cmd=args)

    monkeypatch.setattr("scripts.clone_study_repositories._run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        _clone_or_update(row, repos_dir)

    destination = repos_dir / "example" / "repo"
    assert not destination.exists(), "partial clone directory should be removed on failure"


def test_clone_passes_longpaths_override(tmp_path, monkeypatch):
    row = {"project": "example/repo", "opendev_url": "https://example.invalid/repo.git"}
    repos_dir = tmp_path / "repositories"
    captured = {}

    def fake_run(args, cwd=None):
        captured["args"] = args
        return ""

    monkeypatch.setattr("scripts.clone_study_repositories._run", fake_run)
    _clone_or_update(row, repos_dir)
    assert "-c" in captured["args"]
    assert "core.longpaths=true" in captured["args"]

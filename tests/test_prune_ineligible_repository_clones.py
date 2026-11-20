"""Tests for deleting local clones of repositories that failed final selection."""
from pathlib import Path

from scripts.prune_ineligible_repository_clones import find_prunable, prune


def _make_repo(tmp_path, name):
    path = tmp_path / name
    path.mkdir()
    (path / "file.txt").write_bytes(b"x" * 1024)
    return path


def test_find_prunable_only_matches_collected_and_disqualified(tmp_path):
    ineligible = _make_repo(tmp_path, "ineligible")
    eligible = _make_repo(tmp_path, "eligible")
    pending = _make_repo(tmp_path, "pending")
    rows = [
        {"project": "org/ineligible", "status": "collected", "final_eligible": "false",
         "repository_path": str(ineligible)},
        {"project": "org/eligible", "status": "collected", "final_eligible": "true",
         "repository_path": str(eligible)},
        {"project": "org/pending", "status": "collected", "final_eligible": "not-evaluated",
         "repository_path": str(pending)},
        {"project": "org/never-cloned", "status": "failed", "final_eligible": "false",
         "repository_path": ""},
    ]

    prunable = find_prunable(rows)

    assert [row["project"] for row in prunable] == ["org/ineligible"]


def test_prune_removes_disqualified_clones_and_reports_freed_space(tmp_path):
    ineligible = _make_repo(tmp_path, "ineligible")
    eligible = _make_repo(tmp_path, "eligible")
    rows = [
        {"project": "org/ineligible", "status": "collected", "final_eligible": "false",
         "repository_path": str(ineligible)},
        {"project": "org/eligible", "status": "collected", "final_eligible": "true",
         "repository_path": str(eligible)},
    ]

    removed, freed_bytes = prune(rows)

    assert removed == ["org/ineligible"]
    assert freed_bytes >= 1024
    assert not ineligible.exists()
    assert eligible.exists()


def test_prune_dry_run_reports_without_deleting(tmp_path):
    ineligible = _make_repo(tmp_path, "ineligible")
    rows = [
        {"project": "org/ineligible", "status": "collected", "final_eligible": "false",
         "repository_path": str(ineligible)},
    ]

    removed, freed_bytes = prune(rows, dry_run=True)

    assert removed == ["org/ineligible"]
    assert freed_bytes >= 1024
    assert ineligible.exists()

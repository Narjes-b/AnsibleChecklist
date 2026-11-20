from __future__ import annotations

from pathlib import Path
import subprocess

from scripts import fetch_v007_review_history_parents as recovery


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_parent_parser_reads_the_exact_first_parent(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Validation Test")
    _git(repo, "config", "user.email", "validation@example.invalid")
    first_file = repo / "sample.txt"
    first_file.write_text("first\n", encoding="utf-8")
    _git(repo, "add", "sample.txt")
    _git(repo, "commit", "-q", "-m", "first")
    first = _git(repo, "rev-parse", "HEAD")
    first_file.write_text("second\n", encoding="utf-8")
    _git(repo, "commit", "-qam", "second")
    second = _git(repo, "rev-parse", "HEAD")

    assert recovery._parent_from_commit(repo, second) == first


def test_fetch_configuration_is_exact_sha_shallow_and_tree_filtered() -> None:
    assert recovery.FETCH_ARGS == (
        "fetch",
        "--no-tags",
        "--no-write-fetch-head",
        "--deepen=1",
        "--filter=tree:0",
    )
    assert "--unshallow" not in recovery.FETCH_ARGS
    assert "--all" not in recovery.FETCH_ARGS


def test_existing_parent_is_recorded_without_network_access(tmp_path: Path) -> None:
    result = recovery.fetch_one(
        {
            "repository": "example/repo",
            "repo_path": str(tmp_path),
            "target_commit": "a" * 40,
            "first_parent_commit": "b" * 40,
            "diff_required_occurrences": 2,
            "object_present_before_execution": True,
            "first_parent_resolves_before_execution": True,
        },
        execute=True,
    )

    assert result["fetch_status"] == "already-connected"
    assert result["verified"] is True
    assert result["refs_unchanged"] is True
    assert result["worktree_unchanged"] is True


def test_markdown_dry_run_is_not_reported_as_a_failure() -> None:
    report = {
        "execute": False,
        "counts": {
            "calibration_review_history_occurrences": 335,
            "missing_first_parent_occurrences": 299,
            "missing_diff_required_occurrences": 196,
            "diff_required_occurrences": 196,
            "unique_calibration_target_commits": 1,
            "parent_objects_present_before_execution": 0,
            "parent_objects_missing_before_execution": 1,
            "target_parent_links_resolving_before_execution": 0,
            "repositories_needing_one_commit_deepen": 1,
        },
        "results": [
            {
                "repository": "example/repo",
                "target_commit": "a" * 40,
                "first_parent_commit": "b" * 40,
                "diff_required_occurrences": 1,
                "object_present_before_execution": False,
                "first_parent_resolves_before_execution": False,
                "fetch_status": "dry-run-planned",
                "verified": False,
                "refs_unchanged": None,
                "worktree_unchanged": None,
            }
        ],
    }

    rendered = recovery._render_markdown(report)
    assert "Execution: **DRY RUN**" in rendered
    assert "Result: **PASS**" in rendered

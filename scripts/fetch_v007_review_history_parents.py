#!/usr/bin/env python3
"""Fetch only missing first-parent commit objects for calibration history candidates.

The fetch uses an exact parent SHA, a depth-one request, and ``tree:0`` filtering.
It does not fetch branches, tags, working-tree files, or repository clones. By
default this command is a dry run; pass ``--execute`` to fetch the planned
objects. It operates only on the frozen calibration split.
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
from typing import Any

from scripts import v007_validation_pilot as pilot


EXPECTED_DIFF_REQUIRED_OCCURRENCES = 218
FETCH_ARGS = ("fetch", "--no-tags", "--no-write-fetch-head", "--deepen=1", "--filter=tree:0")
AUDIT_BASENAME = "review-history-first-parent-fetch-audit"


def _run_git(repo_path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo_path}: {result.stderr[:400]}")
    return result


def _parent_from_commit(repo_path: Path, commit_sha: str) -> str:
    raw = _run_git(repo_path, "cat-file", "-p", commit_sha).stdout
    parents = [line.split(" ", 1)[1] for line in raw.splitlines() if line.startswith("parent ")]
    if not parents:
        raise RuntimeError(f"target commit is a root commit and has no first parent: {commit_sha}")
    return parents[0]


def discover_targets(root: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    validation_dir = root / "study/validation-v007-human"
    run_dir = root / "study/runs/v007-full-repro-2026"
    split_rows = {
        row["repository"]: row
        for row in pilot._read_csv(validation_dir / "splits/repository-split.csv")
    }
    acquisition = {
        row["project"]: row
        for row in pilot._read_csv(run_dir / "status/acquisition.csv")
    }
    snapshot_index = {
        row["repository"]: row["canonical_occurrences"]
        for row in pilot._read_csv(run_dir / "raw/raw-output-index.csv")
    }
    result = pilot.load_review_candidates(root, split_rows, acquisition, snapshot_index)
    source_by_rule = result[1]
    missing_by_rule = result[2]
    required_by_rule = result[3]
    source_by_rule_repository = result[4]
    diff_required_by_repository: dict[str, int] = {}
    for (rule_id, repository), count in source_by_rule_repository.items():
        if rule_id not in pilot.REVIEW_MESSAGE_ONLY_RULE_IDS:
            diff_required_by_repository[repository] = diff_required_by_repository.get(repository, 0) + count
    source_count = sum(source_by_rule.values())
    missing_count = sum(missing_by_rule.values())
    required_missing_count = sum(required_by_rule.values())
    diff_required_count = sum(diff_required_by_repository.values())
    if diff_required_count != EXPECTED_DIFF_REQUIRED_OCCURRENCES:
        raise RuntimeError(
            "frozen calibration review-history population changed: "
            f"diff-required occurrences={diff_required_count}"
        )

    targets: list[dict[str, Any]] = []
    for repository, occurrence_count in sorted(diff_required_by_repository.items()):
        split_row = split_rows[repository]
        if split_row.get("split") != "calibration":
            raise RuntimeError(f"refusing to fetch non-calibration repository: {repository}")
        repo_path = pilot._repo_path(root, acquisition[repository])
        target_sha = split_row["commit_sha"]
        parent_sha = _parent_from_commit(repo_path, target_sha)
        remotes = _run_git(repo_path, "remote").stdout.split()
        if "origin" not in remotes:
            raise RuntimeError(f"missing origin remote for calibration repository {repository}")
        present = _run_git(repo_path, "cat-file", "-e", f"{parent_sha}^{{commit}}", check=False).returncode == 0
        resolved = _run_git(repo_path, "rev-parse", "--verify", f"{target_sha}^1", check=False)
        link_resolves = resolved.returncode == 0 and resolved.stdout.strip() == parent_sha
        refs_before = _run_git(repo_path, "for-each-ref", "--format=%(refname) %(objectname)").stdout
        worktree_before = _run_git(repo_path, "status", "--porcelain").stdout
        targets.append(
            {
                "repository": repository,
                "repo_path": str(repo_path),
                "target_commit": target_sha,
                "first_parent_commit": parent_sha,
                "diff_required_occurrences": occurrence_count,
                "object_present_before_execution": present,
                "first_parent_resolves_before_execution": link_resolves,
                "refs_before": refs_before,
                "worktree_before": worktree_before,
            }
        )
    counts = {
        "calibration_review_history_occurrences": source_count,
        "missing_first_parent_occurrences": missing_count,
        "diff_required_occurrences": diff_required_count,
        "missing_diff_required_occurrences": required_missing_count,
        "unique_calibration_target_commits": len(targets),
        "parent_objects_present_before_execution": sum(t["object_present_before_execution"] for t in targets),
        "parent_objects_missing_before_execution": sum(not t["object_present_before_execution"] for t in targets),
        "target_parent_links_resolving_before_execution": sum(t["first_parent_resolves_before_execution"] for t in targets),
        "repositories_needing_one_commit_deepen": sum(not t["first_parent_resolves_before_execution"] for t in targets),
    }
    return targets, counts


def fetch_one(target: dict[str, Any], execute: bool) -> dict[str, Any]:
    repo_path = Path(target["repo_path"])
    parent_sha = target["first_parent_commit"]
    output = {
        key: target[key]
        for key in (
            "repository",
            "target_commit",
            "first_parent_commit",
            "diff_required_occurrences",
            "object_present_before_execution",
            "first_parent_resolves_before_execution",
        )
    }
    if target["first_parent_resolves_before_execution"]:
        output.update(fetch_status="already-connected", verified=True, refs_unchanged=True, worktree_unchanged=True)
        return output
    if not execute:
        output.update(fetch_status="dry-run-planned", verified=False, refs_unchanged=None, worktree_unchanged=None)
        return output

    args = (*FETCH_ARGS, "origin", target["target_commit"])
    fetched = _run_git(repo_path, *args, check=False)
    output["fetch_status"] = "fetch-failed" if fetched.returncode else "fetched"
    if fetched.returncode:
        output["error"] = fetched.stderr.strip()[:500]
        output.update(verified=False, refs_unchanged=None, worktree_unchanged=None)
        return output
    if "filtering not recognized" in fetched.stderr.lower() or "filtering not recognized" in fetched.stdout.lower():
        output["fetch_status"] = "fetch-filter-not-honored"
        output["error"] = "remote did not confirm support for the requested object filter"
        output.update(verified=False, refs_unchanged=None, worktree_unchanged=None)
        return output

    object_type = _run_git(repo_path, "cat-file", "-t", parent_sha, check=False)
    parent_raw = _run_git(repo_path, "cat-file", "-p", target["target_commit"]).stdout
    target_parent = next(
        (line.split(" ", 1)[1] for line in parent_raw.splitlines() if line.startswith("parent ")),
        "",
    )
    resolved_parent = _run_git(repo_path, "rev-parse", "--verify", f"{target['target_commit']}^1", check=False)
    parent_link_resolves = resolved_parent.returncode == 0 and resolved_parent.stdout.strip() == parent_sha
    refs_after = _run_git(repo_path, "for-each-ref", "--format=%(refname) %(objectname)").stdout
    worktree_after = _run_git(repo_path, "status", "--porcelain").stdout
    refs_unchanged = refs_after == target["refs_before"]
    worktree_unchanged = worktree_after == target["worktree_before"]
    verified = (
        object_type.returncode == 0
        and object_type.stdout.strip() == "commit"
        and target_parent == parent_sha
        and parent_link_resolves
    )
    if target["object_present_before_execution"] and parent_link_resolves:
        output["fetch_status"] = "connected-existing-object"
    output.update(
        verified=verified,
        fetched_object_type=object_type.stdout.strip() if object_type.returncode == 0 else "missing",
        target_first_parent_matches=target_parent == parent_sha,
        target_parent_link_resolves=parent_link_resolves,
        refs_unchanged=refs_unchanged,
        worktree_unchanged=worktree_unchanged,
    )
    if not verified or not refs_unchanged or not worktree_unchanged:
        output["fetch_status"] = "verification-failed"
    return output


def _render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    rows = report["results"]
    fetched = sum(row["fetch_status"] == "fetched" and row.get("verified") for row in rows)
    existing_connected = sum(row["fetch_status"] == "connected-existing-object" for row in rows)
    present = sum(row["fetch_status"] == "already-connected" for row in rows)
    failed = [row for row in rows if not row.get("verified") and row["fetch_status"] != "dry-run-planned"]
    lines = [
        "# Calibration review-history first-parent fetch audit",
        "",
        f"Execution: **{'FETCH' if report['execute'] else 'DRY RUN'}**",
        f"Result: **{'PASS' if not failed and (not report['execute'] or fetched + existing_connected + present == len(rows)) else 'INCOMPLETE'}**",
        "",
        "Only exact first-parent links for repositories in the frozen calibration split are considered. Fetches deepen the exact target commit by one parent with `--no-tags --no-write-fetch-head --deepen=1 --filter=tree:0`; no branch or tag ref is fetched or updated. Git receives the missing first-parent commit and minimal tree support objects, not a repository snapshot or file blobs.",
        "",
        "## Population",
        "",
        f"- Calibration review/history source occurrences: {counts['calibration_review_history_occurrences']}",
        f"- Missing-parent occurrences: {counts['missing_first_parent_occurrences']}",
        f"- Total diff-required occurrences: {counts['diff_required_occurrences']}",
        f"- Diff-required occurrences still excluded by a missing parent: {counts['missing_diff_required_occurrences']}",
        f"- Unique target commits in calibration repos: {counts['unique_calibration_target_commits']}",
        f"- Parent objects present before this execution: {counts['parent_objects_present_before_execution']}",
        f"- Parent objects missing before this execution: {counts['parent_objects_missing_before_execution']}",
        f"- Parent links already resolvable before this execution: {counts['target_parent_links_resolving_before_execution']}",
        f"- Repositories needing one-commit deepen: {counts['repositories_needing_one_commit_deepen']}",
        f"- Missing parent commit objects fetched and verified in this execution: {fetched}",
        f"- Existing parent objects connected by updating only the one-parent shallow boundary: {existing_connected}",
        f"- Already connected before execution: {present}",
        f"- Failed/verification issues: {len(failed)}",
        "",
        "## Per-commit results",
        "",
        "| Repository | Target commit | First parent | Required findings | Parent object present | Link resolved before | Status | Verified | Refs unchanged | Worktree unchanged |",
        "|---|---|---|---:|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['repository']}` | `{row['target_commit']}` | `{row['first_parent_commit']}` | "
            f"{row['diff_required_occurrences']} | {row['object_present_before_execution']} | "
            f"{row['first_parent_resolves_before_execution']} | {row['fetch_status']} | {row.get('verified')} | "
            f"{row.get('refs_unchanged')} | {row.get('worktree_unchanged')} |"
        )
    lines.extend(["", "The source pilot templates and contexts are not modified by this fetch. A refreshed pilot must be generated as a new version if these newly available diff candidates are admitted.", ""])
    return "\n".join(lines)


def write_report(output_dir: Path, report: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{AUDIT_BASENAME}.json"
    md_path = output_dir / f"{AUDIT_BASENAME}.md"
    csv_path = output_dir / f"{AUDIT_BASENAME}.csv"
    outputs = {
        json_path: json.dumps(report, indent=2, sort_keys=True) + "\n",
        md_path: _render_markdown(report),
    }
    columns = [
        "repository", "target_commit", "first_parent_commit", "diff_required_occurrences",
        "object_present_before_execution", "first_parent_resolves_before_execution", "fetch_status",
        "verified", "fetched_object_type", "target_first_parent_matches", "target_parent_link_resolves",
        "refs_unchanged", "worktree_unchanged", "error",
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(report["results"])
    outputs[csv_path] = buffer.getvalue()
    for path, content in outputs.items():
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise FileExistsError(f"refusing to overwrite changed audit output: {path}")
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--validation-dir", type=Path, default=Path("study/validation-v007-human"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--execute", action="store_true", help="perform the exact-SHA filtered fetches")
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 4:
        parser.error("workers must be between 1 and 4")
    root = args.root.resolve()
    validation_dir = args.validation_dir if args.validation_dir.is_absolute() else root / args.validation_dir
    targets, counts = discover_targets(root)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(fetch_one, target, args.execute) for target in targets]
        results = [future.result() for future in as_completed(futures)]
    results.sort(key=lambda row: row["repository"])
    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "execute": args.execute,
        "workers": args.workers,
        "fetch_arguments": list(FETCH_ARGS),
        "counts": counts,
        "results": results,
    }
    write_report(validation_dir, report)
    failed = [
        row for row in results
        if args.execute and row.get("fetch_status") not in {"fetched", "connected-existing-object", "already-connected"}
    ]
    print(
        f"mode={'FETCH' if args.execute else 'DRY-RUN'} targets={len(targets)} "
        f"present={counts['parent_objects_present_before_execution']} "
        f"missing={counts['parent_objects_missing_before_execution']} "
        f"fetched={sum(row['fetch_status']=='fetched' and row.get('verified') for row in results)} "
        f"failed={len(failed)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

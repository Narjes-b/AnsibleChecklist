#!/usr/bin/env python3
"""Replay real merged pull requests through ``ansibleguard diff`` and export CSVs.

Each selected pull request is a first-parent merge commit ``M`` of a
calibration-split repository with full local history: base = ``M^1``,
head = ``M``. Repositories are cloned into a scratch work directory, so the
source clones are never modified. Heldout repositories are never opened.

Outputs (in ``--output-dir``):

- ``prs.csv``: one row per replayed pull request (status, counts, runtime).
- ``introduced.csv`` / ``fixed.csv``: one row per introduced / fixed finding.
- ``review.csv``: Git review-rule findings over the PR range (``review-range``).
- ``selection.csv``: every repository considered and why it was or was not used.
- ``README.md``: how the data was produced.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import json
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ANSIBLE_PATH_HINTS = ("roles/", "tasks/", "handlers/", "playbook", "defaults/", "vars/", "site.y", "ansible")


def load_frozen_pull_requests(path: Path, root: Path) -> tuple[list[dict], list[dict]]:
    """Replay exact historical pairs without selecting a newer merge."""
    with (root / "study/validation-v007-human/splits/repository-split.csv").open(encoding="utf-8") as stream:
        split = {row["repository"]: row["split"] for row in csv.DictReader(stream)}
    with path.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    selected, ledger, seen = [], [], set()
    for row in rows:
        repository = row.get("repository", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or any(
                part in {".", ".."} for part in repository.split("/")):
            raise ValueError("unsafe repository in frozen PR manifest")
        if split.get(repository) != "calibration":
            raise ValueError(f"frozen PR is outside calibration split: {repository}")
        if repository in seen:
            raise ValueError(f"duplicate repository in frozen PR manifest: {repository}")
        seen.add(repository)
        for key in ("merge_sha", "base_sha"):
            if not re.fullmatch(r"[a-f0-9]{40}", row.get(key, "")):
                raise ValueError(f"frozen PR requires a full immutable {key}")
        selected.append({key: row[key] for key in ("repository", "merge_sha", "base_sha", "files_changed", "ansible_yaml_changed")})
        ledger.append({"repository": repository, "split": "calibration", "decision": "selected",
                       "reason": f"frozen pair {row['base_sha']}..{row['merge_sha']}"})
    if not selected:
        raise ValueError("frozen PR manifest is empty")
    return selected, ledger


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, errors="replace")
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {result.stderr[:300]}")
    return result.stdout


def _is_ansible_yaml(path: str) -> bool:
    lower = path.lower()
    return lower.endswith((".yml", ".yaml")) and any(hint in lower for hint in ANSIBLE_PATH_HINTS)


def select_pull_requests(root: Path, max_prs: int, max_files: int, scan_merges: int) -> tuple[list[dict], list[dict]]:
    split = {
        row["repository"]: row["split"]
        for row in csv.DictReader(open(root / "study/validation-v007-human/splits/repository-split.csv", encoding="utf-8"))
    }
    clones = root / "study/repositories"
    selected, ledger = [], []
    for repository in sorted(split):
        entry = {"repository": repository, "split": split[repository], "decision": "", "reason": ""}
        ledger.append(entry)
        if split[repository] != "calibration":
            entry.update(decision="excluded", reason="heldout split (never opened)")
            continue
        repo = clones / repository
        if not (repo / ".git").exists():
            entry.update(decision="excluded", reason="no local clone")
            continue
        if _git(repo, "rev-parse", "--is-shallow-repository", check=False).strip() != "false":
            entry.update(decision="excluded", reason="shallow clone (no PR history)")
            continue
        merges = _git(repo, "log", "--merges", "--first-parent", f"-n{scan_merges}", "--format=%H", check=False).split()
        for merge in merges:
            names = _git(repo, "diff", "--name-only", f"{merge}^1", merge, check=False).splitlines()
            ansible = [name for name in names if _is_ansible_yaml(name)]
            if 1 <= len(ansible) <= max_files:
                selected.append({
                    "repository": repository,
                    "merge_sha": merge,
                    "files_changed": len(names),
                    "ansible_yaml_changed": len(ansible),
                })
                entry.update(decision="selected", reason=f"merge {merge[:12]} changes {len(ansible)} Ansible YAML file(s)")
                break
        else:
            entry.update(decision="excluded", reason=f"no recent merge with 1..{max_files} Ansible YAML changes")
        if len(selected) >= max_prs:
            break
    return selected, ledger


def _items(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, list) else payload.get("items", [])


def replay(pr: dict, root: Path, work: Path, timeout: int) -> dict:
    slug = pr["repository"].replace("/", "__")
    target = work / slug
    target.mkdir(parents=True, exist_ok=False)
    clone = target / "repo"
    subprocess.run(["git", "clone", "-q", str(root / "study/repositories" / pr["repository"]), str(clone)], check=True)
    _git(clone, "branch", "-f", "pr-head", pr["merge_sha"])
    base = pr.get("base_sha") or _git(clone, "rev-parse", f"{pr['merge_sha']}^1").strip()
    if _git(clone, "rev-parse", f"{pr['merge_sha']}^1").strip() != base:
        raise ValueError("frozen base is not the recorded merge's first parent")
    _git(clone, "branch", "-f", "pr-base", base)
    result = {**pr, "base_sha": _git(clone, "rev-parse", "pr-base").strip(), "work_dir": str(target)}
    for profile in ("pr", "review-range"):
        out = target / profile
        started = time.monotonic()
        try:
            run = subprocess.run(
                [sys.executable, "-m", "ansibleguard.cli", "diff", str(clone), "--base", "pr-base",
                 "--head", "pr-head", "--profile", profile, "--policy", "ratchet", "-o", str(out)],
                capture_output=True, text=True, errors="replace", timeout=timeout,
            )
            code, err = run.returncode, run.stderr[-400:]
        except subprocess.TimeoutExpired:
            code, err = "timeout", f"exceeded {timeout} s"
        result[f"{profile}_exit"] = code
        result[f"{profile}_seconds"] = round(time.monotonic() - started, 1)
        if code not in (0, 1):
            result[f"{profile}_error"] = " ".join(line for line in err.splitlines() if "Error" in line)[:300] or err[-300:]
    result["clone_clean_after"] = _git(clone, "status", "--porcelain").strip() == ""
    result["leftover_worktrees"] = len(_git(clone, "worktree", "list").splitlines()) - 1
    return result


def _finding_row(pr: dict, item: dict, kind: str) -> dict:
    return {
        "repository": pr["repository"], "merge_sha": pr["merge_sha"], "kind": kind,
        "rule_id": (item.get("native_rules") or [item.get("concept_id")])[0],
        "concept_id": item.get("concept_id"), "provider": item.get("canonical_provider"),
        "severity": item.get("severity"), "policy": item.get("policy"),
        "file": item.get("file"), "line": item.get("line"),
        "on_changed_line": item.get("on_changed_line"), "in_changed_file": item.get("in_changed_file"),
        "message": str(item.get("message", "")).replace("\n", " ")[:300],
    }


def collect(results: list[dict], output_dir: Path) -> None:
    prs, introduced, fixed, review = [], [], [], []
    for pr in results:
        work = Path(pr["work_dir"])
        row = {k: v for k, v in pr.items() if k != "work_dir"}
        comparison_path = work / "pr" / "diff" / "comparison.json"
        if comparison_path.is_file():
            payload = json.loads(comparison_path.read_text(encoding="utf-8"))
            comparison, policy = payload["comparison"], payload["policy"]
            row.update({f"count_{k}": v for k, v in policy.get("counts", {}).items()})
            row["policy_conclusion"] = policy.get("conclusion")
            row["excluded_providers"] = ";".join(comparison.get("snapshot_compatibility", {}).get("excluded_providers", []))
            introduced += [_finding_row(pr, item, "introduced") for item in comparison.get("introduced", [])]
            fixed += [_finding_row(pr, item, "fixed") for item in comparison.get("fixed", [])]
        for item in _items(work / "review-range" / "head" / "findings.json"):
            review.append({
                "repository": pr["repository"], "merge_sha": pr["merge_sha"], "rule_id": item.get("rule_id"),
                "file": item.get("file"), "line": item.get("line"),
                "message": str(item.get("message", "")).replace("\n", " ")[:300],
            })
        prs.append(row)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("prs", prs), ("introduced", introduced), ("fixed", fixed), ("review", review)):
        columns = sorted({key for row in rows for key in row}) if rows else ["repository"]
        if name == "prs":
            first = ["repository", "merge_sha", "base_sha", "files_changed", "ansible_yaml_changed", "pr_exit",
                     "policy_conclusion", "excluded_providers", "count_introduced", "count_introduced_actionable",
                     "count_fixed", "count_unchanged", "count_moved", "count_uncertain", "pr_seconds",
                     "review-range_exit", "clone_clean_after", "leftover_worktrees"]
            columns = [c for c in first if c in columns] + [c for c in columns if c not in first]
        with open(output_dir / f"{name}.csv", "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--work-dir", type=Path, required=True, help="scratch directory for clones and raw outputs")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-prs", type=int, default=25)
    parser.add_argument("--max-files", type=int, default=10)
    parser.add_argument("--scan-merges", type=int, default=60)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=1500)
    parser.add_argument("--prs-manifest", type=Path, help="Frozen prs.csv with exact base/head SHAs; bypass merge selection")
    args = parser.parse_args()
    root = args.root.resolve()
    selected, ledger = (load_frozen_pull_requests(args.prs_manifest, root) if args.prs_manifest else
                        select_pull_requests(root, args.max_prs, args.max_files, args.scan_merges))
    args.output_dir.mkdir(parents=True, exist_ok=False)
    provenance = {"tool_git_sha": _git(root, "rev-parse", "HEAD").strip(),
                  "working_tree_dirty": bool(_git(root, "status", "--porcelain").strip()),
                  "python": sys.version, "manifest": str(args.prs_manifest) if args.prs_manifest else None,
                  "manifest_sha256": hashlib.sha256(args.prs_manifest.read_bytes()).hexdigest() if args.prs_manifest else None,
                  "pairs": selected}
    provenance["implementation_sha256"] = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for directory in (root / "src", root / "scripts") for path in sorted(directory.rglob("*.py"))
    }
    (args.output_dir / "replay-manifest.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    with open(args.output_dir / "selection.csv", "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["repository", "split", "decision", "reason"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(ledger)
    print(f"selected {len(selected)} pull requests", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(replay, pr, root, args.work_dir, args.timeout): pr for pr in selected}
        for future in as_completed(futures):
            pr = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # recorded, never hidden
                results.append({**pr, "pr_exit": "harness-error", "pr_error": str(exc)[:300], "work_dir": str(args.work_dir / "missing")})
            print(f"done {pr['repository']}: pr_exit={results[-1].get('pr_exit')}", flush=True)
    results.sort(key=lambda row: row["repository"])
    collect(results, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check whether PR-replay introduced/fixed findings are supported by the diff.

For each row of ``introduced.csv`` and ``fixed.csv`` produced by
``scripts/pr_replay_study.py``, the real ``pr-base..pr-head`` diff of the
replayed clone is consulted:

- introduced: the file was added, the finding line was added or rewritten,
  some line of the finding's task changed, or the rule is an aggregate metric
  of a changed file;
- fixed: the file was deleted, the base line was deleted or rewritten, some
  line of the finding's base task changed, or the rule is an aggregate metric
  of a changed file.

Rows without such support are flagged for manual review. Writes
``attribution-check.csv`` next to the inputs.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from pathlib import Path
import subprocess
import sys
import tempfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ansibleguard.detectors.shell_instead_of_module import _collect_all_tasks
from ansibleguard.detectors.source_lines import load_with_lines, source_line
from ansibleguard.diff_workflow import parse_changed_lines, parse_line_maps
from ansibleguard.report.comparison import map_base_line

AGGREGATE_RULES = {
    "large-task", "large-play", "large-playbook", "complex-playbook", "missing-abstraction",
    "insufficient-modularization", "high-coupling", "duplicated-code", "excessive-nesting",
}


class Replay:
    def __init__(self, work_dir: Path, repository: str) -> None:
        self.clone = work_dir / repository.replace("/", "__") / "repo"
        forward = self._git("diff", "--unified=0", "--no-ext-diff", "-M", "pr-base", "pr-head")
        backward = self._git("diff", "--unified=0", "--no-ext-diff", "-M", "pr-head", "pr-base")
        self.line_maps = parse_line_maps(forward)
        self.added = parse_changed_lines(forward)
        self.removed = parse_changed_lines(backward)
        self.status = {
            line.split("\t")[-1]: line.split("\t")[0]
            for line in self._git("diff", "--name-status", "-M", "pr-base", "pr-head").splitlines()
        }

    def _git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.clone), *args], capture_output=True, text=True, errors="replace"
        ).stdout

    def task_lines(self, revision: str, path: str, line: int) -> set[int]:
        text = self._git("show", f"{revision}:{path}")
        if not text:
            return {line}
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as handle:
            handle.write(text)
        document = load_with_lines(handle.name)
        Path(handle.name).unlink(missing_ok=True)
        starts = sorted({source_line(task) for task in (_collect_all_tasks(document) if document else [])})
        starts.append(len(text.splitlines()) + 1)
        for begin, end in zip(starts, starts[1:]):
            if begin <= line < end:
                return set(range(begin, end))
        return {line}


def check(row: dict, kind: str, replay: Replay) -> tuple[bool, str]:
    path, line = row["file"], int(row["line"] or 1)
    rule = row["rule_id"].split("/")[-1]
    status = replay.status.get(path, "")
    if kind == "introduced":
        changed = replay.added.get(path, set())
        if status.startswith("A"):
            return True, "file added by the PR"
        if line in changed:
            return True, "finding line added/rewritten"
        if replay.task_lines("pr-head", path, line) & changed:
            return True, "task content changed"
    else:
        changed = replay.removed.get(path, set())
        if status.startswith("D"):
            return True, "file deleted by the PR"
        if map_base_line(replay.line_maps, path, line) is None:
            return True, "finding line deleted/rewritten"
        if replay.task_lines("pr-base", path, line) & changed:
            return True, "task content changed"
    if rule in AGGREGATE_RULES and changed:
        return True, "aggregate metric of a changed file"
    return False, "no change in the finding line or task"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--study-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    replays: dict[str, Replay] = {}
    rows = []
    for kind in ("introduced", "fixed"):
        with open(args.study_dir / f"{kind}.csv", newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                replay = replays.setdefault(row["repository"], Replay(args.work_dir, row["repository"]))
                supported, evidence = check(row, kind, replay)
                rows.append({
                    "kind": kind,
                    **{key: row[key] for key in ("repository", "merge_sha", "rule_id", "severity", "policy", "file", "line", "message")},
                    "attribution_supported": supported,
                    "evidence": evidence,
                })
    columns = ["kind", "repository", "merge_sha", "rule_id", "severity", "policy", "file", "line",
               "message", "attribution_supported", "evidence"]
    with open(args.study_dir / "attribution-check.csv", "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(Counter((row["kind"], row["attribution_supported"]) for row in rows))
    for row in rows:
        if not row["attribution_supported"]:
            print("CHECK", row["kind"], row["repository"], row["rule_id"], row["file"], row["line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

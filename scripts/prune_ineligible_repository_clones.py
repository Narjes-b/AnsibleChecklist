#!/usr/bin/env python3
"""Delete local clones of repositories that failed final selection.

Cloning happens before final eligibility is known (production-Ansible
content confirmation only happens post-clone), so the disk footprint grows
to cover every screening candidate before shrinking back down to the
repositories the study actually keeps. This script does that shrink: given
the final selection CSV, it removes the on-disk clone for every row that was
actually cloned (status=collected) but did not pass final selection
(final_eligible=false). Rows still pending (final_eligible=not-evaluated)
are left alone -- deleting on uncertain data would be irreversible for no
good reason.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import shutil

try:
    from scripts.clone_study_repositories import _force_remove_readonly
except ModuleNotFoundError:  # Direct execution: python scripts/<this-file>.py
    from clone_study_repositories import _force_remove_readonly  # type: ignore[no-redef]


def _dir_size(path):
    total = 0
    for entry in Path(path).rglob("*"):
        if entry.is_file():
            try:
                total += entry.stat().st_size
            except OSError:
                pass
    return total


def find_prunable(rows):
    return [
        row
        for row in rows
        if row.get("status") == "collected"
        and row.get("final_eligible") == "false"
        and row.get("repository_path")
        and Path(row["repository_path"]).is_dir()
    ]


def prune(rows, *, dry_run=False):
    removed = []
    freed_bytes = 0
    for row in find_prunable(rows):
        path = Path(row["repository_path"])
        size = _dir_size(path)
        print(f"{'[dry-run] would remove' if dry_run else 'removing'} "
              f"{row['project']} ({size / 1_048_576:.1f} MiB): {path}")
        if not dry_run:
            shutil.rmtree(path, onerror=_force_remove_readonly)
        removed.append(row["project"])
        freed_bytes += size
    return removed, freed_bytes


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Delete local clones of repositories that failed final selection."
    )
    parser.add_argument("final_selection", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    with args.final_selection.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    removed, freed_bytes = prune(rows, dry_run=args.dry_run)
    verb = "Would free" if args.dry_run else "Freed"
    print(f"{verb} {freed_bytes / 1_073_741_824:.2f} GiB across {len(removed)} disqualified repositories")


if __name__ == "__main__":
    main()

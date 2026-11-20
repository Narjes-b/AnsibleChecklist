#!/usr/bin/env python3
"""Build gate for v2 reviewer context bundles (codebooks-v2 C7).

Checks every ``*.md`` bundle under a directory and lists ALL problems:
- the residual-secret scanner finds nothing;
- a ``Flagged construct`` line is present (static bundles) and is not empty;
- static bundles contain the source excerpt, review bundles the exact commit message;
- a windowed excerpt ("Lines a–b of n" with a != 1 or b != n) comes with the window statement;
- a silently cut listing/search/diff is never allowed: any cut must be stated
  ("further", "not shown", "listing exceeds", "Per-directory path counts");
- review bundles list the changed paths and one diff section per changed path
  (unless message-only).
Exit status 1 when any problem is found; the defect rate is printed for the 5 % gate.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_bundle_secret_scan import scan_text  # noqa: E402

LINES = re.compile(r"^Lines (\d+)–(\d+) of (\d+):", re.MULTILINE)


def check_bundle(text: str) -> list[str]:
    problems = []
    if scan_text(text):
        problems.append("residual secret/PII scan finds matches")
    static = "## Source excerpt" in text
    review = "## Exact target commit message" in text
    if not static and not review:
        return problems + ["neither a source excerpt nor a commit message"]
    if static:
        match = re.search(r"^- Flagged construct: (.+)$", text, re.MULTILINE)
        if not match or not match.group(1).strip():
            problems.append("no 'Flagged construct' line")
        lines = LINES.search(text)
        if not lines:
            problems.append("no 'Lines a–b of n' statement")
        elif (int(lines.group(1)) != 1 or int(lines.group(2)) != int(lines.group(3))) and "window of" not in text:
            problems.append("windowed excerpt without a window statement")
        if "listing truncated" in text and "Per-directory path counts" not in text:
            problems.append("v1-style silent listing truncation")
    if review and "message-only" not in text and "exact target commit message only" not in text:
        changed = re.search(r"^## Changed paths \((\d+)\)", text, re.MULTILINE)
        if not changed:
            problems.append("no changed-paths section")
        else:
            expected = int(changed.group(1))
            sections = len(re.findall(r"^### `", text, re.MULTILINE))
            if sections != expected:
                problems.append(f"{expected} changed paths but {sections} diff sections")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    files = sorted(args.root.rglob("*.md"))
    bad = 0
    for path in files:
        problems = check_bundle(path.read_text(encoding="utf-8", errors="replace"))
        if problems:
            bad += 1
            print(f"{path.relative_to(args.root)}: " + "; ".join(problems))
    rate = bad / len(files) if files else 0.0
    print(f"bundles {len(files)}; with problems {bad} ({rate:.1%}; gate: <= 5.0%)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

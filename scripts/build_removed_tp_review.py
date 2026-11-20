#!/usr/bin/env python3
"""Build the complete source-backed review set for removed historical TPs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


PRIORITY = {
    "unstructured-module": "critical",
    "undocumented-complex-task": "high",
    "complex-playbook": "high",
    "variable-use-before-definition": "high",
    "unnecessary-set-fact": "high",
    "invalid-task-attribute-type": "high",
    "incomplete-task": "high",
    "high-coupling": "medium",
    "unused-include-vars": "medium",
    "incohesive-play": "medium",
    "incohesive-playbook": "medium",
}

RATIONALE = {
    "unstructured-module": "0.0.4 narrowed the rule to missing tasks/main.yml; preserve the old TP as a regression case.",
    "undocumented-complex-task": "0.0.4 introduced stricter complexity thresholds; the historical TP may now fall below them.",
    "complex-playbook": "The historical TP disappeared after complexity/structure definition changes.",
    "unnecessary-abstraction": "The historical TP disappeared after abstraction-scope changes.",
    "unnecessary-set-fact": "Cross-file use analysis or occurrence granularity removed the historical TP.",
    "invalid-task-attribute-type": "0.0.4 permits Jinja values that may resolve to the expected runtime type.",
    "incomplete-task": "0.0.4 excludes TODO/FIXME-only comments and uses executable task content.",
    "high-coupling": "0.0.4 excludes import-only dispatcher files from coupling findings.",
    "unused-include-vars": "0.0.4 searches broader source scope for indirect/cross-file uses.",
    "incohesive-play": "0.0.4 uses a substantially stricter multi-domain cohesion gate.",
    "incohesive-playbook": "0.0.4 requires multiple plays to satisfy the stricter cohesion gate.",
    "duplicate-task-names": "The historical TP must remain available for name-normalization regression review.",
}


def source_context(path: Path, line: int, radius: int = 3) -> str:
    if not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(0, line - radius - 1)
    end = min(len(lines), line + radius)
    return "\\n".join(f"{index + 1}: {lines[index]}" for index in range(start, end))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--paired", type=Path, required=True)
    parser.add_argument("--repositories", type=Path, default=Path("study/repositories"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    rows = []
    with args.paired.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["status"] != "fixed" or row["old_consensus_label"] != "true-positive":
                continue
            source = args.repositories / row["project"] / row["file"]
            line = int(row["line"] or 1)
            rows.append(
                {
                    "project": row["project"],
                    "file": row["file"],
                    "line": line,
                    "concept_id": row["concept_id"],
                    "base_occurrence_id": row["base_occurrence_id"],
                    "old_consensus_label": row["old_consensus_label"],
                    "source_exists": str(source.is_file()).lower(),
                    "review_priority": PRIORITY.get(row["concept_id"], "medium"),
                    "review_disposition": "retain-regression-case",
                    "change_rationale": RATIONALE.get(
                        row["concept_id"],
                        "Detector output changed; preserve the historical TP for adjudication.",
                    ),
                    "old_message": row["base_message"],
                    "old_consensus_reason": row["old_consensus_reason"],
                    "source_context": source_context(source, line),
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} removed historical TP reviews to {args.output}")


if __name__ == "__main__":
    main()

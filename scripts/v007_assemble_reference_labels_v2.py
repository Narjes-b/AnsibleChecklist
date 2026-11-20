#!/usr/bin/env python3
"""Merge per-family AI reference label files into one v2 reviewer form (write-once).

Input: ``--blank`` (a blank v2 form), ``--label-dir`` with one CSV per family
(``sample_id``, the ten v2 decision columns, and ``ai_confidence``).
Output: ``<name>-form.csv`` (v2 schema, passes ``v007_review_schema_v2.validate``), ``<name>-extra.csv``
(``sample_id, ai_confidence``) and ``<name>-summary.md`` (distribution per family against the pilot gates).
Nothing is written when any problem is found; ALL problems are listed.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_review_schema_v2 import V2_COLUMNS, V2_DECISION_COLUMNS, read_table, validate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--blank", type=Path, required=True)
    parser.add_argument("--label-dir", type=Path, required=True)
    parser.add_argument("--validation-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--name", default="claude-reference-pilot2")
    args = parser.parse_args()
    blank = read_table(args.blank)
    labels: dict[str, dict[str, str]] = {}
    for path in sorted(args.label_dir.glob("*.csv")):
        for row in read_table(path):
            if row["sample_id"] in labels:
                raise SystemExit(f"duplicate label for {row['sample_id']}")
            labels[row["sample_id"]] = row
    missing = [r["sample_id"] for r in blank if r["sample_id"] not in labels]
    unknown = sorted(set(labels) - {r["sample_id"] for r in blank})
    if missing or unknown:
        raise SystemExit(f"coverage mismatch: missing {len(missing)} {missing[:5]}, unknown {len(unknown)} {unknown[:5]}")
    filled = []
    for form in blank:
        row = dict(form)
        for column in V2_DECISION_COLUMNS:
            row[column] = labels[form["sample_id"]][column].strip()
        filled.append(row)
    problems = validate(blank, filled, args.validation_dir)
    for sample_id, text in problems:
        print(f"{sample_id}: {text}")
    # validate() rejects blank-vs-filled only through check_row; the blank decision cells were replaced above.
    bad_conf = [r["sample_id"] for r in blank if labels[r["sample_id"]].get("ai_confidence", "").strip() not in {"high", "medium", "low"}]
    if bad_conf:
        print("ai_confidence invalid for", bad_conf[:10])
    print(f"rows {len(filled)}; problems {len(problems) + len(bad_conf)}")
    if problems or bad_conf:
        return 1
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    form_path, extra_path, summary = out / f"{args.name}-form.csv", out / f"{args.name}-extra.csv", out / f"{args.name}-summary.md"
    for path in (form_path, extra_path, summary):
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
    with open(form_path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=V2_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(filled)
    with open(extra_path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["sample_id", "ai_confidence"])
        writer.writerows([r["sample_id"], labels[r["sample_id"]]["ai_confidence"].strip()] for r in blank)
    by: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in filled:
        by["ALL"].append(row)
        by[row["review_family"]].append(row)
    lines = [f"# {args.name}: distribution against the pilot gates", "",
             "Gates: uncertain+unreviewable <= 25 %, bundle issues <= 5 %. A single AI pass; not gold.", "",
             "| Group | n | positive | negative | uncertain | unreviewable | Unc.+unrev. | Bundle issues | codebook-ambiguous |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for group, rows in by.items():
        c = Counter(r["semantic_label"] for r in rows)
        n = len(rows)
        unc = (c["uncertain"] + c["unreviewable"]) / n
        issues = Counter(r["bundle_issue"] for r in rows)
        bundle = sum(v for k, v in issues.items() if k != "none") / n
        lines.append(f"| {group} | {n} | {c['positive']} | {c['negative']} | {c['uncertain']} | {c['unreviewable']} | {unc:.0%} | {bundle:.0%} | {issues['codebook-ambiguous']} |")
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

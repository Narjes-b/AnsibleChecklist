#!/usr/bin/env python3
"""Compare base/head occurrence exports and write a pull-request decision."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from ansibleguard.report.comparison import compare_occurrences, evaluate_policy


def _load_occurrences(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        if payload.get("kind") != "canonical-occurrences":
            raise ValueError(f"unsupported occurrence document: {path}")
        return payload.get("items", [])
    if isinstance(payload, list):
        return payload
    raise ValueError(f"occurrence document must be a list or v2 envelope: {path}")


def _update_summary(path, introduced_by_file):
    path = Path(path)
    if not path.is_file():
        return
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else []
    for required in ("new_pr_findings", "pr_comparison_status"):
        if required not in fields:
            fields.append(required)
    for row in rows:
        row["new_pr_findings"] = str(introduced_by_file.get(row["file"], 0))
        row["pr_comparison_status"] = "compared"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def update_head_output(output_root, comparison, policy):
    """Add PR comparison counts to the head report and both summary aliases."""
    output_root = Path(output_root)
    introduced_by_file = Counter(
        item.get("file", ".") for item in comparison.get("introduced", [])
    )
    _update_summary(output_root / "summary.csv", introduced_by_file)
    _update_summary(output_root / "summary" / "summary.csv", introduced_by_file)
    report_path = output_root / "summary" / "report.json"
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["pr_comparison"] = {
            "status": "compared",
            "introduced": len(comparison.get("introduced", [])),
            "fixed": len(comparison.get("fixed", [])),
            "moved": len(comparison.get("moved", [])),
            "uncertain": len(comparison.get("uncertain", [])),
            "policy_mode": policy["mode"],
            "policy_conclusion": policy["conclusion"],
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path, help="Base occurrences.json")
    parser.add_argument("head", type=Path, help="Head occurrences.json")
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--policy", choices=("observe", "ratchet"), default="observe")
    parser.add_argument(
        "--head-output",
        type=Path,
        help="Head scan output root to enrich with per-file PR counts",
    )
    args = parser.parse_args(argv)

    base = _load_occurrences(args.base)
    head = _load_occurrences(args.head)
    comparison = compare_occurrences(base, head)
    policy = evaluate_policy(comparison, args.policy)
    payload = {
        "schema_version": 2,
        "contract": "ansibleguard://schemas/output-v2.json",
        "kind": "pr-comparison",
        "comparison": comparison,
        "policy": policy,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if args.head_output is not None:
        update_head_output(args.head_output, comparison, policy)
    return 1 if payload["policy"]["conclusion"] == "failure" else 0


if __name__ == "__main__":
    raise SystemExit(main())

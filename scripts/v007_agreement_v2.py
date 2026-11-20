#!/usr/bin/env python3
"""Pilot agreement and gate report for v2 reviewer forms (plan v2, step 4).

Validates both returned forms with the v2 schema validator (all problems are listed and
the run stops), then reports per family and overall: raw agreement, Cohen's kappa and
Gwet's AC1 on ``semantic_label`` and ``actionability_label``, agreement on ``semantic_reason``,
the decided-subset kappa (both positive/negative), and evaluates the pre-registered gates:

- decided-subset kappa >= 0.70 (target) / >= 0.60 (minimum);
- each reviewer's uncertain + unreviewable share <= 25 %;
- share of items where either reviewer reports a bundle issue <= 5 %.

Outputs (write-once): ``agreement-v2.md`` and ``agreement-v2-by-family.csv``.
Neither reviewer is treated as truth.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_human_agreement import _agreement_metrics  # noqa: E402
from scripts.v007_review_schema_v2 import ACTIONABILITY, SEMANTIC, read_table, validate  # noqa: E402

KAPPA_TARGET, KAPPA_MINIMUM, UNCERTAIN_MAX, BUNDLE_MAX = 0.70, 0.60, 0.25, 0.05
NO_ISSUE = "none"


def metric(a: list[str], b: list[str], categories) -> dict | None:
    return _agreement_metrics(a, b, categories) if a else None


def family_report(rows_a: list[dict], rows_b: list[dict]) -> dict:
    n = len(rows_a)
    sem_a, sem_b = [r["semantic_label"] for r in rows_a], [r["semantic_label"] for r in rows_b]
    decided = [(x, y) for x, y in zip(sem_a, sem_b) if x in {"positive", "negative"} and y in {"positive", "negative"}]
    dec = metric([x for x, _ in decided], [y for _, y in decided], ("positive", "negative"))
    full = metric(sem_a, sem_b, SEMANTIC)
    act = metric([r["actionability_label"] for r in rows_a], [r["actionability_label"] for r in rows_b], ACTIONABILITY)
    reason_agree = sum(x["semantic_reason"] == y["semantic_reason"] for x, y in zip(rows_a, rows_b)) / n
    unc_a = sum(x in {"uncertain", "unreviewable"} for x in sem_a) / n
    unc_b = sum(x in {"uncertain", "unreviewable"} for x in sem_b) / n
    bundle = sum(x["bundle_issue"] != NO_ISSUE or y["bundle_issue"] != NO_ISSUE for x, y in zip(rows_a, rows_b)) / n
    kappa = dec["cohens_kappa"] if dec else None
    return {
        "n": n, "decided_n": len(decided), "semantic_raw": full["raw_agreement"], "semantic_kappa": full["cohens_kappa"],
        "semantic_ac1": full["gwets_ac1"], "decided_kappa": kappa, "actionability_raw": act["raw_agreement"],
        "actionability_kappa": act["cohens_kappa"], "reason_raw": reason_agree,
        "uncertain_a": unc_a, "uncertain_b": unc_b, "bundle_issue_rate": bundle,
        "gate_kappa": "target" if kappa is not None and kappa >= KAPPA_TARGET else "minimum" if kappa is not None and kappa >= KAPPA_MINIMUM else "FAIL",
        "gate_uncertain": "pass" if max(unc_a, unc_b) <= UNCERTAIN_MAX else "FAIL",
        "gate_bundle": "pass" if bundle <= BUNDLE_MAX else "FAIL",
    }


def fmt(value) -> str:
    return "n/a" if value is None else f"{value:.3f}" if isinstance(value, float) else str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--blank", type=Path, required=True)
    parser.add_argument("--a", type=Path, required=True)
    parser.add_argument("--b", type=Path, required=True)
    parser.add_argument("--validation-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    blank, a, b = read_table(args.blank), read_table(args.a), read_table(args.b)
    for name, rows in (("A", a), ("B", b)):
        problems = validate(blank, rows, args.validation_dir)
        for sample_id, text in problems:
            print(f"Reviewer {name} {sample_id}: {text}")
        if problems:
            print(f"Reviewer {name}: {len(problems)} problems; no report written")
            return 1
    groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(blank):
        groups["ALL"].append(index)
        groups[row["review_family"]].append(index)
    report = {name: family_report([a[i] for i in idx], [b[i] for i in idx]) for name, idx in groups.items()}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    md, csv_path = args.output_dir / "agreement-v2.md", args.output_dir / "agreement-v2-by-family.csv"
    if md.exists() or csv_path.exists():
        raise SystemExit("refusing to overwrite an existing agreement report")
    columns = list(next(iter(report.values())))
    with open(csv_path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["group", *columns])
        for name, values in report.items():
            writer.writerow([name, *(fmt(values[c]) for c in columns)])
    lines = ["# Pilot agreement and gates (schema v2)", "",
             f"Gates: decided kappa >= {KAPPA_TARGET} (minimum {KAPPA_MINIMUM}); uncertain+unreviewable <= {UNCERTAIN_MAX:.0%} per reviewer; bundle issues <= {BUNDLE_MAX:.0%}.",
             "A family that fails twice is dropped from precision claims. Neither reviewer is truth.", "",
             "| Group | n | Semantic raw | κ | AC1 | Decided n | Decided κ | Action. raw | Reason raw | Unc. A | Unc. B | Bundle | κ gate | Unc. gate | Bundle gate |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|"]
    for name, v in report.items():
        lines.append(f"| {name} | {v['n']} | {fmt(v['semantic_raw'])} | {fmt(v['semantic_kappa'])} | {fmt(v['semantic_ac1'])} | {v['decided_n']} | "
                     f"{fmt(v['decided_kappa'])} | {fmt(v['actionability_raw'])} | {fmt(v['reason_raw'])} | {fmt(v['uncertain_a'])} | "
                     f"{fmt(v['uncertain_b'])} | {fmt(v['bundle_issue_rate'])} | {v['gate_kappa']} | {v['gate_uncertain']} | {v['gate_bundle']} |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

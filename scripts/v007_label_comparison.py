#!/usr/bin/env python3
"""Compare two label files on the same pilot items (drift / agreement report).

Each file is keyed by ``sample_id``. A file either uses the frozen reviewer
columns (``semantic_label`` …) or a prefixed variant (``--b-prefix ai_`` reads
``ai_semantic_label``). Reports, overall and per review family and per rule:

- 4-class agreement on ``semantic_label``: raw agreement, Cohen's kappa, Gwet's AC1;
- the same on the decided subset (both labels positive/negative);
- uncertain / unreviewable rates of each file and the label distribution;
- the confusion matrix and the full list of disagreements.

Neither file is treated as truth: this measures how far two raters differ.
Outputs are written to ``--output-dir`` (a Markdown report and two CSVs).
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_human_agreement import SEMANTIC_LABELS, _agreement_metrics  # noqa: E402


def read_labels(path: Path, prefix: str) -> dict[str, dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    result = {}
    for row in rows:
        result[row["sample_id"]] = {
            "semantic": row[f"{prefix}semantic_label"].strip(),
            "actionability": row.get(f"{prefix}actionability_label", "").strip(),
            "notes": (row.get(f"{prefix}evidence_notes") or row.get(f"{prefix}notes") or "").strip(),
            "rule_id": row.get("rule_id", ""),
            "family": row.get("review_family", ""),
        }
    return result


def metrics(pairs: list[tuple[str, str]], categories) -> dict | None:
    if not pairs:
        return None
    return _agreement_metrics([a for a, _ in pairs], [b for _, b in pairs], categories)


def fmt(value) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--a", type=Path, required=True)
    parser.add_argument("--b", type=Path, required=True)
    parser.add_argument("--a-prefix", default="")
    parser.add_argument("--b-prefix", default="")
    parser.add_argument("--a-name", default="A")
    parser.add_argument("--b-name", default="B")
    parser.add_argument("--master", type=Path, help="agreement-pilot-master.csv to supply rule/family for prefixed files")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    a, b = read_labels(args.a, args.a_prefix), read_labels(args.b, args.b_prefix)
    meta = {}
    if args.master:
        with open(args.master, newline="", encoding="utf-8") as stream:
            meta = {r["sample_id"]: r for r in csv.DictReader(stream)}
    ids = [i for i in a if i in b]
    if len(ids) != len(a) or len(ids) != len(b):
        print(f"warning: {len(a)} vs {len(b)} rows; {len(ids)} paired", file=sys.stderr)
    for i in ids:
        info = meta.get(i, {})
        rule = info.get("rule_id") or a[i]["rule_id"] or b[i]["rule_id"]
        family = info.get("review_family") or a[i]["family"] or b[i]["family"]
        a[i]["rule_id"], a[i]["family"] = rule, family
    groups: dict[str, list[str]] = defaultdict(list)
    for i in ids:
        groups["ALL"].append(i)
        groups["family: " + a[i]["family"]].append(i)
    lines = [f"# Label comparison: {args.a_name} vs {args.b_name}", "",
             f"Paired items: {len(ids)}. Neither file is ground truth.", "",
             "| Group | n | Raw agreement | Cohen κ | Gwet AC1 | Decided n | Decided agreement | Decided κ | "
             f"{args.a_name} uncertain+unrev. | {args.b_name} uncertain+unrev. |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, members in groups.items():
        full = metrics([(a[i]["semantic"], b[i]["semantic"]) for i in members], SEMANTIC_LABELS)
        decided = [(a[i]["semantic"], b[i]["semantic"]) for i in members
                   if a[i]["semantic"] in {"positive", "negative"} and b[i]["semantic"] in {"positive", "negative"}]
        dec = metrics(decided, ("positive", "negative"))
        ua = sum(a[i]["semantic"] in {"uncertain", "unreviewable"} for i in members)
        ub = sum(b[i]["semantic"] in {"uncertain", "unreviewable"} for i in members)
        lines.append(
            f"| {name} | {len(members)} | {fmt(full['raw_agreement'])} | {fmt(full['cohens_kappa'])} | {fmt(full['gwets_ac1'])} | "
            f"{len(decided)} | {fmt(dec['raw_agreement']) if dec else 'n/a'} | {fmt(dec['cohens_kappa']) if dec else 'n/a'} | "
            f"{ua} | {ub} |"
        )
    confusion = Counter((a[i]["semantic"], b[i]["semantic"]) for i in ids)
    lines += ["", f"## Confusion ({args.a_name} rows, {args.b_name} columns)", "",
              "| | " + " | ".join(SEMANTIC_LABELS) + " |", "|---|" + "---:|" * len(SEMANTIC_LABELS)]
    for x in SEMANTIC_LABELS:
        lines.append(f"| {x} | " + " | ".join(str(confusion[(x, y)]) for y in SEMANTIC_LABELS) + " |")
    by_rule: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for i in ids:
        by_rule[a[i]["rule_id"].split("/")[-1]].append((a[i]["semantic"], b[i]["semantic"]))
    lines += ["", "## Per rule (agreement on the 4-class label)", "", "| Rule | n | Agree | Raw |", "|---|---:|---:|---:|"]
    for rule, pairs in sorted(by_rule.items(), key=lambda kv: (sum(x == y for x, y in kv[1]) / len(kv[1]), kv[0])):
        agree = sum(x == y for x, y in pairs)
        lines.append(f"| {rule} | {len(pairs)} | {agree} | {agree / len(pairs):.2f} |")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{args.a_name}-vs-{args.b_name}".replace(" ", "-")
    report = args.output_dir / f"{stem}-agreement.md"
    if report.exists():
        raise SystemExit(f"refusing to overwrite {report}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(args.output_dir / f"{stem}-disagreements.csv", "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["sample_id", "family", "rule_id", f"{args.a_name}_semantic", f"{args.b_name}_semantic",
                         f"{args.a_name}_actionability", f"{args.b_name}_actionability",
                         f"{args.a_name}_notes", f"{args.b_name}_notes"])
        for i in ids:
            if a[i]["semantic"] != b[i]["semantic"]:
                writer.writerow([i, a[i]["family"], a[i]["rule_id"], a[i]["semantic"], b[i]["semantic"],
                                 a[i]["actionability"], b[i]["actionability"], a[i]["notes"][:300], b[i]["notes"][:300]])
    print("\n".join(lines[:14]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

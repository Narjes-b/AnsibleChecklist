# -*- coding: utf-8 -*-
"""Cross-phase rollup: aggregates Phase 1 (agreement-pilot, 350 items,
Reviewer A vs Reviewer B) and Phase 2 (stratified sample, 400 items,
Reviewer A vs Reviewer C) into one summary.

This does NOT merge, dedupe, or adjudicate anything across phases — the two
samples are drawn by different methodologies from different (though
overlapping-in-corpus) populations, and a row in one phase has no identity
relationship to a row in the other. "Final agreement" below means only: rows
where the mechanical classify() rule already found full agreement within a
phase. Every row classified as anything other than Agreement in either phase
remains open, with final_validated_label left blank in that phase's CSV, for
a human to adjudicate. No disagreement is resolved by this script or any
script in this pipeline.
"""
import csv
from collections import Counter
from pathlib import Path

PHASES = [
    ("Phase 1 (agreement-pilot, Reviewer A vs Reviewer B)", Path("consolidated-comparison.csv")),
    ("Phase 2 (stratified sample, Reviewer A vs Reviewer C)", Path("consolidated-comparison-phase2.csv")),
]
OUT_MD = Path("FINAL_AGREEMENT_SUMMARY.md")

lines = []
lines.append("# Cross-phase agreement summary\n")
lines.append("Each phase below is an independent sample with its own methodology; rows are **not** matched or "
              "merged across phases. This is a rollup of already-computed, mechanically-derived agreement "
              "statistics — it introduces no new judgment and resolves no disagreement.\n")

grand_total = 0
grand_counts = Counter()

lines.append("## Combined headline counts\n")
lines.append("| Phase | N | Agreement | Partial agreement | Disagreement | Insufficient info |")
lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")

phase_rows = {}
for name, path in PHASES:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    phase_rows[name] = rows
    n = len(rows)
    counts = Counter(r["agreement_status"] for r in rows)
    grand_total += n
    grand_counts.update(counts)
    lines.append(f"| {name} | {n} | {counts.get('Agreement',0)} | {counts.get('Partial agreement',0)} | "
                 f"{counts.get('Disagreement',0)} | {counts.get('Insufficient information',0)} |")

lines.append(f"| **Combined** | **{grand_total}** | **{grand_counts.get('Agreement',0)}** | "
             f"**{grand_counts.get('Partial agreement',0)}** | **{grand_counts.get('Disagreement',0)}** | "
             f"**{grand_counts.get('Insufficient information',0)}** |\n")

def pct(n, d):
    return f"{100.0 * n / d:.1f}%" if d else "n/a"

lines.append(f"Across both phases combined (N={grand_total}, naive pooled denominator — the two phases are "
              f"different samples, so this is a scale indicator, not a single unified agreement rate): "
              f"**{grand_counts.get('Agreement',0)} items ({pct(grand_counts.get('Agreement',0), grand_total)}) "
              f"reached full agreement** between their two independent reviewers. The remaining "
              f"{grand_total - grand_counts.get('Agreement',0)} items "
              f"({pct(grand_total - grand_counts.get('Agreement',0), grand_total)}) are open and unresolved: "
              f"{grand_counts.get('Disagreement',0)} direct disagreements, "
              f"{grand_counts.get('Partial agreement',0)} partial agreements (same semantic call, different "
              f"severity/reasoning), and {grand_counts.get('Insufficient information',0)} where the two reviewers "
              f"could not be meaningfully compared (at least one found the evidence insufficient).\n")

lines.append("## What \"final\" means here\n")
lines.append("Per the task's hard constraint, **no disagreement is resolved by any script in this pipeline**. "
              "\"Final agreement\" is not a status this pipeline assigns — it is the literal count of rows where "
              "the two independent reviewers' labels already matched exactly (`agreement_status == Agreement`) "
              "under a fixed, documented, mechanical rule. Every other row's `final_validated_label` column is "
              "blank in both phase CSVs and stays that way until a human reviewer adjudicates it.\n")

lines.append("## Where to find the unresolved items\n")
for name, path in PHASES:
    rows = phase_rows[name]
    n = len(rows)
    open_rows = [r for r in rows if r["agreement_status"] != "Agreement"]
    lines.append(f"- **{name}**: `{path.name}`, filter `agreement_status != Agreement` "
                 f"({len(open_rows)} of {n} rows).")
lines.append("")

lines.append("## Reviewer identity\n")
lines.append("Reviewer A is the same reviewer across both phases. Reviewer B (Phase 1) and Reviewer C (Phase 2) "
              "are two distinct, separate reviewers — Reviewer C is not a re-labeling of Reviewer B. All three are "
              "independent AI-generated passes; none is a human reviewer, and none is treated as ground truth. "
              "Which specific underlying model produced each pass is intentionally not recorded in these "
              "deliverables.\n")

lines.append("## Not yet included\n")
lines.append("- Any human-labeled gold standard (neither phase has one yet; both are AI-vs-AI).\n"
              "- The teammate's separate `fix/v007-audit-2026-10-15` branch work (codebook v2.1, \"pilot 2\", "
              "171 items) — a distinct, not-yet-merged validation track; see "
              "`docs/study/v007-audit-2026-10-15.md` and `study/validation-v007-human/pilot2/README.md` on that "
              "branch for its own status.\n"
              "- Task 3's local-model-vs-existing-agent rubric comparison, which is a separate analysis "
              "(`local-llm/task3-comparison.csv`) and is not an agreement/disagreement classification in the "
              "sense used here.\n")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {OUT_MD}")

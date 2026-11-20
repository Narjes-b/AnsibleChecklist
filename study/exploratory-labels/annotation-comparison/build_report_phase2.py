# -*- coding: utf-8 -*-
"""Generates PHASE2_COMPARISON_REPORT.md from consolidated-comparison-phase2.csv
(the 400-item impact-weighted stratified sample). All statistics are computed
directly from the CSV — nothing here is hand-typed."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

IN_CSV = Path("consolidated-comparison-phase2.csv")
OUT_MD = Path("PHASE2_COMPARISON_REPORT.md")

with open(IN_CSV, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

N = len(rows)
status_counts = Counter(r["agreement_status"] for r in rows)
family_counts = defaultdict(lambda: Counter())
for r in rows:
    family_counts[r["review_family"]][r["agreement_status"]] += 1

category_counts = Counter(
    r["disagreement_category"].split(" (")[0]
    for r in rows
    if r["disagreement_category"]
)

def pct(n):
    return f"{100.0 * n / N:.1f}%"

lines = []
lines.append("# Phase 2 comparison report — Reviewer A vs. Reviewer C (stratified sample)\n")
lines.append(f"Denominator for every percentage below: **N = {N}** (the full impact-weighted stratified sample, "
              "identical row set independently labeled by both reviewers; verified 1:1 ID match before comparison).\n")
lines.append("Reviewer identity is deliberately generic, consistent with Phase 1 — Reviewer A is the same reviewer "
              "as Phase 1's Reviewer A; Reviewer C is a new, third independent pass (not Phase 1's Reviewer B). "
              "Which underlying model produced which pass is not recorded here by design.\n")
lines.append("**This uses the same mechanical `classify()` rule as Phase 1** (`build_comparison_phase2.py`), so the "
              "two phases' numbers are directly comparable. Note this differs from the self-reported \"both match\" "
              "figure in `stratified-sample/CHATGPT_REVIEW_REPORT.md`, which counts a looser semantic+actionability "
              "match without requiring `reason_code` agreement — that report's 201/400 (50.3%) and this report's "
              "Agreement count below are not the same measurement and should not be conflated.\n")

lines.append("## Headline counts\n")
lines.append("| Status | Count | % of N |")
lines.append("| --- | ---: | ---: |")
for status in ["Agreement", "Partial agreement", "Disagreement", "Insufficient information"]:
    c = status_counts.get(status, 0)
    lines.append(f"| {status} | {c} | {pct(c)} |")
lines.append(f"| **Total** | **{N}** | **100.0%** |\n")

lines.append(
    "**How `agreement_status` was assigned** (mechanical rule, identical to Phase 1 — see "
    "`build_comparison_phase2.py::classify()`):\n"
    "- **Insufficient information**: at least one reviewer labeled the item `uncertain`/`unreviewable`, and the "
    "other did not make the same call for the same reason.\n"
    "- **Disagreement**: both reviewers gave a decisive label (`positive`/`negative`), but a different one.\n"
    "- **Agreement**: identical `semantic_label`, `actionability_label`, and `reason_code`.\n"
    "- **Partial agreement**: identical `semantic_label`, but `actionability_label` and/or `reason_code` differ.\n"
)

lines.append("## Breakdown by review family\n")
lines.append("| Family | Agreement | Partial agreement | Disagreement | Insufficient info | Total |")
lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
for fam in sorted(family_counts, key=lambda f: -sum(family_counts[f].values())):
    c = family_counts[fam]
    total = sum(c.values())
    lines.append(f"| {fam} | {c.get('Agreement',0)} | {c.get('Partial agreement',0)} | "
                 f"{c.get('Disagreement',0)} | {c.get('Insufficient information',0)} | {total} |")
lines.append("")

lines.append("## Breakdown by rule (top 15 by total occurrences in sample)\n")
rule_counts = defaultdict(lambda: Counter())
for r in rows:
    rule_counts[r["rule_id"]][r["agreement_status"]] += 1
lines.append("| Rule | Agreement | Partial agreement | Disagreement | Insufficient info | Total |")
lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
for rule in sorted(rule_counts, key=lambda rl: -sum(rule_counts[rl].values()))[:15]:
    c = rule_counts[rule]
    total = sum(c.values())
    lines.append(f"| {rule} | {c.get('Agreement',0)} | {c.get('Partial agreement',0)} | "
                 f"{c.get('Disagreement',0)} | {c.get('Insufficient information',0)} | {total} |")
lines.append("")

lines.append("## Disagreement/partial-agreement categories\n")
lines.append("| Category | Count |")
lines.append("| --- | ---: |")
for cat, c in category_counts.most_common():
    lines.append(f"| {cat} | {c} |")
lines.append("")

def example_block(status, n=3):
    examples = [r for r in rows if r["agreement_status"] == status][:n]
    out = []
    for r in examples:
        out.append(f"**{r['issue_id']}** ({r['review_family']}, `{r['rule_id']}`, {r['repository']}:{r['path']}:{r['line']})")
        out.append(f"- Reviewer A: `{r['reviewer_a_label_semantic']}` / `{r['reviewer_a_label_actionability']}` / reason=`{r['reviewer_a_reason_code']}`")
        out.append(f"  - {r['reviewer_a_explanation'][:220]}")
        out.append(f"- Reviewer C: `{r['reviewer_c_label_semantic']}` / `{r['reviewer_c_label_actionability']}` / reason=`{r['reviewer_c_reason_code']}`")
        out.append(f"  - {r['reviewer_c_explanation'][:220]}")
        if r["disagreement_category"]:
            out.append(f"- Disagreement category: {r['disagreement_category']}")
        out.append("")
    return "\n".join(out)

lines.append("## Representative examples\n")
lines.append("### Agreement\n")
lines.append(example_block("Agreement"))
lines.append("### Partial agreement\n")
lines.append(example_block("Partial agreement"))
lines.append("### Disagreement\n")
lines.append(example_block("Disagreement"))
lines.append("### Insufficient information\n")
lines.append(example_block("Insufficient information"))

needs_review = [r for r in rows if r["agreement_status"] != "Agreement"]
lines.append(f"## Issues requiring your decision\n")
lines.append(f"**{len(needs_review)} of {N} items ({pct(len(needs_review))}) are not a full agreement** and are marked "
              "`validation_status = Initially unreviewed` with `final_validated_label` left blank in "
              "`consolidated-comparison-phase2.csv`. Filter that file on `agreement_status != Agreement` to get the "
              "full, traceable list (all 400 original rows are preserved — none were removed or merged).\n")
lines.append(f"- Disagreement: {status_counts.get('Disagreement',0)}")
lines.append(f"- Partial agreement: {status_counts.get('Partial agreement',0)}")
lines.append(f"- Insufficient information: {status_counts.get('Insufficient information',0)}")
lines.append("")

lines.append("## Note on deduplication\n")
lines.append("No deduplication or merging was performed. Both source files have exactly 400 rows, 1:1 matched by "
              "`sample_id` (verified by set equality before any comparison), and all 400 rows are present in the "
              "output unchanged in identity.\n")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {OUT_MD}")

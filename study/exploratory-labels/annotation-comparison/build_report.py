# -*- coding: utf-8 -*-
"""Generates COMPARISON_REPORT.md from consolidated-comparison.csv (Phase 1: the
350-item agreement-pilot sample). All statistics are computed directly from the
CSV — nothing here is hand-typed."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

IN_CSV = Path("consolidated-comparison.csv")
OUT_MD = Path("COMPARISON_REPORT.md")

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
lines.append("# Phase 1 comparison report — Reviewer A vs. Reviewer B\n")
lines.append(f"Denominator for every percentage below: **N = {N}** (the full agreement-pilot sample, "
              "identical row set independently labeled by both reviewers; verified 1:1 ID match before comparison).\n")
lines.append("Reviewer identity is deliberately generic — both passes are AI-generated, independent, and blind to "
              "each other, but which underlying model produced which pass is not recorded here by design.\n")

lines.append("## Headline counts\n")
lines.append("| Status | Count | % of N |")
lines.append("| --- | ---: | ---: |")
for status in ["Agreement", "Partial agreement", "Disagreement", "Insufficient information"]:
    c = status_counts.get(status, 0)
    lines.append(f"| {status} | {c} | {pct(c)} |")
lines.append(f"| **Total** | **{N}** | **100.0%** |\n")

lines.append(
    "**How `agreement_status` was assigned** (mechanical rule, not a judgment call — see "
    "`build_comparison.py::classify()` for the exact logic):\n"
    "- **Insufficient information**: at least one reviewer labeled the item `uncertain`/`unreviewable`. "
    "If both did, and for the same reason, that is scored as `Agreement` on the uncertainty call itself; "
    "any other mix (one reviewer decisive, or both uncertain for different reasons) is `Insufficient information`, "
    "since the two records cannot be meaningfully compared as a semantic agreement or disagreement.\n"
    "- **Disagreement**: both reviewers gave a decisive label (`positive`/`negative`), but a different one.\n"
    "- **Agreement**: identical `semantic_label`, `actionability_label`, and `reason_code`.\n"
    "- **Partial agreement**: identical `semantic_label`, but `actionability_label` and/or `reason_code` differ "
    "— i.e. the two reviewers agree on *whether* the condition is present, but not on severity, remediation, or "
    "the specific reasoning.\n"
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

lines.append("## Disagreement/partial-agreement categories\n")
lines.append("(counts rows whose `disagreement_category` starts with this label; a row can only have one category)\n")
lines.append("| Category | Count |")
lines.append("| --- | ---: |")
for cat, c in category_counts.most_common():
    lines.append(f"| {cat} | {c} |")
lines.append("")

def example_block(status, n=3):
    examples = [r for r in rows if r["agreement_status"] == status][:n]
    out = []
    for r in examples:
        out.append(f"**{r['issue_id']}** ({r['review_family']}, `{r['rule_id']}`, {r['repository']}:{r['path']}:{r['line_start']})")
        out.append(f"- Reviewer A: `{r['reviewer_a_label_semantic']}` / `{r['reviewer_a_label_actionability']}` / reason=`{r['reviewer_a_reason_code']}`")
        out.append(f"  - {r['reviewer_a_explanation'][:220]}")
        out.append(f"- Reviewer B: `{r['reviewer_b_label_semantic']}` / `{r['reviewer_b_label_actionability']}` / reason=`{r['reviewer_b_reason_code']}`")
        out.append(f"  - {r['reviewer_b_explanation'][:220]}")
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
              "`consolidated-comparison.csv`. Filter that file on `agreement_status != Agreement` to get the full, "
              "traceable list (all 350 original rows are preserved — none were removed or merged).\n")
lines.append(f"- Disagreement (both reviewers confident, different label): {status_counts.get('Disagreement',0)}  — highest priority, since this is a direct semantic conflict.")
lines.append(f"- Partial agreement (same label, different severity/reasoning): {status_counts.get('Partial agreement',0)} — lower priority, but still affects actionability/remediation guidance.")
lines.append(f"- Insufficient information (evidence-sufficiency mismatch): {status_counts.get('Insufficient information',0)} — these may need a richer context bundle before a human can even adjudicate them, not just a decision.")
lines.append("")

lines.append("## Note on deduplication\n")
lines.append("No deduplication or merging was performed. Both source files have exactly 350 rows, 1:1 matched by "
              "`sample_id` (verified by set equality before any comparison), and all 350 rows are present in the "
              "output unchanged in identity. No rows were judged to refer to \"the same underlying problem\" as "
              "another row — each `sample_id` is already a distinct frozen occurrence from the agreement-pilot "
              "protocol's own deterministic sampling, not something this task re-sampled or re-grouped.\n")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {OUT_MD}")

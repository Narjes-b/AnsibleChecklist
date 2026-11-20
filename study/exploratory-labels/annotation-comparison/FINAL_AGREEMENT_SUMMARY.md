# Cross-phase agreement summary

Each phase below is an independent sample with its own methodology; rows are **not** matched or merged across phases. This is a rollup of already-computed, mechanically-derived agreement statistics — it introduces no new judgment and resolves no disagreement.

## Combined headline counts

| Phase | N | Agreement | Partial agreement | Disagreement | Insufficient info |
| --- | ---: | ---: | ---: | ---: | ---: |
| Phase 1 (agreement-pilot, Reviewer A vs Reviewer B) | 350 | 143 | 88 | 42 | 77 |
| Phase 2 (stratified sample, Reviewer A vs Reviewer C) | 400 | 151 | 84 | 39 | 126 |
| **Combined** | **750** | **294** | **172** | **81** | **203** |

Across both phases combined (N=750, naive pooled denominator — the two phases are different samples, so this is a scale indicator, not a single unified agreement rate): **294 items (39.2%) reached full agreement** between their two independent reviewers. The remaining 456 items (60.8%) are open and unresolved: 81 direct disagreements, 172 partial agreements (same semantic call, different severity/reasoning), and 203 where the two reviewers could not be meaningfully compared (at least one found the evidence insufficient).

## What "final" means here

Per the task's hard constraint, **no disagreement is resolved by any script in this pipeline**. "Final agreement" is not a status this pipeline assigns — it is the literal count of rows where the two independent reviewers' labels already matched exactly (`agreement_status == Agreement`) under a fixed, documented, mechanical rule. Every other row's `final_validated_label` column is blank in both phase CSVs and stays that way until a human reviewer adjudicates it.

## Where to find the unresolved items

- **Phase 1 (agreement-pilot, Reviewer A vs Reviewer B)**: `consolidated-comparison.csv`, filter `agreement_status != Agreement` (207 of 350 rows).
- **Phase 2 (stratified sample, Reviewer A vs Reviewer C)**: `consolidated-comparison-phase2.csv`, filter `agreement_status != Agreement` (249 of 400 rows).

## Reviewer identity

Reviewer A is the same reviewer across both phases. Reviewer B (Phase 1) and Reviewer C (Phase 2) are two distinct, separate reviewers — Reviewer C is not a re-labeling of Reviewer B. All three are independent AI-generated passes; none is a human reviewer, and none is treated as ground truth. Which specific underlying model produced each pass is intentionally not recorded in these deliverables.

## Not yet included

- Any human-labeled gold standard (neither phase has one yet; both are AI-vs-AI).
- The teammate's separate `fix/v007-audit-2026-10-15` branch work (codebook v2.1, "pilot 2", 171 items) — a distinct, not-yet-merged validation track; see `docs/study/v007-audit-2026-10-15.md` and `study/validation-v007-human/pilot2/README.md` on that branch for its own status.
- Task 3's local-model-vs-existing-agent rubric comparison, which is a separate analysis (`local-llm/task3-comparison.csv`) and is not an agreement/disagreement classification in the sense used here.

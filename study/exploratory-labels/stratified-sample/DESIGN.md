# Impact-weighted stratified sample — design

Replaces the flat 50-per-family agreement-pilot design with a sample that reflects
what actually dominates the real v0.0.7 corpus, while staying human-reviewable.

## Source data

All canonical AnsibleGuard-native occurrences (`native_rules` starting
`ansibleguard/`) across the **127-repo clean subset** (`study/v007-full-repro-results/`,
zero validation failures, single tool commit/rule-catalog identity) — **65,324
occurrences across 59 distinct rules**. Source context is pulled from the actual
frozen repository checkout at each repo's exact commit SHA
(`study/cache/v007-full-repro-2026/repositories/<repo>/<path>`), not from analysis
artifacts, so it reflects the real source the detector saw.

## Stratification

1. Rank all 59 rules by total occurrence count (descending).
2. Compute cumulative share of the corpus and bucket into four tiers:
   - **A-dominant** (0–50% cumulative): just 1 rule (`missing-tags`, 26.4% alone).
   - **B-major** (50–80%): 5 rules.
   - **C-moderate** (80–95%): 12 rules.
   - **D-long-tail** (95–100%): 41 rules, each individually rare.
3. Per-rule sample size = `sqrt(occurrence_count)`, normalized to a target total
   (480, tuned so that after context-extraction losses the final count lands at
   400), floored at 1 and capped at 22 per rule. The square-root weighting is
   deliberate: a flat proportional allocation would let `missing-tags` alone (26% of
   all findings) consume over a quarter of the sample; sqrt-weighting still favors
   high-impact rules but keeps the long tail meaningfully represented.
4. Within a rule, occurrences are deduplicated to one per distinct repository first
   (for source diversity), then deterministically ranked by
   `SHA256("v007-stratified-v1|<rule_id>|<occurrence_id>")` and the top N taken —
   same reproducible-selection method the existing agreement-pilot protocol uses.

## Result (v2, 400 rows)

**400 rows** (of a 480-row pre-extraction target; some rows were dropped where the
frozen checkout didn't have a readable file at the recorded path/line — see
`stratified-sample-manifest.json` for the full per-rule ledger). An earlier v1 pass
at a smaller target (220) produced 178 rows with the same method; v2 simply raises
`TARGET_TOTAL`/`PER_RULE_CAP` and re-runs — the stratification logic and tier
boundaries are unchanged.

| Family | Rows (v2, 400) | Rows (v1, 178) |
| --- | ---: | ---: |
| Style/policy | 133 | 55 |
| Maintainability/complexity | 92 | 41 |
| Variable/reference reasoning | 50 | 23 |
| Objective correctness | 48 | 23 |
| Security | 38 | 17 |
| Structure/reuse | 31 | 16 |
| Review/history | 8 | 3 |

| Tier | Rules | Allocated rows (v2) |
| --- | ---: | ---: |
| A-dominant (0-50% cum. share) | 1 | 22 |
| B-major (50-80%) | 5 | 108 |
| C-moderate (80-95%) | 12 | 147 |
| D-long-tail (95-100%) | 41 | 132 |

Rule coverage: 56 of 59 corpus rules represented (3 rules had zero occurrences with a
readable file at the recorded path/line across the whole corpus).

Review/history stays small in both versions because this sample is scoped to
**static-source** occurrences (concrete file/line findings) rather than
commit-metadata findings, which is what "impact on the actual code collection" means
for this design — commit message/history rules remain the separate panel the
existing agreement-pilot already covers.

## Labeling notes (v2)

All 400 rows were independently AI-labeled (model: claude-sonnet-5, protocol:
`stratified-v2-400`) following the same family codebooks as the agreement pilot.
Overall label distribution: positive 195, uncertain 115, negative 79, unreviewable 11.

A recurring, structural (not per-row-ambiguous) finding across the Maintainability
and Structure/reuse families: several rules (`large-playbook`, `complex-playbook`,
`large-play`, `high-coupling`, `role-readme-absent`, `duplicated-code`,
`missing-abstraction`) assert whole-file or cross-file properties that the ~29-line
context window can structurally never confirm — these drove most of the `uncertain`
labels and are a real gap in context-extraction design to flag for whoever curates
bundles next, not a sign of ambiguous judgment calls. Style/policy labelers also
repeatedly caught rules misapplied to non-Ansible YAML files (Kustomize patches, Go-task
Taskfiles, SOPS-encrypted secrets, Galaxy role-requirements manifests) that happened to
match a rule's surface pattern (line length, missing `name:` key, etc.).

## What this is not

This is a separate, exploratory sample — not a replacement for the frozen 350-item
agreement-pilot (`study/validation-v007-human/samples/agreement-pilot/`), and not
itself a precision/recall measurement. It's built from the same codebook families so
the same review methodology (`REVIEWER_INSTRUCTIONS.md`, family codebooks) applies.

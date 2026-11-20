# V7 frozen development experiment

All 96 outputs were explicitly reviewed by the same unblinded AI implementer using unchanged AI source references. Cases are development-exposed. These are complete-pipeline results, not independent human accuracy or reviewer agreement.

| Condition | Measure | V6 /48 | V7 /48 | Change (percentage points) |
|---|---|---:|---:|---:|
| window | available | 30 | 44 | +29.17 |
| window | decision | 8 | 19 | +22.92 |
| window | content | 3 | 13 | +20.83 |
| window | strict | 3 | 9 | +12.50 |
| scoped | available | 47 | 44 | -6.25 |
| scoped | decision | 44 | 42 | -4.17 |
| scoped | content | 44 | 42 | -4.17 |
| scoped | strict | 44 | 42 | -4.17 |

| Panel / condition | N | Accepted | Decision matches | Adequate | Adequate + citations |
|---|---:|---:|---:|---:|---:|
| all / window | 48 | 44 | 19 | 13 | 9 |
| all / scoped | 48 | 44 | 42 | 42 | 42 |
| controlled / window | 24 | 23 | 10 | 7 | 4 |
| controlled / scoped | 24 | 24 | 24 | 24 | 24 |
| real / window | 24 | 21 | 9 | 6 | 5 |
| real / scoped | 24 | 20 | 18 | 18 | 18 |

## Implementation and outcome interpretation

Generation now uses neutral present/absent/unknown states mapped to the unchanged public assessment vocabulary. No decision is inferred or corrected from prose. State-specific grammars require low confidence and nonempty missing dependencies for unknown; nonempty evidence-boundary text is required. Rule definitions and neutral questions are shared by both conditions. The window arm retains its prior context boundary and receives no scoped facts, selected answers or selected citations.
The scoped condition still uses backend-constrained decisions, authored fact summaries and selected citations. Every free-reasoning claim is also reviewed. Rejected responses, wrong citations, incorrect bit interpretation and ambiguous reference disagreements are retained as unsuccessful outcomes. A right structured decision does not rescue false prose.
There are 8 unavailable/rejected outputs, including 6 conservative byte/token-budget rejections. The larger state-specific grammar and shared rule guidance consume conservative context allowance; this can reduce availability without source truncation. The generation grammar does not certify substantive truth, and the model can still choose an incorrect known state rather than admit unknown facts.
Two smoke rounds (24 calls each) were used, with raw attempts retained. Exact round1/round2 explanation sources were recovered and hash-verified against their recorded identities. Compact JSON serialization followed the second-round code changes; candidate freezing preceded completion of smoke2 collection, with no further model-driven code edits. Final tests and the scored run use the frozen compact candidate. Shared local-model queue affects timing, which is not used as a comparative outcome.

## Repair experiments

Caller-selected local-model drafts: 8/8 delivered; 8/8 passed mechanical and isolated behavioral checks. 4/4 ineligible sources were blocked before any generation request. All eight raw snippets and BEFORE-only prompts were explicitly inspected. No reference AFTER task was supplied and no source was applied. See model-requested-edits-ai-review.csv.
Autonomous triage still produced 0/8 eligible code proposals across 12 source calls. This is a separate task; do not substitute the requested-edit success rate. The prior deterministic generator also passed 8/8, so these tests do not establish LLM superiority.

## Scientific and manuscript provenance

The original detection precision, corpus prevalence, PR replay and 60-case pilot are historical results, not recomputed by this experiment. Corrected detection-family agreement percentages (67%, 27%, 77%) are author-supplied with unresolved denominators/paired labels; no aggregate agreement or kappa/AC1 is inferred. The new 48-case quality counts are not human agreement.
Human explanation/repair forms remain blank and recruitment deferred. An optional internal paper copy may show explicitly hypothetical agreement placeholders; measured paper versions retain the actual method. No independent explanation correctness, general repair semantic correctness or comprehension benefit is established.
Full test suite: 1,676 passed, two skipped. Production hashes match freeze.json. See full-validation.log, validation-sources.tar.gz, raw run records, manual-ai-ratings.csv, environment.json and the archived implementation for reproduction.

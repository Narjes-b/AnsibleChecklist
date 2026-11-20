# Improvement and repeated AI experiment

The default scoped pipeline improved on the same exposed development cases, using the same local model and the unchanged AI source judgments. All 96 new outcomes were reviewed again. The paper files and human-review forms are unchanged.

**These are post hoc judgments by the same AI assistant that implemented the changes.** They are not independent human validation, held-out generalization, or population estimates. The short summaries and decisive citations are now backend-authored/selected; free model reasoning is still reviewed and can make an output fail.

## Scoped pipeline: before and after

| Measure | Before / 48 | After / 48 | Change |
|---|---:|---:|---:|
| Accepted outputs | 45 (93.75%) | 47 (97.92%) | +4.17 pp |
| Decision agrees with unchanged AI reference | 41 (85.42%) | 44 (91.67%) | +6.25 pp |
| Adequate complete explanation | 29 (60.42%) | 41 (85.42%) | +25.0 pp |
| Adequate explanation plus supporting citations | 21 (43.75%) | 38 (79.17%) | +35.42 pp |

The primary adequate-output score increased by 25 percentage points, and the stricter content-plus-citation score by 35.42 points. One new scoped outcome remains interrupted-unknown after an execution-service restart and counts as unsuccessful; the baseline separately had one interrupted window outcome.

## Complete rerun, including the ablation

| Panel / condition | Scheduled | Available | Reference decision matches | Adequate content | Adequate + citations |
|---|---:|---:|---:|---:|---:|
| all / window | 48 | 48 | 8 | 0 | 0 |
| all / scoped | 48 | 47 | 44 | 41 | 38 |
| controlled / window | 24 | 24 | 8 | 0 | 0 |
| controlled / scoped | 24 | 23 | 23 | 23 | 23 |
| real / window | 24 | 24 | 0 | 0 | 0 |
| real / scoped | 24 | 24 | 21 | 18 | 15 |

The new window-only condition regressed from 4/48 to 0/48 adequate outputs. The full V5 prompt expects backend facts that this ablation omits; this is not an isolated retrieval comparison or an improved standalone-model baseline. The before/after scoped comparison above is the relevant default-workflow result. Do not hide the window regression or claim retrieval-only superiority.

## Repairs: keep the two mechanisms separate

The LLM repair rerun returned 12 accepted assessments but still generated zero code proposals and marked none of the eight repair-eligible cases actionable. LLM proposal coverage remains **0/8**. LLM-generated fix correctness cannot be estimated, and is not a 0% correctness result.

A separate explicit-request command now previews only two narrowly selected changes: enable TLS verification or protect a verified direct debug task's output. The caller must choose the edit and declare intent; source comments cannot authorize it. This is deterministic transformation, not LLM repair.

On the same 12 repair sources it generated 8/8 eligible drafts, all 8/8 passed mechanical and isolated behavioral checks, and it generated 0/4 drafts for already-correct or unknown-runtime cases. No source edits were applied. The separate AI edit review found only the requested flag changed, with unrelated fields preserved, in these synthetic fixtures. This does not establish general production correctness.

Behavior checks cover rejecting untrusted certificates, accepting the fixture's trusted endpoint with identical artifact contents, suppressing the synthetic secret in normal/failure controller output, and keeping registered results usable. Source/tag/guard preservation and lint are checked separately. The prior authored mechanical controls improved from 6/8 to 8/8 after fixing serializer indentation.

## Remaining failures

Four new real-source rationales remain factually wrong: one decodes decimal mode 2750 as octal 2750 and calls it safe despite a correct backend summary; three claim no_log is used when it is absent. All fail the content score. Three generic credential abstentions also differ from the unchanged AI static-risk reference; one overlaps the false-prose cases. Those reference/semantic disagreements are not all false factual claims. Path-only citations in mode-omission cases still fail the strict citation check.

The model often simply repeats backend source facts. This can improve the tool's output reliability, but does not show that adding the LLM benefits developers beyond evidence-only output. No developer study was performed.

## Validation and reproduction

The full suite passed **1,649 tests, two skipped**, and the separate requested-edit command passed **eight additional tests**. Frozen V5.2 analyzer sources still match their recorded hashes. Earlier failed smoke attempts, raw outputs, error records, summaries and backend provenance are retained.

See README.md, EXPERIMENT_NOTES.md, comparison-design.json, reviewed-results/, manual-ai-ratings.csv, requested-repair-results.json and requested-repair-ai-review.csv for exact methods, individual judgments and limitations.

Preview a narrow caller-requested draft without modifying source:

```sh
.venv/bin/python scripts/requested_repair.py \
  --root /path/to/repository --file tasks.yml --line 12 \
  --kind enable-tls-verification \
  --intent 'Endpoint authentication is required and its certificate is trusted.' \
  --output /private/path/to/proposal.json
```

Use protect-task-output for a supported direct debug display. Proposals are optional review artifacts, never automatically applied.

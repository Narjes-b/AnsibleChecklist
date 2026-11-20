# Further improvements and repeated experiment: V6

The same 48 explanation cases and fixed AI source reference were reused, and all 96 new outputs were explicitly reviewed. Model digest, context/output limits, temperature and comparison scheduling seed are unchanged. This remains an unblinded AI implementer's development experiment on exposed cases, not human validation or held-out generalization.

## Scoped pipeline: V5.2 to V6

| Measure | V5.2 / 48 | V6 / 48 | Change |
|---|---:|---:|---:|
| Accepted output | 47 (97.92%) | 47 (97.92%) | +0.00 pp |
| Decision agrees with unchanged AI source reference | 44 (91.67%) | 44 (91.67%) | +0.00 pp |
| Adequate complete explanation | 41 (85.42%) | 44 (91.67%) | +6.25 pp |
| Adequate explanation plus supporting citations | 38 (79.17%) | 44 (91.67%) | +12.50 pp |

All 48 scoped assessment states are constrained by a bounded backend predicate or required abstention. Summaries are backend-authored and citations backend-selected. The quality score still inspects every substantive model-reasoning claim; a correct summary does not rescue wrong reasoning. These values measure the complete assisted pipeline, not independent LLM reasoning accuracy.

The remaining four unsuccessful scoped cases comprise one invalid response (low confidence with missing limitations) and three cautious generic-module abstentions that disagree with the original AI supported-static-risk interpretation. The original labels are preserved; the three disagreements are semantic/reference ambiguity, not asserted evidence of false prose. No accepted scoped output was found to repeat the previous decimal/octal or invented-no_log rationale errors in this review.

## Full comparison

| Panel / condition | N | Accepted | Reference decision matches | Adequate | Adequate + citations |
|---|---:|---:|---:|---:|---:|
| all / window | 48 | 30 | 8 | 3 | 3 |
| all / scoped | 48 | 47 | 44 | 44 | 44 |
| controlled / window | 24 | 20 | 8 | 3 | 3 |
| controlled / scoped | 24 | 23 | 23 | 23 | 23 |
| real / window | 24 | 10 | 0 | 0 | 0 |
| real / scoped | 24 | 24 | 21 | 21 | 21 |

The source-only window prompt no longer requires nonexistent backend summary fields. Adequacy recovered from 0/48 to 3/48, but warning assessment remains weak: the model often uses unsupported to mean disapproval of unsafe code, or admits missing facts without choosing insufficient-evidence. Eighteen window calls were rejected; one scoped call failed its response contract. All remain unsuccessful outcomes. No inference retries or favorable-result replacements were used.

## Actual model-written edits when explicitly requested

On the same 12 repair sources, the local model generated 8/8 eligible drafts, and 8/8 passed both mechanical and isolated behavioral checks. All four already-correct/unknown-runtime sources were blocked BEFORE model generation; this is backend filtering, not model abstention.

The model receives only the original task, a caller-selected narrow change and declared intent. No complete reference AFTER task is supplied. Every delivered snippet was checked against its retained raw model response, and every raw prompt was inspected to verify BEFORE-only input. The AST edit changes only validate_certs false-to-true or task-local no_log true; guards, registers, tags, names and other arguments remain unchanged.

TLS tests reject an untrusted certificate, accept the fixture CA and preserve artifact contents. Logging tests suppress the synthetic secret in normal and forced-failure output and preserve registered results for later tasks. The eight original sources remain unmodified. AI edit review is in model-requested-edits-ai-review.csv; raw generations, payloads, validations and container outputs are retained under study/runs/llm-v6-model-requested-edits-2026-11-14/.

This is explicit requested-edit code generation, not autonomous warning triage or discovery of whether a fix is appropriate. The repeated spontaneous triage experiment still produced 0/8 eligible code proposals. Do not replace that zero with the requested-edit score. The existing deterministic requested-edit generator also passed 8/8 in V5.2; this tiny two-transformation panel does not establish that an LLM is necessary or superior.

Two extra live development probes also produced mechanically valid model drafts: a URI task with a guard/custom register, and a nested debug task with inherited logging control and a custom register. These broaden task-shape checks but were not behaviorally executed and are not independent natural-data generalization evidence.

## Implementation and validation

Typed permission facts and observed no_log state are preserved during prompt compaction, numeric/usage contradictions have bounded rejection checks, scalar command references cite actual argument lines, and mode-omission citations carry complete exact task spans. Source-only requests use a separate prompt. The requested-edit CLI supports --generator backend or --generator local-model; neither applies edits, and the local path has no deterministic fallback for failed generations.

Full test suite: **1,666 passed, two skipped**. See full-validation.log. Candidate hashes match freeze.json. Old results and human forms remain unchanged. Prior requested-repair source is preserved byte-for-byte at the SHA recorded in the V5.2 historical source map.

Reproduction details: README.md, reviewed-results/, manual-ai-ratings.csv, execution-failures.json, model-requested-edits-summary.json, model-requested-edits-ai-review.csv and the retained private run directories. The developer study remains deferred and no comprehension benefit is claimed. Paper files were not edited.

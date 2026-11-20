# Source-bound explanation improvement: V8.2

The local model now selects backend-certified claims. The backend authors factual prose, calculates bounded static assessments and supplies exact citations. The raw free-prose baseline is not renamed or overwritten. These are pipeline development results, not independent LLM reasoning accuracy.

| Pipeline | Adequate explanations with supporting citations | Rate |
|---|---:|---:|
| Previous free-prose window | 9/48 | 18.75% |
| Verified window | 41/48 | 85.42% |
| Previous free-prose scoped | 42/48 | 87.50% |
| Verified scoped | 45/48 | 93.75% |

| Panel / condition | N | Available | Decision matches | Adequate + citations |
|---|---:|---:|---:|---:|
| all / window | 48 | 48 | 41 | 41 |
| all / scoped | 48 | 48 | 45 | 45 |
| controlled / window | 24 | 24 | 24 | 24 |
| controlled / scoped | 24 | 24 | 24 | 24 |
| real / window | 24 | 24 | 17 | 17 |
| real / scoped | 24 | 24 | 21 | 21 |

## What changed

Explicit task/module bindings, typed permission interpretation, inherited output controls, visible definitions and missing-runtime contracts replace free factual decisions. The model selects claim IDs only. Invented/duplicate IDs, omitted primary claims, extra prose and changed source are rejected. Public result fields remain compatible, and the free style remains available.
Verified-window facts require every relevant proof span to be present in the original +/-6-line window or its original candidate-definition context. Full-file parsing supplies structural task identity, not unseen source values. Unsupported coverage produces a bounded unknown answer with the exact supplied window attached. Scoped mode supplies complete relevant source. No context-budget rejection occurred in the final 96 calls.
The opt-in CLI is --explain --explain-style verified-facts (also available in diff mode). Source/model/prompt/style identities separate checkpoint caches. Output provenance survives CSV, SARIF and PR annotations.

## Simulated reviewer passes

Simulated A rated 86/96 adequate under the fixed-reference rubric. Simulated B rated 86/96. Both checked actual selected text and source evidence; The reverse-order second pass repeats exact quote/span, packet-scope, raw claim-selection and typed-bit audits. The same automated evaluator conducted both passes. Their 100% consistency is an illustrative internal consistency result, not independent human agreement, and no human kappa/AC1 is reported.
The three full-source generic-credential abstentions disagree with the unchanged supported-static-risk references. Four additional fixed-window cases lack the decisive source values. All seven window and three scoped disagreements remain unsuccessful in the fixed-reference score; labels are not revised to raise it.

## Interpretation

The improvement comes from verified source contracts and deterministic interpretation, not evidence that the underlying 7B model independently reasons better. A deterministic c0 selection produces the same primary summary, decision and citations. Whether model-selected supporting claims improve relevance/comprehension over that control is unmeasured.
The cases are development-exposed, reviews are simulated by the same evaluator, and the extra shape checks are authored fixtures. No independent human correctness, general semantic repair correctness or developer comprehension benefit is established. Original human A/B forms remain blank; simulated forms are separate.
Earlier V8/V8.1 calls are retained as development experiments. V8.1 revealed a range-attachment bug for a citation inside rather than at the start of a window; V8.2 fixes it and was frozen and rerun on all 96 outputs. All attempts are retained; no failed final case was replaced with a favorable retry.
The eight prior requested-edit behavioral successes remain historical and separate from this explanation-only improvement. No autonomous-fix or human-comprehension result is invented.

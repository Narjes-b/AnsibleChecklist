# Neutral schema v3 — third live development pass

Source quotes now come from the backend, and the answer no longer requires defect-only prose. Literal setting checks improve on these reused development fixtures. **The runtime-evidence case still fails. No semantic acceptance gate has passed.**

| Case | Model outcome | Integrated result |
|---|---|---|
| Literal false setting | supported; not-actionable; high confidence | accepted; exact backend quote; expected condition outcome |
| False claim contradicted by true setting | unsupported; not-assessed; high confidence | accepted; exact backend quote; expected outcome |
| Missing runtime input | unsupported; not-assessed; low confidence | schema accepted, but wrong expected outcome; admits missing definitions and inability to determine source |
| Invalid anchor | no request | insufficient-context; expected gate outcome |

Three requests, one attempt each, **18.125 seconds**, stable existing Qwen digest. All three model responses are valid JSON and their citation locations are within supplied context. The backend attaches exact source lines without asking the model to reproduce indentation. The manifest records **3/4 engineering expectation matches**, including the deterministic invalid-anchor gate. This is not a real-project accuracy estimate, and the reused cases have influenced the prompt.

## Versioned change

- Response schema **3**, prompt **`local-review-v3`**. Neutral `summary` and `reasoning` replace required explanations of why an alleged defect is wrong. Earlier schema answers are not promoted into this contract.
- Condition assessment and actionability are separate fields. A visible source predicate can be supported while a change is not actionable or requires more context. Fixes require both supported condition and actionable change; other outcomes must have null recommendations/snippets.
- Model citations contain file and line only. The backend checks membership in the actual nonblank supplied context, rejects conflicting reads, and attaches the exact source quote. This establishes provenance, not semantic entailment.
- Assessment/actionability/evidence propagate through existing report formats. No detector findings, policy decisions or labels are replaced.
- **263 focused tests passed** across integrated LLM, reporting, findings and diff paths.

## Remaining concrete failure

The runtime-input answer lists missing evidence and says the definition may be in inventory, extra-vars or includes; its limitations state that the source cannot be determined. Yet it selects **unsupported**, rather than **insufficient-evidence**. A correct quote does not repair this reasoning error. The next guard must reject decisive condition outcomes when the model itself declares required decision evidence missing. This is a consistency check, not an automatic relabelling of the claim as true or false.

Follow-up guard, prompt `local-review-v3.1`: [consistency-recheck.json](consistency-recheck.json) verifies the original case hashes and applies the stricter structural validator to the preserved raw answers, with **zero model calls**. The contradictory runtime-input answer is now rejected; the two literal-condition answers remain structurally valid. This is not a new live pass or improved semantic score. Original answers/manifests remain unchanged; citation membership was checked in the original run and was not replayed in this structural recheck.

The guard treats `missing_evidence` as facts required to decide the **condition**. If nonempty, a decisive supported/unsupported outcome is invalid. Unknowns affecting only actionability belong in limitations. An omitted or incorrectly identified dependency can still evade this check; it does not replace rule-specific evidence completeness or human review.

The first case's actionability judgment also lacks a complete repository/runtime justification. This pass tests the explicit source condition; it does not certify actionability quality. Full raw answers and prompts remain adjacent for review. See the [parent record](../README.md) for reproduction and earlier unfavorable passes.

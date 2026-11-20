# Local LLM repair record — 2026-10-23

The owner requires local inference. **Current contract: response schema 3 / `local-review-v3.1`, with backend source quotations and separate condition/actionability fields. Semantic acceptance remains unvalidated.** The last live V3 answer misclassified missing runtime evidence; the current guard rejects that contradictory structure in replay, without new inference. The older 12-case results are historical evidence, not a current score; all three retained synthetic live passes below are development diagnostics. No real-project accuracy improvement is established.

## Implemented: transport, source anchors and response validation

- `--explain-host` accepts literal loopback HTTP/HTTPS endpoints. `localhost` is pinned to `127.0.0.1`; arbitrary hostnames, LAN/public addresses, credentials, extra paths, queries and fragments are rejected before opening a connection. Environment proxies and HTTP redirects are disabled. This requirement also applies to direct Python calls through `_call_ollama`.
- Source reads are bounded to 1 MiB, strict UTF-8, non-binary, and within the supplied repository/snapshot root. Absolute paths, traversal, `.git` paths and escaping symlinks cannot enter prompts. Missing/invalid/out-of-bounds anchors produce `llm_status=insufficient-context` without model or cross-file graph calls. Anchors are never clamped to another line.
- The server response schema now rejects extra properties and bounds string lengths. The runtime validator independently checks types, required/unknown fields, confidence enum, blank required values, nullable snippet/limitations fields, duplicate JSON keys, non-finite constants and length limits. Lower confidence requires explicit limitations.
- Requests set `num_predict=1024` as well as `num_ctx=8192`. The combined system/user prompt is limited to 64 KiB; response text to 128 KiB, HTTP envelope to 256 KiB and individual fields to 20,000 characters. Oversized input is rejected, not silently clipped. These byte limits are engineering bounds, not a tokenizer-based guarantee that the whole prompt fits the context window.
- Reject explicit incomplete/truncated model envelopes and invalid content types. Optional model failures stay attached to individual occurrences and do not create trusted fixes.
- CLI help states the local transport restriction. CSV/SARIF continue to receive their existing fields and disclaimers.

Validation: **166 tests passed** across `test_llm_explain.py`, output contracts, SARIF and both diff suites. Tests include a real loopback HTTP stub with hostile proxy environment variables and redirect attempts, plus malformed answers, response limits, invalid source/anchors and no-model-call behavior. No hosted endpoint or actual local model was contacted.

## Implemented: snapshot lifetime and graph cache isolation

- Explicit `--head` and `--staged` comparisons now run explanation, documentation context and playbook summaries while the analyzed head/index tree is still present. Report links remain rooted in the user's repository. Cleanup runs after reporting on both success and failure.
- Existing `--base-results` / `--head-results` inputs have no established source-tree correspondence. The CLI records source context as unavailable, skips source-derived summaries/documentation checks, and returns `insufficient-context` for explanation candidates without invoking a model. The Markdown summary explains the missing source. No current-checkout fallback is used for saved results.
- `compare_outputs` accepts a separate `head_source_root`; direct API callers retain their existing contract of supplying the live head source as `repo_root`. Passing explicit `None` disables source-dependent work.
- Symbol graphs are reused only within one enrichment operation through an operation-local context. Subsequent operations and standalone explanation calls rebuild rather than reuse a process-global root-only cache. Cleanup also runs on exceptions.
- Integration regressions use distinct committed, staged and unstaged markers, cover sequential/parallel head analysis, verify the prompt and summary source, and check worktree/index preservation and cleanup. Model responses in these tests are stubs.
- Ordinary working-tree comparisons still read the working tree; concurrent edits during a scan are not frozen by this patch. Arbitrary saved output reattachment requires future source-hash validation. Candidate-definition scope/completeness remains unresolved.

Validation for this step: **185 tests passed** across source/explanation, diff, output-contract, SARIF and annotation suites, including the saved-source notice. No live inference or measured accuracy claim.

## Implemented: explicit assessments and checked source quotations

This stage introduced **response schema 2**, prompt **`local-review-v2`**, subsequently superseded by V3 below. Identifiers are attached to successes, errors and source-insufficiency records. Historical responses are not rewritten or silently promoted.

- The model must choose `supported`, `unsupported`, or `insufficient-evidence`. Legacy explanatory fields remain for output compatibility, with explicit instructions to describe contradicted/unproven claims neutrally rather than inventing a defect.
- Supported and unsupported assessments require source citations with file, positive line and exact complete source quote. A per-call catalog contains only the primary window and candidate-definition lines actually supplied in the prompt. Citations to another file/line, invented text, or real but omitted source lines are rejected.
- Insufficient evidence requires named missing dependencies, low confidence and limitations. Unsupported/insufficient responses must set recommendation, code snippet and fix rationale to null; runtime validation rejects speculative fixes.
- Up to 16 citations and 16 missing-dependency descriptions are allowed, with bounded field lengths. Quote matching verifies text/provenance **only**: it does not establish scope, relevance, semantic entailment, truth or calibrated confidence. `llm_status=ok` means a valid checked response; the assessment remains an unverified model opinion.
- New fields (`llm_assessment`, `llm_evidence`, `llm_missing_evidence`, `llm_citations_checked`, schema/prompt version) survive canonical JSON, flattened findings, both CSVs (structured fields as JSON), SARIF properties, text, diff reports and annotations. Abstention/unsupported assessments remain visible without a fix. No native SARIF patch is created and detector policy/severity/occurrence counts are not replaced by model judgments.
- Re-enrichment clears previous `llm_*` fields before attaching the new result so a failed rerun cannot retain an old successful fix/assessment.

Validation: **253 tests passed** across LLM contract/reporting, exact snapshot integration, diff, findings, output-contract, SARIF and annotation suites; an additional focused check covers rejection of legacy answers. Source/citation and model responses in these checks are fixtures. A read-only loopback availability probe found the existing `qwen2.5-coder:7b` model, digest `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`; live model acceptance checks are a separate next diagnostic, not part of these test results.

## Live acceptance: first pass failed before inference

[Preserved first pass](../../study/local-llm-acceptance-2026-10-23/README.md): three synthetic model requests all returned HTTP 400; the invalid-anchor no-call gate passed. The 0.31.1 local Ollama server's journal identifies excessive grammar repetition, caused by generation-schema string bounds of 20,000 characters. No semantic model outcome can be scored from this pass. One separate diagnostic replay also failed and preserved the error body. The next fix must keep strict runtime bounds while making the constrained-generation grammar compatible.

The new [acceptance runner](../../scripts/check_local_llm_acceptance.py) records the integrated path, prompts/raw answers, model digest, expectations, hashes and partial progress. It makes one attempt per case, retains all mismatches/failures and never creates human labels. Harness + LLM/report checks: **136 passed**. These fixture checks did not detect the backend grammar incompatibility; the live failed pass remains evidence.

### Grammar repaired; semantic/quotation failures remain

[Second live pass](../../study/local-llm-acceptance-2026-10-23/grammar-repair/README.md): generation omits only string `maxLength` constraints; full runtime bounds remain. All three requests now produce JSON. **137 focused tests passed**. Two answers fail exact quotation because the model adds a space; the accepted low-confidence insufficiency answer still asserts definite runtime failure. The supported-condition case is misclassified as unsupported because the model confuses an example URL's actionability with the literal source predicate. No model quality gate has passed. Next: backend-supplied exact quotes and a fully neutral condition/actionability schema, with another preserved regression pass.

## Current contract: neutral schema v3 and backend quotations

[Third live development pass](../../study/local-llm-acceptance-2026-10-23/neutral-v3/README.md), **263 focused tests passed**:

- Response schema **3** / prompt **`local-review-v3`** removes defect-only required fields in favor of neutral `summary` and `reasoning`. Existing output explanation/context fields carry these for compatibility. V2 is preserved as history, not silently accepted by V3.
- Add separate `actionability`: actionable, not-actionable, context-dependent, not-assessed. Only supported + actionable allows a recommendation/snippet. The model's actionability remains unverified, and does not change detector policy.
- Citations from the model contain file/line only. Validate actual supplied nonblank context membership, reject conflicting reads, then attach exact source quotes in the backend. This removes pointless indentation-copy failures while preserving exact source provenance.
- The two literal-setting cases now meet their expected condition outcomes; all three model answers are schema valid. The runtime-input case still chooses unsupported while admitting missing definitions and inability to decide. The 3/4 engineering matches include a deterministic no-call case and are **not** accuracy.
- Next: enforce consistency between required missing evidence and decisive outcomes, then build rule-specific evidence and a genuinely independent acceptance instrument. Do not keep retuning these four development fixtures and present them as heldout validation.

## Next engineering steps

The V3.1 consistency guard requires insufficient-evidence whenever the model declares required **condition-decision** facts missing. It rejects contradictions, without converting them to true/false labels. A hash-verified [structural replay](../../study/local-llm-acceptance-2026-10-23/neutral-v3/consistency-recheck.json) rejects the known runtime-input answer and retains the two literal answers; no model or citation check was replayed. **147 focused tests passed** across harness, LLM/reporting and source snapshot suites. An unmentioned dependency can still evade this guard; rule-specific completeness and independent acceptance remain pending.

1. **Snapshot completion:** add source-hash validation for reattaching saved results and freeze ordinary working-tree input if concurrent-edit isolation is required. Head/staged lifetime and safe saved-result insufficiency are repaired above.
2. **Graph dependencies:** separate reachable, unresolved and unrelated definitions; report truncation and ambiguity rather than implying the first three candidate definitions are complete scope evidence. Preserve case-sensitive identifiers and explicitly handle legacy subject normalization. Operation-local caching is repaired above.
3. **Assessment acceptance:** exercise the new contract through the actual local model on deterministic synthetic supported/unsupported/missing-evidence cases, then on a frozen, human-reviewed instrument. Count malformed responses, quote failures and abstentions separately from semantic errors. Quote checking and explicit abstention are implemented above; real answer quality remains unvalidated.
4. **Evidence assembly:** ground subjects and full task/play units from frozen YAML; provide rule-specific dependencies. Fixed ±6-line windows and generic categories remain insufficient. Redaction can remove decisive evidence; record this as insufficiency rather than a false-positive/true-positive decision.
5. **Runtime and evaluation:** add an overall budget and incremental persistence, then run the same frozen local-only evaluation across supported cases, false positives, missing evidence, boundary cases and conflicting definitions. Report abstention/coverage and conditional error separately. Require a fresh, human-reviewed instrument before performance claims.

See the [recovery plan](recovery-plan-2026-10-23.md), [sampling methodology](sampling-methodology-2026-10-23.md), [frozen metadata results](../../study/evidence-metadata-2026-10-23/README.md), and [running repair log](recovery-progress.md).

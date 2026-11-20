# V5.2 improvement experiment

This is a development rerun on **previously exposed cases**, following the
owner's request to improve the pipeline and repeat the AI-only experiment.
No manuscript, original PDF/ZIP, human forms, or baseline results were edited.
The developer comprehension study remains deferred.

## What changed

- Nested task spans stop before the next sibling. A sibling's first line cannot
  be rebound to its preceding task. Ambiguous same-line tasks are unavailable.
- Source packets contain explicit facts about visible definitions, effective
  inherited no_log, parsed permission bits and unknown runtime values.
- Decisive citations are selected by the backend and constrained during
  generation. **This is not model-selected citation accuracy or proof of entailment.**
- The short summary is backend-authored, generated from those bounded facts.
  Free model reasoning remains separate and unverified. CLI/report text identifies
  both origins, and packet metadata records `prose_origin` and `citation_policy`.
- The model receives a neutral equivalent source question instead of being asked
  to repeat a detector accusation that may be contradicted by the source. The
  original detector message remains in the finding and private call telemetry.
- The prompt is shorter; opaque hashes/IDs and duplicate derived metadata stay
  in telemetry instead of consuming context. Decisive source spans are retained.
- Known explicit contradictions are rejected and retained as failed outcomes.
  These bounded checks do not certify arbitrary model reasoning.
- Task serialization indents tag sequences correctly for offline ansible-lint.
- An optional internal `review_intent` string on an occurrence supplies explicit
  caller assumptions separately from untrusted source/detector text. No new CLI
  flag is added. Suggestions remain optional and are never applied automatically.

Packet version is 2, contract version 4, prompt `local-review-v5.2`. Response
schema remains structurally compatible at version 3. Existing checkpoint keys
include prompt, packet, source and implementation identity, preventing reuse of
older candidate outputs as if they came from this revision.

## Preserved development history

The V5.0 and V5.1 smoke runs are retained under ignored study/runs/ directories,
with frozen packages in `study/llm-quality-improvement-2026-11-14` and
`study/llm-quality-v51-2026-11-14`. Prompt changes alone still produced a wrong
protected-output summary, and V5.0 also asserted unsafe permissions while their
runtime value was unknown. Those failures were retained, not replaced.

V5.2 passed all eight scheduled four-family smoke outcomes. Inspection confirmed
the scoped summaries and short rationales on the four development cases. This
is a small engineering check, not an independent quality estimate.

## Comparisons and grading

The same 48 explanation and 12 repair source cases are used. Keep the baseline
AI source judgments unchanged. Manually review every new delivered output using
the same content-and-citation criteria; do not reuse the old case-specific rating
tables as a grader for new text. Unavailable outputs remain unsuccessful.
The complete-output metric includes both the backend-authored fact summary and
the unverified model reasoning. It therefore measures the whole assisted pipeline,
**not independent improvement in LLM reasoning**.

The repair rerun supplies the same authored deployment intent through the typed
caller field instead of only embedding it in detector text. Record that interface
change as part of the pipeline comparison. No suggestion is forced or authored
by the backend. Evaluate generated code only if it is actually proposed, using
the isolated behavioral probes and separate AI semantic review. Authored control
edits never count as model repairs.

The same local Qwen model digest, 8192 context, 1024 output limit, temperature
0.1, 120-second request timeout and balanced comparison order are retained.
The baseline has one interrupted-unknown outcome; retain it in its denominator
and disclose it. Host workloads and cold/warm state make timing descriptive.

Scientific limits: a single non-blinded AI implementer reviews outputs after
seeing them, the cases are selected/convenience examples and are now development
exposures, and backend constraints contribute to decisions/prose/citations. No
population estimate, human correctness validation, or developer benefit is claimed.

## Reproduction

Use `scripts/llm_quality_study.py run` with this package and a fresh output
directory for the paired comparison. This candidate is already frozen; do not
overwrite freeze.json or archived attempts. Source review and ordinary human
evaluation gates remain in the original harness.

Use `scripts/llm_v5_experiment.py repair` for the separately identified AI-only
repair rerun with caller intent. The script does not fill human reviewer forms.
Use its `form` and `summarize` commands for a new explicit manual AI-rating CSV
and paired results, retaining notes and checksums. Model errors remain visible.

## Final results and explicit-request drafts

See [RESULTS.md](RESULTS.md) for the completed before/after comparison, all
condition results (including the window-only regression), remaining errors,
repair results and limitations.

`scripts/requested_repair.py` is a separate explicit-request command. It selects
no change automatically, uses no LLM, previews only a verified narrow TLS/debug
edit and never applies it. It produced eight mechanically and behaviorally
checked drafts on eight eligible fixtures and withheld all four ineligible cases.
Its code and results have separate checksums; it did not alter the frozen V5.2
explanation candidate or convert absent LLM proposals into model successes.

The eight additional command tests and AI-only fixture review are recorded in
requested-repair-validation.log and requested-repair-ai-review.csv. These are
bounded synthetic results, not independent human or production validation.

# Local-LLM evaluation results — qwen2.5-coder:7b (Q4_K_M, Ollama)

Real results from running `local-llm/eval/eval_cases.csv` (12 hand-selected
issues from `annotation-comparison/consolidated-comparison.csv`) through the
live local model, scored against Task 3's 6-dimension rubric
(`technical_correctness`, `contextual_grounding`, `diagnostic_clarity`,
`remediation_quality`, `uncertainty_calibration`, `actionability`, each
1-5). Full per-case scores and notes: `local-llm/task3-comparison.csv`.

This is not a polished success report. Two real pipeline bugs were found and
fixed during this evaluation (documented below, under "Pipeline bugs found
and fixed"), and the model itself showed a serious, systematic calibration
failure and at least one outright factual error. Both are reported here in
full because the task brief requires honesty about limitations over claimed
accuracy.

## Headline

- **11 of 12 cases** produced a schema-valid, non-empty explanation.
- **1 of 12 cases** (`V007PILOT-VARIABLE_REFERENCE_REASONING-001`) failed on
  every one of 4 attempts — one HTTP 500 from Ollama mid-generation, three
  truncated/malformed JSON responses that degrade into repeated whitespace
  padding instead of completing. Not a context-length issue (this case's
  prompt, 2.8KB, is smaller than several that succeeded). Root cause not
  identified; documented as a hard, reproducible failure rather than chased
  further.
- **11 of 11 successful responses reported `confidence: "high"` and
  `limitations: "None"` — zero exceptions**, including on two cases
  (`MAINTAINABILITY_COMPLEXITY-005`, `MAINTAINABILITY_COMPLEXITY-012`) where
  *both* independent existing reviewers (Reviewer A and Reviewer B/C) had
  labeled the same issue `uncertain`. The model never once used `medium` or
  `low` confidence or populated `limitations` across the whole eval set.
  This is the single clearest, most quantifiable finding here: **as
  integrated, this model's self-reported confidence carries no information**
  — it does not track problem difficulty, context completeness, or
  disagreement among other reviewers. Any downstream use of the
  `confidence`/`limitations` fields as a filtering or triage signal would be
  unfounded until this is fixed (e.g. via explicit prompting examples of
  calibrated low/medium responses, or a temperature/sampling change).

## Pipeline bugs found and fixed during this evaluation

1. **`source_context` field-name mismatch** (`scripts/prompt_template.py`,
   `scripts/explain.py`): both read `issue.get("source_context", "")`, but
   the actual column in `consolidated-comparison.csv` / `eval_cases.csv` is
   `original_code_or_issue`. Every explanation generated before this fix
   (prompt version `ansible-explain-v1`) was produced with **no real source
   code in the prompt at all** — confirmed by re-running the original 12
   smoke-test cases, 3 of which had the model report "the file is empty"
   (correctly, given it was given nothing) while the other 9 produced
   plausible-sounding, specific-looking explanations referencing variable
   names that do not actually appear anywhere the model could see —
   confabulated, not grounded. Fixed by falling back to
   `original_code_or_issue`; prompt version bumped to `ansible-explain-v1.1`.
   **The pre-fix outputs are not included in these results and should not be
   treated as representative of anything.**
2. **Ollama's default context window (4096 tokens) was silently truncating
   larger prompts.** The model's own advertised `context_length` is 32768
   (per `/api/tags`), but the running server log showed
   `n_ctx_slot = 4096` for every request until `num_ctx` was set explicitly
   in `explain.py`'s request options. This produced a schema-breaking
   response on the one eval case with the largest source context (14.8KB,
   `MAINTAINABILITY_COMPLEXITY-016`): the model's raw response used entirely
   different field names (`issue`/`description`/`recommendation`) and
   described a completely unrelated scenario (an `apt.conf.d/50unattended-
   upgrades` config that does not exist anywhere in that repository) —
   a clear symptom of the prompt (including the JSON schema instructions at
   the end of the system prompt) being truncated before the model could see
   all of it. Fixed by adding `--num-ctx` (default 8192) to `explain.py`,
   which resolved this specific case on retry. **8192 is a practical
   default for the ~8-12GB VRAM budget this model was selected for, not a
   guarantee against truncation on much larger inputs** — this remains a
   real constraint of running a 7B model locally on this hardware, not
   something this fix eliminates in general.

Both bugs are now fixed in the committed code; the results below are from
the fixed pipeline (prompt version `ansible-explain-v1.1`, `num_ctx=8192`).

## Rubric scores (1-5, averaged across the 11 scored cases)

| Dimension | Average | Note |
| --- | ---: | --- |
| Technical correctness | 2.4 | Dragged down by one outright factual error and one full misdiagnosis (see below) |
| Contextual grounding | 3.2 | Generally references real variable/task names from the supplied code; one case (excessive-nesting) stayed generic despite having real context |
| Diagnostic clarity | 3.3 | Usually clear and specific about *what* the model thinks is wrong, independent of whether that's correct |
| Remediation quality | 2.9 | Fixes are plausible Ansible patterns when the diagnosis itself is right; useless or actively wrong when it isn't |
| Uncertainty calibration | **1.1** | See headline — essentially flat across every case regardless of actual difficulty |
| Actionability | 3.1 | A developer could act on most of these, for better or worse, since they read as confident and specific even when wrong |

Full per-case numbers in `task3-comparison.csv`; do not average these into a
single score without reading the per-case notes — several low scores are
driven by one specific, different failure mode each, not a uniform quality
level.

## Named findings (most to least serious)

1. **One outright factual error about Ansible semantics**
   (`OBJECTIVE_CORRECTNESS-001`, rule `invalid-task-attribute-type`): the
   model states that `ignore_errors` "requires a direct boolean value" and
   that `ignore_errors: "{{ ansible_version.full is version('2.9', '<') }}"`
   "is not allowed." This is wrong — Ansible explicitly supports templated
   boolean attributes like this; it is idiomatic version-gating. The model's
   recommended fix (hardcode a boolean) would remove working, intentional
   logic. Stated with `confidence: high`. This directly contradicts the
   system prompt's explicit instruction: "Do not invent Ansible module
   behavior... that you are not confident about."

2. **One full rule misdiagnosis** (`VARIABLE_REFERENCE_REASONING-004`, rule
   `role-variable-precedence-collision`): the model's entire explanation is
   about an unused variable, a different defect category than the rule
   being evaluated (a variable set at two different precedence levels). The
   explanation never engages with precedence at all. Not a disagreement —
   a miss.

3. **A systematic pattern across all 3 "unguarded/unscoped variable" cases**
   (`VARIABLE_REFERENCE_REASONING-005`, `-007`, `-014`): in every one, the
   model confidently states a variable "is used without being defined,"
   when both independent existing reviewers labeled all three `negative`
   (not a real issue) — most plausibly because the variable is actually
   defined elsewhere (role defaults, `group_vars`) outside the single-file
   excerpt the model was given. The system prompt explicitly instructs:
   "do not... assume a variable is undefined... unless that is visible in
   the supplied context" — the model violates this instruction identically
   in 3 of 3 opportunities to do so in this eval set. This is the most
   actionable finding here: it suggests a structural blind spot (the model
   defaults to "undefined" rather than "unknown, outside scope" when a
   variable's definition isn't in view), not a one-off mistake.

4. **An unverifiable-scope overconfidence pattern**
   (`MAINTAINABILITY_COMPLEXITY-012`): the model asserts a handler is unused
   "anywhere in the playbook" — a claim that cannot be verified from a
   single-file excerpt — with `confidence: high` and no limitation noted.

5. **One case where the model disagrees with both existing reviewers on a
   substantive, plausible basis** (`OBJECTIVE_CORRECTNESS-004`,
   non-idempotent `chown`): both existing reviewers called this `negative`;
   the model argues the non-idempotency concern is real. This is flagged
   here, not resolved — whether the task uses a raw shell `chown` (genuinely
   non-idempotent) or the `ansible.builtin.file` module (idempotent)
   determines who's right, and the available excerpt doesn't settle it.
   Per the task brief, this is left open for human adjudication.

6. **Generic, under-grounded explanation despite real context being present**
   (`MAINTAINABILITY_COMPLEXITY-016`): even after the context-window fix
   delivered the real 14.8KB source to the model, its explanation stayed
   generic ("nested blocks can make the playbook harder to read") rather
   than referencing the actual task names visible in that context (Hardware
   Configuration, Raspberry Pi Configuration, Device Trim), which the system
   prompt explicitly asked for.

## What this does and does not establish

- This evaluates one 7B model, one prompt version, one hardware
  configuration, and 12 cases. It is not a claim about local LLMs in
  general, nor a final verdict on this model — it is what was actually
  observed in this run.
- The local model's output **remains a recommendation, not an accepted
  label**, exactly as the task brief requires. None of Task 1's agreement
  statistics were touched by this evaluation, and `task3-comparison.csv`'s
  `labels_agree` column records a human(-equivalent) judgment call, not an
  automatic resolution.
- The single clearest, most reusable finding for future work on this
  pipeline is the confidence-calibration failure (finding set, headline
  section) — before this model's `confidence` field is used for anything
  (triage, filtering, highlighting cases for human review), that field
  needs to be shown to actually vary with correctness or evidence quality,
  which it did not in this eval.

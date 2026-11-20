# local-llm explainer: bugs found and verification (2026-10-18)

Tested this pipeline end-to-end for the first time (per `INTEGRATION.md`, it had
never actually been run against a live model). Ollama 0.31.1 was already
installed; pulled `qwen2.5-coder:7b` (4.7 GB) and ran it against
`local-llm/eval/eval_cases.csv` (the 12-case hand-picked eval set). Found two
mechanical bugs (both fixed in this branch) and one deeper limitation that is
**not** fixed and likely can't be fixed by a prompt/schema change.

## Bug 1 (fixed): `source_context` was never populated

`local-llm/scripts/prompt_template.py::build_user_prompt` read
`issue.get("source_context", "")`, but neither CSV this pipeline is meant to
run against (`eval/eval_cases.csv`, `annotation-comparison/consolidated-comparison.csv`)
has a `source_context` column — the actual column is `original_code_or_issue`.
Every prompt sent to the model had an **empty code snippet**.

Evidence this was silent, not visibly broken: the one pre-existing output file
in this branch, `local-llm/outputs/V007PILOT-MAINTAINABILITY_COMPLEXITY-001.json`,
has `context_supplied_to_model.source_context: ""` and the model's answer is a
generic "the code snippet is incomplete and lacks context" for every field —
easy to mistake for a model limitation rather than an empty-input bug.

Worse: re-running the same empty-context case a second time, the model did
**not** reliably admit it had nothing. It fabricated a plausible-sounding
variable name (`release_path`) that appears nowhere in the input, and rated
its own invention `"confidence": "medium"`. So the failure mode under this bug
was nondeterministic between "admits it has nothing" and "hallucinates with
a straight face" — the second is the dangerous one, since nothing in the
output flags it as ungrounded.

**Fix applied** (`local-llm/scripts/prompt_template.py`):
```python
source_context=issue.get("source_context") or issue.get("original_code_or_issue", ""),
```

## Bug 2 (fixed): model could silently ignore the required JSON schema

`explain.py` called Ollama with `"format": "json"` (valid-JSON-only, not
schema-constrained). On 1 of 12 eval cases the model returned a well-formed
but totally different JSON shape — `{"response": "<a prose paragraph>"}`
instead of the 10 required keys. `validate_explanation()` correctly caught
this and marked the record `completed_with_warnings` rather than `ok`, which
is good defensive design — but the audit record for that issue is still
useless as structured output.

**Fix applied** (`local-llm/scripts/explain.py`): Ollama 0.31.1 supports
schema-constrained structured output (`format: <json-schema-object>`, not
just the string `"json"`). Added `RESPONSE_SCHEMA` (the same 10 keys,
`confidence` constrained to the enum, all 10 marked `required`) and pass that
instead of the bare string. Re-running the same 12 cases: **12/12 `ok`, zero
schema violations** (previously 11/12, with the one prose-only failure above).

## NOT fixed, and not fixable by a prompt/schema patch: false-positive blindness

This is the result that actually matters for whether this pipeline is usable.
5 of the 12 eval cases have a ground-truth label of `negative`/`not-applicable`
from two human reviewers who agreed the detector's finding was a false
positive. `SYSTEM_PROMPT` explicitly instructs the model: *"Not every detected
issue is a real defect... if the supplied evidence shows the flagged condition
is a false positive... say so plainly rather than rationalizing the detector's
claim."*

With both bugs above fixed and real source code reaching every prompt:

- **False positives caught: 0 of 5.** Every one of the 5 known-FP cases came
  back as a confirmed, explained defect.
- **Confidence: `"high"` on 12 of 12 cases**, including the 3 cases the human
  reviewers rated `uncertain`. The model never once hedges.

Example (`V007PILOT-VARIABLE_REFERENCE_REASONING-005`, ground truth
`negative`/`not-applicable`): the human reviewers' correct call relied on
`deploy_next_release_path` being defined earlier in a **different file in the
same role** (`01-register-variables.yml:14`). `source_context` only ever
contains the single file+line range the detector flagged — the model has no
way to see that other file, so it confidently (`"confidence": "high"`)
reports the variable as undefined and recommends "fixing" something that
isn't broken.

This is a scope-of-context problem, not a formatting problem: fixing it would
mean assembling cross-file/role context per issue (e.g. resolving `include`/
`import_role` graphs, pulling in `defaults/`, `vars/`, and files that run
earlier in the same role) before calling the model — a real feature, out of
scope for this pass. Flagging it here so it isn't mistaken for "fixed" just
because the pipeline now runs cleanly end-to-end: **clean output ≠ correct
output**. As shipped (even with both bugs fixed), this pipeline would rubber-
stamp every detector finding as a real defect, which is close to the opposite
of the "catch false positives" use case it's meant to help with.

## Reproducing this verification

```bash
# Ollama must be running with qwen2.5-coder:7b pulled (ollama pull qwen2.5-coder:7b)
cd local-llm/scripts
python explain.py --input ../eval/eval_cases.csv --id-col issue_id \
  --out-dir ../eval/verification-2026-10-18
```

`local-llm/eval/verification-2026-10-18/` in this branch holds the 12 audit
records from the run described above (12/12 `ok`, 0/5 false positives caught,
12/12 `confidence: high`) — compare `explanation` against the ground-truth
`original_detector_annotation`/CSV labels per issue.

## Files changed in this branch

- `local-llm/scripts/prompt_template.py` — Bug 1 fix (one line)
- `local-llm/scripts/explain.py` — Bug 2 fix (schema-constrained `format`)
- `local-llm/eval/verification-2026-10-18/*.json` — 12 audit records from the
  verification run above, for reference
- `local-llm/KNOWN_ISSUES_2026-10-18.md` — this file

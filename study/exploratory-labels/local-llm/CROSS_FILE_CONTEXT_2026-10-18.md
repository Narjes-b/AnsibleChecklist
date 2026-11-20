# Cross-file variable context: implemented, tested on the real false-positive case, mixed result

Follows the recommendation from the earlier accuracy discussion: instead of
RAG or fine-tuning, reuse the project's own semantic engine
(`symbol_index.py`'s `RepositorySymbolGraph`, already built for the
`unguarded-variable`/`set_fact`/etc. detectors) to show the LLM other
same-repository definitions of a flagged variable, since the single-file
blind spot was the measured root cause of the 0/5 false-positive catch rate
in `KNOWN_ISSUES_2026-10-18.md`.

## What was added (`llm_explain.py`)

- `_variable_name_from_occurrence`: recovers the flagged variable's bare
  name from `occurrence["semantic_subject"]` (the only place it survives
  onto a canonical occurrence — see `occurrences.py::_semantic_subject`).
- `_symbol_graph_for`: lazily builds one `RepositorySymbolGraph` per repo
  root via `build_repository_symbol_index` and caches it (one build per
  scan, not per occurrence). Never raises.
- `_cross_file_variable_context`: calls `graph.possible_definitions_of(name)`
  (deliberately repo-wide, not scope-filtered — the point is showing the
  model evidence it would otherwise never see at all) and appends up to 3
  other definition sites, each with real source lines, to the prompt.
- `_locate_definition_line`: a correction needed once real data was tested
  against — `VariableDefinition.line` from `symbol_index.py` is sometimes
  the enclosing task/block's line, not the exact mapping-key line (see
  below). Searches forward up to 30 lines from the reported line for the
  literal `"<name>:"` key and re-centers the snippet there.
- `SYSTEM_PROMPT` extended to explain this new section and explicitly tell
  the model it must reason about applicability itself, not assume a listed
  definition is in scope.

## Real validation: the exact false-positive case from the eval

Cloned `mageops/ansible-infrastructure` at the exact commit
(`5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`) behind
`V007PILOT-VARIABLE_REFERENCE_REASONING-005`, where both human reviewers
agreed `deploy_next_release_path` (used at
`roles/cs.deploy/tasks/07-relink-releases.yml:16`) is **not** a real
false-positive-worthy issue because it's `set_fact`'d earlier in the same
role at `01-register-variables.yml:14`. Ran the actual new code against the
real files (not the eval CSV, which has no real repo to query).

**Bug found and fixed first**: `symbol_index.py` reported this definition's
`line` as `1` — the *first* task in the file (`"- name: Set deploy release
id"`, an unrelated task), not line 14 where `deploy_next_release_path:` is
actually set. Before the `_locate_definition_line` fix, the model was shown
"line 1: `- name: Set deploy release id` / `block:`" as the "definition,"
which is actively misleading. After the fix, it correctly shows lines 12-14,
the real `set_fact:` assignment.

**Result with the fix, on the exact real case:**
- Confidence dropped from `"high"` (before this feature existed, confidently
  wrong) to `"medium"`, with an explicit limitations note — strictly better
  calibration, and the system prompt's "don't guess" instruction is visibly
  working.
- **But it still did not call this a false positive.** With the correct
  evidence sitting directly in the prompt (`tasks/01-register-variables.yml:14:
  deploy_next_release_path: "{{ deploy_releases_dir }}/{{ deploy_release_id }}"`),
  the model's `limitations` field claimed "the exact location... cannot be
  determined from the provided context alone" — which is simply false; it
  was given exactly that location. It still recommended a "fix."

## Honest conclusion

Giving the model correct grounding evidence is necessary but **not
sufficient** on its own with `qwen2.5-coder:7b` at this size. The gap isn't
only "missing information" (that part is now fixed and reusable for any
variable-shaped finding) — part of it is this model's reasoning/instruction-
following not reliably integrating a second evidence section into its final
judgment. This matches a known weak spot of smaller local models: multi-
source integration under a rigid JSON-schema output constraint. Candidate
next steps, not done here:
- A larger model (14B) re-run through the same harness to see if the gap is
  model-capability-bound.
- Self-consistency (sample 2-3x, only surface a false-positive override if
  it agrees across samples) rather than trusting one pass.
- Deciding this family (`unguarded-variable`/cross-file-dependent rules)
  isn't worth model judgment at all, and instead encoding the override as
  deterministic logic in code (symbol_index.py already *has* the answer —
  only the model's framing of it is unreliable) — i.e. let the detector's
  own resolution answer the false-positive question directly, and use the
  LLM only for the explanation text, not the verdict.

No regression found: re-ran the unrelated `openfoodfoundation/ofn-install`
scan (FQCN/task-naming findings, no variable-shaped occurrences) after this
change — identical counts, no crashes, confirming the new symbol-graph build
step degrades safely when there's nothing variable-shaped to use it for.

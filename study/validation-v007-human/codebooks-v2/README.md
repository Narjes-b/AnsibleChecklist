# Codebooks v2.0 (v2.0 confirmed 2026-10-16; v2.1 frozen 2026-10-16, see FREEZE_RECORD.md)

`COMMON_V2.md` plus seven `FAMILY_*_V2.md` replace the v1 codebooks for pilot 2 and later. The v1 files remain unchanged.
Before pilot 2: (1) update the form generator for the new fields (`semantic_reason`, `actionability_reason`, controlled
`external_context_type`) and the validator; (2) run the bundle scanner on every bundle; (3) record SHA-256 of these files in the freeze record; (4) adjust any rule whose operational definition here needs a detector change (below).

## Detector changes implied (v0.0.7.1 candidates)
- Bug-reference regex: add `Fixes|Closes|Resolves #n`, issue URLs and tracker keys.
- Bot/merge commits: skip for message rules.
- Non-Ansible YAML: already excluded for unnamed-task; verify other rules.

## Form schema v2 (implemented)
`scripts/v007_review_schema_v2.py`: `build` writes a blank v2 form from a v1 form (columns: v1 visible columns +
`semantic_label, actionability_label, context_sufficient, requires_external_context, external_context_type,
semantic_reason, actionability_reason, bundle_issue, evidence_notes, reviewer_notes`; `codebook_path` points to the v2 family file);
`validate` reports ALL problems of a returned form (controlled lists, label/reason consistency, `bundle_issue` for
unreviewable items, notes for uncertain/other). Reason lists are read from the v2 family files, so editing a codebook changes the validator.
Not yet adapted to v2: `export_v007_reviewer_packets.py`, `v007_human_agreement.py` (still v1 columns) and the pilot validator; do this when pilot 2 samples are generated.
The test caught a real gap: the style family had no uncertain reasons (added `policy-unknown`, `repository-policy-evidence-missing`).

## Bundle generator v2 (implemented, not yet wired into sample generation)
`scripts/v007_bundle_context_v2.py` provides `static_context` and `review_context` (same signature and return as the v1 functions).
Checked on the 300 non-commit pilot-1 items against the local clones: every bundle states a construct line (197 name the enclosing task found from the anchor line, 103 are explicit file-level findings; the hashed object id is never shown), 0 scanner hits, tree listings complete (limit 400 paths, otherwise per-directory counts), whole-word reference search, handler files for handler rules, windows of ±100 lines. When the run provides a kind-prefixed semantic subject (pilot 2), that name is used.
Review bundles (commit items) were tested on temporary repositories only: all changed paths, including non-YAML, with a stated per-file cap.
Remaining wiring: call these functions from the pilot-2 sample builder in place of the v1 ones, and add a bundle validator (scanner exit 0, construct line present, truncation statements) to the build.

## Gates and reports (implemented)
- `scripts/v007_bundle_validate_v2.py <dir>`: build gate for bundles (scanner clean, construct line, stated cuts, one diff section per changed path); prints the defect rate for the 5 % gate.
- `scripts/v007_agreement_v2.py`: validates two returned v2 forms, then reports agreement per family and evaluates the three pilot gates (decided κ ≥ 0.70 target / 0.60 minimum; uncertain+unreviewable ≤ 25 %; bundle issues ≤ 5 %).
- `scripts/v007_label_comparison.py` already works on v2 forms for rater-vs-rater or rater-vs-reference comparison.
Not adapted: `export_v007_reviewer_packets.py` and `validate_v007_validation_pilot.py` are tied to the frozen pilot-1 master and paths; adapt them together with the pilot-2 sample builder.

## Verification against detector source (2026-10-16)
Checked and corrected: commit-message format (50/72, blank line), bug-reference forms (v0.0.7.1 regex), long-statement (physical line, tab expansion, exemptions),
task-name length and special characters (strictly greater), large-task LOC (strictly greater), high-coupling (strictly greater; dispatcher files),
unnecessary-abstraction (full justifying-key list), missing-abstraction (more than 10 leaf tasks without includes/roles; the earlier "repeated similar tasks" wording was wrong).
Still taken from policy rather than code: placeholder-credential cases, module-level `no_log`, redirected-module version handling, release-note convention fallback.

## v2.1 (2026-10-16): changes after the pilot-2 dry run
v2.1 clarifies undefined rules and addresses bundle defects. It adds: COMMON C10 (file-level findings), C11 (unrecomputable metrics), C12 (inline suppressions), C13 (new reasons);
predicates for become-scope-too-broad, missing-file-extension, duplicate-task-names, complex-expression, undocumented-complex-task, incomplete-task,
unused-handler, silent-error-suppression, missing-handler, overriden-keys, insufficient-modularization, unexpected-task-location, duplicated-code,
overriding-facts, untested-override-change, release-only and merge commits; new reasons (`confirmed-broad-privilege`, `confirmed-redirect`,
`confirmed-removed-syntax`, `condition-absent`, `redaction-hides-value`, ...). Predicates were read from the detector source where it was available;
`duplicated-code` and parts of `silent-error-suppression` follow the rule description and are marked as such. No human has labelled under v2.0 or v2.1.

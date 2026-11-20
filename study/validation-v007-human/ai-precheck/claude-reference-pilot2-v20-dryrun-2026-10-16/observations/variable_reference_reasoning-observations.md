# Observations: variable_reference_reasoning (pilot2, 25 items)

## Bundle defects / header problems
- Placeholder subject `location` on file-level or unnamed findings (001, 002, 006, 009, 012, 015, 017, 021, 025): the header names no variable/expression, which violates the C7 contract. I judged these by scanning the whole file/task instead of marking them unreviewable, but a stricter reading of C2/C7 would make them bundle-defect. 001, 002, 009, 015 (missing-bool-filters, overriding-facts) are file-level with no task named, so the detector's claim is not even stated. Needs a policy decision.
- Input CSV `codebook_path` is `codebooks-v2/FAMILY_VARIABLES_V2.md` while bundle headers still say `codebooks/FAMILY_VARIABLES.md`. check_labels.py derives the v2 file via v2_family_file(), which appends `_V2` again and crashes on the v2 path (FileNotFoundError ..._V2_V2.md). I ran the checker on a temp copy of the input with the v1 path (tmp/vrr_in_v1.csv). Result: 0 problems.
- 005: search output truncated ("145 further matches not shown") so the definition of `net` could not be confirmed or excluded; item also sits in a topology defaults data file, not a task.
- 007, 013: only a +-100 line window of a large file is shown; the whole-commit search compensated, but the window itself cannot show later uses in the same file.
- 004, 010, 020, 023: very long reference-search listings dominate the bundle (27-182 matches); definition lines are hard to find.

## Codebook ambiguities
- Negative reason list (visible-definition, visible-guard, valid-precedence, scope-mismatch) has no code for "no such condition present" (e.g. missing-bool-filters 001: nothing is missing; unused-registered 022: variable is consumed by a template). I used `other` (001) or reused scope-mismatch/valid-precedence; suggest adding `condition-absent`.
- overriding-facts (002, 009, 015): intentional re-set_fact patterns (block/rescue alternatives, register-then-consume in loops, reset of scratch fact after use) technically overwrite a fact. Family file gives no predicate for when overwriting is benign. I labelled all three negative (valid-precedence); 015 is borderline (low confidence).
- Unguarded-variable: family rule says undeclared input without guard is positive/advisory, but 005 (framework-supplied `net`) and 020 (`os_migrate_data_dir`, required extra-var enforced by a validate_data_dir role) are caller-supplied inputs. The line between positive and uncertain/runtime-input-possible is not defined; 020 labelled positive (low confidence), 005 uncertain.
- redundant-default-value (003): set_fact `{}` equals role default but also resets caller overrides, so it is not purely redundant in effect. Labelled positive/advisory.
- precedence-collision (004, 010): same-valued duplicate in defaults and vars is positive by rule; actionability of a same-value collision is low.

## Detector false-positive patterns
- 019 use-before-definition: module parameter key `nics:` treated as a variable read.
- 022 unused-registered-variable: variable consumed by a Jinja template in the same role (templates not scanned), and the role is vendored (community/jdauphant.nginx), out of sampling frame (C9).
- 011 unguarded-variable: `eq` is a Go-template function in a go-task Taskfile (non-Ansible YAML sampled).
- 012, 006, 017, 021, 025 shell/export rules: variables defined inside the same script/command, `command` module with no shell expansion (012), `\$server` inside single-quoted sed (021). Detector appears not to track in-script definitions.
- 008, 023, 024 unguarded/use-before-def: definitions exist elsewhere in the commit (playbook vars, set-facts.yml, env.yml files).

## Process notes
- 15 of 25 labelled negative; decisive facts mostly came from the bounded search listing, so search completeness matters.
- No residual secrets noticed in bundles (redaction markers present in 002, 003, 024); none copied.

# Observations: maintainability_complexity (pilot2, 24 items)

## Codebook gaps
- The v2 family file defines no predicate for complex-expression (001, 013, 024), undocumented-complex-task (011, 023), incomplete-task (006, 018) or unused-handler (012). Labels for these rest on rule names only. 006 was left uncertain for this reason (bundle_issue=codebook-ambiguous); 018 positive on a low-confidence reading (explicit "remove once" marker = incomplete).
- No thresholds are given for large-task / large-play / large-playbook / complex-expression, and the bundles do not show the detector's measured value or threshold. "Measured values reproducible from the bundle" cannot be checked without them. Items 007, 008, 009, 013, 014, 019, 020, 021, 024 were judged on perceived size; 008 (169 lines, ~60 comment lines, 11 tasks) is uncertain because it is unclear whether comments count.
- Negative reason list has no code for "handler is notified indirectly" (012: notify via include_role apply:) or "stub/marker absent"; `other` was used. Suggest adding `handler-referenced` / `dynamic-reference` to negatives for unused-handler.
- deprecated-modules (003, 015): family file defers to an "objective family" for reasons; positive reason `confirmed-defect` used. Bare `include:` is removed (2.16), not merely deprecated; the rule label "deprecated" is loose. Without a pinned ansible version both rely on C1 (2.21).
- Actionability reasons for this family are only the common set; none fits "refactor optional / legacy code" well (used needs-owner-decision, policy-optional, low-value).

## Bundle defects and quirks
- Header line "Asserted subject: location" appears for file/line-anchored findings (001-002, 004-008, 011-020, 023-024); it is a placeholder, not a subject, and no detector message/metric is shown.
- 011: lines 208-287 are one "[REDACTED PRIVATE KEY BLOCK]" plus ~80 "[REDACTED PRIVATE KEY CONTENT]" lines in the middle of a Checkmk task file; almost certainly an over-redaction that hides the rest of the file (real content likely further tasks). Did not affect L136 judgement, but would be unreviewable for any anchor there. Possible redaction regex swallowing to EOF.
- 013: anchor line 70 is inside a task starting at 67 (fine). 024: anchor 312 in task at 308 (fine).
- 022: bundle is a +-100 line window of a 1115-line file with the statement that an indecisive window should be unreviewable; sufficient here.
- Input CSV codebook_path is already the v2 path, but check_labels.py applies v2_family_file again (FAMILY_MAINTAINABILITY_V2_V2.md not found). I ran the checker on a temp copy of the input in /tmp with the v1 path; no repo file edited.

## Detector false-positive patterns
- unused-handler 012: handler fired through include_role `apply: notify:`.
- complex-playbook 002: applied to a role task file (tasks/section_5/...), wrong unit. large-play 007: play anchored is the small first play of a 14-play examples file (file-level size attributed to a play).
- large-task 009 and 021: tasks of 20-23 lines flat parameter lists; likely mis-measured (comments or whole file) or very low threshold.
- complex-expression 013/024: flat or-/and-chains of defined/default checks flagged; readable.
- Duplicate-per-file findings: 015 (11 identical bare includes) would multiply; consider one per file.

## Process notes
- Positives are mostly low-value maintainability notes (advisory). Real defects are the bare `include:` items (003, 015) and shell-instead-of-module (010, 022; 010 uses `command`, rule name says shell).
- 010 handler context: changed_when: true on a reload is intentional.

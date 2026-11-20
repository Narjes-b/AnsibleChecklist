# Codebook v2.1: rules common to all families

Status: confirmed by the study owner on 2026-10-16 (see `../codebooks-v2-draft/POLICY_DECISIONS.md`, rows 1-16).
The frozen v1 codebooks stay as archived evidence. For pilot 2 and later, reviewers use
`REVIEWER_INSTRUCTIONS.md` (v1) as amended here; where they conflict, this file wins. A family file in
this folder replaces the v1 family file.

## C1. Ansible version
Judge behaviour against **ansible-core 2.21** (the version used for the run) unless the bundle shows a pinned version
or a `requires_ansible` / `ansible-core` constraint, which then wins. Do not rely on memory of older releases. If
the answer differs across versions and the bundle does not decide, label `uncertain` with external context type `ansible-version`.

## C2. `uncertain` vs `unreviewable`
- `unreviewable`: the bundle is defective or lacks the evidence the rule needs (cut-off listing, missing subject,
  missing file, redaction hides the decisive text, anchor not on the construct). Reason `bundle-defect`; name the defect in `bundle_issue`.
- `uncertain`: the evidence is complete but the judgment is open (policy unknown, runtime value, convention).
Never use `uncertain` for a bundle defect.

## C3. Outside knowledge
Facts that are not in the bundle (module behaviour of a dependency, another repository's content) are not evidence
unless they are Ansible documentation facts for the version in C1. Otherwise `uncertain` with `external_context_type = collection-docs` or `other-repo-file`.

## C4. Separate the questions
1. `semantic_label`: is the **documented condition** present (rule's own predicate, family file)? Policy preferences do not change it.
2. `actionability_label`: should someone change it here? Separate from 1.
3. Scope: if the item is outside the rule's scope (bot/merge commit for message rules, vendored third-party role, non-Ansible YAML),
   label `negative`, reason `out-of-scope`, and say what it is in `evidence_notes`.

## C5. Reason codes
Two fields replace `reason_code` from pilot 2 on: `semantic_reason` (why the semantic label) and `actionability_reason`
(why the actionability label; `not-applicable` when the semantic label is negative/unreviewable).
Every family has positive semantic reasons (below); common ones: `confirmed-defect`, `confirmed-policy-violation`,
`out-of-scope`, `bundle-defect`, `insufficient-source-context` (uncertain only), `other` (needs a short note).
Common actionability reasons: `fix-is-proportionate`, `low-value`, `policy-optional`, `test-or-fixture-context`, `needs-owner-decision`, `not-applicable`.

## C6. `external_context_type` (controlled)
`none`, `ansible-version`, `collection-docs`, `other-repo-file`, `runtime-value`, `inventory-or-caller`, `organization-policy`, `other`.
Rule: `requires_external_context = no` ⇒ type `none`; `yes` ⇒ any other value.

## C7. Evidence the bundle must contain (generator contract)
The asserted construct (task, variable, attribute, path) is named in the header; the directory listing is complete or says exactly what is cut;
non-YAML files of a commit appear in its diff; imported handler files are shown for handler rules; no residual secret/email (scanner exit 0).
A bundle violating this is `unreviewable` / `bundle-defect`, and counts toward the 5 % bundle-defect gate.

## C8. Overlapping rules
Judge each item on its own rule's predicate; record overlap in `evidence_notes` (for example read-only probe also matched by non-idempotent-command).

## C9. Out of the sampling frame
Vendored third-party roles, non-Ansible YAML (Kustomize/Helm/go-task/mkdocs files), and bot or merge commits for message rules, should not be sampled (plan v2 §6). A commit whose subject starts with `Merge ` (branch, pull request, remote-tracking) is a merge commit even when a shallow clone hides its parents. If one appears anyway: C4 item 3.

## C10. File-level findings and line-1 anchors
Some rules are about a whole file or role (missing-abstraction, unstructured-module, role-readme-absent, duplicated-code, molecule-test-absent). A line-1 anchor with a file-level
construct line is NOT a bundle defect for these: judge the whole file. Mark a bundle defect only when the evidence needed for the rule's predicate is missing (cut-off listing,
hidden decisive text, missing imported file). For rules whose predicate names a block or pair (unnecessary-abstraction, duplicated-code) the bundle's "Computed facts" section
lists the candidate blocks; if it does not and the file is too large to judge, use `unreviewable` / `bundle-defect`.

## C11. Metrics you cannot recompute
Threshold rules (large-task, large-play, large-playbook, complex-playbook, high-coupling, excessive-nesting) are verified for their metric by an automatic oracle, not by you.
`LOC_task` and similar counts are taken from a normalised re-serialisation of the YAML, so they differ from the source line count: do not try to reproduce them. Judge (a) the analysis unit is right,
(b) the construct is visibly of the stated kind/size order, (c) the bundle's computed facts if shown. A threshold-only judgement is `negative` with `wrong-analysis-unit` only if the unit is wrong.

## C12. Inline suppressions
An inline lint-disable (`# noqa`, `# yamllint disable`, `# ansible-lint: skip`) or an explanatory comment on an accepted violation does not change the semantic label; it makes actionability `not-actionable` with reason `policy-optional`.

## C13. Reasons added in v2.1
Negative: `condition-absent` (the documented condition is simply not present), `out-of-scope`. Common negative also: `accepted-in-2.21` where a version rule applies.

# style_policy reference-reviewer observations (50 rows)

## (a) Counts and hardest items
Semantic: positive 29, negative 10, uncertain 11, unreviewable 0.
bundle_issue != none: 22 = 17 codebook-ambiguous (undefined thresholds/conventions) + 5 `other:no repo tree to verify molecule absence` (008, 019, 029, 039, 049).

Five hardest:
1. 003 (inconsistent-naming-convention, lfops): codebook never defines the predicate. File mixes Sentence-case names with lowercase command-mirroring names (l.3, 46, 94, 110). Labeled positive/low; a careful peer could say negative (deliberate convention).
2. 011 and 032 (variable-naming-convention): lowercase snake_case with a prefix (`launcher_`, `magento_`) that differs from the role name. Positive under a role-prefix reading, negative under snake_case-only. Labeled uncertain.
3. 005/027/037/047 (long-task-name, names 89-97 chars): no threshold in codebook or instructions; labeled uncertain. Positive under an 80-char reading, negative under 100/120.
4. 036 (long-statement, 161 chars) and 015 (187): threshold unknown; labeled positive (low/medium) because well above common 120-160 limits, but 036 is borderline.
5. 023 (duplicate-task-names): the duplicate is a block name and its only child task. Labeled positive/medium.
Also hard: 045/014/035/025 (inconsistent naming negatives); all low confidence.

## (b) Bundle defects
- Molecule-test-absent (008, 019, 029, 039, 049): the bundle contains only the role's tasks/main.yml. No directory tree/listing, so the predicate (absence of a molecule/ scenario) cannot be checked at all. All five labeled uncertain. This is a systematic evidence-generation gap, not a reviewer problem. Fix: include a bounded `git ls-tree` of the role dir and repo root in the bundle.
- Windowed bundles (004, 005, 016, 046): only an anchor window of a large file is shown; anchors were fully visible so no label impact.
- Redaction: 004 (value blocks), 026, 027, 035, 042 contain [REDACTED_*] markers; none hid the predicate. In 026 the redaction of `oauth_token=` plus following text collapses lines, but l.9 still visible.
- Non-Ansible subject: 010, 021, 041 are Kustomize/JSON6902 patches (op/path/value). The bundle is faithful; the detector target is wrong.

## (c) Codebook/override ambiguities (would cause disagreement)
- FAMILY_STYLE_POLICY.md lists no predicate per rule. Reviewers must guess what "inconsistent-naming-convention", "variable-naming-convention", "long-statement", "long-task-name" and "missing-file-extension" test. Suggested fix: add a one-line predicate table (e.g. "long-task-name: task name > N characters, N=...; variable-naming: ^[a-z][a-z0-9_]*$ and optional role prefix; long-statement: physical line > N").
- Cautions say "the cutoff alone does not prove poor quality" but never state the cutoff; the threshold must be in the codebook for `positive`.
- Variable naming: unclear whether role-prefix is part of the predicate (011, 032 vs 042 which matches role name k3s).
- Inconsistent naming: unclear whether consistency is per file, per role, per repo, and whether it covers case, prefix, punctuation, quote style.
- Galaxy meta: "incomplete" not defined (which fields). Roles with `standalone: false` (013, 044) or no galaxy_info at all (002, 024, 034): I labeled positive (metadata incomplete) with actionability not-actionable; peers might label negative via "policy-not-in-scope". Suggest explicit guidance: absence of galaxy_info = positive? and where do `optional-practice` vs `policy-not-in-scope` apply (semantic vs actionability reasons share one list).
- reason_code is single-valued but semantic and actionability reasons differ (positive + optional-practice is semantically odd). Suggest two columns or a rule: reason_code describes the semantic label only.
- missing-tags: whether tags inherited from an including role caller (not visible) require external context. I marked requires_external_context=uncertain/role caller for 007, 018, 028, 038, 048.
- Block names for duplicate-task-names (023): not stated whether block/play names count.
- missing-file-extension (006): unclear whether FQCN import_playbook targets are in scope.

## (d) Detector patterns
- True positive (predicate literally holds): unnamed-play (009, 020, 030, 040, 050), unnamed-task on real Ansible (031), duplicate-task-names (001, 012, 033, 043, 023), missing-tags (007, 018, 028, 038, 048), long-statement/long-task-name on STIG files (016, 046), camelCase vars (022), galaxy_info incomplete (002, 013, 024, 034, 044).
- False positive, mechanism = non-Ansible YAML scanned as Ansible: unnamed-task on JSON6902 patches (010, 021, 041).
- False positive, mechanism = extension present: missing-file-extension on a .yml and a .yaml file (006, 017). Both bundles show source_location anchors at line 1 with no sign of what lacked an extension; the rule may be examining references rather than the file.
- Likely false positive: inconsistent-naming-convention at 014, 025, 035, 045 where the anchor name matches file-wide conventions.
- Variable naming at 042 matches role-name prefix (negative).

## (e) Sampling / evidence-generation concerns
- 3 of 4 unnamed-task items (010, 021, 041) and 2 of 2 missing-file-extension items are false positives; the rule outputs on this family look noisy and may be dominated by non-Ansible files.
- Molecule-absent bundles carry no evidence that can decide the predicate (5/5), so those samples cannot contribute to agreement on semantic labels. Consider excluding or regenerating them.
- Several samples (e.g. 015, 042, 011, 022) are `defaults/vars` files; fine for variable rules, but 015 (long-statement) is a variable value, not a task statement.
- No sample evidence of repository-level policy (.yamllint, .ansible-lint, line-length config) in any bundle, so "repository-policy-evidence" could never be used.

## (f) Rule definition vs codebook
- I did not have the rule definitions (not allowed), so I could not compare. The codebook says "names ... special-character predicate" while the only family rules in this sample are length/convention/duplicate; special-character rules are not exercised and some cited cautions (line length, file extension) cover rules whose predicate is not otherwise documented.
- RULE_OVERRIDES maps molecule-test-absent and galaxy-meta-incomplete to this family with "repository role/testing context determines actionability", yet the bundles give no repository context at all; the override assumes context the evidence does not supply.

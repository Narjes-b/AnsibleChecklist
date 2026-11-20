# review_history observations (reference reviewer, 50 rows)

## (a) Counts and hardest items
Counts: positive 13, negative 9, uncertain 28, unreviewable 0. Rows with bundle_issue != none: 4 (007, 008, 015, 016).
Per rule: commit-message-format 25 rows, missing-bug-reference 17, missing-release-note 4, missing-test-update 4.

Working predicates (NOT defined anywhere in my permitted files; I had to infer them):
- commit-message-format: subject length (>72 positive, <=50 with blank separator negative, 51-72 uncertain), blank line after subject. Body wrap and trailer length ignored.
- missing-bug-reference: positive = no issue/bug/ticket ID in the message; a bare squash/merge PR number (#N) = uncertain.
- missing-release-note: positive needs a release-note convention visible in the bundle (none is); changelog path in the change = negative.
- missing-test-update: positive only for real logic change with no test path; pin/revert/decommission changes = uncertain.

Hardest 5:
1. 007 (Release merge, 103 paths, no changelog path, 10 diffs missing): repo convention unknown, release merges may rely on tags.
2. 016 (positive, medium): new ca_path option and shell quoting, no test path, but nothing shows a test suite exists. 004/012/008 have the same epistemics yet I labelled them uncertain; the 016 vs 004 split is a judgement call that two humans may resolve differently.
3. 002/022/028/034/014/026: only a PR number (#N) present; is that a bug reference? Labelled uncertain.
4. 029/031/033/041/048/050 (and other 51-72 char subjects): outcome flips between a 50 and a 72 limit.
5. 020 and 038: 020 cites a cross-repo PR (#494), 038 only has an issue number inside a branch name (fix-...-1040). Labelled negative, low/medium confidence.

## (b) Bundle defects
- 007: 103 changed paths but only 93 `diff --git` blocks. Missing diffs: .python-version, ansible.cfg, library/cloudfront_distribution.py, library/cloudfront_distribution_info.py, library/ec2_launch_template.py, requirements-python.txt, roles/cs.ansible-plugins/filter_plugins/transform.py, roles/cs.repo-rabbitmq/templates/rabbitmq.repo, roles/cs.varnish/templates/vcl/acl.vcl.j2, vars_plugins/mageops_vars.py (apparently all non-.yml/new/extension-filtered files). Bundle is 133 KB; not stated as truncated.
- 008: 9 changed paths, 7 diffs. Missing: roles/splunk/templates/splunk_deployment_conf.j2 (deleted) and terraform/modules/asg/templates/user_data.tpl (modified).
- 015: 2 changed paths (CHANGELOG.md, galaxy.yml), only galaxy.yml diff shown. The very file that decides the verdict (CHANGELOG.md) has no diff. Same pattern: Markdown/non-YAML files dropped from the diff.
- 016: complete, but values like `scale_cluster_authorization_cleanup: [REDACTED_LITERAL]` hide plain booleans (over-redaction of non-secrets, not material). 007 has secret-block redactions (openssl_privatekey), fine.
- Merge commit messages: 001, 003, 004, 007, 009, 012, 014, 016, 017, 025, 026, 027, 037, 038, 044, 045, 046, 049 are git/GitHub-generated "Merge pull request" messages. For diff rules the first-parent diff of a merge is the whole PR (OK). For message rules these messages are tool-generated and say nothing about the author's habits.
- 020: the commit message itself contains a triple-backtick block, nested inside the bundle's ```text fence (renders ambiguously; content is intact).
- 046: message contains the artefact "Reviewed-by: None <None>".
- Message-only bundles state "first parent unavailable locally" (001, 002, 005, ...) while 014, 033, 036 say "available; diff not required": harmless but inconsistent.
- Message-only bundles have empty "Changed paths" sections by design; no problem.

## (c) Codebook / override ambiguities
- FAMILY_REVIEW_HISTORY.md never defines the predicate for any of the five rules (no subject-length limit, body-wrap limit, what counts as a bug reference, what counts as a release note or test, whether trivial changes are exempt). `positive` is defined as "satisfies the rule condition in the codebook" but the codebook has no such condition. Fix: add a one-line operational definition per rule with numeric limits.
- "Commit-message length/format ... repository-specific conventions may make actionability differ" vs REVIEWER_INSTRUCTIONS "if the repository's own policy is not in the bundle and the codebook says policy matters, use uncertain": the codebook says policy affects actionability, not the semantic label. Two humans will disagree on whether policy-missing forces uncertain. Fix: state explicitly that policy only affects actionability for message rules.
- `negative` is defined as "the message contradicts the report, or the relevant required update is present": there is no wording for "rule not applicable" (e.g. a Renovate bump has no bug to reference; a release-merge needs no per-change note). Fix: add an applicability clause or reason code `not-applicable-change`.
- Reason codes lack a message-only uncertain code; I reused `repository-policy-ambiguous` for threshold/definition ambiguity and `release-note-convention` for unknown convention. A `rule-definition-ambiguous` code would be clearer. `message-condition-absent` is used for negatives: for missing-bug-reference "condition absent" is a double-negative (the missing-ness is absent).
- Merge-commit handling: instructions say judge only against limits the codebook defines; codebook defines none, so every merge message is uncertain (10 CMF merges). Fix: declare merge messages out of scope or state limits.
- external_context_type vocabulary is "for example"; I used `repository policy`, `none`.
- REVIEWER_INSTRUCTIONS refer to agreement-pilot.csv and Reviewer A/B; the instructions for this task (reference reviewer) differ, no conflict in labels.

## (d) Detector patterns
- missing-release-note (003, 007, 011, 015): all four are about a real CHANGE (first-parent diff), not whole-repo content. 015 is a false positive (CHANGELOG.md is in the changed path list). 003/007/011 cannot be verified without repo convention; none is a clear true positive. The rule seems to fire when the change touches files without a changelog path regardless of whether the repo keeps one.
- missing-test-update (004, 008, 012, 016): all about changes. 004 (pin bump), 012 (artifact revert), 008 (service decommission) look like weak positives at best (nothing tests would plausibly cover); 016 is the only plausible true positive (logic + quoting changes, no test path). Detector flags any code change lacking a test path; relevance not judged.
- missing-bug-reference: fires on Renovate/bot commits (006, 010, 022, 032) and merge commits (014, 026, 038); these are low-value. True lacks are 024, 030, 036 (human `fix:` messages w/o ID). Messages containing a bug ID were also reported (018 "Fixes #339", 040 AAP-73918, 042 #1543, 033 PACKIT-5037 is in CMF row) - looks like the detector does not parse all reference forms or the PR suffix; 018/040/042 are false positives (high confidence).
- commit-message-format: dominated by Renovate/Dependabot bot messages (019, 021, 023, 035, 043, 048) and merge-commit messages (10 rows). Bot-message positives (021, 035, 043) are technically over-length but not-actionable.

## (e) Sampling / evidence-generation concerns
- 28 of 50 labels are uncertain, chiefly because rule predicates are undefined; this will depress agreement estimates and reflect codebook, not detector, quality.
- Heavy bot/merge content (about 20 of 42 message-rule rows) suggests the sample over-represents commits where the rule is meaningless.
- Diff generation seems to drop non-YAML files (007, 008, 015); for missing-release-note this removes exactly the evidence needed (015).
- 013 message and 031 message are LLM-assisted commits dated 2026; a few messages carry "Co-authored-by: Claude" trailers (002, 005, 013, 031, 036) - no effect on labels.
- 033 appears twice-checkable: its rule is CMF (message "Related to PACKIT-5037") though a bug-ref reading would be negative; unrelated to label.
- Diff-dependent rows with a merge target (003, 004, 007, 012, 016) have a large first-parent diff covering the whole PR; fine, but 007 is a release/develop merge so "per-change" notes are not meaningful.

## (f) Rule definition vs codebook
- I could not read the rule catalog, so I cannot say whether the detector's definitions (e.g. a 72-char threshold, regexes for issue references) conflict with the codebook; the codebook itself gives none, so rule definition and codebook cannot be compared at all from permitted files.
- Codebook says release-note checks need "project release-note convention" while the bundle never provides repository conventions (no tree, no CONTRIBUTING); by the codebook's own wording every missing-release-note and missing-test-update item is at best uncertain unless a changelog/test path is visibly present.

# Family v2: review and history
Question: does the finding accurately describe the target commit message or its first-parent change?

Scope: bot commits (dependabot/renovate and similar) and merge commits are **out of scope** for message rules: `negative`, reason `out-of-scope`.

Operational definitions:
- **Bug reference** (accepted forms): `Closes-Bug`/`Related-Bug`/`Partial-Bug: #n`, `bug #n`, `Fixes|Closes|Resolves #n`, an issue URL, or a tracker key (`ABC-123`). A pull-request number alone is **not** a bug reference. The v0.0.7 detector recognises only the first two; a message with an accepted form the detector misses is `negative`, reason `reference-form-not-detected` (a tool defect to log).
- `missing-bug-reference` applies only when the subject contains bug/fix/repair/regression/issue.
- **Commit-message format** (the rule's own predicate): subject ≤ 50 characters, a blank line after the subject, body lines ≤ 72 characters. Positive when any of the three is violated; name which one in `evidence_notes`. Whether the repository follows a looser convention affects actionability only.
- **Release note**: a changed path matching the detector's release-note pattern (changelog/news/history/release-notes, `changelogs/changelog.yml`, or a `releasenotes/` or `changelogs/fragments/` fragment). If the repository has no such convention visible in the diff or tree: `uncertain` (`organization-policy`), not positive.
- **`untested-override-change`** (the rule's own predicate): the review range changes a configuration YAML file under `defaults/`, `vars/`, `group_vars/` or `host_vars/` and changes no path containing a `test`, `tests` or `molecule` directory. Positive = both hold. A pure version-bump/release commit is positive with `not-actionable`/`low-value`.
- **Release-only commits** (a CHANGELOG/version bump only): the predicate of `missing-test-update` and `untested-override-change` is met literally; label it positive and set actionability `not-actionable` with `low-value`.
- **Merge commits**: any commit whose subject starts with `Merge ` (branch, pull request, remote-tracking) is out of scope for message rules even when its parents are hidden by a shallow clone: `negative` / `out-of-scope`.
- **Test update**: a changed file under a test directory or matching `test_*`/`*_test.*`/molecule. Non-YAML files in the commit count; if the diff omits them, `unreviewable` / `bundle-defect`.

Positive semantic reasons: `confirmed-message-condition`, `confirmed-missing-update`.
Negative: `message-condition-absent`, `relevant-test-present`, `reference-form-not-detected`, `out-of-scope`, `release-note-present`.
Uncertain: `organization-policy`, `repository-policy-ambiguous`, `insufficient-diff-context`.
Unreviewable: `bundle-defect`, `missing-first-parent`, `invalid-range`.

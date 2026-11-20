# Family codebook: review/history

## Review question

Does the finding accurately describe the selected frozen commit message or the change from its actual first parent to that commit?

## Required evidence

Every sampled item must include the full target commit SHA and exact commit message. For diff-dependent rules (`missing-release-note`, `missing-test-update`, and `untested-override-change`), it must also include the actual first-parent SHA, changed-file list, and relevant first-parent diff/context reconstructed from frozen Git objects. A missing base must never be replaced by a root commit, an arbitrary merge base, a guessed release range, or the current branch.

If the first parent is unavailable and cannot be recovered as an exact object, a diff-dependent item is `unreviewable`; do not use detector fallback output as a substitute for the intended review range. `commit-message-format` and `missing-bug-reference` are message-only: the exact target commit object/message is sufficient even when the parent is unavailable. Identify that evidence type in the item context, and do not imply that a diff was reviewed.

## Semantic labels

- `positive`: the exact target message or required actual first-parent diff satisfies the rule condition in the codebook.
- `negative`: the message contradicts the report, or the relevant required update is present in the actual first-parent change.
- `uncertain`: the commit evidence is present but policy meaning or whether a file/test is relevant cannot be determined from the package.
- `unreviewable`: required commit evidence is absent/invalid, or required first-parent/diff evidence is absent for a diff-dependent rule.

## Family-specific cautions

- Commit-message length/format and bug-reference rules are evaluated on the exact target commit message; repository-specific conventions may make actionability differ.
- Release-note checks must inspect the exact set of changed files and project release-note convention. Do not infer the range from a generic `HEAD` label.
- Test-update checks require understanding which changed behavior/configuration the tests would cover; changed-file extension alone is not enough.
- Override-change checks require the actual defaults/vars change and the associated test changes in the same frozen range.
- Detector metadata that records `base: null` or a fallback range is a known data-quality limitation, not ground truth for human review.

## Reason codes

`message-condition-present`, `message-condition-absent`, `first-parent-diff-present`, `relevant-test-present`, `relevant-test-absent`, `release-note-convention`, `repository-policy-ambiguous`, `missing-first-parent`, `invalid-range`, `insufficient-diff-context`, `other`.

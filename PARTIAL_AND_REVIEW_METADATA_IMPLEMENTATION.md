# Completing partial checklist coverage

This implementation strengthens criteria that cannot be covered by task-shape
checks alone. It adds four YAML/source rules and seven Git-aware review rules.

## Source-level partial coverage

The implementation lives in `detectors/partial_checklist.py`.

### Unused Registered Variable

`unused-registered-variable` collects every `register` name and searches all
other scalar values for a reference. An unreferenced result is dead review
state. This extends unused-code coverage beyond `set_fact`, handlers, and
included vars. Dynamic cross-file references remain invisible.

### Unscoped Shell Variable

`unscoped-shell-variable` extracts `$NAME` and `${NAME}` references from
shell/command/raw tasks. It accepts variables declared in task/play
`environment`, inline assignments, and a conservative set of standard process
variables. Other names are reported because remote shell environment is not a
reliable configuration contract. Host-provided custom variables can still be
intentional.

### Invalid Task Attribute Type

`invalid-task-attribute-type` validates universal Ansible task attributes:
boolean flags, integer retry/timing controls, mapping-valued `vars` and
`environment`, and string/list tags. This is deterministic for the checked
attributes but does not replace collection-specific module argument schemas.

### Invalid Numeric Value

`invalid-numeric-value` checks literal ports against `1..65535` and rejects
negative retry/timing controls. Templated values are excluded because their
runtime value is unknown.

## Git-aware review coverage

The implementation lives in `detectors/review_metadata.py`. It locates the Git
root and inspects the latest commit. It emits project findings once, rather
than once per YAML file.

### Missing Release Note

When HEAD changes production YAML but adds no file under
`releasenotes/notes/` or `release_notes/`, `missing-release-note` is emitted.
Not every internal change requires a public note, so this remains a note and
partial checklist coverage.

### Missing Bug Reference

When the subject describes a fix/bug/regression but the message has no
`Closes-Bug`, `Related-Bug`, `Partial-Bug`, or numeric bug reference,
`missing-bug-reference` is emitted. Non-bug commits do not require a tracker
reference.

### Invalid Depends-On Reference

Every present `Depends-On:` trailer is validated as a review URL or 40-digit
Gerrit Change-Id. The detector cannot infer when an absent dependency trailer
was required, so this is partial coverage.

### Commit Message Format

`commit-message-format` enforces a subject no longer than 50 characters, a
blank separator before the body, and body lines no longer than 72 characters.
This directly implements the format described by the paper checklist.

### Removed Copyright Notice

For modified files, `removed-copyright-notice` compares the first 20 lines of
HEAD with the parent revision. A copyright marker present before and absent
after is reported. This checks preservation rather than imposing a new header.

### Missing Test Update

`missing-test-update` reports a latest commit that changes production YAML but
changes nothing under `test`, `tests`, or `molecule`. It proves co-change, not
test correctness, so generated or separately maintained tests remain a limit.

### Untested Override Change

`untested-override-change` narrows the same Git change analysis to role
defaults, vars, group_vars, and host_vars. It requires a test/Molecule change
when override sources change. It does not execute those tests or measure their
assertions.

## Integration and tests

The four file checks flow through parser metrics, assessed metrics, CSV, JSON,
and SARIF. The seven Git checks are added once by `cli.analyze_path()` before
project rollups are written. `findings.py` uses the detail's own file when a
project finding points at a changed path.

`tests/test_partial_checklist.py` covers used/unused registers, scoped/unscoped
shell variables, valid/invalid types, and numeric ranges.
`tests/test_review_metadata.py` creates real temporary Git repositories and
tests both an incomplete review commit and a fully documented/tested commit.


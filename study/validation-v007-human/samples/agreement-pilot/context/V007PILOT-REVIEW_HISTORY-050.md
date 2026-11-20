# Frozen Git review context: V007PILOT-REVIEW_HISTORY-050

- Repository: `seapath/ansible`
- Target commit: `bc10619e516866d0e86af601fd7aa8738b55e645`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
inventories/examples: add SSH private key option for ansible connection

Add a commented line in the example inventories to allow users to
specify a custom SSH private key for Ansible connections. This is useful
for users who do not use the default SSH key and need to provide a
specific key for connecting to their hosts.

Signed-off-by: Mathieu Dupré <mathieu.dupre@savoirfairelinux.com>
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

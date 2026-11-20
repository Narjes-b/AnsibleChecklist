# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-018

- Repository: `autobase-tech/autobase`
- Target commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
Add enable_backups playbook (#1681)

Introduce a cloud_backup_provider variable (defaults to cloud_provider) and a new enable_backups playbook to provision backup storage, install/configure pgBackRest or WAL-G, and update archive_command in DCS.
```

## Changed paths (not required for message-only evidence)


The rule is evaluated only on the exact target commit message above.

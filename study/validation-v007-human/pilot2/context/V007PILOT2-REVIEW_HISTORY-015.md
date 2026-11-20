# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-015

- Repository: `redhat-cop/aap_configuration_extended`
- Target commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
fix(filetree_create): complete controller_instance_groups export (#355)

Export policy fields as native integers and add max_forks,
max_concurrent_jobs, is_container_group, credential, policy_instance_list,
and pod_spec_override when present.

Fixes #339.

Co-authored-by: Cursor <[REDACTED_EMAIL]>
```

## Changed paths (not required for message-only evidence)


The rule is evaluated only on the exact target commit message above.

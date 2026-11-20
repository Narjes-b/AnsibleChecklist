# Frozen Git review context: V007PILOT-REVIEW_HISTORY-018

- Repository: `redhat-cop/aap_configuration_extended`
- Target commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/missing-bug-reference`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
fix(filetree_create): complete controller_instance_groups export (#355)

Export policy fields as native integers and add max_forks,
max_concurrent_jobs, is_container_group, credential, policy_instance_list,
and pod_spec_override when present.

Fixes #339.

Co-authored-by: Cursor <cursoragent@cursor.com>
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

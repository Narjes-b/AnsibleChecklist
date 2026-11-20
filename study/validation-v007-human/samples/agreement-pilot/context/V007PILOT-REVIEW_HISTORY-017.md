# Frozen Git review context: V007PILOT-REVIEW_HISTORY-017

- Repository: `yunionio/ocboot`
- Target commit: `b781237b81676ff5718525da798292e207124e01`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Merge pull request #1711 from swordqiu/hotfix/qj-centos-libselinux-python3

fix: centos 7 libselinux-python3
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

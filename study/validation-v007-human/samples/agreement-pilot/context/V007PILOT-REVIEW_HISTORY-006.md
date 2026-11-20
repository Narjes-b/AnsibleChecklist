# Frozen Git review context: V007PILOT-REVIEW_HISTORY-006

- Repository: `jr0dd/home-ops`
- Target commit: `0e76c37818159bea648890d4ee132616f6ed6499`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/missing-bug-reference`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
fix(github-release): update helm to v3.21.4

| datasource      | package   | from    | to      |
| --------------- | --------- | ------- | ------- |
| github-releases | helm/helm | v3.21.3 | v3.21.4 |
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

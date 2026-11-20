# Frozen Git review context: V007PILOT-REVIEW_HISTORY-028

- Repository: `ansible/galaxy-operator`
- Target commit: `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/missing-bug-reference`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
fix: allow API calls across different namespaces (#281)

Allow ingress on port 8080 for controller-manager pods across
different namespaces.
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

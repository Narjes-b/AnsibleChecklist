# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-004

- Repository: `ansible/galaxy-operator`
- Target commit: `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
fix: allow API calls across different namespaces (#281)

Allow ingress on port 8080 for controller-manager pods across
different namespaces.
```

## Changed paths (not required for message-only evidence)


The rule is evaluated only on the exact target commit message above.

# Frozen Git review context: V007PILOT-REVIEW_HISTORY-010

- Repository: `chkpwd/iac`
- Target commit: `9b789a76960f81aa13ecdb2c29fbcb799b5e4fcf`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/missing-bug-reference`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
fix(container): update image ghcr.io/home-operations/radarr ( 6.4.2.10590 → 6.4.3.10645 )

| datasource | package                        | from        | to          |
| ---------- | ------------------------------ | ----------- | ----------- |
| docker     | ghcr.io/home-operations/radarr | 6.4.2.10590 | 6.4.3.10645 |
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

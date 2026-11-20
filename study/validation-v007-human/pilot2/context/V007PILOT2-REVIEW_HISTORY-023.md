# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-023

- Repository: `ansible/awx-operator`
- Target commit: `45363a1a0d312d16f740c626407a7521bbe3a31c`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
fix: remove unused objects.inv import and fix development.md warnings (#2137)

The mkdocstrings inventory import from docs.ansible.com fails with
HTTP 429 (CloudFlare rate limiting) on both GitHub Actions and Read
the Docs. The import is entirely unused — no src/ directory, no :::
mkdocstrings directives, and no Sphinx cross-reference syntax in any
doc page. Remove it.

Also fix two --strict warnings for development.md:
- Add it to the nav under Contributors Guide
- Replace the relative ../dev link with a GitHub URL

Co-authored-by: Claude Opus 4.6 (1M context) <[REDACTED_EMAIL]>
```

## Changed paths (not required for message-only evidence)


The rule is evaluated only on the exact target commit message above.

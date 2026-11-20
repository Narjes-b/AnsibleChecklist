# Frozen source context: V007PILOT-STYLE_POLICY-002

- Repository: `cfpb/aurora`
- Commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Family: Style/policy
- Rule: `ansibleguard/galaxy-meta-incomplete`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `deploy/roles/postgresql-server/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `c69cd8490b1d643c22ed8efec4ad0aaa910398291b9045e2f3819ea5157ed6c8`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–4 of 4:

```text
    1 | # main.yml
    2 | ---
    3 | dependencies:
    4 | - role: shared
```

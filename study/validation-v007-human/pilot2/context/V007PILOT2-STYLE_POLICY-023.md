# Frozen source context: V007PILOT2-STYLE_POLICY-023

- Repository: `usegalaxy-eu/vgcn`
- Commit: `c65e4ea9febe2bf5eeca04715c93a441d82f7875`
- Family: style_policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `ansible/external.yml` (reported anchor line 2)
- Flagged construct: not named by the finding; the anchor line 2 lies in the task at line 2, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–5 of 5:

```text
    1 | ---
    2 | - hosts: external
    3 |   roles:
    4 |     - lock-root
    5 |     - cloudinit
```

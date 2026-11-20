# Frozen source context: V007PILOT2-SECURITY-010

- Repository: `vrk-kpa/api-catalog`
- Commit: `e81b1cb5a261a290a78eafae67f853efc8f5f7a3`
- Family: security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `ansible/vars/analytics-secrets-defaults.yml` (reported anchor line 9)
- Flagged construct: not named by the finding; the anchor line 9 lies in the top-level key `secret` (line 6).
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–9 of 9:

```text
    1 | ---
    2 | 
    3 | # Warning! This file is open source and available in the Internet! Do not add
    4 | # any real secrets here! These are for local Vagrant and for reference.
    5 | 
    6 | secret:[REDACTED VALUE BLOCK]
    7 |   [REDACTED ENCRYPTED VALUE]
      [... 2 further identical redacted lines, through 9]
```

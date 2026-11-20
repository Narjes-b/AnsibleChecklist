# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-028

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: Maintainability/complexity
- Rule: `ansibleguard/high-coupling`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `vagrant/provisioning/arkcase-upgrade.yml` (reported anchor line 1)
- Object: `source_location` `12c6ef347b625533a37e16da86ae91b64504b6957ccaef9c79e64a4ff8b2a79e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–10 of 10:

```text
    1 | ---
    2 | - hosts: all
    3 |   roles:
    4 |     - common
    5 |     - arkcase-pre-upgrade
    6 |     - arkcase-prerequisites
    7 |     - arkcase-app
    8 |     - arkcase-post-upgrade
    9 |     - snowbound-app
   10 |     - start-arkcase
```

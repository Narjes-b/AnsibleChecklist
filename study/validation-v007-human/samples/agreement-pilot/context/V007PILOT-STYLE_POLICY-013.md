# Frozen source context: V007PILOT-STYLE_POLICY-013

- Repository: `theforeman/foreman-ansible-modules`
- Commit: `6c08783ce38b1dd35fc28e2754b2d11ebf508d95`
- Family: Style/policy
- Rule: `ansibleguard/galaxy-meta-incomplete`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/convert2rhel/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `2d25bb85182feeff6222f47d923b3febea44be979f51ac1ba58d426e7a00ec59`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–4 of 4:

```text
    1 | ---
    2 | galaxy_info:
    3 |   description: Configure everything needed to register and convert CentOS clients to Red Hat Enterprise Linux
    4 |   standalone: false
```

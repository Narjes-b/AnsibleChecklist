# Frozen source context: V007PILOT-STYLE_POLICY-044

- Repository: `aristanetworks/avd`
- Commit: `05092c872036e7e90e1b4986cbfb2b36798c5a4d`
- Family: Style/policy
- Rule: `ansibleguard/galaxy-meta-incomplete`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `ansible_collections/arista/avd/roles/anta_runner/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `32938af7ad9c491ba62091ac2fa00e598f1d69efaffbff8562aef4a85b6995f5`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–3 of 3:

```text
    1 | galaxy_info:
    2 |   description: Run Arista Network Test Automation (ANTA) on EOS via eAPI
    3 |   standalone: false
```

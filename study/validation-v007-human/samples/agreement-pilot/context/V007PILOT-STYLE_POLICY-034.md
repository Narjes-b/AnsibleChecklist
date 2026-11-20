# Frozen source context: V007PILOT-STYLE_POLICY-034

- Repository: `NationalGenomicsInfrastructure/miarka-provision`
- Commit: `52daa7027450753c62cb0f38a2b5ef546cae7ede`
- Family: Style/policy
- Rule: `ansibleguard/galaxy-meta-incomplete`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/archive-upload-ws/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `2fe9c00f8459d0f0a0de5474e3e873b10a925c081f38bc0c1ed127d2d3949740`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–5 of 5:

```text
    1 | ---
    2 | 
    3 | dependencies:
    4 |   - { role: anaconda, tags: anaconda }
    5 |   - { role: setup_base_config, tags: setup_base_config }
```

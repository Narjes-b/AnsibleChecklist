# Frozen source context: V007PILOT-STYLE_POLICY-040

- Repository: `Sunbird-Obsrv/sunbird-data-pipeline`
- Commit: `eb1e1a1c3533c549693dda32cd92c667754aaea9`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `ansible/lpa_provision_geo_location_db.yml` (reported anchor line 2)
- Object: `source_location` `0477132f5a9224809b422d89460ee32926bedb222128d17221bf393fa1a8b55c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–6 of 6:

```text
    1 | ---
    2 | - hosts: localhost
    3 |   vars_files:
    4 |     - "{{inventory_dir}}/secrets.yml"
    5 |   roles:
    6 |     - provision-geo-location-db
```

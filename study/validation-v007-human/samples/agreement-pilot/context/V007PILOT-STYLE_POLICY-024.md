# Frozen source context: V007PILOT-STYLE_POLICY-024

- Repository: `folio-org/folio-ansible`
- Commit: `dde7c5f2011b34eb79b03ef38f334b34449e67af`
- Family: Style/policy
- Rule: `ansibleguard/galaxy-meta-incomplete`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/okapi/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `fb656ef24ef681913454b03b71bb728d144560b7ed80db50e27bdc2fd52c1a2e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–10 of 10:

```text
    1 | ---
    2 | dependencies:
    3 |   - role: common
    4 |     when: folio_install_type == "single_server"
    5 |   - role: create-database
    6 |     vars:
    7 |       db_admin_user: "{{ okapidb_user }}"
    8 |       db_admin_password: "{{ okapidb_password }}"
    9 |       database_name: "{{ okapidb_name }}"
   10 |     when: okapi_storage == "postgres"
```

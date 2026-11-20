# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-004

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/role-variable-precedence-collision`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `roles/postgresql/vars/main.yml` (reported anchor line 5)
- Flagged construct: variable `pg_hba_postgresql_database`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–7 of 7:

```text
    1 | ---
    2 | # vars file for postgresql
    3 | postgres_port: 5432
    4 | pg_hba_postgresql_user: "all"
    5 | pg_hba_postgresql_database: "all"
    6 | pg_hba_method: "md5"
    7 | pg_hba_source: "{{ ansible_host }}/32"
```

## Visible variable references

```text
Whole-word search for `pg_hba_postgresql_database`: 27 matches in 27 files; 27 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
group_vars/ansible_tower/main.yml:17:pg_hba_postgresql_database: "all"
group_vars/approvals/production.yml:26:pg_hba_postgresql_database: "all"
group_vars/approvals/sandbox.yml:29:pg_hba_postgresql_database: "all"
group_vars/approvals/staging.yml:30:pg_hba_postgresql_database: "all"
group_vars/bibdata/production.yml:9:pg_hba_postgresql_database: "all"
group_vars/bibdata/staging.yml:9:pg_hba_postgresql_database: "all"
group_vars/dpul/production.yml:13:pg_hba_postgresql_database: "all"
group_vars/dpul/staging.yml:20:pg_hba_postgresql_database: "all"
group_vars/dss/production.yml:7:pg_hba_postgresql_database: "all"
group_vars/dss/staging.yml:7:pg_hba_postgresql_database: "all"
group_vars/lib_jobs/production.yml:42:pg_hba_postgresql_database: "all"
group_vars/lib_jobs/staging.yml:37:pg_hba_postgresql_database: "all"
group_vars/lockers_and_study_spaces/production.yml:7:pg_hba_postgresql_database: "all"
group_vars/lockers_and_study_spaces/staging.yml:8:pg_hba_postgresql_database: "all"
group_vars/orangelight/common.yml:42:pg_hba_postgresql_database: "all"
group_vars/orcid/main.yml:8:pg_hba_postgresql_database: "all"
group_vars/pdc_describe/main.yml:8:pg_hba_postgresql_database: "all"
group_vars/pdc_discovery/main.yml:9:pg_hba_postgresql_database: "all"
group_vars/pulfalight/production.yml:12:pg_hba_postgresql_database: "all"
group_vars/pulfalight/qa.yml:10:pg_hba_postgresql_database: "all"
group_vars/pulfalight/staging.yml:10:pg_hba_postgresql_database: "all"
group_vars/pulmap/production.yml:41:pg_hba_postgresql_database: "all"
group_vars/pulmap/staging.yml:40:pg_hba_postgresql_database: "all"
group_vars/tigerdata/common.yml:9:pg_hba_postgresql_database: "all"
group_vars/whichiso/main.yml:8:pg_hba_postgresql_database: "all"
roles/postgresql/defaults/main.yml:87:pg_hba_postgresql_database: "all"
roles/postgresql/vars/main.yml:5:pg_hba_postgresql_database: "all"

Other references:
```

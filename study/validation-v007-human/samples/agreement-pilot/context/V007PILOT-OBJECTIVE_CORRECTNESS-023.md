# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-023

- Repository: `os-migrate/os-migrate`
- Commit: `60e4123dd2391233d23149d7dfb6ebe4b0870590`
- Family: Objective correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/import_images/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `c0a476ab25b03d3235034d4bf13c85dd7a96ba011e759206cbb9c8bac655715b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–19 of 19:

```text
    1 | ---
    2 | galaxy_info:
    3 |   author: os-migrate
    4 |   role_name: import_images
    5 |   description: os-migrate resource
    6 |   company: Red Hat
    7 |   license: Apache-2.0
    8 |   min_ansible_version: "2.9"
    9 |   platforms:
   10 |     - name: Fedora
   11 |       versions:
   12 |         - "34"
   13 |   galaxy_tags: ["osmigrate"]
   14 | dependencies:
   15 |   - role: os_migrate.os_migrate.prelude_dst
   16 |   - role: os_migrate.os_migrate.validate_resource_files
   17 |     vars:
   18 |       resource_files:
   19 |         - "{{ os_migrate_data_dir }}/images.yml"
```

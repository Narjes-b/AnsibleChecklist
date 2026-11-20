# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-007

- Repository: `os-migrate/os-migrate`
- Commit: `60e4123dd2391233d23149d7dfb6ebe4b0870590`
- Family: objective_correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/export_router_interfaces/meta/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/export_router_interfaces/meta/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–15 of 15:

```text
    1 | ---
    2 | galaxy_info:
    3 |   author: os-migrate
    4 |   role_name: export_router_interfaces
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
   15 |   - role: os_migrate.os_migrate.prelude_src
```

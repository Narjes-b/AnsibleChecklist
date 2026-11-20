# Frozen source context: V007PILOT-STRUCTURE_REUSE-042

- Repository: `ansible/awx`
- Commit: `54d6e576fb543c76f672603ca7f26913d58cf458`
- Family: Structure/reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `tools/docker-compose/ansible/roles/vault/defaults/main.yml` (reported anchor line 1)
- Object: `source_location` `3ba550fbbef5ad9499b23f9c0ec6fbda49e651a4957bcd7d9afaadf5ba0995b2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–9 of 9:

```text
    1 | ---
    2 | vault_file: "{{ sources_dest }}/secrets/vault_init.yml"
    3 | admin_password_file: "{{ sources_dest }}/secrets/admin_password.yml"
    4 | vault_cert_dir: "{{ sources_dest }}/vault_certs"
    5 | vault_server_cert: "{{ vault_cert_dir }}/server.crt"
    6 | vault_client_cert: "{{ vault_cert_dir }}/client.crt"
    7 | vault_client_key: "{{ vault_cert_dir }}/client.key"
    8 | vault_userpass_username: [REDACTED_LITERAL]
    9 | vault_userpass_password: [REDACTED_LITERAL]
```

## Frozen tracked paths in the relevant role/scope

```text
tools/docker-compose/ansible/roles/vault/defaults/main.yml
tools/docker-compose/ansible/roles/vault/tasks/initialize.yml
tools/docker-compose/ansible/roles/vault/tasks/plumb.yml
tools/docker-compose/ansible/roles/vault/tasks/set_vault_addr.yml
tools/docker-compose/ansible/roles/vault/tasks/unseal.yml
```

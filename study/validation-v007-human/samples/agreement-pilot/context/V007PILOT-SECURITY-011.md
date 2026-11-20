# Frozen source context: V007PILOT-SECURITY-011

- Repository: `ansible/awx`
- Commit: `54d6e576fb543c76f672603ca7f26913d58cf458`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `tools/docker-compose/ansible/roles/sources/tasks/vault_tls.yml` (reported anchor line 19)
- Object: `source_location` `7fb5c74a076454e3e3ee65841ea695ecc4b16650f8e641a31342eeab7ab04aeb`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–31 of 31:

```text
    1 | ---
    2 | - name: Create Certificates for HashiCorp Vault
    3 |   block:
    4 |     - name: Create Hashicorp Vault cert directory
    5 |       file:
    6 |         path: "{{ hashivault_cert_dir }}"
    7 |         state: directory
    8 | 
    9 |     - name: Generate vault server certificate
   10 |       command: 'openssl req -new -newkey rsa:2048 -x509 -days 365 -nodes -out {{ hashivault_server_public_keyfile }} -keyout {{ hashivault_server_private_keyfile }} -subj "{{ hashivault_server_cert_subject }}"{% for ext in hashivault_server_cert_extensions %} -addext "{{ ext }}"{% endfor %}'
   11 |       args:
   12 |         creates: "{{ hashivault_server_public_keyfile }}"
   13 | 
   14 |     - name: Generate vault test client certificate
   15 |       command: 'openssl req -new -newkey rsa:2048 -x509 -days 365 -nodes -out {{ hashivault_client_public_keyfile }} -keyout {{ hashivault_client_private_keyfile }} -subj "{{ hashivault_client_cert_subject }}"{% for ext in hashivault_client_cert_extensions %} -addext "{{ ext }}"{% endfor %}'
   16 |       args:
   17 |         creates: "{{ hashivault_client_public_keyfile }}"
   18 | 
   19 |     - name: Set mode for vault certificates
   20 |       ansible.builtin.file:
   21 |         path: "{{ hashivault_cert_dir }}"
   22 |         recurse: true
   23 |         state: directory
   24 |         mode: 0777
   25 |   when: vault_tls | bool
   26 | 
   27 | - name: Delete Certificates for HashiCorp Vault
   28 |   file:
   29 |     path: "{{ hashivault_cert_dir }}"
   30 |     state: absent
   31 |   when: vault_tls | bool == false
```

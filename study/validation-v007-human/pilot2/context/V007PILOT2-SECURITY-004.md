# Frozen source context: V007PILOT2-SECURITY-004

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `test_roles/confluent.test.ldap/tasks/tls_custom_certs.yml` (reported anchor line 2)
- Flagged construct: not named by the finding; the anchor line 2 lies in the task at line 2, name `Copy CA Cert to Host`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–18 of 18:

```text
    1 | ---
    2 | - name: Copy CA Cert to Host
    3 |   copy:
    4 |     src: "{{ssl_ca_cert_filepath}}"
    5 |     dest: "/var/ssl/private/ldaps/{{ssl_ca_cert_filepath|basename}}"
    6 |     mode: '666'
    7 | 
    8 | - name: Copy Signed Cert to Host
    9 |   copy:
   10 |     src: "{{ssl_signed_cert_filepath}}"
   11 |     dest: "/var/ssl/private/ldaps/{{ssl_signed_cert_filepath|basename}}"
   12 |     mode: '666'
   13 | 
   14 | - name: Copy Key to Host
   15 |   copy:
   16 |     src: "{{ssl_key_filepath}}"
   17 |     dest: "/var/ssl/private/ldaps/{{ssl_key_filepath|basename}}"
   18 |     mode: '666'
```

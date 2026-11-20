# Frozen source context: V007PILOT2-SECURITY-002

- Repository: `kubernetes-sigs/kubespray`
- Commit: `9ee6f9b27981b251d77302fd6cf631f330e0ec39`
- Family: security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `roles/kubernetes/control-plane/tasks/encrypt-at-rest.yml` (reported anchor line 16)
- Flagged construct: task `base 64 decode slurped secrets_encryption.yaml file`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–40 of 40:

```text
    1 | ---
    2 | - name: Check if secret for encrypting data at rest already exist
    3 |   stat:
    4 |     path: "{{ kube_cert_dir }}/secrets_encryption.yaml"
    5 |     get_attributes: false
    6 |     get_checksum: false
    7 |     get_mime: false
    8 |   register: secrets_encryption_file
    9 | 
   10 | - name: Slurp secrets_encryption file if it exists
   11 |   slurp:
   12 |     src: "{{ kube_cert_dir }}/secrets_encryption.yaml"
   13 |   register: secret_file_encoded
   14 |   when: secrets_encryption_file.stat.exists
   15 | 
   16 | - name: Base 64 Decode slurped secrets_encryption.yaml file
   17 |   set_fact:
   18 |     secret_file_decoded: "{{ secret_file_encoded['content'] | b64decode | from_yaml }}"
   19 |   when: secrets_encryption_file.stat.exists
   20 | 
   21 | - name: Extract secret value from secrets_encryption.yaml
   22 |   set_fact:
   23 |     kube_encrypt_token_extracted: "{{ secret_file_decoded | json_query(secrets_encryption_query) | first | b64decode }}"
   24 |   when: secrets_encryption_file.stat.exists
   25 | 
   26 | - name: Set kube_encrypt_token across control plane nodes
   27 |   set_fact:
   28 |     kube_encrypt_token: "{{ kube_encrypt_token_extracted }}"
   29 |   delegate_to: "{{ item }}"
   30 |   delegate_facts: true
   31 |   with_inventory_hostnames: kube_control_plane
   32 |   when: kube_encrypt_token_extracted is defined
   33 | 
   34 | - name: Write secrets for encrypting secret data at rest
   35 |   template:
   36 |     src: secrets_encryption.yaml.j2
   37 |     dest: "{{ kube_cert_dir }}/secrets_encryption.yaml"
   38 |     owner: root
   39 |     group: "{{ kube_cert_group }}"
   40 |     mode: "0640"
```

# Frozen source context: V007PILOT-SECURITY-021

- Repository: `manala/ansible-roles`
- Commit: `1ae6394d7b780665788234418ace2a060903f5f1`
- Family: Security
- Rule: `ansibleguard/unsafe-file-write`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/network/tasks/hosts.yaml` (reported anchor line 3)
- Object: `source_location` `111c5293ea919b2f57745821717585a2bc1ee1f9edc67b1f0844430ced570b30`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–9 of 9:

```text
    1 | ---
    2 | 
    3 | - name: Hosts > File
    4 |   ansible.builtin.lineinfile:
    5 |     path: "{{ manala_network_hosts_file }}"
    6 |     regexp: "^{{ item.key | regex_escape() }}\\s+"
    7 |     line: "{{ item.key ~ ' ' ~ item.value }}"
    8 |     unsafe_writes: true
    9 |   loop: "{{ manala_network_hosts | dict2items }}"
```

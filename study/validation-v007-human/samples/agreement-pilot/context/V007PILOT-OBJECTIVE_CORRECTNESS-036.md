# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-036

- Repository: `ansible-lockdown/RHEL8-CIS`
- Commit: `97a6a9aa80506900009129aa389759d6884d5ec5`
- Family: Objective correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `meta/main.yml` (reported anchor line 1)
- Object: `source_location` `540542996fba6aaa193866ec11d93562019a3ae54f928e04e59f7652131816e1`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–30 of 30:

```text
    1 | ---
    2 | galaxy_info:
    3 |   author: "Ansible-Lockdown Team"
    4 |   description: "Apply the RHEL 8 CIS benchmark"
    5 |   company: "MindPoint Group - A Tyto Athene Company"
    6 |   license: MIT
    7 |   namespace: mindpointgroup
    8 |   role_name: rhel8_cis
    9 |   min_ansible_version: 2.16.1
   10 |   platforms:
   11 |     - name: EL
   12 |       versions:
   13 |         - '8'
   14 |   galaxy_tags:
   15 |     - system
   16 |     - security
   17 |     - cis
   18 |     - hardening
   19 |     - rocky
   20 |     - alma
   21 |     - oel
   22 |     - redhat
   23 |     - rhel
   24 |     - compliance
   25 |     - complianceascode
   26 | collections:
   27 |   - community.general
   28 |   - community.crypto
   29 |   - ansible.posix
   30 | dependencies: []
```

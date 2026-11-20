# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-048

- Repository: `ansible-lockdown/RHEL8-STIG`
- Commit: `baa075468dfa59050141c99d99dcacd2e977248c`
- Family: Objective correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `meta/main.yml` (reported anchor line 1)
- Object: `source_location` `0fc7e4a9bbf5d8ac03ea60db4f846166c2d05da348d093a23096ce9452cad4a4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–30 of 30:

```text
    1 | ---
    2 | galaxy_info:
    3 |   author: "Ansible-Lockdown Team"
    4 |   description: "Apply the DISA RHEL 8 STIG"
    5 |   company: "MindPoint Group - A Tyto Athene Company"
    6 |   license: MIT
    7 |   role_name: rhel8_stig
    8 |   namespace: mindpointgroup
    9 |   min_ansible_version: '2.16.1'
   10 |   platforms:
   11 |     - name: EL
   12 |       versions:
   13 |         - '8'
   14 |   galaxy_tags:
   15 |     - system
   16 |     - security
   17 |     - stig
   18 |     - hardening
   19 |     - benchmark
   20 |     - compliance
   21 |     - redhat
   22 |     - complianceascode
   23 |     - disa
   24 |     - rhel8
   25 |     - mindpoint
   26 | collections:
   27 |   - community.general
   28 |   - community.crypto
   29 |   - ansible.posix
   30 | dependencies: []
```

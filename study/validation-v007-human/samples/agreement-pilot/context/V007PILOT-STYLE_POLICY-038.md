# Frozen source context: V007PILOT-STYLE_POLICY-038

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: Style/policy
- Rule: `ansibleguard/missing-tags`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `vagrant/provisioning/roles/virtualbox/tasks/main.yml` (reported anchor line 5)
- Object: `task` `f78bd5bb1d72aa596aeb6bff65c8f1bd7f62eba28c8e23dbd5a5440f949bde00`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–23 of 23:

```text
    1 | - name: get kernel details
    2 |   command: "uname -a"
    3 |   register: uname
    4 | 
    5 | - name: extract specific kernel version
    6 |   set_fact:
    7 |     kernel_version: "{{ uname.stdout.split(' ')[2] }}"
    8 | 
    9 | - debug:
   10 |     var: kernel_version
   11 |   
   12 | - name: required packages to build virtualbox guest additions
   13 |   become: yes
   14 |   yum:
   15 |     state: present
   16 |     name:
   17 |       - "bzip2"
   18 |       - "@Development Tools"
   19 |       - "kernel-devel-{{ kernel_version }}"
   20 |     
   21 | 
   22 | - include: get-guest-additions.yml
   23 | 
```

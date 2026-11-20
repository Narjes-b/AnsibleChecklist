# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-033

- Repository: `chrisshaiman/lamware`
- Commit: `09f919635087b38354bce34c9bc48e7c6517b463`
- Family: Maintainability/complexity
- Rule: `ansibleguard/shell-instead-of-module`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `ansible/roles/sample-feeder/tasks/main.yml` (reported anchor line 28)
- Object: `task` `c15b43081a330892ab4bc6d9594d0927f39b6274431cfd725d6fef4caf3e2a45`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–59 of 59:

```text
    1 | ---
    2 | # =============================================================================
    3 | # roles/sample-feeder/tasks/main.yml
    4 | # Deploys the MalwareBazaar sample feeder CLI tool.
    5 | #
    6 | # The feeder is an interactive CLI tool — not a daemon. The operator SSHs
    7 | # in via WireGuard and runs it manually with filters to review and submit
    8 | # samples to Cape.
    9 | #
   10 | # Author: Christopher Shaiman
   11 | # License: Apache 2.0
   12 | # =============================================================================
   13 | 
   14 | - name: Create sample-feeder install directory
   15 |   ansible.builtin.file:
   16 |     path: "{{ sample_feeder_dir }}"
   17 |     state: directory
   18 |     owner: "{{ sample_feeder_user }}"
   19 |     group: lamware
   20 |     mode: "0750"
   21 | 
   22 | - name: Install pyzipper for AES-encrypted MalwareBazaar zips
   23 |   ansible.builtin.pip:
   24 |     name: pyzipper
   25 |     state: present
   26 |     break_system_packages: true
   27 | 
   28 | - name: Fix pip package permissions for cape user
   29 |   ansible.builtin.shell: chmod -R a+rX /usr/local/lib/python3.12/dist-packages/
   30 |   args:
   31 |     executable: /bin/bash
   32 |   changed_when: false
   33 | 
   34 | # -------------------------------------------------------------------------
   35 | # Deploy CLI tool and config
   36 | # -------------------------------------------------------------------------
   37 | 
   38 | - name: Deploy sample_feeder.py
   39 |   ansible.builtin.template:
   40 |     src: sample_feeder.py.j2
   41 |     dest: "{{ sample_feeder_dir }}/sample_feeder.py"
   42 |     owner: "{{ sample_feeder_user }}"
   43 |     group: "{{ sample_feeder_user }}"
   44 |     mode: "0750"
   45 | 
   46 | - name: Write sample-feeder config
   47 |   ansible.builtin.template:
   48 |     src: sample-feeder.conf.j2
   49 |     dest: "{{ sample_feeder_dir }}/config.json"
   50 |     owner: "{{ sample_feeder_user }}"
   51 |     group: lamware
   52 |     mode: "0640"
   53 |   no_log: true
   54 | 
   55 | - name: Create convenience symlink
   56 |   ansible.builtin.file:
   57 |     src: "{{ sample_feeder_dir }}/sample_feeder.py"
   58 |     dest: /usr/local/bin/sample-feeder
   59 |     state: link
```

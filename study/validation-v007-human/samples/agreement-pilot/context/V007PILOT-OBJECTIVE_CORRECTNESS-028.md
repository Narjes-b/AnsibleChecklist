# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-028

- Repository: `rtdevx/homelab`
- Commit: `a23266aa968127747db1aa91d544ab60ce402f55`
- Family: Objective correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/bootstrap/bootstrap.yml` (reported anchor line 52)
- Object: `task` `f6fefe644fe4757adddb5cb59a8a9b57fe7833322e2da37b605f0897e0f7d709`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–63 of 63:

```text
    1 | ---
    2 | 
    3 | #
    4 | #To run first time, sudo enabled user's password is required. 
    5 | #.ssh keys and sudoers file copied in the initial run:
    6 | #
    7 | #:~>ansible-playbook --ask-become-pass ./bootstrap/bootstrap.yml -i ./inventory/bootstrap.yml
    8 | #
    9 | 
   10 | - hosts: all
   11 |   become: true
   12 |   
   13 |   pre_tasks:
   14 | 
   15 |   - name: install updates (CentOS)
   16 |     tags: always
   17 |     dnf:
   18 |       update_only: yes
   19 |       update_cache: yes
   20 |     when: ansible_distribution == "CentOS"
   21 |     register: updated
   22 | 
   23 |   - name: install updates (Ubuntu)
   24 |     tags: always   
   25 |     apt:
   26 |       upgrade: dist
   27 |       update_cache: yes
   28 |     when: ansible_distribution == "Ubuntu"
   29 |     register: updated
   30 | 
   31 |   - name: Rebooting after applying updates.
   32 |     tags: always
   33 |     reboot:
   34 |       msg: Rebooting...
   35 |     when: updated.changed
   36 | 
   37 | - hosts: all
   38 |   become: true
   39 |   tasks:
   40 | 
   41 |   - name: Add User ansible
   42 |     tags: always
   43 |     user: 
   44 |       name: ansible
   45 |       state: present
   46 |       groups: sudo
   47 |       comment: "Add User ansible"
   48 |       shell: /bin/bash
   49 | 
   50 |   - name: Update authorized_keys for user ansible
   51 |     tags: always
   52 |     authorized_key:
   53 |       user: ansible
   54 |       key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPXFX63LfEGDYBI+bT1VeaTE/L+ovz8aPvl3nTk8vcSY ansible"
   55 | 
   56 |   - name: Add sudoers file for ansible user
   57 |     tags: always
   58 |     copy:
   59 |       src: sudoer_ansible
   60 |       dest: /etc/sudoers.d/ansible
   61 |       owner: root
   62 |       group: root
   63 |       mode: 0440
```

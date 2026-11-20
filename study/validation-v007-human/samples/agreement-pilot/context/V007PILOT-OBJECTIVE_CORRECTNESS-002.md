# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-002

- Repository: `freeipa/ansible-freeipa`
- Commit: `5ba9b59d5b614abdb0af70fc9f2d336e5479e833`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/ipabackup/tasks/copy_backup_from_server.yml` (reported anchor line 34)
- Object: `source_location` `21fec760471cb358e9f2927d4fed4a5519c7cf2be593697dbd900aa2b846095b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–48 of 48:

```text
    1 | ---
    2 | - name: Fail on invalid ipabackup_item
    3 |   ansible.builtin.fail:
    4 |     msg: "ipabackup_item {{ ipabackup_item }} is not valid"
    5 |   when: ipabackup_item is not defined or
    6 |         ipabackup_item | length < 1 or
    7 |         (ipabackup_item.find("ipa-full-") == -1 and
    8 |          ipabackup_item.find("ipa-data-") == -1)
    9 | 
   10 | - name: Set controller destination directory
   11 |   ansible.builtin.set_fact:
   12 |     __derived_controller_dir:
   13 |         "{{ ipabackup_controller_path | default(lookup('env', 'PWD')) }}/{{
   14 |          ipabackup_name_prefix | default(ansible_facts['fqdn']) }}_{{
   15 |          ipabackup_item }}/"
   16 | 
   17 | - name: Stat backup on server
   18 |   ansible.builtin.stat:
   19 |     path: "{{ ipabackup_dir }}/{{ ipabackup_item }}"
   20 |   register: result_backup_stat
   21 | 
   22 | - name: Fail on missing backup directory
   23 |   ansible.builtin.fail:
   24 |     msg: "Unable to find backup {{ ipabackup_item }}"
   25 |   when: result_backup_stat.stat.isdir is not defined
   26 | 
   27 | - name: Get backup files to copy for "{{ ipabackup_item }}"
   28 |   ansible.builtin.shell:
   29 |     find . -type f | cut -d"/" -f 2
   30 |   args:
   31 |     chdir: "{{ ipabackup_dir }}/{{ ipabackup_item }}"
   32 |   register: result_find_backup_files
   33 | 
   34 | - name: Copy server backup files to controller
   35 |   ansible.builtin.fetch:
   36 |     flat: yes
   37 |     src: "{{ ipabackup_dir }}/{{ ipabackup_item }}/{{ item }}"
   38 |     dest: "{{ __derived_controller_dir }}"
   39 |   with_items:
   40 |   - "{{ result_find_backup_files.stdout_lines }}"
   41 | 
   42 | - name: Fix file modes for backup on controller
   43 |   ansible.builtin.file:
   44 |     dest: "{{ __derived_controller_dir }}"
   45 |     mode: u=rwX,go=
   46 |     recurse: yes
   47 |   delegate_to: localhost
   48 |   become: no
```

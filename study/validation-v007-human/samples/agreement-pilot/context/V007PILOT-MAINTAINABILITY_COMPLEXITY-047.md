# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-047

- Repository: `freeipa/ansible-freeipa`
- Commit: `5ba9b59d5b614abdb0af70fc9f2d336e5479e833`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-expression`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/ipabackup/tasks/main.yml` (reported anchor line 53)
- Object: `source_location` `7466a4c70e9e5f67e2ef56b6e02590fdf4eda5c4f0f1deb663e791f851f46502`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–145 of 145:

```text
    1 | ---
    2 | # tasks file for ipabackup
    3 | 
    4 | - name: Check for empty vars
    5 |   ansible.builtin.fail:
    6 |     msg: "Variable {{ item }} is empty"
    7 |   when: "item in vars and not vars[item]"
    8 |   with_items: "{{ ipabackup_empty_var_checks }}"
    9 |   vars:
   10 |     ipabackup_empty_var_checks:
   11 |     - ipabackup_backend
   12 |     - ipabackup_gpg_keyring
   13 |     - ipabackup_instance
   14 |     - ipabackup_log_file
   15 |     - ipabackup_password
   16 |     - ipabackup_name
   17 |     - ipabackup_controller_path
   18 |     - ipabackup_name_prefix
   19 |     - ipabackup_firewalld_zone
   20 | 
   21 | - name: Set ipabackup_data if ipabackup_data is not set but ipabackup_online is
   22 |   ansible.builtin.set_fact:
   23 |     ipabackup_data: yes
   24 |   when: ipabackup_online | bool and not ipabackup_data | bool
   25 | 
   26 | - name: Fail if ipabackup_from_controller and ipabackup_to_controller are set
   27 |   ansible.builtin.fail:
   28 |     msg: "ipabackup_from_controller and ipabackup_to_controller are set"
   29 |   when: ipabackup_from_controller | bool and ipabackup_to_controller | bool
   30 | 
   31 | - name: Fail for given ipabackup_name if state is not copied, restored or absent
   32 |   ansible.builtin.fail:
   33 |     msg: "ipabackup_name is given and state is not copied, restored or absent"
   34 |   when: state is not defined or
   35 |         (state != "copied" and state != "restored" and state != "absent") and
   36 |         ipabackup_name is defined
   37 | 
   38 | - name: Get ipabackup_dir from IPA installation
   39 |   ansible.builtin.include_tasks: "{{ role_path }}/tasks/get_ipabackup_dir.yml"
   40 | 
   41 | - name: Backup IPA server
   42 |   ansible.builtin.include_tasks: "{{ role_path }}/tasks/backup.yml"
   43 |   when: state|default("present") == "present"
   44 | 
   45 | - name: Fail on missing ipabackup_name
   46 |   ansible.builtin.fail:
   47 |     msg: "ipabackup_name is not set"
   48 |   when: (ipabackup_name is not defined or not ipabackup_name) and
   49 |         state is defined and
   50 |         (state == "copied" or state == "restored" or state == "absent")
   51 | 
   52 | - name: Get all backup names for copy to controller
   53 |   when: state is defined and
   54 |         ((state == "copied" and ipabackup_to_controller) or
   55 |          state == "absent") and
   56 |         ipabackup_name is defined and ipabackup_name == "all"
   57 |   block:
   58 |   - name: Get list of all backups on IPA server
   59 |     ansible.builtin.shell:
   60 |       find . -name "ipa-full-*" -o -name "ipa-data-*" | cut -d"/" -f 2
   61 |     args:
   62 |       chdir: "{{ ipabackup_dir }}/"
   63 |     register: result_backup_find_backup_files
   64 | 
   65 |   - name: Set ipabackup_names using backup list
   66 |     ansible.builtin.set_fact:
   67 |       ipabackup_names: "{{ result_backup_find_backup_files.stdout_lines }}"
   68 | 
   69 | - name: Set ipabackup_names from ipabackup_name
   70 |   when: ipabackup_names is not defined and ipabackup_name is defined
   71 |   block:
   72 |   - name: Fail on ipabackup_name all
   73 |     ansible.builtin.fail:
   74 |       msg: "ipabackup_name can not be all in this case"
   75 |     when: ipabackup_name is defined and ipabackup_name == "all"
   76 | 
   77 |   - name: Set ipabackup_names from ipabackup_name string
   78 |     ansible.builtin.set_fact:
   79 |       ipabackup_names: ["{{ ipabackup_name }}"]
   80 |     when: ipabackup_name | type_debug != "list"
   81 | 
   82 |   - name: Set ipabackup_names from ipabackup_name list
   83 |     ansible.builtin.set_fact:
   84 |       ipabackup_names: "{{ ipabackup_name }}"
   85 |     when: ipabackup_name | type_debug == "list"
   86 | 
   87 | - name: Set empty ipabackup_names if ipabackup_name is not defined
   88 |   ansible.builtin.set_fact:
   89 |     ipabackup_names: []
   90 |   when: ipabackup_names is not defined and ipabackup_name is not defined
   91 | 
   92 | - name: Process "{{ ipabackup_names }}"
   93 |   when: state is defined and
   94 |         ((state == "copied" and ipabackup_to_controller) or state == "absent")
   95 |   block:
   96 |   - name: Copy backup from IPA server
   97 |     ansible.builtin.include_tasks: "{{ role_path }}/tasks/copy_backup_from_server.yml"
   98 |     vars:
   99 |       ipabackup_item: "{{ main_item | basename }}"
  100 |     with_items:
  101 |     - "{{ ipabackup_names }}"
  102 |     loop_control:
  103 |       loop_var: main_item
  104 |     when: state is defined and state == "copied"
  105 | 
  106 |   - name: Remove backup from IPA server
  107 |     ansible.builtin.include_tasks: "{{ role_path }}/tasks/remove_backup_from_server.yml"
  108 |     vars:
  109 |       ipabackup_item: "{{ main_item | basename }}"
  110 |     with_items:
  111 |     - "{{ ipabackup_names }}"
  112 |     loop_control:
  113 |       loop_var: main_item
  114 |     when: state is defined and state == "absent"
  115 | 
  116 | # Fail with more than one entry in ipabackup_names for copy to sever and
  117 | # restore.
  118 | 
  119 | - name: Fail to copy or restore more than one backup on the server
  120 |   ansible.builtin.fail:
  121 |     msg: "Only one backup can be copied to the server or restored"
  122 |   when: state is defined and (state == "copied" or state == "restored") and
  123 |         ipabackup_from_controller | bool and ipabackup_names | length != 1
  124 | 
  125 | # Use only first item in ipabackup_names for copy to server and for restore.
  126 | 
  127 | - name: Process "{{ ipabackup_names[0] }}"
  128 |   when: ipabackup_from_controller or
  129 |         (state|default("present") == "copied" and not ipabackup_to_controller)
  130 |   vars:
  131 |     ipabackup_name: "{{ ipabackup_names[0] }}"
  132 |   block:
  133 |   - name: Copy backup to server
  134 |     ansible.builtin.include_tasks: "{{ role_path }}/tasks/copy_backup_to_server.yml"
  135 | 
  136 |   - name: Restore IPA server after copy
  137 |     ansible.builtin.include_tasks: "{{ role_path }}/tasks/restore.yml"
  138 |     when: state|default("present") == "restored"
  139 | 
  140 | - name: Restore IPA server
  141 |   ansible.builtin.include_tasks: "{{ role_path }}/tasks/restore.yml"
  142 |   vars:
  143 |     ipabackup_item: "{{ ipabackup_names[0] | basename }}"
  144 |   when: not ipabackup_from_controller and
  145 |         state|default("present") == "restored"
```

# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-047

- Repository: `wonderbird/ansible-all-my-things`
- Commit: `4993019d9dfb175eef6cb40fce4ea56138e6a374`
- Family: Objective correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `playbooks/restore/restore.yml` (reported anchor line 101)
- Object: `source_location` `0959750c27f35534494f7f15d09c174eb33137af99efd3e4809dc2ead7c44143`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–105 of 105:

```text
    1 | ---
    2 | # Usage: Import this task into your playbook
    3 | #
    4 | # Parameters
    5 | #
    6 | #   users:                      List of users to restore backup for
    7 | #   backup_file:                Name of the backup file within the backup directory.
    8 | #   destination_beneath_home:   Destination folder relative to each user's home directory
    9 | #   delete_before_beneath_home: (optional) List of files and directories to delete before restoring,
   10 | #                               relative to each user's home directory. These entries will
   11 | #                               only be deleted, if the backup file has been successfully
   12 | #                               uploaded. This allows to restore a clean backup.
   13 | #
   14 | #                               ATTENTION: This variable is always of type LIST, even if it contains
   15 | #                                          only one entry.
   16 | #
   17 | - name: Calculate backup directory
   18 |   set_fact:
   19 |     backup_dir: "{{ lookup('env', 'BACKUP_DIR') | default(playbook_dir ~ '/../../configuration/home/my_desktop_user/backup', true) }}"
   20 | 
   21 | - name: Calculate source path
   22 |   set_fact:
   23 |     source_path: "{{ (backup_dir ~ '/' ~ backup_file) | realpath }}"
   24 | 
   25 | - name: Calculate remote temp path
   26 |   set_fact:
   27 |     remote_temp_path: "/tmp/{{ backup_file }}"
   28 | 
   29 | - name: Calculate destination directories
   30 |   set_fact:
   31 |     delete_before_beneath_home: "{{ delete_before_beneath_home | default([]) | list }}"
   32 |     destinations: "{{ users | map('regex_replace', '^', '/home/') | map('regex_replace', '$', '/' + destination_beneath_home) | list }}"
   33 | 
   34 | - name: Distribute destinations across users
   35 |   set_fact:
   36 |     user_destinations: "{{ users | zip(destinations) | list }}"
   37 |     delete_before: "{{ users | product(delete_before_beneath_home) | map('join', '/') | map('regex_replace', '^', '/home/') | list }}"
   38 | 
   39 | - name: Show backup parameters
   40 |   debug:
   41 |     msg:
   42 |       - "Restoring backup:"
   43 |       - ""
   44 |       - "          Users: {{ users | list }}"
   45 |       - "         Source: {{ source_path }}"
   46 |       - "    Remote temp: {{ remote_temp_path }}"
   47 | 
   48 | - name: Show destination directories
   49 |   debug:
   50 |     msg: "- {{ item }}"
   51 |   loop: "{{ destinations }}"
   52 | 
   53 | - name: Show folders to delete before restoring
   54 |   debug:
   55 |     msg: "- {{ item }}"
   56 |   loop: "{{ delete_before }}"
   57 | 
   58 | - name: Check if backup file exists
   59 |   delegate_to: localhost
   60 |   become: false
   61 |   stat:
   62 |     path: "{{ source_path }}"
   63 |   register: backup_local
   64 | 
   65 | - name: Upload backup file
   66 |   copy:
   67 |     src: "{{ source_path }}"
   68 |     dest: "{{ remote_temp_path }}"
   69 |     mode: '0644'
   70 |   when: backup_local.stat.exists
   71 |   register: upload_result
   72 | 
   73 | - name: Clean up target directories
   74 |   file:
   75 |     path: "{{ item }}"
   76 |     state: absent
   77 |   when: not upload_result.failed | default(true)
   78 |   loop: "{{ delete_before }}"
   79 | 
   80 | - name: Ensure parent directories exist
   81 |   file:
   82 |     path: "{{ item.1 | dirname }}"
   83 |     state: directory
   84 |     mode: '0755'
   85 |     owner: "{{ item.0 }}"
   86 |     group: "{{ item.0 }}"
   87 |   when: not upload_result.failed | default(true)
   88 |   loop: "{{ user_destinations }}"
   89 | 
   90 | - name: Extract backup
   91 |   become_user: "{{ item.0 }}"
   92 |   unarchive:
   93 |     src: "{{ remote_temp_path }}"
   94 |     dest: "{{ item.1 | dirname }}"
   95 |     owner: "{{ item.0 }}"
   96 |     group: "{{ item.0 }}"
   97 |     remote_src: yes
   98 |   loop: "{{ user_destinations }}"
   99 |   when: not upload_result.failed | default(true)
  100 | 
  101 | - name: Remove temporary archive
  102 |   file:
  103 |     path: "{{ remote_temp_path }}"
  104 |     state: absent
  105 |   ignore_errors: true
```

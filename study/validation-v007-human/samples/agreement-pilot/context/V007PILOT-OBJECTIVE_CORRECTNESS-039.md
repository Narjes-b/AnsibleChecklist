# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-039

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: Objective correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `vagrant/provisioning/roles/arkcase-post-upgrade/tasks/main.yml` (reported anchor line 86)
- Object: `source_location` `addbb5b54079d48aff843f2bfdbec377c27b9b78c6f54a49cc9b084fd1919ab3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–133 of 133:

```text
    1 | - name: Get folders in a folder
    2 |   find:
    3 |     paths: "{{ root_folder }}/data/arkcase-home"
    4 |     patterns: '.arkcase-backup*'
    5 |     hidden: yes
    6 |     file_type: directory
    7 |   register: found_folders
    8 | 
    9 | - name: Get latest folder
   10 |   set_fact:
   11 |     latest_config_backup_folder: "{{ found_folders.files | sort(attribute='mtime',reverse=true) | first }}"
   12 |   ignore_errors: true
   13 | 
   14 | - name: see if we have an older version with more configurations to restore
   15 |   set_fact:
   16 |     older_config_in_use: "{{ arkcase_version != '' and (arkcase_version is version('2021.04', '<') or ( arkcase_version is version('2023.02.03', '>') and arkcase_version is version('2024', '<'))) }}"
   17 | 
   18 | - name: see if we need to restore the extra configurations from older versions
   19 |   set_fact:
   20 |     restore_more_config_files: "{{ arkcase_version != '' and latest_config_backup_folder is not none and older_config_in_use }}"
   21 | 
   22 | - name: log incoming versions
   23 |   debug:
   24 |     msg: "arkcase-version: {{ arkcase_version }}; latest_config_backup_folder: {{ latest_config_backup_folder }}; older_config_in_use: {{ older_config_in_use }}; restore_more_config_files: {{ restore_more_config_files }}"
   25 | 
   26 | 
   27 | - name: restore config files (2021.03 and below)
   28 |   become: yes
   29 |   become_user: arkcase
   30 |   command: cp {{ latest_config_backup_folder.path }}/acm/{{ item }} {{ root_folder }}/data/arkcase-home/.arkcase/acm/{{ item }}
   31 |   loop:
   32 |     - "acmSequenceConfiguration.json"
   33 |   when: restore_more_config_files
   34 | 
   35 | - name: Restore runtime files from previous backup
   36 |   become: yes
   37 |   become_user: arkcase
   38 |   command: rsync -avm --include='*runtime*' -f 'hide,! */' {{ latest_config_backup_folder.path }}/acm/acm-config-server-repo/ {{ root_folder }}/data/arkcase-home/.arkcase/acm/acm-config-server-repo/
   39 |   when: latest_config_backup_folder is defined
   40 |   ignore_errors: true
   41 | 
   42 | - name: find "templates-configuration.json" file (2021.03 and below)
   43 |   become: yes
   44 |   become_user: arkcase
   45 |   stat:
   46 |     path: "{{ latest_config_backup_folder.path }}/acm/templates-configuration.json"
   47 |   register: template_file
   48 |   when: restore_more_config_files
   49 | 
   50 | - name: copy a new "templates-configuration.json" file into place, backing up the original if it differs from the copied version  (2021.03 and bellow)
   51 |   become: yes
   52 |   become_user: arkcase
   53 |   copy:
   54 |     src: "{{ latest_config_backup_folder.path }}/acm/templates-configuration.json"
   55 |     dest: /home/arkcase/.arkcase/acm
   56 |     owner: arkcase
   57 |     group: arkcase
   58 |     mode: '0666'
   59 |     backup: true
   60 |     remote_src: yes
   61 |   when:  restore_more_config_files and template_file.stat.exists
   62 | 
   63 | - name: match the file naming (2021.03 and below)
   64 |   become: yes
   65 |   become_user: arkcase
   66 |   find:
   67 |     paths: "{{ latest_config_backup_folder.path }}/acm/correspondenceTemplates"
   68 |     file_type: file
   69 |     use_regex: yes
   70 |     patterns: ['([0-9]{4})(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])(2[0-3]|[01][0-9])([0-5][0-9])([0-5][0-9]_.*..docx)']
   71 |   register: files_to_copy
   72 |   when: restore_more_config_files
   73 | 
   74 | - name: copy matched files (2021.03 and below)
   75 |   become: yes
   76 |   become_user: arkcase
   77 |   copy:
   78 |     src: "{{ item.path }}"
   79 |     dest: /home/arkcase/.arkcase/acm/correspondenceTemplates
   80 |     owner: arkcase
   81 |     group: arkcase
   82 |     remote_src: yes
   83 |   with_items: "{{ files_to_copy.files }}"
   84 |   when: restore_more_config_files and files_to_copy is defined and (arkcase_version != "" and arkcase_version is version('2020.18', '>='))
   85 | 
   86 | - name: find files with 640 permissions (2021.03 and below)
   87 |   become: yes
   88 |   become_user: arkcase
   89 |   command: find {{ latest_config_backup_folder.path }}/acm/templates -type f -perm 640 -name "*.html"
   90 |   register: files
   91 |   when: latest_config_backup_folder is defined
   92 |   ignore_errors: true
   93 | 
   94 | - name: copy files (2021.03 and below)
   95 |   become: yes
   96 |   become_user: arkcase
   97 |   copy:
   98 |     src: "{{ item }}"
   99 |     dest: /home/arkcase/.arkcase/acm/templates
  100 |     owner: arkcase
  101 |     group: arkcase
  102 |     mode: '0640'
  103 |     remote_src: yes
  104 |   with_items: "{{ files.stdout_lines }}"
  105 |   when: restore_more_config_files and (arkcase_version != "" and arkcase_version is version('2020.18', '>='))
  106 | 
  107 | - name: read current setenv.sh
  108 |   become: yes
  109 |   become_user: arkcase
  110 |   command: cat {{ root_folder }}/app/arkcase/bin/setenv.sh
  111 |   register: setenv_contents
  112 |   changed_when: false
  113 | 
  114 | - name: ensure ldap is in the profile (no other profiles already exist)
  115 |   become: yes
  116 |   become_user: arkcase
  117 |   blockinfile:
  118 |     path: "{{ root_folder }}/app/arkcase/bin/setenv.sh"
  119 |     insertbefore: EOF
  120 |     marker: "# {mark} ANSIBLE MANAGED BLOCK - Core"
  121 |     block: |
  122 |       export JAVA_OPTS="$JAVA_OPTS -Dspring.profiles.active=ldap"
  123 |   when: '"-Dspring.profiles.active" not in setenv_contents.stdout'
  124 | 
  125 | - name: copy pdftron annotation files
  126 |   become: yes
  127 |   become_user: arkcase
  128 |   copy:
  129 |     src: "{{ item }}"
  130 |     dest: "{{ root_folder }}/data/arkcase-home/.arkcase/pdftron/annotations/"
  131 |     remote_src: yes
  132 |   with_fileglob:
  133 |     - "{{ latest_config_backup_folder.path }}/pdftron/annotations/*"
```

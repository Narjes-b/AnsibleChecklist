# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-049

- Repository: `UtrechtUniversity/yoda`
- Commit: `a9175010319fee30fb056665e9821937f0ec07c5`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/yoda_rulesets/tasks/main.yml` (reported anchor line 8)
- Object: `source_location` `0f6caeab3deeb549efd54cab556a8720e07269ea1d033fd2d0273333ab06d74c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–177 of 177:

```text
    1 | ---
    2 | # copyright Utrecht University
    3 | 
    4 | - name: Include OS-specific variables
    5 |   ansible.builtin.include_vars: "{{ ansible_os_family }}.yml"
    6 | 
    7 | 
    8 | - name: Check out rulesets without local patches from Github
    9 |   become_user: "{{ irods_service_account }}"
   10 |   become: true
   11 |   ansible.builtin.git:
   12 |     repo: "{{ item.repo }}"
   13 |     dest: "/etc/irods/{{ item.name }}"
   14 |     version: "{{ item.version }}"
   15 |     update: "{{ update_rulesets }}"
   16 |     force: true
   17 |   with_items: "{{ extra_rulesets + core_rulesets }}"
   18 |   when: "'repo' in item and 'patch' not in item"
   19 |   register: repochanges
   20 |   notify: Restart iRODS
   21 | 
   22 | 
   23 | - name: Check out rulesets with local patches from Github
   24 |   become_user: "{{ irods_service_account }}"
   25 |   become: true
   26 |   ansible.builtin.git:
   27 |     repo: "{{ item.repo }}"
   28 |     dest: "/etc/irods/repo_{{ item.name }}"
   29 |     version: "{{ item.version }}"
   30 |     update: "{{ update_rulesets }}"
   31 |   with_items: "{{ extra_rulesets + core_rulesets }}"
   32 |   when: "'repo' in item and 'patch' in item"
   33 |   register: patch_repochanges
   34 |   notify: Restart iRODS
   35 | 
   36 | 
   37 | - name: Sync rulesets with repos before applying patches
   38 |   become_user: "{{ irods_service_account }}"
   39 |   become: true
   40 |   ansible.posix.synchronize:
   41 |     src: "/etc/irods/repo_{{ item.name }}/"
   42 |     dest: "/etc/irods/{{ item.name }}"
   43 |     checksum: true
   44 |     delete: true
   45 |     rsync_opts:
   46 |       - "--exclude=rules_uu.cfg"
   47 |   delegate_to: "{{ inventory_hostname }}"
   48 |   with_items: "{{ extra_rulesets + core_rulesets }}"
   49 |   when: "not ansible_check_mode and 'repo' in item and 'patch' in item"
   50 | 
   51 | 
   52 | - name: Create patch files for rulesets
   53 |   become_user: "{{ irods_service_account }}"
   54 |   become: true
   55 |   ansible.builtin.copy: # noqa template-instead-of-copy
   56 |     dest: "/etc/irods/{{ item.name }}.patch"
   57 |     content: "{{ item['patch'] }}"
   58 |     mode: '0644'
   59 |   with_items: "{{ extra_rulesets + core_rulesets }}"
   60 |   when: "'repo' in item and 'patch' in item"
   61 | 
   62 | 
   63 | - name: Apply patches to rulesets
   64 |   become_user: "{{ irods_service_account }}"
   65 |   become: true
   66 |   ansible.builtin.command: # noqa no-changed-when command-instead-of-module
   67 |     chdir: "/etc/irods/{{ item.name }}"
   68 |     cmd: "git apply /etc/irods/{{ item.name }}.patch"
   69 |   with_items: "{{ extra_rulesets + core_rulesets }}"
   70 |   when: "'repo' in item and 'patch' in item and item['patch'] not in ['']"
   71 |   notify: Restart iRODS
   72 | 
   73 | 
   74 | - name: Remove temporary rule and cache files
   75 |   become_user: '{{ irods_service_account }}'
   76 |   become: true
   77 |   ansible.builtin.command: # noqa no-changed-when no-handler
   78 |     cmd: '/bin/find /etc/irods -type f ( -name "*.re.*" -o -name "*.pyc" ) -delete'
   79 |   when: repochanges.changed or patch_repochanges.changed
   80 | 
   81 | 
   82 | - name: Run make install for each ruleset
   83 |   become_user: "{{ irods_service_account }}"
   84 |   become: true
   85 |   community.general.make:
   86 |     chdir: "/etc/irods/{{ item.0.name }}"
   87 |     target: install
   88 |   when: "'repo' in item.0"
   89 |   changed_when: item.1.changed or ( 'repo' in item.0 and 'patch' in item.0 )
   90 |   with_together:
   91 |     - "{{ extra_rulesets + core_rulesets }}"
   92 |     - "{{ repochanges.results }}"
   93 |     - "{{ patch_repochanges.results }}"
   94 | 
   95 | 
   96 | - name: Install requirements for ruleset
   97 |   become_user: "{{ irods_service_account }}"
   98 |   become: true
   99 |   ansible.builtin.pip:
  100 |     requirements: /etc/irods/yoda-ruleset/requirements.txt
  101 |     extra_args: --user --break-system-packages
  102 |     executable: "{{ yoda_rulesets_pip3_path }}"
  103 |   when: ansible_os_family == 'Debian'
  104 | 
  105 | 
  106 | - name: Install requirements for ruleset
  107 |   become_user: "{{ irods_service_account }}"
  108 |   become: true
  109 |   ansible.builtin.pip:
  110 |     requirements: /etc/irods/yoda-ruleset/requirements.txt
  111 |     executable: "{{ yoda_rulesets_pip3_path }}"
  112 |   when: ansible_os_family == 'RedHat'
  113 | 
  114 | 
  115 | - name: Link ruleset directory
  116 |   ansible.builtin.file:
  117 |     src: "{{ ruleset.name }}"
  118 |     dest: "/etc/irods/{{ ruleset.ruleset_name | replace('-', '_') }}"
  119 |     state: link
  120 |   with_items: "{{ extra_rulesets + core_rulesets }}"
  121 |   loop_control:
  122 |     loop_var: ruleset
  123 |   when: ruleset.install_scripts
  124 | 
  125 | 
  126 | - name: Create local Yoda ruleset configuration
  127 |   ansible.builtin.template:
  128 |     src: rules_uu.cfg.j2
  129 |     dest: "/etc/irods/yoda-ruleset/rules_uu.cfg"
  130 |     owner: '{{ irods_service_account }}'
  131 |     group: '{{ irods_service_account }}'
  132 |     mode: '0600'
  133 |   no_log: true
  134 |   when: not ansible_check_mode
  135 | 
  136 | 
  137 | - name: Ensure all rulesets are in server config
  138 |   become_user: "{{ irods_service_account }}"
  139 |   become: true
  140 |   # noqa fqcn[action]
  141 |   irods_rulesets:
  142 |     config_path: "/etc/irods/server_config.json"
  143 |     rulesets: "{{ (extra_rulesets + core_rulesets) | map(attribute='ruleset_name') | list }}"
  144 |   when: not ansible_check_mode
  145 |   notify: Restart iRODS
  146 | 
  147 | 
  148 | - name: Flush handlers to restart iRODS if needed
  149 |   ansible.builtin.meta: flush_handlers
  150 | 
  151 | 
  152 | - name: Ensure Python rules are loaded
  153 |   become_user: "{{ irods_service_account }}"
  154 |   become: true
  155 |   ansible.builtin.copy:
  156 |     src: "core.py"
  157 |     dest: "/etc/irods/core.py"
  158 |     mode: '0644'
  159 | 
  160 | 
  161 | - name: Copy securecopy script to ExecCmd dir
  162 |   become_user: "{{ irods_service_account }}"
  163 |   become: true
  164 |   ansible.builtin.copy:
  165 |     remote_src: true
  166 |     src: "/etc/irods/yoda-ruleset/tools/securecopy.sh"
  167 |     dest: "/var/lib/irods/msiExecCmd_bin/securecopy.sh"
  168 |     mode: '0755'
  169 |   when: not ansible_check_mode
  170 | 
  171 | 
  172 | - name: Install Yoda rulesets
  173 |   ansible.builtin.include_tasks: "{{ ruleset.name }}.yml"
  174 |   with_items: "{{ extra_rulesets + core_rulesets }}"
  175 |   loop_control:
  176 |     loop_var: ruleset
  177 |   when: ruleset.install_scripts and 'icats' in group_names
```

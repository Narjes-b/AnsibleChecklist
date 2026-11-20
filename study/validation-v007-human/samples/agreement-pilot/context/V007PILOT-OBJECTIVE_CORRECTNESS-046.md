# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-046

- Repository: `roots/trellis`
- Commit: `cd8e671076918a82efb43d5a313451f4e71da318`
- Family: Objective correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/users/tasks/main.yml` (reported anchor line 88)
- Object: `task` `129c2969e9bea6500cc8f5fe78a623006859e87c8bd866b8cdd505c6ea9fdf8d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–105 of 105:

```text
    1 | ---
    2 | - name: Ensure requested groups are present
    3 |   group:
    4 |     name: "{{ item }}"
    5 |     state: present
    6 |   loop: "{{ users | sum(attribute='groups', start=[]) | list | unique }}"
    7 | 
    8 | - name: Ensure sudo group has sudo privileges
    9 |   lineinfile:
   10 |     dest: /etc/sudoers
   11 |     state: present
   12 |     regexp: "^%sudo"
   13 |     line: "%sudo ALL=(ALL:ALL) ALL"
   14 |     validate: "/usr/sbin/visudo -cf %s"
   15 | 
   16 | - name: Fail if root login will be disabled but admin_user will not be a sudoer
   17 |   assert:
   18 |     that:
   19 |       - "{{ 'sudo' in (users | selectattr('name', 'equalto', admin_user) | map(attribute='groups') | first | default([])) }}"
   20 |       - "{{ (vault_users | default([]) | selectattr('name', 'equalto', admin_user) | first | default({})).password is defined }}"
   21 |     msg: |
   22 |       When `sshd_permit_root_login: false`, you must add `sudo` to the `groups` for admin_user (in `users` hash), and set a password for admin_user in `vault_users` (in `group_vars/{{ env }}/vault.yml`). Otherwise Ansible could lose the ability to run the necessary sudo commands. {% if sudoer_passwords is defined or vault_sudoer_passwords is defined %}
   23 | 
   24 | 
   25 |       Please note that `sudoer_passwords` and `vault_sudoer_passwords have been replaced with `vault_users`. {% endif %}
   26 |       More info:
   27 |       > https://roots.io/trellis/docs/security/#admin-user-sudoer-password
   28 |   when: not sshd_permit_root_login
   29 |   tags: sshd
   30 | 
   31 | - name: Hash user passwords
   32 |   command:
   33 |     cmd: |
   34 |       mkpasswd -m sha-512 --salt={{ (item.salt | default(''))[:16] |  regex_replace("[^\.\/a-zA-Z0-9]", "x") }}
   35 |     stdin: "{{ item.password }}"
   36 |   loop: "{{ vault_users | default([]) }}"
   37 |   loop_control:
   38 |     label: "{{ item.name }}"
   39 |   when: item.password is defined
   40 |   register: user_passwords_hashed
   41 |   no_log: true
   42 |   changed_when: false
   43 | 
   44 | - name: Setup users
   45 |   user:
   46 |     name: "{{ item.name }}"
   47 |     group: "{{ item.groups[0] }}"
   48 |     groups: "{{ item.groups | join(',') }}"
   49 |     password: "{{ (user_passwords_hashed.results | selectattr('item.name', 'equalto', item.name) | map(attribute='stdout') | first) | default(omit) }}"
   50 |     state: present
   51 |     shell: /bin/bash
   52 |     update_password: "{{ item.update_password | default('always') }}"
   53 |   loop: "{{ users }}"
   54 |   loop_control:
   55 |     label: "{{ item.name }}"
   56 | 
   57 | - name: Add web user sudoers items for services
   58 |   template:
   59 |     src: sudoers.d.j2
   60 |     dest: "/etc/sudoers.d/{{ web_user }}-services"
   61 |     mode: '0440'
   62 |     owner: root
   63 |     group: root
   64 |     validate: "/usr/sbin/visudo -cf %s"
   65 |   when: web_sudoers[0] is defined
   66 | 
   67 | - name: Replace all user SSH keys with first non-empty key
   68 |   authorized_key:
   69 |     user: "{{ item.name }}"
   70 |     key: "{{ (item['keys'] | select('truthy') | list).0 }}"
   71 |     exclusive: true
   72 |   loop: "{{ users | default([]) }}"
   73 |   loop_control:
   74 |     label: "{{ item.name }}"
   75 |   when:
   76 |     - reset_user_ssh_keys | default(false)
   77 |     - (item['keys'] | select('truthy') | list | length) > 0
   78 | 
   79 | - name: Add user SSH keys
   80 |   authorized_key:
   81 |     user: "{{ item.0.name }}"
   82 |     key: "{{ item.1 }}"
   83 |   loop: "{{ users | default([]) | subelements('keys') }}"
   84 |   loop_control:
   85 |     label: "{{ item.0.name }}"
   86 | 
   87 | - name: Add deploy SSH keys
   88 |   authorized_key:
   89 |     user: "{{ web_user }}"
   90 |     key: "{{ lookup('file', item) }}"
   91 |   with_fileglob: 'public_keys/*.pub'
   92 | 
   93 | - name: Check whether Ansible can connect as admin_user
   94 |   command: ansible {{ inventory_hostname }} -m ping -u {{ admin_user }} {{ cli_options | default('') }}
   95 |   delegate_to: localhost
   96 |   failed_when: false
   97 |   changed_when: false
   98 |   become: no
   99 |   register: admin_user_status
  100 |   when: (ansible_user != admin_user and not sshd_permit_root_login) or (cli_ask_pass | default(false) and not sshd_password_authentication)
  101 |   tags: [connection-tests, sshd]
  102 | 
  103 | - import_tasks: connection-warnings.yml
  104 |   when: admin_user_status is not skipped and admin_user_status.rc != 0
  105 |   tags: [connection-tests, sshd]
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-018

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: Maintainability/complexity
- Rule: `ansibleguard/incomplete-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `onecloud/roles/mariadb-ha/tasks/main.yml` (reported anchor line 37)
- Object: `source_location` `228710b3997cd8f5bf4fc7092c718887d4c873e6c70a0edeee7bff65fcd113c7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–91 of 91:

```text
    1 | ---
    2 | - name: gather os specific variables
    3 |   include_vars: "{{ item }}"
    4 |   with_first_found:
    5 |     - files:
    6 |         - "{{ ansible_distribution|lower | replace(' ', '_')}}-{{ ansible_architecture }}.yml"
    7 |         - "{{ ansible_distribution|lower }}-{{ ansible_distribution_major_version|lower|replace('/', '_') }}.yml"
    8 |         - "{{ ansible_distribution|lower }}-{{ ansible_distribution_release|lower }}.yml"
    9 |         - "{{ ansible_distribution|lower }}-{{ ansible_distribution_major_version|lower|replace('/', '_') }}.yml"
   10 |         - "{{ ansible_distribution|lower }}.yml"
   11 |         - "{{ ansible_os_family|lower }}.yml"
   12 |         - "{{ ansible_distribution|lower| replace(' ', '_')| replace('_\"_', '') }}.yml"
   13 |       paths:
   14 |         - ../vars
   15 |   tags:
   16 |     - facts
   17 | 
   18 | - name: Install mariadb
   19 |   package:
   20 |     name: "{{ item }}"
   21 |     state: present
   22 |   failed_when: false
   23 |   loop: "{{ mariadb_package_info.pkgs }}"
   24 | 
   25 | - name: pips for mysql/mariadb
   26 |   pip:
   27 |     name: PyMySQL
   28 |   vars:
   29 |     ansible_python_interpreter: /usr/bin/python3
   30 | 
   31 | - name: copy my.cnf
   32 |   template:
   33 |     src: my.cnf.j2
   34 |     dest: /etc/my.cnf
   35 |     backup: yes
   36 | 
   37 | - name: mariadb config hack
   38 |   shell: |
   39 |     if [ ! -d /etc/my.cnf.d ] && [ -d /etc/mysql ]; then
   40 |       ln -sf /etc/mysql /etc/my.cnf.d
   41 |     fi
   42 |     if [ -f /etc/mysql/mariadb.conf.d/50-server.cnf ] && grep -qP 'bind-address *= *127.0.0.1' /etc/mysql/mariadb.conf.d/50-server.cnf; then
   43 |       cp -vf /etc/mysql/mariadb.conf.d/50-server.cnf /etc/mysql/mariadb.conf.d/50-server.cnf.$(date +"%Y%m%d-%H%M%S").bak
   44 |       sed -i 's#bind-address *= *127.0.0.1#bind-address = 0.0.0.0#' /etc/mysql/mariadb.conf.d/50-server.cnf
   45 |     fi
   46 |     systemctl restart mariadb
   47 |   args:
   48 |     executable: /bin/bash
   49 | 
   50 | - name: start mariadb
   51 |   systemd:
   52 |     name: mariadb
   53 |     enabled: yes
   54 |     state: started
   55 | 
   56 | - name: Change root password
   57 |   mysql_user:
   58 |     login_unix_socket: "{{ login_unix_socket }}"
   59 |     login_user: "{{ db_user }}"
   60 |     login_port: "{{ db_port | default(3306) }}"
   61 |     login_password: "{{ db_password }}"
   62 |     password: "{{ db_password }}"
   63 |     name: "{{ db_user }}"
   64 |     priv: '*.*:ALL,GRANT'
   65 |     host: "{{ item }}"
   66 |     check_implicit_admin: true
   67 |   loop:
   68 |     - "localhost"
   69 |     - "%"
   70 |     - "::1"
   71 |     - "127.0.0.1"
   72 |   vars:
   73 |     ansible_python_interpreter: /usr/bin/python3
   74 | 
   75 | - name: Remove all anonymous user accounts
   76 |   mysql_user:
   77 |     name: ''
   78 |     host_all: yes
   79 |     state: absent
   80 |     login_user: "{{ db_user }}"
   81 |     login_password: "{{ db_password }}"
   82 | 
   83 | - name: Remove test database
   84 |   mysql_db:
   85 |     name: test
   86 |     state: absent
   87 |     login_user: "{{ db_user }}"
   88 |     login_password: "{{ db_password }}"
   89 | 
   90 | - when: groups['mariadb_ha_nodes'] | length > 1
   91 |   include_tasks: 05ha.yml
```

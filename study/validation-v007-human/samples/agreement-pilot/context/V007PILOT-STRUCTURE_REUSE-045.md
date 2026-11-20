# Frozen source context: V007PILOT-STRUCTURE_REUSE-045

- Repository: `oliversalzburg/ansible-workstation`
- Commit: `635ab67d1fdf72ea4de69556c8dd428626699df5`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `provision/ansible/roles/podman_radarr/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `e9bfca179e7b31b8530f85aaa6cc2e79b90bde573fa1ea9fad709a51ccee12e0`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–145 of 145:

```text
    1 | ---
    2 | - name: Create groups
    3 |   become: true
    4 |   register: _podman_radarr_groups
    5 |   ansible.builtin.group:
    6 |     name: "{{ item }}"
    7 |     state: present
    8 |     system: true
    9 |   loop: "{{ podman_radarr_groups }}"
   10 |   notify: Restart radarr
   11 | 
   12 | - name: Ensure user is a group member
   13 |   become: true
   14 |   ansible.builtin.user:
   15 |     name: "{{ ansible_user }}"
   16 |     groups: "{{ podman_radarr_groups }}"
   17 |     append: true
   18 |   notify: Restart radarr
   19 | 
   20 | - name: Create user
   21 |   become: true
   22 |   register: _podman_radarr_user
   23 |   ansible.builtin.user:
   24 |     comment: "{{ podman_radarr_name }}"
   25 |     create_home: false
   26 |     group: "{{ _podman_radarr_groups.results[0].gid }}"
   27 |     groups: "{{ podman_radarr_groups }}"
   28 |     home: "{{ podman_radarr_basedir }}"
   29 |     name: "{{ podman_radarr_id }}"
   30 |     password: [REDACTED_LITERAL]
   31 |     shell: "/usr/sbin/nologin"
   32 |     system: true
   33 |   notify: Restart radarr
   34 | 
   35 | 
   36 | - name: Ensure working directory exists
   37 |   become: true
   38 |   ansible.builtin.file:
   39 |     path: "{{ podman_radarr_basedir }}"
   40 |     state: directory
   41 |     owner: "{{ _podman_radarr_user.uid }}"
   42 |     group: "{{ _podman_radarr_groups.results[0].gid }}"
   43 |     mode: "0o750"
   44 |   notify: Restart radarr
   45 | 
   46 | - name: Ensure directories exist
   47 |   become: true
   48 |   ansible.builtin.file:
   49 |     path: "{{ podman_radarr_basedir }}/{{ item }}"
   50 |     state: directory
   51 |     owner: "{{ _podman_radarr_user.uid }}"
   52 |     group: "{{ _podman_radarr_groups.results[0].gid }}"
   53 |     mode: "0o750"
   54 |   loop:
   55 |     - config
   56 |   notify: Restart radarr
   57 | 
   58 | 
   59 | - name: Create postgres user
   60 |   register: podman_radarr_result
   61 |   retries: 3
   62 |   delay: 3
   63 |   until: podman_radarr_result is not failed
   64 |   community.postgresql.postgresql_user:
   65 |     login_host: localhost
   66 |     login_password: "{{ podman_postgres_master_password }}"
   67 |     login_user: "{{ podman_postgres_master_user }}"
   68 |     name: "{{ podman_radarr_pg_user }}"
   69 |     password: "{{ podman_radarr_pg_password }}"
   70 |   notify: Restart radarr
   71 | 
   72 | - name: Create postgres database
   73 |   register: podman_radarr_result
   74 |   retries: 3
   75 |   delay: 3
   76 |   until: podman_radarr_result is not failed
   77 |   community.postgresql.postgresql_db:
   78 |     login_host: localhost
   79 |     login_password: "{{ podman_postgres_master_password }}"
   80 |     login_user: "{{ podman_postgres_master_user }}"
   81 |     name: "{{ podman_radarr_pg_db }}-{{ item }}"
   82 |     owner: "{{ podman_radarr_pg_user }}"
   83 |   loop:
   84 |     - main
   85 |     - log
   86 |   notify: Restart radarr
   87 | 
   88 | - name: "GRANT ALL PRIVILEGES ON DATABASE 'db' TO 'user'"
   89 |   community.postgresql.postgresql_privs:
   90 |     login_host: localhost
   91 |     login_password: "{{ podman_postgres_master_password }}"
   92 |     login_user: "{{ podman_postgres_master_user }}"
   93 |     login_db: postgres
   94 |     privs: ALL
   95 |     type: database
   96 |     obj: "{{ podman_radarr_pg_db }}-{{ item }}"
   97 |     role: "{{ podman_radarr_pg_user }}"
   98 |   loop:
   99 |     - main
  100 |     - log
  101 |   notify: Restart radarr
  102 | 
  103 | - name: "GRANT USAGE, CREATE ON SCHEMA PUBLIC TO 'user'"
  104 |   community.postgresql.postgresql_privs:
  105 |     login_host: localhost
  106 |     login_password: "{{ podman_postgres_master_password }}"
  107 |     login_user: "{{ podman_postgres_master_user }}"
  108 |     login_db: postgres
  109 |     privs: CREATE
  110 |     type: schema
  111 |     obj: public
  112 |     role: "{{ podman_radarr_pg_user }}"
  113 |   notify: Restart radarr
  114 | 
  115 | 
  116 | - name: Copy configuration
  117 |   become: true
  118 |   ansible.builtin.template:
  119 |     src: "config.xml.j2"
  120 |     dest: "{{ podman_radarr_basedir }}/config/config.xml"
  121 |     owner: "{{ _podman_radarr_user.uid }}"
  122 |     group: "{{ _podman_radarr_groups.results[0].gid }}"
  123 |     mode: "0o640"
  124 |   notify: Restart radarr
  125 | 
  126 | 
  127 | - name: Copy service files
  128 |   become: true
  129 |   ansible.builtin.template:
  130 |     src: "{{ item }}.j2"
  131 |     dest: "{{ directory_systemd }}/{{ item }}"
  132 |     owner: root
  133 |     group: root
  134 |     mode: "0o644"
  135 |   loop:
  136 |     - radarr-main.service
  137 |     - radarr.service
  138 |   notify: Restart radarr
  139 | 
  140 | - name: Enable and check radarr service
  141 |   become: true
  142 |   ansible.builtin.systemd:
  143 |     enabled: true
  144 |     name: radarr
  145 |   notify: Restart radarr
```

## Frozen tracked paths in the relevant role/scope

```text
provision/ansible/roles/podman_radarr/defaults/main.yml
provision/ansible/roles/podman_radarr/handlers/main.yml
provision/ansible/roles/podman_radarr/tasks/main.yml
provision/ansible/roles/podman_radarr/templates/config.xml.j2
provision/ansible/roles/podman_radarr/templates/radarr-exporter.service.j2
provision/ansible/roles/podman_radarr/templates/radarr-main.service.j2
provision/ansible/roles/podman_radarr/templates/radarr.service.j2
```

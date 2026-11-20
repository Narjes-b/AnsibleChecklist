# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-029

- Repository: `vrk-kpa/api-catalog`
- Commit: `e81b1cb5a261a290a78eafae67f853efc8f5f7a3`
- Family: Objective correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/roles/postgres/tasks/main.yml` (reported anchor line 20)
- Object: `source_location` `233c7a69f54b2ac628681c0a30987cea3651b20e8c72b2c4b169ad9f85034d16`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–50 of 50:

```text
    1 | ---
    2 | 
    3 | - name: Install postgres
    4 |   apt: pkg={{ item }} state=latest
    5 |   with_items:
    6 |     - postgresql
    7 | 
    8 | - name: Copy postgres configurations
    9 |   template: src={{ item.file }} dest={{ item.dest }} owner=postgres group=postgres mode="0640"
   10 |   with_items:
   11 |   - { file: pg_hba.conf.j2, dest: "/etc/postgresql/{{ system.postgresql.version }}/main/pg_hba.conf" }
   12 |   - { file: postgresql.conf.j2, dest: "/etc/postgresql/{{ system.postgresql.version }}/main/postgresql.conf" }
   13 | 
   14 | - name: Generate self-signed SSL certificate
   15 |   command: openssl req -new -nodes -x509 -subj "/C=FI/ST=Helsinki/L=Helsinki/O=IT/CN={{ public_facing_hostname }}" -days 3650 -keyout "/var/lib/postgresql/{{ system.postgresql.version }}/main/server.key" -out "/var/lib/postgresql/{{ system.postgresql.version }}/main/server.crt" -extensions v3_ca creates="/var/lib/postgresql/{{ system.postgresql.version }}/main/server.crt"
   16 | 
   17 | - name: Set certificate file ownership and mode
   18 |   shell: chmod 600 /var/lib/postgresql/{{ system.postgresql.version }}/main/server.* && chown "postgres:postgres" /var/lib/postgresql/{{ system.postgresql.version }}/main/server.*
   19 | 
   20 | - name: Ensure CKAN is not running before making changes to the database
   21 |   supervisorctl: name="{{ ckan_supervisor_name }}" state=stopped
   22 |   ignore_errors: True
   23 | 
   24 | - name: Restart postgres
   25 |   service: name=postgresql state=restarted
   26 | 
   27 | - name: Setup postgres users
   28 |   become_user: postgres
   29 |   become: true
   30 |   postgresql_user: user={{ item.user }} password={{ item.password }} encrypted=yes
   31 |   with_items:
   32 |   - { user: "{{ database_ckan.username }}", password: "{{ database_ckan.password }}" }
   33 | 
   34 | - name: Setup postgres databases
   35 |   become_user: postgres
   36 |   postgresql_db: name={{ item.name }} owner={{ item.owner }} encoding={{ item.encoding }} lc_collate={{ item.collate }} lc_ctype={{ item.ctype }} template={{ item.template }}
   37 |   with_items:
   38 |   - { name: "{{ database_ckan.name }}", owner: "{{ database_ckan.username }}", encoding: 'UTF-8', collate: 'fi_FI.UTF-8', ctype: 'en_US.UTF-8', template: 'template0' }
   39 |   ignore_errors: True
   40 | 
   41 | 
   42 | - block:
   43 |     - name: Setup postgres test database
   44 |       become_user: postgres
   45 |       postgresql_db: name={{ item.name }} owner={{ item.owner }} encoding={{ item.encoding }} lc_collate={{ item.collate }} lc_ctype={{ item.ctype }} template={{ item.template }}
   46 |       with_items:
   47 | 
   48 |         - { name: "{{ database_test.name }}", owner: "{{ database_test.username }}", encoding: 'UTF-8', collate: 'fi_FI.UTF-8', ctype: 'en_US.UTF-8', template: 'template0' }
   49 |       ignore_errors: True
   50 |   when: deployment_environment_id == 'vagrant'
```

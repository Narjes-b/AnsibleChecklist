# Frozen source context: V007PILOT2-SECURITY-012

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `roles/lockers_and_study_spaces/defaults/main.yml` (reported anchor line 31)
- Flagged construct: variable `vault_postgres_admin_password`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–46 of 46:

```text
    1 | ---
    2 | # defaults file for roles/lockers_and_study_spaces
    3 | rails_app_env: "production"
    4 | install_mailcatcher: false
    5 | app_secret_key: [REDACTED_LITERAL]
    6 | app_db_name: 'lockers_and_study_spaces'
    7 | app_db_user: 'lockers_and_study_spaces'
    8 | app_db_password: [REDACTED_LITERAL]
    9 | app_db_host: 'localhost'
   10 | app_host_name: 'localhost'
   11 | application_host_protocol: 'http'
   12 | lockers_honeybadger_key: changeme
   13 | lockers_secret_key_base: [REDACTED_LITERAL]
   14 | logrotate_rules:
   15 |   - name: "lockers_and_study_spaces"
   16 |     paths:
   17 |       - "/opt/{{ rails_app_directory }}/current/log/*.log"
   18 |     options:
   19 |       rotate: "{{ logrotate_global_defaults.rotate }}"
   20 |       maxsize: "{{ logrotate_global_defaults.maxsize }}"
   21 |       create_mode: "{{ logrotate_global_defaults.create_mode }}"
   22 |       create_owner: "{{ logrotate_global_defaults.create_owner }}"
   23 |       create_group: "{{ logrotate_global_defaults.create_group }}"
   24 |       su_user: "{{ logrotate_global_defaults.su_user }}"
   25 |       su_group: "{{ logrotate_global_defaults.su_group }}"
   26 | # postgres test VM settings
   27 | postgres_port: 5432
   28 | postgres_version: 15
   29 | postgres_host: postgres
   30 | postgres_admin_user: postgres
   31 | vault_postgres_admin_password: [REDACTED_LITERAL]
   32 | postgres_apt_key_url: "https://www.postgresql.org/media/keys/ACCC4CF8.asc"
   33 | postgres_apt_repository: "deb http://apt.postgresql.org/pub/repos/apt {{ ansible_distribution_release }}-pgdg main"
   34 | postgres_apt_key_path: "/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc"
   35 | postgres_apt_repository_uri: "https://apt.postgresql.org/pub/repos/apt"
   36 | postgres_apt_source_types: "deb"
   37 | postgres_apt_components: "main"
   38 | # database creation settings
   39 | postgres_database_encoding: "UTF8"
   40 | postgres_database_locale: "{{ postgres_locale | default('en_US.UTF-8') }}"
   41 | postgres_database_lc_collate: "{{ postgres_database_locale }}"
   42 | postgres_database_lc_ctype: "{{ postgres_database_locale }}"
   43 | postgres_database_template: "template0"
   44 | # architecture support
   45 | postgres_supported_architecture: "x86_64"
   46 | postgres_apt_architecture: "amd64"
```

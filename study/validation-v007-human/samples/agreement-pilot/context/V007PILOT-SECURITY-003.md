# Frozen source context: V007PILOT-SECURITY-003

- Repository: `folio-org/folio-ansible`
- Commit: `dde7c5f2011b34eb79b03ef38f334b34449e67af`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/deprecated/mod-auth-data/defaults/main.yml` (reported anchor line 7)
- Object: `source_location` `f5c66c4bb58c0be563061196655a9da5f83c47e7793a52cfa6c72c6e4b34eaa3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–56 of 56:

```text
    1 | ---
    2 | okapi_port: 9130
    3 | 
    4 | okapi_url: "http://{{ ansible_default_ipv4.address }}:{{ okapi_port }}"
    5 | 
    6 | pg_admin_user: folio_admin
    7 | pg_admin_password: [REDACTED_LITERAL]
    8 | pg_host: "{{ ansible_default_ipv4.address }}"
    9 | pg_port: 5432
   10 | 
   11 | module_database: okapi_modules
   12 | 
   13 | # Prefixes for module ids
   14 | mod_auth_prefixes:
   15 |   - permissions-module
   16 |   - authtoken-module
   17 |   - login-module
   18 |   - mod-users
   19 | 
   20 | # Schema names for db
   21 | mod_permissions_schema: diku_permissions_module
   22 | mod_login_schema: diku_login_module
   23 | mod_users_schema: diku_mod_users
   24 | 
   25 | admin_user:
   26 |   username: diku_admin
   27 |   password: admin
   28 |   hash: 52DCA1934B2B32BEA274900A496DF162EC172C1E
   29 |   salt: 483A7C864569B90C24A0A6151139FF0B95005B16
   30 |   perms_user_id: 2408ae64-56ad-4177-9024-1e35fe5d895c
   31 |   permissions: "\\\"perms.all\\\""
   32 |   id: 1ad737b0-d847-11e6-bf26-cec0c932ce01
   33 |   first_name: DIKU
   34 |   last_name: ADMINISTRATOR
   35 |   email: admin@diku.example.org
   36 | 
   37 | admin_permissions:
   38 |   - login.all
   39 |   - users.all
   40 | 
   41 | # Permissions not defined in module descriptors
   42 | additional_permissions: []
   43 | 
   44 | mod_auth_users:
   45 |   - username: auth_test1
   46 |     id: 77136CF1-FF93-4C45-B7B5-187BCB711745
   47 |     perms_user_id: e12e46e4-9293-4f75-99ab-181633ab9530
   48 |     password: [REDACTED_LITERAL]
   49 |   - username: auth_test2
   50 |     id: 17B39C4D-FFAE-4D62-A75D-1B22F45A081E
   51 |     perms_user_id: f0977134-cd1a-4e0d-978e-9cad29e9a98a
   52 |     password: [REDACTED_LITERAL]
   53 | 
   54 | auth_by_username: false
   55 | 
   56 | top_down_install: false
```

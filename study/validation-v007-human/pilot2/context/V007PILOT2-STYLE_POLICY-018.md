# Frozen source context: V007PILOT2-STYLE_POLICY-018

- Repository: `folio-org/folio-ansible`
- Commit: `dde7c5f2011b34eb79b03ef38f334b34449e67af`
- Family: style_policy
- Rule: `ansibleguard/unnamed-task`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/deprecated/mod-calendar-data/tasks/main.yml` (reported anchor line 5)
- Flagged construct: not named by the finding; the anchor line 5 lies in the task at line 5, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–74 of 74:

```text
    1 | ---
    2 | # Role to enable mod-calendar for the sample tenant
    3 | 
    4 | # wait a few seconds to make sure modules are spun up
    5 | - wait_for: timeout=10
    6 | 
    7 | - set_fact:
    8 |     mod_calendar_module: "{{ okapi_modules|selectattr('id','match','^'+mod_calendar_prefix+'(-[0-9].*)?$')|list }}"
    9 | 
   10 | - name: Check tenant mod-calendar registration
   11 |   uri:
   12 |     url: "{{ okapi_url }}/_/proxy/tenants/diku/modules/{{ mod_calendar_module.0.id }}"
   13 |     status_code: 200, 404
   14 |   register: tenant_mod_calendar
   15 | 
   16 | - name: Enable mod-calendar module for tenant
   17 |   uri:
   18 |     url: "{{ okapi_url }}/_/proxy/tenants/diku/modules"
   19 |     method: POST
   20 |     body_format: json
   21 |     body: '{ "id" : "{{ mod_calendar_module.0.id }}" }'
   22 |     status_code: 201
   23 |   register: mod_calendar_enable
   24 |   changed_when: mod_calendar_enable.status == 201
   25 |   when: tenant_mod_calendar.status == 404 and not top_down_install
   26 | 
   27 | - name: Login as {{ admin_user.username }}
   28 |   uri:
   29 |     url: "{{ okapi_url }}/authn/login"
   30 |     method: POST
   31 |     body_format: json
   32 |     headers:
   33 |       X-Okapi-Tenant: diku
   34 |       Accept: application/json
   35 |     body: "{ 'username' : '{{ admin_user.username }}', 'password' : '{{ admin_user.password }}' }"
   36 |     status_code: 201
   37 |   register: mod_calendar_login
   38 |   when: auth_required
   39 | 
   40 | - name: Assign mod-calendar permissions to other users (auth by username)
   41 |   uri:
   42 |     url: "{{ okapi_url }}/perms/users/{{ item.0.username }}/permissions"
   43 |     method: POST
   44 |     body_format: json
   45 |     headers:
   46 |       X-Okapi-Tenant: diku
   47 |       X-Okapi-Token: "{{ mod_calendar_login.x_okapi_token }}"
   48 |       Accept: application/json
   49 |     body: '{ "permissionName" : "{{ item.1 }}" }'
   50 |     status_code: 200,422
   51 |   register: mod_calendar_perms
   52 |   changed_when: mod_calendar_perms.status == 200
   53 |   with_subelements:
   54 |     - "{{ mod_calendar_permissions }}"
   55 |     - permissions
   56 |   when: auth_required and auth_by_username
   57 | 
   58 | - name: Assign mod-calendar permissions to other users (auth by id)
   59 |   uri:
   60 |     url: "{{ okapi_url }}/perms/users/{{ item.0.perms_user_id }}/permissions"
   61 |     method: POST
   62 |     body_format: json
   63 |     headers:
   64 |       X-Okapi-Tenant: diku
   65 |       X-Okapi-Token: "{{ mod_calendar_login.x_okapi_token }}"
   66 |       Accept: application/json
   67 |     body: '{ "permissionName" : "{{ item.1 }}" }'
   68 |     status_code: 200,422
   69 |   register: mod_calendar_perms
   70 |   changed_when: mod_calendar_perms.status == 200
   71 |   with_subelements:
   72 |     - "{{ mod_calendar_permissions }}"
   73 |     - permissions
   74 |   when: auth_required and not auth_by_username
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-021

- Repository: `folio-org/folio-ansible`
- Commit: `dde7c5f2011b34eb79b03ef38f334b34449e67af`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/deprecated/mod-codex-ekb-data/tasks/main.yml` (reported anchor line 90)
- Object: `task` `bd46d646be5626248d00490a853cfd46d532b3778270deffbf026ffde8f305cd`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–134 of 134:

```text
    1 | ---
    2 | # wait a few seconds to make sure modules are spun up
    3 | - wait_for: timeout=10
    4 |   
    5 | - name: set fact mod_codex_ekb_module
    6 |   set_fact:
    7 |     mod_codex_ekb_module: "{{ okapi_modules|selectattr('id','match','^'+mod_codex_ekb_prefix+'(-[0-9].*)?$')|list }}"
    8 | 
    9 | - name: Check mod-codex-ekb deployment
   10 |   uri: 
   11 |     url: "{{ okapi_url }}/_/discovery/modules/{{ mod_codex_ekb_module.0.id }}"
   12 |     status_code: 200, 404
   13 |   register: mod_codex_ekb_deploy
   14 |   when: not top_down_install
   15 | 
   16 | - name: Set mod-codex-ekb deployment status for top down install
   17 |   set_fact: 
   18 |     mod_codex_ekb_deploy:
   19 |       status: 200
   20 |   when: mod_codex_ekb_deploy.skipped is defined and mod_codex_ekb_deploy.skipped
   21 |       
   22 | - name: Check tenant mod-codex-ekb registration
   23 |   uri:
   24 |     url: "{{ okapi_url }}/_/proxy/tenants/diku/modules/{{ mod_codex_ekb_module.0.id }}"
   25 |     status_code: 200, 404
   26 |   when: mod_codex_ekb_deploy.status == 200
   27 |   register: tenant_mod_codex_ekb
   28 | 
   29 | - name: Enable mod-codex-ekb module for tenant
   30 |   uri:
   31 |     url: "{{ okapi_url }}/_/proxy/tenants/diku/modules"
   32 |     method: POST
   33 |     body_format: json
   34 |     body: '{ "id" : "{{ mod_codex_ekb_module.0.id }}" }'
   35 |     status_code: 201
   36 |   register: mod_codex_ekb_enable
   37 |   changed_when: mod_codex_ekb_enable.status == 201
   38 |   when: tenant_mod_codex_ekb.status == 404 and not top_down_install
   39 | 
   40 | - name: Login as {{ admin_user.username }}
   41 |   uri: 
   42 |     url: "{{ okapi_url }}/authn/login"
   43 |     method: POST
   44 |     body_format: json
   45 |     headers: 
   46 |       X-Okapi-Tenant: diku
   47 |       Accept: application/json
   48 |     body: "{ 'username' : '{{ admin_user.username }}', 'password' : '{{ admin_user.password }}' }"
   49 |     status_code: 201
   50 |   register: mod_codex_ekb_login
   51 |   when: mod_codex_ekb_deploy.status == 200 and auth_required
   52 | 
   53 | - name: Assign mod-codex-ekb permissions to other users (auth by username)
   54 |   uri: 
   55 |     url: "{{ okapi_url }}/perms/users/{{ item.0.username }}/permissions"
   56 |     method: POST
   57 |     body_format: json
   58 |     headers: 
   59 |       X-Okapi-Tenant: diku
   60 |       X-Okapi-Token: "{{ mod_codex_ekb_login.x_okapi_token }}"
   61 |       Accept: application/json
   62 |     body:  '{ "permissionName" : "{{ item.1 }}" }'
   63 |     status_code: 200,422
   64 |   register: mod_codex_ekb_perms
   65 |   changed_when: mod_codex_ekb_perms.status == 200
   66 |   with_subelements: 
   67 |     - "{{ mod_codex_ekb_permissions }}"
   68 |     - permissions
   69 |   when: mod_codex_ekb_deploy.status == 200 and auth_required and auth_by_username
   70 | 
   71 | - name: Assign mod-codex-ekb permissions to other users (auth by id)
   72 |   uri: 
   73 |     url: "{{ okapi_url }}/perms/users/{{ item.0.perms_user_id }}/permissions"
   74 |     method: POST
   75 |     body_format: json
   76 |     headers: 
   77 |       X-Okapi_Tenant: diku
   78 |       X-Okapi-Token: "{{ mod_codex_ekb_login.x_okapi_token }}"
   79 |       Accept: application/json
   80 |     body: '{ "permissionName" : "{{ item.1 }}" }'
   81 |     status_code: 200,422
   82 |   register: mod_codex_ekb_perms
   83 |   changed_when: mod_codex_ekb_perms.status == 200
   84 |   with_subelements: 
   85 |     - "{{ mod_codex_ekb_permissions }}" 
   86 |     - permissions
   87 |   when: mod_codex_ekb_deploy.status == 200 and auth_required and not auth_by_username 
   88 |  
   89 | # Add RM API key
   90 | - name: Add RM API customer ID
   91 |   uri: 
   92 |     url: "{{ okapi_url }}/configurations/entries"
   93 |     method: POST
   94 |     body_format: json
   95 |     headers: 
   96 |       Authtoken-Refresh-Cache: [REDACTED_LITERAL]
   97 |       X-Okapi-Tenant: diku
   98 |       X-Okapi-Token: "{{ mod_codex_ekb_login.x_okapi_token }}"
   99 |       Accept: application/json
  100 |     body: '{ "module": "EKB", "configName": "api_access", "code": "kb.ebsco.customerId", "description": "EBSCO RM-API Customer ID", "enabled": true, "value": "{{ rmapi_custid }}" }'
  101 |     status_code: 201,422
  102 |   register: mod_codex_ekb_custid 
  103 |   changed_when: mod_codex_ekb_custid.status == 201
  104 |   when: mod_codex_ekb_deploy.status == 200 and auth_required and rmapi and rmapi_custid
  105 |    
  106 | - name: Add RM API key
  107 |   uri: 
  108 |     url: "{{ okapi_url }}/configurations/entries"
  109 |     method: POST
  110 |     body_format: json
  111 |     headers: 
  112 |       X-Okapi-Tenant: diku
  113 |       X-Okapi-Token: "{{ mod_codex_ekb_login.x_okapi_token }}"
  114 |       Accept: application/json
  115 |     body: '{ "module": "EKB", "configName": "api_access", "code": "kb.ebsco.apiKey", "description": "EBSCO RM-API API Key", "enabled": true, "value": "{{ rmapi_key }}" }'
  116 |     status_code: 201,422
  117 |   register: mod_codex_ekb_apikey
  118 |   changed_when: mod_codex_ekb_apikey.status =[REDACTED_LITERAL]
  119 |   when: mod_codex_ekb_deploy.status == 200 and auth_required and rmapi and rmapi_key
  120 | 
  121 | - name: Add RM API URL
  122 |   uri: 
  123 |     url: "{{ okapi_url }}/configurations/entries"
  124 |     method: POST
  125 |     body_format: json
  126 |     headers: 
  127 |       X-Okapi-Tenant: diku
  128 |       X-Okapi-Token: "{{ mod_codex_ekb_login.x_okapi_token }}"
  129 |       Accept: application/json
  130 |     body: '{ "module": "EKB", "configName": "api_access", "code": "kb.ebsco.url", "description": "EBSCO RM-API URL", "enabled": true, "value": "{{ rmapi_url }}" }'
  131 |     status_code: 201,422
  132 |   register: mod_codex_ekb_url
  133 |   changed_when: mod_codex_ekb_url.status == 201
  134 |   when: mod_codex_ekb_deploy.status == 200 and auth_required and rmapi and rmapi_url
```

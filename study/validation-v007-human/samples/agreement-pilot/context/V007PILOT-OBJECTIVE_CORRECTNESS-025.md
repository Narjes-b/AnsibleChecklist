# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-025

- Repository: `folio-org/folio-ansible`
- Commit: `dde7c5f2011b34eb79b03ef38f334b34449e67af`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/okapi-tenant-deploy/tasks/main.yml` (reported anchor line 22)
- Object: `source_location` `90785239cc4af0292ea26b9d91356d97ee3bcd0ed49bfb37f84540e9a0d57cbc`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–99 of 99:

```text
    1 | ---
    2 | - name: Set Okapi environment
    3 |   uri:
    4 |     url: "{{ okapi_url }}/_/env"
    5 |     method: POST
    6 |     body_format: json
    7 |     headers:
    8 |       X-Okapi-Tenant: "supertenant"
    9 |       X-Okapi-Token: "{{ supertenant_token | default('') }}"
   10 |       Accept: application/json, text/plain
   11 |     body: "{{ item|to_json }}"
   12 |     status_code: 201
   13 |   register: set_okapi_env
   14 |   changed_when: set_okapi_env.status == 201
   15 |   with_items: "{{ module_env }}"
   16 | 
   17 | - name: Post deployment descriptors for remote modules
   18 |   include_tasks: okapi-discovery.yml
   19 |   when: folio_install_type == "single_server" and item.url is defined
   20 |   with_items: "{{ folio_modules }}"
   21 | 
   22 | - name: Build tenant parameter list
   23 |   set_fact:
   24 |     tenant_parameters: "{{ tenant_parameters|default([]) + item.tenant_parameters }}"
   25 |   when: item.tenant_parameters|default(false)
   26 |   with_items: "{{ folio_modules }}"
   27 | 
   28 | - name: Discard duplicates in tenant parameter list
   29 |   set_fact:
   30 |     tenant_parameters: "{{ tenant_parameters|default([])|unique }}"
   31 | 
   32 | - name: Convert tenant parameter list to query string
   33 |   set_fact:
   34 |     tenant_param_querystr: "{{ tenant_param_querystr|default('') + item.name + '%3D' + item.value }}{% if item != tenant_parameters[-1] %}%2C{% endif %}"
   35 |   with_items: "{{ tenant_parameters }}"
   36 | 
   37 | - name: Create dict for install object
   38 |   set_fact:
   39 |     install_obj:
   40 |       action: enable
   41 | 
   42 | - name: Build install list for modules with deployment
   43 |   set_fact:
   44 |     install_deploy: "{{ install_deploy|default([]) + [ install_obj|combine({'id': item.name + '-' + item.version}) ] if item.version is defined else install_deploy|default([]) + [ install_obj|combine({'id': item.name}) ] }}"
   45 |   when: folio_install_type == "single_server" and item.name not in omit_enable and item.url is not defined and item.deploy is defined and item.deploy is sameas true
   46 |   with_items: "{{ folio_modules }}"
   47 | 
   48 | - name: Build install list for modules without deployment
   49 |   set_fact:
   50 |     install: "{{ install|default([]) + [ install_obj|combine({'id': item.name + '-' + item.version}) ] if item.version is defined else install|default([]) + [ install_obj|combine({'id': item.name}) ] }}"
   51 |   when: (folio_install_type == "kubernetes" or item.url is defined or item.deploy is not defined or item.deploy is sameas false) and item.name not in omit_enable
   52 |   with_items: "{{ folio_modules }}"
   53 | 
   54 | - name: Post install list for deployment and enabling
   55 |   uri:
   56 |     url: "{{ okapi_url }}/_/proxy/tenants/{{ tenant }}/install?deploy=true{% if tenant_param_querystr|default(false) %}&tenantParameters={{ tenant_param_querystr }}{% endif %}"
   57 |     method: POST
   58 |     body_format: json
   59 |     headers:
   60 |       X-Okapi-Tenant: "supertenant"
   61 |       X-Okapi-Token: "{{ supertenant_token | default('') }}"
   62 |       Accept: application/json, text/plain
   63 |     body: "{{ install_deploy }}"
   64 |     timeout: "{{ deploy_timeout }}"
   65 |   register: deploy_request
   66 |   changed_when: deploy_request.status == 200
   67 |   when: install_deploy|default(false)
   68 | 
   69 | - name: Post install list for enabling modules (no deployment)
   70 |   uri:
   71 |     url: "{{ okapi_url }}/_/proxy/tenants/{{ tenant }}/install{% if tenant_param_querystr|default(false) %}?tenantParameters={{ tenant_param_querystr }}{% endif %}"
   72 |     method: POST
   73 |     body_format: json
   74 |     headers:
   75 |       X-Okapi-Tenant: "supertenant"
   76 |       X-Okapi-Token: "{{ supertenant_token | default('') }}"
   77 |       Accept: application/json, text/plain
   78 |     body: "{{ install }}"
   79 |     timeout: "{{ deploy_timeout }}"
   80 |   register: install_request
   81 |   changed_when: install_request.status == 200
   82 |   when: install|default(false)
   83 | 
   84 | - name: Create directory for saving install files
   85 |   become: yes
   86 |   file:
   87 |     path: "{{ save_dir }}"
   88 |     state: directory
   89 |   when: save_install and (install|default(false) or install_deploy|default(false))
   90 | 
   91 | - name: Save okapi-install.json
   92 |   become: yes
   93 |   copy: dest={{ save_dir }}/okapi-install.json content={{ install_deploy|to_nice_json }}
   94 |   when: save_install and (install_deploy|default(false))
   95 | 
   96 | - name: Save stripes-install.json
   97 |   become: yes
   98 |   copy: dest={{ save_dir }}/stripes-install.json content={{ install|to_nice_json }}
   99 |   when: save_install and (install|default(false))
```

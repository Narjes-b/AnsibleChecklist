# Frozen source context: V007PILOT-SECURITY-029

- Repository: `ansible/galaxy-operator`
- Commit: `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/galaxy-config/tasks/sso-configuration.yml` (reported anchor line 165)
- Object: `task` `c4a6b542babb8c0af22b63113f6af80d7d96d1c2d083373d9fb4d35c0d41388c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–244 of 244:

```text
    1 | ---
    2 | - k8s_status:
    3 |     api_version: "{{ api_version }}"
    4 |     kind: "{{ kind }}"
    5 |     name: "{{ ansible_operator_meta.name }}"
    6 |     namespace: "{{ ansible_operator_meta.namespace }}"
    7 |     conditions:
    8 |       - type: "{{ deployment_type|capitalize }}-API-Ready"
    9 |         message: Checking SSO Secret configurations
   10 |         reason: CheckingSSOSecret
   11 |         status: "False"
   12 |         lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
   13 | 
   14 | - name: Check for specified sso configuration secret
   15 |   k8s_info:
   16 |     kind: Secret
   17 |     namespace: '{{ ansible_operator_meta.namespace }}'
   18 |     name: '{{ sso_secret }}'
   19 |   register: _sso_configuration
   20 |   no_log: "{{ no_log }}"
   21 | 
   22 | - name: Check sso secret data format
   23 |   set_fact:
   24 |     sso_secret_data_available: [REDACTED_LITERAL]
   25 |   when:
   26 |     - _sso_configuration is defined
   27 |     - _sso_configuration.resources is defined
   28 |     - _sso_configuration.resources[0] is defined
   29 |     - _sso_configuration.resources[0].data is defined
   30 | 
   31 | - block:
   32 |   - k8s_status:
   33 |       api_version: "{{ api_version }}"
   34 |       kind: "{{ kind }}"
   35 |       name: "{{ ansible_operator_meta.name }}"
   36 |       namespace: "{{ ansible_operator_meta.namespace }}"
   37 |       conditions:
   38 |         - type: "{{ deployment_type|capitalize }}-API-Ready"
   39 |           message: Unexpected format in SSO Secret
   40 |           reason: UnexpectedSSOSecretFormat
   41 |           status: "False"
   42 | 
   43 |   - name: Fail if sso secret object is an unexpected format
   44 |     fail:
   45 |       msg: "Cannot read the data for secret {{ _sso_configuration  }}"
   46 |   when:
   47 |     - not sso_secret_data_available
   48 | 
   49 | - name: Check if social_auth_keycloak_key is found
   50 |   set_fact:
   51 |     social_auth_keycloak_key_available: true
   52 |   when:
   53 |     - _sso_configuration.resources[0].data['social_auth_keycloak_key'] is defined
   54 |     - _sso_configuration.resources[0].data['social_auth_keycloak_key'] | length
   55 | 
   56 | - name: Check if social_auth_keycloak_secret is found
   57 |   set_fact:
   58 |     social_auth_keycloak_secret_available: [REDACTED_LITERAL]
   59 |   when:
   60 |     - _sso_configuration.resources[0].data['social_auth_keycloak_secret'] is defined
   61 |     - _sso_configuration.resources[0].data['social_auth_keycloak_secret'] | length
   62 | 
   63 | - name: Check if social_auth_keycloak_public_key is found
   64 |   set_fact:
   65 |     social_auth_keycloak_public_key_available: true
   66 |   when:
   67 |     - _sso_configuration.resources[0].data['social_auth_keycloak_public_key'] is defined
   68 |     - _sso_configuration.resources[0].data['social_auth_keycloak_public_key'] | length
   69 | 
   70 | - name: Store social_auth_keycloak_public_key
   71 |   set_fact:
   72 |     social_auth_keycloak_public_key: "{{ _sso_configuration.resources[0].data['social_auth_keycloak_public_key'] | b64decode }}"
   73 |   no_log: "{{ no_log }}"
   74 | 
   75 | - name: Check if keycloak_host is found
   76 |   set_fact:
   77 |     keycloak_host_available: true
   78 |   when:
   79 |     - _sso_configuration.resources[0].data['keycloak_host'] is defined
   80 |     - _sso_configuration.resources[0].data['keycloak_host'] | length
   81 | 
   82 | - name: Check if keycloak_protocol is found
   83 |   set_fact:
   84 |     keycloak_protocol_available: true
   85 |   when:
   86 |     - _sso_configuration.resources[0].data['keycloak_protocol'] is defined
   87 |     - _sso_configuration.resources[0].data['keycloak_protocol'] | length
   88 | 
   89 | - name: Check if keycloak_port is found
   90 |   set_fact:
   91 |     keycloak_port_available: true
   92 |   when:
   93 |     - _sso_configuration.resources[0].data['keycloak_port'] is defined
   94 |     - _sso_configuration.resources[0].data['keycloak_port'] | length
   95 | 
   96 | - name: Check if keycloak_realm is found
   97 |   set_fact:
   98 |     keycloak_realm_available: true
   99 |   when:
  100 |     - _sso_configuration.resources[0].data['keycloak_realm'] is defined
  101 |     - _sso_configuration.resources[0].data['keycloak_realm'] | length
  102 | 
  103 | - name: Check if keycloak_admin_role is found
  104 |   set_fact:
  105 |     keycloak_admin_role_available: true
  106 |   when:
  107 |     - _sso_configuration.resources[0].data['keycloak_admin_role'] is defined
  108 |     - _sso_configuration.resources[0].data['keycloak_admin_role'] | length
  109 | 
  110 | - name: Check if keycloak_group_token_claim is found
  111 |   set_fact:
  112 |     keycloak_group_token_claim_available: [REDACTED_LITERAL]
  113 |   when:
  114 |     - _sso_configuration.resources[0].data['keycloak_group_token_claim'] is defined
  115 |     - _sso_configuration.resources[0].data['keycloak_group_token_claim'] | length
  116 | 
  117 | - name: Check if keycloak_role_token_claim is found
  118 |   set_fact:
  119 |     keycloak_role_token_claim_available: [REDACTED_LITERAL]
  120 |   when:
  121 |     - _sso_configuration.resources[0].data['keycloak_role_token_claim'] is defined
  122 |     - _sso_configuration.resources[0].data['keycloak_role_token_claim'] | length
  123 | 
  124 | - name: Check if keycloak_host_loopback is found
  125 |   set_fact:
  126 |     keycloak_host_loopback_available: true
  127 |   when:
  128 |     - _sso_configuration.resources[0].data['keycloak_host_loopback'] is defined
  129 |     - _sso_configuration.resources[0].data['keycloak_host_loopback'] | length
  130 | 
  131 | ### Check to make sure all required sso config values are set before proceeding
  132 | - block:
  133 |   - k8s_status:
  134 |       api_version: "{{ api_version }}"
  135 |       kind: "{{ kind }}"
  136 |       name: "{{ ansible_operator_meta.name }}"
  137 |       namespace: "{{ ansible_operator_meta.namespace }}"
  138 |       conditions:
  139 |         - type: "{{ deployment_type|capitalize }}-API-Ready"
  140 |           message: Missing SSO fields on Secret
  141 |           reason: MissingSSOFields
  142 |           status: "False"
  143 |           lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
  144 | 
  145 |   - name: Fail if required sso secret items are not present
  146 |     fail:
  147 |       msg: "Secret {{ sso_secret }} is missing required configuration data."
  148 | 
  149 |   when:
  150 |     - sso_secret_data_available
  151 |     - not social_auth_keycloak_key_available
  152 |     - not social_auth_keycloak_secret_available
  153 |     - not social_auth_keycloak_public_key_available
  154 |     - not keycloak_host_available
  155 |     - not keycloak_protocol_available
  156 |     - not keycloak_port_available
  157 |     - not keycloak_realm_available
  158 | 
  159 | ### Store Required Variables
  160 | - name: Store social_auth_keycloak_key
  161 |   set_fact:
  162 |     social_auth_keycloak_key: "{{ _sso_configuration.resources[0].data['social_auth_keycloak_key'] | b64decode }}"
  163 |   no_log: "{{ no_log }}"
  164 | 
  165 | - name: Store social_auth_keycloak_secret
  166 |   set_fact:
  167 |     social_auth_keycloak_secret: "{{ _sso_configuration.resources[0].data['social_auth_keycloak_secret'] | b64decode }}"
  168 |   no_log: "{{ no_log }}"
  169 | 
  170 | - name: Store social_auth_keycloak_public_key
  171 |   set_fact:
  172 |     social_auth_keycloak_public_key: "{{ _sso_configuration.resources[0].data['social_auth_keycloak_public_key'] | b64decode }}"
  173 |   no_log: "{{ no_log }}"
  174 | 
  175 | - name: Store keycloak_host
  176 |   set_fact:
  177 |     keycloak_host: "{{ _sso_configuration.resources[0].data['keycloak_host'] | b64decode }}"
  178 |   no_log: "{{ no_log }}"
  179 | 
  180 | - name: Store keycloak_protocol
  181 |   set_fact:
  182 |     keycloak_protocol: "{{ _sso_configuration.resources[0].data['keycloak_protocol'] | b64decode }}"
  183 |   no_log: "{{ no_log }}"
  184 | 
  185 | - name: Store keycloak_port
  186 |   set_fact:
  187 |     keycloak_port: "{{ _sso_configuration.resources[0].data['keycloak_port'] | b64decode }}"
  188 |   no_log: "{{ no_log }}"
  189 | 
  190 | - name: Store keycloak_realm
  191 |   set_fact:
  192 |     keycloak_realm: "{{ _sso_configuration.resources[0].data['keycloak_realm'] | b64decode }}"
  193 |   no_log: "{{ no_log }}"
  194 | 
  195 | ### Store Optional Variables
  196 | - name: Store keycloak_admin_role
  197 |   set_fact:
  198 |     keycloak_admin_role: "{{ _sso_configuration.resources[0].data['keycloak_admin_role'] | b64decode }}"
  199 |   when: keycloak_admin_role_available | default(False)
  200 |   no_log: "{{ no_log }}"
  201 | 
  202 | - name: Store keycloak_group_token_claim
  203 |   set_fact:
  204 |     keycloak_group_token_claim: "{{ _sso_configuration.resources[0].data['keycloak_group_token_claim'] | b64decode }}"
  205 |   when: keycloak_group_token_claim_available | default(False)
  206 |   no_log: "{{ no_log }}"
  207 | 
  208 | - name: Store keycloak_role_token_claim
  209 |   set_fact:
  210 |     keycloak_role_token_claim: "{{ _sso_configuration.resources[0].data['keycloak_role_token_claim'] | b64decode }}"
  211 |   when: keycloak_role_token_claim_available | default(False)
  212 |   no_log: "{{ no_log }}"
  213 | 
  214 | - name: Store keycloak_host_loopback
  215 |   set_fact:
  216 |     keycloak_host_loopback: "{{ _sso_configuration.resources[0].data['keycloak_host_loopback'] | b64decode }}"
  217 |   when: keycloak_host_loopback_available | default(False)
  218 |   no_log: "{{ no_log }}"
  219 | 
  220 | - name: Add SSO settings to sso_settings dict
  221 |   block:
  222 | 
  223 |     - set_fact:
  224 |         sso_settings:
  225 |           social_auth_keycloak_key: "{{ social_auth_keycloak_key }}"
  226 |           social_auth_keycloak_secret: "{{ social_auth_keycloak_secret }}"
  227 |           social_auth_keycloak_public_key: "{{ social_auth_keycloak_public_key }}"
  228 |           social_auth_login_redirect_url: "{{ social_auth_login_redirect_url | default(omit) }}"
  229 |           social_auth_redirect_is_https: True
  230 |           keycloak_host: "{{ keycloak_host }}"
  231 |           keycloak_port: "{{ keycloak_port }}"
  232 |           keycloak_protocol: "{{ keycloak_protocol }}"
  233 |           keycloak_realm: "{{ keycloak_realm }}"
  234 |           keycloak_admin_role: "{{ keycloak_admin_role }}"
  235 |           keycloak_group_token_claim: "{{ keycloak_group_token_claim | default(omit) }}"
  236 |           keycloak_role_token_claim: "{{ keycloak_role_token_claim | default(omit) }}"
  237 |           keycloak_host_loopback: "{{ keycloak_host_loopback | default(omit) }}"
  238 | 
  239 |     - name: Inject SSO settings into pulp_settings
  240 |       set_fact:
  241 |         pulp_combined_settings: "{{ pulp_combined_settings | combine(sso_settings, recursive=True) }}"
  242 | 
  243 |   run_once: true
  244 |   no_log: "{{ no_log }}"
```

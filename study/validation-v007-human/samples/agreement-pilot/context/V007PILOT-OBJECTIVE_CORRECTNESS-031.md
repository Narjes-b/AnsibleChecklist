# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-031

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/kafka_connect_replicator/tasks/rbac_replicator_consumer.yml` (reported anchor line 76)
- Object: `source_location` `22ae455e1768c273e4517b0909db2b0725b01094f6cc56ce6247ce1f65fb282b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–410 of 410:

```text
    1 | ---
    2 | - name: Decide Where to delegate task of getting superuser token
    3 |   set_fact:
    4 |     delegation_target: >-
    5 |       {%- if external_mds_enabled | bool and (mds_ssl_client_authentication != 'none' or oauth_superuser_client_assertion_enabled | bool) -%}
    6 |         localhost
    7 |       {%- elif oauth_superuser_client_assertion_enabled | bool or mds_ssl_client_authentication != 'none' -%}
    8 |         {{ groups['kafka_broker'][0] }}
    9 |       {%- else -%}
   10 |         {{ inventory_hostname }}
   11 |       {%- endif -%}
   12 | 
   13 | - name: Get Authorization Token for Connect Replicator Consumer ERP User
   14 |   import_role:
   15 |     name: common
   16 |     tasks_from: get_authorization_token.yml
   17 |   vars:
   18 |     oauth: "{{ kafka_connect_replicator_oauth_enabled }}"
   19 |     oauth_user: "{{ kafka_connect_replicator_consumer_erp_oauth_user }}"
   20 |     oauth_password: "{{ kafka_connect_replicator_consumer_erp_oauth_password }}"
   21 |     ldap_user: "{{ kafka_connect_replicator_consumer_erp_admin_user }}"
   22 |     ldap_password: "{{ kafka_connect_replicator_consumer_erp_admin_password }}"
   23 |     mtls_client_cert: "{{ mds_super_user_external_cert_path if external_mds_enabled|bool else kafka_broker_cert_path }}"
   24 |     mtls_client_key: "{{ mds_super_user_external_key_path if external_mds_enabled|bool else kafka_broker_key_path }}"
   25 |     cert_auth_only_enabled: "{{ kafka_connect_replicator_mds_cert_auth_only|bool }}"
   26 |     oauth_client_assertion_enabled: "{{ kafka_connect_replicator_consumer_erp_oauth_client_assertion_enabled }}"
   27 |     oauth_client_assertion_issuer: "{{ kafka_connect_replicator_consumer_erp_oauth_client_assertion_issuer }}"
   28 |     oauth_client_assertion_sub: "{{ kafka_connect_replicator_consumer_erp_oauth_client_assertion_sub }}"
   29 |     oauth_client_assertion_audience: "{{ kafka_connect_replicator_consumer_erp_oauth_client_assertion_audience }}"
   30 |     oauth_client_assertion_private_key_file: "{{ kafka_connect_replicator_consumer_erp_oauth_client_assertion_private_key_file_dest_path }}"
   31 |     oauth_client_assertion_private_key_passphrase: "{{ kafka_connect_replicator_consumer_erp_oauth_client_assertion_private_key_passphrase }}"
   32 |     oauth_client_assertion_file: "{{ kafka_connect_replicator_consumer_erp_third_party_oauth_client_assertion_config.consumer_erp }}"
   33 |     oauth_client_assertion_template_file: "{{ kafka_connect_replicator_consumer_erp_oauth_client_assertion_template_file_dest_path }}"
   34 |   # For single cluster delegating this task to broker as in case of cert based token retrival only broker can get a super user token using its certs
   35 |   # For Centralized MDS other clusters can't delegate to MDS cluster as that cluster may not have permissions to ssh into MDS, thus delegate to localhost
   36 |   when: kafka_connect_replicator_consumer_rbac_enabled or kafka_connect_replicator_oauth_enabled
   37 |   delegate_to: "{{ delegation_target }}"
   38 | 
   39 | - set_fact:
   40 |     send_client_cert: "{{ mds_ssl_client_authentication in ['required', 'requested'] }}"
   41 | 
   42 | - name: Create SSL Certificate Directory
   43 |   file:
   44 |     path: /var/ssl/private/kafka_connect_replicator_consumer
   45 |     state: directory
   46 |     mode: '755'
   47 |   tags:
   48 |     - privileged
   49 | 
   50 | - name: Check if MDS pem file exists on Ansible Controller
   51 |   stat:
   52 |     path: "{{ kafka_connect_replicator_consumer_erp_pem_file }}"
   53 |   register: replicator_pem_file
   54 |   delegate_to: localhost
   55 |   vars:
   56 |     ansible_connection: local
   57 |     ansible_become: "{{ ansible_become_localhost }}"
   58 | 
   59 | - name: Debug
   60 |   ansible.builtin.debug:
   61 |     msg: WARNING - The file {{kafka_connect_replicator_consumer_erp_pem_file}} doesn't exist on the control node
   62 |   when: not replicator_pem_file.stat.exists|bool
   63 | 
   64 | - name: Copy in MDS Public Pem File
   65 |   copy:
   66 |     src: "{{ kafka_connect_replicator_consumer_erp_pem_file }}"
   67 |     dest: "{{ kafka_connect_replicator_consumer_rbac_enabled_public_pem_path }}"
   68 |     mode: '640'
   69 |     owner: "{{kafka_connect_replicator_user}}"
   70 |     group: "{{kafka_connect_replicator_group}}"
   71 |   when: replicator_pem_file.stat.exists|bool
   72 |   diff: "{{ not mask_sensitive_diff|bool }}"
   73 | 
   74 | # The following block of URI calls sets up the permissions for replicator when cluster_id is used for the indetifier.
   75 | 
   76 | - name: Grant Confluent Replicator User Developer Read on White List Topics on Source Cluster
   77 |   uri:
   78 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperRead/bindings"
   79 |     method: POST
   80 |     validate_certs: false
   81 |     headers:
   82 |       Content-Type: application/json
   83 |       Authorization: [REDACTED_LITERAL]
   84 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
   85 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
   86 |     body_format: json
   87 |     body: >
   88 |       {
   89 |         "scope": {
   90 |           "clusters": {
   91 |             "kafka-cluster":"{{kafka_connect_replicator_consumer_kafka_cluster_id}}"
   92 |             }
   93 |         },
   94 |         "resourcePatterns": [
   95 |           {
   96 |             "resourceType":"Topic",
   97 |             "name":"{{ item }}",
   98 |             "patternType":"LITERAL"
   99 |           }
  100 |         ]
  101 |       }
  102 |     status_code: 204
  103 |   register: replicator_mds_result
  104 |   until: replicator_mds_result.status == 204
  105 |   retries: 30
  106 |   delay: 5
  107 |   no_log: "{{mask_secrets|bool}}"
  108 |   with_items: "{{ kafka_connect_replicator_white_list.split(',') }}"
  109 |   when: kafka_connect_replicator_consumer_kafka_cluster_id != "" and not ansible_check_mode
  110 | 
  111 | - name: Grant Confluent Replicator User Developer Manage on White List Topics on Source Cluster
  112 |   uri:
  113 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperManage/bindings"
  114 |     method: POST
  115 |     validate_certs: false
  116 |     headers:
  117 |       Content-Type: application/json
  118 |       Authorization: [REDACTED_LITERAL]
  119 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  120 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  121 |     body_format: json
  122 |     body: >
  123 |       {
  124 |         "scope": {
  125 |           "clusters": {
  126 |             "kafka-cluster":"{{kafka_connect_replicator_consumer_kafka_cluster_id}}"
  127 |             }
  128 |         },
  129 |         "resourcePatterns": [
  130 |           {
  131 |             "resourceType":"Topic",
  132 |             "name":"{{ item }}",
  133 |             "patternType":"LITERAL"
  134 |           }
  135 |         ]
  136 |       }
  137 |     status_code: 204
  138 |   register: replicator_mds_result
  139 |   until: replicator_mds_result.status == 204
  140 |   retries: 30
  141 |   delay: 5
  142 |   no_log: "{{mask_secrets|bool}}"
  143 |   with_items: "{{ kafka_connect_replicator_white_list.split(',') }}"
  144 |   when: kafka_connect_replicator_consumer_kafka_cluster_id != "" and not ansible_check_mode
  145 | 
  146 | - name: Grant Confluent Replicator User Developer Read on timestamp topic on Source Cluster
  147 |   uri:
  148 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperRead/bindings"
  149 |     method: POST
  150 |     validate_certs: false
  151 |     headers:
  152 |       Content-Type: application/json
  153 |       Authorization: [REDACTED_LITERAL]
  154 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  155 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  156 |     body_format: json
  157 |     body: >
  158 |       {
  159 |         "scope": {
  160 |           "clusters": {
  161 |             "kafka-cluster":"{{kafka_connect_replicator_consumer_kafka_cluster_id}}"
  162 |             }
  163 |         },
  164 |         "resourcePatterns": [
  165 |           {
  166 |             "resourceType":"Topic",
  167 |             "name":"{{kafka_connect_replicator_consumer_timestamps_topic}}",
  168 |             "patternType":"LITERAL"
  169 |           }
  170 |         ]
  171 |       }
  172 |     status_code: 204
  173 |   register: replicator_mds_result
  174 |   until: replicator_mds_result.status == 204
  175 |   retries: 30
  176 |   delay: 5
  177 |   no_log: "{{mask_secrets|bool}}"
  178 |   when: kafka_connect_replicator_consumer_kafka_cluster_id != "" and not ansible_check_mode
  179 | 
  180 | - name: Grant Confluent Replicator User Developer Manage on timestamp topic on Source Cluster
  181 |   uri:
  182 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperManage/bindings"
  183 |     method: POST
  184 |     validate_certs: false
  185 |     headers:
  186 |       Content-Type: application/json
  187 |       Authorization: [REDACTED_LITERAL]
  188 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  189 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  190 |     body_format: json
  191 |     body: >
  192 |       {
  193 |         "scope": {
  194 |           "clusters": {
  195 |             "kafka-cluster":"{{kafka_connect_replicator_consumer_kafka_cluster_id}}"
  196 |             }
  197 |         },
  198 |         "resourcePatterns": [
  199 |           {
  200 |             "resourceType":"Topic",
  201 |             "name":"{{kafka_connect_replicator_consumer_timestamps_topic}}",
  202 |             "patternType":"LITERAL"
  203 |           }
  204 |         ]
  205 |       }
  206 |     status_code: 204
  207 |   register: replicator_mds_result
  208 |   until: replicator_mds_result.status == 204
  209 |   retries: 30
  210 |   delay: 5
  211 |   no_log: "{{mask_secrets|bool}}"
  212 |   when: kafka_connect_replicator_consumer_kafka_cluster_id != "" and not ansible_check_mode
  213 | 
  214 | - name: Grant Confluent Replicator User Resource Owner on Group on Source Cluster
  215 |   uri:
  216 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/ResourceOwner/bindings"
  217 |     method: POST
  218 |     validate_certs: false
  219 |     headers:
  220 |       Content-Type: application/json
  221 |       Authorization: [REDACTED_LITERAL]
  222 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  223 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  224 |     body_format: json
  225 |     body: >
  226 |       {
  227 |         "scope": {
  228 |           "clusters": {
  229 |             "kafka-cluster":"{{kafka_connect_replicator_consumer_kafka_cluster_id}}"
  230 |             }
  231 |         },
  232 |         "resourcePatterns": [
  233 |           {
  234 |             "resourceType":"Group",
  235 |             "name":"{{ kafka_connect_replicator_cluster_id }}",
  236 |             "patternType":"PREFIXED"
  237 |           }
  238 |         ]
  239 |       }
  240 |     status_code: 204
  241 |   register: replicator_mds_result
  242 |   until: replicator_mds_result.status == 204
  243 |   retries: 30
  244 |   delay: 5
  245 |   no_log: "{{mask_secrets|bool}}"
  246 |   when: kafka_connect_replicator_consumer_kafka_cluster_id != "" and not ansible_check_mode
  247 | 
  248 | # The following block of URI calls sets up the permissions for replicator when cluster_name is used for the indetifier.
  249 | 
  250 | - name: Grant Confluent Replicator User Developer Read on White List Topics on Source Cluster
  251 |   uri:
  252 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperRead/bindings"
  253 |     method: POST
  254 |     validate_certs: false
  255 |     headers:
  256 |       Content-Type: application/json
  257 |       Authorization: [REDACTED_LITERAL]
  258 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  259 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  260 |     body_format: json
  261 |     body: >
  262 |       {
  263 |         "scope": {
  264 |           "clusterName": "{{ kafka_connect_replicator_consumer_kafka_cluster_name }}"
  265 |         },
  266 |         "resourcePatterns": [
  267 |           {
  268 |             "resourceType":"Topic",
  269 |             "name":"{{ item }}",
  270 |             "patternType":"LITERAL"
  271 |           }
  272 |         ]
  273 |       }
  274 |     status_code: 204
  275 |   register: replicator_mds_result
  276 |   until: replicator_mds_result.status == 204
  277 |   retries: 30
  278 |   delay: 5
  279 |   no_log: "{{mask_secrets|bool}}"
  280 |   with_items: "{{ kafka_connect_replicator_white_list.split(',') }}"
  281 |   when: kafka_connect_replicator_consumer_kafka_cluster_name != "" and not ansible_check_mode
  282 | 
  283 | - name: Grant Confluent Replicator User Developer Manage on White List Topics on Source Cluster
  284 |   uri:
  285 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperManage/bindings"
  286 |     method: POST
  287 |     validate_certs: false
  288 |     headers:
  289 |       Content-Type: application/json
  290 |       Authorization: [REDACTED_LITERAL]
  291 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  292 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  293 |     body_format: json
  294 |     body: >
  295 |       {
  296 |         "scope": {
  297 |           "clusterName": "{{ kafka_connect_replicator_consumer_kafka_cluster_name }}"
  298 |         },
  299 |         "resourcePatterns": [
  300 |           {
  301 |             "resourceType":"Topic",
  302 |             "name":"{{ item }}",
  303 |             "patternType":"LITERAL"
  304 |           }
  305 |         ]
  306 |       }
  307 |     status_code: 204
  308 |   register: replicator_mds_result
  309 |   until: replicator_mds_result.status == 204
  310 |   retries: 30
  311 |   delay: 5
  312 |   no_log: "{{mask_secrets|bool}}"
  313 |   with_items: "{{ kafka_connect_replicator_white_list.split(',') }}"
  314 |   when: kafka_connect_replicator_consumer_kafka_cluster_name != "" and not ansible_check_mode
  315 | 
  316 | - name: Grant Confluent Replicator User Developer Read on timestamp topic on Source Cluster
  317 |   uri:
  318 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperRead/bindings"
  319 |     method: POST
  320 |     validate_certs: false
  321 |     headers:
  322 |       Content-Type: application/json
  323 |       Authorization: [REDACTED_LITERAL]
  324 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  325 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  326 |     body_format: json
  327 |     body: >
  328 |       {
  329 |         "scope": {
  330 |           "clusterName": "{{ kafka_connect_replicator_consumer_kafka_cluster_name }}"
  331 |         },
  332 |         "resourcePatterns": [
  333 |           {
  334 |             "resourceType":"Topic",
  335 |             "name":"{{kafka_connect_replicator_consumer_timestamps_topic}}",
  336 |             "patternType":"LITERAL"
  337 |           }
  338 |         ]
  339 |       }
  340 |     status_code: 204
  341 |   register: replicator_mds_result
  342 |   until: replicator_mds_result.status == 204
  343 |   retries: 30
  344 |   delay: 5
  345 |   no_log: "{{mask_secrets|bool}}"
  346 |   when: kafka_connect_replicator_consumer_kafka_cluster_name != "" and not ansible_check_mode
  347 | 
  348 | - name: Grant Confluent Replicator User Developer Manage on timestamp topic on Source Cluster
  349 |   uri:
  350 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/DeveloperManage/bindings"
  351 |     method: POST
  352 |     validate_certs: false
  353 |     headers:
  354 |       Content-Type: application/json
  355 |       Authorization: [REDACTED_LITERAL]
  356 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  357 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  358 |     body_format: json
  359 |     body: >
  360 |       {
  361 |         "scope": {
  362 |           "clusterName": "{{ kafka_connect_replicator_consumer_kafka_cluster_name }}"
  363 |         },
  364 |         "resourcePatterns": [
  365 |           {
  366 |             "resourceType":"Topic",
  367 |             "name":"{{kafka_connect_replicator_consumer_timestamps_topic}}",
  368 |             "patternType":"LITERAL"
  369 |           }
  370 |         ]
  371 |       }
  372 |     status_code: 204
  373 |   register: replicator_mds_result
  374 |   until: replicator_mds_result.status == 204
  375 |   retries: 30
  376 |   delay: 5
  377 |   no_log: "{{mask_secrets|bool}}"
  378 |   when: kafka_connect_replicator_consumer_kafka_cluster_name != "" and not ansible_check_mode
  379 | 
  380 | - name: Grant Confluent Replicator User Resource Owner on Group on Source Cluster
  381 |   uri:
  382 |     url: "{{kafka_connect_replicator_consumer_erp_host.split(',')[0]| default('localhost:8090')}}/security/1.0/principals/User:{{replicator_consumer_user}}/roles/ResourceOwner/bindings"
  383 |     method: POST
  384 |     validate_certs: false
  385 |     headers:
  386 |       Content-Type: application/json
  387 |       Authorization: [REDACTED_LITERAL]
  388 |     client_cert: "{{ kafka_connect_replicator_consumer_cert_path if send_client_cert|bool else omit }}"
  389 |     client_key: "{{ kafka_connect_replicator_consumer_key_path if send_client_cert|bool else omit }}"
  390 |     body_format: json
  391 |     body: >
  392 |       {
  393 |         "scope": {
  394 |           "clusterName": "{{ kafka_connect_replicator_consumer_kafka_cluster_name }}"
  395 |         },
  396 |         "resourcePatterns": [
  397 |           {
  398 |             "resourceType":"Group",
  399 |             "name":"{{ kafka_connect_replicator_cluster_id }}",
  400 |             "patternType":"PREFIXED"
  401 |           }
  402 |         ]
  403 |       }
  404 |     status_code: 204
  405 |   register: replicator_mds_result
  406 |   until: replicator_mds_result.status == 204
  407 |   retries: 30
  408 |   delay: 5
  409 |   no_log: "{{mask_secrets|bool}}"
  410 |   when: kafka_connect_replicator_consumer_kafka_cluster_name != "" and not ansible_check_mode
```

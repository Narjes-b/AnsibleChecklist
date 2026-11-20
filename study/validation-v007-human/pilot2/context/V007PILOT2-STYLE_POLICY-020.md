# Frozen source context: V007PILOT2-STYLE_POLICY-020

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: style_policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/control_center_next_gen/tasks/main.yml` (reported anchor line 173)
- Flagged construct: task `create control center next gen dependencies prometheus (`web-config-prom.yml`) & alertmanager (`web-config-am.yml`) configuration`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 73–273 of 634:

```text
   73 |     name: "{{ control_center_next_gen_packages | product([confluent_control_center_next_gen_package_debian_suffix]) | map('join') | list }}"
   74 |   register: install_c3_package_result
   75 |   until: install_c3_package_result is success or ansible_check_mode
   76 |   retries: 5
   77 |   delay: 90
   78 |   when:
   79 |     - ansible_os_family == "Debian"
   80 |     - installation_method == "package"
   81 |   ignore_errors: "{{ ansible_check_mode }}"
   82 |   tags:
   83 |     - package
   84 |     - cp_package
   85 |   notify: restart control center next gen
   86 | 
   87 | - name: Create Control Center Next Gen Group
   88 |   group:
   89 |     name: "{{control_center_next_gen_group}}"
   90 |   tags:
   91 |     - privileged
   92 | 
   93 | - name: Check if Control Center Next Gen User Exists
   94 |   # Create user task must be skipped for non-linux users
   95 |   getent:
   96 |     database: passwd
   97 |     key: "{{control_center_next_gen_user}}"
   98 |   failed_when: false
   99 | 
  100 | - name: Create Control Center Next Gen User
  101 |   user:
  102 |     name: "{{control_center_next_gen_user}}"
  103 |     comment: Confluent Control Center
  104 |     system: true
  105 |     shell: "{{user_login_shell}}"
  106 |     group: "{{control_center_next_gen_group}}"
  107 |   when: (getent_passwd|default({}))[control_center_next_gen_user] is not defined
  108 |   tags:
  109 |     - privileged
  110 | 
  111 | - name: Set Control Center Next Gen Data Dir & Control Center Next Gen Dependencies (Prometheus, AlertManager)'s Config Dir permissions
  112 |   file:
  113 |     path: "{{ item }}"
  114 |     owner: "{{control_center_next_gen_user}}"
  115 |     group: "{{control_center_next_gen_group}}"
  116 |     state: directory
  117 |     mode: '750'
  118 |   loop:
  119 |     - "{{control_center_next_gen_final_properties['confluent.controlcenter.data.dir']}}"
  120 |     - "{{control_center_next_gen_dependencies_config_path}}"
  121 |   tags:
  122 |     - filesystem
  123 | 
  124 | - name: Set Control Center Next Gen Data Dir & Control Center Next Gen Dependencies (Prometheus, AlertManager)'s Config Dir file permissions
  125 |   file:
  126 |     path: "{{ item }}"
  127 |     owner: "{{control_center_next_gen_user}}"
  128 |     group: "{{control_center_next_gen_group}}"
  129 |     recurse: true
  130 |   loop:
  131 |     - "{{control_center_next_gen_final_properties['confluent.controlcenter.data.dir']}}"
  132 |   tags:
  133 |     - filesystem
  134 | 
  135 | - name: Copy Control Center Next Gen Dependencies Prometheus and AlertManager configuration files
  136 |   include_tasks: copy_dependency_configs.yml
  137 |   loop:
  138 |     - name: prometheus_generated
  139 |       src: "{{control_center_next_gen_dependency_prometheus_generated_src_config_file}}"
  140 |       dest: "{{control_center_next_gen_dep_prometheus.config_file}}"
  141 |       always_copy: false
  142 |     - name: prometheus_recording_rules
  143 |       src: "{{control_center_next_gen_dependency_recording_rules_generated_src_config_file}}"
  144 |       dest: "{{control_center_next_gen_dep_prometheus.recording_rules_config_file}}"
  145 |       always_copy: true
  146 |     - name: prometheus_trigger_rules
  147 |       src: "{{control_center_next_gen_dependency_trigger_rules_generated_src_config_file}}"
  148 |       dest: "{{control_center_next_gen_dep_prometheus.trigger_rules_config_file}}"
  149 |       always_copy: false
  150 |     - name: alertmanager_generated
  151 |       src: "{{control_center_next_gen_dependency_alertmanager_generated_src_config_file}}"
  152 |       dest: "{{control_center_next_gen_dep_alertmanager.config_file}}"
  153 |       always_copy: false
  154 |   tags:
  155 |     - configuration
  156 | 
  157 | - name: Create Control Center Next Gen Dependency Prometheus `prometheus-generated-overlay.yml` configuration
  158 |   template:
  159 |     src: prometheus_generated_overlay.yml.j2
  160 |     dest: "{{control_center_next_gen_dependency_prometheus_custom_overlay_path}}"
  161 |     mode: '640'
  162 |     owner: "{{control_center_next_gen_user}}"
  163 |     group: "{{control_center_next_gen_group}}"
  164 |   tags:
  165 |     - configuration
  166 | 
  167 | - name:  Merge Control Center Next Gen Dependency Prometheus overlay with `prometheus-generated.yml` configuration
  168 |   include_tasks: prometheus_config_overlay.yml
  169 |   when: control_center_next_gen_dependency_prometheus_custom_overlay_path is defined
  170 |   tags:
  171 |     - configuration
  172 | 
  173 | - name: Create Control Center Next Gen Dependencies Prometheus (`web-config-prom.yml`) & AlertManager (`web-config-am.yml`) configuration
  174 |   template:
  175 |     src: "{{item.template}}"
  176 |     dest: "{{item.dest}}"
  177 |     mode: '640'
  178 |     owner: "{{control_center_next_gen_user}}"
  179 |     group: "{{control_center_next_gen_group}}"
  180 |   loop:
  181 |     - template: "prometheus_web_config.yml.j2"
  182 |       dest: "{{control_center_next_gen_dep_prometheus.web_config_file}}"
  183 |     - template: "alertmanager_web_config.yml.j2"
  184 |       dest: "{{control_center_next_gen_dep_alertmanager.web_config_file}}"
  185 |   notify: restart control center next gen
  186 |   tags:
  187 |     - configuration
  188 | 
  189 | - name: Set Control Center Next Gen Data Dir & Control Center Next Gen Dependencies (Prometheus, AlertManager)'s Config Dir file permissions
  190 |   file:
  191 |     path: "{{ item }}"
  192 |     owner: "{{control_center_next_gen_user}}"
  193 |     group: "{{control_center_next_gen_group}}"
  194 |   loop:
  195 |     - "{{control_center_next_gen_dep_prometheus.config_file}}"
  196 |     - "{{control_center_next_gen_dep_prometheus.recording_rules_config_file}}"
  197 |     - "{{control_center_next_gen_dep_prometheus.trigger_rules_config_file}}"
  198 |     - "{{control_center_next_gen_dep_prometheus.web_config_file}}"
  199 |     - "{{control_center_next_gen_dep_alertmanager.config_file}}"
  200 |     - "{{control_center_next_gen_dep_alertmanager.web_config_file}}"
  201 |   tags:
  202 |     - filesystem
  203 | 
  204 | # Archive File deployments need to create SystemD service units
  205 | # Copy the tarball's systemd service to the system
  206 | - name: Copy Control Center Next Gen & its Dependencies Prometheus & AlertManager Service from archive file to system
  207 |   copy:
  208 |     src: "{{item.service_file_source}}"
  209 |     remote_src: true
  210 |     dest: "{{item.service_file_dest}}"
  211 |     mode: '640'
  212 |     force: true
  213 |   loop:
  214 |     - service_file_source: "{{confluent_control_center_next_gen_binary_base_path}}/lib/systemd/system/{{control_center_next_gen_dep_prometheus.systemd_file|basename}}"
  215 |       service_file_dest: "{{control_center_next_gen_dep_prometheus.systemd_file}}"
  216 |     - service_file_source: "{{confluent_control_center_next_gen_binary_base_path}}/lib/systemd/system/{{control_center_next_gen_dep_alertmanager.systemd_file|basename}}"
  217 |       service_file_dest: "{{control_center_next_gen_dep_alertmanager.systemd_file}}"
  218 |     - service_file_source: "{{confluent_control_center_next_gen_binary_base_path}}/lib/systemd/system/{{control_center_next_gen.systemd_file|basename}}"
  219 |       service_file_dest: "{{control_center_next_gen.systemd_file}}"
  220 |   when: installation_method == "archive"
  221 |   tags:
  222 |     - systemd
  223 | 
  224 | - name: Create Control Center Next Gen Keystore and Truststore
  225 |   include_role:
  226 |     name: ssl
  227 |   vars:
  228 |     truststore_storepass: "{{control_center_next_gen_truststore_storepass}}"
  229 |     truststore_path: "{{control_center_next_gen_truststore_path}}"
  230 |     keystore_path: "{{control_center_next_gen_keystore_path}}"
  231 |     keystore_storepass: "{{control_center_next_gen_keystore_storepass}}"
  232 |     keystore_keypass: "{{control_center_next_gen_keystore_keypass}}"
  233 |     service_name: control_center
  234 |     user: "{{control_center_next_gen_user}}"
  235 |     group: "{{control_center_next_gen_group}}"
  236 |     hostnames: "{{ [inventory_hostname, ansible_fqdn, ansible_host, ansible_ssh_host|default(omit), hostname|default(omit)] | unique }}"
  237 |     ca_cert_path: "{{control_center_next_gen_ca_cert_path}}"
  238 |     cert_path: "{{control_center_next_gen_cert_path}}"
  239 |     key_path: "{{control_center_next_gen_key_path}}"
  240 |     export_certs: "{{control_center_next_gen_export_certs}}"
  241 |   # CCloud Kafka does not need Keystores/Truststores
  242 |   when: >
  243 |     control_center_next_gen_ssl_enabled|bool or
  244 |     ( kafka_broker_listeners[control_center_next_gen_kafka_listener_name]['ssl_enabled'] | default(ssl_enabled) | bool and not public_certificates_enabled|bool ) or
  245 |     ( kafka_broker_listeners[control_center_next_gen_streams_kafka_listener_name]['ssl_enabled'] | default(ssl_enabled) | bool and not public_certificates_enabled|bool ) or
  246 |     ( mds_tls_enabled | bool and not public_certificates_enabled|bool ) or
  247 |     ( 'schema_registry' in groups and schema_registry_ssl_enabled|bool ) or
  248 |     ( 'kafka_connect' in groups and kafka_connect_ssl_enabled|bool ) or
  249 |     ( 'ksql' in groups and ksql_ssl_enabled|bool )
  250 |   tags: ssl
  251 | 
  252 | - name: Create Control Center Next Gen Dependency Prometheus Keystore and Truststore
  253 |   include_role:
  254 |     name: ssl
  255 |   vars:
  256 |     truststore_storepass: "{{control_center_next_gen_dependency_prometheus_truststore_storepass}}"
  257 |     truststore_path: "{{control_center_next_gen_dependency_prometheus_truststore_path}}"
  258 |     keystore_path: "{{control_center_next_gen_dependency_prometheus_keystore_path}}"
  259 |     keystore_storepass: "{{control_center_next_gen_dependency_prometheus_keystore_storepass}}"
  260 |     keystore_keypass: "{{control_center_next_gen_dependency_prometheus_keystore_keypass}}"
  261 |     service_name: "{{control_center_next_gen_dependency_prometheus_service_name}}"
  262 |     user: "{{control_center_next_gen_user}}"
  263 |     group: "{{control_center_next_gen_group}}"
  264 |     hostnames: "{{ [inventory_hostname, ansible_fqdn, ansible_host, ansible_ssh_host|default(omit), hostname|default(omit)] | unique }}"
  265 |     ca_cert_path: "{{control_center_next_gen_dependency_prometheus_ca_cert_path}}"
  266 |     cert_path: "{{control_center_next_gen_dependency_prometheus_cert_path}}"
  267 |     key_path: "{{control_center_next_gen_dependency_prometheus_key_path}}"
  268 |     export_certs: "true"
  269 |   when: control_center_next_gen_dependency_prometheus_ssl_enabled|bool
  270 | 
  271 | - name:  Create Control Center Next Gen Dependency Alertmanager Keystore and Truststore
  272 |   include_role:
  273 |     name: ssl
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-039

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: Maintainability/complexity
- Rule: `ansibleguard/high-coupling`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/support_bundle.yml` (reported anchor line 1)
- Object: `source_location` `bf48bf67b4af12ec238e87fa5e0f59ba4215e209c345662e4a0d664e77a31925`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–354 of 354:

```text
    1 | ---
    2 | # Support Bundle Collection Playbook
    3 | # Collects comprehensive diagnostic information from Confluent Platform deployment
    4 | # including configs, logs, system info, diagnostics, and SSL metadata
    5 | 
    6 | - name: Support Bundle Setup
    7 |   hosts: localhost
    8 |   connection: local
    9 |   gather_facts: false
   10 |   tags: always
   11 |   vars:
   12 |     ansible_become: false
   13 |   tasks:
   14 |     - name: Gather facts without become
   15 |       setup:
   16 | 
   17 |     - import_role:
   18 |         name: confluent.platform.variables
   19 | 
   20 |     - name: Generate bundle timestamp
   21 |       set_fact:
   22 |         bundle_timestamp: "{{ ansible_date_time.date | regex_replace('-','') }}_{{ ansible_date_time.time | regex_replace(':','') }}"
   23 | 
   24 |     - name: Set bundle name
   25 |       set_fact:
   26 |         bundle_name: "support_bundle_{{ bundle_timestamp }}_{{ support_bundle_cluster_name }}"
   27 |         bundle_path: "{{ (support_bundle_output_path | regex_replace('/$', '')) }}/support_bundle_{{ bundle_timestamp }}_{{ support_bundle_cluster_name }}"
   28 | 
   29 |     - name: Create bundle directory structure
   30 |       file:
   31 |         path: "{{ bundle_path }}/ansible"
   32 |         state: directory
   33 |         mode: '0755'
   34 | 
   35 |     - name: Check inventory file existence
   36 |       stat:
   37 |         path: "{{ item }}"
   38 |       loop: "{{ ansible_inventory_sources }}"
   39 |       when:
   40 |         - item is defined
   41 |         - item | length > 0
   42 |       register: inventory_file_stats
   43 |       ignore_errors: true
   44 | 
   45 |     - name: Copy inventory files to bundle
   46 |       copy:
   47 |         src: "{{ item.item }}"
   48 |         dest: "{{ bundle_path }}/ansible/inventory_{{ idx + 1 }}_raw.yml"
   49 |         mode: '0644'
   50 |       loop: "{{ inventory_file_stats.results | default([]) }}"
   51 |       loop_control:
   52 |         index_var: idx
   53 |       when:
   54 |         - item.stat is defined
   55 |         - item.stat.exists
   56 |         - item.stat.isreg
   57 |       ignore_errors: true
   58 |       register: inventory_files_copied
   59 | 
   60 |     - name: Sanitize inventory files
   61 |       include_tasks: ../roles/common/tasks/sanitize_inventory_files_local.yml
   62 | 
   63 | - name: Import all variables
   64 |   hosts: all
   65 |   tags: always
   66 |   tasks:
   67 |     - import_role:
   68 |         name: confluent.platform.variables
   69 | 
   70 |     - name: Gather Java version and memory info
   71 |       shell: |
   72 |         java -version 2>&1 | head -1 || echo "N/A"
   73 |       args:
   74 |         executable: "{{ shell_executable }}"
   75 |       register: java_version_raw
   76 |       changed_when: false
   77 |       ignore_errors: true
   78 | 
   79 |     - name: Set Java version fact
   80 |       set_fact:
   81 |         java_version_info: "{{ java_version_raw.stdout | default('N/A') }}"
   82 | 
   83 |     - name: Gather memory statistics
   84 |       shell: |
   85 |         free -m | awk 'NR==2{print $2","$3","$4","$7}'
   86 |       args:
   87 |         executable: "{{ shell_executable }}"
   88 |       register: memory_stats_raw
   89 |       changed_when: false
   90 |       ignore_errors: true
   91 | 
   92 |     - name: Set memory facts
   93 |       set_fact:
   94 |         memory_total_mb: "{{ memory_stats_raw.stdout.split(',')[0] | default(ansible_memtotal_mb) }}"
   95 |         memory_used_mb: "{{ memory_stats_raw.stdout.split(',')[1] | default('N/A') }}"
   96 |         memory_free_mb: "{{ memory_stats_raw.stdout.split(',')[2] | default('N/A') }}"
   97 |         memory_available_mb: "{{ memory_stats_raw.stdout.split(',')[3] | default('N/A') }}"
   98 |       when: memory_stats_raw is succeeded
   99 | 
  100 | - name: Zookeeper Support Bundle
  101 |   hosts: zookeeper
  102 |   gather_facts: true
  103 |   tags: zookeeper
  104 |   ignore_errors: true
  105 |   tasks:
  106 |     - include_role:
  107 |         name: confluent.platform.common
  108 |         tasks_from: collect_support_bundle.yml
  109 |       vars:
  110 |         service_name: "{{ zookeeper_service_name }}"
  111 |         component_name: "zookeeper"
  112 |         component: "{{ zookeeper }}"
  113 |         config_file: "{{ zookeeper.config_file }}"
  114 |         log_dir: "{{ zookeeper_log_dir }}"
  115 |         user: "{{ zookeeper_user }}"
  116 |         group: "{{ zookeeper_group }}"
  117 | 
  118 | - name: Kafka Controller Support Bundle
  119 |   hosts: kafka_controller
  120 |   gather_facts: true
  121 |   tags: kafka_controller_support_bundle
  122 |   ignore_errors: true
  123 |   tasks:
  124 |     - include_role:
  125 |         name: confluent.platform.common
  126 |         tasks_from: collect_support_bundle.yml
  127 |       vars:
  128 |         service_name: "{{ kafka_controller_service_name }}"
  129 |         component_name: "kafka_controller"
  130 |         component: "{{ kafka_controller }}"
  131 |         config_file: "{{ kafka_controller.config_file }}"
  132 |         log_dir: "{{ kafka_controller_log_dir }}"
  133 |         user: "{{ kafka_controller_user }}"
  134 |         group: "{{ kafka_controller_group }}"
  135 | 
  136 | - name: Kafka Broker Support Bundle
  137 |   hosts: kafka_broker
  138 |   gather_facts: true
  139 |   tags: kafka_broker_support_bundle
  140 |   ignore_errors: true
  141 |   tasks:
  142 |     - include_role:
  143 |         name: confluent.platform.common
  144 |         tasks_from: collect_support_bundle.yml
  145 |       vars:
  146 |         service_name: "{{ kafka_broker_service_name }}"
  147 |         component_name: "kafka_broker"
  148 |         component: "{{ kafka_broker }}"
  149 |         config_file: "{{ kafka_broker.config_file }}"
  150 |         log_dir: "{{ kafka_broker_log_dir }}"
  151 |         user: "{{ kafka_broker_user }}"
  152 |         group: "{{ kafka_broker_group }}"
  153 | 
  154 | - name: Schema Registry Support Bundle
  155 |   hosts: schema_registry
  156 |   gather_facts: true
  157 |   tags: schema_registry_support_bundle
  158 |   ignore_errors: true
  159 |   tasks:
  160 |     - include_role:
  161 |         name: confluent.platform.common
  162 |         tasks_from: collect_support_bundle.yml
  163 |       vars:
  164 |         service_name: "{{ schema_registry_service_name }}"
  165 |         component_name: "schema_registry"
  166 |         component: "{{ schema_registry }}"
  167 |         config_file: "{{ schema_registry.config_file }}"
  168 |         log_dir: "{{ schema_registry_log_dir }}"
  169 |         user: "{{ schema_registry_user }}"
  170 |         group: "{{ schema_registry_group }}"
  171 | 
  172 | - name: Kafka Connect Support Bundle
  173 |   hosts: kafka_connect
  174 |   gather_facts: true
  175 |   tags: kafka_connect_support_bundle
  176 |   ignore_errors: true
  177 |   tasks:
  178 |     - include_role:
  179 |         name: confluent.platform.common
  180 |         tasks_from: collect_support_bundle.yml
  181 |       vars:
  182 |         service_name: "{{ kafka_connect_service_name }}"
  183 |         component_name: "kafka_connect"
  184 |         component: "{{ kafka_connect }}"
  185 |         config_file: "{{ kafka_connect.config_file }}"
  186 |         log_dir: "{{ kafka_connect_log_dir }}"
  187 |         user: "{{ kafka_connect_user }}"
  188 |         group: "{{ kafka_connect_group }}"
  189 | 
  190 | - name: Kafka Connect Replicator Support Bundle
  191 |   hosts: kafka_connect_replicator
  192 |   gather_facts: true
  193 |   tags: kafka_connect_replicator_support_bundle
  194 |   ignore_errors: true
  195 |   tasks:
  196 |     - include_role:
  197 |         name: confluent.platform.common
  198 |         tasks_from: collect_support_bundle.yml
  199 |       vars:
  200 |         service_name: "{{ kafka_connect_replicator_service_name }}"
  201 |         component_name: "kafka_connect_replicator"
  202 |         component: "{{ kafka_connect_replicator }}"
  203 |         config_file: "{{ kafka_connect_replicator.config_file }}"
  204 |         log_dir: "{{ kafka_connect_replicator_log_dir }}"
  205 |         user: "{{ kafka_connect_replicator_user }}"
  206 |         group: "{{ kafka_connect_replicator_group }}"
  207 | 
  208 | - name: KSQL Support Bundle
  209 |   hosts: ksql
  210 |   gather_facts: true
  211 |   tags: ksql_support_bundle
  212 |   ignore_errors: true
  213 |   tasks:
  214 |     - include_role:
  215 |         name: confluent.platform.common
  216 |         tasks_from: collect_support_bundle.yml
  217 |       vars:
  218 |         service_name: "{{ ksql_service_name }}"
  219 |         component_name: "ksql"
  220 |         component: "{{ ksql }}"
  221 |         config_file: "{{ ksql.config_file }}"
  222 |         log_dir: "{{ ksql_log_dir }}"
  223 |         user: "{{ ksql_user }}"
  224 |         group: "{{ ksql_group }}"
  225 | 
  226 | - name: Kafka Rest Support Bundle
  227 |   hosts: kafka_rest
  228 |   gather_facts: true
  229 |   tags: kafka_rest_support_bundle
  230 |   ignore_errors: true
  231 |   tasks:
  232 |     - include_role:
  233 |         name: confluent.platform.common
  234 |         tasks_from: collect_support_bundle.yml
  235 |       vars:
  236 |         service_name: "{{ kafka_rest_service_name }}"
  237 |         component_name: "kafka_rest"
  238 |         component: "{{ kafka_rest }}"
  239 |         config_file: "{{ kafka_rest.config_file }}"
  240 |         log_dir: "{{ kafka_rest_log_dir }}"
  241 |         user: "{{ kafka_rest_user }}"
  242 |         group: "{{ kafka_rest_group }}"
  243 | 
  244 | - name: Control Center Support Bundle
  245 |   hosts: control_center
  246 |   gather_facts: true
  247 |   tags: control_center_support_bundle
  248 |   ignore_errors: true
  249 |   tasks:
  250 |     - include_role:
  251 |         name: confluent.platform.common
  252 |         tasks_from: collect_support_bundle.yml
  253 |       vars:
  254 |         service_name: "{{ control_center_service_name }}"
  255 |         component_name: "control_center"
  256 |         component: "{{ control_center }}"
  257 |         config_file: "{{ control_center.config_file }}"
  258 |         log_dir: "{{ control_center_log_dir }}"
  259 |         user: "{{ control_center_user }}"
  260 |         group: "{{ control_center_group }}"
  261 | 
  262 | - name: Control Center Next Gen Support Bundle
  263 |   hosts: control_center_next_gen
  264 |   gather_facts: true
  265 |   tags: control_center_next_gen_support_bundle
  266 |   ignore_errors: true
  267 |   tasks:
  268 |     - include_role:
  269 |         name: confluent.platform.common
  270 |         tasks_from: collect_support_bundle.yml
  271 |       vars:
  272 |         service_name: "{{ control_center_next_gen_service_name }}"
  273 |         component_name: "control_center_next_gen"
  274 |         component: "{{ control_center_next_gen }}"
  275 |         config_file: "{{ control_center_next_gen.config_file }}"
  276 |         log_dir: "{{ control_center_next_gen_log_dir }}"
  277 |         user: "{{ control_center_next_gen_user }}"
  278 |         group: "{{ control_center_next_gen_group }}"
  279 | 
  280 | - name: USM Agent Support Bundle
  281 |   hosts: usm_agent
  282 |   gather_facts: true
  283 |   tags: usm_agent_support_bundle
  284 |   ignore_errors: true
  285 |   tasks:
  286 |     - include_role:
  287 |         name: confluent.platform.common
  288 |         tasks_from: collect_support_bundle.yml
  289 |       vars:
  290 |         service_name: "{{ usm_agent_service_name }}"
  291 |         component_name: "usm_agent"
  292 |         component: "{{ usm_agent }}"
  293 |         config_file: "{{ usm_agent.config_file }}"
  294 |         log_dir: "{{ usm_agent.log_dir }}"
  295 |         user: "{{ usm_agent_default_user }}"
  296 |         group: "{{ usm_agent_default_group }}"
  297 | 
  298 | - name: Finalize Support Bundle
  299 |   hosts: localhost
  300 |   connection: local
  301 |   gather_facts: false
  302 |   tags: always
  303 |   vars:
  304 |     ansible_become: false
  305 |   tasks:
  306 |     - import_role:
  307 |         name: confluent.platform.variables
  308 | 
  309 |     - name: Generate bundle manifest
  310 |       template:
  311 |         src: "{{ playbook_dir }}/../roles/common/templates/bundle_manifest.yml.j2"
  312 |         dest: "{{ hostvars['localhost']['bundle_path'] }}/bundle_manifest.yml"
  313 |         mode: '0644'
  314 |       vars:
  315 |         support_bundle_component_groups: ['zookeeper', 'kafka_controller', 'kafka_broker', 'schema_registry', 'kafka_connect', 'kafka_connect_replicator', 'ksql', 'kafka_rest', 'control_center', 'control_center_next_gen', 'usm_agent']
  316 | 
  317 |     - name: Copy Ansible playbook execution log to bundle
  318 |       copy:
  319 |         src: "{{ support_bundle_ansible_log_path }}"
  320 |         dest: "{{ hostvars['localhost']['bundle_path'] }}/ansible/ansible_playbook.log"
  321 |         mode: '0644'
  322 |       when: support_bundle_ansible_log_path | length > 0
  323 |       # Collect-as-much-as-possible: never fail the bundle (see design)
  324 |       ignore_errors: true  # noqa: ignore-errors
  325 | 
  326 |     - name: Archive support bundle
  327 |       archive:
  328 |         path: "{{ hostvars['localhost']['bundle_path'] }}"
  329 |         dest: "{{ (support_bundle_output_path | regex_replace('/$', '')) }}/{{ hostvars['localhost']['bundle_name'] }}.tar.gz"
  330 |         format: gz
  331 |         mode: '0644'
  332 | 
  333 |     - name: Get archive file stats
  334 |       stat:
  335 |         path: "{{ (support_bundle_output_path | regex_replace('/$', '')) }}/{{ hostvars['localhost']['bundle_name'] }}.tar.gz"
  336 |       register: bundle_archive_stats
  337 | 
  338 |     - name: Display completion message
  339 |       debug:
  340 |         msg: |
  341 |           ========================================
  342 |           Support Bundle Created Successfully
  343 |           ========================================
  344 |           Archive: {{ (support_bundle_output_path | regex_replace('/$', '')) }}/{{ hostvars['localhost']['bundle_name'] }}.tar.gz
  345 | 
  346 |           Uncompressed Directory: {{ hostvars['localhost']['bundle_path'] }}
  347 | 
  348 |           IMPORTANT:
  349 |           - Review the uncompressed directory contents before sharing
  350 |           - Verify automatic sanitization removed all sensitive data
  351 |           - Manually redact any additional sensitive information if needed
  352 |           - Delete the uncompressed directory after review
  353 | 
  354 |           Please upload the .tar.gz file to your support ticket.
```

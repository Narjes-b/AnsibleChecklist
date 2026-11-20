# Frozen source context: V007PILOT2-STRUCTURE_REUSE-016

- Repository: `cisco-en-programmability/dnacenter-ansible`
- Commit: `33276c6275a666371b085bea241441cf4f6a29d2`
- Family: structure_reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `playbooks/tags_playbook_config_generator.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`playbooks/tags_playbook_config_generator.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–425 of 425:

```text
    1 | ---
    2 | # Example 1: Generate all configurations for all tags and tag memberships
    3 | - name: Generate complete brownfield tag configuration
    4 |   hosts: dnac_servers
    5 |   vars_files:
    6 |     - credentials.yml
    7 |   gather_facts: false
    8 |   connection: local
    9 |   tasks:
   10 |     - name: Generate all tag configurations from Cisco Catalyst Center
   11 |       cisco.dnac.tags_playbook_config_generator:
   12 |         dnac_host: "{{ dnac_host }}"
   13 |         dnac_port: "{{ dnac_port }}"
   14 |         dnac_username: "{{ dnac_username }}"
   15 |         dnac_password: "{{ dnac_password }}"
   16 |         dnac_verify: "{{ dnac_verify }}"
   17 |         dnac_debug: "{{ dnac_debug }}"
   18 |         dnac_version: "{{ dnac_version }}"
   19 |         dnac_log: true
   20 |         dnac_log_level: DEBUG
   21 |         dnac_log_append: false
   22 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
   23 |         state: gathered
   24 |         # No config provided - generates all configurations
   25 | 
   26 | # Example 2: Generate all configurations with custom file path
   27 | - name: Generate complete brownfield tag configuration with custom filename
   28 |   hosts: dnac_servers
   29 |   vars_files:
   30 |     - credentials.yml
   31 |   gather_facts: false
   32 |   connection: local
   33 |   tasks:
   34 |     - name: Generate all tag configurations to a specific file
   35 |       cisco.dnac.tags_playbook_config_generator:
   36 |         dnac_host: "{{ dnac_host }}"
   37 |         dnac_port: "{{ dnac_port }}"
   38 |         dnac_username: "{{ dnac_username }}"
   39 |         dnac_password: "{{ dnac_password }}"
   40 |         dnac_verify: "{{ dnac_verify }}"
   41 |         dnac_debug: "{{ dnac_debug }}"
   42 |         dnac_version: "{{ dnac_version }}"
   43 |         dnac_log: true
   44 |         dnac_log_level: DEBUG
   45 |         dnac_log_append: false
   46 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
   47 |         state: gathered
   48 |         file_path: "/tmp/complete_tags_config.yaml"
   49 |         file_mode: "overwrite"
   50 |         # No config provided - generates all configurations
   51 | 
   52 | # Example 3: Generate only tag configurations without memberships
   53 | - name: Generate tag definitions only
   54 |   hosts: dnac_servers
   55 |   vars_files:
   56 |     - credentials.yml
   57 |   gather_facts: false
   58 |   connection: local
   59 |   tasks:
   60 |     - name: Export all tag definitions to YAML file
   61 |       cisco.dnac.tags_playbook_config_generator:
   62 |         dnac_host: "{{ dnac_host }}"
   63 |         dnac_port: "{{ dnac_port }}"
   64 |         dnac_username: "{{ dnac_username }}"
   65 |         dnac_password: "{{ dnac_password }}"
   66 |         dnac_verify: "{{ dnac_verify }}"
   67 |         dnac_debug: "{{ dnac_debug }}"
   68 |         dnac_version: "{{ dnac_version }}"
   69 |         dnac_log: true
   70 |         dnac_log_level: DEBUG
   71 |         dnac_log_append: false
   72 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
   73 |         state: gathered
   74 |         file_path: "/tmp/catc_tags.yaml"
   75 |         file_mode: "overwrite"
   76 |         config:
   77 |           component_specific_filters:
   78 |             components_list: ["tags"]
   79 | 
   80 | # Example 4: Generate only tag membership configurations
   81 | - name: Generate tag memberships only
   82 |   hosts: dnac_servers
   83 |   vars_files:
   84 |     - credentials.yml
   85 |   gather_facts: false
   86 |   connection: local
   87 |   tasks:
   88 |     - name: Export all tag memberships to YAML file
   89 |       cisco.dnac.tags_playbook_config_generator:
   90 |         dnac_host: "{{ dnac_host }}"
   91 |         dnac_port: "{{ dnac_port }}"
   92 |         dnac_username: "{{ dnac_username }}"
   93 |         dnac_password: "{{ dnac_password }}"
   94 |         dnac_verify: "{{ dnac_verify }}"
   95 |         dnac_debug: "{{ dnac_debug }}"
   96 |         dnac_version: "{{ dnac_version }}"
   97 |         dnac_log: true
   98 |         dnac_log_level: DEBUG
   99 |         dnac_log_append: false
  100 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  101 |         state: gathered
  102 |         file_path: "/tmp/catc_tags.yaml"
  103 |         file_mode: "overwrite"
  104 |         config:
  105 |           component_specific_filters:
  106 |             components_list: ["tag_memberships"]
  107 | 
  108 | # Example 5: Generate both tags and memberships together
  109 | - name: Generate tags and their memberships
  110 |   hosts: dnac_servers
  111 |   vars_files:
  112 |     - credentials.yml
  113 |   gather_facts: false
  114 |   connection: local
  115 |   tasks:
  116 |     - name: Export tags and tag memberships to YAML file
  117 |       cisco.dnac.tags_playbook_config_generator:
  118 |         dnac_host: "{{ dnac_host }}"
  119 |         dnac_port: "{{ dnac_port }}"
  120 |         dnac_username: "{{ dnac_username }}"
  121 |         dnac_password: "{{ dnac_password }}"
  122 |         dnac_verify: "{{ dnac_verify }}"
  123 |         dnac_debug: "{{ dnac_debug }}"
  124 |         dnac_version: "{{ dnac_version }}"
  125 |         dnac_log: true
  126 |         dnac_log_level: DEBUG
  127 |         dnac_log_append: false
  128 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  129 |         state: gathered
  130 |         file_path: "/tmp/catc_tags.yaml"
  131 |         file_mode: "overwrite"
  132 |         config:
  133 |           component_specific_filters:
  134 |             components_list: ["tags", "tag_memberships"]
  135 | 
  136 | # Example 6: Auto-populate components_list from component filters
  137 | - name: Generate configuration with auto-populated components_list
  138 |   hosts: dnac_servers
  139 |   vars_files:
  140 |     - credentials.yml
  141 |   gather_facts: false
  142 |   connection: local
  143 |   tasks:
  144 |     - name: Export tags by providing filters without explicit components_list
  145 |       cisco.dnac.tags_playbook_config_generator:
  146 |         dnac_host: "{{ dnac_host }}"
  147 |         dnac_port: "{{ dnac_port }}"
  148 |         dnac_username: "{{ dnac_username }}"
  149 |         dnac_password: "{{ dnac_password }}"
  150 |         dnac_verify: "{{ dnac_verify }}"
  151 |         dnac_debug: "{{ dnac_debug }}"
  152 |         dnac_version: "{{ dnac_version }}"
  153 |         dnac_log: true
  154 |         dnac_log_level: DEBUG
  155 |         dnac_log_append: false
  156 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  157 |         state: gathered
  158 |         file_path: "/tmp/catc_tags.yaml"
  159 |         file_mode: "overwrite"
  160 |         config:
  161 |           component_specific_filters:
  162 |             # No components_list specified, but tags filters are provided
  163 |             # The 'tags' component will be automatically added to components_list
  164 |             tags:
  165 |               - tag_name: Production
  166 |               - tag_name: Data-Center
  167 |       # This will automatically include 'tags' in components_list and retrieve only those tags
  168 | 
  169 | # Example 7: Filter specific tags by name
  170 | - name: Generate configuration for specific tags by name
  171 |   hosts: dnac_servers
  172 |   vars_files:
  173 |     - credentials.yml
  174 |   gather_facts: false
  175 |   connection: local
  176 |   tasks:
  177 |     - name: Export specific tags to YAML file
  178 |       cisco.dnac.tags_playbook_config_generator:
  179 |         dnac_host: "{{ dnac_host }}"
  180 |         dnac_port: "{{ dnac_port }}"
  181 |         dnac_username: "{{ dnac_username }}"
  182 |         dnac_password: "{{ dnac_password }}"
  183 |         dnac_verify: "{{ dnac_verify }}"
  184 |         dnac_debug: "{{ dnac_debug }}"
  185 |         dnac_version: "{{ dnac_version }}"
  186 |         dnac_log: true
  187 |         dnac_log_level: DEBUG
  188 |         dnac_log_append: false
  189 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  190 |         state: gathered
  191 |         file_path: "/tmp/catc_tags.yaml"
  192 |         file_mode: "overwrite"
  193 |         config:
  194 |           component_specific_filters:
  195 |             components_list: ["tags", "tag_memberships"]
  196 |             tags:
  197 |               - tag_name: Production
  198 |               - tag_name: Data-Center
  199 | 
  200 | # Example 8: Filter specific tag memberships by tag name
  201 | - name: Generate memberships for specific tags
  202 |   hosts: dnac_servers
  203 |   vars_files:
  204 |     - credentials.yml
  205 |   gather_facts: false
  206 |   connection: local
  207 |   tasks:
  208 |     - name: Export memberships for specific tags
  209 |       cisco.dnac.tags_playbook_config_generator:
  210 |         dnac_host: "{{ dnac_host }}"
  211 |         dnac_port: "{{ dnac_port }}"
  212 |         dnac_username: "{{ dnac_username }}"
  213 |         dnac_password: "{{ dnac_password }}"
  214 |         dnac_verify: "{{ dnac_verify }}"
  215 |         dnac_debug: "{{ dnac_debug }}"
  216 |         dnac_version: "{{ dnac_version }}"
  217 |         dnac_log: true
  218 |         dnac_log_level: DEBUG
  219 |         dnac_log_append: false
  220 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  221 |         state: gathered
  222 |         file_path: "/tmp/catc_tags.yaml"
  223 |         file_mode: "overwrite"
  224 |         config:
  225 |           component_specific_filters:
  226 |             components_list: ["tags", "tag_memberships"]
  227 |             tag_memberships:
  228 |               - tag_name: Campus-Switches
  229 |               - tag_name: Core-Routers
  230 | 
  231 | # Example 9: Generate tag configuration with append mode
  232 | - name: Generate and append tag configuration
  233 |   hosts: dnac_servers
  234 |   vars_files:
  235 |     - credentials.yml
  236 |   gather_facts: false
  237 |   connection: local
  238 |   tasks:
  239 |     - name: Append tag configurations to existing file
  240 |       cisco.dnac.tags_playbook_config_generator:
  241 |         dnac_host: "{{ dnac_host }}"
  242 |         dnac_port: "{{ dnac_port }}"
  243 |         dnac_username: "{{ dnac_username }}"
  244 |         dnac_password: "{{ dnac_password }}"
  245 |         dnac_verify: "{{ dnac_verify }}"
  246 |         dnac_debug: "{{ dnac_debug }}"
  247 |         dnac_version: "{{ dnac_version }}"
  248 |         dnac_log: true
  249 |         dnac_log_level: DEBUG
  250 |         dnac_log_append: false
  251 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  252 |         state: gathered
  253 |         file_path: "/tmp/all_tags.yaml"
  254 |         file_mode: "append"
  255 |         config:
  256 |           component_specific_filters:
  257 |             components_list: ["tags", "tag_memberships"]
  258 |             tags:
  259 |               - tag_name: Branch-Office
  260 |               - tag_name: Access-Points
  261 | 
  262 | # Example 10: Retrieve all tag memberships with hostname as device identifier
  263 | - name: Generate all tag memberships using hostname identifier
  264 |   hosts: dnac_servers
  265 |   vars_files:
  266 |     - credentials.yml
  267 |   gather_facts: false
  268 |   connection: local
  269 |   tasks:
  270 |     - name: Export all tag memberships with hostnames
  271 |       cisco.dnac.tags_playbook_config_generator:
  272 |         dnac_host: "{{ dnac_host }}"
  273 |         dnac_port: "{{ dnac_port }}"
  274 |         dnac_username: "{{ dnac_username }}"
  275 |         dnac_password: "{{ dnac_password }}"
  276 |         dnac_verify: "{{ dnac_verify }}"
  277 |         dnac_debug: "{{ dnac_debug }}"
  278 |         dnac_version: "{{ dnac_version }}"
  279 |         dnac_log: true
  280 |         dnac_log_level: DEBUG
  281 |         dnac_log_append: false
  282 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  283 |         state: gathered
  284 |         file_path: "/tmp/tags_by_hostname.yaml"
  285 |         file_mode: "overwrite"
  286 |         config:
  287 |           component_specific_filters:
  288 |             components_list: ["tag_memberships"]
  289 |             tag_memberships:
  290 |               - device_identifier: hostname
  291 |       # This will retrieve all tags with their members identified by hostname instead of serial_number
  292 | 
  293 | # Example 11: Retrieve specific tag membership with IP address as device identifier
  294 | - name: Generate specific tag membership using IP address identifier
  295 |   hosts: dnac_servers
  296 |   vars_files:
  297 |     - credentials.yml
  298 |   gather_facts: false
  299 |   connection: local
  300 |   tasks:
  301 |     - name: Export specific tag membership with IP addresses
  302 |       cisco.dnac.tags_playbook_config_generator:
  303 |         dnac_host: "{{ dnac_host }}"
  304 |         dnac_port: "{{ dnac_port }}"
  305 |         dnac_username: "{{ dnac_username }}"
  306 |         dnac_password: "{{ dnac_password }}"
  307 |         dnac_verify: "{{ dnac_verify }}"
  308 |         dnac_debug: "{{ dnac_debug }}"
  309 |         dnac_version: "{{ dnac_version }}"
  310 |         dnac_log: true
  311 |         dnac_log_level: DEBUG
  312 |         dnac_log_append: false
  313 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  314 |         state: gathered
  315 |         file_path: "/tmp/production_tag_by_ip.yaml"
  316 |         file_mode: "overwrite"
  317 |         config:
  318 |           component_specific_filters:
  319 |             components_list: ["tag_memberships"]
  320 |             tag_memberships:
  321 |               - tag_name: Production
  322 |                 device_identifier: ip_address
  323 |       # This will retrieve only the 'Production' tag's members with IP addresses
  324 | 
  325 | # Example 12: Retrieve tag memberships with MAC address as device identifier
  326 | - name: Generate tag memberships using MAC address identifier
  327 |   hosts: dnac_servers
  328 |   vars_files:
  329 |     - credentials.yml
  330 |   gather_facts: false
  331 |   connection: local
  332 |   tasks:
  333 |     - name: Export tag memberships with MAC addresses
  334 |       cisco.dnac.tags_playbook_config_generator:
  335 |         dnac_host: "{{ dnac_host }}"
  336 |         dnac_port: "{{ dnac_port }}"
  337 |         dnac_username: "{{ dnac_username }}"
  338 |         dnac_password: "{{ dnac_password }}"
  339 |         dnac_verify: "{{ dnac_verify }}"
  340 |         dnac_debug: "{{ dnac_debug }}"
  341 |         dnac_version: "{{ dnac_version }}"
  342 |         dnac_log: true
  343 |         dnac_log_level: DEBUG
  344 |         dnac_log_append: false
  345 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  346 |         state: gathered
  347 |         file_path: "/tmp/tags_by_mac.yaml"
  348 |         file_mode: "overwrite"
  349 |         config:
  350 |           component_specific_filters:
  351 |             components_list: ["tag_memberships"]
  352 |             tag_memberships:
  353 |               - tag_name: Campus-Switches
  354 |                 device_identifier: mac_address
  355 |               - tag_name: Core-Routers
  356 |                 device_identifier: mac_address
  357 |       # This will retrieve specific tags' members with MAC addresses
  358 | 
  359 | # Example 13: Retrieve tag memberships with default device identifier (serial_number)
  360 | - name: Generate tag memberships with default serial number identifier
  361 |   hosts: dnac_servers
  362 |   vars_files:
  363 |     - credentials.yml
  364 |   gather_facts: false
  365 |   connection: local
  366 |   tasks:
  367 |     - name: Export tag memberships with serial numbers (default)
  368 |       cisco.dnac.tags_playbook_config_generator:
  369 |         dnac_host: "{{ dnac_host }}"
  370 |         dnac_port: "{{ dnac_port }}"
  371 |         dnac_username: "{{ dnac_username }}"
  372 |         dnac_password: "{{ dnac_password }}"
  373 |         dnac_verify: "{{ dnac_verify }}"
  374 |         dnac_debug: "{{ dnac_debug }}"
  375 |         dnac_version: "{{ dnac_version }}"
  376 |         dnac_log: true
  377 |         dnac_log_level: DEBUG
  378 |         dnac_log_append: false
  379 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  380 |         state: gathered
  381 |         file_path: "/tmp/tags_by_serial.yaml"
  382 |         file_mode: "overwrite"
  383 |         config:
  384 |           component_specific_filters:
  385 |             components_list: ["tag_memberships"]
  386 |             tag_memberships:
  387 |               - tag_name: Data-Center
  388 |       # When device_identifier is not specified, it defaults to 'serial_number'
  389 | 
  390 | # Example 14: Mixed configuration with different device identifiers
  391 | - name: Generate tag configurations with mixed device identifiers
  392 |   hosts: dnac_servers
  393 |   vars_files:
  394 |     - credentials.yml
  395 |   gather_facts: false
  396 |   connection: local
  397 |   tasks:
  398 |     - name: Export tags with various device identifier formats
  399 |       cisco.dnac.tags_playbook_config_generator:
  400 |         dnac_host: "{{ dnac_host }}"
  401 |         dnac_port: "{{ dnac_port }}"
  402 |         dnac_username: "{{ dnac_username }}"
  403 |         dnac_password: "{{ dnac_password }}"
  404 |         dnac_verify: "{{ dnac_verify }}"
  405 |         dnac_debug: "{{ dnac_debug }}"
  406 |         dnac_version: "{{ dnac_version }}"
  407 |         dnac_log: true
  408 |         dnac_log_level: DEBUG
  409 |         dnac_log_append: false
  410 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  411 |         state: gathered
  412 |         file_path: "/tmp/mixed_identifiers.yaml"
  413 |         file_mode: "overwrite"
  414 |         config:
  415 |           component_specific_filters:
  416 |             components_list: ["tag_memberships"]
  417 |             tag_memberships:
  418 |               - tag_name: Production
  419 |                 device_identifier: hostname
  420 |               - tag_name: Development
  421 |                 device_identifier: ip_address
  422 |               - tag_name: Testing
  423 |                 device_identifier: mac_address
  424 |               - tag_name: Staging
  425 |       # Different tags can use different device identifiers in the same configuration
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `.`; 2679 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

Listing exceeds 400: paths beside the cited file, then a per-directory count of ALL paths.
playbooks/PnP.yml
playbooks/accesspoint_location_playbook_config_generator.yml
playbooks/accesspoint_location_workflow_manager.yml
playbooks/accesspoint_playbook_config_generator.yml
playbooks/accesspoint_workflow_manager.yml
playbooks/application_policy_playbook_config_generator.yml
playbooks/application_policy_workflow_manager.yml
playbooks/application_set_info.yml
playbooks/application_sets.yml
playbooks/applications.yml
playbooks/assurance_device_health_score_settings_playbook_config_generator.yml
playbooks/assurance_device_health_score_settings_workflow_manager.yml
playbooks/assurance_icap_settings_workflow_manager.yml
playbooks/assurance_issue_playbook_config_generator.yml
playbooks/assurance_issue_workflow_manager.yml
playbooks/authentication_import.yml
playbooks/backup_and_restore_playbook_config_generator.yml
playbooks/backup_and_restore_workflow_manager.yml
playbooks/command_runner_run_command.yml
playbooks/configs_backup.yml
playbooks/configuration_template_version_create.yml
playbooks/device_configs_backup_workflow_manager.yml
playbooks/device_credential_intent.yml
playbooks/device_credential_playbook_config_generator.yml
playbooks/device_credential_workflow_manager.yml
playbooks/device_details.template
playbooks/device_provision.yml
playbooks/device_provision_workflow.yml
playbooks/discovery.yml
playbooks/discovery_intent.yml
playbooks/discovery_playbook_config_generator.yml
playbooks/discovery_workflow_manager.yml
playbooks/download_device_cmd_runner_output.yml
playbooks/event_webhook_create.yml
playbooks/events_and_notifications_playbook_config_generator.yml
playbooks/events_and_notifications_workflow_manager.yml
playbooks/fabric_devices_info_workflow_manager.yml
playbooks/files/test.template
playbooks/get_tag_members_by_id.yml
playbooks/global_credentials.yml
playbooks/global_credentials_info.yml
playbooks/global_pool.yml
playbooks/hosts
playbooks/import_image_file.yml
playbooks/inventory_device.yml
playbooks/inventory_playbook_config_generator.yml
playbooks/inventory_workflow_manager.yml
playbooks/ise_radius_integration_playbook_config_generator.yml
playbooks/ise_radius_integration_workflow_manager.yml
playbooks/lan_automation_workflow_manager.yml
playbooks/network_compliance_workflow_manager.yml
playbooks/network_device_custom_prompt_info.yml
playbooks/network_device_info.yml
playbooks/network_device_update_role.yml
playbooks/network_devices_info_workflow_manager.yml
playbooks/network_profile_switching_playbook_config_generator.yml
playbooks/network_profile_switching_workflow_manager.yml
playbooks/network_profile_wireless_playbook_config_generator.yml
playbooks/network_profile_wireless_workflow_manager.yml
playbooks/network_settings_intent.yml
playbooks/network_settings_playbook_config_generator.yml
playbooks/network_settings_workflow_manager.yml
playbooks/path_trace_workflow_manager.yml
playbooks/pnp_device.yml
playbooks/pnp_playbook_config_generator.yml
playbooks/pnp_workflow_manager.yml
playbooks/provision_playbook_config_generator.yml
playbooks/provision_workflow_manager.yml
playbooks/reports_executions_info.yml
playbooks/reports_workflow_manager.yml
playbooks/reserve_ip_subpool.yml
playbooks/rma_playbook_config_generator.yml
playbooks/rma_workflow_manager.yml
playbooks/sda_anycast_gateways.yml
playbooks/sda_extranet_policies_playbook_config_generator.yml
playbooks/sda_extranet_policies_workflow_manager.yml
playbooks/sda_fabric.yml
playbooks/sda_fabric_devices_playbook_config_generator.yaml
playbooks/sda_fabric_devices_workflow_manager.yml
playbooks/sda_fabric_multicast_playbook_config_generator.yml
playbooks/sda_fabric_multicast_workflow_manager.yml
playbooks/sda_fabric_site.yml
playbooks/sda_fabric_sites_zones_playbook_config_generator.yml
playbooks/sda_fabric_sites_zones_workflow_manager.yml
playbooks/sda_fabric_transits_playbook_config_generator.yml
playbooks/sda_fabric_transits_workflow_manager.yml
playbooks/sda_fabric_virtual_networks_playbook_config_generator.yml
playbooks/sda_fabric_virtual_networks_workflow_manager.yml
playbooks/sda_host_port_onboarding_playbook_config_generator.yml
playbooks/sda_host_port_onboarding_workflow_manager.yml
playbooks/sda_layer3_virtual_networks.yml
playbooks/sda_virtual_network_v2.yml
playbooks/site_intent.yml
playbooks/site_playbook_config_generator.yml
playbooks/site_workflow_manager.yml
playbooks/swim_import_local.yml
playbooks/swim_intent.yml
playbooks/swim_workflow_manager.yml
playbooks/tag.yml
playbooks/tags_playbook_config_generator.yml
playbooks/tags_workflow_manager.yml
playbooks/template.yml
playbooks/template_playbook_config_generator.yml
playbooks/template_pnp_intent.yml
playbooks/template_workflow_manager.yml
playbooks/tests/test-1592357065255.csv
playbooks/user_info.yml
playbooks/user_role_playbook_config_generator.yml
playbooks/user_role_workflow_manager.yml
playbooks/vars/credentials.template
playbooks/vars/image_details.yml
playbooks/vars/input_events_and_notification.yml
playbooks/wired_campus_automation_playbook_config_generator.yml
playbooks/wired_campus_automation_workflow_manager.yml
playbooks/wireless_design_playbook_config_generator.yml
playbooks/wireless_design_workflow_manager.yml
playbooks/wireless_enterprise_ssid.yml

Per-directory path counts:
.: 13
.circleci: 1
.github: 1
.github/ISSUE_TEMPLATE: 3
.github/workflows: 8
changelogs: 1
docs: 4
docs/_gh_include: 2
meta: 1
playbooks: 112
playbooks/files: 1
playbooks/tests: 1
playbooks/vars: 3
plugins: 2
plugins/action: 1052
plugins/doc_fragments: 5
plugins/module_utils: 6
plugins/modules: 1137
plugins/plugin_utils: 3
tests/integration/ccc_aaa_server_management/defaults: 1
tests/integration/ccc_aaa_server_management/meta: 1
tests/integration/ccc_aaa_server_management/tasks: 1
tests/integration/ccc_aaa_server_management/tests: 2
tests/integration/ccc_aaa_server_management/vars: 2
tests/integration/ccc_accesspoint_location_workflow_management/defaults: 1
tests/integration/ccc_accesspoint_location_workflow_management/meta: 1
tests/integration/ccc_accesspoint_location_workflow_management/tasks: 1
tests/integration/ccc_accesspoint_location_workflow_management/tests: 1
tests/integration/ccc_accesspoint_location_workflow_management/vars: 1
tests/integration/ccc_accesspoint_workflow_management/defaults: 1
tests/integration/ccc_accesspoint_workflow_management/meta: 1
tests/integration/ccc_accesspoint_workflow_management/tasks: 1
tests/integration/ccc_accesspoint_workflow_management/tests: 1
tests/integration/ccc_accesspoint_workflow_management/vars: 1
tests/integration/ccc_application_policy_workflow_manager/defaults: 1
tests/integration/ccc_application_policy_workflow_manager/meta: 1
tests/integration/ccc_application_policy_workflow_manager/tasks: 1
tests/integration/ccc_application_policy_workflow_manager/tests: 1
tests/integration/ccc_application_policy_workflow_manager/vars: 1
tests/integration/ccc_assurance_device_health_score_settings_management/defaults: 1
tests/integration/ccc_assurance_device_health_score_settings_management/meta: 1
tests/integration/ccc_assurance_device_health_score_settings_management/tasks: 1
tests/integration/ccc_assurance_device_health_score_settings_management/tests: 1
tests/integration/ccc_assurance_device_health_score_settings_management/vars: 1
tests/integration/ccc_assurance_icap_settings_management/defaults: 1
tests/integration/ccc_assurance_icap_settings_management/meta: 1
tests/integration/ccc_assurance_icap_settings_management/tasks: 1
tests/integration/ccc_assurance_icap_settings_management/tests: 1
tests/integration/ccc_assurance_icap_settings_management/vars: 1
tests/integration/ccc_assurance_issue_management/defaults: 1
tests/integration/ccc_assurance_issue_management/meta: 1
tests/integration/ccc_assurance_issue_management/tasks: 1
tests/integration/ccc_assurance_issue_management/tests: 1
tests/integration/ccc_assurance_issue_management/vars: 1
tests/integration/ccc_backup_and_restore_workflow_manager/defaults: 1
tests/integration/ccc_backup_and_restore_workflow_manager/meta: 1
tests/integration/ccc_backup_and_restore_workflow_manager/tasks: 1
tests/integration/ccc_backup_and_restore_workflow_manager/tests: 1
tests/integration/ccc_backup_and_restore_workflow_manager/vars: 1
tests/integration/ccc_device_configs_backup_management/defaults: 1
tests/integration/ccc_device_configs_backup_management/meta: 1
tests/integration/ccc_device_configs_backup_management/tasks: 1
tests/integration/ccc_device_configs_backup_management/tests: 1
tests/integration/ccc_device_configs_backup_management/vars: 1
tests/integration/ccc_device_credential_management/defaults: 1
tests/integration/ccc_device_credential_management/meta: 1
tests/integration/ccc_device_credential_management/tasks: 1
tests/integration/ccc_device_credential_management/tests: 2
tests/integration/ccc_device_credential_management/vars: 2
tests/integration/ccc_discovery_management/defaults: 1
tests/integration/ccc_discovery_management/meta: 1
tests/integration/ccc_discovery_management/tasks: 1
tests/integration/ccc_discovery_management/tests: 1
tests/integration/ccc_discovery_management/vars: 2
tests/integration/ccc_fabric_devices_info_workflow_manager/defaults: 1
tests/integration/ccc_fabric_devices_info_workflow_manager/meta: 1
tests/integration/ccc_fabric_devices_info_workflow_manager/tasks: 1
tests/integration/ccc_fabric_devices_info_workflow_manager/tests: 1
tests/integration/ccc_fabric_devices_info_workflow_manager/vars: 1
tests/integration/ccc_inventory_management/defaults: 1
tests/integration/ccc_inventory_management/meta: 1
tests/integration/ccc_inventory_management/tasks: 1
tests/integration/ccc_inventory_management/tests: 1
tests/integration/ccc_inventory_management/vars: 1
tests/integration/ccc_network_compliance_management/defaults: 1
tests/integration/ccc_network_compliance_management/meta: 1
tests/integration/ccc_network_compliance_management/tasks: 1
tests/integration/ccc_network_compliance_management/tests: 1
tests/integration/ccc_network_compliance_management/vars: 1
tests/integration/ccc_network_devices_info_workflow_manager/defaults: 1
tests/integration/ccc_network_devices_info_workflow_manager/meta: 1
tests/integration/ccc_network_devices_info_workflow_manager/tasks: 1
tests/integration/ccc_network_devices_info_workflow_manager/tests: 1
tests/integration/ccc_network_devices_info_workflow_manager/vars: 1
tests/integration/ccc_network_profile_switching_workflow_management/defaults: 1
tests/integration/ccc_network_profile_switching_workflow_management/meta: 1
tests/integration/ccc_network_profile_switching_workflow_management/tasks: 1
tests/integration/ccc_network_profile_switching_workflow_management/tests: 1
tests/integration/ccc_network_profile_switching_workflow_management/vars: 1
tests/integration/ccc_network_profile_wireless_workflow_management/defaults: 1
tests/integration/ccc_network_profile_wireless_workflow_management/meta: 1
tests/integration/ccc_network_profile_wireless_workflow_management/tasks: 1
tests/integration/ccc_network_profile_wireless_workflow_management/tests: 1
tests/integration/ccc_network_profile_wireless_workflow_management/vars: 1
tests/integration/ccc_network_settings_management/defaults: 1
tests/integration/ccc_network_settings_management/meta: 1
tests/integration/ccc_network_settings_management/tasks: 1
tests/integration/ccc_network_settings_management/tests: 1
tests/integration/ccc_network_settings_management/vars: 1
tests/integration/ccc_path_trace_workflow_manager/defaults: 1
tests/integration/ccc_path_trace_workflow_manager/meta: 1
tests/integration/ccc_path_trace_workflow_manager/tasks: 1
tests/integration/ccc_path_trace_workflow_manager/tests: 1
tests/integration/ccc_path_trace_workflow_manager/vars: 1
tests/integration/ccc_pnp_management/defaults: 1
tests/integration/ccc_pnp_management/meta: 1
tests/integration/ccc_pnp_management/tasks: 1
tests/integration/ccc_pnp_management/tests: 1
tests/integration/ccc_pnp_management/vars: 1
tests/integration/ccc_reports_workflow_management/defaults: 1
tests/integration/ccc_reports_workflow_management/meta: 1
tests/integration/ccc_reports_workflow_management/tasks: 1
tests/integration/ccc_reports_workflow_management/tests: 1
tests/integration/ccc_reports_workflow_management/vars: 1
tests/integration/ccc_sda_fabric_devices_workflow_management/defaults: 1
tests/integration/ccc_sda_fabric_devices_workflow_management/meta: 1
tests/integration/ccc_sda_fabric_devices_workflow_management/tasks: 1
tests/integration/ccc_sda_fabric_devices_workflow_management/tests: 1
tests/integration/ccc_sda_fabric_devices_workflow_management/vars: 1
tests/integration/ccc_site_management/defaults: 1
tests/integration/ccc_site_management/meta: 1
tests/integration/ccc_site_management/tasks: 1
tests/integration/ccc_site_management/tests: 1
tests/integration/ccc_site_management/vars: 1
tests/integration/ccc_site_workflow_manager/defaults: 1
tests/integration/ccc_site_workflow_manager/meta: 1
tests/integration/ccc_site_workflow_manager/tasks: 1
tests/integration/ccc_site_workflow_manager/tests: 1
tests/integration/ccc_site_workflow_manager/vars: 1
tests/integration/ccc_swim_management/defaults: 1
tests/integration/ccc_swim_management/meta: 1
tests/integration/ccc_swim_management/tasks: 1
tests/integration/ccc_swim_management/tests: 1
tests/integration/ccc_swim_management/vars: 1
tests/integration/ccc_tags_workflow_management/defaults: 1
tests/integration/ccc_tags_workflow_management/meta: 1
tests/integration/ccc_tags_workflow_management/tasks: 1
tests/integration/ccc_tags_workflow_management/tests: 1
tests/integration/ccc_tags_workflow_management/vars: 1
tests/integration/ccc_template_management/defaults: 1
tests/integration/ccc_template_management/meta: 1
tests/integration/ccc_template_management/tasks: 1
tests/integration/ccc_template_management/tests: 4
tests/integration/ccc_template_management/vars: 3
tests/integration/ccc_user_role_workflow_manager/defaults: 1
tests/integration/ccc_user_role_workflow_manager/meta: 1
tests/integration/ccc_user_role_workflow_manager/tasks: 1
tests/integration/ccc_user_role_workflow_manager/tests: 1
tests/integration/ccc_user_role_workflow_manager/vars: 1
tests/integration/ccc_wired_campus_automation_management/defaults: 1
tests/integration/ccc_wired_campus_automation_management/meta: 1
tests/integration/ccc_wired_campus_automation_management/tasks: 1
tests/integration/ccc_wired_campus_automation_management/tests: 12
tests/integration/ccc_wired_campus_automation_management/vars: 12
tests/integration/ccc_wireless_design_management/defaults: 1
tests/integration/ccc_wireless_design_management/meta: 1
tests/integration/ccc_wireless_design_management/tasks: 1
tests/integration/ccc_wireless_design_management/tests: 1
tests/integration/ccc_wireless_design_management/vars: 1
tests/unit/modules/dnac: 71
tests/unit/modules/dnac/fixtures: 70
```

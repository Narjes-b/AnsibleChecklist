# Frozen source context: V007PILOT-STRUCTURE_REUSE-038

- Repository: `cisco-en-programmability/dnacenter-ansible`
- Commit: `33276c6275a666371b085bea241441cf4f6a29d2`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `playbooks/sda_fabric_devices_playbook_config_generator.yaml` (reported anchor line 1)
- Object: `source_location` `957f6589b808036ba635f5ddde81ce759714e8599a0ee5e0788f008605bfcc0d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–221 of 221:

```text
    1 | ---
    2 | # ============================================================================
    3 | # SDA Fabric Devices Playbook Config Generator Examples
    4 | # ============================================================================
    5 | # This playbook demonstrates various ways to generate YAML configurations
    6 | # for SDA fabric devices from an existing Cisco Catalyst Center deployment.
    7 | #
    8 | # The module supports:
    9 | # - Complete infrastructure discovery (all fabric sites, all devices)
   10 | # - Filtered extraction (specific fabric sites, device roles, or IP addresses)
   11 | # - File append mode for combining multiple configurations
   12 | #
   13 | # Prerequisites:
   14 | # - Cisco Catalyst Center version 2.3.7.6 or higher
   15 | # - Valid credentials configured in credentials.yml
   16 | # - Network connectivity to Catalyst Center
   17 | # ============================================================================
   18 | 
   19 | # Example 1: Generate all fabric device configurations for all fabric sites
   20 | - name: Generate complete SDA fabric devices configuration
   21 |   hosts: dnac_servers
   22 |   vars_files:
   23 |     - credentials.yml
   24 |   gather_facts: false
   25 |   connection: local
   26 |   tasks:
   27 |     - name: Generate all SDA fabric device configurations from Cisco Catalyst Center
   28 |       cisco.dnac.sda_fabric_devices_playbook_config_generator:
   29 |         dnac_host: "{{ dnac_host }}"
   30 |         dnac_port: "{{ dnac_port }}"
   31 |         dnac_username: "{{ dnac_username }}"
   32 |         dnac_password: "{{ dnac_password }}"
   33 |         dnac_verify: "{{ dnac_verify }}"
   34 |         dnac_debug: "{{ dnac_debug }}"
   35 |         dnac_version: "{{ dnac_version }}"
   36 |         dnac_log: true
   37 |         dnac_log_level: DEBUG
   38 |         dnac_log_append: false
   39 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
   40 |         state: gathered
   41 |         # No config provided - generates all configurations
   42 | 
   43 | # Example 2: Generate all configurations with custom file path
   44 | - name: Generate complete SDA fabric devices configuration with custom filename
   45 |   hosts: dnac_servers
   46 |   vars_files:
   47 |     - credentials.yml
   48 |   gather_facts: false
   49 |   connection: local
   50 |   tasks:
   51 |     - name: Generate all SDA fabric device configurations to a specific file
   52 |       cisco.dnac.sda_fabric_devices_playbook_config_generator:
   53 |         dnac_host: "{{ dnac_host }}"
   54 |         dnac_port: "{{ dnac_port }}"
   55 |         dnac_username: "{{ dnac_username }}"
   56 |         dnac_password: "{{ dnac_password }}"
   57 |         dnac_verify: "{{ dnac_verify }}"
   58 |         dnac_debug: "{{ dnac_debug }}"
   59 |         dnac_version: "{{ dnac_version }}"
   60 |         dnac_log: true
   61 |         dnac_log_level: DEBUG
   62 |         dnac_log_append: false
   63 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
   64 |         state: gathered
   65 |         file_path: "/tmp/complete_sda_fabric_devices_config.yaml"
   66 |         file_mode: "overwrite"
   67 |         # No config provided - generates all configurations
   68 | 
   69 | # Example 3: Generate fabric device configurations for a specific fabric site
   70 | - name: Generate fabric device configurations for one fabric site
   71 |   hosts: dnac_servers
   72 |   vars_files:
   73 |     - credentials.yml
   74 |   gather_facts: false
   75 |   connection: local
   76 |   tasks:
   77 |     - name: Export fabric devices from San Jose fabric
   78 |       cisco.dnac.sda_fabric_devices_playbook_config_generator:
   79 |         dnac_host: "{{ dnac_host }}"
   80 |         dnac_port: "{{ dnac_port }}"
   81 |         dnac_username: "{{ dnac_username }}"
   82 |         dnac_password: "{{ dnac_password }}"
   83 |         dnac_verify: "{{ dnac_verify }}"
   84 |         dnac_debug: "{{ dnac_debug }}"
   85 |         dnac_version: "{{ dnac_version }}"
   86 |         dnac_log: true
   87 |         dnac_log_level: DEBUG
   88 |         dnac_log_append: false
   89 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
   90 |         state: gathered
   91 |         file_path: "/tmp/san_jose_fabric_devices.yaml"
   92 |         file_mode: "overwrite"
   93 |         config:
   94 |           component_specific_filters:
   95 |             components_list: ["fabric_devices"]
   96 |             fabric_devices:
   97 |               - fabric_name: "Global/USA/SAN-JOSE"
   98 | 
   99 | # Example 4: Generate configuration for devices with specific roles in a fabric site
  100 | - name: Generate configuration for border and control plane devices
  101 |   hosts: dnac_servers
  102 |   vars_files:
  103 |     - credentials.yml
  104 |   gather_facts: false
  105 |   connection: local
  106 |   tasks:
  107 |     - name: Export border and control plane fabric devices from San Jose fabric
  108 |       cisco.dnac.sda_fabric_devices_playbook_config_generator:
  109 |         dnac_host: "{{ dnac_host }}"
  110 |         dnac_port: "{{ dnac_port }}"
  111 |         dnac_username: "{{ dnac_username }}"
  112 |         dnac_password: "{{ dnac_password }}"
  113 |         dnac_verify: "{{ dnac_verify }}"
  114 |         dnac_debug: "{{ dnac_debug }}"
  115 |         dnac_version: "{{ dnac_version }}"
  116 |         dnac_log: true
  117 |         dnac_log_level: DEBUG
  118 |         dnac_log_append: false
  119 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  120 |         state: gathered
  121 |         file_path: "/tmp/border_and_cp_devices.yaml"
  122 |         file_mode: "overwrite"
  123 |         config:
  124 |           component_specific_filters:
  125 |             components_list: ["fabric_devices"]
  126 |             fabric_devices:
  127 |               - fabric_name: "Global/USA/SAN-JOSE"
  128 |                 device_roles: ["BORDER_NODE", "CONTROL_PLANE_NODE"]
  129 | 
  130 | # Example 5: Generate configuration for a specific device in a fabric site
  131 | - name: Generate configuration for a specific fabric device
  132 |   hosts: dnac_servers
  133 |   vars_files:
  134 |     - credentials.yml
  135 |   gather_facts: false
  136 |   connection: local
  137 |   tasks:
  138 |     - name: Export specific fabric device configuration
  139 |       cisco.dnac.sda_fabric_devices_playbook_config_generator:
  140 |         dnac_host: "{{ dnac_host }}"
  141 |         dnac_port: "{{ dnac_port }}"
  142 |         dnac_username: "{{ dnac_username }}"
  143 |         dnac_password: "{{ dnac_password }}"
  144 |         dnac_verify: "{{ dnac_verify }}"
  145 |         dnac_debug: "{{ dnac_debug }}"
  146 |         dnac_version: "{{ dnac_version }}"
  147 |         dnac_log: true
  148 |         dnac_log_level: DEBUG
  149 |         dnac_log_append: false
  150 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  151 |         state: gathered
  152 |         file_path: "/tmp/specific_fabric_device.yaml"
  153 |         file_mode: "overwrite"
  154 |         config:
  155 |           component_specific_filters:
  156 |             components_list: ["fabric_devices"]
  157 |             fabric_devices:
  158 |               - fabric_name: "Global/USA/SAN-JOSE"
  159 |                 device_ip: "10.0.0.1"
  160 | 
  161 | # Example 6: Auto-populate components_list from component filters
  162 | - name: Generate configuration with auto-populated components_list
  163 |   hosts: dnac_servers
  164 |   vars_files:
  165 |     - credentials.yml
  166 |   gather_facts: false
  167 |   connection: local
  168 |   tasks:
  169 |     - name: Export fabric devices without explicit components_list
  170 |       cisco.dnac.sda_fabric_devices_playbook_config_generator:
  171 |         dnac_host: "{{ dnac_host }}"
  172 |         dnac_port: "{{ dnac_port }}"
  173 |         dnac_username: "{{ dnac_username }}"
  174 |         dnac_password: "{{ dnac_password }}"
  175 |         dnac_verify: "{{ dnac_verify }}"
  176 |         dnac_debug: "{{ dnac_debug }}"
  177 |         dnac_version: "{{ dnac_version }}"
  178 |         dnac_log: true
  179 |         dnac_log_level: DEBUG
  180 |         dnac_log_append: false
  181 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  182 |         state: gathered
  183 |         file_path: "/tmp/san_jose_fabric.yaml"
  184 |         file_mode: "overwrite"
  185 |         config:
  186 |           component_specific_filters:
  187 |             # No components_list specified, but fabric_devices filters are provided
  188 |             # The 'fabric_devices' component will be automatically added to components_list
  189 |             fabric_devices:
  190 |               - fabric_name: "Global/USA/SAN-JOSE"
  191 | 
  192 | # Example 7: Generate configuration with append mode
  193 | - name: Generate and append SDA fabric device configuration
  194 |   hosts: dnac_servers
  195 |   vars_files:
  196 |     - credentials.yml
  197 |   gather_facts: false
  198 |   connection: local
  199 |   tasks:
  200 |     - name: Append fabric device configurations to existing file
  201 |       cisco.dnac.sda_fabric_devices_playbook_config_generator:
  202 |         dnac_host: "{{ dnac_host }}"
  203 |         dnac_port: "{{ dnac_port }}"
  204 |         dnac_username: "{{ dnac_username }}"
  205 |         dnac_password: "{{ dnac_password }}"
  206 |         dnac_verify: "{{ dnac_verify }}"
  207 |         dnac_debug: "{{ dnac_debug }}"
  208 |         dnac_version: "{{ dnac_version }}"
  209 |         dnac_log: true
  210 |         dnac_log_level: DEBUG
  211 |         dnac_log_append: false
  212 |         dnac_log_file_path: "{{ dnac_log_file_path }}"
  213 |         state: gathered
  214 |         file_path: "/tmp/all_fabric_devices.yaml"
  215 |         file_mode: "append"
  216 |         config:
  217 |           component_specific_filters:
  218 |             components_list: ["fabric_devices"]
  219 |             fabric_devices:
  220 |               - fabric_name: "Global/India/Bangalore"
  221 |                 device_roles: ["BORDER_NODE"]
```

## Frozen tracked paths in the relevant role/scope

```text
.ansible-lint
.circleci/config.yml
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/feature_request.md
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/ansible-lint.yml
.github/workflows/automerge.yml
.github/workflows/docs.yml
.github/workflows/integration_tests.yml
.github/workflows/main.yml
.github/workflows/sanity_tests.yml
.github/workflows/sanity_tests_devel.yml
.github/workflows/unit_tests.yml
.gitignore
.yamllint.yml
CODEOWNERS
CONTRIBUTING.md
LICENSE
Makefile
Pipfile
README.md
changelogs/changelog.yaml
docs/Makefile
docs/_gh_include/footer.inc
docs/_gh_include/header.inc
docs/conf.py
docs/index.rst
docs/requirements.txt
galaxy.yml
meta/runtime.yml
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
[listing truncated after 120 paths]
```

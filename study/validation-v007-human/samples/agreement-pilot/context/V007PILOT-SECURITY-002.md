# Frozen source context: V007PILOT-SECURITY-002

- Repository: `cisco-en-programmability/dnacenter-ansible`
- Commit: `33276c6275a666371b085bea241441cf4f6a29d2`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `playbooks/network_devices_info_workflow_manager.yml` (reported anchor line 8)
- Object: `task` `9693f6ccbc1b4a3fbbeae8a7b0723cdb016c03ca4e61a78d9febb0d6a9f27f13`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–58 of 58:

```text
    1 | ---
    2 | - name: Get network devices info on Cisco Catalyst Center
    3 |   hosts: localhost
    4 |   connection: local
    5 |   vars_files:
    6 |     - vars/credentials.yml
    7 |   tasks:
    8 |     - name: Get Network Devices Info on Cisco Catalyst Center
    9 |       cisco.dnac.network_devices_info_workflow_manager:
   10 |         dnac_host: "{{ dnac_host }}"
   11 |         dnac_username: "{{ dnac_username }}"
   12 |         dnac_password: "{{ dnac_password }}"
   13 |         dnac_verify: "{{ dnac_verify }}"
   14 |         dnac_port: "{{ dnac_port }}"
   15 |         dnac_version: "{{ dnac_version }}"
   16 |         dnac_debug: "{{ dnac_debug }}"
   17 |         dnac_log: true
   18 |         dnac_log_level: DEBUG
   19 |         config_verify: false
   20 |         dnac_api_task_timeout: 1000
   21 |         dnac_task_poll_interval: 1
   22 |         state: gathered
   23 |         config:
   24 |           - network_devices:
   25 |               - site_hierarchy: Global/USA/SAN JOSE
   26 |                 device_type: "Cisco Catalyst 9300 Switch"
   27 |                 device_role: "ACCESS"
   28 |                 device_family: "Switches and Hubs"
   29 |                 software_version: "17.12.1"
   30 |                 os_type: "IOS-XE"
   31 |                 device_identifier:
   32 |                   - ip_address: ["204.1.2.1"]
   33 |                   - serial_number: ["FCW2137L0SB"]
   34 |                   - hostname: ["SJ-BN-9300.cisco.local"]
   35 |                   - mac_address: ["90:88:55:90:26:00"]
   36 |                 timeout: 60
   37 |                 retries: 3
   38 |                 interval: 10
   39 |                 requested_info:
   40 |                   - device_info
   41 |                   - interface_info
   42 |                   - interface_vlan_info
   43 |                   - line_card_info
   44 |                   - supervisor_card_info
   45 |                   - poe_info
   46 |                   - module_count_info
   47 |                   - connected_device_info
   48 |                   - device_interfaces_by_range_info
   49 |                   - device_config_info
   50 |                   - device_summary_info
   51 |                   - device_polling_interval_info
   52 |                   - device_stack_info
   53 |                   - device_link_mismatch_info
   54 |                 output_file_info:
   55 |                   file_path: /Users/priyadharshini/Downloads/info
   56 |                   file_format: json
   57 |                   file_mode: w
   58 |                   timestamp: true
```

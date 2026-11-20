# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-047

- Repository: `cisco-en-programmability/dnacenter-ansible`
- Commit: `33276c6275a666371b085bea241441cf4f6a29d2`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `playbooks/wired_campus_automation_workflow_manager.yml` (reported anchor line 412)
- Object: `variable` `1b8f32c4167a7c37489cbf99ffcc6a73b8adee6636691d4da22c9b8475b5f078`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 377–447 of 991:

```text
  377 |                 vtp_mode: "TRANSPARENT"
  378 |                 vtp_version: "VERSION_2"
  379 |                 vtp_domain_name: "CORPORATE_DOMAIN"
  380 |                 vtp_pruning: true
  381 |                 vtp_configuration_file_name: "flash:vtp_config.dat"
  382 |                 vtp_source_interface: "Loopback0"
  383 |       register: result_vtp_configure
  384 |       tags: [vtp, configure]
  385 | 
  386 |     - name: "EXAMPLE: Update VTP to client mode"
  387 |       cisco.dnac.wired_campus_automation_workflow_manager:
  388 |         <<: *dnac_login
  389 |         state: merged
  390 |         config:
  391 |           - ip_address: "204.1.2.3"
  392 |             device_collection_status_check: false
  393 |             layer2_configuration:
  394 |               vtp:
  395 |                 vtp_mode: "CLIENT"
  396 |                 vtp_pruning: false
  397 |       register: result_vtp_update
  398 |       tags: [vtp, update]
  399 | 
  400 |     - name: "EXAMPLE: Reset VTP to default settings"
  401 |       cisco.dnac.wired_campus_automation_workflow_manager:
  402 |         <<: *dnac_login
  403 |         state: deleted
  404 |         config:
  405 |           - ip_address: "204.1.2.3"
  406 |             device_collection_status_check: false
  407 |             layer2_configuration:
  408 |               vtp: {}
  409 |       register: result_vtp_reset
  410 |       tags: [vtp, reset]
  411 | 
  412 |     - name: "EXAMPLE: Reset VTP to default settings while providing full configuration"
  413 |       cisco.dnac.wired_campus_automation_workflow_manager:
  414 |         <<: *dnac_login
  415 |         state: deleted
  416 |         config:
  417 |           - ip_address: "204.1.2.3"
  418 |             device_collection_status_check: false
  419 |             layer2_configuration:
  420 |               vtp:
  421 |                 vtp_mode: "TRANSPARENT"
  422 |                 vtp_version: "VERSION_2"
  423 |                 vtp_domain_name: "CORPORATE_DOMAIN"
  424 |                 vtp_pruning: true
  425 |                 vtp_configuration_file_name: "flash:vtp_config.dat"
  426 |                 vtp_source_interface: "Loopback0"
  427 |       register: result_vtp_reset_full_config
  428 |       tags: [vtp, reset]
  429 | 
  430 |     # =============================================================================
  431 |     # DHCP SNOOPING CONFIGURATION EXAMPLES
  432 |     # =============================================================================
  433 | 
  434 |     - name: "EXAMPLE: Configure DHCP Snooping with comprehensive settings"
  435 |       cisco.dnac.wired_campus_automation_workflow_manager:
  436 |         <<: *dnac_login
  437 |         state: merged
  438 |         config:
  439 |           - ip_address: "204.1.2.3"
  440 |             device_collection_status_check: false
  441 |             layer2_configuration:
  442 |               dhcp_snooping:
  443 |                 dhcp_admin_status: true
  444 |                 dhcp_snooping_vlans: [100, 200, 300]
  445 |                 dhcp_snooping_glean: true
  446 |                 dhcp_snooping_database_agent_url: "tftp://192.168.1.100/dhcp_binding.db"
  447 |                 dhcp_snooping_database_timeout: 600
```

## Visible variable references

```text
33276c6275a666371b085bea241441cf4f6a29d2:playbooks/wired_campus_automation_workflow_manager.yml:427:      register: result_vtp_reset_full_config
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

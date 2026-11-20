# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-013

- Repository: `cisco-en-programmability/dnacenter-ansible`
- Commit: `33276c6275a666371b085bea241441cf4f6a29d2`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `playbooks/wired_campus_automation_playbook_config_generator.yml` (reported anchor line 458)
- Flagged construct: variable `result_lab_default`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 358–558 of 572:

```text
  358 |     # =============================================================================
  359 | 
  360 |     - name: "EXAMPLE: Generate YAML Configuration for security features"
  361 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  362 |         <<: *dnac_login
  363 |         state: gathered
  364 |         file_mode: "append"
  365 |         file_path: "/tmp/security_features_config.yml"
  366 |         config:
  367 |           global_filters:
  368 |             serial_number_list: ["FCW2140L05Y", "FCW2140L06Z"]
  369 |           component_specific_filters:
  370 |             layer2_configurations:
  371 |               layer2_features: ["dhcp_snooping", "igmp_snooping", "authentication"]
  372 |       register: result_security_config
  373 |       tags: [security_filtering, security_features]
  374 | 
  375 |     - name: "EXAMPLE: Generate configuration for authentication features only"
  376 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  377 |         <<: *dnac_login
  378 |         state: gathered
  379 |         file_mode: "append"
  380 |         file_path: "/tmp/authentication_config.yml"
  381 |         config:
  382 |           global_filters:
  383 |             ip_address_list: ["192.168.1.10", "192.168.1.11"]
  384 |           component_specific_filters:
  385 |             layer2_configurations:
  386 |               layer2_features: ["authentication"]
  387 |       register: result_authentication_only
  388 |       tags: [security_filtering, authentication]
  389 | 
  390 |     # =============================================================================
  391 |     # COMPREHENSIVE FILTERING COMBINATIONS
  392 |     # =============================================================================
  393 | 
  394 |     - name: "EXAMPLE: Generate YAML Configuration with comprehensive filtering"
  395 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  396 |         <<: *dnac_login
  397 |         state: gathered
  398 |         file_mode: "append"
  399 |         file_path: "/tmp/comprehensive_filtered_config.yml"
  400 |         config:
  401 |           global_filters:
  402 |             ip_address_list: ["192.168.1.10", "192.168.1.11"]
  403 |           component_specific_filters:
  404 |             components_list: ["layer2_configurations"]
  405 |             layer2_configurations:
  406 |               layer2_features: ["vlans", "stp", "port_configuration"]
  407 |               vlans:
  408 |                 vlan_ids_list: ["10", "20", "100"]
  409 |               port_configuration:
  410 |                 interface_names_list:
  411 |                   - "GigabitEthernet1/0/1"
  412 |                   - "GigabitEthernet1/0/24"
  413 |       register: result_comprehensive_filtering
  414 |       tags: [comprehensive, multi_filter]
  415 | 
  416 |     - name: "EXAMPLE: Generate YAML Configuration with all available components (future-proof)"
  417 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  418 |         <<: *dnac_login
  419 |         state: gathered
  420 |         file_mode: "append"
  421 |         file_path: "/tmp/all_components_config.yml"
  422 |         config:
  423 |           global_filters:
  424 |             ip_address_list: ["192.168.1.10", "192.168.1.11"]
  425 |           component_specific_filters:
  426 |             components_list: ["layer2_configurations"]
  427 |             layer2_configurations:
  428 |               layer2_features:
  429 |                 - "vlans"
  430 |                 - "cdp"
  431 |                 - "lldp"
  432 |                 - "stp"
  433 |                 - "vtp"
  434 |                 - "dhcp_snooping"
  435 |                 - "igmp_snooping"
  436 |                 - "mld_snooping"
  437 |                 - "authentication"
  438 |                 - "logical_ports"
  439 |                 - "port_configuration"
  440 |       register: result_all_components
  441 |       tags: [comprehensive, all_components]
  442 | 
  443 |     # =============================================================================
  444 |     # DEFAULT FILE PATH SCENARIOS
  445 |     # =============================================================================
  446 | 
  447 |     - name: "EXAMPLE: Generate YAML Configuration with default file path"
  448 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  449 |         <<: *dnac_login
  450 |         state: gathered
  451 |         file_mode: "append"
  452 |         config:
  453 |           global_filters:
  454 |             ip_address_list: ["192.168.1.10"]
  455 |       register: result_default_path
  456 |       tags: [default_settings, default_path]
  457 | 
  458 |     - name: "EXAMPLE: Generate configuration for lab environment with defaults"
  459 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  460 |         <<: *dnac_login
  461 |         state: gathered
  462 |         file_mode: "append"
  463 |         config:
  464 |           global_filters:
  465 |             hostname_list: ["lab-switch-01.test.com", "lab-switch-02.test.com"]
  466 |       register: result_lab_default
  467 |       tags: [lab_environment, defaults]
  468 | 
  469 |     # =============================================================================
  470 |     # SPECIALIZED USE CASES
  471 |     # =============================================================================
  472 | 
  473 |     - name: "EXAMPLE: Generate configuration for campus distribution layer"
  474 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  475 |         <<: *dnac_login
  476 |         state: gathered
  477 |         file_mode: "append"
  478 |         file_path: "/tmp/distribution_layer_config.yml"
  479 |         config:
  480 |           global_filters:
  481 |             hostname_list: ["dist-switch-01", "dist-switch-02"]
  482 |           component_specific_filters:
  483 |             layer2_configurations:
  484 |               layer2_features: ["vlans", "stp", "vtp", "logical_ports"]
  485 |               vlans:
  486 |                 vlan_ids_list: ["10", "20", "30", "40", "100", "200"]
  487 |       register: result_distribution_layer
  488 |       tags: [campus_network, distribution]
  489 | 
  490 |     - name: "EXAMPLE: Generate configuration for access layer switches"
  491 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  492 |         <<: *dnac_login
  493 |         state: gathered
  494 |         file_mode: "append"
  495 |         file_path: "/tmp/access_layer_config.yml"
  496 |         config:
  497 |           global_filters:
  498 |             hostname_list: ["access-sw-01", "access-sw-02", "access-sw-03"]
  499 |           component_specific_filters:
  500 |             layer2_configurations:
  501 |               layer2_features: ["vlans", "authentication", "dhcp_snooping", "port_configuration"]
  502 |               vlans:
  503 |                 vlan_ids_list: ["10", "20", "100", "200"]
  504 |               port_configuration:
  505 |                 interface_names_list:
  506 |                   - "GigabitEthernet1/0/1"
  507 |                   - "GigabitEthernet1/0/2"
  508 |                   - "GigabitEthernet1/0/3"
  509 |                   - "GigabitEthernet1/0/4"
  510 |       register: result_access_layer
  511 |       tags: [campus_network, access_layer]
  512 | 
  513 |     - name: "EXAMPLE: Generate configuration for specific building infrastructure"
  514 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  515 |         <<: *dnac_login
  516 |         state: gathered
  517 |         file_mode: "append"
  518 |         file_path: "/tmp/building_a_config.yml"
  519 |         config:
  520 |           global_filters:
  521 |             hostname_list:
  522 |               - "bldg-a-dist-01"
  523 |               - "bldg-a-acc-01"
  524 |               - "bldg-a-acc-02"
  525 |               - "bldg-a-acc-03"
  526 |           component_specific_filters:
  527 |             components_list: ["layer2_configurations"]
  528 |             layer2_configurations:
  529 |               layer2_features: ["vlans", "cdp", "lldp", "stp", "authentication", "port_configuration"]
  530 |       register: result_building_config
  531 |       tags: [building_specific, infrastructure]
  532 | 
  533 |     # =============================================================================
  534 |     # MAINTENANCE AND AUDIT SCENARIOS
  535 |     # =============================================================================
  536 | 
  537 |     - name: "EXAMPLE: Generate audit configuration for compliance review"
  538 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  539 |         <<: *dnac_login
  540 |         state: gathered
  541 |         file_mode: "append"
  542 |         file_path: "/tmp/compliance_audit_config.yml"
  543 |         config:
  544 |           global_filters:
  545 |             ip_address_list:
  546 |               - "192.168.1.10"
  547 |               - "192.168.1.11"
  548 |               - "192.168.1.12"
  549 |               - "192.168.1.13"
  550 |           component_specific_filters:
  551 |             layer2_configurations:
  552 |               layer2_features: ["authentication", "dhcp_snooping", "igmp_snooping"]
  553 |       register: result_compliance_audit
  554 |       tags: [maintenance, audit, compliance]
  555 | 
  556 |     - name: "EXAMPLE: Generate backup configuration for disaster recovery"
  557 |       cisco.dnac.wired_campus_automation_playbook_config_generator:
  558 |         <<: *dnac_login
```

## Visible variable references

```text
Whole-word search for `result_lab_default`: 1 matches in 1 files; 1 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
playbooks/wired_campus_automation_playbook_config_generator.yml:466:      register: result_lab_default

Other references:
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).

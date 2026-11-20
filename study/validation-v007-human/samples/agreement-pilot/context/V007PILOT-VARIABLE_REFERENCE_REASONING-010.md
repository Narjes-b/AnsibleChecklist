# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-010

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/missing-bool-filters`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/custom/matrix-bot-draupnir/tasks/validate_config.yml` (reported anchor line 1)
- Object: `source_location` `ac30625ef40e041565c3b4748223c6d21311e4f5e936aa20c3577fd3305d2222`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–92 of 92:

```text
    1 | # SPDX-FileCopyrightText: 2023 - 2025 MDAD project contributors
    2 | # SPDX-FileCopyrightText: 2023 - 2026 Catalan Lover <catalanlover@protonmail.com>
    3 | # SPDX-FileCopyrightText: 2024 - 2025 Slavi Pantaleev
    4 | #
    5 | # SPDX-License-Identifier: AGPL-3.0-or-later
    6 | 
    7 | ---
    8 | 
    9 | - name: (Deprecation) Catch and report renamed Draupnir settings
   10 |   ansible.builtin.fail:
   11 |     msg: >-
   12 |       Your configuration contains a variable, which now has a different name.
   13 |       Please rename the variable (`{{ item.old }}` -> `{{ item.new }}`) on your configuration file (vars.yml).
   14 |   when: "lookup('ansible.builtin.varnames', ('^' + item.old + '$'), wantlist=True) | length > 0"
   15 |   with_items:
   16 |     - {'old': 'matrix_bot_draupnir_container_image_name_prefix', 'new': 'matrix_bot_draupnir_container_image_registry_prefix'}
   17 |     - {'old': 'matrix_bot_draupnir_enable_room_state_backing_store', 'new': 'matrix_bot_draupnir_config_roomStateBackingStore_enabled'}
   18 |     - {'old': 'matrix_bot_draupnir_disable_server_acl', 'new': 'matrix_bot_draupnir_config_disableServerACL'}
   19 |     - {'old': 'matrix_bot_draupnir_enable_experimental_rust_crypto', 'new': 'matrix_bot_draupnir_config_experimentalRustCrypto'}
   20 |     - {'old': 'matrix_bot_draupnir_access_token', 'new': 'matrix_bot_draupnir_config_accessToken'}
   21 |     - {'old': 'matrix_bot_draupnir_management_room', 'new': 'matrix_bot_draupnir_config_managementRoom'}
   22 |     - {'old': 'matrix_bot_draupnir_homeserver_url', 'new': 'matrix_bot_draupnir_config_homeserverUrl'}
   23 |     - {'old': 'matrix_bot_draupnir_raw_homeserver_url', 'new': 'matrix_bot_draupnir_config_rawHomeserverUrl'}
   24 |     - {'old': 'matrix_bot_draupnir_web_enabled', 'new': 'matrix_bot_draupnir_config_web_enabled'}
   25 |     - {'old': 'matrix_bot_draupnir_abuse_reporting_enabled', 'new': 'matrix_bot_draupnir_config_web_abuseReporting'}
   26 |     - {'old': 'matrix_bot_draupnir_display_reports', 'new': 'matrix_bot_draupnir_config_displayReports'}
   27 |     - {'old': 'matrix_bot_draupnir_container_labels_traefik_hostname', 'new': 'matrix_bot_draupnir_container_labels_web_abuseReporting_traefik_hostname'}
   28 |     - {'old': 'matrix_bot_draupnir_container_labels_traefik_path_regexp', 'new': 'matrix_bot_draupnir_container_labels_web_abuseReporting_traefik_path_regexp'}
   29 |     - {'old': 'matrix_bot_draupnir_container_labels_traefik_rule', 'new': 'matrix_bot_draupnir_container_labels_web_abuseReporting_traefik_rule'}
   30 |     - {'old': 'matrix_bot_draupnir_container_labels_traefik_priority', 'new': 'matrix_bot_draupnir_container_labels_web_abuseReporting_traefik_priority'}
   31 |     - {'old': 'matrix_bot_draupnir_container_labels_traefik_entrypoints', 'new': 'matrix_bot_draupnir_container_labels_web_abuseReporting_traefik_entrypoints'}
   32 |     - {'old': 'matrix_bot_draupnir_container_labels_traefik_tls', 'new': 'matrix_bot_draupnir_container_labels_web_abuseReporting_traefik_tls'}
   33 |     - {'old': 'matrix_bot_draupnir_container_labels_traefik_tls_certResolver', 'new': 'matrix_bot_draupnir_container_labels_web_abuseReporting_traefik_tls_certResolver'}
   34 |     - {'old': 'matrix_bot_draupnir_docker_image', 'new': 'matrix_bot_draupnir_container_image'}
   35 |     - {'old': 'matrix_bot_draupnir_docker_image_force_pull', 'new': 'matrix_bot_draupnir_container_image_force_pull'}
   36 |     - {'old': 'matrix_bot_draupnir_docker_image_registry_prefix', 'new': 'matrix_bot_draupnir_container_image_registry_prefix'}
   37 |     - {'old': 'matrix_bot_draupnir_docker_image_registry_prefix_upstream', 'new': 'matrix_bot_draupnir_container_image_registry_prefix_upstream'}
   38 |     - {'old': 'matrix_bot_draupnir_docker_image_registry_prefix_upstream_default', 'new': 'matrix_bot_draupnir_container_image_registry_prefix_upstream_default'}
   39 |     - {'old': 'matrix_bot_draupnir_docker_src_files_path', 'new': 'matrix_bot_draupnir_container_src_files_path'}
   40 |     - {'old': 'matrix_bot_draupnir_container_image_force_pull', 'new': '<removed> (No longer needed due to new docker module doing this natively only if needed.)'}
   41 | 
   42 | - name: Fail if required matrix-bot-draupnir variables are undefined
   43 |   ansible.builtin.fail:
   44 |     msg: "The `{{ item.name }}` variable must be defined and have a non-null value."
   45 |   with_items:
   46 |     - {'name': 'matrix_bot_draupnir_config_accessToken', when: "{{ not matrix_bot_draupnir_pantalaimon_use and not matrix_bot_draupnir_login_native }}"}
   47 |     - {'name': 'matrix_bot_draupnir_config_accessToken', when: "{{ matrix_bot_draupnir_config_experimentalRustCrypto }}"}
   48 |     - {'name': 'matrix_bot_draupnir_config_managementRoom', when: "{{ not matrix_bot_draupnir_zero_touch_deploy }}"}
   49 |     - {'name': 'matrix_bot_draupnir_config_initialManager', when: "{{ matrix_bot_draupnir_zero_touch_deploy }}"}
   50 |     - {'name': 'matrix_bot_draupnir_container_network', when: true}
   51 |     - {'name': 'matrix_bot_draupnir_config_homeserverUrl', when: true}
   52 |     - {'name': 'matrix_bot_draupnir_config_rawHomeserverUrl', when: true}
   53 |     - {'name': 'matrix_bot_draupnir_pantalaimon_username', when: "{{ matrix_bot_draupnir_pantalaimon_use }}"}
   54 |     - {'name': 'matrix_bot_draupnir_pantalaimon_password', when: "{{ matrix_bot_draupnir_pantalaimon_use }}"}
   55 |   when: "item.when | bool and (lookup('vars', item.name, default='') == '' or lookup('vars', item.name, default='') is none)"
   56 | 
   57 | - name: Fail if Draupnir room hijacking enabled without enabling the Synapse Admin API
   58 |   ansible.builtin.fail:
   59 |     msg: "When matrix_bot_draupnir_config_admin_enableMakeRoomAdminCommand is enabled, matrix_bot_draupnir_admin_api_enabled must also be enabled"
   60 |   when: "matrix_bot_draupnir_config_admin_enableMakeRoomAdminCommand | bool and not matrix_bot_draupnir_admin_api_enabled | bool"
   61 | 
   62 | - name: Fail if inappropriate variables are defined
   63 |   ansible.builtin.fail:
   64 |     msg: "The `{{ item.name }}` variable must be undefined or have a null value."
   65 |   with_items:
   66 |     - {'name': 'matrix_bot_draupnir_config_accessToken', when: "{{ matrix_bot_draupnir_pantalaimon_use }}"}
   67 |     - {'name': 'matrix_bot_draupnir_config_accessToken', when: "{{ matrix_bot_draupnir_login_native }}"}
   68 |     - {'name': 'matrix_bot_draupnir_config_managementRoom', when: "{{ matrix_bot_draupnir_zero_touch_deploy }}"}
   69 |     - {'name': 'matrix_bot_draupnir_config_initialManager', when: "{{ not matrix_bot_draupnir_zero_touch_deploy }}"}
   70 |   when: "item.when | bool and not (lookup('vars', item.name, default='') == '' or lookup('vars', item.name, default='') is none)"
   71 | 
   72 | - name: Fail when matrix_bot_draupnir_config_experimentalRustCrypto is enabled together with matrix_bot_draupnir_pantalaimon_use
   73 |   ansible.builtin.fail:
   74 |     msg: >-
   75 |       Your configuration is trying to enable matrix_bot_draupnir_config_experimentalRustCrypto and matrix_bot_draupnir_pantalaimon_use at the same time.
   76 |       These settings are mutually incompatible and therefore can't be used at the same time.
   77 |   when:
   78 |     - matrix_bot_draupnir_pantalaimon_use
   79 |     - matrix_bot_draupnir_config_experimentalRustCrypto
   80 | 
   81 | - when: "matrix_bot_draupnir_pantalaimon_use == 'true' and matrix_bot_draupnir_pantalaimon_breakage_ignore == 'false'"
   82 |   block:
   83 |     - name: Inject warning if Pantalaimon is used together with Draupnir
   84 |       ansible.builtin.set_fact:
   85 |         devture_playbook_runtime_messages_list: |
   86 |           {{
   87 |             devture_playbook_runtime_messages_list | default([])
   88 |             +
   89 |             [
   90 |               "Note: Draupnir does not support running with Pantalaimon as it would break all workflows that involve answering prompts with reactions. To enable E2EE for Draupnir, it is recommended to use matrix_bot_draupnir_config_experimentalRustCrypto instead. This warning can be disabled by setting matrix_bot_draupnir_pantalaimon_breakage_ignore to true."
   91 |             ]
   92 |           }}
```

# Frozen source context: V007PILOT-STYLE_POLICY-004

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: Style/policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/variables/vars/main.yml` (reported anchor line 2528)
- Object: `source_location` `1a3cf34646bc5200ef65c1437727876bd891c1e88d4fd0675a3fcfe41a3499ba`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 2493–2563 of 2955:

```text
 2493 |       confluent.controlcenter.schema.registry.basic.auth.user.info: "{{schema_registry_basic_users_final.admin.principal}}:{{schema_registry_basic_users_final.admin.password}}"
 2494 |   sr_oauth:
 2495 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) }}"
 2496 |     properties:
 2497 |       confluent.controlcenter.schema.registry.oauthbearer.login.client.id: "{{ control_center_next_gen_oauth_user }}"
 2498 |   sr_oauth_secret:[REDACTED VALUE BLOCK]
 2499 |     [REDACTED ENCRYPTED VALUE]
 2500 |     [REDACTED ENCRYPTED VALUE]
 2501 |       [REDACTED ENCRYPTED VALUE]
 2502 |       [REDACTED ENCRYPTED VALUE]
 2503 |   sr_oauth_scope:
 2504 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) and oauth_groups_scope!='none' and (not control_center_next_gen_oauth_client_assertion_enabled) }}"
 2505 |     properties:
 2506 |       confluent.controlcenter.schema.registry.oauthbearer.login.oauth.scope: "{{ oauth_groups_scope }}"
 2507 |   sr_oauth_third_party_client_assertion:
 2508 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) and control_center_next_gen_oauth_client_assertion_enabled and control_center_next_gen_oauth_client_assertion_file_base_path != 'none' }}"
 2509 |     properties:
 2510 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.file: "{{ control_center_next_gen_third_party_oauth_client_assertion_config.kafka }}"
 2511 |   sr_oauth_local_client_assertion:
 2512 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) and control_center_next_gen_oauth_client_assertion_enabled and control_center_next_gen_oauth_client_assertion_file_base_path == 'none' }}"
 2513 |     properties:
 2514 |       confluent.controlcenter.schema.registry.bearer.auth.credentials.source: [REDACTED_LITERAL]
 2515 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.claim.iss: "{{ control_center_next_gen_oauth_client_assertion_issuer }}"
 2516 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.claim.sub: "{{ control_center_next_gen_oauth_client_assertion_sub }}"
 2517 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.claim.aud: "{{ control_center_next_gen_oauth_client_assertion_audience }}"
 2518 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.private.key.file: "{{ control_center_next_gen_oauth_client_assertion_private_key_file_dest_path }}"
 2519 |   sr_oauth_local_client_assertion_template_file:
 2520 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) and control_center_next_gen_oauth_client_assertion_enabled and control_center_next_gen_oauth_client_assertion_file_base_path == 'none' and control_center_next_gen_oauth_client_assertion_template_file != 'none' }}"
 2521 |     properties:
 2522 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.template.file: "{{ control_center_next_gen_oauth_client_assertion_template_file_dest_path }}"
 2523 |   sr_oauth_local_client_assertion_passphrase:[REDACTED VALUE BLOCK]
 2524 |     [REDACTED ENCRYPTED VALUE]
 2525 |     [REDACTED ENCRYPTED VALUE]
 2526 |       [REDACTED ENCRYPTED VALUE]
 2527 |   sr_oauth_local_client_assertion_jti_include:
 2528 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) and control_center_next_gen_oauth_client_assertion_enabled and control_center_next_gen_oauth_client_assertion_file_base_path == 'none' and control_center_next_gen_oauth_client_assertion_jti_include != 'none' }}"
 2529 |     properties:
 2530 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.claim.jti.include: "{{ control_center_next_gen_oauth_client_assertion_jti_include }}"
 2531 |   sr_oauth_local_client_assertion_nbf_include:
 2532 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) and control_center_next_gen_oauth_client_assertion_enabled and control_center_next_gen_oauth_client_assertion_file_base_path == 'none' and control_center_next_gen_oauth_client_assertion_nbf_include != 'none' }}"
 2533 |     properties:
 2534 |       confluent.controlcenter.schema.registry.oauthbearer.assertion.claim.nbf.include: "{{ control_center_next_gen_oauth_client_assertion_nbf_include }}"
 2535 |   sr_oauth_ssl:
 2536 |     enabled: "{{ ('schema_registry' in groups and schema_registry_oauth_enabled|bool) and (not rbac_enabled|bool) and idp_self_signed }}"
 2537 |     properties:
 2538 |       confluent.controlcenter.schema.registry.ssl.truststore.location: "{{ control_center_next_gen_truststore_path }}"
 2539 |       confluent.controlcenter.schema.registry.ssl.truststore.password: "{{ control_center_next_gen_truststore_storepass }}"
 2540 |   connect:
 2541 |     enabled: "{{ kafka_connect_cluster_ansible_group_names | default(omit) | length > 0 }}"
 2542 |     properties: "{{ kafka_connect_cluster_ansible_group_names | confluent.platform.c3_connect_properties(groups, hostvars, kafka_connect_ssl_enabled,
 2543 |         kafka_connect_http_protocol, kafka_connect_rest_port, kafka_connect_group_id, control_center_next_gen_truststore_path, control_center_next_gen_truststore_storepass,
 2544 |         control_center_next_gen_keystore_path, control_center_next_gen_keystore_storepass, control_center_next_gen_keystore_keypass, kafka_connect_oauth_enabled, rbac_enabled,
 2545 |         control_center_next_gen_oauth_user, control_center_next_gen_oauth_password, oauth_groups_scope, idp_self_signed) }}"
 2546 |   ksql:
 2547 |     enabled: "{{ ksql_cluster_ansible_group_names | default(omit) | length > 0 }}"
 2548 |     properties: "{{ ksql_cluster_ansible_group_names | confluent.platform.c3_ksql_properties(groups, hostvars, ksql_ssl_enabled,
 2549 |         ksql_http_protocol, ksql_listener_port, control_center_next_gen_truststore_path, control_center_next_gen_truststore_storepass,
 2550 |         control_center_next_gen_keystore_path, control_center_next_gen_keystore_storepass, control_center_next_gen_keystore_keypass, ksql_oauth_enabled, rbac_enabled,
 2551 |         control_center_next_gen_oauth_user, control_center_next_gen_oauth_password, oauth_groups_scope, idp_self_signed) }}"
 2552 |   oauth:
 2553 |     enabled: "{{oauth_enabled or schema_registry_oauth_enabled or kafka_connect_oauth_enabled or ksql_oauth_enabled}}"
 2554 |     properties:
 2555 |       confluent.metadata.oauthbearer.token.endpoint.url: "{{ oauth_token_uri }}"
 2556 |   rbac:
 2557 |     enabled: "{{rbac_enabled}}"
 2558 |     properties:
 2559 |       confluent.controlcenter.rest.authentication.method: BEARER
 2560 |       public.key.path: "{{rbac_enabled_public_pem_path}}"
 2561 |       confluent.metadata.bootstrap.server.urls: "{{mds_bootstrap_server_urls}}"
 2562 |   rbac_ldap:
 2563 |     enabled: "{{rbac_enabled and auth_mode == 'ldap' and (not control_center_next_gen_mds_cert_auth_only) }}"
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

# Frozen source context: V007PILOT-STRUCTURE_REUSE-020

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `playbooks/fetch_logs.yml` (reported anchor line 1)
- Object: `source_location` `162515bd365fba406af4e142e43283c70b713694e9debbddbceea1b589657894`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–127 of 127:

```text
    1 | ---
    2 | - name: Import all variables
    3 |   hosts: all
    4 |   tags: always
    5 |   tasks:
    6 |     - import_role:
    7 |         name: variables
    8 | 
    9 | - name: Kafka Controller Provisioning
   10 |   hosts: kafka_controller
   11 |   gather_facts: false
   12 |   tags: kafka_controller
   13 |   tasks:
   14 |     - include_role:
   15 |         name: common
   16 |         tasks_from: fetch_logs.yml
   17 |       vars:
   18 |         service_name: "{{ kafka_controller_service_name }}"
   19 |         config_file: "{{ kafka_controller.config_file }}"
   20 |         log_dir: "{{kafka_controller_log_dir}}"
   21 |         user: "{{kafka_controller_user}}"
   22 |         group: "{{kafka_controller_group}}"
   23 | 
   24 | - name: Kafka Broker Provisioning
   25 |   hosts: kafka_broker
   26 |   gather_facts: false
   27 |   tags: kafka_broker
   28 |   tasks:
   29 |     - include_role:
   30 |         name: common
   31 |         tasks_from: fetch_logs.yml
   32 |       vars:
   33 |         service_name: "{{ kafka_broker_service_name }}"
   34 |         config_file: "{{ kafka_broker.config_file }}"
   35 |         log_dir: "{{kafka_broker_log_dir}}"
   36 |         user: "{{kafka_broker_user}}"
   37 |         group: "{{kafka_broker_group}}"
   38 | 
   39 | - name: Schema Registry Provisioning
   40 |   hosts: schema_registry
   41 |   gather_facts: false
   42 |   tags: schema_registry
   43 |   tasks:
   44 |     - include_role:
   45 |         name: common
   46 |         tasks_from: fetch_logs.yml
   47 |       vars:
   48 |         service_name: "{{ schema_registry_service_name }}"
   49 |         config_file: "{{ schema_registry.config_file }}"
   50 |         log_dir: "{{schema_registry_log_dir}}"
   51 |         user: "{{schema_registry_user}}"
   52 |         group: "{{schema_registry_group}}"
   53 | 
   54 | - name: Kafka Connect Provisioning
   55 |   hosts: kafka_connect
   56 |   gather_facts: false
   57 |   tags: kafka_connect
   58 |   tasks:
   59 |     - include_role:
   60 |         name: common
   61 |         tasks_from: fetch_logs.yml
   62 |       vars:
   63 |         service_name: "{{ kafka_connect_service_name }}"
   64 |         config_file: "{{ kafka_connect.config_file }}"
   65 |         log_dir: "{{kafka_connect_log_dir}}"
   66 |         user: "{{kafka_connect_user}}"
   67 |         group: "{{kafka_connect_group}}"
   68 | 
   69 | - name: Kafka Connect Provisioning
   70 |   hosts: kafka_connect_replicator
   71 |   gather_facts: false
   72 |   tags: kafka_connect_replicator
   73 |   tasks:
   74 |     - include_role:
   75 |         name: common
   76 |         tasks_from: fetch_logs.yml
   77 |       vars:
   78 |         service_name: "{{ kafka_connect_replicator_service_name }}"
   79 |         config_file: "{{ kafka_connect_replicator.config_file }}"
   80 |         log_dir: "{{kafka_connect_replicator_log_dir}}"
   81 |         user: "{{kafka_connect_replicator_user}}"
   82 |         group: "{{kafka_connect_replicator_group}}"
   83 | 
   84 | - name: KSQL Provisioning
   85 |   hosts: ksql
   86 |   gather_facts: false
   87 |   tags: ksql
   88 |   tasks:
   89 |     - include_role:
   90 |         name: common
   91 |         tasks_from: fetch_logs.yml
   92 |       vars:
   93 |         service_name: "{{ ksql_service_name }}"
   94 |         config_file: "{{ ksql.config_file }}"
   95 |         log_dir: "{{ksql_log_dir}}"
   96 |         user: "{{ksql_user}}"
   97 |         group: "{{ksql_group}}"
   98 | 
   99 | - name: Kafka Rest Provisioning
  100 |   hosts: kafka_rest
  101 |   gather_facts: false
  102 |   tags: kafka_rest
  103 |   tasks:
  104 |     - include_role:
  105 |         name: common
  106 |         tasks_from: fetch_logs.yml
  107 |       vars:
  108 |         service_name: "{{ kafka_rest_service_name }}"
  109 |         config_file: "{{ kafka_rest.config_file }}"
  110 |         log_dir: "{{kafka_rest_log_dir}}"
  111 |         user: "{{kafka_rest_user}}"
  112 |         group: "{{kafka_rest_group}}"
  113 | 
  114 | - name: Control Center Next Gen Provisioning
  115 |   hosts: control_center_next_gen
  116 |   gather_facts: false
  117 |   tags: control_center_next_gen
  118 |   tasks:
  119 |     - include_role:
  120 |         name: common
  121 |         tasks_from: fetch_logs.yml
  122 |       vars:
  123 |         service_name: "{{ control_center_next_gen_service_name }}"
  124 |         config_file: "{{ control_center_next_gen.config_file }}"
  125 |         log_dir: "{{control_center_next_gen_log_dir}}"
  126 |         user: "{{control_center_next_gen_user}}"
  127 |         group: "{{control_center_next_gen_group}}"
```

## Frozen tracked paths in the relevant role/scope

```text
.ansible-lint
.bumpversion-ansible.cfg
.bumpversion.cfg
.config/molecule/config.yml
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/issue-report.md
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/linter.yml
.gitignore
.python-version
.semaphore/build_collection.sh
.semaphore/sanity_tests.sh
.semaphore/semaphore.yml
.semaphore/setfact_secret_check.py
.semaphore/tests/README.md
.semaphore/tests/__init__.py
.semaphore/tests/pytest.ini
.semaphore/tests/requirements.txt
.semaphore/tests/test_setfact_secret_check.py
.semaphore/tests/test_uri_auth_check.py
.semaphore/uri_auth_check.py
.yamllint
CHANGELOG.rst
LICENSE.md
README.md
ansible.cfg
docs/CODE_OF_CONDUCT.md
docs/CONTRIBUTING.md
docs/DEVELOPMENT_GUIDE.md
docs/HOW_TO_TEST.md
docs/MOLECULE_SCENARIOS.md
docs/PULL_REQUEST_TEMPLATE.md
docs/TAGS.md
docs/VARIABLES.md
docs/doc.py
docs/hosts_example.yml
docs/molecule_doc.py
docs/rules_example.json
docs/sample_inventories/ACLs.txt
docs/sample_inventories/c3-next-gen-active-active-setup/README.md
docs/sample_inventories/c3-next-gen-active-active-setup/c3-next-gen-active-active.yml
docs/sample_inventories/ccloud.yml
docs/sample_inventories/ccloud_self_managed_schema_registry.yml
docs/sample_inventories/client_listener_for_ldap_users.yml
docs/sample_inventories/controller_broker_scram_kraft.yml
docs/sample_inventories/fips.yml
docs/sample_inventories/inter_broker_scram_kraft.yml
docs/sample_inventories/kafka_connect_replicator.yml
docs/sample_inventories/kafka_connect_replicator_rbac.yml
docs/sample_inventories/kerberos_kraft.yml
docs/sample_inventories/mtlsACLs.txt
docs/sample_inventories/mtls_kraft.yml
docs/sample_inventories/multi_connect_workers_on_single_node.yml
docs/sample_inventories/nonRBACtoRBACLdap.yml
docs/sample_inventories/nonRBACtoRBACOAuth.yml
docs/sample_inventories/non_root_deployment.yml
docs/sample_inventories/oauth_brownfield.yml
docs/sample_inventories/oauth_greenfield.yml
docs/sample_inventories/oauth_greenfield_non_rbac.yml
docs/sample_inventories/rbac-ldap-to-mtls-brownfield/README.md
docs/sample_inventories/rbac-ldap-to-mtls-brownfield/step0_ldap_setup.yml
docs/sample_inventories/rbac-ldap-to-mtls-brownfield/step1_enable_mtls.yml
docs/sample_inventories/rbac-ldap-to-mtls-brownfield/step2_client_migration.yml
docs/sample_inventories/rbac-ldap-to-mtls-brownfield/step3_required.yml
docs/sample_inventories/rbac-ldap-to-mtls-brownfield/step4_ldap_to_sso.yml
docs/sample_inventories/rbac-oauth-to-mtls-brownfield/README.md
docs/sample_inventories/rbac-oauth-to-mtls-brownfield/step0_oauth_sso_setup.yml
docs/sample_inventories/rbac-oauth-to-mtls-brownfield/step1_enable_mtls.yml
docs/sample_inventories/rbac-oauth-to-mtls-brownfield/step2_client_migration.yml
docs/sample_inventories/rbac-oauth-to-mtls-brownfield/step3_required.yml
docs/sample_inventories/rbac-over-mtls-centralized-mds.yml
docs/sample_inventories/rbac-over-mtls-file-based-user-store.yml
docs/sample_inventories/rbac-over-oauth-and-mtls.yml
docs/sample_inventories/rbac_centralized_mds_kerberos_custom_certs_example.yml
docs/sample_inventories/rbac_kerberos_custom_certs_example.yml
docs/sample_inventories/rbac_mutiple_ksql.yml
docs/sample_inventories/rbac_sso_c3.yml
docs/sample_inventories/sasl_ssl_kraft.yml
docs/sample_inventories/single_dev_node.yml
docs/sample_inventories/sr-automation-workflow/README.md
docs/sample_inventories/sr-automation-workflow/sr_switchover_cp_to_cc.yml
docs/sample_inventories/ssm/ssm_hostname_aliasing.yml
docs/sample_inventories/ssm/ssm_without_hostname_aliasing.yml
docs/sample_inventories/usm_agent/README_USM_AGENT.md
docs/sample_inventories/usm_agent/usm_agent_basic_auth.yml
docs/sample_inventories/usm_agent/usm_agent_basic_auth_tls.yml
docs/sample_inventories/usm_agent/usm_agent_mtls.yml
docs/sample_inventories/usm_agent/usm_agent_mtls_custom_certs.yml
docs/sample_inventories/usm_agent/usm_agent_no_auth.yml
galaxy.yml
galaxy_importer/galaxy-importer.cfg
githooks/README.md
githooks/install-githooks.sh
githooks/prepare-commit-msg
meta/runtime.yml
molecule/Dockerfile-amazonlinux2023.j2
molecule/Dockerfile-centos8-base.j2
molecule/Dockerfile-debian-archive.j2
molecule/Dockerfile-debian-java21.j2
molecule/Dockerfile-debian10-java11.j2
molecule/Dockerfile-debian10.j2
molecule/Dockerfile-debian12-java17.j2
molecule/Dockerfile-debian12.j2
molecule/Dockerfile-oauth.j2
molecule/Dockerfile-rhel-java17.j2
molecule/Dockerfile-rhel-java21.j2
molecule/Dockerfile-rhel-java25.j2
molecule/Dockerfile-rhel-python39.j2
molecule/Dockerfile-rhel-tar.j2
molecule/Dockerfile-ubuntu-archive.j2
molecule/Dockerfile-ubuntu-java17-lean.j2
molecule/Dockerfile-ubuntu-java17.j2
molecule/Dockerfile-ubuntu-java21-lean.j2
molecule/Dockerfile-ubuntu-java21.j2
molecule/Dockerfile-ubuntu-java25-lean.j2
molecule/Dockerfile-ubuntu-java25.j2
molecule/Dockerfile-ubuntu2004-archive-java25.j2
molecule/Dockerfile-ubuntu2004-archive.j2
molecule/archive-community-plaintext-rhel/cleanup.yml
molecule/archive-community-plaintext-rhel/molecule.yml
[listing truncated after 120 paths]
```

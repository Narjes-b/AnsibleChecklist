# Frozen source context: V007PILOT-STRUCTURE_REUSE-044

- Repository: `os-migrate/os-migrate`
- Commit: `60e4123dd2391233d23149d7dfb6ebe4b0870590`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `playbooks/deploy_conversion_hosts.yml` (reported anchor line 1)
- Object: `source_location` `50d2e3aa2376df100040d144be6528504cb7b6281f0530dc69468d4508554d20`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–208 of 208:

```text
    1 | - name: Deploy conversion hosts
    2 |   hosts: migrator
    3 |   environment:
    4 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
    5 |   any_errors_fatal: true
    6 |   tasks:
    7 |     - name: Deploy the src conversion host inventory
    8 |       ansible.builtin.include_role:
    9 |         name: os_migrate.os_migrate.conversion_host
   10 |       vars:
   11 |         os_migrate_conversion_host_name: "{{ os_migrate_src_conversion_host_name }}"
   12 |         os_migrate_conversion_image_name: "{{ os_migrate_src_conversion_image_name | default('os_migrate_conv') }}"
   13 |         os_migrate_conversion_net_name: "{{ os_migrate_src_conversion_net_name | default('os_migrate_conv') }}"
   14 |         os_migrate_conversion_subnet_name: "{{ os_migrate_src_conversion_subnet_name | default('os_migrate_conv') }}"
   15 |         os_migrate_conversion_router_name: "{{ os_migrate_src_conversion_router_name | default('os_migrate_conv') }}"
   16 |         os_migrate_conversion_secgroup_name: "{{ os_migrate_src_conversion_secgroup_name | default('os_migrate_conv') }}"
   17 |         os_migrate_conversion_keypair_name: "{{ os_migrate_src_conversion_keypair_name | default('os_migrate_conv') }}"
   18 |         os_migrate_conversion_host_boot_from_volume: "{{ os_migrate_src_conversion_host_boot_from_volume | default(omit) }}"
   19 |         os_migrate_conversion_host_volume_size: "{{ os_migrate_src_conversion_host_volume_size | default(omit) }}"
   20 |         os_migrate_conversion_availability_zone: "{{ os_migrate_src_conversion_availability_zone | default(omit) }}"
   21 |         os_migrate_conversion_cloud: src
   22 |         os_migrate_conversion_validate_certs: "{{ os_migrate_src_validate_certs | default(omit) }}"
   23 |         os_migrate_conversion_ca_cert: "{{ os_migrate_src_ca_cert | default(omit) }}"
   24 |         os_migrate_conversion_client_cert: "{{ os_migrate_src_client_cert | default(omit) }}"
   25 |         os_migrate_conversion_client_key: "{{ os_migrate_src_client_key | default(omit) }}"
   26 |         os_migrate_conversion_flavor_name:
   27 |           "{{ os_migrate_src_conversion_flavor_name | default(omit) }}"
   28 |         os_migrate_conversion_external_network_name:
   29 |           "{{ os_migrate_src_conversion_external_network_name | default('') }}"
   30 |         os_migrate_conversion_net_mtu: "{{ os_migrate_src_conversion_net_mtu | default(omit) }}"
   31 |         os_migrate_conversion_subnet_dns_nameservers:
   32 |           "{{ os_migrate_src_conversion_subnet_dns_nameservers | default(omit) }}"
   33 |         os_migrate_conversion_manage_network: "{{ os_migrate_src_conversion_manage_network | default(true) }}"
   34 |         os_migrate_conversion_manage_fip: "{{ os_migrate_src_conversion_manage_fip | default(true) }}"
   35 |         os_migrate_conversion_floating_ip_address: "{{ os_migrate_src_conversion_floating_ip_address | default(false) }}"
   36 |       when: os_migrate_deploy_src_conversion_host | default(true) | bool
   37 | 
   38 |     - name: Deploy the dst conversion host inventory
   39 |       ansible.builtin.include_role:
   40 |         name: os_migrate.os_migrate.conversion_host
   41 |       vars:
   42 |         os_migrate_conversion_host_name: "{{ os_migrate_dst_conversion_host_name }}"
   43 |         os_migrate_conversion_image_name: "{{ os_migrate_dst_conversion_image_name | default('os_migrate_conv') }}"
   44 |         os_migrate_conversion_net_name: "{{ os_migrate_dst_conversion_net_name | default('os_migrate_conv') }}"
   45 |         os_migrate_conversion_subnet_name: "{{ os_migrate_dst_conversion_subnet_name | default('os_migrate_conv') }}"
   46 |         os_migrate_conversion_router_name: "{{ os_migrate_dst_conversion_router_name | default('os_migrate_conv') }}"
   47 |         os_migrate_conversion_secgroup_name: "{{ os_migrate_dst_conversion_secgroup_name | default('os_migrate_conv') }}"
   48 |         os_migrate_conversion_keypair_name: "{{ os_migrate_dst_conversion_keypair_name | default('os_migrate_conv') }}"
   49 |         os_migrate_conversion_host_boot_from_volume: "{{ os_migrate_dst_conversion_host_boot_from_volume | default(omit) }}"
   50 |         os_migrate_conversion_host_volume_size: "{{ os_migrate_dst_conversion_host_volume_size | default(omit) }}"
   51 |         os_migrate_conversion_availability_zone: "{{ os_migrate_dst_conversion_availability_zone | default(omit) }}"
   52 |         os_migrate_conversion_cloud: dst
   53 |         os_migrate_conversion_validate_certs: "{{ os_migrate_dst_validate_certs | default(omit) }}"
   54 |         os_migrate_conversion_ca_cert: "{{ os_migrate_dst_ca_cert | default(omit) }}"
   55 |         os_migrate_conversion_client_cert: "{{ os_migrate_dst_client_cert | default(omit) }}"
   56 |         os_migrate_conversion_client_key: "{{ os_migrate_dst_client_key | default(omit) }}"
   57 |         os_migrate_conversion_flavor_name:
   58 |           "{{ os_migrate_dst_conversion_flavor_name | default(omit) }}"
   59 |         os_migrate_conversion_external_network_name:
   60 |           "{{ os_migrate_dst_conversion_external_network_name | default('') }}"
   61 |         os_migrate_conversion_net_mtu: "{{ os_migrate_dst_conversion_net_mtu | default(omit) }}"
   62 |         os_migrate_conversion_subnet_dns_nameservers:
   63 |           "{{ os_migrate_dst_conversion_subnet_dns_nameservers | default(omit) }}"
   64 |         os_migrate_conversion_manage_network: "{{ os_migrate_dst_conversion_manage_network | default(true) }}"
   65 |         os_migrate_conversion_manage_fip: "{{ os_migrate_dst_conversion_manage_fip | default(true) }}"
   66 |         os_migrate_conversion_floating_ip_address: "{{ os_migrate_dst_conversion_floating_ip_address | default(false) }}"
   67 |       when: os_migrate_deploy_dst_conversion_host | default(true) | bool
   68 | 
   69 |     - name: Prepare the conversion host link
   70 |       ansible.builtin.include_role:
   71 |         name: os_migrate.os_migrate.conversion_host
   72 |         tasks_from: link_prepare.yml
   73 |       when: os_migrate_link_conversion_hosts | default(true) | bool
   74 | 
   75 |     - name: Pause to let sshd start on the conversion hosts
   76 |       ansible.builtin.pause:
   77 |         minutes: 2
   78 | 
   79 | - name: Configure source conversion host
   80 |   hosts: os_migrate_conv_src
   81 |   environment:
   82 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
   83 |   any_errors_fatal: true
   84 |   tasks:
   85 |     - name: Insert the auth keys in src
   86 |       ansible.builtin.include_role:
   87 |         name: os_migrate.os_migrate.conversion_host_content
   88 |         tasks_from: link_insert_authorized_key.yml
   89 |       when: os_migrate_link_conversion_hosts | default(true) | bool
   90 | 
   91 | - name: Configure destination conversion host
   92 |   hosts: os_migrate_conv_dst
   93 |   environment:
   94 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
   95 |   any_errors_fatal: true
   96 |   tasks:
   97 |     - name: Insert the auth keys in dst
   98 |       ansible.builtin.include_role:
   99 |         name: os_migrate.os_migrate.conversion_host_content
  100 |         tasks_from: link_insert_private_key.yml
  101 |       when: os_migrate_link_conversion_hosts | default(true) | bool
  102 | 
  103 | - name: Configure password access for conversion hosts
  104 |   hosts: conversion_hosts
  105 |   environment:
  106 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
  107 |   any_errors_fatal: true
  108 |   tasks:
  109 |     - name: Enable ssh_user password access to the conversion hosts
  110 |       ansible.builtin.include_role:
  111 |         name: os_migrate.os_migrate.conversion_host_content
  112 |         tasks_from: enable_password_access.yml
  113 |       when: os_migrate_conversion_host_ssh_user_enable_password_access | default(false) | bool
  114 |   vars:
  115 |     ansible_become_user: root
  116 |     ansible_become: true
  117 | 
  118 | - name: Set source conversion host facts
  119 |   hosts: os_migrate_conv_src
  120 |   environment:
  121 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
  122 |   any_errors_fatal: true
  123 |   tasks:
  124 |     - name: Set src conversion host facts
  125 |       ansible.builtin.set_fact:
  126 |         os_migrate_conversion_host_pre_content_hook: "{{ os_migrate_src_conversion_host_pre_content_hook | default(false) }}"
  127 |         os_migrate_conversion_host_post_content_hook: "{{ os_migrate_src_conversion_host_post_content_hook | default(false) }}"
  128 | 
  129 | - name: Set destination conversion host facts
  130 |   hosts: os_migrate_conv_dst
  131 |   environment:
  132 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
  133 |   any_errors_fatal: true
  134 |   tasks:
  135 |     - name: Set dst conversion host facts
  136 |       ansible.builtin.set_fact:
  137 |         os_migrate_conversion_host_pre_content_hook: "{{ os_migrate_dst_conversion_host_pre_content_hook | default(false) }}"
  138 |         os_migrate_conversion_host_post_content_hook: "{{ os_migrate_dst_conversion_host_post_content_hook | default(false) }}"
  139 | 
  140 | - name: Reboot source conversion host
  141 |   hosts: migrator
  142 |   environment:
  143 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
  144 |   any_errors_fatal: true
  145 |   tasks:
  146 |     - name: Reboot the src conversion host if required
  147 |       ansible.builtin.include_role:
  148 |         name: os_migrate.os_migrate.conversion_host
  149 |         tasks_from: reboot.yml
  150 |       vars:
  151 |         os_migrate_conversion_host_name: "{{ os_migrate_src_conversion_host_name }}"
  152 |         os_migrate_conversion_cloud: src
  153 |         os_migrate_conversion_validate_certs: "{{ os_migrate_src_validate_certs | default(omit) }}"
  154 |         os_migrate_conversion_ca_cert: "{{ os_migrate_src_ca_cert | default(omit) }}"
  155 |         os_migrate_conversion_client_cert: "{{ os_migrate_src_client_cert | default(omit) }}"
  156 |         os_migrate_conversion_client_key: "{{ os_migrate_src_client_key | default(omit) }}"
  157 |       when: os_migrate_reboot_conversion_hosts | default(false) | bool
  158 | 
  159 |     - name: Wait for src conversion host reachability
  160 |       ansible.builtin.wait_for:
  161 |         port: 22
  162 |         host: "{{ hostvars['os_migrate_conv_src']['ansible_ssh_host'] }}"
  163 |         search_regex: OpenSSH
  164 |         sleep: 5
  165 |         timeout: 600
  166 |       when: os_migrate_reboot_conversion_hosts | default(false) | bool
  167 | 
  168 | - name: Reboot destination conversion host
  169 |   hosts: migrator
  170 |   environment:
  171 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
  172 |   any_errors_fatal: true
  173 |   tasks:
  174 |     - name: Reboot the dst conversion host if required
  175 |       ansible.builtin.include_role:
  176 |         name: os_migrate.os_migrate.conversion_host
  177 |         tasks_from: reboot.yml
  178 |       vars:
  179 |         os_migrate_conversion_host_name: "{{ os_migrate_dst_conversion_host_name }}"
  180 |         os_migrate_conversion_cloud: dst
  181 |         os_migrate_conversion_validate_certs: "{{ os_migrate_dst_validate_certs | default(omit) }}"
  182 |         os_migrate_conversion_ca_cert: "{{ os_migrate_dst_ca_cert | default(omit) }}"
  183 |         os_migrate_conversion_client_cert: "{{ os_migrate_dst_client_cert | default(omit) }}"
  184 |         os_migrate_conversion_client_key: "{{ os_migrate_dst_client_key | default(omit) }}"
  185 |       when: os_migrate_reboot_conversion_hosts | default(false) | bool
  186 | 
  187 |     - name: Wait for dst conversion host reachability
  188 |       ansible.builtin.wait_for:
  189 |         port: 22
  190 |         host: "{{ hostvars['os_migrate_conv_dst']['ansible_ssh_host'] }}"
  191 |         search_regex: OpenSSH
  192 |         sleep: 5
  193 |         timeout: 600
  194 |       when: os_migrate_reboot_conversion_hosts | default(false) | bool
  195 | 
  196 | - name: Install conversion host content
  197 |   hosts: conversion_hosts
  198 |   environment:
  199 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
  200 |   any_errors_fatal: true
  201 |   tasks:
  202 |     - name: Install the conversion host content
  203 |       ansible.builtin.include_role:
  204 |         name: os_migrate.os_migrate.conversion_host_content
  205 |       when: os_migrate_conversion_host_content_install | default(true) | bool
  206 |   vars:
  207 |     ansible_become_user: root
  208 |     ansible_become: true
```

## Frozen tracked paths in the relevant role/scope

```text
.ansible-lint
.ansible-lint-ignore
.github/workflows/ansible-lint.yml
.github/workflows/ansible-test.yml
.github/workflows/build-aee.yml
.github/workflows/certification-checks.yml
.github/workflows/docs-build-pr.yml
.github/workflows/docs-build.yml
.github/workflows/import-galaxy.yml
.github/workflows/python-lint.yml
.gitignore
.pre-commit-config.yaml
.python-version
.ruff.toml
CHANGELOG.rst
CODEOWNERS
LICENSE
Makefile
README.md
aee/bindep.txt
aee/build.sh
aee/execution-environment.yml
aee/requirements.txt
aee/requirements.yml
bindep.txt
docs/src/.gitignore
docs/src/Makefile
docs/src/_exts/ansible-autodoc.py
docs/src/conf.py
docs/src/devel/README.rst
docs/src/devel/contributing-code.rst
docs/src/devel/contributing-docs.rst
docs/src/devel/contributing-general.rst
docs/src/devel/design.rst
docs/src/devel/dev-env-setup.rst
docs/src/devel/dev-env-vagrant-non-containerized.rst
docs/src/devel/releasing.rst
docs/src/images/plantuml/detached-volume-migration-data-flow.plantuml
docs/src/images/plantuml/pcm-birds-eye.plantuml
docs/src/images/plantuml/pre-workload-migration-data-flow.plantuml
docs/src/images/plantuml/pre-workload-migration-workflow.plantuml
docs/src/images/plantuml/workload-migration-data-flow.plantuml
docs/src/images/plantuml/workload-migration-sequence.plantuml
docs/src/images/plantuml/workload-migration-workflow.plantuml
docs/src/index.rst
docs/src/make.bat
docs/src/modules.rst
docs/src/modules/.gitkeep
docs/src/modules/module-auth_info.rst
docs/src/modules/module-export_detached_volume.rst
docs/src/modules/module-export_flavor.rst
docs/src/modules/module-export_image_blob.rst
docs/src/modules/module-export_image_meta.rst
docs/src/modules/module-export_keypair.rst
docs/src/modules/module-export_network.rst
docs/src/modules/module-export_project.rst
docs/src/modules/module-export_router.rst
docs/src/modules/module-export_router_interfaces.rst
docs/src/modules/module-export_security_group.rst
docs/src/modules/module-export_security_group_rules.rst
docs/src/modules/module-export_subnet.rst
docs/src/modules/module-export_user.rst
docs/src/modules/module-export_user_project_role_assignment.rst
docs/src/modules/module-export_workload.rst
docs/src/modules/module-import_flavor.rst
docs/src/modules/module-import_image.rst
docs/src/modules/module-import_keypair.rst
docs/src/modules/module-import_network.rst
docs/src/modules/module-import_project.rst
docs/src/modules/module-import_router.rst
docs/src/modules/module-import_router_interface.rst
docs/src/modules/module-import_security_group.rst
docs/src/modules/module-import_security_group_rule.rst
docs/src/modules/module-import_subnet.rst
docs/src/modules/module-import_user.rst
docs/src/modules/module-import_user_project_role_assignment.rst
docs/src/modules/module-import_volumes_export.rst
docs/src/modules/module-import_volumes_src_cleanup.rst
docs/src/modules/module-import_volumes_transfer.rst
docs/src/modules/module-import_workload_create_instance.rst
docs/src/modules/module-import_workload_dst_check.rst
docs/src/modules/module-import_workload_dst_failure_cleanup.rst
docs/src/modules/module-import_workload_export_volumes.rst
docs/src/modules/module-import_workload_prelim.rst
docs/src/modules/module-import_workload_src_check.rst
docs/src/modules/module-import_workload_src_cleanup.rst
docs/src/modules/module-import_workload_transfer_volumes.rst
docs/src/modules/module-os_conversion_host_info.rst
docs/src/modules/module-os_keypairs_info.rst
docs/src/modules/module-os_role_assignments_info.rst
docs/src/modules/module-os_routers_info.rst
docs/src/modules/module-os_security_groups_info.rst
docs/src/modules/module-read_resources.rst
docs/src/modules/module-validate_resource_files.rst
docs/src/roles.rst
docs/src/roles/.gitkeep
docs/src/roles/role-conversion_host.rst
docs/src/roles/role-conversion_host_content.rst
docs/src/roles/role-export_detached_volumes.rst
docs/src/roles/role-export_flavors.rst
docs/src/roles/role-export_images.rst
docs/src/roles/role-export_keypairs.rst
docs/src/roles/role-export_networks.rst
docs/src/roles/role-export_projects.rst
docs/src/roles/role-export_router_interfaces.rst
docs/src/roles/role-export_routers.rst
docs/src/roles/role-export_security_group_rules.rst
docs/src/roles/role-export_security_groups.rst
docs/src/roles/role-export_subnets.rst
docs/src/roles/role-export_user_project_role_assignment.rst
docs/src/roles/role-export_users.rst
docs/src/roles/role-export_users_keypairs.rst
docs/src/roles/role-export_workloads.rst
docs/src/roles/role-import_detached_volumes.rst
docs/src/roles/role-import_flavors.rst
docs/src/roles/role-import_from_hypervisor.rst
docs/src/roles/role-import_images.rst
docs/src/roles/role-import_keypairs.rst
docs/src/roles/role-import_networks.rst
docs/src/roles/role-import_projects.rst
[listing truncated after 120 paths]
```

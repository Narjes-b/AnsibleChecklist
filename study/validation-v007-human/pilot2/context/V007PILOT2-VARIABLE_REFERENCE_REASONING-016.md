# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-016

- Repository: `os-migrate/os-migrate`
- Commit: `60e4123dd2391233d23149d7dfb6ebe4b0870590`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `playbooks/export_images.yml` (reported anchor line 4)
- Flagged construct: variable `os_migrate_data_dir`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–6 of 6:

```text
    1 | - name: Export images
    2 |   hosts: migrator
    3 |   environment:
    4 |     OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
    5 |   roles:
    6 |     - os_migrate.os_migrate.export_images
```

## Visible variable references

```text
Whole-word search for `os_migrate_data_dir`: 182 matches in 133 files; 0 look like definitions (key assignment, register, set_fact) and are listed first.
No definition-like match (key assignment, register, set_fact) found.

Other references:
playbooks/delete_conversion_hosts.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/delete_conversion_hosts.yml:19:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/delete_conversion_hosts.yml:30:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:82:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:94:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:106:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:121:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:132:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:143:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:171:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/deploy_conversion_hosts.yml:199:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_detached_volumes.yml:5:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_flavors.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_images.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_keypairs.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_networks.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_projects.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_router_interfaces.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_routers.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_security_group_rules.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_security_groups.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_subnets.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_user_project_role_assignments.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_users.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_users_keypairs.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/export_workloads.yml:5:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_detached_volumes.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_flavors.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_from_hypervisor.yml:7:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_images.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_keypairs.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_networks.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_projects.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_router_interfaces.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_routers.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_security_group_rules.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_security_groups.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_subnets.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_user_project_role_assignments.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_users.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_users_keypairs.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
playbooks/import_workloads.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
roles/conversion_host/defaults/main.yml:32:os_migrate_conversion_keypair_private_path: "{{ os_migrate_data_dir }}/conversion/ssh.key"
roles/conversion_host/defaults/main.yml:33:os_migrate_conversion_link_keypair_private_path: "{{ os_migrate_data_dir }}/conversion/link-ssh.key"
roles/conversion_host_content/defaults/main.yml:23:os_migrate_conversion_link_keypair_private_path: "{{ os_migrate_data_dir }}/conversion/link-ssh.key"
roles/export_detached_volumes/tasks/main.yml:20:    path: "{{ os_migrate_data_dir }}/detached_volumes.yml"
roles/export_flavors/tasks/main.yml:26:    path: "{{ os_migrate_data_dir }}/flavors.yml"
roles/export_images/defaults/main.yml:2:os_migrate_image_blobs_dir: "{{ os_migrate_data_dir }}/image_blobs"
roles/export_images/tasks/main.yml:37:    path: "{{ os_migrate_data_dir }}/images.yml"
roles/export_keypairs/tasks/main.yml:26:    path: "{{ os_migrate_data_dir }}/keypairs.yml"
roles/export_networks/tasks/main.yml:27:    path: "{{ os_migrate_data_dir }}/networks.yml"
roles/export_projects/tasks/main.yml:26:    path: "{{ os_migrate_data_dir }}/projects.yml"
roles/export_router_interfaces/tasks/main.yml:27:    path: "{{ os_migrate_data_dir }}/router_interfaces.yml"
roles/export_routers/tasks/main.yml:26:    path: "{{ os_migrate_data_dir }}/routers.yml"
roles/export_security_group_rules/tasks/main.yml:28:    path: "{{ os_migrate_data_dir }}/security_group_rules.yml"
roles/export_security_groups/tasks/main.yml:25:    path: "{{ os_migrate_data_dir }}/security_groups.yml"
roles/export_subnets/tasks/main.yml:27:    path: "{{ os_migrate_data_dir }}/subnets.yml"
roles/export_user_project_role_assignments/tasks/main.yml:45:    path: "{{ os_migrate_data_dir }}/user_project_role_assignments.yml"
roles/export_users/tasks/main.yml:25:    path: "{{ os_migrate_data_dir }}/users.yml"
roles/export_users_keypairs/tasks/export_single_user_keypairs.yml:27:    path: "{{ os_migrate_data_dir }}/users_keypairs.yml"
roles/export_workloads/tasks/main.yml:25:    path: "{{ os_migrate_data_dir }}/workloads.yml"
roles/import_detached_volumes/defaults/main.yml:1:os_migrate_conversion_keypair_private_path: "{{ os_migrate_data_dir }}/conversion/ssh.key"
roles/import_detached_volumes/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/detached_volumes.yml"
roles/import_detached_volumes/tasks/import_volumes.yml:3:    file: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
roles/import_detached_volumes/tasks/import_volumes.yml:18:    log_dir: "{{ os_migrate_data_dir }}/volume_logs"
roles/import_detached_volumes/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/detached_volumes.yml"
roles/import_detached_volumes/tasks/main.yml:20:    path: "{{ os_migrate_data_dir }}/volume_logs"
roles/import_flavors/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/flavors.yml"
roles/import_flavors/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/flavors.yml"
roles/import_from_hypervisor/tasks/main.yml:7:    src: "{{ os_migrate_data_dir }}/workloads.yml"
roles/import_from_hypervisor/tasks/workload.yml:80:    path: "{{ os_migrate_data_dir }}/workloads.yml"
roles/import_images/defaults/main.yml:1:os_migrate_image_blobs_dir: "{{ os_migrate_data_dir }}/image_blobs"
roles/import_images/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/images.yml"
roles/import_images/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/images.yml"
roles/import_keypairs/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/keypairs.yml"
roles/import_keypairs/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/keypairs.yml"
roles/import_networks/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/networks.yml"
roles/import_networks/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/networks.yml"
roles/import_projects/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/projects.yml"
roles/import_projects/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/projects.yml"
roles/import_router_interfaces/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/router_interfaces.yml"
roles/import_router_interfaces/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/router_interfaces.yml"
roles/import_routers/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/routers.yml"
roles/import_routers/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/routers.yml"
roles/import_security_group_rules/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/security_group_rules.yml"
roles/import_security_group_rules/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/security_group_rules.yml"
roles/import_security_groups/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/security_groups.yml"
roles/import_security_groups/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/security_groups.yml"
roles/import_subnets/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/subnets.yml"
roles/import_subnets/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/subnets.yml"
roles/import_user_project_role_assignments/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/user_project_role_assignments.yml"
roles/import_users/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/users.yml"
roles/import_users/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/users.yml"
roles/import_users_keypairs/meta/main.yml:19:        - "{{ os_migrate_data_dir }}/users_keypairs.yml"
roles/import_users_keypairs/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/users_keypairs.yml"
roles/import_workloads/defaults/main.yml:1:os_migrate_conversion_keypair_private_path: "{{ os_migrate_data_dir }}/conversion/ssh.key"
roles/import_workloads/meta/main.yml:20:        - "{{ os_migrate_data_dir }}/workloads.yml"
roles/import_workloads/tasks/main.yml:3:    path: "{{ os_migrate_data_dir }}/workloads.yml"
roles/import_workloads/tasks/main.yml:20:    path: "{{ os_migrate_data_dir }}/workload_logs"
roles/import_workloads/tasks/workload.yml:13:        log_dir: "{{ os_migrate_data_dir }}/workload_logs"
roles/import_workloads/tasks/workload.yml:69:        file: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
roles/prelude_common/tasks/main.yml:54:    dest: "{{ os_migrate_clouds_path | default(os_migrate_data_dir ~ '/clouds.yaml') }}"
roles/validate_data_dir/tasks/main.yml:4:      - "{{ os_migrate_data_dir }}"
tests/e2e/tasks/common/prep.yml:2:- name: delete os_migrate_data_dir
tests/e2e/tasks/common/prep.yml:4:    path: "{{ os_migrate_data_dir }}"
tests/e2e/tasks/common/prep.yml:19:- name: create os_migrate_data_dir
tests/e2e/tasks/common/prep.yml:21:    path: "{{ os_migrate_data_dir }}"
tests/e2e/tasks/tenant/clean_pre_workload.yml:3:    path: "{{ os_migrate_data_dir }}/{{ item }}"
tests/e2e/tasks/tenant/clean_workload.yml:3:    path: "{{ os_migrate_data_dir }}/{{ item }}"
tests/e2e/tasks/tenant/run_pre_workload.yml:23:                               os_migrate_data_dir +
tests/e2e/tasks/tenant/run_pre_workload.yml:55:                                      os_migrate_data_dir +
tests/e2e/tasks/tenant/run_pre_workload.yml:83:                                              os_migrate_data_dir +
tests/e2e/tasks/tenant/run_pre_workload.yml:112:                                               os_migrate_data_dir +
tests/e2e/tasks/tenant/run_pre_workload.yml:145:                                      os_migrate_data_dir +
tests/e2e/tasks/tenant/run_pre_workload.yml:177:                                         os_migrate_data_dir +
tests/e2e/tasks/tenant/run_pre_workload.yml:205:                               os_migrate_data_dir +
tests/e2e/tasks/tenant/run_workload.yml:30:        path: "{{ os_migrate_data_dir }}/workloads.yml"
tests/e2e/tasks/tenant/run_workload.yml:37:        path: "{{ os_migrate_data_dir }}/workloads.yml"
tests/e2e/tasks/tenant/run_workload.yml:44:        path: "{{ os_migrate_data_dir }}/workloads.yml"
tests/e2e/tasks/tenant/run_workload.yml:56:                               os_migrate_data_dir +
tests/e2e/tasks/tenant/run_workload_existing_fip.yml:26:    path: "{{ os_migrate_data_dir }}/workloads.yml"
tests/e2e/tasks/tenant/run_workload_existing_fip.yml:32:    path: "{{ os_migrate_data_dir }}/workloads.yml"
tests/e2e/test_as_tenant.yml:28:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path|default(os_migrate_data_dir ~ '/clouds.yaml') }}"
tests/func/tasks/admin/idempotence/flavor.yml:12:    path: "{{ os_migrate_data_dir }}/flavors.yml"
tests/func/tasks/admin/idempotence/flavor.yml:19:                                os_migrate_data_dir +
tests/func/tasks/admin/idempotence/project.yml:14:    path: "{{ os_migrate_data_dir }}/projects.yml"
tests/func/tasks/admin/idempotence/project.yml:21:                                os_migrate_data_dir +
tests/func/tasks/admin/idempotence/user.yml:14:    path: "{{ os_migrate_data_dir }}/users.yml"
tests/func/tasks/admin/idempotence/user.yml:20:    path: "{{ os_migrate_data_dir }}/users.yml"
tests/func/tasks/admin/idempotence/user.yml:26:    user_resources_idem: "{{ (lookup('file', os_migrate_data_dir + '/users.yml')
tests/func/tasks/admin/idempotence/user_keypair.yml:6:    path: "{{ os_migrate_data_dir }}/users_keypairs.yml"
tests/func/tasks/admin/idempotence/user_keypair.yml:21:    path: "{{ os_migrate_data_dir }}/users_keypairs.yml"
tests/func/tasks/admin/idempotence/user_keypair.yml:27:    path: "{{ os_migrate_data_dir }}/users_keypairs.yml"
tests/func/tasks/admin/idempotence/user_keypair.yml:34:                                os_migrate_data_dir +
tests/func/tasks/admin/idempotence/user_project_role_assignment.yml:14:    path: "{{ os_migrate_data_dir }}/user_project_role_assignments.yml"
tests/func/tasks/admin/idempotence/user_project_role_assignment.yml:20:    path: "{{ os_migrate_data_dir }}/user_project_role_assignments.yml"
tests/func/tasks/admin/idempotence/user_project_role_assignment.yml:27:                                os_migrate_data_dir +
tests/func/tasks/admin/run/flavor.yml:10:    path: "{{ os_migrate_data_dir }}/flavors.yml"
tests/func/tasks/admin/run/flavor.yml:17:                                  os_migrate_data_dir +
tests/func/tasks/admin/run/project.yml:17:    path: "{{ os_migrate_data_dir }}/projects.yml"
tests/func/tasks/admin/run/project.yml:24:                           os_migrate_data_dir +
tests/func/tasks/admin/run/user.yml:12:    path: "{{ os_migrate_data_dir }}/users.yml"
tests/func/tasks/admin/run/user.yml:18:    path: "{{ os_migrate_data_dir }}/users.yml"
tests/func/tasks/admin/run/user.yml:25:                           os_migrate_data_dir +
tests/func/tasks/admin/run/user_keypair.yml:12:    path: "{{ os_migrate_data_dir }}/users_keypairs.yml"
tests/func/tasks/admin/run/user_keypair.yml:18:    path: "{{ os_migrate_data_dir }}/users_keypairs.yml"
tests/func/tasks/admin/run/user_keypair.yml:25:                                  os_migrate_data_dir +
tests/func/tasks/admin/run/user_project_role_assignment.yml:10:    path: "{{ os_migrate_data_dir }}/user_project_role_assignments.yml"
tests/func/tasks/admin/run/user_project_role_assignment.yml:16:    path: "{{ os_migrate_data_dir }}/user_project_role_assignments.yml"
tests/func/tasks/admin/run/user_project_role_assignment.yml:23:                           os_migrate_data_dir +
tests/func/tasks/admin/update/project.yml:3:    path: "{{ os_migrate_data_dir }}/projects.yml"
tests/func/tasks/admin/update/user.yml:3:    path: "{{ os_migrate_data_dir }}/users.yml"
tests/func/tasks/global/prep.yml:2:- name: delete os_migrate_data_dir
tests/func/tasks/global/prep.yml:4:    path: "{{ os_migrate_data_dir }}"
tests/func/tasks/global/prep.yml:20:- name: create os_migrate_data_dir
tests/func/tasks/global/prep.yml:22:    path: "{{ os_migrate_data_dir }}"
tests/func/tasks/tenant/idempotence/image.yml:13:                                  os_migrate_data_dir +
tests/func/tasks/tenant/idempotence/keypair.yml:13:                                os_migrate_data_dir +
tests/func/tasks/tenant/idempotence/network.yml:13:                                os_migrate_data_dir +
tests/func/tasks/tenant/idempotence/router.yml:13:                                os_migrate_data_dir +
tests/func/tasks/tenant/idempotence/router_interface.yml:13:                                os_migrate_data_dir +
tests/func/tasks/tenant/idempotence/security_group.yml:13:                                   os_migrate_data_dir +
tests/func/tasks/tenant/idempotence/security_group_rule.yml:13:                                os_migrate_data_dir +
tests/func/tasks/tenant/idempotence/subnet.yml:13:                                os_migrate_data_dir +
tests/func/tasks/tenant/independent/validate_data_dir.yml:7:        -e "os_migrate_data_dir=$OS_MIGRATE_DATA" \
tests/func/tasks/tenant/independent/validate_data_dir.yml:19:        -e "os_migrate_data_dir=$OS_MIGRATE_DATA" \
tests/func/tasks/tenant/run/image.yml:16:                           os_migrate_data_dir +
tests/func/tasks/tenant/run/keypair.yml:8:                                  os_migrate_data_dir +
tests/func/tasks/tenant/run/network.yml:16:                           os_migrate_data_dir +
tests/func/tasks/tenant/run/router.yml:16:                                  os_migrate_data_dir +
tests/func/tasks/tenant/run/router_interface.yml:16:                                     os_migrate_data_dir +
tests/func/tasks/tenant/run/security_group.yml:16:                                          os_migrate_data_dir +
tests/func/tasks/tenant/run/security_group_rule.yml:16:                                               os_migrate_data_dir +
tests/func/tasks/tenant/run/subnet.yml:16:                                  os_migrate_data_dir +
tests/func/tasks/tenant/update/image.yml:3:    path: "{{ os_migrate_data_dir }}/images.yml"
tests/func/tasks/tenant/update/network.yml:3:    path: "{{ os_migrate_data_dir }}/networks.yml"
tests/func/tasks/tenant/update/router.yml:3:    path: "{{ os_migrate_data_dir }}/routers.yml"
tests/func/tasks/tenant/update/security_group.yml:3:    path: "{{ os_migrate_data_dir }}/security_groups.yml"
tests/func/tasks/tenant/update/subnet.yml:3:    path: "{{ os_migrate_data_dir }}/subnets.yml"
tests/func/test_as_admin.yml:4:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path|default(os_migrate_data_dir ~ '/clouds.yaml') }}"
tests/func/test_as_tenant.yml:12:    OS_CLIENT_CONFIG_FILE: "{{ os_migrate_clouds_path|default(os_migrate_data_dir ~ '/clouds.yaml') }}"
```

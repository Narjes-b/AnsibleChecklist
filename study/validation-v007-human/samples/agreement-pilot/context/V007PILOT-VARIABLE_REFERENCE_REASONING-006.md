# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-006

- Repository: `redhat-cop/aap_configuration_extended`
- Commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unnecessary-set-fact`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/object_diff/tasks/controller_notification_templates.yml` (reported anchor line 26)
- Object: `variable` `5bd2b3e6ba76201c588eedf9308920639874f7cc3b2f60386c189f49b3eced92`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–27 of 27:

```text
    1 | ---
    2 | - name: Get the organization ID
    3 |   ansible.builtin.set_fact:
    4 |     __controller_organization_id: "{{ lookup('ansible.platform.gateway_api', 'api/controller/' + controller_api_version + '/organizations',
    5 |                                              query_params={'name': orgs},
    6 |                                              host=aap_hostname, oauth_token=[REDACTED_LITERAL]
    7 |                                    }}"
    8 | 
    9 | - name: "Get the API list of all Notification Templates in Organization {{ orgs }}"
   10 |   ansible.builtin.set_fact:
   11 |     __controller_api_notification_templates: "{{ query('ansible.platform.gateway_api', 'api/controller/' + controller_api_version + '/notification_templates',
   12 |                                                        query_params={'organization': __controller_organization_id.id},
   13 |                                                        host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   14 |                                                        return_all=true, max_objects=query_controller_api_max_objects)
   15 |                                               }}"
   16 | 
   17 | - name: "Find the difference of Notification Template between what is on the Controller versus CasC on SCM"
   18 |   ansible.builtin.set_fact:
   19 |     __notification_templates_difference: "{{ query('infra.aap_configuration_extended.controller_object_diff',
   20 |                                                    api_list=__controller_api_notification_templates, compare_list=controller_notifications,
   21 |                                                    with_present=include_present_state, set_absent=true) | flatten
   22 |                                           }}"
   23 | 
   24 | - name: "Set notification_template's list to be configured"
   25 |   ansible.builtin.set_fact:
   26 |     controller_notifications: "{{ __notification_templates_difference }}"
   27 | ...
```

## Visible variable references

```text
b58344f735518744459c0501cf8971c0541f0caa:changelogs/fragments/issue13-object-diff-docs.yml:7:    entry ``var`` with ``controller_notifications``.
b58344f735518744459c0501cf8971c0541f0caa:playbooks/flatten_filetree_create_output.yaml:15:    filetree_controller_notifications: *filetree_create_output_dir
b58344f735518744459c0501cf8971c0541f0caa:playbooks/flatten_filetree_create_output.yaml:64:        - name: controller_notifications
b58344f735518744459c0501cf8971c0541f0caa:playbooks/flatten_filetree_create_output.yaml:65:          value: "{{ controller_notifications }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/aap_rules_validation/defaults/main.yml:49:  notification_templates: controller_notifications
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_create/defaults/main.yml:31:filetree_create_controller_notifications: "controller_notification_templates.d"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_create/tasks/controller_notification_templates.yml:56:        __task_name_append: "{{ filetree_create_controller_notifications }} output directory for notification templates in {{ output_path }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_create/tasks/controller_notification_templates.yml:57:        __path: "{{ output_path }}/{{ needed_path | regex_replace('/', '_') }}/{{ filetree_create_controller_notifications }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_create/tasks/controller_notification_templates.yml:73:        __dest: "{{ output_path }}/{{ (current_notification_templates_asset_value.summary_fields.organization.name | default(organization, true)) | regex_replace('/', '_') }}/{{ filetree_create_controller_notifications }}/{{ current_notification_templates_asset_value.name | regex_replace('/', '_') }}.yaml"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_create/templates/controller_notification_templates.j2:4:controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/defaults/main.yml:59:filetree_controller_notifications: "{{ dir_orgs_vars }}/{{ orgs }}/env/common/controller_notification_templates.d/"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/defaults/main.yml:117:  - {name: controller_notification_templates, var: controller_notifications, tags: [notification_templates, controller_notification_templates]}
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/meta/argument_specs.yml:96:      filetree_controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/apply_filetree_read_layout.yml:50:    filetree_controller_notifications: "{{ dir_orgs_vars }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:2:- name: "Get list of files inside {{ filetree_controller_notifications }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:4:    paths: "{{ filetree_controller_notifications }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:9:    contains: "controller_notifications:"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:12:  register: __list_files_controller_notifications
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:17:  loop: "{{ __list_files_controller_notifications.files }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:20:  register: __contents_filetree_controller_notifications
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:21:  failed_when: "'VARIABLE IS NOT DEFINED' in __contents_filetree_controller_notifications"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:25:    __populate_controller_notifications: "{{ (__populate_controller_notifications | default([])) + __populate_notifications_list_item.ansible_facts.controller_notifications }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:26:  loop: "{{ __contents_filetree_controller_notifications.results }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:31:    - __contents_filetree_controller_notifications is defined
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:32:    - __contents_filetree_controller_notifications.results is defined
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:33:    - __contents_filetree_controller_notifications.results | length > 0
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:34:    - __populate_notifications_list_item.ansible_facts.controller_notifications is defined
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:38:    controller_notifications: "{{ __populate_controller_notifications }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/filetree_read/tasks/controller_notification_templates.yml:40:  when: __populate_controller_notifications is defined
b58344f735518744459c0501cf8971c0541f0caa:roles/object_diff/defaults/main.yml:17:controller_notifications: []
b58344f735518744459c0501cf8971c0541f0caa:roles/object_diff/defaults/main.yml:46:  - {name: controller_notification_templates, var: controller_notifications, tags: controller_notification_templates}
b58344f735518744459c0501cf8971c0541f0caa:roles/object_diff/tasks/controller_notification_templates.yml:20:                                                   api_list=__controller_api_notification_templates, compare_list=controller_notifications,
b58344f735518744459c0501cf8971c0541f0caa:roles/object_diff/tasks/controller_notification_templates.yml:26:    controller_notifications: "{{ __notification_templates_difference }}"
b58344f735518744459c0501cf8971c0541f0caa:roles/object_diff/tests/vars.yaml:13:filetree_controller_notifications: *a
b58344f735518744459c0501cf8971c0541f0caa:roles/upgrade_config/tasks/common_item/common_item.yaml:55:    regex: '^controller_notifications:\s*$'
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/custom/notifications.yml:2:controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/fc/Default/notification_templates/Email notification differential.yaml:2:controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/fc/Default/notification_templates/Email notification.yaml:2:controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/fc/Satellite/notification_templates/irc-satqe-chat-notification.yaml:2:controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/gv/group_vars/all/notifications.yml:2:controller_notifications_all: []
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/gv/group_vars/dev/main.yml:14:controller_notifications: "{{ controller_notifications_all + controller_notifications_dev }}"
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/gv/group_vars/dev/notifications.yml:2:controller_notifications_dev: []
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/gv/group_vars/prod/main.yml:14:controller_notifications: "{{ controller_notifications_all + controller_notifications_prod }}"
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/gv/group_vars/prod/notifications.yml:2:controller_notifications_prod: []
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/roundtrip/notifications.yml:2:controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/roundtrip_extra_vars/extra_vars_read.yml:27:filetree_controller_notifications: /tmp/filetree_roundtrip_test/input
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/roundtrip_extra_vars/extra_vars_read_export.yml:28:filetree_controller_notifications: /tmp/filetree_output_default
b58344f735518744459c0501cf8971c0541f0caa:tests/configs/upgrade_configs/aap_24/notifications.yaml:2:controller_notifications:
b58344f735518744459c0501cf8971c0541f0caa:tests/test_filetree_read.yaml:60:    filetree_controller_notifications: *custom_configs_path
b58344f735518744459c0501cf8971c0541f0caa:tests/test_filetree_read.yaml:112:    filetree_controller_notifications: *roundtrip_configs_path
[reference search truncated after 50 matches]
```

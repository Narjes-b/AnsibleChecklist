# Frozen source context: V007PILOT-STYLE_POLICY-019

- Repository: `redhat-cop/infra.aap_configuration`
- Commit: `f84d6a61e4b18aa135d707fe539371587bc92931`
- Family: Style/policy
- Rule: `ansibleguard/molecule-test-absent`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/controller_instance_groups/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `7c652d4af84909ed4ced65c592557b6b48039c818e67af97c5e3592dea550bc2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–101 of 101:

```text
    1 | ---
    2 | - name: Manage Controller Instance Groups Block
    3 |   vars:
    4 |     ansible_async_dir: "{{ aap_configuration_async_dir }}"
    5 |   no_log: "{{ controller_configuration_instance_groups_secure_logging }}"
    6 |   block:
    7 |     - name: Managing Controller Instance Groups
    8 |       ansible.controller.instance_group:
    9 |         name: "{{ __controller_instance_group_item.name | mandatory }}"
   10 |         new_name: "{{ __controller_instance_group_item.new_name | default(omit, true) }}"
   11 |         credential: "{{ __controller_instance_group_item.credential | default(('' if controller_configuration_instance_groups_enforce_defaults else omit), true) }}"
   12 |         is_container_group: "{{ __controller_instance_group_item.is_container_group | default((false if controller_configuration_instance_groups_enforce_defaults else omit), true) }}"
   13 |         policy_instance_percentage: "{{ __controller_instance_group_item.policy_instance_percentage | default(0, true) if __controller_instance_group_item.policy_instance_percentage is defined or controller_configuration_instance_groups_enforce_defaults else omit }}"
   14 |         policy_instance_minimum: "{{ __controller_instance_group_item.policy_instance_minimum | default(0, true) if __controller_instance_group_item.policy_instance_minimum is defined or controller_configuration_instance_groups_enforce_defaults else omit }}"
   15 |         policy_instance_list: "{{ __controller_instance_group_item.policy_instance_list | default(([] if controller_configuration_instance_groups_enforce_defaults else omit), true) }}"
   16 |         max_concurrent_jobs: "{{ __controller_instance_group_item.max_concurrent_jobs | default(0, true) if __controller_instance_group_item.max_concurrent_jobs is defined or controller_configuration_instance_groups_enforce_defaults else omit }}"
   17 |         max_forks: "{{ __controller_instance_group_item.max_forks | default(0, true) if __controller_instance_group_item.max_forks is defined or controller_configuration_instance_groups_enforce_defaults else omit }}"
   18 |         pod_spec_override: "{{ __controller_instance_group_item.pod_spec_override | default(('' if controller_configuration_instance_groups_enforce_defaults else omit), true) }}"
   19 |         instances: "{{ __controller_instance_group_item.instances | default(([] if controller_configuration_instance_groups_enforce_defaults else omit), true) }}"
   20 |         state: "{{ __controller_instance_group_item.state | default(platform_state | default('present')) }}"
   21 | 
   22 |         # Role Standard Options
   23 |         controller_username: "{{ aap_username | default(omit, true) }}"
   24 |         controller_password: "{{ aap_password | default(omit, true) }}"
   25 |         controller_oauthtoken: "{{ aap_token | default(omit, true) }}"
   26 |         request_timeout: "{{ aap_request_timeout | default(10, true) }}"
   27 |         controller_host: "{{ aap_hostname | default(omit, true) }}"
   28 |         validate_certs: "{{ aap_validate_certs | default(omit) }}"
   29 |       loop: "{{ controller_instance_groups }}"
   30 |       loop_control:
   31 |         loop_var: __controller_instance_group_item
   32 |         label: "{{ __operation.verb }} Controller Instance Group {{ __controller_instance_group_item.name }}"
   33 |         pause: "{{ controller_configuration_instance_groups_loop_delay }}"
   34 |       when: controller_instance_groups is defined
   35 |       async: "{{ ansible_check_mode | ternary(0, 1000) }}"
   36 |       poll: 0
   37 |       register: __instance_groups_job_async
   38 |       changed_when: (__instance_groups_job_async.changed if ansible_check_mode else false)
   39 |       vars:
   40 |         __operation: "{{ operation_translate[__controller_instance_group_item.state | default(platform_state) | default('present')] }}"
   41 | 
   42 |     - name: Flag for errors (check mode only)
   43 |       ansible.builtin.set_fact:
   44 |         error_flag: true
   45 |       when: ansible_check_mode and __instance_groups_job_async.failed is defined and __instance_groups_job_async.failed
   46 | 
   47 |     - name: Managing Controller Instance Groups | Wait for finish the instance groups management
   48 |       when:
   49 |         - not ansible_check_mode
   50 |         - __instance_groups_job_async_results_item.ansible_job_id is defined
   51 |       ansible.builtin.include_role:
   52 |         name: infra.aap_configuration.collect_async_status
   53 |       loop: "{{ __instance_groups_job_async.results }}"
   54 |       loop_control:
   55 |         loop_var: __instance_groups_job_async_results_item
   56 |         label: "{{ __operation.verb }} Controller instance group {{ __instance_groups_job_async_results_item.__controller_instance_group_item.name }} | Wait for finish
   57 |           the instance groups {{ __operation.action }}"
   58 |       vars:
   59 |         cas_secure_logging: "{{ controller_configuration_instance_groups_secure_logging }}"
   60 |         cas_async_delay: "{{ controller_configuration_instance_groups_async_delay }}"
   61 |         cas_async_retries: "{{ controller_configuration_instance_groups_async_retries }}"
   62 |         cas_job_async_results_item: "{{ __instance_groups_job_async_results_item }}"
   63 |         cas_register_subvar: controller_instance_groups
   64 |         cas_error_list_var_name: "controller_instance_groups_errors"
   65 |         __operation: "{{ operation_translate[__instance_groups_job_async_results_item.__controller_instance_group_item.state | default(platform_state) | default('present')] }}"
   66 |         cas_object_label: "{{ __operation.verb }} Controller instance group {{ __instance_groups_job_async_results_item.__controller_instance_group_item.name }} | Wait for finish the instance groups {{ __operation.action }}"
   67 | 
   68 |   always:
   69 |     - name: Cleanup async results files
   70 |       when:
   71 |         - not ansible_check_mode
   72 |         - __instance_groups_job_async_results_item.ansible_job_id is defined
   73 |       ansible.builtin.async_status:
   74 |         jid: "{{ __instance_groups_job_async_results_item.ansible_job_id }}"
   75 |         mode: cleanup
   76 |       loop: "{{ __instance_groups_job_async.results }}"
   77 |       loop_control:
   78 |         loop_var: __instance_groups_job_async_results_item
   79 |         label: "Cleaning up job results file: {{ __instance_groups_job_async_results_item.results_file | default('Unknown') }}"
   80 | 
   81 | - name: Add roles to instance groups
   82 |   ansible.builtin.include_role:
   83 |     name: infra.aap_configuration.controller_roles
   84 |   when: aap_configuration_apply_object_roles
   85 |   vars:
   86 |     controller_roles: "{{ _controller_roles | from_yaml | default([], true) | list }}"
   87 |     _item_list: "{{ controller_instance_groups }}"
   88 |     _failed_items: "{{ aap_configuration_role_errors['controller_instance_groups_errors'] | default([]) | map(attribute='name') | list }}"
   89 |     _controller_roles: |
   90 |       {% for _item in _item_list %}
   91 |       {% if (_item.roles is defined) and ((_item.state | default(platform_state | default('present'))) != 'absent') and (_item.name not in _failed_items) %}
   92 |       {% for _role in _item.roles.keys() %}
   93 |       - role: "{{ _role }}"
   94 |         instance_groups:
   95 |           - "{{ _item.new_name | default(_item.name) }}"
   96 |         teams: {{ _item.roles[_role].teams | default(omit) }}
   97 |         users: {{ _item.roles[_role].users | default(omit) }}
   98 |       {% endfor %}
   99 |       {% endif %}
  100 |       {% endfor %}
  101 | ...
```

# Frozen source context: V007PILOT-STYLE_POLICY-026

- Repository: `redhat-cop/aap_configuration_extended`
- Commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Family: Style/policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/filetree_create/tasks/controller_schedules.yml` (reported anchor line 9)
- Object: `source_location` `b52a13a1a3d8aa296a789b1b6b758e8f95ef5b6300d958730c01d1223c5e1dca`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–88 of 88:

```text
    1 | ---
    2 | - name: "Get current Schedules from the API"
    3 |   ansible.builtin.set_fact:
    4 |     schedules_lookvar: "{{ query('ansible.platform.gateway_api',
    5 |                                 (schedules_related_url if schedules_related_url is defined else 'api/controller/v2/schedules/'),
    6 |                                 query_params=(query_params | combine({'name': schedule_name} if schedule_name is defined and schedules_related_url is not defined else {},
    7 |                                   {'id': schedule_id} if schedule_id is defined and schedule_name is not defined and schedules_related_url is not defined else {},
    8 |                                   {'unified_job_template': unified_job_template_id} if unified_job_template_id is defined and schedules_related_url is not defined else {},
    9 |                                   {'unified_job_template__organization': organization_id} if organization_id is defined and schedule_name is not defined and schedule_id is not defined and unified_job_template_id is not defined and schedules_related_url is not defined else {})),
   10 |                                 host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   11 |                                 return_all=true, max_objects=query_controller_api_max_objects)
   12 |                        }}"
   13 |   vars:
   14 |     query_params: {}
   15 |   no_log: "{{ controller_configuration_filetree_create_secure_logging }}"
   16 | 
   17 | - name: "Block for to generate flatten output"
   18 |   when:
   19 |     - flatten_output is defined
   20 |     - flatten_output | bool
   21 |   vars:
   22 |     __dest: "{{ output_path }}/controller_schedules.yaml"
   23 |   block:
   24 |     - name: "Add current schedules to the controller_schedules flat file"
   25 |       ansible.builtin.blockinfile:
   26 |         create: true
   27 |         mode: "0644"
   28 |         insertafter: EOF
   29 |         path: "{{ __dest }}"
   30 |         marker: ""
   31 |         block: "{{ lookup('template', 'templates/controller_schedules.j2') }}"
   32 |       vars:
   33 |         label_id: "{{ current_schedules_asset_value.id }}"
   34 |         label_name: "{{ current_schedules_asset_value.name | regex_replace('/', '_') }}"
   35 |         query_credentials: "{{ query('ansible.platform.gateway_api', current_schedules_asset_value.related.credentials,
   36 |                      host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   37 |                      return_all=true, max_objects=query_controller_api_max_objects) if current_schedules_asset_value.related.credentials is defined else [] }}"
   38 |         query_instance_groups: "{{ query('ansible.platform.gateway_api', current_schedules_asset_value.related.instance_groups,
   39 |                      host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   40 |                      return_all=true, max_objects=query_controller_api_max_objects) if current_schedules_asset_value.related.instance_groups is defined else [] }}"
   41 |         query_labels: "{{ query('ansible.platform.gateway_api', current_schedules_asset_value.related.labels,
   42 |                      host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   43 |                      return_all=true, max_objects=query_controller_api_max_objects) if current_schedules_asset_value.related.labels is defined else [] }}"
   44 |         last_schedule: "{{ current_schedule_index == ((schedules_lookvar | length) - 1) }}"
   45 |       loop: "{{ schedules_lookvar }}"
   46 |       loop_control:
   47 |         index_var: current_schedule_index
   48 |         loop_var: current_schedules_asset_value
   49 |         label: "{{ __dest }}"
   50 | 
   51 |     - name: "Remove all the blank lines introduced by the last task"
   52 |       ansible.builtin.lineinfile:
   53 |         path: "{{ __dest }}"
   54 |         line: ''
   55 |         state: absent
   56 | 
   57 | - name: "Block for to generate the filetree_create normal output"
   58 |   when: flatten_output is not defined or not (flatten_output | bool)
   59 |   block:
   60 |     - name: "Create the controller_schedules output directory for schedules in {{ output_path }}"
   61 |       ansible.builtin.file:
   62 |         path: "{{ output_path }}/{{ filetree_create_controller_schedules }}"
   63 |         state: directory
   64 |         mode: '0755'
   65 | 
   66 |     - name: "Add current schedules to the controller_schedules output file in {{ output_path }}"
   67 |       ansible.builtin.template:
   68 |         src: "templates/controller_schedules.j2"
   69 |         dest: "{{ __dest }}"
   70 |         mode: '0644'
   71 |       vars:
   72 |         label_id: "{{ current_schedules_asset_value.id }}"
   73 |         label_name: "{{ current_schedules_asset_value.name | regex_replace('/', '_') }}"
   74 |         __dest: "{{ output_path }}/{{ filetree_create_controller_schedules }}/{{ (label_id ~ '_') if not (omit_id | default(false) | bool) else '' }}{{ label_name | regex_replace('/', '_') }}.yaml"
   75 |         query_credentials: "{{ query('ansible.platform.gateway_api', current_schedules_asset_value.related.credentials,
   76 |                      host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   77 |                      return_all=true, max_objects=query_controller_api_max_objects) if current_schedules_asset_value.related.credentials is defined else [] }}"
   78 |         query_instance_groups: "{{ query('ansible.platform.gateway_api', current_schedules_asset_value.related.instance_groups,
   79 |                      host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   80 |                      return_all=true, max_objects=query_controller_api_max_objects) if current_schedules_asset_value.related.instance_groups is defined else [] }}"
   81 |         query_labels: "{{ query('ansible.platform.gateway_api', current_schedules_asset_value.related.labels,
   82 |                      host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   83 |                      return_all=true, max_objects=query_controller_api_max_objects) if current_schedules_asset_value.related.labels is defined else [] }}"
   84 |       loop: "{{ schedules_lookvar }}"
   85 |       loop_control:
   86 |         loop_var: current_schedules_asset_value
   87 |         label: "{{ __dest }}"
   88 | ...
```

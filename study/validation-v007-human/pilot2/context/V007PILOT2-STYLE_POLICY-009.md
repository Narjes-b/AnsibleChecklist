# Frozen source context: V007PILOT2-STYLE_POLICY-009

- Repository: `redhat-cop/infra.aap_configuration`
- Commit: `f84d6a61e4b18aa135d707fe539371587bc92931`
- Family: style_policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/gateway_teams/tasks/main.yml` (reported anchor line 44)
- Flagged construct: not named by the finding; the anchor line 44 lies in the task at line 38, name `infra.aap_configuration.collect_async_status`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–67 of 67:

```text
    1 | ---
    2 | - name: Manage Gateway Teams Block
    3 |   vars:
    4 |     ansible_async_dir: "{{ aap_configuration_async_dir }}"
    5 |   no_log: "{{ gateway_teams_secure_logging }}"
    6 |   block:
    7 |     - name: Teams | Configuration
    8 |       ansible.platform.team:
    9 |         name: "{{ __gateway_teams_item.name | mandatory }}"
   10 |         new_name: "{{ __gateway_teams_item.new_name | default(omit) }}"
   11 |         description: "{{ __gateway_teams_item.description | default(omit) }}"
   12 |         organization: "{{ __gateway_teams_item.organization | default(omit) }}"
   13 |         new_organization: "{{ __gateway_teams_item.new_organization | default(omit) }}"
   14 |         state: "{{ __gateway_teams_item.state | default(platform_state | default(omit, true)) }}"
   15 | 
   16 |         # Role Standard Options
   17 |         gateway_hostname: "{{ aap_hostname | default(omit, true) }}"
   18 |         gateway_username: "{{ aap_username | default(omit, true) }}"
   19 |         gateway_password: "{{ aap_password | default(omit, true) }}"
   20 |         gateway_token: "{{ aap_token | default(omit, true) }}"
   21 |         gateway_request_timeout: "{{ aap_request_timeout | default(10, true) }}"
   22 |         gateway_validate_certs: "{{ aap_validate_certs | default(omit) }}"
   23 |       loop: "{{ aap_teams }}"
   24 |       loop_control:
   25 |         loop_var: __gateway_teams_item
   26 |         label: "{{ __operation.verb }} the Gateway team {{ __gateway_teams_item.name }}"
   27 |         pause: "{{ gateway_teams_loop_delay }}"
   28 |       async: 1000
   29 |       poll: 0
   30 |       register: __gateway_teams_job_async
   31 |       changed_when: false
   32 |       vars:
   33 |         __operation: "{{ operation_translate[__gateway_teams_item.state | default(platform_state) | default('present')] }}"
   34 | 
   35 |     - name: Teams | Wait for finish the configuration
   36 |       when:
   37 |         - not ansible_check_mode
   38 |         - __gateway_teams_job_async_results_item.ansible_job_id is defined
   39 |       ansible.builtin.include_role:
   40 |         name: infra.aap_configuration.collect_async_status
   41 |       loop: "{{ __gateway_teams_job_async.results }}"
   42 |       loop_control:
   43 |         loop_var: __gateway_teams_job_async_results_item
   44 |         label: "{{ __operation.verb }} Gateway team {{ __gateway_teams_job_async_results_item.__gateway_teams_item.name }} | Wait for finish the Gateway team {{ __operation.action }}"
   45 |       vars:
   46 |         cas_secure_logging: "{{ gateway_teams_secure_logging }}"
   47 |         cas_async_delay: "{{ gateway_teams_async_delay }}"
   48 |         cas_async_retries: "{{ gateway_teams_async_retries }}"
   49 |         cas_job_async_results_item: "{{ __gateway_teams_job_async_results_item }}"
   50 |         cas_register_subvar: gateway_teams
   51 |         cas_error_list_var_name: "gateway_teams_errors"
   52 |         __operation: "{{ operation_translate[__gateway_teams_job_async_results_item.__gateway_teams_item.state | default(platform_state) | default('present')] }}"
   53 |         cas_object_label: "{{ __operation.verb }} Gateway team {{ __gateway_teams_job_async_results_item.__gateway_teams_item.name }} | Wait for finish the Gateway team {{ __operation.action }}"
   54 | 
   55 |   always:
   56 |     - name: Cleanup async results files
   57 |       when:
   58 |         - not ansible_check_mode
   59 |         - __gateway_teams_job_async_results_item.ansible_job_id is defined
   60 |       ansible.builtin.async_status:
   61 |         jid: "{{ __gateway_teams_job_async_results_item.ansible_job_id }}"
   62 |         mode: cleanup
   63 |       loop: "{{ __gateway_teams_job_async.results }}"
   64 |       loop_control:
   65 |         loop_var: __gateway_teams_job_async_results_item
   66 |         label: "Cleaning up job results file: {{ __gateway_teams_job_async_results_item.results_file | default('Unknown') }}"
   67 | ...
```

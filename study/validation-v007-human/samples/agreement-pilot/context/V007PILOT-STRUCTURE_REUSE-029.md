# Frozen source context: V007PILOT-STRUCTURE_REUSE-029

- Repository: `mageops/ansible-infrastructure`
- Commit: `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`
- Family: Structure/reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/cs.aws-lambda-varnish/tasks/create-autoscaling-handler-lambda.yml` (reported anchor line 1)
- Object: `source_location` `8fc6a529543b0c3558329fded7c9794592093e3eff7354dc61f28fdfac5ef865`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–85 of 85:

```text
    1 | - name: Transform instance filters to format used in Lambda
    2 |   set_fact:
    3 |     varnish_instances_filter_lambda: "{{ varnish_instances_aws_tags | prefix_keys('tag:') | dict2items | map('json_query', _jq_map_ec2_instance_filter)|list }}"
    4 |     varnish_backend_instances_filter_lambda: "{{ varnish_backend_instances_aws_tags | prefix_keys('tag:')  | dict2items | map('json_query', _jq_map_ec2_instance_filter)|list }}"
    5 |     varnish_extra_instances_filter_lambda: "{{ varnish_extra_instances_aws_tags | prefix_keys('tag:') | dict2items | map('json_query', _jq_map_ec2_instance_filter)|list }}"
    6 |   vars:
    7 |     _jq_map_ec2_instance_filter: '{Name: key, Values: [value]}'
    8 | 
    9 | - name: Check if lambda function exists
   10 |   community.aws.lambda_info:
   11 |     region: "{{ aws_region }}"
   12 |   register: _lambda_facts
   13 | 
   14 | - name: Delete lambda function if it exists with different runtime
   15 |   lambda:
   16 |     name: "{{ aws_lambda_handle_varnish_autoscaling_event_name }}"
   17 |     state: absent
   18 |     region: "{{ aws_region }}"
   19 |   when: _lambda_facts.ansible_facts.lambda_facts.function[aws_lambda_handle_varnish_autoscaling_event_name] is defined and _lambda_facts.ansible_facts.lambda_facts.function[aws_lambda_handle_varnish_autoscaling_event_name].runtime != aws_lambda_varnish_runtime
   20 | 
   21 | # Why these workarounds exist:
   22 | # `amazon.aws.lambda` update path calls botocore waiter `FunctionActive` before applying updates.
   23 | # In our case AWS reports some idle VPC lambdas as `State=Inactive` (`StateReasonCode=Idle`).
   24 | # That waiter does not handle `Inactive` as a valid transition state, so it keeps polling until:
   25 | # "Waiter FunctionActive failed: Max attempts exceeded".
   26 | # Deleting and recreating the function forces create path (no failing pre-update waiter), which unblocks deploy.
   27 | 
   28 | 
   29 | - name: Register lambda handler for autoscaling event
   30 |   block:
   31 |     - name: Register lambda handler for autoscaling event
   32 |       lambda: &handle_varnish_autoscaling_event_lambda_args
   33 |         name: "{{ aws_lambda_handle_varnish_autoscaling_event_name }}"
   34 |         state: present
   35 |         zip_file: "{{ aws_lambda_varnish_deploy_package_path }}"
   36 |         runtime: "{{ aws_lambda_varnish_runtime }}"
   37 |         role: "arn:aws:iam::{{ aws_account_id }}:role/{{ aws_iam_role_autoscaling_event_lambda }}"
   38 |         handler: handle_autoscaling_event.handle
   39 |         region: "{{ aws_region }}"
   40 |         timeout: 120
   41 |         environment_variables:
   42 |             VARNISH_INSTANCE_FILTER: "{{ varnish_instances_filter_lambda | to_json }}"
   43 |             BACKEND_INSTANCE_FILTER: "{{ varnish_backend_instances_filter_lambda | to_json }}"
   44 |             EXTRA_INSTANCE_FILTER: "{{ varnish_extra_instances_filter_lambda | to_json }}"
   45 |             KEY_BUCKET: "{{ aws_lambda_update_varnish_vcl_function_s3_bucket_name }}"
   46 |             KEY_NAME: "{{ aws_lambda_update_varnish_vcl_function_ssh_key_name }}"
   47 |             SSH_USERNAME: "{{ varnish_manager_user }}"
   48 |             ASG_PREFIX: "{{ mageops_app_name }}"
   49 |             TERMINATE_HOOK: "{{ aws_app_node_webnodedown_hook_name }}"
   50 |             UPDATE_LAMBDA_NAME: "{{ aws_lambda_update_varnish_backends_name }}"
   51 |       register: handle_autoscaling_event_lambda
   52 |       until: handle_autoscaling_event_lambda is not failed
   53 |       retries: 3
   54 |       delay: 30
   55 |   rescue:
   56 |     - name: Recreate lambda handler for autoscaling event after deployment error
   57 |       block:
   58 |         - name: Delete lambda function before recreation
   59 |           lambda:
   60 |             name: "{{ aws_lambda_handle_varnish_autoscaling_event_name }}"
   61 |             state: absent
   62 |             region: "{{ aws_region }}"
   63 | 
   64 |         - name: Recreate lambda handler for autoscaling event
   65 |           lambda: *handle_varnish_autoscaling_event_lambda_args
   66 |           register: handle_autoscaling_event_lambda
   67 |           until: handle_autoscaling_event_lambda is not failed
   68 |           retries: 3
   69 |           delay: 30
   70 | 
   71 | - name: Register autoscaling trigger
   72 |   set_fact:
   73 |     varnish_autoscaling_trigger:
   74 |       id: "{{ aws_lambda_handle_varnish_autoscaling_event_name }}-target"
   75 |       arn: "{{ handle_autoscaling_event_lambda.configuration.function_arn }}"
   76 | 
   77 | - name: Append trigger to list
   78 |   set_fact:
   79 |     aws_autoscaling_triggers_list: "{{ aws_autoscaling_triggers_list + [varnish_autoscaling_trigger] }}"
   80 |     aws_autoscaling_lambda_functions_list: "{{ aws_autoscaling_lambda_functions_list + [aws_lambda_handle_varnish_autoscaling_event_name] }}"
   81 | 
   82 | 
   83 | - name: Require cs.aws-autoscaling-triggers finalizer
   84 |   set_fact:
   85 |     finalize_roles: "{{ finalize_roles + ['cs.aws-autoscaling-triggers'] }}"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/cs.aws-lambda-varnish/defaults/main.yml
roles/cs.aws-lambda-varnish/meta/main.yml
roles/cs.aws-lambda-varnish/tasks/create-autoscaling-handler-lambda.yml
roles/cs.aws-lambda-varnish/tasks/create-update-varnish-backends-lambda.yml
roles/cs.aws-lambda-varnish/tasks/main.yml
```

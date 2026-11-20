# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-021

- Repository: `CentOS-PaaS-SIG/linchpin`
- Commit: `0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f`
- Family: maintainability_complexity
- Rule: `ansibleguard/large-task`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `linchpin/provision/roles/azure/tasks/provisionVM.yml` (reported anchor line 11)
- Flagged construct: task `provisioning azure vm when not async`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–79 of 79:

```text
    1 | ---
    2 | - set_fact:
    3 |     network_interface_names: []
    4 |   when: network_interface_names is not defined
    5 | 
    6 | - set_fact:
    7 |     network_interface_names: res_def['network_interface_names']
    8 |   when: network_interface_names is defined
    9 | 
   10 | 
   11 | - name: "Provisioning Azure VM when not async"
   12 |   azure_rm_virtualmachine:
   13 |     ad_user: "{{ auth_var['user'] | default(omit) }}"
   14 |     password: "{{ auth_var['password'] | default(omit) }}"
   15 |     client_id: "{{ auth_var['client_id'] | default(omit) }}"
   16 |     tenant: "{{ auth_var['tenant'] | default(omit) }}"
   17 |     secret: "{{ auth_var['secret'] | default(omit) }}"
   18 |     subscription_id: "{{ auth_var['subscription_id'] | default(omit) }}"
   19 |     admin_username: "{{ res_def['vm_username'] | default('linchpin') }}"
   20 |     admin_password: "{{ res_def['vm_password'] | default('Linchpin!') }}"
   21 |     resource_group: "{{ res_def['resource_group'] | default(omit) }}"
   22 |     ssh_public_keys: "{{ssh_public_keys}}"
   23 |     vm_size: "{{ res_def['vm_size'] | default('Standard_DS1_v2') }}"
   24 |     name: "{{ nameOfvm | default(omit) }}"
   25 |     network_interface_names: "{{ network_interface_names }}"
   26 |     virtual_network_name: "{{res_def['virtual_network_name']|default(vn_name)}}"
   27 |     image: "{{ image | default(omit) }}"
   28 |     availability_set: "{{ res_def['availability_set'] | default(omit) }}"
   29 |     boot_diagnostics:
   30 |       enabled: true
   31 |   register: res_def_output
   32 |   when: not _async
   33 |   no_log: "{{ not debug_mode }}"
   34 | 
   35 | - name: "Append outputitem to topology_outputs"
   36 |   set_fact:
   37 |     topology_outputs_azure_vm: "{{ topology_outputs_azure_vm + [res_def_output.ansible_facts.azure_vm] }}"
   38 |   when: res_def_output['changed'] == true and not _async
   39 | 
   40 | - name: "Async:: Provisioning Azure VM"
   41 |   azure_rm_virtualmachine:
   42 |     ad_user: "{{ auth_var['user'] | default(omit) }}"
   43 |     password: "{{ auth_var['password'] | default(omit) }}"
   44 |     client_id: "{{ auth_var['client_id'] | default(omit) }}"
   45 |     tenant: "{{ auth_var['tenant'] | default(omit) }}"
   46 |     secret: "{{ auth_var['secret'] | default(omit) }}"
   47 |     subscription_id: "{{ auth_var['subscription_id'] | default(omit) }}"
   48 |     admin_username: "{{ res_def['vm_username'] | default('linchpin') }}"
   49 |     admin_password: "{{ res_def['vm_password'] | default('Linchpin!') }}"
   50 |     resource_group: "{{ res_def['resource_group'] | default(omit) }}"
   51 |     vm_size: "{{ res_def['vm_size'] | default('Standard_DS1_v2') }}"
   52 |     availability_set: "{{ res_def['availability_set'] | default(omit) }}"
   53 |     virtual_network_name: "{{res_def['virtual_network_name']|default(vn_name)}}"
   54 |     name: "{{  nameOfvm| default(omit) }}"
   55 |     image: "{{ image | default(omit) }}"
   56 |     boot_diagnostics:
   57 |       enabled: true
   58 |   async: "{{ async_timeout }}"
   59 |   poll: 0
   60 |   register: res_def_output
   61 |   when: _async
   62 |   no_log: "{{ not debug_mode }}"
   63 | 
   64 | 
   65 | - name: "Async:: Append outputitem to topology_outputs"
   66 |   set_fact:
   67 |     async_outputs_azure_vm: "{{ async_outputs_azure_vm + [res_def_output.ansible_facts.azure_vm] }}"
   68 |   when: _async
   69 | 
   70 | 
   71 | - name: "Add type to resource"
   72 |   set_fact:
   73 |     topology_outputs_azure_vm: "{{ topology_outputs_azure_vm | add_res_data(res_grp_type, res_def['role']) }}"
   74 | 
   75 | 
   76 | - name: "Async:: Add type to resource"
   77 |   set_fact:
   78 |     async_outputs_azure_vm: "{{ async_outputs_azure_vm | add_res_data(lookup('vars', 'role_name'), res_def['role']) }}"
   79 |   when: _async
```

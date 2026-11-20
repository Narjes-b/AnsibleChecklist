# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-019

- Repository: `CentOS-PaaS-SIG/linchpin`
- Commit: `0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `linchpin/provision/roles/ovirt/tasks/provision_ovirt_vms.yml` (reported anchor line 27)
- Flagged construct: variable `nics`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–136 of 136:

```text
    1 | - name: "Provision ovirt_disk resources"
    2 |   ovirt_disk:
    3 |     state: "{{ state }}"
    4 |     auth: "{{ ovirt_auth }}"
    5 |     name: "{{ ovirt_resource_name }}-{{ disk_item['name'] }}"
    6 |     size: "{{ disk_item['size'] }}"
    7 |     format: "{{ disk_item['format'] }}"
    8 |     storage_domain: "{{ disk_item['storage_domain'] }}"
    9 |     interface: "{{ disk_item['interface'] | default(omit) }}"
   10 |   with_items: "{{ res_def['disks'] | default([]) }}"
   11 |   loop_control:
   12 |     loop_var: disk_item
   13 |   register: disk
   14 | 
   15 | - name: "create disks variable"
   16 |   set_fact:
   17 |     disks: []
   18 | 
   19 | - name: "add results to disks"
   20 |   set_fact:
   21 |     disks: "{{ disks | default([]) }} +
   22 |             {{ [{ 'name': disks_item['disk']['alias'] }] }}"
   23 |   with_items: "{{ disk.results }}"
   24 |   loop_control:
   25 |     loop_var: disks_item
   26 | 
   27 | - name: "Provision/deprovision ovirt_vms resources"
   28 |   ovirt_vm:
   29 |     state: "{{ state }}"
   30 |     auth: "{{ ovirt_auth }}"
   31 |     name: "{{ ovirt_resource_name }}"
   32 |     template: "{{ res_def['template'] | default(omit) }}"
   33 |     cluster: "{{ res_def['cluster'] }}"
   34 |     memory: "{{ res_def['memory'] | default(omit) }}"
   35 |     cpu_cores: "{{ res_def['cpu_cores'] | default(omit) }}"
   36 |     cpu_shares: "{{ res_def['cpu_shares'] | default(omit) }}"
   37 |     cpu_sockets: "{{ res_def['cpu_sockets'] | default(omit) }}"
   38 |     memory_guaranteed: "{{ res_def['memory_guaranteed'] | default(omit) }}"
   39 |     high_availability: "{{ res_def['high_availability'] | default(omit) }}"
   40 |     cloud_init: "{{ res_def['cloud_init'] | default(omit) }}"
   41 |     host: "{{ res_def['host'] | default(omit) }}"
   42 |     cd_iso: "{{ res_def['cd_iso'] | default(omit) }}"
   43 |     type: "{{ res_def['type'] | default(omit) }}"
   44 |     operating_system: "{{ res_def['operating_system'] | default(omit) }}"
   45 |     disks: "{{ disks | default(omit) }}"
   46 |     nics: "{{ res_def['nics'] | default(omit) }}"
   47 |     fetch_nested: true
   48 |     nested_attributes: ips
   49 |   when: not _async
   50 | 
   51 | # If the machine isn't powered on and the guest agent has not reported the
   52 | # IP address fetch_nested will not be able to retrieve the nested_attributes:
   53 | # ips
   54 | # - After the machine has been created start the vm
   55 | # - Wait for an IPv4 address
   56 | # - Use ovirt_vms to fetch variables
   57 | 
   58 | - name: "Start Ovirt VMs"
   59 |   ovirt_vm:
   60 |     state: "running"
   61 |     auth: "{{ ovirt_auth }}"
   62 |     name: "{{ ovirt_resource_name }}"
   63 |   when: not _async
   64 | 
   65 | - name: Wait for IPv4 address
   66 |   ovirt_nic_facts:
   67 |     auth: "{{ ovirt_auth }}"
   68 |     vm: "{{ ovirt_resource_name }}"
   69 |     name: "nic1"
   70 |   register: nics
   71 |   when: not _async
   72 |   until:
   73 |     - ovirt_nics | length > 0
   74 |     - ovirt_nics[0].reported_devices | length > 0
   75 |     - ovirt_nics[0].reported_devices[0].ips |
   76 |       selectattr('version', 'match', 'v4') |
   77 |       list |
   78 |       length > 0
   79 |   retries: 12
   80 |   delay: 30
   81 | 
   82 | - name: "Retrieve Nested Attributes for Ovirt VM"
   83 |   ovirt_vm:
   84 |     state: "{{ state }}"
   85 |     auth: "{{ ovirt_auth }}"
   86 |     name: "{{ ovirt_resource_name }}"
   87 |     fetch_nested: true
   88 |     nested_attributes: ips
   89 |   when: not _async
   90 |   register: res_def_output
   91 | 
   92 | - name: "Append outputitem to topology_outputs"
   93 |   set_fact:
   94 |     topology_outputs_ovirt_vms: "{{ topology_outputs_ovirt_vms +
   95 |                                     [ res_def_output ] }}"
   96 |   when: not _async
   97 | 
   98 | - name: "Provision/deprovision ovirt_vms resources"
   99 |   ovirt_vm:
  100 |     state: "{{ state }}"
  101 |     auth: "{{ ovirt_auth }}"
  102 |     name: "{{ ovirt_resource_name }}"
  103 |     template: "{{ res_def['template'] | default(omit) }}"
  104 |     cluster: "{{ res_def['cluster'] }}"
  105 |     memory: "{{ res_def['memory'] | default(omit) }}"
  106 |     cpu_cores: "{{ res_def['cpu_cores'] | default(omit) }}"
  107 |     cpu_shares: "{{ res_def['cpu_shares'] | default(omit) }}"
  108 |     cpu_sockets: "{{ res_def['cpu_sockets'] | default(omit) }}"
  109 |     memory_guaranteed: "{{ res_def['memory_guaranteed'] | default(omit) }}"
  110 |     high_availability: "{{ res_def['high_availability'] | default(omit) }}"
  111 |     cloud_init: "{{ res_def['cloud_init'] | default(omit) }}"
  112 |     host: "{{ res_def['host'] | default(omit) }}"
  113 |     cd_iso: "{{ res_def['cd_iso'] | default(omit) }}"
  114 |     type: "{{ res_def['type'] | default(omit) }}"
  115 |     operating_system: "{{ res_def['operating_system'] | default(omit) }}"
  116 |     disks: "{{ disks | default(omit) }}"
  117 |     nics: "{{ res_def['nics'] | default(omit) }}"
  118 |     fetch_nested: true
  119 |     nested_attributes: ips
  120 |   when: _async
  121 |   async: "{{ async_timeout | default(1000) }}"
  122 |   poll: 0
  123 |   register: res_def_output
  124 | 
  125 | # following tasks saves the async job details
  126 | - name: "Async:: save the job id"
  127 |   set_fact:
  128 |     topology_outputs_ovirt_vms: "{{ topology_outputs_ovirt_vms +
  129 |                                     [ res_def_output ] }}"
  130 |   when: _async
  131 | 
  132 | - name: "Add type to resource"
  133 |   set_fact:
  134 |     topology_outputs_ovirt_vms: "{{ topology_outputs_ovirt_vms |
  135 |                                     add_res_data(res_grp_type,
  136 |                                                  res_def['role']) }}"
```

## Visible variable references

```text
Whole-word search for `nics`: 9 matches in 3 files; 9 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
linchpin/provision/roles/openstack/tasks/provision_os_server.yml:50:    nics: "{{ res_def['networks'] | default(None) | os_net }}"
linchpin/provision/roles/openstack/tasks/provision_os_server.yml:134:    nics: "{{ res_def['networks'] | default(None) | os_net }}"
linchpin/provision/roles/openstack/tasks/provision_os_server.yml:204:    nics: "{{ res_def['networks'] | default(None) | os_net }}"
linchpin/provision/roles/openstack/tasks/teardown_os_server.yml:69:    nics: "{{ res_def['networks'] | default(None) | os_net }}"
linchpin/provision/roles/openstack/tasks/teardown_os_server.yml:152:    nics: "{{ res_def['networks'] | default(None) | os_net }}"
linchpin/provision/roles/openstack/tasks/teardown_os_server.yml:222:    nics: "{{ res_def['networks'] | default(None) | os_net }}"
linchpin/provision/roles/ovirt/tasks/provision_ovirt_vms.yml:46:    nics: "{{ res_def['nics'] | default(omit) }}"
linchpin/provision/roles/ovirt/tasks/provision_ovirt_vms.yml:70:  register: nics
linchpin/provision/roles/ovirt/tasks/provision_ovirt_vms.yml:117:    nics: "{{ res_def['nics'] | default(omit) }}"

Other references:
```

# Frozen source context: V007PILOT-STYLE_POLICY-036

- Repository: `Kubeinit/kubeinit`
- Commit: `da6fec314d5594b6bd97ef2e4e71f9098a85e63c`
- Family: Style/policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `kubeinit/roles/kubeinit_prepare/tasks/prepare_groups.yml` (reported anchor line 171)
- Object: `source_location` `7abda4e1fc7f193031601daf2fd8c41c7c3f8120380ee3d616ec8be90bf4549c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–176 of 176:

```text
    1 | ---
    2 | # Copyright kubeinit contributors
    3 | # All Rights Reserved.
    4 | #
    5 | # Licensed under the Apache License, Version 2.0 (the "License"); you may
    6 | # not use this file except in compliance with the License. You may obtain
    7 | # a copy of the License at
    8 | #
    9 | #     http://www.apache.org/licenses/LICENSE-2.0
   10 | #
   11 | # Unless required by applicable law or agreed to in writing, software
   12 | # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
   13 | # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
   14 | # License for the specific language governing permissions and limitations
   15 | # under the License.
   16 | 
   17 | 
   18 | #
   19 | # Define additional groups we will use
   20 | #
   21 | - name: Add all controller nodes to the all_controller_nodes group
   22 |   ansible.builtin.add_host:
   23 |     name: "{{ item }}"
   24 |     guest_name: "{{ kubeinit_cluster_name }}-{{ item }}"
   25 |     group: all_controller_nodes
   26 |     fqdn: "{{ item }}.{{ kubeinit_cluster_fqdn }}"
   27 |     target: "{{ hostvars[item].target }}"
   28 |     os: "{{ hostvars[item].os }}"
   29 |   loop: "{{ groups['controller_nodes'][0:hostvars[kubeinit_cluster_name].controller_count|int] | default([]) | list }}"
   30 | 
   31 | - name: Add all compute nodes to the all_compute_nodes group
   32 |   ansible.builtin.add_host:
   33 |     name: "{{ item }}"
   34 |     guest_name: "{{ kubeinit_cluster_name }}-{{ item }}"
   35 |     group: all_compute_nodes
   36 |     fqdn: "{{ item }}.{{ kubeinit_cluster_fqdn }}"
   37 |     target: "{{ hostvars[item].target }}"
   38 |     os: "{{ hostvars[item].os }}"
   39 |   loop: "{{ groups['compute_nodes'][0:hostvars[kubeinit_cluster_name].compute_count|int] | default([]) | list }}"
   40 | 
   41 | - name: Add all controller and compute nodes to the all_cluster_nodes group
   42 |   ansible.builtin.add_host:
   43 |     name: "{{ item }}"
   44 |     group: all_cluster_nodes
   45 |     fqdn: "{{ hostvars[item].fqdn }}"
   46 |     target: "{{ hostvars[item].target }}"
   47 |     os: "{{ hostvars[item].os }}"
   48 |   loop: "{{ groups['all_controller_nodes'] + groups['all_compute_nodes'] | default([]) }}"
   49 | 
   50 | - name: Add any extra cluster vm guest nodes to the all_extra_nodes group
   51 |   ansible.builtin.add_host:
   52 |     name: "{{ item }}"
   53 |     guest_name: "{{ kubeinit_cluster_name }}-{{ item }}"
   54 |     group: all_extra_nodes
   55 |     fqdn: "{{ item }}.{{ kubeinit_cluster_fqdn }}"
   56 |     target: "{{ hostvars[item].target }}"
   57 |     os: "{{ hostvars[item].os }}"
   58 |     ram: "{{ hostvars[item].ram }}"
   59 |   loop: "{{ groups['extra_nodes'] | default([]) | list }}"
   60 |   when: kubeinit_cluster_distro in hostvars[item].when_distro
   61 | 
   62 | - name: Collect all cluster node hypervisors
   63 |   ansible.builtin.set_fact:
   64 |     all_cluster_hypervisors: "{{ all_cluster_hypervisors | default([]) | union([hostvars[item].target]) }}"
   65 |   loop: "{{ groups['all_cluster_nodes'] + (groups['all_extra_nodes'] | default([])) }}"
   66 | 
   67 | - name: Show the before and after values of the hypervisors fact
   68 |   ansible.builtin.debug:
   69 |     msg: "{{ groups['kubeinit_hypervisors'] }} ==> {{ all_cluster_hypervisors }}"
   70 | 
   71 | # TODO: check later to see if this would be a useful optimization
   72 | # - name: Set all cluster hypervisors fact
   73 | #   ansible.builtin.add_host:
   74 | #     name: "{{ kubeinit_cluster_name }}"
   75 | #     hypervisors: "{{ all_cluster_hypervisors }}"
   76 | 
   77 | - name: Add all service nodes to the all_service_nodes group
   78 |   ansible.builtin.add_host:
   79 |     name: "{{ item }}"
   80 |     guest_name: "{{ kubeinit_cluster_name }}-{{ item }}"
   81 |     group: all_service_nodes
   82 |     fqdn: "{{ item }}.{{ kubeinit_cluster_fqdn }}"
   83 |     services: "{{ hostvars[item].services }}"
   84 |     target: "{{ hostvars[item].target }}"
   85 |     os: "{{ hostvars[item].os }}"
   86 |     type: container
   87 |     container_host: "{{ hostvars[item].target }}"
   88 |   loop: "{{ groups['service_nodes'] | default([]) | list }}"
   89 | 
   90 | - name: Create tuples for each service and each service node providing that service
   91 |   ansible.builtin.set_fact:
   92 |     cluster_services: "{{ (cluster_services | default([])) + (item[0] | product([item[1]])) }}"
   93 |   loop: "{{ groups['all_service_nodes'] | map('extract', hostvars, 'services') | zip(groups['all_service_nodes']) }}"
   94 | 
   95 | - name: Combine those tuples into dict of services and nodes providing that service
   96 |   ansible.builtin.set_fact:
   97 |     cluster_services_dict: "{{ (cluster_services_dict | default({})) | combine({item[0]: cluster_services_dict[item[0]] | default([]) + [item[1]]}) }}"
   98 |   loop: "{{ cluster_services }}"
   99 | 
  100 | - name: Check for any services being provided on more than one service node
  101 |   ansible.builtin.fail:
  102 |     msg:
  103 |       "You are not currently permitted to run the same service on more than one service node."
  104 |   loop: "{{ cluster_services_dict | dict2items }}"
  105 |   when: item.value | length > 1
  106 | 
  107 | - name: Use first service node if there is no assigned provision service node
  108 |   ansible.builtin.set_fact:
  109 |     cluster_services_dict: "{{ cluster_services_dict | combine({'provision': [groups['all_service_nodes'][0]]}) }}"
  110 |   when: "'provision' not in cluster_services_dict"
  111 | 
  112 | - name: Flatten dictionary values into final form
  113 |   ansible.builtin.set_fact:
  114 |     all_cluster_services: "{{ (all_cluster_services | default({})) | combine({item.key: item.value[0]}) }}"
  115 |   loop: "{{ cluster_services_dict | dict2items | flatten }}"
  116 | 
  117 | - name: Set fact for cluster nameserver
  118 |   ansible.builtin.set_fact:
  119 |     kubeinit_cluster_nameserver: "{{ hostvars[all_cluster_services['bind']].ansible_host }}"
  120 |   when: "'bind' in all_cluster_services"
  121 | 
  122 | - name: Set all services cluster fact
  123 |   ansible.builtin.add_host:
  124 |     name: "{{ kubeinit_cluster_name }}"
  125 |     nameserver: "{{ kubeinit_cluster_nameserver | default(omit) }}"
  126 |     services: "{{ all_cluster_services }}"
  127 | 
  128 | - name: Add all service and cluster nodes to the all_nodes group
  129 |   ansible.builtin.add_host:
  130 |     name: "{{ item }}"
  131 |     group: all_nodes
  132 |     fqdn: "{{ hostvars[item].fqdn }}"
  133 |     os: "{{ hostvars[item].os }}"
  134 |   loop: "{{ groups['all_service_nodes'] + groups['all_cluster_nodes'] + (groups['all_extra_nodes'] | default([])) }}"
  135 | 
  136 | - name: Add all cluster hypervisors to the all_hosts group
  137 |   ansible.builtin.add_host:
  138 |     name: "{{ item }}"
  139 |     group: all_hosts
  140 |   loop: "{{ groups['kubeinit_hypervisors'] }}"
  141 |   when: >
  142 |     item in hostvars[kubeinit_ovn_central_host_name].target or
  143 |     item in groups['kubeinit_hypervisors']
  144 | 
  145 | - name: Add all hosts to the all_ovn_hosts group
  146 |   ansible.builtin.add_host:
  147 |     name: "{{ item }}"
  148 |     group: all_ovn_hosts
  149 |   loop: "{{ groups['all_hosts'] }}"
  150 | 
  151 | - name: Collect all of the localhost and hypervisor authorized keys into authorized_keys list
  152 |   ansible.builtin.set_fact:
  153 |     all_authorized_keys: "{{ (all_authorized_keys | default([])) | union([hostvars[item].authorized_key]) }}"
  154 |   loop: "{{ ['localhost'] | union(groups['all_hosts']) }}"
  155 | 
  156 | - name: Set all hypervisor authorized keys cluster fact
  157 |   ansible.builtin.add_host:
  158 |     name: "{{ kubeinit_cluster_name }}"
  159 |     authorized_keys: "{{ all_authorized_keys }}"
  160 | 
  161 | - name: Add services guest and cluster nodes to the all_guest_vms group
  162 |   ansible.builtin.add_host:
  163 |     name: "{{ item }}"
  164 |     group: all_guest_vms
  165 |   loop: "{{ groups['all_cluster_nodes'] + (groups['all_extra_nodes'] | default([])) }}"
  166 |   when: hostvars[item].type == 'virtual'
  167 | 
  168 | - name: Collect all of the node aliases
  169 |   ansible.builtin.set_fact:
  170 |     all_node_aliases: "{{ (all_node_aliases | default([])) + ([item[0]] | product(item) | list) }}"
  171 |   loop: "{{ groups['all_nodes'] | zip(groups['all_nodes'] | map('extract', hostvars, 'fqdn'), groups['all_nodes'] | map('extract', hostvars, 'ansible_host')) }}"
  172 | 
  173 | - name: Set all node aliases cluster fact
  174 |   ansible.builtin.add_host:
  175 |     name: "{{ kubeinit_cluster_name }}"
  176 |     node_aliases: "{{ all_node_aliases }}"
```

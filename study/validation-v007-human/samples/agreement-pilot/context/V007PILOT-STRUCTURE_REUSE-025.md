# Frozen source context: V007PILOT-STRUCTURE_REUSE-025

- Repository: `Kubeinit/kubeinit`
- Commit: `da6fec314d5594b6bd97ef2e4e71f9098a85e63c`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `kubeinit/roles/kubeinit_prepare/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `cedf33f17b6a7206ebc64011e983668ba0aed6009c126cad7ab85b2db4c9ebad`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–298 of 298:

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
   17 | - name: Gather hosts facts and stop the deployment if required
   18 |   block:
   19 |     - name: Gather hypervisor facts if needed
   20 |       ansible.builtin.include_tasks: prepare_hypervisors.yml
   21 |       vars:
   22 |         hypervisors_prepared: "{{ 'kubeinit_facts' in groups }}"
   23 |       when: not hypervisors_prepared
   24 | 
   25 |     - name: Add task-prepare-hypervisors to tasks_completed
   26 |       ansible.builtin.add_host:
   27 |         name: "kubeinit-facts"
   28 |         tasks_completed: "{{ hostvars['kubeinit-facts'].tasks_completed | union(['task-prepare-hypervisors']) }}"
   29 | 
   30 |     - name: Stop the deployment if required
   31 |       block:
   32 |         - name: Stop after 'task-prepare-hypervisors' when requested
   33 |           ansible.builtin.add_host:
   34 |             name: "kubeinit-facts"
   35 |             playbook_terminated: true
   36 |         - name: End play
   37 |           ansible.builtin.meta: end_play
   38 |       when: kubeinit_stop_after_task is defined and kubeinit_stop_after_task in hostvars['kubeinit-facts'].tasks_completed
   39 | 
   40 |     - name: Stop the deployment if required
   41 |       block:
   42 |         - name: "Stop before 'task-prepare-environment' when requested"
   43 |           ansible.builtin.add_host:
   44 |             name: "kubeinit-facts"
   45 |             playbook_terminated: true
   46 |         - name: End play
   47 |           ansible.builtin.meta: end_play
   48 |       when: kubeinit_stop_before_task is defined and kubeinit_stop_before_task == 'task-prepare-environment'
   49 |   tags: omit_from_grapher
   50 | 
   51 | - name: Define kubeinit_facts_hostvars
   52 |   ansible.builtin.set_fact:
   53 |     kubeinit_facts_hostvars: "{{ hostvars['kubeinit-facts'] }}"
   54 | 
   55 | #
   56 | # Setup bastion_host group
   57 | #
   58 | - name: Parse bastion_host_spec into a dictionary if defined
   59 |   ansible.builtin.set_fact:
   60 |     bastion_host_map: "{{ bastion_host_spec | from_yaml }}"
   61 |   when: bastion_host_spec is defined
   62 | 
   63 | - name: Assert bastion_host group and bastion_host_spec have same name when both defined
   64 |   ansible.builtin.assert:
   65 |     msg: "Cluster bastion host from inventory and command-line specification must match."
   66 |     that: bastion_host_map['host'] == groups['bastion_host'][0]
   67 |   when: bastion_host_map['host'] | default('') | length > 0 and groups['bastion_host'][0] | default('') | length > 0
   68 | 
   69 | - name: Define kubeinit_bastion_host_name
   70 |   ansible.builtin.set_fact:
   71 |     kubeinit_bastion_host_name: "{{ groups['bastion_host'][0] | default(bastion_host_map['host']) | default('bastion') }}"
   72 | 
   73 | - name: Assert bastion_host group does not have both target and ansible_host keys
   74 |   ansible.builtin.assert:
   75 |     msg: "The bastion_host group cannot have both target and ansible_host keys."
   76 |     that: hostvars[kubeinit_bastion_host_name]['target'] is not defined or hostvars[kubeinit_bastion_host_name]['ansible_host'] is not defined
   77 |   when: hostvars[kubeinit_bastion_host_name] is defined
   78 | 
   79 | - name: Define default bastion target and ansible_host from group target
   80 |   ansible.builtin.set_fact:
   81 |     default_bastion_target: "{{ hostvars[kubeinit_bastion_host_name].target }}"
   82 |     default_ansible_host: "{{ hostvars[hostvars[kubeinit_bastion_host_name].target].ansible_host }}"
   83 |   when: hostvars[kubeinit_bastion_host_name].target | default('') | length > 0
   84 | 
   85 | - name: Define default bastion target and ansible_host from group ansible_host
   86 |   ansible.builtin.set_fact:
   87 |     default_bastion_target: "{{ kubeinit_bastion_host_name }}"
   88 |     default_ansible_host: "{{ hostvars[kubeinit_bastion_host_name].ansible_host }}"
   89 |   when: hostvars[kubeinit_bastion_host_name].ansible_host | default('') | length > 0
   90 | 
   91 | - name: Assert bastion_host_spec does not have both target and ansible_host keys
   92 |   ansible.builtin.assert:
   93 |     msg: "The bastion_host_spec cannot have both target and ansible_host keys."
   94 |     that: bastion_host_map['target'] is not defined or bastion_host_map['ansible_host'] is not defined
   95 |   when: bastion_host_map is defined
   96 | 
   97 | - name: Define default bastion target and ansible_host from spec target
   98 |   ansible.builtin.set_fact:
   99 |     default_bastion_target: "{{ bastion_host_map['target'] }}"
  100 |     default_ansible_host: "{{ hostvars[bastion_host_map['target']].ansible_host }}"
  101 |   when: bastion_host_map['target'] | default('') | length > 0
  102 | 
  103 | - name: Define default bastion target and ansible_host from spec ansible_host
  104 |   ansible.builtin.set_fact:
  105 |     default_bastion_target: "{{ kubeinit_bastion_host_name }}"
  106 |     default_ansible_host: "{{ bastion_host_map['ansible_host'] }}"
  107 |   when: bastion_host_map['ansible_host'] | default('') | length > 0
  108 | 
  109 | - name: Use the first hypervisor if neither bastion host spec or group defines a target or ansible_host
  110 |   ansible.builtin.add_host:
  111 |     name: "{{ kubeinit_bastion_host_name }}"
  112 |     group: 'bastion_host'
  113 |     target: "{{ default_bastion_target | default(groups['kubeinit_hypervisors'] | first) }}"
  114 |     ansible_host: "{{ default_ansible_host | default(hostvars[groups['kubeinit_hypervisors'] | first].ansible_host) }}"
  115 | 
  116 | #
  117 | # Setup ovn_central_host group
  118 | #
  119 | - name: Parse ovn_central_host_spec into a dictionary if defined
  120 |   ansible.builtin.set_fact:
  121 |     ovn_central_host_map: "{{ ovn_central_host_spec | from_yaml }}"
  122 |   when: ovn_central_host_spec is defined
  123 | 
  124 | - name: Assert ovn_central_host group and ovn_central_host_spec have same name when both defined
  125 |   ansible.builtin.assert:
  126 |     msg: "Cluster ovn-central host from inventory and command-line specification must match."
  127 |     that: ovn_central_host_map['host'] == groups['ovn_central_host'][0]
  128 |   when: ovn_central_host_map['host'] | default('') | length > 0 and groups['ovn_central_host'][0] | default('') | length > 0
  129 | 
  130 | - name: Define kubeinit_ovn_central_host_name
  131 |   ansible.builtin.set_fact:
  132 |     kubeinit_ovn_central_host_name: "{{ groups['ovn_central_host'][0] | default(ovn_central_host_map['host']) | default('ovn-central') }}"
  133 | 
  134 | - name: Define default ovn-central target and ansible_host from group target
  135 |   ansible.builtin.set_fact:
  136 |     default_ovn_central_target: "{{ hostvars[kubeinit_ovn_central_host_name].target }}"
  137 |   when: hostvars[kubeinit_ovn_central_host_name].target | default('') | length > 0
  138 | 
  139 | - name: Define default ovn-central target and ansible_host from spec target
  140 |   ansible.builtin.set_fact:
  141 |     default_ovn_central_target: "{{ ovn_central_host_map['target'] }}"
  142 |   when: ovn_central_host_map['target'] | default('') | length > 0
  143 | 
  144 | - name: Use the first hypervisor if neither ovn-central host spec or group defines a target
  145 |   ansible.builtin.add_host:
  146 |     name: "{{ kubeinit_ovn_central_host_name }}"
  147 |     group: 'ovn_central_host'
  148 |     target: "{{ default_ovn_central_target | default(groups['kubeinit_hypervisors'] | first) }}"
  149 | 
  150 | - name: Add ansible_host for ovn_central_host
  151 |   ansible.builtin.add_host:
  152 |     name: "{{ kubeinit_ovn_central_host_name }}"
  153 |     group: 'ovn_central_host'
  154 |     ansible_host: "{{ hostvars[hostvars[kubeinit_ovn_central_host_name].target].ansible_host }}"
  155 | 
  156 | - name: Prepare groups
  157 |   ansible.builtin.include_tasks: prepare_groups.yml
  158 | 
  159 | - name: Define group facts
  160 |   ansible.builtin.set_fact:
  161 |     kubeinit_cluster_hostvars: "{{ hostvars[kubeinit_cluster_name] }}"
  162 |     kubeinit_bastion_host: "{{ hostvars[kubeinit_bastion_host_name].target }}"
  163 |     kubeinit_ovn_central_host: "{{ hostvars[kubeinit_ovn_central_host_name].target }}"
  164 |     kubeinit_first_controller_node: "{{ groups['all_controller_nodes'][0] }}"
  165 |     kubeinit_hypervisor_count: "{{ groups['kubeinit_hypervisors'] | length }}"
  166 |     kubeinit_controller_count: "{{ groups['all_controller_nodes'] | length }}"
  167 |     kubeinit_compute_count: "{{ groups['all_compute_nodes'] | default([]) | length }}"
  168 |     kubeinit_cluster_node_count: "{{ groups['all_cluster_nodes'] | default([]) | length }}"
  169 |   loop: "{{ ['localhost'] | union(groups['kubeinit_hypervisors']) }}"
  170 |   delegate_to: "{{ item }}"
  171 | 
  172 | - name: Install podman if required
  173 |   ansible.builtin.package:
  174 |     state: present
  175 |     name: "podman"
  176 |     use: "{{ hostvars['localhost']['ansible_facts']['pkg_mgr'] }}"
  177 |   when: not hostvars['localhost'].podman_is_installed
  178 | 
  179 | - name: Define service node facts
  180 |   ansible.builtin.set_fact:
  181 |     kubeinit_apache_service_name: "{{ kubeinit_cluster_name }}-apache"
  182 |     kubeinit_bind_service_name: "{{ kubeinit_cluster_name }}-bind"
  183 |     kubeinit_dnsmasq_service_name: "{{ kubeinit_cluster_name }}-dnsmasq"
  184 |     kubeinit_haproxy_service_name: "{{ kubeinit_cluster_name }}-haproxy"
  185 |     kubeinit_provision_service_name: "{{ kubeinit_cluster_name }}-provision"
  186 |     kubeinit_registry_service_name: "{{ kubeinit_cluster_name }}-registry"
  187 |     kubeinit_apache_service_node: "{{ kubeinit_cluster_hostvars.services['apache'] | default(None) }}"
  188 |     kubeinit_bind_service_node: "{{ kubeinit_cluster_hostvars.services['bind'] | default(None) }}"
  189 |     kubeinit_dnsmasq_service_node: "{{ kubeinit_cluster_hostvars.services['dnsmasq'] | default(None) }}"
  190 |     kubeinit_haproxy_service_node: "{{ kubeinit_cluster_hostvars.services['haproxy'] | default(None) }}"
  191 |     kubeinit_provision_service_node: "{{ kubeinit_cluster_hostvars.services['provision'] }}"
  192 |     kubeinit_registry_service_node: "{{ kubeinit_cluster_hostvars.services['registry'] | default(None) }}"
  193 |   loop: "{{ ['localhost'] | union(groups['kubeinit_hypervisors']) }}"
  194 |   delegate_to: "{{ item }}"
  195 | 
  196 | - name: Gather facts from bastion host if it is not a hypervisor host
  197 |   block:
  198 | 
  199 |     - name: Gather hosts facts and omit from the documentation grapher
  200 |       block:
  201 |         - name: Gather facts from bastion_host if needed
  202 |           ansible.builtin.include_role:
  203 |             name: kubeinit.kubeinit.kubeinit_libvirt
  204 |             tasks_from: gather_host_facts.yml
  205 |             public: true
  206 |           vars:
  207 |             _param_gather_host: "{{ kubeinit_bastion_host }}"
  208 |       tags: omit_from_grapher
  209 | 
  210 |     - name: Generate an OpenSSH keypair bastion host
  211 |       community.crypto.openssh_keypair:
  212 |         path: "~/.ssh/{{ kubeinit_cluster_name }}_id_{{ kubeinit_ssh_keytype }}"
  213 |         type: "{{ kubeinit_ssh_keytype }}"
  214 |         comment: "{{ kubeinit_cluster_name }} {{ kubeinit_bastion_host }}"
  215 |         regenerate: 'never'
  216 |       register: _result_bastion_keypair
  217 |       delegate_to: "{{ kubeinit_bastion_host }}"
  218 | 
  219 |     - name: Set authorized_key hostvar for bastion host
  220 |       ansible.builtin.add_host:
  221 |         name: "{{ kubeinit_bastion_host }}"
  222 |         authorized_key: "{{ _result_bastion_keypair.public_key + ' ' + _result_bastion_keypair.comment }}"
  223 | 
  224 |     - name: Add bastion host authorized key to cluster authorized_keys
  225 |       ansible.builtin.set_fact:
  226 |         authorized_keys_with_bastion: "{{ kubeinit_cluster_hostvars.authorized_keys | union([hostvars[kubeinit_bastion_host].authorized_key]) }}"
  227 | 
  228 |     - name: Set all cluster hypervisors fact
  229 |       ansible.builtin.add_host:
  230 |         name: "{{ kubeinit_cluster_name }}"
  231 |         authorized_keys: "{{ authorized_keys_with_bastion }}"
  232 | 
  233 |     - name: Update kubeinit_cluster_hostvars
  234 |       ansible.builtin.set_fact:
  235 |         kubeinit_cluster_hostvars: "{{ hostvars[kubeinit_cluster_name] }}"
  236 | 
  237 |   when: kubeinit_bastion_host not in groups['all_hosts']
  238 | 
  239 | - name: Add all cluster authorized keys to all hypervisors
  240 |   ansible.posix.authorized_key:
  241 |     user: root
  242 |     key: "{{ _key }}"
  243 |     state: present
  244 |   loop: "{{ groups['all_hosts'] | product(kubeinit_cluster_hostvars.authorized_keys) | list }}"
  245 |   vars:
  246 |     _host: "{{ item[0] }}"
  247 |     _key: "{{ item[1] }}"
  248 |   delegate_to: "{{ _host }}"
  249 | 
  250 | - name: Define additional host, node and services facts
  251 |   ansible.builtin.set_fact:
  252 |     kubeinit_bastion_host_address: "{{ hostvars[kubeinit_bastion_host].ssh_connection_address }}"
  253 |     kubeinit_apache_service_address: "{{ hostvars[kubeinit_apache_service_node].ansible_host | default(None) }}"
  254 |     kubeinit_bind_service_address: "{{ hostvars[kubeinit_bind_service_node].ansible_host | default(None) }}"
  255 |     kubeinit_dnsmasq_service_address: "{{ hostvars[kubeinit_dnsmasq_service_node].ansible_host | default(None) }}"
  256 |     kubeinit_haproxy_service_address: "{{ hostvars[kubeinit_haproxy_service_node].ansible_host | default(None) }}"
  257 |     kubeinit_provision_service_address: "{{ hostvars[kubeinit_provision_service_node].ansible_host }}"
  258 |     kubeinit_registry_service_address: "{{ hostvars[kubeinit_registry_service_node].ansible_host | default(None) }}"
  259 |     kubeinit_service_user: "root"
  260 |     kubeinit_service_user_dir: "/root"
  261 |     kubeinit_ingress_hostname: "ingress"
  262 |     kubeinit_bind_volume_name: "{{ kubeinit_bind_service_name }}-config"
  263 |     kubeinit_registry_port: "5000"
  264 |     kubeinit_registry_fqdn: "{{ kubeinit_registry_service_node }}.{{ kubeinit_cluster_fqdn }}"
  265 |     kubeinit_registry_fqdn_alt: "registry.{{ kubeinit_cluster_fqdn }}"
  266 |     kubeinit_registry_uri: "{{ kubeinit_registry_service_node }}.{{ kubeinit_cluster_fqdn }}:5000"
  267 |     kubeinit_services_data_volume: "{{ kubeinit_cluster_name }}-data"
  268 |   loop: "{{ ['localhost'] | union(groups['kubeinit_hypervisors']) }}"
  269 |   delegate_to: "{{ item }}"
  270 | 
  271 | - name: Add ssh ProxyCommand option for all nodes
  272 |   ansible.builtin.add_host:
  273 |     name: "{{ item }}"
  274 |     ansible_ssh_common_args: >-
  275 |       {{ ansible_ssh_common_args }} -i ~/.ssh/{{ kubeinit_cluster_name }}_id_{{ kubeinit_ssh_keytype }} -o ProxyCommand="ssh {{ ansible_ssh_common_args }} -i ~/.ssh/{{ kubeinit_cluster_name }}_id_{{ kubeinit_ssh_keytype }} -W %h:%p -q root@{{ hostvars[kubeinit_ovn_central_host].ssh_connection_address }}"
  276 |   loop: "{{ groups['all_nodes'] }}"
  277 | 
  278 | - name: Gather hosts facts and stop the deployment if required
  279 |   block:
  280 |     - name: Add task-prepare-environment to tasks_completed
  281 |       ansible.builtin.add_host:
  282 |         name: "kubeinit-facts"
  283 |         tasks_completed: "{{ kubeinit_facts_hostvars.tasks_completed | union(['task-prepare-environment']) }}"
  284 | 
  285 |     - name: Update kubeinit_facts_hostvars
  286 |       ansible.builtin.set_fact:
  287 |         kubeinit_facts_hostvars: "{{ hostvars['kubeinit-facts'] }}"
  288 | 
  289 |     - name: Stop the deployment if required
  290 |       block:
  291 |         - name: Stop after 'task-prepare-environment' when requested
  292 |           ansible.builtin.add_host:
  293 |             name: "kubeinit-facts"
  294 |             playbook_terminated: true
  295 |         - name: End play
  296 |           ansible.builtin.meta: end_play
  297 |       when: kubeinit_stop_after_task is defined and kubeinit_stop_after_task in kubeinit_facts_hostvars.tasks_completed
  298 |   tags: omit_from_grapher
```

## Frozen tracked paths in the relevant role/scope

```text
kubeinit/roles/kubeinit_prepare/README.md
kubeinit/roles/kubeinit_prepare/defaults/main.yml
kubeinit/roles/kubeinit_prepare/files/.gitkeep
kubeinit/roles/kubeinit_prepare/handlers/main.yml
kubeinit/roles/kubeinit_prepare/meta/main.yml
kubeinit/roles/kubeinit_prepare/molecule/default/converge.yml
kubeinit/roles/kubeinit_prepare/molecule/default/molecule.yml
kubeinit/roles/kubeinit_prepare/molecule/default/verify.yml
kubeinit/roles/kubeinit_prepare/tasks/build_hypervisors_group.yml
kubeinit/roles/kubeinit_prepare/tasks/create_host_ssh_config.yml
kubeinit/roles/kubeinit_prepare/tasks/deploy_cluster.yml
kubeinit/roles/kubeinit_prepare/tasks/gather_kubeinit_facts.yml
kubeinit/roles/kubeinit_prepare/tasks/gather_kubeinit_secrets.yml
kubeinit/roles/kubeinit_prepare/tasks/main.yml
kubeinit/roles/kubeinit_prepare/tasks/post_deployment.yml
kubeinit/roles/kubeinit_prepare/tasks/prepare_cluster.yml
kubeinit/roles/kubeinit_prepare/tasks/prepare_groups.yml
kubeinit/roles/kubeinit_prepare/tasks/prepare_hypervisor.yml
kubeinit/roles/kubeinit_prepare/tasks/prepare_hypervisors.yml
kubeinit/roles/kubeinit_prepare/tasks/prepare_podman.yml
kubeinit/roles/kubeinit_prepare/templates/ssh-config.j2
kubeinit/roles/kubeinit_prepare/vars/main.yml
```

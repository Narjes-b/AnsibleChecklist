# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-032

- Repository: `Kubeinit/kubeinit`
- Commit: `da6fec314d5594b6bd97ef2e4e71f9098a85e63c`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unnecessary-set-fact`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `kubeinit/roles/kubeinit_prepare/tasks/gather_kubeinit_facts.yml` (reported anchor line 210)
- Object: `variable` `0e5a62a64c90dd6e4c906f64d3e302ef20ede2f987e3c0ab7afe4e3a176aa673`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–407 of 407:

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
   17 | #
   18 | # Gather kubeinit facts
   19 | #
   20 | 
   21 | - name: Load kubeinit_defaults group
   22 |   ansible.builtin.add_host:
   23 |     name: 'kubeinit-defaults'
   24 |     groups: 'kubeinit_defaults'
   25 | 
   26 | - name: Gather kubeinit secrets
   27 |   ansible.builtin.include_role:
   28 |     name: kubeinit.kubeinit.kubeinit_prepare
   29 |     tasks_from: gather_kubeinit_secrets.yml
   30 |     public: true
   31 |   vars:
   32 |     _param_secret_names:[REDACTED VALUE BLOCK]
   33 |       [REDACTED ENCRYPTED VALUE]
   34 |       [REDACTED ENCRYPTED VALUE]
   35 |       [REDACTED ENCRYPTED VALUE]
   36 | 
   37 | - name: Parse kubeinit_network_spec into a dictionary when defined
   38 |   ansible.builtin.set_fact:
   39 |     kubeinit_network_map: "{{ kubeinit_network_spec | from_yaml }}"
   40 |   when: kubeinit_network_spec is defined
   41 | 
   42 | - name: Define kubeinit_network_name
   43 |   ansible.builtin.set_fact:
   44 |     kubeinit_network_name: "{{ kubeinit_network_map['network_name'] | default(hostvars['kubeinit-defaults'].default_network_name) }}"
   45 | 
   46 | - name: Use kubeinit_network_name as host for kubeinit_network group and load default properties
   47 |   ansible.builtin.add_host:
   48 |     name: "{{ kubeinit_network_name }}"
   49 |     groups: 'kubeinit_network'
   50 | 
   51 | - name: Add kubeinit_network_map entries to kubeint_network group
   52 |   ansible.builtin.add_host:
   53 |     name: "{{ kubeinit_network_name }}"
   54 |     groups: 'kubeinit_network'
   55 |     network: "{{ kubeinit_network_map['network'] | default(omit) }}"
   56 |     gateway_offset: "{{ kubeinit_network_map['gateway_offset'] | default(omit) }}"
   57 |     dhcp_start_offset: "{{ kubeinit_network_map['dhcp_start_offset'] | default(omit) }}"
   58 |     dhcp_end_offset: "{{ kubeinit_network_map['dhcp_end_offset'] | default(omit) }}"
   59 |   when: kubeinit_network_spec is defined
   60 | 
   61 | - name: Define kubeinit_network_hostvars and kubeinit_fact_natwork
   62 |   ansible.builtin.set_fact:
   63 |     kubeinit_network_hostvars: "{{ hostvars[kubeinit_network_name] }}"
   64 |     kubeinit_fact_network: "{{ hostvars[kubeinit_network_name].network }}"
   65 | 
   66 | - name: Set facts from kubeinit_network group
   67 |   ansible.builtin.set_fact:
   68 |     kubeinit_cluster_network_name: "{{ kubeinit_network_name }}"
   69 |     kubeinit_cluster_network: "{{ kubeinit_fact_network | ansible.utils.ipv4('net') }}"
   70 |     kubeinit_cluster_prefix: "{{ kubeinit_fact_network | ansible.utils.ipv4('prefix') }}"
   71 |     kubeinit_cluster_netmask: "{{ kubeinit_fact_network | ansible.utils.ipv4('netmask') | ansible.utils.ipv4('address') }}"
   72 |     kubeinit_cluster_gateway: "{{ kubeinit_fact_network | ansible.utils.ipv4(kubeinit_network_hostvars.gateway_offset|int) | ansible.utils.ipv4('address') }}"
   73 |     kubeinit_cluster_next_available: "{{ kubeinit_fact_network | ansible.utils.ipv4(kubeinit_network_hostvars.dhcp_start_offset|int) | ansible.utils.ipv4('address') }}"
   74 |     kubeinit_cluster_last_available: "{{ kubeinit_fact_network | ansible.utils.ipv4(kubeinit_network_hostvars.dhcp_end_offset|int) | ansible.utils.ipv4('address') }}"
   75 | 
   76 | - name: Assert additional constraints
   77 |   ansible.builtin.assert:
   78 |     that:
   79 |       - kubeinit_cluster_prefix|int < 30
   80 | 
   81 | - name: Add cluster network facts to cluster facts
   82 |   ansible.builtin.add_host:
   83 |     name: "{{ kubeinit_cluster_name }}"
   84 |     network_name: "{{ kubeinit_cluster_network_name }}"
   85 |     network: "{{ kubeinit_cluster_network }}"
   86 |     prefix: "{{ kubeinit_cluster_prefix }}"
   87 |     netmask: "{{ kubeinit_cluster_netmask }}"
   88 |     gateway: "{{ kubeinit_cluster_gateway }}"
   89 | 
   90 | - name: Assign controller_nodes addresses
   91 |   ansible.builtin.add_host:
   92 |     name: "{{ controller_node }}"
   93 |     group: ['controller_nodes', 'cluster_nodes']
   94 |     ansible_connection: 'ssh'
   95 |     ansible_host: "{{ kubeinit_cluster_next_available | ansible.utils.ipmath(ansible_loop.index0) | ansible.utils.ipv4('address') }}"
   96 |     ansible_user: root
   97 |     type: 'virtual'
   98 |   loop: "{{ range(kubeinit_spec_controller_count|int) | list }}"
   99 |   loop_control:
  100 |     extended: true
  101 |   vars:
  102 |     controller_node: "{{ hostvars[kubeinit_cluster_name].controller_name_pattern | format(ansible_loop.index) }}"
  103 | 
  104 | - name: Update next available address for allocation
  105 |   ansible.builtin.set_fact:
  106 |     kubeinit_cluster_next_available: "{{ kubeinit_cluster_next_available | ansible.utils.ipmath(kubeinit_spec_controller_count|int) }}"
  107 | 
  108 | - name: Assign compute_nodes addresses
  109 |   ansible.builtin.add_host:
  110 |     name: "{{ compute_node }}"
  111 |     group: ['compute_nodes', 'cluster_nodes']
  112 |     ansible_connection: 'ssh'
  113 |     ansible_host: "{{ kubeinit_cluster_next_available | ansible.utils.ipmath(ansible_loop.index0) | ansible.utils.ipv4('address') }}"
  114 |     ansible_user: root
  115 |     type: 'virtual'
  116 |   loop: "{{ range(kubeinit_spec_compute_count|int) | list }}"
  117 |   loop_control:
  118 |     extended: true
  119 |   vars:
  120 |     compute_node: "{{ hostvars[kubeinit_cluster_name].compute_name_pattern | format(ansible_loop.index) }}"
  121 | 
  122 | - name: Update next available address for allocation
  123 |   ansible.builtin.set_fact:
  124 |     kubeinit_cluster_next_available: "{{ kubeinit_cluster_next_available | ansible.utils.ipmath(kubeinit_spec_compute_count|int) }}"
  125 | 
  126 | - name: Set extra_nodes_map_list fact to defaults
  127 |   ansible.builtin.set_fact:
  128 |     extra_nodes_map_list: "{{ hostvars['kubeinit-defaults'].default_extra_nodes_map_list }}"
  129 | 
  130 | - name: Add entries from extra_nodes_spec to extra_nodes_map_list when defined
  131 |   ansible.builtin.set_fact:
  132 |     extra_nodes_map_list: "{{ extra_nodes_map_list + (extra_nodes_spec | from_yaml) }}"
  133 |   when: extra_nodes_spec is defined
  134 | 
  135 | - name: Add extra_nodes entries for the current distro only
  136 |   ansible.builtin.add_host:
  137 |     name: "{{ item['name'] }}"
  138 |     group: 'extra_nodes'
  139 |     when_distro: "{{ item['when_distro'] | default(omit) }}"
  140 |   loop: "{{ extra_nodes_map_list }}"
  141 |   when: (item['when_distro'] is not defined or kubeinit_cluster_distro in item['when_distro']) and item['name'] is defined
  142 | 
  143 | - name: Set fact for the number of extra nodes in this cluster
  144 |   ansible.builtin.set_fact:
  145 |     kubeinit_spec_extra_count: "{{ groups['extra_nodes'] | default([]) | length | int }}"
  146 | 
  147 | - name: Assign extra_nodes addresses
  148 |   ansible.builtin.add_host:
  149 |     name: "{{ extra_node }}"
  150 |     group: 'extra_nodes'
  151 |     ansible_connection: 'ssh'
  152 |     ansible_host: "{{ kubeinit_cluster_next_available | ansible.utils.ipmath(ansible_loop.index0) | ansible.utils.ipv4('address') }}"
  153 |     ansible_user: root
  154 |     type: 'virtual'
  155 |   loop: "{{ groups['extra_nodes'] | default([]) }}"
  156 |   loop_control:
  157 |     loop_var: extra_node
  158 |     extended: true
  159 | 
  160 | - name: Update next available address for allocation
  161 |   ansible.builtin.set_fact:
  162 |     kubeinit_cluster_next_available: "{{ kubeinit_cluster_next_available | ansible.utils.ipmath(kubeinit_spec_extra_count|int) }}"
  163 |   when: kubeinit_spec_extra_count|int > 0
  164 | 
  165 | - name: Set service_nodes_map_list fact to defaults
  166 |   ansible.builtin.set_fact:
  167 |     service_nodes_map_list: "{{ hostvars['kubeinit-defaults'].default_service_nodes_map_list }}"
  168 | 
  169 | - name: Add entries from service_nodes_spec to service_nodes_map_list when defined
  170 |   ansible.builtin.set_fact:
  171 |     service_nodes_map_list: "{{ service_nodes_map_list + (service_nodes_spec | from_yaml) }}"
  172 |   when: service_nodes_spec is defined
  173 | 
  174 | - name: Add service_nodes entries for the current distro only
  175 |   ansible.builtin.add_host:
  176 |     name: "{{ item['name'] }}"
  177 |     group: 'service_nodes'
  178 |     when_distro: "{{ item['when_distro'] | default(omit) }}"
  179 |   loop: "{{ service_nodes_map_list }}"
  180 |   when: (item['when_distro'] is not defined or kubeinit_cluster_distro in item['when_distro']) and item['name'] is defined
  181 | 
  182 | - name: Set fact for the number of service nodes in this cluster
  183 |   ansible.builtin.set_fact:
  184 |     kubeinit_spec_service_count: "{{ groups['service_nodes'] | length | int }}"
  185 | 
  186 | - name: Assign service_nodes addresses
  187 |   ansible.builtin.add_host:
  188 |     name: "{{ service_node }}"
  189 |     group: 'service_nodes'
  190 |     ansible_connection: 'ssh'
  191 |     ansible_host: "{{ kubeinit_cluster_last_available | ansible.utils.ipmath(0 - ansible_loop.index0) | ansible.utils.ipv4('address') }}"
  192 |     ansible_user: root
  193 |     type: 'container'
  194 |   loop: "{{ groups['service_nodes'] }}"
  195 |   loop_control:
  196 |     loop_var: service_node
  197 |     extended: true
  198 | 
  199 | - name: Update last available address for allocation
  200 |   ansible.builtin.set_fact:
  201 |     kubeinit_cluster_last_available: "{{ kubeinit_cluster_last_available | ansible.utils.ipmath(0 - (kubeinit_spec_service_count|int)) }}"
  202 | 
  203 | - name: Set cluster dhcp facts
  204 |   ansible.builtin.set_fact:
  205 |     kubeinit_cluster_dhcp_start: "{{ kubeinit_cluster_next_available | ansible.utils.ipv4('address') }}"
  206 |     kubeinit_cluster_dhcp_end: "{{ kubeinit_cluster_last_available | ansible.utils.ipv4('address') }}"
  207 | 
  208 | - name: Set cluster dhcp range size
  209 |   ansible.builtin.set_fact:
  210 |     kubeinit_cluster_dhcp_count: "{{ (kubeinit_cluster_dhcp_end | ansible.utils.ipv4('int') | int) - (kubeinit_cluster_dhcp_start | ansible.utils.ipv4('int') | int) + 1 }}"
  211 | 
  212 | - name: Assert sufficient dhcp range
  213 |   ansible.builtin.assert:
  214 |     that:
  215 |       - kubeinit_cluster_dhcp_count|int > 0
  216 | 
  217 | - name: Assign dhcp facts
  218 |   ansible.builtin.add_host:
  219 |     name: "{{ kubeinit_cluster_name }}"
  220 |     dhcp_start: "{{ kubeinit_cluster_dhcp_start }}"
  221 |     dhcp_end: "{{ kubeinit_cluster_dhcp_end }}"
  222 | 
  223 | - name: Clear kubeinit_network_hostvars
  224 |   ansible.builtin.set_fact:
  225 |     kubeinit_network_hostvars: null
  226 | 
  227 | - name: Set cluster_nodes_map_list fact to defaults
  228 |   ansible.builtin.set_fact:
  229 |     cluster_nodes_map_list: "{{ hostvars['kubeinit-defaults'].default_cluster_nodes_map_list }}"
  230 | 
  231 | - name: Add entries from cluster_nodes_spec to cluster_nodes_map_list when defined
  232 |   ansible.builtin.set_fact:
  233 |     cluster_nodes_map_list: "{{ cluster_nodes_map_list + (cluster_nodes_spec | from_yaml) }}"
  234 |   when: cluster_nodes_spec is defined
  235 | 
  236 | - name: Add all items in cluster_nodes_map_list to cluster_nodes_defaults for this distro
  237 |   ansible.builtin.set_fact:
  238 |     cluster_nodes_defaults: "{{ cluster_nodes_defaults | default([]) + (groups['cluster_nodes'] | product([item])) }}"
  239 |   loop: "{{ cluster_nodes_map_list }}"
  240 |   when: item['when_distro'] is not defined or kubeinit_cluster_distro in item['when_distro']
  241 | 
  242 | - name: Apply defaults to all cluster nodes
  243 |   ansible.builtin.add_host:
  244 |     name: "{{ _host }}"
  245 |     os: "{{ _defaults['os'] if (_defaults['os'] is defined and _group_matches|bool and _type_matches|bool) else omit }}"
  246 |     vcpus: "{{ _defaults['vcpus'] if (_defaults['vcpus'] is defined and _group_matches|bool and _type_matches|bool) else omit }}"
  247 |     maxvcpus: "{{ _defaults['maxvcpus'] if (_defaults['maxvcpus'] is defined and _group_matches|bool and _type_matches|bool) else omit }}"
  248 |     disk: "{{ _defaults['disk'] if (_defaults['disk'] is defined and _group_matches|bool and _type_matches|bool) else omit }}"
  249 |     ram: "{{ _defaults['ram'] if (_defaults['ram'] is defined and _group_matches|bool and _type_matches|bool) else omit }}"
  250 |     target_order: "{{ _defaults['target_order'] if (_defaults['target_order'] is defined and _group_matches|bool and _type_matches|bool) else omit }}"
  251 |   loop: "{{ cluster_nodes_defaults }}"
  252 |   vars:
  253 |     _host: "{{ item[0] }}"
  254 |     _defaults: "{{ item[1] }}"
  255 |     _group_matches: "{{ item[1]['when_group'] | default('cluster_nodes') in hostvars[item[0]].group_names }}"
  256 |     _type_matches: "{{ item[1]['when_type'] | default(hostvars[item[0]].type) | default('') == hostvars[item[0]].type | default('') }}"
  257 | 
  258 | - name: Clear cluster_nodes_defaults
  259 |   ansible.builtin.set_fact:
  260 |     cluster_nodes_defaults: null
  261 | 
  262 | - name: Add extra_nodes_map_list to config for current distro only
  263 |   ansible.builtin.set_fact:
  264 |     extra_nodes_config: "{{ extra_nodes_config | default([]) + (groups['extra_nodes'] | default([]) | product([item])) }}"
  265 |   loop: "{{ extra_nodes_map_list }}"
  266 |   when: item['when_distro'] is not defined or kubeinit_cluster_distro in item['when_distro']
  267 | 
  268 | - name: Apply config to all extra nodes
  269 |   ansible.builtin.add_host:
  270 |     name: "{{ _host }}"
  271 |     os: "{{ _config['os'] if (_config['os'] is defined and _type_matches|bool) else omit }}"
  272 |     vcpus: "{{ _config['vcpus'] if (_config['vcpus'] is defined and _type_matches|bool) else omit }}"
  273 |     maxvcpus: "{{ _config['maxvcpus'] if (_config['maxvcpus'] is defined and _type_matches|bool) else omit }}"
  274 |     disk: "{{ _config['disk'] if (_config['disk'] is defined and _type_matches|bool) else omit }}"
  275 |     ram: "{{ _config['ram'] if (_config['ram'] is defined and _type_matches|bool) else omit }}"
  276 |     target_order: "{{ _config['target_order'] if (_config['target_order'] is defined and _type_matches|bool) else omit }}"
  277 |   loop: "{{ extra_nodes_config }}"
  278 |   vars:
  279 |     _host: "{{ item[0] }}"
  280 |     _config: "{{ item[1] }}"
  281 |     _type_matches: "{{ item[1]['when_type'] | default(hostvars[item[0]].type) | default('') == hostvars[item[0]].type | default('') }}"
  282 |   when: _config['name'] | default(_host) == _host
  283 | 
  284 | - name: Add service_nodes_map_list to config for current distro only
  285 |   ansible.builtin.set_fact:
  286 |     service_nodes_config: "{{ service_nodes_config | default([]) + (groups['service_nodes'] | product([item])) }}"
  287 |   loop: "{{ service_nodes_map_list }}"
  288 |   when: item['when_distro'] is not defined or kubeinit_cluster_distro in item['when_distro']
  289 | 
  290 | - name: Apply config to all service nodes
  291 |   ansible.builtin.add_host:
  292 |     name: "{{ _host }}"
  293 |     os: "{{ _config['os'] if (_config['os'] is defined) else omit }}"
  294 |     services: "{{ _config['services'] if (_config['services'] is defined) else omit }}"
  295 |     target_order: "{{ _config['target_order'] if (_config['target_order'] is defined) else omit }}"
  296 |   loop: "{{ service_nodes_config }}"
  297 |   vars:
  298 |     _host: "{{ item[0] }}"
  299 |     _config: "{{ item[1] }}"
  300 |   when: _config['name'] | default(_host) == _host
  301 | 
  302 | - name: Define kubeinit_facts_hostvars
  303 |   ansible.builtin.set_fact:
  304 |     kubeinit_facts_hostvars: "{{ hostvars['kubeinit-facts'] }}"
  305 | 
  306 | - name: Define kubeinit_ssh_keytype
  307 |   ansible.builtin.set_fact:
  308 |     kubeinit_ssh_keytype: "{{ hostvars['kubeinit-env'].ssh_keytype }}"
  309 | 
  310 | - name: Use cluster name as random number seed
  311 |   ansible.builtin.set_fact:
  312 |     _random_mac: "{{ '52:54:00' | community.general.random_mac(seed=kubeinit_cluster_name) }}"
  313 |     _random_uuid: "{{ 999999 | random(seed=kubeinit_cluster_name) | to_uuid }}"
  314 | 
  315 | - name: Assign remaining controller_nodes facts
  316 |   ansible.builtin.add_host:
  317 |     name: "{{ controller_node }}"
  318 |     group: ['controller_nodes', 'cluster_nodes']
  319 |     mac: "{{ hostvars[controller_node].mac | default('52:54:00' | community.general.random_mac) }}"
  320 |     interfaceid: "{{ hostvars[controller_node].interfaceid | default(999999 | random | to_uuid) }}"
  321 |   loop: "{{ range(kubeinit_spec_controller_count|int) | list }}"
  322 |   loop_control:
  323 |     extended: true
  324 |   vars:
  325 |     controller_node: "{{ hostvars[kubeinit_cluster_name].controller_name_pattern | format(ansible_loop.index) }}"
  326 | 
  327 | - name: Assign remaining compute_nodes facts
  328 |   ansible.builtin.add_host:
  329 |     name: "{{ compute_node }}"
  330 |     group: ['compute_nodes', 'cluster_nodes']
  331 |     mac: "{{ hostvars[compute_node].mac | default('52:54:00' | community.general.random_mac) }}"
  332 |     interfaceid: "{{ hostvars[compute_node].interfaceid | default(999999 | random | to_uuid) }}"
  333 |   loop: "{{ range(kubeinit_spec_compute_count|int) | list }}"
  334 |   loop_control:
  335 |     extended: true
  336 |   vars:
  337 |     compute_node: "{{ hostvars[kubeinit_cluster_name].compute_name_pattern | format(ansible_loop.index) }}"
  338 | 
  339 | - name: Assign remaining extra_nodes facts
  340 |   ansible.builtin.add_host:
  341 |     name: "{{ hostvars[extra_node].inventory_hostname }}"
  342 |     group: 'extra_nodes'
  343 |     mac: "{{ hostvars[extra_node].mac | default('52:54:00' | community.general.random_mac) }}"
  344 |     interfaceid: "{{ hostvars[extra_node].interfaceid | default(999999 | random | to_uuid) }}"
  345 |   loop: "{{ groups['extra_nodes'] | default([]) }}"
  346 |   loop_control:
  347 |     loop_var: extra_node
  348 |     extended: true
  349 | 
  350 | - name: Assign remaining service_nodes facts
  351 |   ansible.builtin.add_host:
  352 |     name: "{{ hostvars[service_node].inventory_hostname }}"
  353 |     group: 'service_nodes'
  354 |     mac: "{{ hostvars[service_node].mac | default('52:54:00' | community.general.random_mac) }}"
  355 |     interfaceid: "{{ hostvars[service_node].interfaceid | default(999999 | random | to_uuid) }}"
  356 |   loop: "{{ groups['service_nodes'] | default([]) }}"
  357 |   loop_control:
  358 |     loop_var: service_node
  359 |     extended: true
  360 | 
  361 | - name: Set additional kubeinit-env facts
  362 |   ansible.builtin.set_fact:
  363 |     kubeinit_dns_public: "{{ hostvars['kubeinit-env'].dns_public }}"
  364 | 
  365 | - name: Set registry authentication facts
  366 |   ansible.builtin.set_fact:
  367 |     kubeinit_registry_user: registryusername
  368 |     kubeinit_registry_password: [REDACTED_LITERAL]
  369 | 
  370 | - name: Determine the hypervisor target for all inventory nodes
  371 |   ansible.builtin.set_fact:
  372 |     node_targets: "{{ (node_targets | default([])) | union([inventory_node] | product(hostvars[inventory_node].target_order | reverse)) }}"
  373 |   loop: "{{ groups['cluster_nodes'] + (groups['extra_nodes'] | default([])) + groups['service_nodes'] }}"
  374 |   loop_control:
  375 |     loop_var: inventory_node
  376 | 
  377 | - name: Assign the first requested hypervisor available for each node
  378 |   ansible.builtin.add_host:
  379 |     name: "{{ inventory_node }}"
  380 |     target: "{{ hostvars[inventory_node].target | default(candidate) }}"
  381 |   loop: "{{ node_targets }}"
  382 |   vars:
  383 |     inventory_node: "{{ item[0] }}"
  384 |     candidate: "{{ item[1] }}"
  385 |   when: candidate in groups['kubeinit_hypervisors']
  386 | 
  387 | - name: Update hosts and stop the deployment if required
  388 |   block:
  389 |     - name: Add tasks-gather-facts to tasks completed
  390 |       ansible.builtin.add_host:
  391 |         name: "kubeinit-facts"
  392 |         tasks_completed: "{{ ['task-gather-facts'] }}"
  393 | 
  394 |     - name: Update kubeinit_facts_hostvars
  395 |       ansible.builtin.set_fact:
  396 |         kubeinit_facts_hostvars: "{{ hostvars['kubeinit-facts'] }}"
  397 | 
  398 |     - name: Stop the deployment if required
  399 |       block:
  400 |         - name: Stop after 'task-gather-facts' when requested
  401 |           ansible.builtin.add_host:
  402 |             name: "kubeinit-facts"
  403 |             playbook_terminated: true
  404 |         - name: End play
  405 |           ansible.builtin.meta: end_play
  406 |       when: kubeinit_stop_after_task is defined and kubeinit_stop_after_task in hostvars['kubeinit-facts'].tasks_completed
  407 |   tags: omit_from_grapher
```

## Visible variable references

```text
da6fec314d5594b6bd97ef2e4e71f9098a85e63c:kubeinit/roles/kubeinit_prepare/tasks/gather_kubeinit_facts.yml:210:    kubeinit_cluster_dhcp_count: "{{ (kubeinit_cluster_dhcp_end | ansible.utils.ipv4('int') | int) - (kubeinit_cluster_dhcp_start | ansible.utils.ipv4('int') | int) + 1 }}"
da6fec314d5594b6bd97ef2e4e71f9098a85e63c:kubeinit/roles/kubeinit_prepare/tasks/gather_kubeinit_facts.yml:215:      - kubeinit_cluster_dhcp_count|int > 0
```

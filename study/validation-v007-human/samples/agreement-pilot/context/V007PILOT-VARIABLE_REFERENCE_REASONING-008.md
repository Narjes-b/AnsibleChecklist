# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-008

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `automation/roles/cloud_resources/tasks/azure.yml` (reported anchor line 241)
- Object: `variable` `586ab6f6c2cbfe5574e7ec2d9891cc29d2d866b976f17b8e81c92f3319bc6e8f`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–485 of 485:

```text
    1 | ---
    2 | # Create (if state is present)
    3 | - block:
    4 |     # if ssh_key_content is not defined, get the user public key from the system (if exists)
    5 |     - name: "Set variable: ssh_key_content"
    6 |       ansible.builtin.set_fact:
    7 |         ssh_key_content: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
    8 |       no_log: true # do not display the public key
    9 |       when: ssh_key_content is not defined or ssh_key_content | length < 1
   10 | 
   11 |     - name: "Azure: Create resource group"
   12 |       azure.azcollection.azure_rm_resourcegroup:
   13 |         name: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
   14 |         location: "{{ server_location }}"
   15 | 
   16 |     # if server_network is not specified, create a network and subnet
   17 |     - block:
   18 |         - name: "Azure: Create virtual network"
   19 |           azure.azcollection.azure_rm_virtualnetwork:
   20 |             resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
   21 |             name: "{{ azure_virtual_network | default('postgres-cluster-network') }}"
   22 |             address_prefixes_cidr: ["{{ azure_virtual_network_prefix | default('10.0.0.0/16') }}"]
   23 | 
   24 |         - name: "Azure: Create subnet"
   25 |           azure.azcollection.azure_rm_subnet:
   26 |             resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
   27 |             name: "{{ azure_subnet | default('postgres-cluster-subnet') }}"
   28 |             address_prefix_cidr: "{{ azure_subnet_prefix | default('10.0.1.0/24') }}"
   29 |             virtual_network: "{{ azure_virtual_network | default('postgres-cluster-network') }}"
   30 |       when: server_network | length < 1
   31 | 
   32 |     - name: "Azure: Gather information about network"
   33 |       azure.azcollection.azure_rm_virtualnetwork_info:
   34 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
   35 |         name: "{{ server_network | default(azure_virtual_network | default('postgres-cluster-network'), true) }}"
   36 |       register: network_info
   37 | 
   38 |     - name: "Azure: Create public IP address"
   39 |       azure.azcollection.azure_rm_publicipaddress:
   40 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
   41 |         name: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-public-ip"
   42 |         allocation_method: "Static"
   43 |         sku: "Standard"
   44 |       loop: "{{ range(0, server_count | int) | list }}"
   45 |       loop_control:
   46 |         index_var: idx
   47 |         label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-public-ip"
   48 |       register: public_ip_address
   49 |       when: server_public_ip | bool
   50 | 
   51 |     # Security Group (Firewall)
   52 |     - name: "Azure: Create or modify Security Group"
   53 |       azure.azcollection.azure_rm_securitygroup:
   54 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
   55 |         name: "{{ patroni_cluster_name }}-security-group"
   56 |         rules: "{{ rules }}"
   57 |       vars:
   58 |         rules: >-
   59 |           {{
   60 |             ([{
   61 |               'name': 'public-ssh-rule',
   62 |               'description': 'SSH public access',
   63 |               'protocol': 'Tcp',
   64 |               'destination_port_range': [ansible_ssh_port | default(22)],
   65 |               'source_address_prefix': ssh_public_allowed_ips | default('0.0.0.0/0', true) | split(','),
   66 |               'access': 'Allow',
   67 |               'priority': 1200,
   68 |               'direction': 'Inbound'
   69 |             }] if server_public_ip | bool and ssh_public_access | bool else []) +
   70 |             ([{
   71 |               'name': 'public-netdata-rule',
   72 |               'description': 'Netdata public access',
   73 |               'protocol': 'Tcp',
   74 |               'destination_port_range': [netdata_port | default('19999')],
   75 |               'source_address_prefix': netdata_public_allowed_ips | default('0.0.0.0/0', true) | split(','),
   76 |               'access': 'Allow',
   77 |               'priority': 1400,
   78 |               'direction': 'Inbound'
   79 |             }] if netdata_install | bool and netdata_public_access | bool else []) +
   80 |             ([{
   81 |               'name': 'public-database-rule',
   82 |               'description': 'Database public access',
   83 |               'protocol': 'Tcp',
   84 |               'destination_port_range': ([
   85 |                   haproxy_listen_port.master | default('5000'),
   86 |                   haproxy_listen_port.replicas | default('5001'),
   87 |                   haproxy_listen_port.replicas_sync | default('5002'),
   88 |                   haproxy_listen_port.replicas_async | default('5003')
   89 |                 ] if with_haproxy_load_balancing | bool else []) +
   90 |                 ([pgbouncer_listen_port | default('6432')] if not with_haproxy_load_balancing | bool and pgbouncer_install | bool else []) +
   91 |                 ([postgresql_port | default('5432')] if not with_haproxy_load_balancing | bool and not pgbouncer_install | bool else []),
   92 |               'source_address_prefix': '0.0.0.0/0',
   93 |               'access': 'Allow',
   94 |               'priority': 1300,
   95 |               'direction': 'Inbound'
   96 |             }] if database_public_access | bool else []) +
   97 |             [{
   98 |               'name': 'private-postgres-cluster-rule',
   99 |               'description': 'Postgres cluster ports',
  100 |               'protocol': 'Tcp',
  101 |               'destination_port_range': [ansible_ssh_port | default(22)] +
  102 |                 ([
  103 |                   haproxy_listen_port.master | default('5000'),
  104 |                   haproxy_listen_port.replicas | default('5001'),
  105 |                   haproxy_listen_port.replicas_sync | default('5002'),
  106 |                   haproxy_listen_port.replicas_async | default('5003'),
  107 |                   haproxy_listen_port.stats | default('7000')
  108 |                 ] if with_haproxy_load_balancing | bool else []) +
  109 |                 ([pgbouncer_listen_port | default('6432')] if pgbouncer_install | bool else []) +
  110 |                 [
  111 |                   postgresql_port | default('5432'),
  112 |                   patroni_restapi_port | default('8008'),
  113 |                 ] +
  114 |                 ([
  115 |                   etcd_client_port | default('2379'),
  116 |                   etcd_peer_port | default('2380'),
  117 |                 ] if dcs_type == 'etcd' else []) +
  118 |                 ([
  119 |                   consul_ports_dns | default('8600'),
  120 |                   consul_ports_http | default('8500'),
  121 |                   consul_ports_rpc | default('8400'),
  122 |                   consul_ports_serf_lan | default('8301'),
  123 |                   consul_ports_serf_wan | default('8302'),
  124 |                   consul_ports_server | default('8300')
  125 |                 ] if dcs_type == 'consul' else []) +
  126 |                 ([netdata_port | default('19999')] if netdata_install | bool else []),
  127 |               'source_address_prefix': network_info.virtualnetworks[0].address_prefixes,
  128 |               'access': 'Allow',
  129 |               'priority': 1000,
  130 |               'direction': 'Inbound'
  131 |             }]
  132 |           }}
  133 |       when: cloud_firewall | bool
  134 | 
  135 |     # Network interface
  136 |     - name: "Azure: Create network interface"
  137 |       azure.azcollection.azure_rm_networkinterface:
  138 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  139 |         name: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-network-interface"
  140 |         virtual_network: "{{ server_network | default(azure_virtual_network | default('postgres-cluster-network'), true) }}"
  141 |         subnet_name: "{{ azure_subnet | default('postgres-cluster-subnet') }}"
  142 |         security_group: "{{ patroni_cluster_name }}-security-group"
  143 |         ip_configurations:
  144 |           - name: ipconfig1
  145 |             primary: true
  146 |             public_ip_address_name: "{{ server_public_ip | bool | ternary(server_name | lower ~ '%02d' % (idx + 1) ~ '-public-ip', None) }}"
  147 |         dns_servers:
  148 |           - 8.8.8.8
  149 |       loop: "{{ range(0, server_count | int) | list }}"
  150 |       loop_control:
  151 |         index_var: idx
  152 |         label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-network-interface"
  153 | 
  154 |     # Server and volume
  155 |     - name: "Azure: Gather information about virtual machines"
  156 |       azure.azcollection.azure_rm_virtualmachine_info:
  157 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  158 |         name: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  159 |       loop: "{{ range(0, server_count | int) | list }}"
  160 |       loop_control:
  161 |         index_var: idx
  162 |         label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  163 |       register: azure_rm_virtualmachine_info
  164 |       failed_when: false
  165 | 
  166 |     - name: "Azure: Create virtual machine"
  167 |       azure.azcollection.azure_rm_virtualmachine:
  168 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  169 |         name: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  170 |         state: present
  171 |         started: true
  172 |         location: "{{ server_location }}"
  173 |         vm_size: "{{ server_type }}"
  174 |         priority: "{{ 'Spot' if server_spot | default(false) | bool else 'None' }}"
  175 |         eviction_policy: "{{ 'Deallocate' if server_spot | default(false) | bool else omit }}"
  176 |         admin_username: "{{ azure_admin_username | default('azureadmin') }}"
  177 |         ssh_public_keys:
  178 |           - path: /home/azureadmin/.ssh/authorized_keys
  179 |             key_data: "{{ ssh_key_content }}"
  180 |         ssh_password_enabled: [REDACTED_LITERAL]
  181 |         image:
  182 |           offer: "{{ azure_vm_image_offer | default('ubuntu-24_04-lts') }}"
  183 |           publisher: "{{ azure_vm_image_publisher | default('Canonical') }}"
  184 |           sku: "{{ azure_vm_image_sku | default('server') }}"
  185 |           version: "{{ azure_vm_image_version | default('latest') }}"
  186 |         os_type: Linux
  187 |         os_disk_size_gb: "{{ system_volume_size | default('80') }}" # system disk size
  188 |         managed_disk_type: "{{ system_volume_type | default('StandardSSD_LRS', true) }}"
  189 |         data_disks: "{{ [] if use_local_disk | bool else [data_disk] }}"
  190 |         network_interface_names:
  191 |           - "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-network-interface"
  192 |         tags:
  193 |           Cluster: "{{ patroni_cluster_name }}"
  194 |       loop: "{{ range(0, server_count | int) | list }}"
  195 |       loop_control:
  196 |         index_var: idx
  197 |         label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  198 |       register: server_result
  199 |       vars:
  200 |         data_disk:
  201 |           lun: 0
  202 |           disk_size_gb: "{{ volume_size | int }}"
  203 |           managed_disk_type: "{{ volume_type | default('StandardSSD_LRS', true) }}"
  204 | 
  205 |     # Required to allow data disk size to be changed after deployment without deallocating the VM.
  206 |     - name: "Azure: Ensure data disk size"
  207 |       azure.azcollection.azure_rm_manageddisk:
  208 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  209 |         name: "{{ item.ansible_facts.azure_vm.storage_profile.data_disks[0].name }}"
  210 |         location: "{{ server_location }}"
  211 |         disk_size_gb: "{{ volume_size | int }}"
  212 |         state: present
  213 |       loop: "{{ server_result.results | selectattr('ansible_facts.azure_vm', 'defined') | list }}"
  214 |       loop_control:
  215 |         label: "{{ item.ansible_facts.azure_vm.storage_profile.data_disks[0].name | default('data-disk') }}"
  216 |       when:
  217 |         - not use_local_disk | bool
  218 |         - item.ansible_facts.azure_vm.storage_profile.data_disks is defined
  219 |         - item.ansible_facts.azure_vm.storage_profile.data_disks | length > 0
  220 |         - item.ansible_facts.azure_vm.storage_profile.data_disks[0].managed_disk is defined
  221 | 
  222 |     # Load Balancer
  223 |     - name: "Azure: Create public IP address for Load Balancer"
  224 |       azure.azcollection.azure_rm_publicipaddress:
  225 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  226 |         name: "{{ patroni_cluster_name }}-{{ item }}-public-ip"
  227 |         allocation_method: "Static"
  228 |         sku: "Standard"
  229 |       loop:
  230 |         - "primary"
  231 |         - "replica"
  232 |         - "sync"
  233 |       loop_control:
  234 |         label: "{{ patroni_cluster_name }}-{{ item }}-public-ip"
  235 |       register: azure_load_balancer_public_ip
  236 |       when: database_public_access | bool and cloud_load_balancer | bool and
  237 |         (item == 'primary' or
  238 |         (item == 'replica' and server_count | int > 1) or
  239 |         (item in ['sync', 'async'] and server_count | int > 1 and synchronous_mode | bool))
  240 | 
  241 |     - name: "Azure: Create or modify Load Balancer"
  242 |       azure.azcollection.azure_rm_loadbalancer:
  243 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  244 |         name: "{{ patroni_cluster_name }}-{{ item }}"
  245 |         location: "{{ server_location }}"
  246 |         frontend_ip_configurations:
  247 |           - name: "{{ patroni_cluster_name }}-{{ item }}-frontend"
  248 |             public_ip_address: "{{ database_public_access | bool | ternary(patroni_cluster_name ~ '-' ~ item ~ '-public-ip', omit) }}"
  249 |             subnet: "{{ database_public_access | bool | ternary(omit, network_info.virtualnetworks[0].subnets[0].id) }}"
  250 |         backend_address_pools:
  251 |           - name: "{{ patroni_cluster_name }}-{{ item }}-backend"
  252 |         probes:
  253 |           - name: "{{ patroni_cluster_name }}-{{ item }}-health-probe"
  254 |             protocol: "{{ patroni_restapi_protocol | capitalize }}"
  255 |             port: "{{ patroni_restapi_port }}"
  256 |             request_path: "/{{ item }}"
  257 |             interval: 5
  258 |             fail_count: 2
  259 |         load_balancing_rules:
  260 |           - name: "{{ patroni_cluster_name }}-{{ item }}-rule"
  261 |             frontend_ip_configuration: "{{ patroni_cluster_name }}-{{ item }}-frontend"
  262 |             frontend_port: "{{ pgbouncer_listen_port | default('6432') if pgbouncer_install | bool else postgresql_port | default('5432') }}"
  263 |             backend_address_pool: "{{ patroni_cluster_name }}-{{ item }}-backend"
  264 |             backend_port: "{{ pgbouncer_listen_port | default('6432') if pgbouncer_install | bool else postgresql_port | default('5432') }}"
  265 |             probe: "{{ patroni_cluster_name }}-{{ item }}-health-probe"
  266 |             protocol: "Tcp"
  267 |             idle_timeout: 10 # in minutes
  268 |             enable_floating_ip: false
  269 |             disable_outbound_snat: true
  270 |         sku: "Standard"
  271 |       loop:
  272 |         - "primary"
  273 |         - "replica"
  274 |         - "sync"
  275 |       loop_control:
  276 |         label: "{{ patroni_cluster_name }}-{{ item }}"
  277 |       register: azure_load_balancer
  278 |       when: cloud_load_balancer | bool and
  279 |         (item == 'primary' or
  280 |         (item == 'replica' and server_count | int > 1) or
  281 |         (item in ['sync', 'async'] and server_count | int > 1 and synchronous_mode | bool))
  282 | 
  283 |     - name: Extract virtual machine private IPs
  284 |       ansible.builtin.set_fact:
  285 |         private_ips: >-
  286 |           {{
  287 |             private_ips | default([]) +
  288 |             [item.ansible_facts.azure_vm.network_profile.network_interfaces[0].properties.ip_configurations[0].private_ip_address]
  289 |           }}
  290 |       loop: "{{ server_result.results | selectattr('ansible_facts.azure_vm', 'defined') | list }}"
  291 |       loop_control:
  292 |         label: "{{ item.ansible_facts.azure_vm.network_profile.network_interfaces[0].properties.ip_configurations[0].private_ip_address }}"
  293 | 
  294 |     # Note: We use Azure CLI here because there is no ansible module available to manage the list of IP addresses within a backend pool.
  295 |     - name: "Azure: Add virtual machine IP addresses to Load Balancer backend pool"
  296 |       ansible.builtin.shell: |
  297 |         {% for ip in private_ips %}
  298 |         az network lb address-pool address add \
  299 |         --resource-group {{ azure_resource_group | default('postgres-cluster-resource-group-' ~ server_location) }} \
  300 |         --lb-name {{ patroni_cluster_name }}-{{ item }} \
  301 |         --pool-name {{ patroni_cluster_name }}-{{ item }}-backend \
  302 |         --vnet {{ azure_virtual_network | default('postgres-cluster-network') }} \
  303 |         --name address-{{ ip }} \
  304 |         --ip-address {{ ip }}
  305 |         {% endfor %}
  306 |       args:
  307 |         executable: /bin/bash
  308 |       loop:
  309 |         - "primary"
  310 |         - "replica"
  311 |         - "sync"
  312 |       loop_control:
  313 |         label: "{{ patroni_cluster_name }}-{{ item }}-backend"
  314 |       when: cloud_load_balancer | bool and
  315 |         (item == 'primary' or
  316 |         (item == 'replica' and server_count | int > 1) or
  317 |         (item in ['sync', 'async'] and server_count | int > 1 and synchronous_mode | bool))
  318 | 
  319 |   when: state == 'present'
  320 | 
  321 | # Info
  322 | - name: Server info
  323 |   ansible.builtin.debug:
  324 |     msg:
  325 |       id: "{{ item.ansible_facts.azure_vm.id | default('N/A', true) }}"
  326 |       name: "{{ item.ansible_facts.azure_vm.name | default('N/A', true) }}"
  327 |       image: "{{ item.ansible_facts.azure_vm.storage_profile.image_reference | default('N/A', true) }}"
  328 |       type: "{{ item.ansible_facts.azure_vm.hardware_profile.vm_size | default('N/A', true) }}"
  329 |       volume_size: "{{ item.ansible_facts.azure_vm.storage_profile.data_disks[0].disk_size_gb | default('N/A', true) }} GB"
  330 |       volume_type: "{{ item.ansible_facts.azure_vm.storage_profile.data_disks[0].managed_disk.storage_account_type | default('N/A', true) }}"
  331 |       public_ip: >-
  332 |         {{
  333 |           (public_ip_address.results if public_ip_address is defined else [])
  334 |           | selectattr('idx', 'equalto', item.idx) | map(attribute='state.ip_address') | first | default('N/A', true)
  335 |         }}
  336 |       private_ip: >-
  337 |         {{
  338 |           item.ansible_facts.azure_vm.network_profile.network_interfaces[0].properties.ip_configurations[0].private_ip_address | default('N/A', true)
  339 |         }}
  340 |   loop: "{{ server_result.results }}"
  341 |   loop_control:
  342 |     index_var: idx
  343 |     label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  344 |   when:
  345 |     - server_result.results is defined
  346 |     - item.ansible_facts is defined
  347 | 
  348 | # Check SSH access - via a public IP address
  349 | - name: "Wait for host to be available via SSH"
  350 |   ansible.builtin.wait_for:
  351 |     host: "{{ item.state.ip_address }}"
  352 |     port: 22
  353 |     delay: 5
  354 |     timeout: 300
  355 |   loop: "{{ public_ip_address.results }}"
  356 |   loop_control:
  357 |     index_var: idx
  358 |     label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  359 |   when:
  360 |     - public_ip_address.results | default([]) | length > 0
  361 |     - server_public_ip | bool
  362 |     - ssh_public_access | bool
  363 |     - item.state.ip_address is defined
  364 | 
  365 | # Check SSH access - via a private IP address (if public IP is not defined)
  366 | - name: "Wait for host to be available via SSH"
  367 |   ansible.builtin.wait_for:
  368 |     host: "{{ item.ansible_facts.azure_vm.network_profile.network_interfaces[0].properties.ip_configurations[0].private_ip_address }}"
  369 |     port: 22
  370 |     delay: 5
  371 |     timeout: 300
  372 |   loop: "{{ server_result.results }}"
  373 |   loop_control:
  374 |     index_var: idx
  375 |     label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  376 |   when:
  377 |     - not (server_public_ip | bool and ssh_public_access | bool)
  378 |     - server_result.results is defined
  379 |     - item.ansible_facts.azure_vm.network_profile.network_interfaces[0].properties.ip_configurations[0].private_ip_address is defined
  380 | 
  381 | # Inventory
  382 | - block:
  383 |     - name: "Inventory | Extract IP addresses"
  384 |       ansible.builtin.set_fact: # yamllint disable rule:line-length
  385 |         ip_addresses: >-
  386 |           {{ ip_addresses | default([]) +
  387 |             [{
  388 |               'public_ip': (public_ip_address.results if public_ip_address is defined else []) | selectattr('idx', 'equalto', item.idx) | map(attribute='state.ip_address') | first | default(''),
  389 |               'private_ip': item.ansible_facts.azure_vm.network_profile.network_interfaces[0].properties.ip_configurations[0].private_ip_address | default(''),
  390 |               'new_node': (cluster_scaling | default(false) | bool and item.ansible_facts.azure_vm.id not in existing_vm_ids)
  391 |             }]
  392 |           }}
  393 |       vars:
  394 |         existing_vm_ids: >-
  395 |           {{
  396 |             azure_rm_virtualmachine_info.results | default([])
  397 |             | map(attribute='vms') | map('default', []) | list | flatten
  398 |             | selectattr('id','defined') | map(attribute='id') | list
  399 |           }}
  400 |       loop: "{{ server_result.results | selectattr('ansible_facts.azure_vm', 'defined') | list }}"
  401 |       loop_control:
  402 |         label: >-
  403 |           public_ip: {{ (public_ip_address.results if public_ip_address is defined else []) | selectattr('idx', 'equalto', item.idx) | map(attribute='state.ip_address') | first | default('') }},
  404 |           private_ip: {{ item.ansible_facts.azure_vm.network_profile.network_interfaces[0].properties.ip_configurations[0].private_ip_address | default('') }}
  405 | 
  406 |     - name: "Inventory | Generate in-memory inventory"
  407 |       ansible.builtin.import_tasks: inventory.yml
  408 |   when:
  409 |     - server_result.results is defined
  410 |     - (server_result.results | selectattr('ansible_facts.azure_vm', 'defined') | list | length) > 0
  411 |     - generate_inventory | default(true) | bool
  412 | 
  413 | # Delete (if state is absent)
  414 | - block:
  415 |     - name: "Azure: Delete virtual machine"
  416 |       azure.azcollection.azure_rm_virtualmachine:
  417 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  418 |         name: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  419 |         state: absent
  420 |       loop: "{{ range(0, server_count | int) | list }}"
  421 |       loop_control:
  422 |         index_var: idx
  423 |         label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}"
  424 | 
  425 |     - name: "Azure: Delete network interface"
  426 |       azure.azcollection.azure_rm_networkinterface:
  427 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  428 |         name: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-network-interface"
  429 |         state: absent
  430 |       loop: "{{ range(0, server_count | int) | list }}"
  431 |       loop_control:
  432 |         index_var: idx
  433 |         label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-network-interface"
  434 | 
  435 |     - name: "Azure: Delete public IP address"
  436 |       azure.azcollection.azure_rm_publicipaddress:
  437 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  438 |         name: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-public-ip"
  439 |         state: absent
  440 |       loop: "{{ range(0, server_count | int) | list }}"
  441 |       loop_control:
  442 |         index_var: idx
  443 |         label: "{{ server_name | lower }}{{ '%02d' % (idx + 1) }}-public-ip"
  444 |       when: server_public_ip | bool
  445 | 
  446 |     - name: "Azure: Delete Load Balancer"
  447 |       azure.azcollection.azure_rm_loadbalancer:
  448 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  449 |         name: "{{ patroni_cluster_name }}-{{ item }}"
  450 |         location: "{{ server_location }}"
  451 |         state: absent
  452 |       loop:
  453 |         - "primary"
  454 |         - "replica"
  455 |         - "sync"
  456 |       loop_control:
  457 |         label: "{{ patroni_cluster_name }}-{{ item }}"
  458 |       when: cloud_load_balancer | bool and
  459 |         (item == 'primary' or
  460 |         (item == 'replica' and server_count | int > 1) or
  461 |         (item in ['sync', 'async'] and server_count | int > 1 and synchronous_mode | bool))
  462 | 
  463 |     - name: "Azure: Delete Load Balancer public IP address"
  464 |       azure.azcollection.azure_rm_publicipaddress:
  465 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  466 |         name: "{{ patroni_cluster_name }}-{{ item }}-public-ip"
  467 |         state: absent
  468 |       loop:
  469 |         - "primary"
  470 |         - "replica"
  471 |         - "sync"
  472 |       loop_control:
  473 |         label: "{{ patroni_cluster_name }}-{{ item }}-public-ip"
  474 |       when: database_public_access | bool and cloud_load_balancer | bool and
  475 |         (item == 'primary' or
  476 |         (item == 'replica' and server_count | int > 1) or
  477 |         (item in ['sync', 'async'] and server_count | int > 1 and synchronous_mode | bool))
  478 | 
  479 |     - name: "Azure: Delete Security Group"
  480 |       azure.azcollection.azure_rm_securitygroup:
  481 |         resource_group: "{{ azure_resource_group | default('postgres-cluster-resource-group' ~ '-' ~ server_location) }}"
  482 |         name: "{{ patroni_cluster_name }}-security-group"
  483 |         state: absent
  484 | 
  485 |   when: state == 'absent'
```

## Visible variable references

```text
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/cloud_resources/tasks/azure.yml:235:      register: azure_load_balancer_public_ip
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/cloud_resources/tasks/azure.yml:277:      register: azure_load_balancer
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/deploy_finish/tasks/main.yml:298:    lb_primary_public: "{{ (hostvars['localhost']['azure_load_balancer_public_ip']['results'] | selectattr('item', 'equalto', 'primary') | first).state.ip_address | default('N/A') }}"
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/deploy_finish/tasks/main.yml:299:    lb_replica_public: "{{ (hostvars['localhost']['azure_load_balancer_public_ip']['results'] | selectattr('item', 'equalto', 'replica') | first).state.ip_address | default('N/A') }}"
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/deploy_finish/tasks/main.yml:300:    lb_sync_public: "{{ (hostvars['localhost']['azure_load_balancer_public_ip']['results'] | selectattr('item', 'equalto', 'sync') | first).state.ip_address | default('N/A') }}"
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/deploy_finish/tasks/main.yml:301:    lb_primary_private: "{{ (hostvars['localhost']['azure_load_balancer']['results'] | selectattr('item', 'equalto', 'primary') | first).state.frontend_ip_configurations[0].private_ip_address | default('N/A') }}"
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/deploy_finish/tasks/main.yml:302:    lb_replica_private: "{{ (hostvars['localhost']['azure_load_balancer']['results'] | selectattr('item', 'equalto', 'replica') | first).state.frontend_ip_configurations[0].private_ip_address | default('N/A') }}"
f24ff3d316e688901a1118a9f769798f40dd42e7:automation/roles/deploy_finish/tasks/main.yml:303:    lb_sync_private: "{{ (hostvars['localhost']['azure_load_balancer']['results'] | selectattr('item', 'equalto', 'sync') | first).state.frontend_ip_configurations[0].private_ip_address | default('N/A') }}"
```

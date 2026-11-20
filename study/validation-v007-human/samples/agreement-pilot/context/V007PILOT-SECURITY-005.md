# Frozen source context: V007PILOT-SECURITY-005

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `playbooks/utils/replace_vm_host.yml` (reported anchor line 31)
- Object: `task` `2a303262305eeac2095dccf1ec6f8ba248037dc288f6a295c30d0cbbc47a780f`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–382 of 382:

```text
    1 | ---
    2 | #  This playbook deletes a VM and replaces it from a vSphere template. This is the only warning you will get. Running this playbook has destructive consequences!
    3 | #  This playbook should only be run from ansible tower. No need for detailed instructions or examples here, because you should not run it here.
    4 | #
    5 | - name: replace the {{ replacement_vm }} VM on the {{ runtime_env | default('staging') }} vSphere
    6 |   hosts: localhost
    7 |   remote_user: pulsys
    8 |   become: true
    9 | 
   10 |   vars:
   11 |     slack_alerts_channel: "#infrastructure"
   12 |     vm_template_name: "{{ vm_template | default('template_jammy_spring_2024') }}"
   13 | 
   14 |   vars_files:
   15 |     - ../../group_vars/all/vault.yml
   16 |     - ../../group_vars/vsphere/vault.yml
   17 |     - ../../group_vars/vsphere/{{ runtime_env | default('staging') }}.yml
   18 | 
   19 |   tasks:
   20 |     - name: Gather info on VM to replace
   21 |       community.vmware.vmware_vm_info:
   22 |         hostname: "{{ vcenter_hostname }}"
   23 |         username: "{{ vcenter_username }}"
   24 |         password: "{{ vcenter_password }}"
   25 |         validate_certs: false
   26 |         show_allocated: true
   27 |         vm_name: "{{ replacement_vm }}"
   28 |       register: old_vm_info
   29 | 
   30 |     - name: Gather network info on VM to replace
   31 |       community.vmware.vmware_guest_network:
   32 |         hostname: "{{ vcenter_hostname }}"
   33 |         username: "{{ vcenter_username }}"
   34 |         password: "{{ vcenter_password }}"
   35 |         name: "{{ replacement_vm }}"
   36 |         validate_certs: false
   37 |         gather_network_info: true
   38 |       register: old_vm_net_info
   39 | 
   40 |     - name: Build VM FQDN
   41 |       set_fact:
   42 |         vm_fqdn: "{{ replacement_vm }}.{{ dns_domain }}"
   43 | 
   44 |     - name: Compute datastore name robustly
   45 |       set_fact:
   46 |         vm_datastore_name: >-
   47 |           {%- set vm = old_vm_info.virtual_machines[0] -%}
   48 |           {%- if vm.datastore is defined -%}
   49 |             {%- if vm.datastore is string -%}
   50 |               {{ vm.datastore }}
   51 |             {%- elif vm.datastore is sequence and not (vm.datastore is string) -%}
   52 |               {{ vm.datastore | first }}
   53 |             {%- elif vm.datastore is mapping and 'name' in vm.datastore -%}
   54 |               {{ vm.datastore.name }}
   55 |             {%- else -%}
   56 |               datastore1
   57 |             {%- endif -%}
   58 |           {%- elif vm.datastore_url is defined -%}
   59 |             {%- set dsu = (vm.datastore_url | first) if (vm.datastore_url is sequence and not (vm.datastore_url is string)) else vm.datastore_url -%}
   60 |             {%- if dsu is mapping and 'name' in dsu -%}
   61 |               {{ dsu.name }}
   62 |             {%- elif dsu is string and dsu.startswith('[') -%}
   63 |               {{ dsu.split(']')[0] | regex_replace('^\\[', '') }}
   64 |             {%- else -%}
   65 |               datastore1
   66 |             {%- endif -%}
   67 |           {%- else -%}
   68 |             datastore1
   69 |           {%- endif -%}
   70 | 
   71 |     - name: Get current VM hardware details
   72 |       community.vmware.vmware_guest_info:
   73 |         hostname: "{{ vcenter_hostname }}"
   74 |         username: "{{ vcenter_username }}"
   75 |         password: "{{ vcenter_password }}"
   76 |         validate_certs: false
   77 |         datacenter: "{{ vcenter_datacenter }}"
   78 |         name: "{{ replacement_vm }}"
   79 |         schema: vsphere
   80 |         properties:
   81 |           - config.hardware.device
   82 |       register: vm_hardware_info
   83 | 
   84 |     - name: Get template hardware details
   85 |       community.vmware.vmware_guest_info:
   86 |         hostname: "{{ vcenter_hostname }}"
   87 |         username: "{{ vcenter_username }}"
   88 |         password: "{{ vcenter_password }}"
   89 |         validate_certs: false
   90 |         datacenter: "{{ vcenter_datacenter }}"
   91 |         name: "{{ vm_template_name }}"
   92 |         schema: vsphere
   93 |         properties:
   94 |           - config.hardware.device
   95 |       register: template_hardware_info
   96 | 
   97 |     - name: Build disk config from current VM
   98 |       set_fact:
   99 |         vm_disk_config: >-
  100 |           {%- set disks = [] -%}
  101 |           {%- for device in vm_hardware_info.instance.config.hardware.device | default([]) -%}
  102 |             {%- if device._vimtype == 'vim.vm.device.VirtualDisk' -%}
  103 |               {%- set _ = disks.append({
  104 |                 'size_gb': (device.capacityInKB / 1024 / 1024) | round(0, 'ceil') | int,
  105 |                 'unit_number': device.unitNumber | default(loop.index0),
  106 |                 'controller_type': 'paravirtual',
  107 |                 'controller_number': 0,
  108 |                 'datastore': vm_datastore_name
  109 |               }) -%}
  110 |             {%- endif -%}
  111 |           {%- endfor -%}
  112 |           {{ disks | sort(attribute='unit_number') }}
  113 | 
  114 |     - name: Build disk config from template
  115 |       set_fact:
  116 |         template_disk_config: >-
  117 |           {%- set disks = [] -%}
  118 |           {%- for device in template_hardware_info.instance.config.hardware.device | default([]) -%}
  119 |             {%- if device._vimtype == 'vim.vm.device.VirtualDisk' -%}
  120 |               {%- set _ = disks.append({
  121 |                 'size_gb': (device.capacityInKB / 1024 / 1024) | round(0, 'ceil') | int,
  122 |                 'unit_number': device.unitNumber | default(loop.index0)
  123 |               }) -%}
  124 |             {%- endif -%}
  125 |           {%- endfor -%}
  126 |           {{ disks | sort(attribute='unit_number') }}
  127 | 
  128 |     - name: Fail if template has more disks than current VM
  129 |       ansible.builtin.fail:
  130 |         msg: >-
  131 |           Template {{ vm_template_name }} has {{ template_disk_config | length }} disk(s)
  132 |           but {{ replacement_vm }} has {{ vm_disk_config | length }} disk(s).
  133 |           Refusing to continue.
  134 |       when: template_disk_config | length > vm_disk_config | length
  135 | 
  136 |     - name: Build map of template disks by unit number
  137 |       set_fact:
  138 |         template_disk_map: "{{ template_disk_map | default({}) | combine({ (item.unit_number | string): item.size_gb }) }}"
  139 |       loop: "{{ template_disk_config }}"
  140 | 
  141 |     - name: Build safe disk config
  142 |       set_fact:
  143 |         vm_disk_config_safe: >-
  144 |           {%- set disks = [] -%}
  145 |           {%- for disk in vm_disk_config -%}
  146 |             {%- set template_size = template_disk_map[disk.unit_number | string] | default(disk.size_gb) -%}
  147 |             {%- set _ = disks.append({
  148 |               'size_gb': [disk.size_gb, template_size] | max,
  149 |               'unit_number': disk.unit_number,
  150 |               'controller_type': 'paravirtual',
  151 |               'controller_number': 0,
  152 |               'datastore': vm_datastore_name
  153 |             }) -%}
  154 |           {%- endfor -%}
  155 |           {{ disks | sort(attribute='unit_number') }}
  156 | 
  157 |     - name: Show safe disk config
  158 |       ansible.builtin.debug:
  159 |         var: vm_disk_config_safe
  160 | 
  161 |     - name: Print out warning
  162 |       ansible.builtin.debug:
  163 |         msg:
  164 |           - Ansible will now move and power off the current {{ old_vm_info.virtual_machines[0].guest_name }} VM.
  165 |           - Then create a replacement in the {{ old_vm_net_info.network_info[0].network_name }} network.
  166 |           - The new VM will have {{ vm_disk_config_safe | length }} disk(s) using a template-safe configuration on datastore {{ vm_datastore_name }}.
  167 | 
  168 |     - name: Move old VM to a different folder (ToBeDeleted, Forensics)
  169 |       community.vmware.vmware_guest_move:
  170 |         hostname: "{{ vcenter_hostname }}"
  171 |         username: "{{ vcenter_username }}"
  172 |         password: "{{ vcenter_password }}"
  173 |         validate_certs: false
  174 |         datacenter: "{{ vcenter_datacenter }}"
  175 |         dest_folder: "{{ vm_dest_folder }}"
  176 |         uuid: "{{ old_vm_info.virtual_machines[0].uuid }}"
  177 | 
  178 |     - name: Power off old VM using UUID
  179 |       community.vmware.vmware_guest_powerstate:
  180 |         hostname: "{{ vcenter_hostname }}"
  181 |         username: "{{ vcenter_username }}"
  182 |         password: "{{ vcenter_password }}"
  183 |         validate_certs: false
  184 |         datacenter: "{{ vcenter_datacenter }}"
  185 |         uuid: "{{ old_vm_info.virtual_machines[0].uuid }}"
  186 |         state: powered-off
  187 | 
  188 |     - name: Rename old VM using moid
  189 |       community.vmware.vmware_object_rename:
  190 |         hostname: "{{ vcenter_hostname }}"
  191 |         username: "{{ vcenter_username }}"
  192 |         password: "{{ vcenter_password }}"
  193 |         validate_certs: false
  194 |         new_name: "{{ old_vm_info.virtual_machines[0].guest_name }}-{{ ansible_date_time.iso8601_basic_short }}"
  195 |         object_moid: "{{ old_vm_info.virtual_machines[0].moid }}"
  196 |         object_type: VirtualMachine
  197 | 
  198 |     - name: Create replacement VM from template
  199 |       community.vmware.vmware_guest:
  200 |         hostname: "{{ vcenter_hostname }}"
  201 |         username: "{{ vcenter_username }}"
  202 |         password: "{{ vcenter_password }}"
  203 |         validate_certs: false
  204 |         datacenter: "{{ vcenter_datacenter }}"
  205 |         cluster: "{{ vcenter_cluster }}"
  206 |         folder: "{{ old_vm_info.virtual_machines[0].folder }}"
  207 |         name: "{{ replacement_vm }}"
  208 |         template: "{{ vm_template_name }}"
  209 |         state: powered-on
  210 |         disk: "{{ vm_disk_config_safe }}"
  211 |         hardware:
  212 |           memory_mb: "{{ old_vm_info.virtual_machines[0].allocated.memory | int | default(16384) }}"
  213 |           num_cpus: "{{ old_vm_info.virtual_machines[0].allocated.cpu | int | default(2) }}"
  214 |           num_cpu_cores_per_socket: "{{ vm_cpu_cores | default(1) }}"
  215 |           scsi: paravirtual
  216 |           version: latest
  217 |           boot_firmware: efi
  218 |         networks:
  219 |           - name: "{{ old_vm_net_info.network_info[0].network_name }}"
  220 |             mac: "{{ old_vm_net_info.network_info[0].mac_address }}"
  221 |             connected: true
  222 |             start_connected: true
  223 |             device_type: vmxnet3
  224 |         wait_for_ip_address: true
  225 |         wait_for_ip_address_timeout: 120
  226 | 
  227 |     - name: Ensure NIC is connected now and at boot
  228 |       community.vmware.vmware_guest_network:
  229 |         hostname: "{{ vcenter_hostname }}"
  230 |         username: "{{ vcenter_username }}"
  231 |         password: "{{ vcenter_password }}"
  232 |         validate_certs: false
  233 |         datacenter: "{{ vcenter_datacenter }}"
  234 |         name: "{{ replacement_vm }}"
  235 |         mac_address: "{{ old_vm_net_info.network_info[0].mac_address }}"
  236 |         network_name: "{{ old_vm_net_info.network_info[0].network_name }}"
  237 |         connected: true
  238 |         start_connected: true
  239 |         state: present
  240 | 
  241 |     - name: Verify NIC connection status
  242 |       community.vmware.vmware_guest_network:
  243 |         hostname: "{{ vcenter_hostname }}"
  244 |         username: "{{ vcenter_username }}"
  245 |         password: "{{ vcenter_password }}"
  246 |         validate_certs: false
  247 |         datacenter: "{{ vcenter_datacenter }}"
  248 |         name: "{{ replacement_vm }}"
  249 |         gather_network_info: true
  250 |       register: verify_net
  251 | 
  252 |     - name: Show adapter connection state
  253 |       ansible.builtin.debug:
  254 |         msg: >-
  255 |           {{ verify_net.network_info
  256 |              | map(attribute='connected')
  257 |              | list }}
  258 | 
  259 |     - name: Print out relevant details of old VM
  260 |       vars:
  261 |         msg: |
  262 |              The VM you replaced had
  263 |              an UUID of {{ old_vm_info.virtual_machines[0].uuid }}
  264 |              a mac address of {{ old_vm_info.virtual_machines[0].mac_address[0] }}
  265 |              an IP address of {{ old_vm_info.virtual_machines[0].ip_address }}
  266 |              in the {{ old_vm_net_info.network_info[0].network_name }} network
  267 |              {{ old_vm_info.virtual_machines[0].allocated.cpu }} CPUs
  268 |              {{ (old_vm_info.virtual_machines[0].allocated.memory | int / 1024) }} GB of memory
  269 |              {{ old_vm_info.virtual_machines[0].allocated.storage | human_readable }} of disk allocated
  270 |              {{ vm_disk_config_safe | length }} disk(s)
  271 |       ansible.builtin.debug:
  272 |         msg: "{{ msg.split('\n') }}"
  273 | 
  274 |     - name: Gather details on new VM
  275 |       community.vmware.vmware_vm_info:
  276 |         hostname: "{{ vcenter_hostname }}"
  277 |         username: "{{ vcenter_username }}"
  278 |         password: "{{ vcenter_password }}"
  279 |         validate_certs: false
  280 |         show_allocated: true
  281 |         vm_name: "{{ replacement_vm }}"
  282 |       register: new_vm_info
  283 | 
  284 |     - name: Gather network info new VM
  285 |       community.vmware.vmware_guest_network:
  286 |         hostname: "{{ vcenter_hostname }}"
  287 |         username: "{{ vcenter_username }}"
  288 |         password: "{{ vcenter_password }}"
  289 |         name: "{{ replacement_vm }}"
  290 |         validate_certs: false
  291 |         gather_network_info: true
  292 |       register: new_vm_net_info
  293 | 
  294 |     - name: Gather disk info on new VM
  295 |       community.vmware.vmware_guest_disk:
  296 |         hostname: "{{ vcenter_hostname }}"
  297 |         username: "{{ vcenter_username }}"
  298 |         password: "{{ vcenter_password }}"
  299 |         validate_certs: false
  300 |         datacenter: "{{ vcenter_datacenter }}"
  301 |         name: "{{ replacement_vm }}"
  302 |       register: new_vm_disk_info
  303 |       ignore_errors: true
  304 | 
  305 |     - name: Print out relevant details of new VM
  306 |       vars:
  307 |         msg: |
  308 |              The VM you just created has
  309 |              an UUID of {{ new_vm_info.virtual_machines[0].uuid }}
  310 |              a mac address of {{ new_vm_info.virtual_machines[0].mac_address[0] }}
  311 |              in the {{ new_vm_net_info.network_info[0].network_name }} network
  312 |              an IP address of {{ new_vm_info.virtual_machines[0].ip_address }}
  313 |              {{ new_vm_info.virtual_machines[0].allocated.cpu }} CPUs
  314 |              {{ (new_vm_info.virtual_machines[0].allocated.memory | int / 1024) }} GB of memory
  315 |              {{ new_vm_info.virtual_machines[0].allocated.storage | human_readable }} of disk allocated
  316 |              {{ (new_vm_disk_info.guest_disk_info.keys() | list | length) if (new_vm_disk_info.guest_disk_info is defined) else vm_disk_config_safe | length }} disk(s) configured
  317 |       ansible.builtin.debug:
  318 |         msg: "{{ msg.split('\n') }}"
  319 | 
  320 |     - name: Remove old VM using UUID
  321 |       community.vmware.vmware_guest:
  322 |         hostname: "{{ vcenter_hostname }}"
  323 |         username: "{{ vcenter_username }}"
  324 |         password: "{{ vcenter_password }}"
  325 |         validate_certs: false
  326 |         datacenter: "{{ vcenter_datacenter }}"
  327 |         cluster: "{{ vcenter_cluster }}"
  328 |         folder: "{{ vm_dest_folder }}"
  329 |         uuid: "{{ old_vm_info.virtual_machines[0].uuid }}"
  330 |         state: absent
  331 |         force: true
  332 |       when: vm_dest_folder is search("ToBeDeleted")
  333 | 
  334 |     - name: Remove host from TowerDeploy1 known hosts
  335 |       ansible.builtin.known_hosts:
  336 |         path: /home/deploy/.ssh/known_hosts
  337 |         name: "{{ vm_fqdn }}"
  338 |         state: absent
  339 |       delegate_to: towerdeploy1.princeton.edu
  340 |       become: true
  341 |       become_user: deploy
  342 | 
  343 |   post_tasks:
  344 |     - name: Create summary report
  345 |       set_fact:
  346 |         replacement_summary: |
  347 |           ========================================
  348 |           VM REPLACEMENT SUMMARY
  349 |           ========================================
  350 |           VM Name: {{ replacement_vm }}
  351 |           FQDN: {{ vm_fqdn }}
  352 |           Environment: {{ runtime_env | default('staging') }}
  353 | 
  354 |           OLD VM:
  355 |           - UUID: {{ old_vm_info.virtual_machines[0].uuid }}
  356 |           - Status: {% if vm_dest_folder is search("ToBeDeleted") %}Deleted{% else %}Moved to {{ vm_dest_folder }}{% endif %}
  357 | 
  358 |           TEMPLATE:
  359 |           - Name: {{ vm_template_name }}
  360 |           - Disks: {{ template_disk_config | length }}
  361 |           {% for disk in template_disk_config %}
  362 |           - Template Disk {{ loop.index }}: {{ disk.size_gb }}GB (unit {{ disk.unit_number }})
  363 |           {% endfor %}
  364 | 
  365 |           NEW VM:
  366 |           - UUID: {{ new_vm_info.virtual_machines[0].uuid }}
  367 |           - IP: {{ new_vm_info.virtual_machines[0].ip_address | default('Not yet assigned') }}
  368 |           - CPUs: {{ new_vm_info.virtual_machines[0].allocated.cpu }}
  369 |           - Memory: {{ (new_vm_info.virtual_machines[0].allocated.memory | int / 1024) }}GB
  370 |           - Disks: {{ vm_disk_config_safe | length }}
  371 |           {% for disk in vm_disk_config_safe %}
  372 |           - Disk {{ loop.index }}: {{ disk.size_gb }}GB (unit {{ disk.unit_number }})
  373 |           {% endfor %}
  374 |           ========================================
  375 | 
  376 |     - name: Display final summary
  377 |       debug:
  378 |         msg: "{{ replacement_summary.split('\n') }}"
  379 | 
  380 |     - name: send information to slack
  381 |       ansible.builtin.include_tasks:
  382 |         file: slack_tasks_end_of_playbook.yml
```

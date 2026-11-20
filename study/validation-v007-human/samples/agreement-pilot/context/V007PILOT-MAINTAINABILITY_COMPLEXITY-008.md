# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-008

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/utils/create_proxmox_vm.yml` (reported anchor line 1)
- Object: `source_location` `f06f5ef52b7759cd8ef07fe54ece0021a8bd21b3dd078257fad3ec0939da3988`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–267 of 267:

```text
    1 | ---
    2 | #  This playbook should only be run from ansible tower. No need for detailed instructions or examples here, because you should not run it here.
    3 | #
    4 | - name: Create a Proxmox VM from a cluster template
    5 |   hosts: localhost
    6 |   connection: local
    7 |   gather_facts: false
    8 | 
    9 |   collections:
   10 |     - community.proxmox
   11 | 
   12 |   vars:
   13 | 
   14 |     # Required deployment variables. Supply these with -e or a vars file.
   15 |     # proxmox_template_vmid: 1002
   16 |     # proxmox_vm_vmid: 1200
   17 |     # proxmox_vm_name: sandbox-example1
   18 | 
   19 |     # PUL Proxmox cluster defaults.
   20 |     proxmox_target_node: lib-pxserv01a
   21 |     proxmox_target_storage: Lib-Storage-VMs
   22 |     proxmox_vm_bridge: vmbr0
   23 | 
   24 |     # Clone options.
   25 |     proxmox_clone_full: true
   26 |     proxmox_clone_format: qcow2
   27 |     proxmox_clone_timeout: 1800
   28 | 
   29 |     # VM hardware.
   30 |     proxmox_vm_cores: 2
   31 |     proxmox_vm_sockets: 1
   32 |     proxmox_vm_memory_mb: 8192
   33 |     proxmox_vm_balloon_mb: 0
   34 |     proxmox_vm_agent: enabled=1,fstrim_cloned_disks=1
   35 |     proxmox_vm_onboot: true
   36 |     proxmox_vm_protection: false
   37 |     proxmox_vm_tags:
   38 |       - ansible-managed
   39 |     proxmox_vm_description: >-
   40 |       Created by Ansible from Proxmox source VMID
   41 |       {{ proxmox_template_vmid | default('unknown') }}.
   42 | 
   43 |     # NIC configuration. proxmox_nic preserves the cloned MAC when mac is omitted.
   44 |     proxmox_configure_nic: true
   45 |     proxmox_vm_nic: net0
   46 |     proxmox_vm_nic_model: virtio
   47 |     proxmox_vm_firewall: true
   48 |     proxmox_vm_vlan_tag: null
   49 | 
   50 |     # Cloud-init configuration for the Noble and Rocky templates.
   51 |     proxmox_cloud_init_enabled: true
   52 |     proxmox_vm_ciuser: pulsys
   53 |     proxmox_vm_ciupgrade: false
   54 |     proxmox_vm_ipconfig0: ip=dhcp
   55 |     proxmox_vm_sshkeys: "{{ lookup('env', 'PROXMOX_VM_SSH_KEYS') }}"
   56 |     proxmox_vm_nameservers: []
   57 |     proxmox_vm_searchdomains: []
   58 | 
   59 |     # Proxmox can grow disks but cannot shrink them through the API.
   60 |     proxmox_vm_disk: scsi0
   61 |     proxmox_vm_disk_size: null
   62 | 
   63 |     proxmox_vm_start: true
   64 | 
   65 |   module_defaults:
   66 |     group/community.proxmox.proxmox:
   67 |       api_host: "{{ proxmox_api_host }}"
   68 |       api_user: "{{ proxmox_api_user }}"
   69 |       api_token_id: "{{ proxmox_api_token_id }}"
   70 |       api_token_secret: "{{ proxmox_api_token_secret }}"
   71 |       validate_certs: "{{ proxmox_validate_certs }}"
   72 |       api_timeout: 30
   73 | 
   74 |   tasks:
   75 |     - name: Validate required input and API credentials
   76 |       ansible.builtin.assert:
   77 |         that:
   78 |           - proxmox_template_vmid is defined
   79 |           - proxmox_vm_vmid is defined
   80 |           - proxmox_vm_name is defined
   81 |           - proxmox_vm_name | length > 0
   82 |           - proxmox_template_vmid | int != proxmox_vm_vmid | int
   83 |           - proxmox_api_host | length > 0
   84 |           - proxmox_api_user | length > 0
   85 |           - proxmox_api_token_id | length > 0
   86 |           - proxmox_api_token_secret | length > 0
   87 |         fail_msg: >-
   88 |           Set proxmox_template_vmid, proxmox_vm_vmid, and proxmox_vm_name.
   89 |           Export PROXMOX_USER, PROXMOX_TOKEN_ID, and
   90 |           PROXMOX_TOKEN_SECRET before running the playbook.
   91 | 
   92 |     - name: Look up the source template or stopped source VM
   93 |       community.proxmox.proxmox_vm_info:
   94 |         vmid: "{{ proxmox_template_vmid | int }}"
   95 |         type: qemu
   96 |         config: current
   97 |       register: proxmox_source_lookup
   98 | 
   99 |     - name: Verify the source VM exists and is safe to clone
  100 |       ansible.builtin.assert:
  101 |         that:
  102 |           - proxmox_source_lookup.proxmox_vms | length == 1
  103 |           - >-
  104 |             (proxmox_source_lookup.proxmox_vms[0].template | default(false) | bool)
  105 |             or
  106 |             (proxmox_source_lookup.proxmox_vms[0].status == 'stopped')
  107 |         fail_msg: >-
  108 |           Source VMID {{ proxmox_template_vmid }} was not found, or it is a
  109 |           non-template VM that is currently running.
  110 | 
  111 |     - name: Save source VM information
  112 |       ansible.builtin.set_fact:
  113 |         proxmox_source_vm: "{{ proxmox_source_lookup.proxmox_vms[0] }}"
  114 | 
  115 |     - name: Look up the requested target VMID
  116 |       community.proxmox.proxmox_vm_info:
  117 |         vmid: "{{ proxmox_vm_vmid | int }}"
  118 |         type: qemu
  119 |         config: current
  120 |       register: proxmox_target_id_lookup
  121 | 
  122 |     - name: Look up the requested target name
  123 |       community.proxmox.proxmox_vm_info:
  124 |         name: "{{ proxmox_vm_name }}"
  125 |         type: qemu
  126 |         config: current
  127 |       register: proxmox_target_name_lookup
  128 | 
  129 |     - name: Reject conflicting target VMID or VM name
  130 |       ansible.builtin.assert:
  131 |         that:
  132 |           - proxmox_target_id_lookup.proxmox_vms | length <= 1
  133 |           - proxmox_target_name_lookup.proxmox_vms | length <= 1
  134 |           - >-
  135 |             (proxmox_target_id_lookup.proxmox_vms | length == 0)
  136 |             or
  137 |             (proxmox_target_id_lookup.proxmox_vms[0].name == proxmox_vm_name)
  138 |           - >-
  139 |             (proxmox_target_name_lookup.proxmox_vms | length == 0)
  140 |             or
  141 |             (proxmox_target_name_lookup.proxmox_vms[0].vmid | int
  142 |              == proxmox_vm_vmid | int)
  143 |         fail_msg: >-
  144 |           The requested VMID or VM name is already assigned to a different VM.
  145 |           Choose a unique proxmox_vm_vmid and proxmox_vm_name.
  146 | 
  147 |     - name: Clone the source into a full VM copy
  148 |       community.proxmox.proxmox_kvm:
  149 |         clone: "{{ proxmox_source_vm.name }}"
  150 |         vmid: "{{ proxmox_template_vmid | int }}"
  151 |         newid: "{{ proxmox_vm_vmid | int }}"
  152 |         name: "{{ proxmox_vm_name }}"
  153 |         node: "{{ proxmox_source_vm.node }}"
  154 |         target: >-
  155 |           {{ proxmox_target_node
  156 |              if proxmox_target_node != proxmox_source_vm.node
  157 |              else omit }}
  158 |         storage: "{{ proxmox_target_storage }}"
  159 |         full: "{{ proxmox_clone_full }}"
  160 |         format: >-
  161 |           {{ proxmox_clone_format if proxmox_clone_full else 'unspecified' }}
  162 |         timeout: "{{ proxmox_clone_timeout }}"
  163 |       when: proxmox_target_id_lookup.proxmox_vms | length == 0
  164 |       register: proxmox_clone_result
  165 | 
  166 |     - name: Read the cloned or existing target VM
  167 |       community.proxmox.proxmox_vm_info:
  168 |         vmid: "{{ proxmox_vm_vmid | int }}"
  169 |         type: qemu
  170 |         config: current
  171 |       register: proxmox_target_lookup
  172 |       retries: 12
  173 |       delay: 5
  174 |       until: proxmox_target_lookup.proxmox_vms | length == 1
  175 | 
  176 |     - name: Save target VM information
  177 |       ansible.builtin.set_fact:
  178 |         proxmox_target_vm: "{{ proxmox_target_lookup.proxmox_vms[0] }}"
  179 | 
  180 |     - name: Configure VM hardware and metadata
  181 |       community.proxmox.proxmox_kvm:
  182 |         vmid: "{{ proxmox_vm_vmid | int }}"
  183 |         name: "{{ proxmox_vm_name }}"
  184 |         node: "{{ proxmox_target_vm.node }}"
  185 |         cores: "{{ proxmox_vm_cores | int }}"
  186 |         sockets: "{{ proxmox_vm_sockets | int }}"
  187 |         memory: "{{ proxmox_vm_memory_mb | int }}"
  188 |         balloon: "{{ proxmox_vm_balloon_mb | int }}"
  189 |         agent: "{{ proxmox_vm_agent }}"
  190 |         onboot: "{{ proxmox_vm_onboot | bool }}"
  191 |         protection: "{{ proxmox_vm_protection | bool }}"
  192 |         tags: "{{ proxmox_vm_tags }}"
  193 |         description: "{{ proxmox_vm_description }}"
  194 |         update: true
  195 | 
  196 |     - name: Configure cloud-init values
  197 |       community.proxmox.proxmox_kvm:
  198 |         vmid: "{{ proxmox_vm_vmid | int }}"
  199 |         name: "{{ proxmox_vm_name }}"
  200 |         node: "{{ proxmox_target_vm.node }}"
  201 |         ciuser: "{{ proxmox_vm_ciuser }}"
  202 |         ciupgrade: "{{ proxmox_vm_ciupgrade | bool }}"
  203 |         sshkeys: >-
  204 |           {{ proxmox_vm_sshkeys
  205 |              if proxmox_vm_sshkeys | length > 0
  206 |              else omit }}
  207 |         nameservers: >-
  208 |           {{ proxmox_vm_nameservers
  209 |              if proxmox_vm_nameservers | length > 0
  210 |              else omit }}
  211 |         searchdomains: >-
  212 |           {{ proxmox_vm_searchdomains
  213 |              if proxmox_vm_searchdomains | length > 0
  214 |              else omit }}
  215 |         ipconfig:
  216 |           ipconfig0: "{{ proxmox_vm_ipconfig0 }}"
  217 |         update: true
  218 |       when: proxmox_cloud_init_enabled | bool
  219 | 
  220 |     - name: Configure the primary NIC without changing its MAC address
  221 |       community.proxmox.proxmox_nic:
  222 |         vmid: "{{ proxmox_vm_vmid | int }}"
  223 |         name: "{{ proxmox_vm_name }}"
  224 |         interface: "{{ proxmox_vm_nic }}"
  225 |         bridge: "{{ proxmox_vm_bridge }}"
  226 |         model: "{{ proxmox_vm_nic_model }}"
  227 |         firewall: "{{ proxmox_vm_firewall | bool }}"
  228 |         tag: >-
  229 |           {{ proxmox_vm_vlan_tag
  230 |              if proxmox_vm_vlan_tag is not none
  231 |              else omit }}
  232 |         state: present
  233 |       when: proxmox_configure_nic | bool
  234 | 
  235 |     - name: Grow the root disk when a larger size was requested
  236 |       community.proxmox.proxmox_disk:
  237 |         vmid: "{{ proxmox_vm_vmid | int }}"
  238 |         disk: "{{ proxmox_vm_disk }}"
  239 |         size: "{{ proxmox_vm_disk_size }}"
  240 |         state: resized
  241 |       when:
  242 |         - proxmox_vm_disk_size is not none
  243 |         - proxmox_vm_disk_size | string | length > 0
  244 | 
  245 |     - name: Start the VM
  246 |       community.proxmox.proxmox_kvm:
  247 |         vmid: "{{ proxmox_vm_vmid | int }}"
  248 |         state: started
  249 |         timeout: 300
  250 |       when: proxmox_vm_start | bool
  251 | 
  252 |     - name: Show deployment summary
  253 |       ansible.builtin.debug:
  254 |         msg:
  255 |           vmid: "{{ proxmox_vm_vmid | int }}"
  256 |           name: "{{ proxmox_vm_name }}"
  257 |           source_vmid: "{{ proxmox_template_vmid | int }}"
  258 |           source_name: "{{ proxmox_source_vm.name }}"
  259 |           node: "{{ proxmox_target_vm.node }}"
  260 |           storage: "{{ proxmox_target_storage }}"
  261 |           bridge: "{{ proxmox_vm_bridge }}"
  262 |           cloud_init_ip: >-
  263 |             {{ proxmox_vm_ipconfig0
  264 |                if proxmox_cloud_init_enabled | bool
  265 |                else 'inherited from source' }}
  266 |           desired_state: >-
  267 |             {{ 'started' if proxmox_vm_start | bool else 'stopped' }}
```

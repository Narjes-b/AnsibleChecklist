# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-003

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: maintainability_complexity
- Rule: `ansibleguard/deprecated-modules`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `plugins/tripleo-overcloud/tasks/upgrade/11/main.yml` (reported anchor line 137)
- Flagged construct: task `unnamed task`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–264 of 264:

```text
    1 | ---
    2 | - name: Generate ~/deprecated_cli_options.yaml
    3 |   include_tasks: convert_cli_options.yml
    4 |   vars:
    5 |       value_list:
    6 |           - searched: neutron-flat-networks
    7 |             parameter_name: NeutronFlatNetworks
    8 |           - searched: neutron-physical-bridge
    9 |             parameter_name: NeutronPhysicalBridge
   10 |           - searched: neutron-bridge-mappings
   11 |             parameter_name: NeutronBridgeMappings
   12 |           - searched: neutron-public-interface
   13 |             parameter_name: NeutronPublicInterface
   14 |           - searched: neutron-network-type
   15 |             parameter_name: NeutronNetworkType
   16 |           - searched: neutron-tunnel-types
   17 |             parameter_name: NeutronTunnelTypes
   18 |           - searched: neutron-disable-tunneling
   19 |             parameter_name: NeutronTunnelTypes
   20 |           - searched: neutron-tunnel-id-ranges
   21 |             parameter_name: NeutronTunnelIdRanges
   22 |           - searched: neutron-vni-ranges
   23 |             parameter_name: NeutronVniRanges
   24 |           - searched: neutron-network-vlan-ranges
   25 |             parameter_name: NeutronNetworkVLANRanges
   26 |           - searched: neutron-mechanism-drivers
   27 |             parameter_name: NeutronMechanismDrivers
   28 |   with_items: "{{ value_list }}"
   29 |   tags: convert_cli_options
   30 | 
   31 | - name: Check for ~/deprecated_cli_options.yaml
   32 |   stat:
   33 |       path: ~/deprecated_cli_options.yaml
   34 |   register: is_deprecated
   35 |   tags: convert_cli_options
   36 | 
   37 | - block:
   38 |     - name: Store last deploy command line
   39 |       command: "tail -1 {{ overcloud_upgrade_script }}"
   40 |       register: deploy_lastline
   41 | 
   42 |     - name: Add the environment to the deploy command
   43 |       lineinfile:
   44 |           dest: "{{ overcloud_upgrade_script }}"
   45 |           insertbefore: "{{ deploy_lastline.stdout }}"
   46 |           line: "-e ~/deprecated_cli_options.yaml \\"
   47 |   when: is_deprecated.stat.exists
   48 |   tags: convert_cli_options
   49 | 
   50 | - name: Determine if a custom roles_data was used
   51 |   shell: "grep '\\-r\\ \\|\\-\\-roles' {{ overcloud_upgrade_script }}"
   52 |   ignore_errors: true
   53 |   register: is_roles
   54 |   tags: convert_roles_data
   55 | 
   56 | - name: Convert roles_data.yaml
   57 |   include_tasks: convert_roles_data.yml
   58 |   when: is_roles.rc == 0
   59 |   tags: convert_roles_data
   60 | 
   61 | - block:
   62 |     - debug:
   63 |           msg: "Starting floating IP dataplane ping check during major upgrade"
   64 |     - include: ../../update/common/startping.yaml
   65 |   when: install.dataplaneping|default(False)
   66 |   vars:
   67 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
   68 | 
   69 | - name: Initiate composable upgrade process
   70 |   include_tasks: composable_upgrade.yml
   71 |   tags: composable_upgrade
   72 |   vars:
   73 |       composable_upgrade_script: "~/overcloud_upgrade_composable.sh"
   74 | 
   75 | - block:
   76 |     - debug:
   77 |           msg: "Ending floating IP dataplane ping check during major upgrade"
   78 |     - include: ../../update/common/endping.yaml
   79 |   when: install.dataplaneping|default(False)
   80 | 
   81 | - name: Grab auth data from {{ overcloud_rc }} file and publish it as YAML
   82 |   shell: |
   83 |       source {{ overcloud_rc }}
   84 |       echo "
   85 |       auth_url: $OS_AUTH_URL
   86 |       username: $OS_USERNAME
   87 |       password: [REDACTED_LITERAL]
   88 |       project_name: ${OS_PROJECT_NAME:-$OS_TENANT_NAME}
   89 |       "
   90 |       if [ -n "$OS_PROJECT_DOMAIN_NAME" ]; then
   91 |           echo "project_domain_name: $OS_PROJECT_DOMAIN_NAME"
   92 |       fi
   93 |       if [ -n "$OS_USER_DOMAIN_NAME" ]; then
   94 |           echo "user_domain_name: $OS_USER_DOMAIN_NAME"
   95 |       fi
   96 |   register: creds
   97 | 
   98 | - block:
   99 |     - debug:
  100 |           msg: "Starting floating IP dataplane ping check during major upgrade"
  101 |     - include: ../../update/common/startping.yaml
  102 |   when: install.dataplaneping|default(False)
  103 |   vars:
  104 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  105 | 
  106 | - name: Compute Upgrade
  107 |   include_tasks: compute_upgrade.yml
  108 |   with_items: "{{ groups.compute|default([])|difference(groups.unused|default([])) }}"
  109 |   loop_control:
  110 |       loop_var: node_name
  111 |   tags: computes_upgrade
  112 | 
  113 | - block:
  114 |     - debug:
  115 |           msg: "Ending floating IP dataplane ping check during major upgrade"
  116 |     - include: ../../update/common/endping.yaml
  117 |   when: install.dataplaneping|default(False)
  118 | 
  119 | - block:
  120 |     - debug:
  121 |           msg: "Starting floating IP dataplane ping check during major upgrade"
  122 |     - include: ../../update/common/startping.yaml
  123 |   when: install.dataplaneping|default(False)
  124 |   vars:
  125 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  126 | 
  127 | - name: Swift Upgrade
  128 |   include_tasks: swift_upgrade.yml
  129 |   with_items: "{{ groups.swift|default([])|difference(groups.unused|default([])) }}"
  130 |   loop_control:
  131 |       loop_var: node_name
  132 |   tags: swift_upgrade
  133 | 
  134 | - block:
  135 |     - debug:
  136 |           msg: "Ending floating IP dataplane ping check during major upgrade"
  137 |     - include: ../../update/common/endping.yaml
  138 |   when: install.dataplaneping|default(False)
  139 | 
  140 | - block:
  141 |     - debug:
  142 |           msg: "Starting floating IP dataplane ping check during major upgrade"
  143 |     - include: ../../update/common/startping.yaml
  144 |   when: install.dataplaneping|default(False)
  145 |   vars:
  146 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  147 | 
  148 | - name: Converge
  149 |   include_tasks: converge_upgrade.yml
  150 |   tags: converge_upgrade
  151 |   vars:
  152 |       converge_script: "~/overcloud_upgrade_converge.sh"
  153 | 
  154 | - block:
  155 |     - debug:
  156 |           msg: "Ending floating IP dataplane ping check during major upgrade"
  157 |     - include: ../../update/common/endping.yaml
  158 |   when: install.dataplaneping|default(False)
  159 | 
  160 | - block:
  161 |     - debug:
  162 |           msg: "Starting floating IP dataplane ping check during major upgrade"
  163 |     - include: ../../update/common/startping.yaml
  164 |   when: install.dataplaneping|default(False)
  165 |   vars:
  166 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  167 | 
  168 | - name: Ceph Upgrade
  169 |   include_tasks: ceph_upgrade.yml
  170 |   with_items: "{{ groups.ceph|default([])|difference(groups.unused|default([])) }}"
  171 |   loop_control:
  172 |       loop_var: node_name
  173 |   tags: upgrade_ceph
  174 | 
  175 | - block:
  176 |     - debug:
  177 |           msg: "Ending floating IP dataplane ping check during major upgrade"
  178 |     - include: ../../update/common/endping.yaml
  179 |   when: install.dataplaneping|default(False)
  180 | 
  181 | - name: List custom roles nodes < 17
  182 |   shell: |
  183 |       source {{ undercloud_rc }}
  184 |       openstack server list -f json
  185 |   register: custom_nodes
  186 |   tags: custom_role_post
  187 |   when:
  188 |     - install.openstack.version|default(overcloud_version)|openstack_release < 17
  189 | 
  190 | - name: List custom roles nodes >= 17
  191 |   shell: |
  192 |     source {{ undercloud_rc }}
  193 |     metalsmith -f json list
  194 |   register: custom_nodes
  195 |   tags: custom_role_post
  196 |   when:
  197 |     - install.openstack.version|default(overcloud_version)|openstack_release >= 17
  198 | 
  199 | - block:
  200 |     - debug:
  201 |           msg: "Starting floating IP dataplane ping check during major upgrade"
  202 |     - include: ../../update/common/startping.yaml
  203 |   when: install.dataplaneping|default(False)
  204 |   vars:
  205 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  206 | 
  207 | - include_tasks: custom_roles_upgrade.yml < 17
  208 |   with_items: "{{ custom_nodes.stdout|default([]) }}"
  209 |   when:
  210 |       - "'objectstorage' not in '{{ item.Name }}'"
  211 |       - "'swift-r' not in '{{ item.Name }}'"
  212 |       - "'ceph' not in '{{ item.Name }}'"
  213 |       - "'stor-r' not in '{{ item.Name }}'"
  214 |       - "'controller' not in '{{ item.Name }}'"
  215 |       - "'ctrl' not in '{{ item.Name }}'"
  216 |       - "'compute' not in '{{ item.Name }}'"
  217 |       - "'comp' not in '{{ item.Name }}'"
  218 |       - install.openstack.version|default(overcloud_version)|openstack_release < 17
  219 |   vars:
  220 |       node_name: "{{ item.Name }}"
  221 |   tags: custom_role_post
  222 | 
  223 | - include_tasks: custom_roles_upgrade.yml >= 17
  224 |   with_items: "{{ custom_nodes.stdout|default([]) }}"
  225 |   when:
  226 |       - "'objectstorage' not in '{{ item.name }}'"
  227 |       - "'swift-r' not in '{{ item.name }}'"
  228 |       - "'ceph' not in '{{ item.name }}'"
  229 |       - "'stor-r' not in '{{ item.name }}'"
  230 |       - "'controller' not in '{{ item.name }}'"
  231 |       - "'ctrl' not in '{{ item.name }}'"
  232 |       - "'compute' not in '{{ item.name }}'"
  233 |       - "'comp' not in '{{ item.name }}'"
  234 |       - install.openstack.version|default(overcloud_version)|openstack_release >= 17
  235 |   vars:
  236 |       node_name: "{{ item.name }}"
  237 |   tags: custom_role_post
  238 | 
  239 | - block:
  240 |     - debug:
  241 |           msg: "Ending floating IP dataplane ping check during major upgrade"
  242 |     - include: ../../update/common/endping.yaml
  243 |   when: install.dataplaneping|default(False)
  244 | 
  245 | - block:
  246 |     - debug:
  247 |           msg: "Starting floating IP dataplane ping check during major upgrade"
  248 |     - include: ../../update/common/startping.yaml
  249 |   when: install.dataplaneping|default(False)
  250 |   vars:
  251 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  252 | 
  253 | - name: Post upgrade controller nodes
  254 |   include_tasks: controller_postupgrade.yml
  255 |   with_items: "{{ groups.controller|default([])|difference(groups.unused|default([])) }}"
  256 |   loop_control:
  257 |       loop_var: node_name
  258 |   tags: controller_post
  259 | 
  260 | - block:
  261 |     - debug:
  262 |           msg: "Ending floating IP dataplane ping check during major upgrade"
  263 |     - include: ../../update/common/endping.yaml
  264 |   when: install.dataplaneping|default(False)
```

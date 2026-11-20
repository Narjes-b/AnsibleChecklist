# Frozen source context: V007PILOT2-STRUCTURE_REUSE-002

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: structure_reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `ansible/playbook/ocp/ocp_openstack_create_jump_server.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`ansible/playbook/ocp/ocp_openstack_create_jump_server.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–265 of 265:

```text
    1 | ---
    2 | # Requires:
    3 | # vars:
    4 | #   tmp_directory: temporary directory =/opt/ocp/_tmp/ansible.yxam0y7mbuild 
    5 | #   ocp_root_directory: /opt/ocp 
    6 | #   ocp_cluster_name: ocp-sdev 
    7 | #   vm_name: ocp-sdev-p75fs-jump-server
    8 | - name: "Build OpenStack authentication for v3password"
    9 |   ansible.builtin.import_playbook: "../openstack/openstack_auth_passstore_v3password.yml"
   10 | 
   11 | - name: "Load the metadata from the OCP installation directory"
   12 |   hosts: "{{ ocp_bootstrap_host | default('localhost') }}"
   13 |   gather_facts: true
   14 | 
   15 |   tasks:
   16 | 
   17 |     - name: Calculate installation folder
   18 |       ansible.builtin.set_fact:
   19 |         installation_dir: "{{ ocp_root_directory }}/{{ ocp_cluster_name }}"
   20 | 
   21 |     # - name: "Load metadata from ansible installation folder"
   22 |     #   ansible.builtin.set_fact:
   23 |     #     ocp_cluster_metadata: "{{ lookup('file', installation_dir + '/metadata.json') | from_json }}"
   24 | 
   25 |     - name: Get OCP cluster metadata
   26 |       ansible.builtin.import_role:
   27 |         name: ocp_cluster
   28 |         tasks_from: get_metadata.yml
   29 | 
   30 |     # - name: "Print facts"
   31 |     #   ansible.builtin.debug:
   32 |     #     msg: 
   33 |     #       # - "ocp_cluster_metadata: {{ ocp_cluster_metadata }}"
   34 |     #       # - "ansible_installation_folder_base64: {{ ansible_installation_folder_base64 }}"
   35 |     #       # - "kubeadmin_password: {{ kubeadmin_password }}"
   36 |     #       - "ocp_cluster_metadata: {{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
   37 |     #       - "ansible_installation_folder_base64: {{ hostvars[ocp_bootstrap_host]['install_dir'] }}"
   38 |     #       - "kubeadmin_password: {{ hostvars[ocp_bootstrap_host]['kubeadmin_password'] }}"
   39 |     #     verbosity: 1
   40 | 
   41 |     - name: "Collect bootstrap host facts into localhost"
   42 |       ansible.builtin.set_fact:
   43 |           ocp_cluster_metadata: "{{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
   44 |           # ansible_installation_folder_base64: "{{ query('passwordstore', 'openstack/' + ocp_bootstrap_host + '/install_dir' )[0] }}"
   45 |           ansible_installation_folder_base64: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/install_dir' )[0] }}"
   46 |           # kubeadmin_password: "{{ query('passwordstore', 'openstack/' + ocp_bootstrap_host + '/kubeadmin' )[0] }}"
   47 |           kubeadmin_password: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/kubeadmin' )[0] }}"
   48 |       when: ocp_bootstrap_host is defined
   49 |       delegate_facts: True
   50 |       delegate_to: localhost
   51 | 
   52 |     - name: "Print facts"
   53 |       ansible.builtin.debug:
   54 |         msg: 
   55 |           - "ocp_cluster_metadata: {{ ocp_cluster_metadata }}"
   56 |           - "ocp_cluster_metadata: {{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
   57 |           - "ocp_cluster_metadata: {{ hostvars['localhost']['ocp_cluster_metadata'] }}"
   58 | 
   59 | - name: "Deploy Jump Server"
   60 |   ansible.builtin.import_playbook: "../openstack/openstack_vm_create_passwordstore.yml"
   61 |   vars:
   62 |     state: present
   63 |     openstack:
   64 |       timeout: 300
   65 |       vm: 
   66 |         network: "{{ ocp_cluster_metadata.infraID }}-openshift"
   67 |         image: "Fedora-Cloud-Base-37"
   68 |         flavor: "m1.small"
   69 |     vm_name: "{{ ocp_cluster_metadata.infraID }}-jump-server"
   70 |     skip_post_installation: true
   71 | 
   72 | - name: "Create floating IP for Jump Server"
   73 |   hosts: localhost
   74 |   gather_facts: true
   75 | 
   76 |   tasks:
   77 | 
   78 |     - name: Getting fip by associated fixed IP address.
   79 |       openstack.cloud.floating_ip_info:
   80 |         auth: "{{ rhos_auth }}"
   81 |         auth_type: "{{ rhos_auth_type }}"
   82 |         fixed_ip_address: "{{ query('passwordstore', 'openstack/' + vm_name + '/ansible_ssh_host' )[0] }}"
   83 |       register: fip
   84 |       ignore_errors: true
   85 | 
   86 |     - name: "Print FIP query"
   87 |       ansible.builtin.debug:
   88 |         msg: 
   89 |           - "fip: {{ fip }}"
   90 |         verbosity: 1
   91 | 
   92 |     - name: "Set floating ip variable is already created"
   93 |       ansible.builtin.set_fact:
   94 |         jump_server_floating_ip: "{{ fip.floating_ips[0].floating_ip_address }}"
   95 |       when: not fip.failed and (fip.floating_ips | length > 0)
   96 | 
   97 |     - name: "Create Floating IP for Jump Server"
   98 |       openstack.cloud.floating_ip:
   99 |         auth: "{{ rhos_auth }}"
  100 |         auth_type: "{{ rhos_auth_type }}"
  101 |         state: present
  102 |         reuse: true
  103 |         server: "{{ ocp_cluster_metadata.infraID }}-jump-server"
  104 |         network: "{{ rhos_network | default('provider_net_cci_13') }}"
  105 |         # fixed_address: 192.0.2.3
  106 |         wait: true
  107 |         timeout: 180
  108 |       # ansible.builtin.shell: 
  109 |       #   cmd: |
  110 |       #     openstack --os-cloud openstack floating ip create --description "OCP API {{ ocp_cluster_name }}.{{ snowdrop_domain }}" -f value -c floating_ip_address {{ openstack_network_provider }}
  111 |       # args:
  112 |       #   chdir: "{{ work_directory }}"
  113 |       register: rhos_floating_ip_jump_server_res
  114 |       when: jump_server_floating_ip is not defined
  115 | 
  116 |     - name: "Set floating ip variable is already created"
  117 |       ansible.builtin.set_fact:
  118 |         jump_server_floating_ip: "{{ rhos_floating_ip_jump_server_res.floating_ip.fixed_ip_address }}"
  119 |       when: jump_server_floating_ip is not defined
  120 | 
  121 |     - name: "Store Floating IP on the passwordstore"
  122 |       ansible.builtin.set_fact:
  123 |         ansible_installation_folder_passwordstore: "{{ query('passwordstore', 'openstack/' + vm_name + '/floating_ip create=True userpass=' + jump_server_floating_ip )[0] }}"
  124 | 
  125 | - name:  "Wait for the VM to boot and we can ssh"
  126 |   hosts: "{{ vm_name | default([]) }}"
  127 |   gather_facts: no
  128 | 
  129 |   tasks:
  130 | 
  131 |     - name: "Wait for connection to host"
  132 |       ansible.builtin.wait_for:
  133 |         host: "{{ query('passwordstore', 'openstack/' + inventory_hostname + '/floating_ip')[0] }}"
  134 |         port: "{{ query('passwordstore', 'openstack/' + inventory_hostname + '/ansible_ssh_port')[0] }}"
  135 |         timeout: 120
  136 |       vars:
  137 |         ansible_connection: local
  138 |       register: wait_for_connection_reg
  139 | 
  140 |   post_tasks:
  141 | 
  142 |     - name: Refresh the inventory so the newly added host is available
  143 |       meta: refresh_inventory
  144 | 
  145 |     - name: "DON'T FORGET TO SECURE YOUR SERVER"
  146 |       ansible.builtin.debug:
  147 |         msg: 
  148 |           - "DON'T FORGET TO SECURE YOUR SERVER!!!"
  149 |           - ""
  150 |           - "Trying to start start server securization automatically."
  151 |           - "For manual execution: $ ansible-playbook ansible/playbook/sec_host.yml -e vm_name={{ vm_name }} -e provider=openstack"
  152 | 
  153 | - name: "Add to known hosts"
  154 |   hosts: localhost
  155 |   gather_facts: true
  156 | 
  157 |   tasks:
  158 | 
  159 |     - name: "Add host Floating IP to known hosts {{ hostvars[vm_name]['floating_ip'] }}"
  160 |       ansible.builtin.known_hosts:
  161 |         name: "{{ hostvars[vm_name]['floating_ip'] }}"
  162 |         key: "{{ lookup('pipe', 'ssh-keyscan {{ hostvars[vm_name].floating_ip }}') }}"
  163 |         hash_host: true
  164 | 
  165 | - name: "Add to known hosts"
  166 |   hosts: "{{ vm_name | default([]) }}"
  167 |   gather_facts: true
  168 | 
  169 |   tasks:
  170 | 
  171 |     - name: "Add host Floating IP to known hosts {{ hostvars[vm_name]['floating_ip'] }}"
  172 |       ansible.builtin.known_hosts:
  173 |         name: "{{ hostvars[vm_name]['floating_ip'] }}"
  174 |         key: "{{ lookup('pipe', 'ssh-keyscan {{ hostvars[vm_name].floating_ip }}') }}"
  175 |         hash_host: true
  176 | 
  177 | - name: "Extract installation dictory from passwordstore"
  178 |   hosts: "localhost"
  179 |   gather_facts: true
  180 | 
  181 |   tasks:
  182 | 
  183 |     - name: "Extract installation dictory from passwordstore"
  184 |       ansible.builtin.copy: 
  185 |         content: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '/install_dir')[0] | b64decode }}" 
  186 |         dest: /tmp/ocp-installation.tgz
  187 |       when: ocp_bootstrap_host is not defined
  188 | 
  189 |     - name: "Extract installation dictory from passwordstore"
  190 |       ansible.builtin.copy: 
  191 |         content: "{{ query('passwordstore', 'openstack/' + ocp_bootstrap_host + '/install_dir')[0] | b64decode }}" 
  192 |         dest: /tmp/ocp-installation.tgz
  193 |       when: ocp_bootstrap_host is defined
  194 | 
  195 | - name: "Post Jump Server OCP"
  196 |   hosts: "{{ vm_name | default([]) }}"
  197 |   gather_facts: true
  198 | 
  199 |   pre_tasks:
  200 |     - name: Set required variables
  201 |       ansible.builtin.set_fact:
  202 |         remote_bin_folder: /home/snowdrop/.local/bin
  203 | 
  204 |   tasks:
  205 |     - name: Create home .local/bin folder
  206 |       ansible.builtin.file:
  207 |         path: "{{ remote_bin_folder }}"
  208 |         recurse: true
  209 |         state: directory
  210 |         owner: "{{ ansible_user_id }}"
  211 |         group: "{{ ansible_user_id }}"
  212 |         mode: '0755'
  213 | 
  214 |     - name: Copy installation folder to remote host
  215 |       ansible.builtin.copy:
  216 |         src: /tmp/ocp-installation.tgz
  217 |         dest: /tmp/ocp-installation.tgz
  218 | 
  219 |     - name: Extract OCP installation into /home/snowdrop
  220 |       ansible.builtin.unarchive:
  221 |         src: /tmp/ocp-installation.tgz
  222 |         dest: /home/snowdrop
  223 | 
  224 | 
  225 |     # - name: Download OCP files
  226 |     #   ansible.builtin.import_role:
  227 |     #     name: ocp_cluster
  228 |     #     tasks_from: install_prepare.yml
  229 |     #   vars:
  230 |     #     ocp_bin_directory: "{{ remote_bin_folder }}"
  231 | 
  232 |     - name: Download OCP files
  233 |       ansible.builtin.import_role:
  234 |         name: ocp_cluster
  235 |         tasks_from: download_installation_files.yml
  236 |       vars:
  237 |         ocp_cluster_bin_directory: "{{ remote_bin_folder }}"
  238 | 
  239 |   post_tasks:
  240 | 
  241 |     - name: "DON'T FORGET TO SECURE YOUR SERVER"
  242 |       ansible.builtin.debug:
  243 |         msg: 
  244 |           - "DON'T FORGET TO SECURE YOUR SERVER!!!"
  245 |           - ""
  246 |           - "Trying to start start server securization automatically."
  247 |           - "For manual execution: $ ansible-playbook ansible/playbook/sec_host.yml -e vm_name={{ vm_name }} -e provider=openstack"
  248 | 
  249 | - name: "Init Jump Server"
  250 |   hosts: "{{ vm_name | default([]) }}"
  251 |   gather_facts: yes
  252 | 
  253 |   tasks:
  254 |     - name: Init RHOS VM
  255 |       ansible.builtin.include_role:
  256 |         name: "openstack/init_vm"
  257 | 
  258 | - name: "Secure Jump Server"
  259 |   ansible.builtin.import_playbook: "../sec_host.yml"
  260 |   vars:
  261 |     provider: "openstack"
  262 |     hosts: "{{ vm_name | default([]) }}"
  263 | 
  264 | ...
  265 | # ansible-playbook ansible/playbook/ocp/ocp_openstack_deploy_jump_server.yml -e tmp_directory=/opt/ocp/_tmp/ansible.yxam0y7mbuild -e ocp_root_directory=/opt/ocp -e ocp_cluster_name=ocp-sdev -e vm_name=ocp-sdev-p75fs-jump-server
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `.`; 722 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: yes

Listing exceeds 400: paths beside the cited file, then a per-directory count of ALL paths.
ansible/playbook/ocp/README.adoc
ansible/playbook/ocp/ocp_openstack_create_jump_server.yml
ansible/playbook/ocp/ocp_openstack_info.yml
ansible/playbook/ocp/ocp_openstack_install.yml
ansible/playbook/ocp/ocp_openstack_install_post.yml
ansible/playbook/ocp/ocp_openstack_remove.yml
ansible/playbook/ocp/ocp_openstack_test.yml
ansible/playbook/ocp/rhosp_init_jump_server_pass.yml

Per-directory path counts:
.: 7
.github/workflows: 3
_data: 1
ansible: 3
ansible/ansible_collections/snowdrop/godaddy: 2
ansible/ansible_collections/snowdrop/godaddy/meta: 1
ansible/ansible_collections/snowdrop/godaddy/playbooks: 1
ansible/ansible_collections/snowdrop/godaddy/plugins: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns: 2
ansible/ansible_collections/snowdrop/godaddy/roles/dns/defaults: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns/handlers: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns/meta: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns/molecule/default: 6
ansible/ansible_collections/snowdrop/godaddy/roles/dns/tasks: 3
ansible/ansible_collections/snowdrop/godaddy/roles/dns/templates: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns/vars: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns_info: 2
ansible/ansible_collections/snowdrop/godaddy/roles/dns_info/defaults: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns_info/handlers: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns_info/meta: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns_info/molecule/default: 6
ansible/ansible_collections/snowdrop/godaddy/roles/dns_info/tasks: 1
ansible/ansible_collections/snowdrop/godaddy/roles/dns_info/vars: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain: 2
ansible/ansible_collections/snowdrop/godaddy/roles/domain/defaults: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain/handlers: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain/meta: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain/molecule/default: 6
ansible/ansible_collections/snowdrop/godaddy/roles/domain/tasks: 3
ansible/ansible_collections/snowdrop/godaddy/roles/domain/templates: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain/vars: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain_info: 2
ansible/ansible_collections/snowdrop/godaddy/roles/domain_info/defaults: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain_info/handlers: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain_info/meta: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain_info/molecule/default: 6
ansible/ansible_collections/snowdrop/godaddy/roles/domain_info/tasks: 1
ansible/ansible_collections/snowdrop/godaddy/roles/domain_info/vars: 1
ansible/inventory: 4
ansible/playbook: 12
ansible/playbook/edu: 4
ansible/playbook/godaddy: 7
ansible/playbook/hetzner: 13
ansible/playbook/kubernetes: 11
ansible/playbook/ocp: 8
ansible/playbook/openstack: 18
ansible/playbook/passstore: [REDACTED_LITERAL]
ansible/playbook/tools: 5
ansible/roles: 1
ansible/roles/add_extra_users/defaults: 1
ansible/roles/add_extra_users/meta: 1
ansible/roles/add_extra_users/tasks: 1
ansible/roles/cfssl_tool/defaults: 1
ansible/roles/cfssl_tool/tasks: 1
ansible/roles/cluster/defaults: 1
ansible/roles/cluster/files: 3
ansible/roles/cluster/tasks: 16
ansible/roles/component_crd_operator/defaults: 1
ansible/roles/component_crd_operator/files: 5
ansible/roles/component_crd_operator/meta: 1
ansible/roles/component_crd_operator/tasks: 3
ansible/roles/component_crd_operator/templates: 2
ansible/roles/containerd: 1
ansible/roles/containerd/defaults: 1
ansible/roles/containerd/tasks: 3
ansible/roles/containerd/templates: 1
ansible/roles/containerd/vars: 1
ansible/roles/core/disable-swap: 1
ansible/roles/core/disable-swap/defaults: 1
ansible/roles/core/disable-swap/handlers: 1
ansible/roles/core/disable-swap/meta: 1
ansible/roles/core/disable-swap/tasks: 2
ansible/roles/core/disable-swap/vars: 5
ansible/roles/create_projects/tasks: 1
ansible/roles/delete_extra_users/defaults: 1
ansible/roles/delete_extra_users/meta: 1
ansible/roles/delete_extra_users/tasks: 1
ansible/roles/dns/tasks: 1
ansible/roles/dns/templates: 1
ansible/roles/docker: 1
ansible/roles/docker/defaults: 1
ansible/roles/docker/tasks: 5
ansible/roles/docker/vars: 3
ansible/roles/docker_config: 1
ansible/roles/docker_config/tasks: 1
ansible/roles/docker_registry/defaults: 1
ansible/roles/docker_registry/tasks: 4
ansible/roles/docker_registry/templates: 5
ansible/roles/enable_cluster_role/meta: 1
ansible/roles/enable_cluster_role/tasks: 1
ansible/roles/generate_inventory: 1
ansible/roles/generate_inventory/defaults: 1
ansible/roles/generate_inventory/tasks: 5
ansible/roles/generate_inventory/templates: 3
ansible/roles/halkyon/defaults: 1
ansible/roles/halkyon/files: 5
ansible/roles/halkyon/meta: 1
ansible/roles/halkyon/tasks: 10
ansible/roles/halkyon/templates: 5
ansible/roles/helm/defaults: 1
ansible/roles/helm/tasks: 1
ansible/roles/helm/templates: 1
ansible/roles/hetzner/activate_context: 1
ansible/roles/hetzner/activate_context/tasks: 1
ansible/roles/hetzner/create_context: 1
ansible/roles/hetzner/create_context/tasks: 1
ansible/roles/hetzner/create_context/vars: 5
ansible/roles/hetzner/create_server: 1
ansible/roles/hetzner/create_server/meta: 1
ansible/roles/hetzner/create_server/tasks: 1
ansible/roles/hetzner/create_server/templates: 2
ansible/roles/hetzner/create_ssh_key: 1
ansible/roles/hetzner/create_ssh_key/meta: 1
ansible/roles/hetzner/create_ssh_key/tasks: 1
ansible/roles/hetzner/delete_server: 1
ansible/roles/hetzner/delete_server/tasks: 1
ansible/roles/hetzner/delete_ssh_key: 1
ansible/roles/hetzner/delete_ssh_key/meta: 1
ansible/roles/hetzner/delete_ssh_key/tasks: 1
ansible/roles/hetzner/start_server: 1
ansible/roles/hetzner/start_server/tasks: 1
ansible/roles/hetzner/stop_server: 1
ansible/roles/hetzner/stop_server/tasks: 1
ansible/roles/identity_provider/meta: 1
ansible/roles/identity_provider/tasks: 1
ansible/roles/identity_provider/templates: 1
ansible/roles/ingress: 1
ansible/roles/ingress/defaults: 1
ansible/roles/ingress/tasks: 3
ansible/roles/install_istio/defaults: 1
ansible/roles/install_istio/meta: 1
ansible/roles/install_istio/tasks: 3
ansible/roles/install_istio/templates: 3
ansible/roles/install_jaeger/meta: 1
ansible/roles/install_jaeger/tasks: 1
ansible/roles/install_jenkins/files: 2
ansible/roles/install_jenkins/meta: 1
ansible/roles/install_jenkins/tasks: 1
ansible/roles/install_jenkins/templates: 1
ansible/roles/install_launcher/defaults: 1
ansible/roles/install_launcher/meta: 1
ansible/roles/install_launcher/tasks: 1
ansible/roles/install_nexus/defaults: 1
ansible/roles/install_nexus/files: 7
ansible/roles/install_nexus/meta: 1
ansible/roles/install_nexus/tasks: 1
ansible/roles/install_nexus/vars: 1
ansible/roles/install_oc/defaults: 1
ansible/roles/install_oc/tasks: 5
ansible/roles/install_packages/defaults: 1
ansible/roles/install_packages/tasks: 1
ansible/roles/k8s_bash: 1
ansible/roles/k8s_bash/defaults: 1
ansible/roles/k8s_bash/tasks: 1
ansible/roles/k8s_bash/vars: 1
ansible/roles/k8s_cert_manager: 1
ansible/roles/k8s_cert_manager/defaults: 1
ansible/roles/k8s_cert_manager/meta: 1
ansible/roles/k8s_cert_manager/tasks: 3
ansible/roles/k8s_cluster: 1
ansible/roles/k8s_cluster/defaults: 1
ansible/roles/k8s_cluster/files/sysctl.d: 1
ansible/roles/k8s_cluster/tasks: 8
ansible/roles/k8s_cluster/templates: 5
ansible/roles/k8s_cluster/templates/calico: 2
ansible/roles/k8s_cluster/vars: 2
ansible/roles/k8s_config: 1
ansible/roles/k8s_config/defaults: 1
ansible/roles/k8s_config/tasks: 3
ansible/roles/k8s_config/templates: 1
ansible/roles/k8s_dashboard/defaults: 1
ansible/roles/k8s_dashboard/files: 2
ansible/roles/k8s_dashboard/tasks: 4
ansible/roles/k8s_halkyon_site/defaults: 1
ansible/roles/k8s_halkyon_site/tasks: 3
ansible/roles/k8s_issuer_certificate/defaults: 1
ansible/roles/k8s_issuer_certificate/tasks: 3
ansible/roles/k8s_issuer_certificate/templates: 3
ansible/roles/k8s_service_broker/tasks: 3
ansible/roles/k8s_service_broker/templates: 1
ansible/roles/k8s_snowdrop_site/defaults: 1
ansible/roles/k8s_snowdrop_site/tasks: 3
ansible/roles/kind: 1
ansible/roles/kind/defaults: 1
ansible/roles/kind/tasks: 5
ansible/roles/kind/templates: 1
ansible/roles/kind/vars: 1
ansible/roles/kubedb/defaults: 1
ansible/roles/kubedb/tasks: 5
ansible/roles/kubedb/templates: 2
ansible/roles/ocp4_console/defaults: 1
ansible/roles/ocp4_console/tasks: 3
ansible/roles/ocp4_console/templates: 1
ansible/roles/ocp_cluster: 1
ansible/roles/ocp_cluster/defaults: 1
ansible/roles/ocp_cluster/files: 3
ansible/roles/ocp_cluster/meta: 2
ansible/roles/ocp_cluster/tasks: 11
ansible/roles/ocp_cluster/templates: 8
ansible/roles/ocp_cluster/vars: 2
ansible/roles/openshift_env/library: 1
ansible/roles/openshift_env/tasks: 2
ansible/roles/openshift_env/vars: 1
ansible/roles/openstack/init_vm/defaults: 1
ansible/roles/openstack/init_vm/tasks: 2
ansible/roles/openstack/init_vm/vars: 2
ansible/roles/passstore/ansible_inventory: 1
ansible/roles/passstore/ansible_inventory/tasks: 7
ansible/roles/passstore/check: 1
ansible/roles/passstore/check/tasks: 1
ansible/roles/persistence/defaults: 1
ansible/roles/persistence/files: 2
ansible/roles/persistence/meta: 1
ansible/roles/persistence/tasks: 3
ansible/roles/restart_master/meta: 1
ansible/roles/restart_master/tasks: 1
ansible/roles/sec/audit/handlers: 1
ansible/roles/sec/audit/tasks: 1
ansible/roles/sec/audit/templates: 1
ansible/roles/sec/audit/vars: 3
ansible/roles/sec/firewalld: 1
ansible/roles/sec/firewalld/defaults: 1
ansible/roles/sec/firewalld/handlers: 1
ansible/roles/sec/firewalld/tasks: 5
ansible/roles/sec/firewalld/vars: 2
ansible/roles/sec/journalctl/tasks: 1
ansible/roles/sec/motd: 1
ansible/roles/sec/motd/meta: 1
ansible/roles/sec/motd/tasks: 1
ansible/roles/sec/motd/templates: 1
ansible/roles/sec/selinux/handlers: 1
ansible/roles/sec/selinux/tasks: 1
ansible/roles/sec/selinux/vars: 2
ansible/roles/sec/sshd_port/handlers: 1
ansible/roles/sec/sshd_port/meta: 1
ansible/roles/sec/sshd_port/tasks: 1
ansible/roles/sec/sshd_port/vars: 1
ansible/roles/sec/sysctl/handlers: 1
ansible/roles/sec/sysctl/tasks: 1
ansible/roles/sec/update/tasks: 1
ansible/roles/snowdrop_site/defaults: 1
ansible/roles/snowdrop_site/meta: 1
ansible/roles/snowdrop_site/tasks: 3
ansible/roles/tekton_pipelines/defaults: 1
ansible/roles/tekton_pipelines/meta: 1
ansible/roles/tekton_pipelines/tasks: 3
ansible/roles/tools/bash_alias: 1
ansible/roles/tools/bash_alias/defaults: 1
ansible/roles/tools/bash_alias/tasks: 4
ansible/roles/tools/bash_alias/vars: 1
ansible/roles/tools/brew: 1
ansible/roles/tools/brew/defaults: 1
ansible/roles/tools/brew/tasks: 1
ansible/roles/tools/brew/vars: 3
ansible/roles/tools/k9s: 1
ansible/roles/tools/k9s/defaults: 1
ansible/roles/tools/k9s/tasks: 3
ansible/roles/tools/k9s/templates: 1
ansible/roles/tools/k9s/vars: 2
ansible/roles/tools/misc: 1
ansible/roles/tools/misc/defaults: 1
ansible/roles/tools/misc/tasks: 3
ansible/roles/tools/misc/vars: 1
ansible/roles/tools/pacman: 1
ansible/roles/tools/pacman/defaults: 1
ansible/roles/tools/pacman/tasks: 3
ansible/roles/tools/pacman/vars: 2
ansible/roles/tools/sysstats: 1
ansible/roles/tools/sysstats/defaults: 1
ansible/roles/tools/sysstats/tasks: 3
ansible/roles/tools/sysstats/vars: 1
ansible/roles/uninstall_launcher/defaults: 1
ansible/roles/uninstall_launcher/meta: 1
ansible/roles/uninstall_launcher/tasks: 1
awx: 8
awx/conf: 3
awx/conf/import: 7
awx/kustomize: 2
awx/postgresql: 3
collections: 1
container: 1
container/build: 3
container/samples: 4
container/scripts: 3
doc: 10
hetzner: 7
hetzner/scripts: 3
ibm-cloud: 1
ibm-cloud/ansible: 10
kind: 8
kind/functions: 1
kubernetes: 1
kubernetes/ansible: 1
kubernetes/scripts: 2
kubernetes/test: 1
molecule: 1
openshift: 3
openstack: 2
passwordstore: [REDACTED_LITERAL]
sandbox: 2
sandbox/cluster_up: 9
sandbox/kind: 4
sandbox/minishift: 2
sandbox/oc: 3
sandbox/vagrant: 3
sandbox/vagrant/ansible: 2
sandbox/vagrant/scripts: 2
sandbox/virtualbox: 2
sandbox/virtualbox/build-centos-iso: 4
snowdrop-bot: 1
snowdrop-bot/ansible: 2
tooling: 4
tooling/asciidoctor: 2
tooling/etc: 1
tooling/src/main/java/dev/snowdrop: 2
tooling/src/main/java/dev/snowdrop/extension: 1
tooling/src/main/java/dev/snowdrop/type: 2
tooling/src/test/java/dev/snowdrop: 3
tools: 2
```

# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-043

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `ansible/playbook/ocp/ocp_openstack_install_post.yml` (reported anchor line 58)
- Object: `variable` `84f1f8814c5e432e03d26886b8766629746bcb00b6f7d747153f3724599dd6f4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–122 of 122:

```text
    1 | ---
    2 | - name: "Build OpenStack authentication for v3password"
    3 |   ansible.builtin.import_playbook: "../openstack/openstack_auth_passstore_v3password.yml"
    4 | 
    5 | - name: "Load the metadata from the OCP installation directory"
    6 |   hosts: "{{ ocp_bootstrap_host | default('localhost') }}"
    7 |   gather_facts: true
    8 | 
    9 |   tasks:
   10 | 
   11 |     - name: "Archive the installation data directory"
   12 |       ansible.builtin.shell:
   13 |         cmd: |
   14 |           tar -czf {{ tmp_directory }}/{{ ocp_cluster_name }}-data.tar.gz {{ ocp_cluster_name }}/
   15 |       args:
   16 |         chdir: "{{ ocp_root_directory }}"
   17 | 
   18 |     - name: Calculate installation folder
   19 |       ansible.builtin.set_fact:
   20 |         installation_dir: "{{ ocp_root_directory }}/{{ ocp_cluster_name }}"
   21 | 
   22 |     - name: Get OCP cluster metadata
   23 |       ansible.builtin.import_role:
   24 |         name: ocp_cluster
   25 |         tasks_from: get_metadata.yml
   26 | 
   27 |     - name: "Slurp kubeadmin password"
   28 |       ansible.builtin.slurp:
   29 |         src: "{{ installation_dir }}/auth/kubeadmin-password"
   30 |       register: kubeadmin_password_slurp
   31 | 
   32 |     - name: "Transform kubeadmin password slurp"
   33 |       ansible.builtin.set_fact:
   34 |         kubeadmin_password: "{{ kubeadmin_password_slurp.content | b64decode }}"
   35 | 
   36 |     - name: "Slurp OCP installation folder"
   37 |       ansible.builtin.slurp:
   38 |         src: "{{ tmp_directory }}/{{ ocp_cluster_name }}-data.tar.gz"
   39 |       register: ansible_installation_folder_base64_slurp
   40 | 
   41 |     - name: "Base64 encode OCP installation folder"
   42 |       ansible.builtin.set_fact:
   43 |         ansible_installation_folder_base64: "{{ ansible_installation_folder_base64_slurp.content }}"
   44 | 
   45 | - name: "Get OCP installation information"
   46 |   ansible.builtin.import_playbook: "ocp_openstack_info.yml"
   47 |   vars:
   48 |     # ocp_cluster_name: "{{ ocp_cluster_name }}"
   49 |     # ocp_root_directory: "{{ ocp_root_directory }}"
   50 |     vm_name: "{{ ocp_bootstrap_host | default(['localhost']) }}"
   51 | 
   52 | - name: "Store the OCP information on the passwordstore"
   53 |   hosts: "localhost"
   54 |   gather_facts: true
   55 | 
   56 |   tasks:
   57 | 
   58 |     - name: "Print installation variables remote"
   59 |       ansible.builtin.debug:
   60 |         msg:
   61 |           - "ocp_cluster_metadata.infraID: {{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata']['infraID'] }}"
   62 |           - "ansible_installation_folder_base64: {{ hostvars[ocp_bootstrap_host]['ansible_installation_folder_base64'] }}"
   63 |           - "kubeadmin_password: {{ hostvars[ocp_bootstrap_host]['kubeadmin_password'] }}"
   64 |       when: ocp_bootstrap_host is defined
   65 | 
   66 |     - name: "Set localhost facts"
   67 |       ansible.builtin.set_fact:
   68 |           ocp_cluster_metadata: "{{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
   69 |           ansible_installation_folder_base64: "{{ hostvars[ocp_bootstrap_host]['ansible_installation_folder_base64'] }}"
   70 |           kubeadmin_password: "{{ hostvars[ocp_bootstrap_host]['kubeadmin_password'] }}"
   71 |       when: ocp_bootstrap_host is defined
   72 | 
   73 |     - name: "Store the OCP information on the bootstrap host passwordstore"
   74 |       ansible.builtin.set_fact:
   75 |         ansible_installation_folder_passwordstore: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/install_dir create=True userpass=' + ansible_installation_folder_base64 )[0] }}"
   76 |         console_user: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/console_user create=True userpass=[REDACTED_LITERAL]
   77 |         console_pwd: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/console_pwd create=True userpass=' + kubeadmin_password )[0] }}"
   78 |         console_url: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/console_url create=True userpass=[REDACTED_LITERAL]
   79 |         api_url: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/api_url create=True userpass=[REDACTED_LITERAL]
   80 | 
   81 |     - name: "Store the OCP API user information on the bootstrap host passwordstore"
   82 |       ansible.builtin.set_fact:
   83 |         admin_user: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/admin_user create=True userpass=[REDACTED_LITERAL]
   84 |         admin_pwd: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/admin_pwd create=True userpass=' + ocp_cluster_user_admin_pw )[0] }}"
   85 |         dev_user: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/dev_user create=True userpass=[REDACTED_LITERAL]
   86 |         dev_pw: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/dev_pw create=True userpass=[REDACTED_LITERAL]
   87 |       when: admin_user is defined and admin_pwd is defined and dev_user is defined and dev_pw is defined
   88 | 
   89 |   post_tasks:
   90 | 
   91 |     - name: "Deploying jump server"
   92 |       ansible.builtin.debug:
   93 |         msg:
   94 |           - "Deploying the jump server. If it fails these steps can be executed manually:"
   95 |           - "$ ansible-playbook ansible/playbook/ocp/ocp_openstack_create_jump_server.yml -e tmp_directory={{ tmp_directory }} -e ocp_root_directory={{ ocp_root_directory }} -e ocp_cluster_name={{ ocp_cluster_name }} -e vm_name={{ ocp_cluster_metadata.infraID }}-jump-server {% if ocp_bootstrap_host is defined %}-e ocp_bootstrap_host={{ ocp_bootstrap_host }}{% endif %}"
   96 | 
   97 | - name: "Publish cluster Console DNS records"
   98 |   ansible.builtin.import_playbook: "../godaddy/godaddy_dns_create_passwordstore.yml"
   99 |   vars:
  100 |     api_environment: prod
  101 |     dns:
  102 |       data: "{{ ocp_cluster.floating_ip_ingress_address }}"
  103 |     domain_name: snowdrop.dev
  104 |     record_name: "*.apps.{{ ocp_cluster_name }}"
  105 |     record_type: A
  106 | 
  107 | - name: "Publish cluster API DNS records"
  108 |   ansible.builtin.import_playbook: "../godaddy/godaddy_dns_create_passwordstore.yml"
  109 |   vars:
  110 |     api_environment: prod
  111 |     dns:
  112 |       data: "{{ ocp_cluster.floating_ip_api_address }}"
  113 |     domain_name: snowdrop.dev
  114 |     record_name: "api.{{ ocp_cluster_name }}"
  115 |     record_type: A
  116 | 
  117 | - name: "Deploy Jump Server"
  118 |   ansible.builtin.import_playbook: "ocp_openstack_create_jump_server.yml"
  119 |   vars:
  120 |     vm_name: "{{ ocp_cluster_metadata.infraID }}-jump-server"
  121 | ...
  122 | # ansible-playbook ansible/playbook/ocp/ocp_openstack_install_post.yml -e tmp_directory=/opt/ocp/_tmp/ansible.yxam0y7mbuild -e ocp_root_directory=/opt/ocp -e ocp_cluster_name=ocp-sdev
```

## Visible variable references

```text
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:23:    #     ocp_cluster_metadata: "{{ lookup('file', installation_dir + '/metadata.json') | from_json }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:33:    #       # - "ocp_cluster_metadata: {{ ocp_cluster_metadata }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:36:    #       - "ocp_cluster_metadata: {{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:43:          ocp_cluster_metadata: "{{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:45:          ansible_installation_folder_base64: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/install_dir' )[0] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:47:          kubeadmin_password: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/kubeadmin' )[0] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:55:          - "ocp_cluster_metadata: {{ ocp_cluster_metadata }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:56:          - "ocp_cluster_metadata: {{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:57:          - "ocp_cluster_metadata: {{ hostvars['localhost']['ocp_cluster_metadata'] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:66:        network: "{{ ocp_cluster_metadata.infraID }}-openshift"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:69:    vm_name: "{{ ocp_cluster_metadata.infraID }}-jump-server"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:103:        server: "{{ ocp_cluster_metadata.infraID }}-jump-server"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_create_jump_server.yml:185:        content: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '/install_dir')[0] | b64decode }}" 
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_info.yml:31:      when: ocp_cluster_metadata is undefined
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_info.yml:35:        msg: "ocp_cluster_metadata: {{ ocp_cluster_metadata }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_info.yml:58:          cluster_name: "{{ ocp_cluster_metadata.clusterName }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_info.yml:60:          jump_server_vm_name: "{{ ocp_cluster_metadata.infraID }}-jump-server"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install.yml:106:    vm_name: "{{ ocp_cluster_metadata.infraID }}-jump-server"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install.yml:111:    vm_name: "{{ ocp_cluster_metadata.infraID }}-jump-server"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:61:          - "ocp_cluster_metadata.infraID: {{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata']['infraID'] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:68:          ocp_cluster_metadata: "{{ hostvars[ocp_bootstrap_host]['ocp_cluster_metadata'] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:75:        ansible_installation_folder_passwordstore: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/install_dir create=True userpass=' + ansible_installation_folder_base64 )[0] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:76:        console_user: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/console_user create=True userpass=[REDACTED_LITERAL]
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:77:        console_pwd: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/console_pwd create=True userpass=' + kubeadmin_password )[0] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:78:        console_url: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/console_url create=True userpass=[REDACTED_LITERAL]
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:79:        api_url: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/api_url create=True userpass=[REDACTED_LITERAL]
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:83:        admin_user: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/admin_user create=True userpass=[REDACTED_LITERAL]
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:84:        admin_pwd: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/admin_pwd create=True userpass=' + ocp_cluster_user_admin_pw )[0] }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:85:        dev_user: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/dev_user create=True userpass=[REDACTED_LITERAL]
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:86:        dev_pw: "{{ query('passwordstore', 'openstack/' + ocp_cluster_metadata.infraID + '-jump-server/dev_pw create=True userpass=[REDACTED_LITERAL]
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:95:          - "$ ansible-playbook ansible/playbook/ocp/ocp_openstack_create_jump_server.yml -e tmp_directory={{ tmp_directory }} -e ocp_root_directory={{ ocp_root_directory }} -e ocp_cluster_name={{ ocp_cluster_name }} -e vm_name={{ ocp_cluster_metadata.infraID }}-jump-server {% if ocp_bootstrap_host is defined %}-e ocp_bootstrap_host={{ ocp_bootstrap_host }}{% endif %}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/playbook/ocp/ocp_openstack_install_post.yml:120:    vm_name: "{{ ocp_cluster_metadata.infraID }}-jump-server"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/roles/ocp_cluster/tasks/build_output.yml:30:      metadata: "{{ ocp_cluster_metadata }}"
0a9fe0fb57bd9759833bb9974d5022d945b2647c:ansible/roles/ocp_cluster/tasks/get_metadata.yml:14:    ocp_cluster_metadata: "{{ ocp_cluster_slurp_metadata.content | b64decode | from_json }}"
```

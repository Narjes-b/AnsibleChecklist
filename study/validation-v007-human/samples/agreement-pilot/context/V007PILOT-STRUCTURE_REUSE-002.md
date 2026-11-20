# Frozen source context: V007PILOT-STRUCTURE_REUSE-002

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible_tower_aws/3_load.yml` (reported anchor line 1)
- Object: `source_location` `bc4a40eb86be366c7b57bd4eb8c3b349be2ee1eaa01d5342fa5c250b4e9da526`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–186 of 186:

```text
    1 | # file: 3_load.yml
    2 | ---
    3 | 
    4 | - name: Wait for AWS AMIs to become initialized
    5 |   hosts: localhost
    6 |   gather_facts: no
    7 |   tasks:
    8 |     - wait_for:
    9 |         host: "{{ item }}"
   10 |         port: 22
   11 |         state: started
   12 |         timeout: 300
   13 |       with_items:
   14 |         - "{{ groups.rhel_nodes }}"
   15 |         - "{{ groups.tower_rhel_nodes }}"
   16 | 
   17 | - name: Configure repositories on all RHEL nodes
   18 |   become: yes
   19 |   remote_user: ec2-user
   20 |   hosts:
   21 |     - tower_rhel_nodes
   22 |     - rhel_nodes
   23 |   gather_facts: yes
   24 |   roles:
   25 |     - role: subscription_manager 
   26 |     - role: firewalld
   27 | 
   28 | - name: Configure epel on tower nodes
   29 |   become: yes
   30 |   remote_user: ec2-user
   31 |   hosts: tower_rhel_nodes
   32 |   roles:
   33 |     - role: epel
   34 | 
   35 | - name: Remove Red Hat EAP packages
   36 |   become: yes
   37 |   remote_user: ec2-user
   38 |   hosts:
   39 |     - tower_rhel_nodes
   40 |     - rhel_nodes
   41 |   gather_facts: no
   42 |   tasks:
   43 |     - package:
   44 |         name: eap7-*
   45 |         state: absent
   46 |       when: jboss|bool
   47 |       ignore_errors: yes
   48 | 
   49 | - name: Ensure python3-pip installed for powerline (RHEL 8)
   50 |   become: yes
   51 |   remote_user: ec2-user
   52 |   hosts: tower_rhel_nodes
   53 |   gather_facts: no
   54 |   tasks:
   55 |     - package:
   56 |         name: python3-pip
   57 |         state: latest
   58 |       when: rhel_ver == 'RHEL-8'
   59 | 
   60 | - name: Configure software on nodes
   61 |   become: yes
   62 |   remote_user: ec2-user
   63 |   hosts: tower_rhel_nodes
   64 |   gather_facts: no
   65 |   roles:
   66 |     - role: nodejs
   67 |     - role: ansible.tower
   68 |     - role: system-user
   69 |     - role: powerline
   70 |     - role: vscode
   71 |       when: graphical|bool
   72 |     - role: graphical
   73 |       when: graphical|bool
   74 |     - role: code-server
   75 |       code_pass: "{{ workshop_password }}"
   76 |   tasks:
   77 |     - name: push out student templates
   78 |       copy:
   79 |         src: "{{ item }}"
   80 |         dest: "~{{ system_user }}/{{ item }}"
   81 |         mode: 0644
   82 |       with_items:
   83 |       - "hello.js"
   84 |       - "hello.service"
   85 | 
   86 | - name: Load real cert for web console
   87 |   become: yes
   88 |   remote_user: ec2-user
   89 |   hosts: tower_rhel_nodes
   90 |   gather_facts: yes
   91 |   tasks:
   92 |     - name: install cockpit package if it's not present
   93 |       package:
   94 |         name: cockpit-ws
   95 |         state: present
   96 | 
   97 |     - name: install real certificate to web console
   98 |       copy:
   99 |         dest: "/etc/cockpit/ws-certs.d/acme.cert"
  100 |         content: "{{ lookup('file', deploy_working_dir + '/' + workshop_prefix + '.' + domain_name + '_cert.pem') }}\n{{ lookup('file', deploy_working_dir + '/' + workshop_prefix + '.' + domain_name + '_key.pem') }}"
  101 |         owner: "root"
  102 |         group: "cockpit-ws"
  103 | 
  104 |     - name: stage real cert for tower
  105 |       copy:
  106 |         dest: "~ec2-user/cert.pem"
  107 |         src: "{{ deploy_working_dir }}/{{ workshop_prefix }}.{{ domain_name }}_cert.pem"
  108 |         owner: "ec2-user"
  109 |         group: "ec2-user"
  110 |         mode: "0644"
  111 | 
  112 |     - name: stage real key for tower
  113 |       copy:
  114 |         dest: "~ec2-user/key.pem"
  115 |         src: "{{ deploy_working_dir }}/{{ workshop_prefix }}.{{ domain_name }}_key.pem"
  116 |         owner: "ec2-user"
  117 |         group: "ec2-user"
  118 |         mode: "0644"
  119 | 
  120 | - name: Configure web console (RHEL 7)
  121 |   become: yes
  122 |   remote_user: ec2-user
  123 |   hosts: tower_rhel_nodes
  124 |   gather_facts: no
  125 |   roles:
  126 |     - role: wetty
  127 |       when: rhel_ver == 'RHEL-7'
  128 | 
  129 | - name: Configure web console (RHEL 8)
  130 |   become: yes
  131 |   remote_user: ec2-user
  132 |   hosts: tower_rhel_nodes
  133 |   gather_facts: no
  134 |   roles:
  135 |     - role: cockpit
  136 |       when: rhel_ver == 'RHEL-8'
  137 | 
  138 | - name: Stage Maven POMs
  139 |   become: yes
  140 |   remote_user: ec2-user
  141 |   hosts: rhel_nodes
  142 |   gather_facts: yes
  143 |   roles:
  144 |     - role: poms
  145 |       when: jboss|bool
  146 | 
  147 | - name: Upgrade packages
  148 |   become: yes
  149 |   remote_user: ec2-user
  150 |   hosts:
  151 |     - tower_rhel_nodes
  152 |     - rhel_nodes
  153 |   roles:
  154 |     - role: upgrade
  155 | 
  156 | - name: Re-enable SCL repo when upgrade disables it
  157 |   become: yes
  158 |   remote_user: ec2-user
  159 |   hosts:
  160 |     - tower_rhel_nodes
  161 |     - rhel_nodes
  162 |   gather_facts: yes
  163 |   roles:
  164 |     - role: subscription_manager 
  165 | 
  166 | - name: Open ports 80,443 on nodes
  167 |   become: yes
  168 |   remote_user: ec2-user
  169 |   hosts:
  170 |     - rhel_nodes
  171 |   gather_facts: yes
  172 |   tasks:
  173 |     - name: open firewalld ports
  174 |       firewalld:
  175 |         service: "{{ item }}"
  176 |         permanent: yes
  177 |         state: enabled
  178 |       with_items:
  179 |       - 'http'
  180 |       - 'https'
  181 |     - name: restart service
  182 |       service:
  183 |         name: firewalld
  184 |         state: reloaded
  185 | 
  186 | ...
```

## Frozen tracked paths in the relevant role/scope

```text
.gitignore
.gitmodules
CONTRIBUTING.md
README.md
ansible_tower_aws/.gitignore
ansible_tower_aws/1_provision.yml
ansible_tower_aws/2_preload.yml
ansible_tower_aws/3_load.yml
ansible_tower_aws/4_unregister.yml
ansible_tower_aws/README.md
ansible_tower_aws/admin.sh
ansible_tower_aws/ansible.cfg
ansible_tower_aws/files/code-server.service
ansible_tower_aws/files/example-network-playbook.yml
ansible_tower_aws/files/hello.js
ansible_tower_aws/files/hello.service
ansible_tower_aws/filter_plugins/sort_versions.py
ansible_tower_aws/group_vars/all_example.yml
ansible_tower_aws/host_vars/localhost
ansible_tower_aws/img/Ansible-Tower-Logotype-Large-RGB-FullGrey-300x124.png
ansible_tower_aws/img/Logo-Red_Hat-Enterprise_Linux_8-B-Standard-RGB.png
ansible_tower_aws/img/ansible-tower.png
ansible_tower_aws/img/codiad.png
ansible_tower_aws/inventory/hosts
ansible_tower_aws/roles/admin_server_config/defaults/main.yml
ansible_tower_aws/roles/admin_server_config/handlers/main.yml
ansible_tower_aws/roles/admin_server_config/meta/main.yml
ansible_tower_aws/roles/admin_server_config/tasks/main.yml
ansible_tower_aws/roles/admin_server_config/templates/bashrc.j2
ansible_tower_aws/roles/admin_server_config/templates/env.sh.j2
ansible_tower_aws/roles/admin_server_config/vars/main.yml
ansible_tower_aws/roles/admin_server_prep/defaults/main.yml
ansible_tower_aws/roles/admin_server_prep/handlers/main.yml
ansible_tower_aws/roles/admin_server_prep/meta/main.yml
ansible_tower_aws/roles/admin_server_prep/tasks/main.yml
ansible_tower_aws/roles/admin_server_prep/templates/aws_credentials_vault.yml.j2
ansible_tower_aws/roles/admin_server_prep/templates/example.j2
ansible_tower_aws/roles/admin_server_prep/templates/workshop-password.j2
ansible_tower_aws/roles/admin_server_prep/vars/main.yml
ansible_tower_aws/roles/ansible.tower/defaults/main.yml
ansible_tower_aws/roles/ansible.tower/files/license
ansible_tower_aws/roles/ansible.tower/files/vimrc
ansible_tower_aws/roles/ansible.tower/handlers/main.yml
ansible_tower_aws/roles/ansible.tower/meta/main.yml
ansible_tower_aws/roles/ansible.tower/tasks/main.yml
ansible_tower_aws/roles/ansible.tower/tasks/nodes_setup.yml
ansible_tower_aws/roles/ansible.tower/tasks/tower_setup.yml
ansible_tower_aws/roles/ansible.tower/tasks/user_setup.yml
ansible_tower_aws/roles/ansible.tower/templates/ansible.cfg.j2
ansible_tower_aws/roles/ansible.tower/templates/inventory.j2
ansible_tower_aws/roles/ansible.tower/vars/main.yml
ansible_tower_aws/roles/aws.create/README.md
ansible_tower_aws/roles/aws.create/defaults/main.yml
ansible_tower_aws/roles/aws.create/handlers/main.yml
ansible_tower_aws/roles/aws.create/tasks/main.yml
ansible_tower_aws/roles/aws.create/templates/ec2.ini.j2
ansible_tower_aws/roles/aws.create/templates/facts.j2
ansible_tower_aws/roles/aws.create/templates/hosts.j2
ansible_tower_aws/roles/aws.create/templates/winrm.txt.j2
ansible_tower_aws/roles/aws.remove/README.md
ansible_tower_aws/roles/aws.remove/defaults/main.yml
ansible_tower_aws/roles/aws.remove/handlers/main.yml
ansible_tower_aws/roles/aws.remove/tasks/main.yml
ansible_tower_aws/roles/aws.remove/templates/ec2.ini.j2
ansible_tower_aws/roles/aws.remove/templates/hosts.j2
ansible_tower_aws/roles/subscription_manager/defaults/main.yml
ansible_tower_aws/roles/subscription_manager/handlers/main.yml
ansible_tower_aws/roles/subscription_manager/meta/main.yml
ansible_tower_aws/roles/subscription_manager/tasks/cloud_access.yml
ansible_tower_aws/roles/subscription_manager/tasks/main.yml
ansible_tower_aws/roles/subscription_manager/tasks/repos-rhel6.yml
ansible_tower_aws/roles/subscription_manager/tasks/repos-rhel7.yml
ansible_tower_aws/roles/subscription_manager/tasks/repos-rhel8.yml
ansible_tower_aws/roles/subscription_manager/tasks/repos-rhel8beta.yml
ansible_tower_aws/roles/subscription_manager/tasks/subscribe.yml
ansible_tower_aws/roles/subscription_manager/templates/example.j2
ansible_tower_aws/roles/subscription_manager/vars/main.yml
ansible_tower_aws/roles/unregister/defaults/main.yml
ansible_tower_aws/roles/unregister/handlers/main.yml
ansible_tower_aws/roles/unregister/meta/main.yml
ansible_tower_aws/roles/unregister/tasks/main.yml
ansible_tower_aws/roles/unregister/templates/example.j2
ansible_tower_aws/roles/unregister/vars/main.yml
ansible_tower_azure/1_provision.yml
ansible_tower_azure/2_load.yml
ansible_tower_azure/3_unregister.yml
ansible_tower_azure/README.md
ansible_tower_azure/Vagrantfile
ansible_tower_azure/ansible.cfg
ansible_tower_azure/env.sh_example
ansible_tower_azure/galaxy.yml
ansible_tower_azure/group_vars/all_example
ansible_tower_azure/host_vars/localhost
ansible_tower_azure/img/Ansible-Tower-Logotype-Large-RGB-FullGrey-300x124.png
ansible_tower_azure/img/ansible-tower.png
ansible_tower_azure/img/codiad.png
ansible_tower_azure/inventory/hosts
ansible_tower_azure/roles/ansible.tower/defaults/main.yml
ansible_tower_azure/roles/ansible.tower/files/license
ansible_tower_azure/roles/ansible.tower/files/vimrc
ansible_tower_azure/roles/ansible.tower/handlers/main.yml
ansible_tower_azure/roles/ansible.tower/meta/main.yml
ansible_tower_azure/roles/ansible.tower/tasks/main.yml
ansible_tower_azure/roles/ansible.tower/tasks/nodes_setup.yml
ansible_tower_azure/roles/ansible.tower/tasks/tower_setup.yml
ansible_tower_azure/roles/ansible.tower/tasks/user_setup.yml
ansible_tower_azure/roles/ansible.tower/tasks/walkthroughs.yml
ansible_tower_azure/roles/ansible.tower/templates/ansible.cfg.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-0.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-1.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-2.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-3.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-4.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-5.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-6.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.0-7.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.1-1.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.1-2.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.1-3.sh.j2
ansible_tower_azure/roles/ansible.tower/templates/exercise1.1-4.sh.j2
[listing truncated after 120 paths]
```

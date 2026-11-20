# Frozen source context: V007PILOT-SECURITY-044

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `plugins/tripleo-undercloud/configure.yml` (reported anchor line 164)
- Object: `task` `2b2841aa4bc227d4f9bb8eba78023678a4d7e36d500be72cde139b9f53d26b54`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–235 of 235:

```text
    1 | - name: Configure Undercloud
    2 |   hosts: undercloud
    3 |   tags: configure
    4 |   gather_facts: no
    5 |   any_errors_fatal: true
    6 |   vars:
    7 |       - conf: "{{ install.config|default({}) }}"
    8 |       - osp_release: "{{ install.version|openstack_release }}"
    9 |       - conf_instack: '/usr/share/instack-undercloud/undercloud.conf.sample'
   10 |       - conf_oooclient: '/usr/share/python-tripleoclient/undercloud.conf.sample'
   11 |       - local_src: "{%- if conf.file|default('') -%}
   12 |                 {{ conf.file }}
   13 |                 {%- else -%}
   14 |                 templates/undercloud.conf.j2
   15 |                 {%- endif -%}"
   16 |       - custom_template: "{{ install.get('custom', {}).template|default('') }}"
   17 |       - custom_template_file: "{{ working_dir }}/custom_template.yaml"
   18 |       - custom_template_configured: "{{ (custom_template != '') | ternary(True, False) }}"
   19 |   tasks:
   20 |       - name: set workingr_dir fact
   21 |         set_fact:
   22 |             working_dir: "/home/{{ install.user.name }}"
   23 | 
   24 |       # We ingore anything with : as it's ipv6 address and we will only set ipv4 nameserver by default
   25 |       - name: get nameservers
   26 |         command: awk '/#|:/ {next} /nameserver/ { ips=ips $2"," } END {print substr(ips, 1, length(ips)-1)}' /etc/resolv.conf
   27 |         register: nameservers
   28 |         changed_when: False
   29 | 
   30 |       - name: set undercloud_nameservers fact
   31 |         set_fact:
   32 |             undercloud_nameservers: "{{ nameservers.stdout }}"
   33 |         when: nameservers.stdout != ''
   34 | 
   35 |       - name: generate container images environment file
   36 |         import_tasks: tasks/prepare_uc_images.yml
   37 |         when:
   38 |             - install.version|openstack_distribution == 'OSP'
   39 |             - install.version|openstack_release > 13
   40 | 
   41 |       - name: template the undercloud.conf
   42 |         template:
   43 |             src: "{{ local_src }}"
   44 |             dest: ~/undercloud.conf
   45 |             force: yes
   46 |             mode: 0755
   47 |         when: local_src != "none"
   48 | 
   49 |       - name: copy custom heat template for undercloud.conf
   50 |         template:
   51 |             src: "{{ custom_template }}"
   52 |             dest: "{{ custom_template_file }}"
   53 |             force: yes
   54 |             mode: 0755
   55 |         when: custom_template_configured
   56 | 
   57 |       - name: make sure ~/.ssh exists
   58 |         file:
   59 |             path: ~/.ssh
   60 |             state: directory
   61 |             mode: 0700
   62 | 
   63 |       - name: create default developer-friendly ~/.ssh/config for the stack user
   64 |         template:
   65 |             src: templates/ssh.config.j2
   66 |             dest: ~/.ssh/config
   67 |             mode: 0600
   68 | 
   69 |       - name: copy default undercloud config
   70 |         copy:
   71 |             remote_src: yes
   72 |             src: "{{ conf_oooclient }}"
   73 |             dest: ~/undercloud.conf
   74 |             force: yes
   75 |             mode: 0755
   76 |         when: local_src == "none"
   77 | 
   78 |       - name: override values in undercloud conf
   79 |         include_tasks: tasks/inject_undercloud_conf.yml
   80 |         with_dict: "{{ conf.options|default({}) }}"
   81 |         loop_control:
   82 |             loop_var: section
   83 | 
   84 |       - name: enable undercloud-ssl
   85 |         include_tasks: tasks/ssl.yml
   86 |         when: install.ssl or install.version|openstack_release > 13
   87 |         tags: ssl
   88 | 
   89 |       - name: create the base undercloud deploy script
   90 |         template:
   91 |             src: undercloud_deploy.sh.j2
   92 |             dest: ~/undercloud_deploy.sh
   93 |             mode: 0755
   94 | 
   95 |       - name: the undercloud deploy script
   96 |         command: "cat undercloud_deploy.sh"
   97 |         tags: deploy
   98 | 
   99 |       # to avoid i/o bottlenecks during overcloud deployment
  100 |       # limit the number of nodes being deployed simultaneously to 5
  101 |       - block:
  102 |           - name: set max_concurrent_builds via hieradata
  103 |             copy:
  104 |                 content: 'nova::compute::ironic::max_concurrent_builds: 5'
  105 |                 dest: "{{ working_dir }}/hiera_override.yaml"
  106 | 
  107 |           - name: Ensure cloud domain is set via hieradata for neutron dhcp
  108 |             lineinfile:
  109 |               path: "{{ working_dir }}/hiera_override.yaml"
  110 |               state: present
  111 |               line: "nova::network::neutron::dhcp_domain: {{ install.overcloud.domain }}"
  112 |             when:
  113 |                 - install.version|openstack_release < 12
  114 |           - name: Ensure neutron has dns_domain set to cloud domain
  115 |             lineinfile:
  116 |               path: "{{ working_dir }}/hiera_override.yaml"
  117 |               state: present
  118 |               line: "neutron::dns_domain: {{ install.overcloud.domain }}"
  119 |             when:
  120 |                 - install.version|openstack_release < 12
  121 | 
  122 |           - block:
  123 |               - name: get global mtu hieradata for neutron from local_mtu
  124 |                 command: 'awk -F= "/^local_mtu\s*=\s*/ {print $2}" ~/undercloud.conf'
  125 |                 register: local_mtu
  126 |                 changed_when: False
  127 | 
  128 |               - name: set global mtu hieradata for neutron from local_mtu
  129 |                 lineinfile:
  130 |                   path: "{{ working_dir }}/hiera_override.yaml"
  131 |                   state: present
  132 |                   line: "neutron::global_physnet_mtu: {{ local_mtu.stdout }}"
  133 |                 when:
  134 |                     - local_mtu.stdout != ""
  135 |             when:
  136 |                 - install.version|openstack_release < 14
  137 | 
  138 |           - name: set additional config via hieradata
  139 |             lineinfile:
  140 |               path: "{{ working_dir }}/hiera_override.yaml"
  141 |               state: present
  142 |               line: "{{ item.key }}: {{ item.value }}"
  143 |               regexp: "{{ item.key }}"
  144 |             with_dict: "{{ install.hieradata.config|default({}) }}"
  145 |             when: '"hieradata" in install'
  146 | 
  147 |           - name: set hieradata in undercloud.conf
  148 |             ini_file:
  149 |                 path: "{{ working_dir }}/undercloud.conf"
  150 |                 section: DEFAULT
  151 |                 option: hieradata_override
  152 |                 value: "{{ working_dir }}/hiera_override.yaml"
  153 |         when:
  154 |             - install.version|openstack_release > 9
  155 | 
  156 |       - block:
  157 |           - name: ensure 'patch' tool is installed
  158 |             become: true
  159 |             dnf:
  160 |               name: patch
  161 |               state: present
  162 | 
  163 |           - name: download workarounds file
  164 |             get_url:
  165 |                 url: "{{ install.workarounds }}"
  166 |                 dest: "{{ inventory_dir }}/workarounds.yml"
  167 |                 backup: yes
  168 |                 force: yes
  169 |                 validate_certs: no
  170 |             delegate_to: localhost
  171 | 
  172 |           - name: load workarounds vars
  173 |             include_vars: "{{ lookup('first_found', possible_files) }}"
  174 |             vars:
  175 |               possible_files:
  176 |                 - "{{ inventory_dir }}/workarounds.yml"
  177 |                 - "{{ playbook_dir }}/workarounds.yml"
  178 | 
  179 |           - name: create workarounds scripts
  180 |             template:
  181 |               src: templates/workarounds.sh.j2
  182 |               dest: "~/{{ item }}.sh"
  183 |               mode: 0775
  184 |             with_items:
  185 |               - 'pre_undercloud_deploy_workarounds'
  186 |               - 'post_undercloud_deploy_workarounds'
  187 |         when: install.workarounds != ''
  188 | 
  189 |       - name: Preparing custom environment files for the undercloud deployment
  190 |         block:
  191 |           - name: Create custom environment file - Ironic Direct Deploy Interface
  192 |             copy:
  193 |               dest: "{{ ironic_custom_env_file }}"
  194 |               content: |
  195 |                 parameter_defaults:
  196 |                    IronicDefaultDeployInterface: direct
  197 |                 {% if install.version|default(undercloud_version) | openstack_release > 14 and install.image.download.source == 'http' %}
  198 |                    IronicImageDownloadSource: http
  199 |                 {% endif %}
  200 |             when: deploy_interface_direct
  201 | 
  202 |           - name: Create a custom environment file - NTP Pool
  203 |             copy:
  204 |               dest: "{{ ntp_custom_env_file }}"
  205 |               content: |
  206 |                 parameter_defaults:
  207 |                    NtpPool: {{ install.ntp.pool }}
  208 |                    NtpServer: []
  209 |             when: configure_ntp_pool
  210 | 
  211 |           - name: Set custom env files in undercloud.conf
  212 |             vars:
  213 |               undercloud_conf_path: "{{ working_dir }}/undercloud.conf"
  214 |               env_files:
  215 |                 - "{{ deploy_interface_direct | ternary(ironic_custom_env_file,'') }}"
  216 |                 - "{{ configure_ntp_pool | ternary(ntp_custom_env_file,'') }}"
  217 |                 - "{{ custom_template_configured | ternary(custom_template_file,'') }}"
  218 |             ini_file:
  219 |               path: "{{ undercloud_conf_path }}"
  220 |               section: DEFAULT
  221 |               option: custom_env_files
  222 |               value: "{{ env_files | difference(['']) | join(',') }}"
  223 | 
  224 |         vars:
  225 |           - ironic_custom_env_file: "{{ working_dir }}/ironic_deploy_interface_direct.yaml"
  226 |           - ntp_custom_env_file: "{{ working_dir }}/ntp_pool.yaml"
  227 |           - deploy_interface_direct_conditions:
  228 |               - "{{ install.deploy_interface_default == 'direct' }}"
  229 |               - "{{ install.version|default(undercloud_version) | openstack_release > 13 }}"
  230 |           - deploy_interface_direct: "{{ (false in deploy_interface_direct_conditions) | ternary(False, True) }}"
  231 |           - configure_ntp_pool_conditions:
  232 |               - "{{ install.get('ntp', {}).pool is defined and install.ntp.pool != '' }}"
  233 |               - "{{ install.version|openstack_release >= 15 }}"
  234 |           - configure_ntp_pool: "{{ (false in configure_ntp_pool_conditions) | ternary(False, True) }}"
  235 |         when: deploy_interface_direct or configure_ntp_pool or custom_template_configured
```

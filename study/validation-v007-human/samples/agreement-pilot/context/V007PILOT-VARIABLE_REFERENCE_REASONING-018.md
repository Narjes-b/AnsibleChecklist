# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-018

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `plugins/tripleo-overcloud/deploy.yml` (reported anchor line 270)
- Object: `variable` `df8c30e053b10ac3a4092dd080b20037248b17bb4235b964745510407cbfa1a7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–315 of 315:

```text
    1 | - name: non-container hacks
    2 |   hosts: undercloud
    3 |   any_errors_fatal: true
    4 |   tags:
    5 |       - deploy_preparation
    6 |       - deploy_environment
    7 |   tasks:
    8 |       - shell: |
    9 |           #MODIFY THT_ROOT to point to your tripleo-heat-templates
   10 |           THT_ROOT=/usr/share/openstack-tripleo-heat-templates/
   11 |           cd $THT_ROOT/environments
   12 |           > docker.yaml
   13 |           > docker-ha.yaml
   14 |           find . -exec sed -i -e "s|docker/services/collectd.yaml|puppet/services/metrics/collectd.yaml|g" {} \;
   15 |           find . -exec sed -e "s|docker/services/sensu-client.yaml|puppet/services/monitoring/sensu-client.yaml|g" -i {} \;
   16 |           find . -exec sed -e "s|docker/services|puppet/services|g" -i {} \;
   17 |         when:
   18 |           - not install.containers | bool
   19 |           - install.version|default(undercloud_version)|openstack_release >= 12
   20 |         become: yes
   21 | 
   22 | - import_playbook: build_templates.yml
   23 |   tags:
   24 |       - deploy_preparation
   25 |       - templates
   26 | 
   27 | - import_playbook: tls_everywhere.yml
   28 |   tags:
   29 |       - deploy_preparation
   30 |       - templates
   31 |       - freeipa
   32 |   when:
   33 |       - install.tls.everywhere|default(False)
   34 |       - install.version|default(undercloud_version)|openstack_release >= 12
   35 |       - (install.version|default(undercloud_version)|openstack_distribution) == 'OSP'
   36 | 
   37 | - name: Run heat agent script in a background if splitstack deployment
   38 |   hosts: undercloud
   39 |   gather_facts: no
   40 |   any_errors_fatal: true
   41 |   tags: deploy_preparation
   42 |   tasks:
   43 |     - name: Run heat agent script in a background if splitstack deployment
   44 |       shell: ~{{ ansible_user|default(ansible_ssh_user)  }}/heat-agent.sh > heat_agent.log 2>&1
   45 |       async: 1000
   46 |       poll: 0
   47 |       when: install.splitstack|default(False)
   48 | 
   49 | - name: Disable iscsid service on undercloud
   50 |   import_playbook: stop_iscsi.yml
   51 | 
   52 | # net/vip provisioning stpes moved to earlier stages in order to use VIP and other address
   53 | # in template generations, for example for IP based SSL certifactes
   54 | - name: Deploy the nodes
   55 |   vars:
   56 |       - template_base: "{{ ansible_user_dir }}/{{ install.deployment.files | basename }}"
   57 |   hosts: undercloud
   58 |   any_errors_fatal: true
   59 |   tasks:
   60 |       - name: Provision the ("baremetal") nodes
   61 |         shell: |
   62 |             source ~/stackrc
   63 |             set -o pipefail
   64 |             openstack overcloud node provision \
   65 |             {% if install.overcloud.ssh.user != '' %}
   66 |             --overcloud-ssh-user {{ install.overcloud.ssh.user }} \
   67 |             {% endif %}
   68 |             --concurrency {{ install.overcloud.concurrency }} \
   69 |             --network-config --stack {{ install.overcloud.stack }} \
   70 |             -o /home/stack/templates/overcloud-baremetal-deployed.yaml  {{ template_base }}/network/baremetal_deployment.yaml | \
   71 |             tee -a /home/stack/overcloud_provision_nodes.log
   72 |         when:
   73 |             - (install.version|default(undercloud_version) | openstack_release >= 17)
   74 |         tags: baremetal_deployment
   75 | 
   76 | 
   77 | # For <17, the inventory can't be updated at this point because the nodes
   78 | # don't exist here yet and they would end up in the "unused" group.
   79 | - name: Update inventory with details about node provisioning
   80 |   import_playbook: update_inventory.yml
   81 |   when:
   82 |       - (install.version|default(undercloud_version) | openstack_release >= 17)
   83 | 
   84 | - name: Deploy Deployed Ceph using cephadm and local UC registry
   85 |   hosts: undercloud
   86 |   vars:
   87 |       - containers_home_dir: "/home/stack"
   88 |       - template_base: "{{ ansible_user_dir }}/{{ install.deployment.files | basename }}"
   89 |       - ceph_node_cnt: "{{ ((install.storage.nodes|default(0)) or (groups['ceph']|default([])|length) or 1) }}"
   90 |   any_errors_fatal: true
   91 |   tasks:
   92 |       - name: Detect presence of roles_data.yaml
   93 |         stat:
   94 |           path: "{{ template_base }}/roles/roles_data.yaml"
   95 |         register: roles_data_file
   96 | 
   97 |       - block:
   98 |           - name: create ceph deploy script
   99 |             template:
  100 |                 src: templates/overcloud_ceph_deploy.sh.j2
  101 |                 dest: "~/overcloud_ceph_deploy.sh"
  102 |                 mode: 0755
  103 |                 force: true
  104 | 
  105 |           - name: Deploy Ceph separately from OC(Deployed Ceph topology)
  106 |             shell: |
  107 |                 source ~/stackrc
  108 |                 set -o pipefail
  109 |                 set -x
  110 |                 bash ~/overcloud_ceph_deploy.sh \
  111 |                   |& tee -a /home/stack/overcloud_ceph_deployment.log
  112 |         when:
  113 |             - (install.version|default(undercloud_version) | openstack_release >= 17.0)
  114 |             - install.storage.backend|default('') == 'ceph'
  115 |             - not install.storage.external
  116 | 
  117 | - name: Deploy the Overcloud
  118 |   hosts: undercloud
  119 |   gather_facts: yes
  120 |   any_errors_fatal: true
  121 |   vars:
  122 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  123 |   tags:
  124 |       - deploy
  125 |   tasks:
  126 |       - block:
  127 |           - name: adjust max number of concurrent builds to prevent undercloud overload
  128 |             ini_file:
  129 |                 path: /etc/nova/nova.conf
  130 |                 section: DEFAULT
  131 |                 option: max_concurrent_builds
  132 |                 value: 5
  133 |             become: yes
  134 | 
  135 |           - name: restart nova services
  136 |             command: "systemctl restart openstack-nova-*"
  137 |             become: yes
  138 |         when:
  139 |             - install.version|openstack_release < 10
  140 | 
  141 |       - name: Execute the pre overcloud deploy action
  142 |         shell: |
  143 |           {{ install.overcloud.predeploy.action }} &> pre_overcloud_install_action.log
  144 |         register: pre_overcloud_install_action
  145 |         when: install.get('overcloud', {}).get('predeploy', {}).get('action', {})
  146 | 
  147 |       - name: Execute the overcloud deploy script
  148 |         shell: |
  149 |             source ~/stackrc
  150 |             bash {{ overcloud_deploy_script }} &> overcloud_install.log
  151 |         register: overcloud_deploy
  152 |         ignore_errors: yes
  153 | 
  154 |       - include_role:
  155 |             name: tls-everywhere
  156 |         vars:
  157 |             stages:
  158 |                 - post_overcloud
  159 |         when:
  160 |             - install.tls.everywhere|default(False)
  161 |             - install.version|default(undercloud_version)|openstack_release >= 12
  162 |             - overcloud_deploy.rc == 0
  163 | 
  164 |       - name: Print the last few lines of the output to spot failures
  165 |         command: tail -n60 overcloud_install.log
  166 | 
  167 |       # List of failures is supported since RHOS10
  168 |       - name: Print stack failures
  169 |         shell: |
  170 |             source ~/stackrc
  171 |             openstack stack failures list {{ install.overcloud.stack }}
  172 |         when:
  173 |             - overcloud_deploy.rc != 0
  174 |             - install.version|default(undercloud_version)|openstack_release >= 10
  175 |             - install.version|default(undercloud_version)|openstack_release < 17
  176 |         tags: skip_ansible_lint
  177 | 
  178 |       - name: Prepare stack failures long log
  179 |         shell: |
  180 |             source ~/stackrc
  181 |             openstack stack failures list {{ install.overcloud.stack }} --long > openstack_failures_long.log
  182 |         when:
  183 |             - overcloud_deploy.rc != 0
  184 |             - install.version|default(undercloud_version)|openstack_release >= 10
  185 |             - install.version|default(undercloud_version)|openstack_release < 17
  186 |         tags: skip_ansible_lint
  187 | 
  188 |       - name: copy summary script
  189 |         template:
  190 |             src: deploy_info.sh.j2
  191 |             dest: ~/deploy_info.sh
  192 |             mode: 0755
  193 |         tags: summary
  194 | 
  195 |       - name: Prepare Execute the deployment summary script
  196 |         become: yes
  197 |         shell: |
  198 |             mkdir -p /var/log/extra/
  199 |             source ~{{ ansible_user|default(ansible_ssh_user) }}/stackrc
  200 |             ~{{ ansible_user|default(ansible_ssh_user) }}/deploy_info.sh --long > /var/log/extra/deploy_resources.log 2>&1 &
  201 |             ~{{ ansible_user|default(ansible_ssh_user) }}/deploy_info.sh 2>&1 &
  202 |             wait
  203 |         tags: summary
  204 | 
  205 |       - name: Execute the post overcloud deploy action
  206 |         shell: |
  207 |           {{ install.overcloud.postdeploy.action }} &> post_overcloud_install_action.log
  208 |         when: install.get('overcloud', {}).get('postdeploy', {}).get('action', {})
  209 | 
  210 | - name: Update inventory with overcloud details
  211 |   import_playbook: update_inventory.yml
  212 |   tags:
  213 |       - inventory_update
  214 |       - deploy
  215 | 
  216 | - name: Verify overcloud deployment
  217 |   hosts: undercloud
  218 |   gather_facts: no
  219 |   any_errors_fatal: true
  220 |   vars:
  221 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  222 |   tags:
  223 |       - deploy
  224 |   tasks:
  225 |     - fail:
  226 |           msg: "Overcloud deployment failed... :("
  227 |       when: overcloud_deploy is defined and overcloud_deploy.rc != 0
  228 | 
  229 |     - name: verify overcloudrc was created
  230 |       wait_for:
  231 |           path: "{{ overcloudrc_file }}"
  232 |           state: present
  233 |           timeout: 60
  234 | 
  235 |     - name: check if we have v3 rc file
  236 |       stat:
  237 |           path: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc.v3"
  238 |       register: rc_file_path
  239 |       tags:
  240 |           - clouds_file
  241 | 
  242 |     - name: update clouds.yaml file
  243 |       include_tasks: clouds.yml
  244 |       vars:
  245 |             v3_file: "{{ install.overcloud.stack }}rc.v3"
  246 |             v2_file: "{{ install.overcloud.stack }}rc"
  247 |             auth_file_path: "{{ ansible_user_dir }}/{{ rc_file_path.stat.exists | ternary(v3_file, v2_file) }}"
  248 |             cloudname: "{{ install.overcloud.stack }}"
  249 |       tags:
  250 |           - clouds_file
  251 | 
  252 |     - name: fetch the overcloud rc file
  253 |       tags:
  254 |           - fetch_rc_file
  255 |       fetch:
  256 |           src: "{{ overcloudrc_file }}"
  257 |           dest: "{{ inventory_dir }}/keystonerc"
  258 |           flat: yes
  259 |           fail_on_missing: yes
  260 | 
  261 |     - name: fetch overcloud v3 file if present
  262 |       tags:
  263 |           - fetch_rc_file
  264 |       fetch:
  265 |           src: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc.v3"
  266 |           dest: "{{ inventory_dir }}/{{ install.overcloud.stack }}rc.v3"
  267 |           flat: yes
  268 |           fail_on_missing: no
  269 | 
  270 |     - name: Read baremetal nodes got from user input on hybrid deployment
  271 |       block:
  272 |         - name: Set hybrid var
  273 |           include_vars:
  274 |               file: "{{ install.hybrid }}"
  275 |               name: bm_nodes
  276 | 
  277 |         - name: get nodes name
  278 |           set_fact:
  279 |               node_name: "{{ item.name }}"
  280 |           with_items: "{{ bm_nodes.nodes }}"
  281 |           register: nodes
  282 | 
  283 |         - name: set list of bm nodes
  284 |           set_fact:
  285 |               bm_nodes: "{{ nodes.results | map(attribute='ansible_facts.node_name') | list }}"
  286 |       when: install.hybrid is defined
  287 | 
  288 |     - name: set bm_nodes to empty when not hybrid
  289 |       set_fact:
  290 |           bm_nodes: ""
  291 |       when: install.hybrid is not defined
  292 | 
  293 |     - name: Get overcloud nodes
  294 |       set_fact:
  295 |         oc_nodes: "{{ groups.get('overcloud_nodes', []) }}"
  296 | 
  297 | - name: Allow vbmc ports for all the overcloud nodes
  298 |   hosts: localhost
  299 |   gather_facts: no
  300 |   any_errors_fatal: true
  301 |   tags:
  302 |       - deploy
  303 |       - vbmc_post
  304 |   vars_files:
  305 |       - "{{ install.public.subnet }}"
  306 |   tasks:
  307 |       - name: setup vbmc access for all the available overcloud nodes
  308 |         include_role:
  309 |             name: vbmc
  310 |             tasks_from: iptables_overcloud.yml
  311 |         when:
  312 |             - "'hypervisor' in groups"
  313 |             - install.version|default(undercloud_version) | openstack_release >= 11 or install.vbmc.force
  314 |             - subnet is defined
  315 |             - subnet.cidr is defined
```

## Visible variable references

```text
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/deploy.yml:275:              name: bm_nodes
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/deploy.yml:280:          with_items: "{{ bm_nodes.nodes }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/deploy.yml:285:              bm_nodes: "{{ nodes.results | map(attribute='ansible_facts.node_name') | list }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/deploy.yml:288:    - name: set bm_nodes to empty when not hybrid
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/deploy.yml:290:          bm_nodes: ""
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:39:                name: bm_nodes
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:44:            with_items: "{{ bm_nodes.nodes }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:49:                bm_nodes_names: "{{ nodes.results | map(attribute='ansible_facts.node_name') | list }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:52:      - name: set bm_nodes to empty when not hybrid
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:54:            bm_nodes_names: ""
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:68:            vbmc_nodes: "{{ oc_nodes + oc_ironic | difference(bm_nodes_names) }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:92:            - "{{ oc_nodes + oc_ironic | difference(bm_nodes_names) }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:97:            vm_nodes: "{{ oc_nodes | difference(bm_nodes_names) }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:131:            vm_nodes: "{{ oc_ironic | difference(bm_nodes_names) }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/hypervisor.yml:156:            vm_nodes: "{{ oc_nodes + oc_ironic | difference(bm_nodes_names) }}"
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/templates/instackenv.json.j2:10:{% for bm_host in (bm_nodes|default({}))['nodes']|default([]) %}
d00a414759c83765e8fd2e19d48f06d492736a93:plugins/tripleo-overcloud/templates/instackenv.json.j2:18:    {% if loop.first and (bm_nodes|default({}))['nodes']|default([]) %},{% endif %}
```

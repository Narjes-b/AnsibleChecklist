# Frozen source context: V007PILOT2-STRUCTURE_REUSE-011

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: structure_reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `plugins/tripleo-overcloud/deploy.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`plugins/tripleo-overcloud/deploy.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

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

## Frozen tracked paths in the relevant role/scope

```text
Scope: `.`; 1181 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

Listing exceeds 400: paths beside the cited file, then a per-directory count of ALL paths.
plugins/tripleo-overcloud/build_templates.yml
plugins/tripleo-overcloud/clouds.yml
plugins/tripleo-overcloud/collect-ansible-facts.yml
plugins/tripleo-overcloud/composable_roles.yml
plugins/tripleo-overcloud/delete.yml
plugins/tripleo-overcloud/deploy.yml
plugins/tripleo-overcloud/docker_after_workaround.yml
plugins/tripleo-overcloud/fetchfiles.yml
plugins/tripleo-overcloud/files/ansible_playbook/Compute.yaml
plugins/tripleo-overcloud/files/ansible_playbook/Controller.sssd_selinux.yaml.j2
plugins/tripleo-overcloud/files/ansible_playbook/Controller.yaml
plugins/tripleo-overcloud/files/ansible_playbook/ControllerOpenstack.yaml
plugins/tripleo-overcloud/files/ansible_playbook/Database.yaml
plugins/tripleo-overcloud/files/ansible_playbook/Messaging.yaml
plugins/tripleo-overcloud/files/ansible_playbook/Networker.yaml
plugins/tripleo-overcloud/files/config_lvm.yaml
plugins/tripleo-overcloud/files/control_node_placement/network_mapping.yaml
plugins/tripleo-overcloud/files/debug.yaml
plugins/tripleo-overcloud/files/firstboot/firstboot-infrared.yaml
plugins/tripleo-overcloud/files/generate_baremetal_deployment_from_roles_data.py
plugins/tripleo-overcloud/files/network/neutron-lbaas.yml
plugins/tripleo-overcloud/files/roles/composition/controller.yml
plugins/tripleo-overcloud/files/roles/composition/database.yml
plugins/tripleo-overcloud/files/roles/composition/messaging.yml
plugins/tripleo-overcloud/files/roles/composition/networker.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker-novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker-novacontrol/database.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker-novacontrol/messaging.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker-novacontrol/networker.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker-novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker/controller.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker/database.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker/messaging.yml
plugins/tripleo-overcloud/files/roles/database-messaging-networker/networker.yml
plugins/tripleo-overcloud/files/roles/database-messaging-novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/database-messaging-novacontrol/database.yml
plugins/tripleo-overcloud/files/roles/database-messaging-novacontrol/messaging.yml
plugins/tripleo-overcloud/files/roles/database-messaging-novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/database-messaging/controller.yml
plugins/tripleo-overcloud/files/roles/database-messaging/database.yml
plugins/tripleo-overcloud/files/roles/database-messaging/messaging.yml
plugins/tripleo-overcloud/files/roles/database-networker-novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/database-networker-novacontrol/database.yml
plugins/tripleo-overcloud/files/roles/database-networker-novacontrol/networker.yml
plugins/tripleo-overcloud/files/roles/database-networker-novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/database-networker/controller.yml
plugins/tripleo-overcloud/files/roles/database-networker/database.yml
plugins/tripleo-overcloud/files/roles/database-networker/networker.yml
plugins/tripleo-overcloud/files/roles/database-novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/database-novacontrol/database.yml
plugins/tripleo-overcloud/files/roles/database-novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/database/controller.yml
plugins/tripleo-overcloud/files/roles/database/database.yml
plugins/tripleo-overcloud/files/roles/default/ceph.yml
plugins/tripleo-overcloud/files/roles/default/compute.yml
plugins/tripleo-overcloud/files/roles/default/controller.yml
plugins/tripleo-overcloud/files/roles/default/swift.yml
plugins/tripleo-overcloud/files/roles/hcicephmon/controller.yml
plugins/tripleo-overcloud/files/roles/hcicephmon/hcicephmon.yml
plugins/tripleo-overcloud/files/roles/heat/controller.yml
plugins/tripleo-overcloud/files/roles/heat/heat.yml
plugins/tripleo-overcloud/files/roles/ironic/controller.yml
plugins/tripleo-overcloud/files/roles/ironic/ironic.yml
plugins/tripleo-overcloud/files/roles/mds/controller.yml
plugins/tripleo-overcloud/files/roles/mds/mds.yml
plugins/tripleo-overcloud/files/roles/messaging-networker-novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/messaging-networker-novacontrol/messaging.yml
plugins/tripleo-overcloud/files/roles/messaging-networker-novacontrol/networker.yml
plugins/tripleo-overcloud/files/roles/messaging-networker-novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/messaging-novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/messaging-novacontrol/messaging.yml
plugins/tripleo-overcloud/files/roles/messaging-novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/messaging/controller.yml
plugins/tripleo-overcloud/files/roles/messaging/messaging.yml
plugins/tripleo-overcloud/files/roles/monitor/controller.yml
plugins/tripleo-overcloud/files/roles/monitor/monitor.yml
plugins/tripleo-overcloud/files/roles/networker-messaging/controller.yml
plugins/tripleo-overcloud/files/roles/networker-messaging/messaging.yml
plugins/tripleo-overcloud/files/roles/networker-messaging/networker.yml
plugins/tripleo-overcloud/files/roles/networker-novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/networker-novacontrol/networker.yml
plugins/tripleo-overcloud/files/roles/networker-novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/networker/README.md
plugins/tripleo-overcloud/files/roles/networker/controller.yml
plugins/tripleo-overcloud/files/roles/networker/networker.yml
plugins/tripleo-overcloud/files/roles/novacontrol/compute.yml
plugins/tripleo-overcloud/files/roles/novacontrol/controller.yml
plugins/tripleo-overcloud/files/roles/novacontrol/novacontrol.yml
plugins/tripleo-overcloud/files/roles/osdcompute/osdcompute.yml
plugins/tripleo-overcloud/files/roles/radosgw/controller.yml
plugins/tripleo-overcloud/files/roles/radosgw/radosgw.yml
plugins/tripleo-overcloud/files/roles/serviceapi/controller.yml
plugins/tripleo-overcloud/files/roles/serviceapi/serviceapi.yml
plugins/tripleo-overcloud/files/roles/serviceapi_networker/controller.yml
plugins/tripleo-overcloud/files/roles/serviceapi_networker/networker.yml
plugins/tripleo-overcloud/files/roles/serviceapi_networker/serviceapi.yml
plugins/tripleo-overcloud/files/roles/telemetry/controller.yml
plugins/tripleo-overcloud/files/roles/telemetry/telemetry.yml
plugins/tripleo-overcloud/files/upgrade/10/ignore-ceph-warnings.yaml
plugins/tripleo-overcloud/hypervisor.yml
plugins/tripleo-overcloud/install.yml
plugins/tripleo-overcloud/introspect.yml
plugins/tripleo-overcloud/library/roles_node_count.py
plugins/tripleo-overcloud/library/set_default_route_networks.py
plugins/tripleo-overcloud/library/yedit.py
plugins/tripleo-overcloud/loadbalancer.yml
plugins/tripleo-overcloud/local-nfs-server.yml
plugins/tripleo-overcloud/main.yml
plugins/tripleo-overcloud/ovb.yml
plugins/tripleo-overcloud/overcloud_ceph_reboot.yml
plugins/tripleo-overcloud/overcloud_compute_reboot.yml
plugins/tripleo-overcloud/overcloud_controllers_reboot.yml
plugins/tripleo-overcloud/overcloud_reboot.yml
plugins/tripleo-overcloud/plugin.spec
plugins/tripleo-overcloud/pre.yml
plugins/tripleo-overcloud/roles/containers/append-deploy-script/meta/main.yml
plugins/tripleo-overcloud/roles/containers/append-deploy-script/tasks/main.yml
plugins/tripleo-overcloud/roles/containers/common/defaults/main.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/meta/main.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build/build_images.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build/container_images_packages.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build/patch_images.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build/patch_images_do.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build/patch_images_tripleo-modify-image.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build/prepare_tmp_repos.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build/update_images.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/ceph-ansible.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/customize_cinder_pure.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/env_files.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/main.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/nondefault_images_fact.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/override_container_images_urls.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/pre.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/workarounds.yml
plugins/tripleo-overcloud/roles/containers/prepare-templates/templates/cinder-pure-Dockerfile.j2
plugins/tripleo-overcloud/roles/loadbalancer/tasks/main.yml
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.service.j2
plugins/tripleo-overcloud/roles/loadbalancer/templates/vlan-external.cfg.j2
plugins/tripleo-overcloud/roles/loadbalancer/templates/vlan-internal_api.cfg.j2
plugins/tripleo-overcloud/roles/loadbalancer/templates/vlan-plain.cfg.j2
plugins/tripleo-overcloud/roles/loadbalancer/templates/vlan-storage.cfg.j2
plugins/tripleo-overcloud/roles/loadbalancer/templates/vlan-storage_mgmt.cfg.j2
plugins/tripleo-overcloud/roles/loadbalancer/templates/vlan-tenant.cfg.j2
plugins/tripleo-overcloud/splitstack.yml
plugins/tripleo-overcloud/stop_iscsi.yml
plugins/tripleo-overcloud/tag.yml
plugins/tripleo-overcloud/tasks/add_overcloud_host.yml
plugins/tripleo-overcloud/tasks/append_script.yml
plugins/tripleo-overcloud/tasks/composable_roles/add_role_vars.yml
plugins/tripleo-overcloud/tasks/control_node_placement/custom_hostnames.yml
plugins/tripleo-overcloud/tasks/control_node_placement/predictable_ips.yml
plugins/tripleo-overcloud/tasks/control_node_placement/specific_node_ids.yml
plugins/tripleo-overcloud/tasks/discover_provision_net.yml
plugins/tripleo-overcloud/tasks/environment_plan.yml
plugins/tripleo-overcloud/tasks/environment_templates.yml
plugins/tripleo-overcloud/tasks/fencing.yml
plugins/tripleo-overcloud/tasks/firstboot.yml
plugins/tripleo-overcloud/tasks/generate_baremetal_deployment.yml
plugins/tripleo-overcloud/tasks/hostname.yml
plugins/tripleo-overcloud/tasks/introspection_recovery.yml
plugins/tripleo-overcloud/tasks/ironic_environment_templates.yml
plugins/tripleo-overcloud/tasks/loadbalancer_templates.yml
plugins/tripleo-overcloud/tasks/multirhel.yml
plugins/tripleo-overcloud/tasks/network.yml
plugins/tripleo-overcloud/tasks/network/custom_network_names.yml
plugins/tripleo-overcloud/tasks/opstools/main.yml
plugins/tripleo-overcloud/tasks/rdo-docker-ha.yml
plugins/tripleo-overcloud/tasks/ssl.yml
plugins/tripleo-overcloud/tasks/storage/ceph.yml
plugins/tripleo-overcloud/tasks/storage/discover_backend.yml
plugins/tripleo-overcloud/tasks/storage/disks_from_instackenv.yml
plugins/tripleo-overcloud/tasks/storage/lvm.yml
plugins/tripleo-overcloud/tasks/storage/main.yml
plugins/tripleo-overcloud/tasks/storage/netapp-iscsi.yml
plugins/tripleo-overcloud/tasks/storage/netapp-nfs.yml
plugins/tripleo-overcloud/tasks/storage/netapp.yml
plugins/tripleo-overcloud/tasks/storage/nfs.yml
plugins/tripleo-overcloud/tasks/storage/nova-nfs.yml
plugins/tripleo-overcloud/tasks/storage/swift.yml
plugins/tripleo-overcloud/tasks/trust_uc.yml
plugins/tripleo-overcloud/tasks/undercloud-ext-vlan.yml
plugins/tripleo-overcloud/tasks/update/common/create_update_script.yaml
plugins/tripleo-overcloud/tasks/update/common/endping.yaml
plugins/tripleo-overcloud/tasks/update/common/startping.yaml
plugins/tripleo-overcloud/tasks/update/common/update_mistral_plan.yaml
plugins/tripleo-overcloud/tasks/update/common/update_overcloud.yaml
plugins/tripleo-overcloud/tasks/update/undercloud_validation.yml
plugins/tripleo-overcloud/tasks/upgrade/10/aodh_migration.yml
plugins/tripleo-overcloud/tasks/upgrade/10/ceilometer_migration.yml
plugins/tripleo-overcloud/tasks/upgrade/10/controller_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/10/convergence.yml
plugins/tripleo-overcloud/tasks/upgrade/10/main.yml
plugins/tripleo-overcloud/tasks/upgrade/10/ssl.yml
plugins/tripleo-overcloud/tasks/upgrade/10/upgrade_init.yml
plugins/tripleo-overcloud/tasks/upgrade/11/ceph_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/11/composable_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/11/compute_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/11/controller_postupgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/11/converge_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/11/convert_cli_options.yml
plugins/tripleo-overcloud/tasks/upgrade/11/convert_roles_data.yml
plugins/tripleo-overcloud/tasks/upgrade/11/custom_roles_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/11/evacute_compute.yml
plugins/tripleo-overcloud/tasks/upgrade/11/main.yml
plugins/tripleo-overcloud/tasks/upgrade/11/packages_check.yml
plugins/tripleo-overcloud/tasks/upgrade/11/reboot_node.yml
plugins/tripleo-overcloud/tasks/upgrade/11/swift_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/8/controller_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/8/convergence.yml
plugins/tripleo-overcloud/tasks/upgrade/8/main.yml
plugins/tripleo-overcloud/tasks/upgrade/8/upgrade_init.yml
plugins/tripleo-overcloud/tasks/upgrade/9/main.yml
plugins/tripleo-overcloud/tasks/upgrade/9/ssl.yml
plugins/tripleo-overcloud/tasks/upgrade/common/node_upgrade.yml
plugins/tripleo-overcloud/tasks/upgrade/common/upgrade_step.yml
plugins/tripleo-overcloud/tasks/upgrade/overcloud_validation.yml
plugins/tripleo-overcloud/tasks/upgrade/undercloud_validation.yml
plugins/tripleo-overcloud/templates/ComputeRHEL8.yaml.j2
plugins/tripleo-overcloud/templates/composable_roles/network-config.yaml.j2
plugins/tripleo-overcloud/templates/composable_roles/nodes.yaml.j2
plugins/tripleo-overcloud/templates/composable_roles/overcloud_deploy.sh.j2
plugins/tripleo-overcloud/templates/composable_roles/roles_data.yaml.j2
plugins/tripleo-overcloud/templates/compute-dvr.yaml.j2
plugins/tripleo-overcloud/templates/control_node_placement/custom_hostnames.yaml.j2
plugins/tripleo-overcloud/templates/control_node_placement/predictable_ips.yaml.j2
plugins/tripleo-overcloud/templates/control_node_placement/scheduler_hints_env.yaml.j2
plugins/tripleo-overcloud/templates/debug.yaml.j2
plugins/tripleo-overcloud/templates/deploy_info.sh.j2
plugins/tripleo-overcloud/templates/dvr-override.yaml.j2
plugins/tripleo-overcloud/templates/firstboot.yaml.j2
plugins/tripleo-overcloud/templates/hostnames.yml.j2
plugins/tripleo-overcloud/templates/ifcfg-vlan.j2
plugins/tripleo-overcloud/templates/instackenv-bmc.json.j2
plugins/tripleo-overcloud/templates/instackenv.json.j2
plugins/tripleo-overcloud/templates/ironic-custom.yaml.j2
plugins/tripleo-overcloud/templates/loadbalancer/external-lb.yaml.j2
plugins/tripleo-overcloud/templates/loadbalancer/vlan-internal_api.cfg.j2
plugins/tripleo-overcloud/templates/network_data-v6.yaml.j2
plugins/tripleo-overcloud/templates/network_data.yaml.j2
plugins/tripleo-overcloud/templates/nodes_data.yaml.j2
plugins/tripleo-overcloud/templates/nodes_software_config.yaml.j2
plugins/tripleo-overcloud/templates/opstools/collectd.yml.j2
plugins/tripleo-overcloud/templates/opstools/logging_no_ssl.yml.j2
plugins/tripleo-overcloud/templates/opstools/monitoring.yml.j2
plugins/tripleo-overcloud/templates/overcloud_ceph_deploy.sh.j2
plugins/tripleo-overcloud/templates/overcloud_deploy.sh.j2
plugins/tripleo-overcloud/templates/overcloud_ironic_nodes.yaml.j2
plugins/tripleo-overcloud/templates/splitstack/ctrlplane-template.yml.j2
plugins/tripleo-overcloud/templates/splitstack/heat-agent.sh.j2
plugins/tripleo-overcloud/templates/splitstack/overcloud_deploy.sh.j2
plugins/tripleo-overcloud/templates/splitstack/roles-port-config.yml.j2
plugins/tripleo-overcloud/templates/ssl/cloud-names.yaml.j2
plugins/tripleo-overcloud/templates/ssl/public_vip.yaml.j2
plugins/tripleo-overcloud/templates/sssd_selinux_workaround.yaml
plugins/tripleo-overcloud/templates/storage/cinder-nfs-custom.yml.j2
plugins/tripleo-overcloud/templates/storage/internal.yml.j2
plugins/tripleo-overcloud/templates/storage/nova-nfs-custom.yml.j2
plugins/tripleo-overcloud/templates/tripleo_roles/hostnames.yaml.j2
plugins/tripleo-overcloud/templates/tripleo_roles/nodes.yaml.j2
plugins/tripleo-overcloud/templates/tripleo_roles/overcloud_deploy.sh.j2
plugins/tripleo-overcloud/templates/tripleo_roles/tripleo_roles.sh.j2
plugins/tripleo-overcloud/tls_everywhere.yml
plugins/tripleo-overcloud/tripleo_roles.yml
plugins/tripleo-overcloud/update.yml
plugins/tripleo-overcloud/update_inventory.yml
plugins/tripleo-overcloud/upgrade.yml
plugins/tripleo-overcloud/validate.yml
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/network-environment-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/network-environment.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/network-environment_v2.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/network_data_v2.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ceph-storage.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ceph-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/cinder-storage.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/cinder-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/compute.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/computehci.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/controller-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/controller.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/database.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/database.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/database_internal.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/heat.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ironic.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ironicconductor.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/ceph-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/cinder-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/controller-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/database.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/database_internal.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/heat.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/ironic.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/messaging.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/messaging_internal.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/monitor.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/networker.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/novacontrol.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/opstools.yml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/osdcompute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/radosgw.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/serviceapi.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/swift-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/messaging.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/messaging.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/messaging_internal.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/monitor.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/networker.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/networker.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/novacontrol.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/novacontrol.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/opstools.yml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/osdcompute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/radosgw.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/serviceapi.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/swift-storage.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/swift-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/telemetry.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/predictable-ips-v6.yaml
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/predictable-ips.yaml
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/vip_data.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/ovb/README
plugins/tripleo-overcloud/vars/deployment/files/virt/network/baremetal_deployment.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/network-environment-v6-all.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/network-environment-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/network-environment.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/network-environment_v2.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/network_data_v2.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/predictable-ips-v6.yaml
plugins/tripleo-overcloud/vars/deployment/files/virt/network/predictable-ips.yaml
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/ceph-storage.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/ceph-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/cinder-storage.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/cinder-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/compute-dvr.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/compute.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller-v6.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/ceph-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/cinder-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/controller-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/swift-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/swift-storage.j2.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/swift-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt/network/vip_data.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/network-environment.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/three-nics-vlans/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/three-nics-vlans/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/legacy/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/legacy/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/network-environment.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/predictable-ips.yaml
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/ceph-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/cinder-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/controller-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/ceph-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/cinder-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/controller-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/swift-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/swift-storage.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/network-environment-v6.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/network-environment.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/four-nics-vlans/compute.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/four-nics-vlans/controller.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/network-environment.yaml.j2
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/predictable-ips.yaml
plugins/tripleo-overcloud/vars/environment/plan/example.yml
plugins/tripleo-overcloud/vars/instackenv/profiles.yml
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv4.yml
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv6.yml
plugins/tripleo-overcloud/vars/overcloud/templates/aide.yml
plugins/tripleo-overcloud/vars/overcloud/templates/barbican-backend-pkcs11-atos.yml
plugins/tripleo-overcloud/vars/overcloud/templates/barbican-backend-pkcs11-thales.yml
plugins/tripleo-overcloud/vars/overcloud/templates/barbican.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceilometer-write-qdr-edge-only.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceilometer-write-qdr-mesh.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-ansible-external.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-ansible.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-crush-class.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-dashboard.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-mds.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-min-osds.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-osd-encryption.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-rbdmirror.yml
plugins/tripleo-overcloud/vars/overcloud/templates/ceph-rgw.yml
[88 further paths beside the cited file not listed]

Per-directory path counts:
.: 17
docs: 2
docs/examples: 6
docs/source: 41
docs/source/_static: 1
etc/bash_completion.d: 1
infrared: 5
infrared/common: 1
infrared/common/callback_plugins: 2
infrared/common/filter_plugins: 6
infrared/common/library: 4
infrared/common/roles: 1
infrared/common/roles/cdn_registery/defaults: 1
infrared/common/roles/cdn_registery/tasks: 2
infrared/common/roles/collect-ansible-facts/defaults: 1
infrared/common/roles/collect-ansible-facts/tasks: 1
infrared/common/roles/create_venv/defaults: 1
infrared/common/roles/create_venv/tasks: 1
infrared/common/roles/dstat/tasks: 1
infrared/common/roles/dstat/templates: 1
infrared/common/roles/freeipa-setup: 1
infrared/common/roles/freeipa-setup/defaults: 1
infrared/common/roles/freeipa-setup/meta: 1
infrared/common/roles/freeipa-setup/tasks: 2
infrared/common/roles/freeipa-setup/templates: 2
infrared/common/roles/from-script/defaults: 1
infrared/common/roles/from-script/tasks: 1
infrared/common/roles/from-source/defaults: 1
infrared/common/roles/from-source/tasks: 2
infrared/common/roles/from-source/templates: 1
infrared/common/roles/inventory-update: 1
infrared/common/roles/inventory-update/defaults: 1
infrared/common/roles/inventory-update/tasks: 1
infrared/common/roles/inventory-update/templates: 1
infrared/common/roles/network/forward-port/defaults: 1
infrared/common/roles/network/forward-port/tasks: 1
infrared/common/roles/rdo-release/defaults: 1
infrared/common/roles/rdo-release/tasks: 3
infrared/common/roles/resurrect_host/tasks: 1
infrared/common/roles/rhos-release/defaults: 1
infrared/common/roles/rhos-release/files: 2
infrared/common/roles/rhos-release/tasks: 1
infrared/common/roles/shade: 1
infrared/common/roles/shade/defaults: 1
infrared/common/roles/shade/tasks: 1
infrared/common/roles/tls-ca/tasks: 2
infrared/common/roles/tls-everywhere: 1
infrared/common/roles/tls-everywhere/defaults: 1
infrared/common/roles/tls-everywhere/tasks: 8
infrared/common/roles/tls-everywhere/templates: 4
infrared/common/roles/tls-everywhere/vars: 2
infrared/common/roles/vbmc: 1
infrared/common/roles/vbmc/defaults: 1
infrared/common/roles/vbmc/tasks: 8
infrared/common/roles/version-discovery: 1
infrared/common/roles/version-discovery/defaults: 1
infrared/common/roles/version-discovery/tasks: 4
infrared/core: 3
infrared/core/cli: 2
infrared/core/inspector: 3
infrared/core/services: 5
infrared/core/utils: 7
plugins/beaker: 4
plugins/beaker/library: 1
plugins/beaker/vars/image: 10
plugins/collect-logs: 2
plugins/collect-logs/tasks: 4
plugins/collect-logs/vars: 1
plugins/foreman: 3
plugins/foreman/library: 1
plugins/list-builds: 2
plugins/list-builds/library: 1
plugins/list-builds/templates: 1
plugins/openstack: 9
plugins/openstack/defaults/topology/network: 3
plugins/openstack/defaults/topology/nodes: 13
plugins/openstack/roles/bmc/files: 1
plugins/openstack/roles/bmc/tasks: 2
plugins/openstack/roles/bmc/templates: 3
plugins/openstack/roles/bmc/vars: 1
plugins/openstack/roles/hostvars/defaults: 1
plugins/openstack/roles/hostvars/tasks: 3
plugins/openstack/roles/hostvars/templates: 1
plugins/openstack/tasks: 6
plugins/openstack/vars/topology/network: 1
plugins/openstack/vars/topology/nodes: 1
plugins/ospdui: 6
plugins/ospdui/roles/vnc-server/defaults: 1
plugins/ospdui/roles/vnc-server/tasks: 1
plugins/ospdui/roles/vnc-server/templates: 1
plugins/ospdui/tasks: 4
plugins/ospdui/templates: 2
plugins/ospdui/vars/setup: 2
plugins/ospdui/vars/topology/config: 1
plugins/packstack: 8
plugins/packstack/files: 1
plugins/packstack/vars/network/common: 1
plugins/packstack/vars/network/service: 2
plugins/packstack/vars/network/variant: 6
plugins/packstack/vars/public/subnet: 1
plugins/pytest-runner: 3
plugins/rally: 2
plugins/rally/filter_plugins: 1
plugins/rally/tasks: 1
plugins/rally/tasks/post: 1
plugins/rally/tasks/pre: 1
plugins/rally/tasks/setup: 1
plugins/rally/tasks/setup/git: 1
plugins/rally/tasks/setup/pip: 1
plugins/rally/tasks/setup/rpm: 2
plugins/rally/vars/image: 1
plugins/rally/vars/setup: 3
plugins/rally/vars/tests: 23
plugins/tempest: 2
plugins/tempest/tasks: 5
plugins/tempest/tasks/configure: 5
plugins/tempest/tasks/configure/method: 5
plugins/tempest/tasks/image: 1
plugins/tempest/tasks/pre: 4
plugins/tempest/tasks/setup: 1
plugins/tempest/tasks/setup/git: 2
plugins/tempest/tasks/setup/pip: 2
plugins/tempest/tasks/setup/rpm: 3
plugins/tempest/vars: 2
plugins/tempest/vars/config: 1
plugins/tempest/vars/setup: 3
plugins/tempest/vars/tests: 62
plugins/tripleo-overcloud: 32
plugins/tripleo-overcloud/files: 3
plugins/tripleo-overcloud/files/ansible_playbook: 7
plugins/tripleo-overcloud/files/control_node_placement: 1
plugins/tripleo-overcloud/files/firstboot: 1
plugins/tripleo-overcloud/files/network: 1
plugins/tripleo-overcloud/files/roles/composition: 4
plugins/tripleo-overcloud/files/roles/database: 2
plugins/tripleo-overcloud/files/roles/database-messaging: 3
plugins/tripleo-overcloud/files/roles/database-messaging-networker: 4
plugins/tripleo-overcloud/files/roles/database-messaging-networker-novacontrol: 5
plugins/tripleo-overcloud/files/roles/database-messaging-novacontrol: 4
plugins/tripleo-overcloud/files/roles/database-networker: 3
plugins/tripleo-overcloud/files/roles/database-networker-novacontrol: 4
plugins/tripleo-overcloud/files/roles/database-novacontrol: 3
plugins/tripleo-overcloud/files/roles/default: 4
plugins/tripleo-overcloud/files/roles/hcicephmon: 2
plugins/tripleo-overcloud/files/roles/heat: 2
plugins/tripleo-overcloud/files/roles/ironic: 2
plugins/tripleo-overcloud/files/roles/mds: 2
plugins/tripleo-overcloud/files/roles/messaging: 2
plugins/tripleo-overcloud/files/roles/messaging-networker-novacontrol: 4
plugins/tripleo-overcloud/files/roles/messaging-novacontrol: 3
plugins/tripleo-overcloud/files/roles/monitor: 2
plugins/tripleo-overcloud/files/roles/networker: 3
plugins/tripleo-overcloud/files/roles/networker-messaging: 3
plugins/tripleo-overcloud/files/roles/networker-novacontrol: 3
plugins/tripleo-overcloud/files/roles/novacontrol: 3
plugins/tripleo-overcloud/files/roles/osdcompute: 1
plugins/tripleo-overcloud/files/roles/radosgw: 2
plugins/tripleo-overcloud/files/roles/serviceapi: 2
plugins/tripleo-overcloud/files/roles/serviceapi_networker: 3
plugins/tripleo-overcloud/files/roles/telemetry: 2
plugins/tripleo-overcloud/files/upgrade/10: 1
plugins/tripleo-overcloud/library: 3
plugins/tripleo-overcloud/roles/containers/append-deploy-script/meta: 1
plugins/tripleo-overcloud/roles/containers/append-deploy-script/tasks: 1
plugins/tripleo-overcloud/roles/containers/common/defaults: 1
plugins/tripleo-overcloud/roles/containers/prepare-templates/meta: 1
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks: 8
plugins/tripleo-overcloud/roles/containers/prepare-templates/tasks/build: 7
plugins/tripleo-overcloud/roles/containers/prepare-templates/templates: 1
plugins/tripleo-overcloud/roles/loadbalancer/tasks: 1
plugins/tripleo-overcloud/roles/loadbalancer/templates: 8
plugins/tripleo-overcloud/tasks: 18
plugins/tripleo-overcloud/tasks/composable_roles: 1
plugins/tripleo-overcloud/tasks/control_node_placement: 3
plugins/tripleo-overcloud/tasks/network: 1
plugins/tripleo-overcloud/tasks/opstools: 1
plugins/tripleo-overcloud/tasks/storage: 11
plugins/tripleo-overcloud/tasks/update: 1
plugins/tripleo-overcloud/tasks/update/common: 5
plugins/tripleo-overcloud/tasks/upgrade: 2
plugins/tripleo-overcloud/tasks/upgrade/10: 7
plugins/tripleo-overcloud/tasks/upgrade/11: 13
plugins/tripleo-overcloud/tasks/upgrade/8: 4
plugins/tripleo-overcloud/tasks/upgrade/9: 2
plugins/tripleo-overcloud/tasks/upgrade/common: 2
plugins/tripleo-overcloud/templates: 19
plugins/tripleo-overcloud/templates/composable_roles: 4
plugins/tripleo-overcloud/templates/control_node_placement: 3
plugins/tripleo-overcloud/templates/loadbalancer: 2
plugins/tripleo-overcloud/templates/opstools: 3
plugins/tripleo-overcloud/templates/splitstack: 4
plugins/tripleo-overcloud/templates/ssl: 2
plugins/tripleo-overcloud/templates/storage: 3
plugins/tripleo-overcloud/templates/tripleo_roles: 4
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network: 7
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs: 31
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy: 19
plugins/tripleo-overcloud/vars/deployment/files/ovb: 1
plugins/tripleo-overcloud/vars/deployment/files/virt/network: 9
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans: 13
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy: 6
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network: 1
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/three-nics-vlans: 2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network: 2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans: 2
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/legacy: 2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network: 2
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans: 6
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy: 6
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network: 2
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/four-nics-vlans: 2
plugins/tripleo-overcloud/vars/environment/plan: 1
plugins/tripleo-overcloud/vars/instackenv: 1
plugins/tripleo-overcloud/vars/loadbalancer: 2
plugins/tripleo-overcloud/vars/overcloud/templates: 97
plugins/tripleo-overcloud/vars/public/subnet: 2
plugins/tripleo-overcloud/vars/storage/ceph: 1
plugins/tripleo-overcloud/vars/storage/config: 1
plugins/tripleo-standalone: 4
plugins/tripleo-standalone/templates: 2
plugins/tripleo-undercloud: 23
plugins/tripleo-undercloud/tasks: 6
plugins/tripleo-undercloud/tasks/images: 6
plugins/tripleo-undercloud/tasks/upgrade: 3
plugins/tripleo-undercloud/templates: 5
plugins/tripleo-undercloud/vars/cdn: 1
plugins/tripleo-undercloud/vars/ssl: 1
plugins/tripleo-undercloud/vars/topology: 2
plugins/virsh: 28
plugins/virsh/defaults/topology/network: 23
plugins/virsh/defaults/topology/nodes: 55
plugins/virsh/filter_plugins: 2
plugins/virsh/tasks: 26
plugins/virsh/templates: 12
plugins/virsh/vars: 6
plugins/virsh/vars/topology/network: 1
plugins/virsh/vars/topology/nodes: 1
releasenotes/notes: 4
tests: 10
tests/example: 3
tests/example/files: 2
tests/example/plugins: 1
tests/example/plugins/add_remove_all_plugins/install_plugin1: 1
tests/example/plugins/add_remove_all_plugins/install_plugin2: 1
tests/example/plugins/add_remove_all_plugins/provision_plugin1: 1
tests/example/plugins/add_remove_all_plugins/provision_plugin2: 1
tests/example/plugins/add_remove_all_plugins/test_plugin1: 1
tests/example/plugins/add_remove_all_plugins/test_plugin2: 1
tests/example/plugins/git_plugin: 1
tests/example/plugins/help_screen_plugin_with_list_yamls: 1
tests/example/plugins/help_screen_plugin_with_list_yamls/defaults/topology/networks: 2
tests/example/plugins/help_screen_plugin_with_list_yamls/vars/topology: 2
tests/example/plugins/help_screen_plugin_with_list_yamls/vars/topology/networks: 2
tests/example/plugins/plugin_with_entry_point: 1
tests/example/plugins/plugin_with_requirements: 1
tests/example/plugins/plugin_with_role_path/infrared/plugin: 2
tests/example/plugins/plugin_with_src_path: 1
tests/example/plugins/plugin_with_src_path/infrared_plugin: 1
tests/example/plugins/plugin_with_unsupported_option_type_in_spec: 1
tests/example/plugins/plugin_without_spec: 1
tests/example/plugins/type1_plugin1: 1
tests/example/plugins/type1_plugin2: 1
tests/example/plugins/type2_plugin1: 1
tests/example/plugins/unsupported_plugin: 1
tests/example/post_tasks: 3
tests/example/roles/example_role/tasks: 1
tests/example/vars: 1
tests/files/utils/dicts: 3
```

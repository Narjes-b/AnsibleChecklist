# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-005

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `plugins/virsh/defaults/topology/network/4_nets.yml` (reported anchor line 61)
- Flagged construct: variable `net`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–100 of 100:

```text
    1 | ---
    2 | networks:
    3 |     net1:
    4 |         external_connectivity: no
    5 |         name: "ctlplane"
    6 |         ip_address: "192.168.{{ data_net }}.254"
    7 |         netmask: "255.255.255.0"
    8 |     net2:
    9 |         external_connectivity: yes
   10 |         name: "management"
   11 |         ip_address: "172.16.{{ net }}.1"
   12 |         netmask: "255.255.255.0"
   13 |         forward: nat
   14 |         dhcp:
   15 |             range:
   16 |                 start: "172.16.{{ net }}.2"
   17 |                 end: "172.16.{{ net }}.100"
   18 |             subnet_cidr: "172.16.{{ net }}.0/24"
   19 |             subnet_gateway: "172.16.{{ net }}.1"
   20 |         floating_ip:
   21 |             start: "172.16.{{ net }}.101"
   22 |             end: "172.16.{{ net }}.150"
   23 |     net3:
   24 |         external_connectivity: yes
   25 |         name: "external"
   26 |         ipv6:
   27 |             ip_address: "2620:52:0:13b8::fe"
   28 |             prefix: "64"
   29 |             dhcp:
   30 |                 range:
   31 |                     start: "2620:52:0:13b8::fe:1"
   32 |                     end: "2620:52:0:13b8::fe:ff"
   33 |         ip_address: "10.0.{{ net }}.1"
   34 |         netmask: "255.255.255.0"
   35 |         forward: nat
   36 |         dhcp:
   37 |             range:
   38 |                 start: "10.0.{{ net }}.2"
   39 |                 end: "10.0.{{ net }}.100"
   40 |             subnet_cidr: "10.0.{{ net }}.0/24"
   41 |             subnet_gateway: "10.0.{{ net }}.1"
   42 |         floating_ip:
   43 |             start: "10.0.{{ net }}.101"
   44 |             end: "10.0.{{ net }}.150"
   45 |     net4:
   46 |         external_connectivity: yes
   47 |         name: "tenant"
   48 |         ipv6:
   49 |             ip_address: "2620:52:0:13b9::fe"
   50 |             prefix: "64"
   51 |             dhcp:
   52 |                 range:
   53 |                     start: "2620:52:0:13b9::fe:1"
   54 |                     end: "2620:52:0:13b9::fe:ff"
   55 |         ip_address: "10.0.{{ net + 1 | string }}.1"
   56 |         netmask: "255.255.255.0"
   57 |         forward: nat
   58 |         dhcp:
   59 |             range:
   60 |                 start: "10.0.{{ net + 1 | string }}.2"
   61 |                 end: "10.0.{{ net + 1 | string }}.100"
   62 |             subnet_cidr: "10.0.{{ net + 1 | string }}.0/24"
   63 |             subnet_gateway: "10.0.{{ net + 1 | string }}.1"
   64 |         floating_ip:
   65 |             start: "10.0.{{ net + 1 | string }}.101"
   66 |             end: "10.0.{{ net + 1 | string }}.150"
   67 | 
   68 | 
   69 | nodes:
   70 |     default:
   71 |         interfaces:
   72 |             - network: "ctlplane"
   73 |             - network: "management"
   74 |             - network: "external"
   75 |             - network: "tenant"
   76 |         external_network:
   77 |             network: "management"
   78 |     novacontrol:
   79 |         interfaces:
   80 |             - network: "ctlplane"
   81 |             - network: "management"
   82 |         external_network:
   83 |             network: "management"
   84 |     odl:
   85 |         interfaces:
   86 |             - network: "management"
   87 |         external_network:
   88 |             network: "management"
   89 |     cfme:
   90 |         interfaces:
   91 |             - network: "external"
   92 |             - network: "ctlplane"
   93 |         external_network:
   94 |             network: "external"
   95 |     cfme_tester:
   96 |         interfaces:
   97 |             - network: "external"
   98 |             - network: "ctlplane"
   99 |         external_network:
  100 |             network: "external"
```

## Visible variable references

```text
Whole-word search for `net`: 345 matches in 121 files; 20 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv4.yml:17:            net: 172.17.1.0/24
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv4.yml:21:            net: 10.0.0.0/24
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv4.yml:25:            net: 172.17.3.0/24
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv4.yml:29:            net: 172.17.4.0/24
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv4.yml:37:            net: 172.17.2.0/24
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv6.yml:17:            net: fd00:fd00:fd00:2000::/64
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv6.yml:21:            net: 2620:52:0:13b8::/64
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv6.yml:25:            net: fd00:fd00:fd00:3000::/64
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv6.yml:29:            net: fd00:fd00:fd00:4000::/64
plugins/tripleo-overcloud/vars/loadbalancer/external-ipv6.yml:37:            net: 172.17.2.0/24
plugins/virsh/defaults/topology/network/bgp_networks.yml:6:    net: 10.0.0.0
plugins/virsh/defaults/topology/network/bgp_networks.yml:11:    net: 10.1.0.0
plugins/virsh/defaults/topology/network/bgp_networks.yml:14:    net: 10.2.0.0
plugins/virsh/defaults/topology/network/bgp_networks.yml:17:    net: 192.168.14.0
plugins/virsh/defaults/topology/network/bgp_networks_ipv6.yml:6:    net: 10.0.0.0
plugins/virsh/defaults/topology/network/bgp_networks_ipv6.yml:15:    net: 10.1.0.0
plugins/virsh/defaults/topology/network/bgp_networks_ipv6.yml:20:    net: 10.2.0.0
plugins/virsh/defaults/topology/network/bgp_networks_ipv6.yml:25:    net: 192.168.14.0/24
plugins/virsh/provision_networks.yml:30:          net: "{{ ansible_local.run[prefix].net if prefix is defined else 0 }}"
plugins/virsh/tasks/load_topology.yml:21:      net: "{{ ansible_local.run[prefix].net if prefix is defined else 10 }}"

Other references:
infrared/common/roles/rdo-release/defaults/main.yml:48:                - os-net-config
infrared/common/roles/rdo-release/defaults/main.yml:82:                 - os-net-config
infrared/common/roles/tls-everywhere/tasks/prepare_freeipa.yml:20:        - 'net-tools'
infrared/common/roles/tls-everywhere/tasks/prepare_freeipa.yml:31:        - 'net-tools'
plugins/openstack/post.yml:37:        command: find /sys/class/net -type l -not -lname '*virtual*' -printf '%f\n'
plugins/openstack/roles/bmc/tasks/main.yml:116:- name: Ensure /etc/os-net-config directory exists
plugins/openstack/roles/bmc/tasks/main.yml:118:      path: "/etc/os-net-config"
plugins/openstack/roles/bmc/tasks/main.yml:121:- name: Deploy os-net-config configuration
plugins/openstack/roles/bmc/tasks/main.yml:123:      src: "os-net-config.j2"
plugins/openstack/roles/bmc/tasks/main.yml:124:      dest: "/etc/os-net-config/config.yaml"
plugins/openstack/roles/bmc/vars/main.yml:3:  - os-net-config
plugins/openstack/tasks/servers.yml:17:  command: "echo net-name={{ provision.prefix }}{{ topology_node.interfaces[item].network }}"
plugins/packstack/create_external_network.yml:109:            name: net.ipv4.conf.eth0.rp_filter
plugins/rally/vars/image/cirros.yml:3:    url: 'https://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img'
plugins/tripleo-overcloud/deploy.yml:52:# net/vip provisioning stpes moved to earlier stages in order to use VIP and other address
plugins/tripleo-overcloud/ovb.yml:28:        command: "cat /sys/class/net/{{ ipmi_interface }}/mtu"
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:27:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8777 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:34:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8776 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:42:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.storage.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:9292 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:48:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:9292 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:56:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:9293 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:63:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:9191 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:82:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8004 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:89:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8000 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:96:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8003 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:105:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:80 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:112:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:35357 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:118:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:22 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:125:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:5000 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:137:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:3306 backup check fall 5 inter 2000 on-marked-down shutdown-sessions port 9200 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:144:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:9696 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:151:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8773 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:157:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8775 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:165:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:6080 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:172:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8774 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:178:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:6641 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:184:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:6642 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:200:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:6379 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:207:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.storage.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8080 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:215:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8042 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:222:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8041 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:229:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8386 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:241:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8778 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2:253:server {{ loadbalancer.controllers.name_prefix }}{{x}} {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}:8778 check fall 5 inter 2000 rise 2
plugins/tripleo-overcloud/tasks/opstools/main.yml:2:  shell: virsh net-dhcp-leases external | awk '/{{ groups["opstools"][0] }}/ {print $5};' | sed 's/\/[0-9]*//'
plugins/tripleo-overcloud/templates/compute-dvr.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/templates/compute-dvr.yaml.j2:173:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/templates/loadbalancer/external-lb.yaml.j2:106:    - {{ loadbalancer.network.external.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/templates/loadbalancer/external-lb.yaml.j2:110:    - {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/templates/loadbalancer/external-lb.yaml.j2:114:    - {{ loadbalancer.network.storage.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/templates/loadbalancer/external-lb.yaml.j2:118:    - {{ loadbalancer.network.storage_mgmnt.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/templates/loadbalancer/external-lb.yaml.j2:122:    - {{ loadbalancer.network.tenant.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/templates/nodes_software_config.yaml.j2:12:{# include net-configs templates #}
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ceph-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ceph-storage.yaml.j2:207:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/cinder-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/cinder-storage.yaml.j2:185:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/compute.yaml.j2:200:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/controller-v6.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/controller-v6.yaml.j2:215:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/controller.yaml.j2:208:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/database.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/database.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/database_internal.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/database_internal.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/heat.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/heat.yaml.j2:174:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ironic.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/ironic.yaml.j2:174:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/ceph-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/cinder-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/controller-v6.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/database.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/database_internal.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/heat.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/ironic.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/messaging.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/messaging_internal.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/monitor.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/networker.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/novacontrol.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/opstools.yml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/osdcompute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/radosgw.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/serviceapi.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/legacy/swift-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/messaging.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/messaging.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/messaging_internal.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/messaging_internal.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/monitor.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/monitor.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/networker.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/networker.yaml.j2:200:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/novacontrol.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/novacontrol.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/opstools.yml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/opstools.yml.j2:134:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/osdcompute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/osdcompute.yaml.j2:177:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/radosgw.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/radosgw.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/serviceapi.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/serviceapi.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/swift-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/swift-storage.yaml.j2:186:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/telemetry.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/composable_roles/network/nic-configs/telemetry.yaml.j2:173:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt/network/baremetal_deployment.yaml.j2:44:      fixed_ip: {{ loadbalancer.network.external.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/vars/deployment/files/virt/network/baremetal_deployment.yaml.j2:47:      fixed_ip: {{ loadbalancer.network.internal_api.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/vars/deployment/files/virt/network/baremetal_deployment.yaml.j2:50:      fixed_ip: {{ loadbalancer.network.storage.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/vars/deployment/files/virt/network/baremetal_deployment.yaml.j2:53:      fixed_ip: {{ loadbalancer.network.storage_mgmnt.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/vars/deployment/files/virt/network/baremetal_deployment.yaml.j2:56:      fixed_ip: {{ loadbalancer.network.tenant.net | ipaddr('net') | ipaddr(loadbalancer.controllers.pool_start + x) | ipaddr('address') }}
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/ceph-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/ceph-storage.yaml.j2:185:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/cinder-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/cinder-storage.yaml.j2:185:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/compute.yaml.j2:179:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller-v6.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller-v6.yaml.j2:197:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/controller.yaml.j2:191:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/ceph-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/cinder-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/controller-v6.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/legacy/swift-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/swift-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt/network/three-nics-vlans/swift-storage.yaml.j2:185:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/three-nics-vlans/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/three-nics-vlans/compute.yaml.j2:173:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/three-nics-vlans/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_4nets_multi_hypervisor/network/three-nics-vlans/controller.yaml.j2:185:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/compute.yaml.j2:173:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/controller.yaml.j2:185:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/legacy/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_4nics/network/four-nics-vlans/legacy/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/ceph-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/ceph-storage.yaml.j2:133:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/cinder-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/cinder-storage.yaml.j2:134:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/compute.yaml.j2:133:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/controller-v6.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/controller-v6.yaml.j2:133:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/controller.yaml.j2:133:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/ceph-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/cinder-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/controller-v6.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/legacy/swift-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/swift-storage.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_5nics/network/five-nics-vlans/swift-storage.yaml.j2:133:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/four-nics-vlans/compute.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/four-nics-vlans/compute.yaml.j2:200:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/four-nics-vlans/controller.yaml.j2:4:  Software Config to drive os-net-config to configure multiple interfaces
plugins/tripleo-overcloud/vars/deployment/files/virt_vswitch/network/four-nics-vlans/controller.yaml.j2:185:                  get_file: {{ install.heat.templates.basedir }}/network/scripts/run-os-net-config.sh
plugins/tripleo-overcloud/vars/public/subnet/default_subnet.yml:5:    # Gateway for ext.net may differ from ExternalInterfaceDefaultRoute.
plugins/tripleo-overcloud/vars/public/subnet/default_subnet.yml:7:    # it explicitly also here for ext. net. purpose.
plugins/tripleo-standalone/templates/standalone_parameters.yaml.j2:27:  # re-use ctlplane bridge for public net
plugins/tripleo-standalone/templates/standalone_parameters.yaml.j2:30:  # enable to force metadata for public net
plugins/tripleo-undercloud/post.yml:38:        SUBNET="$( neutron net-show ctlplane -c subnets | awk '/subnets/ {print $4}' )"
plugins/tripleo-undercloud/restore.yml:82:                --operations dhcp-client-state,dhcp-server-state,net-hostname,net-hwaddr,udev-persistent-net,ssh-hostkeys
plugins/tripleo-undercloud/restore.yml:135:            virsh net-dhcp-leases external | grep {{ mac_ext.stdout }} | awk '($4 == "ipv4") && ($6 =="{{ undercloud_node.name }}") {print $5}'
plugins/tripleo-undercloud/restore_containerized.yml:84:                --operations dhcp-client-state,dhcp-server-state,net-hostname,net-hwaddr,udev-persistent-net,ssh-hostkeys
plugins/tripleo-undercloud/restore_containerized.yml:138:            virsh net-dhcp-leases {{ install.snapshot.access.network }} | grep {{ mac_access.stdout }} | awk '($4 == "ipv4") && ($6 =="{{ undercloud_node.name }}") {print $5}'
plugins/tripleo-undercloud/tasks/images/repos.yml:228:  command: "virt-customize -a {{ overcloud_image_file }} --selinux-relabel --delete /usr/libexec/os-apply-config/templates/etc/os-net-config/config.json"
plugins/virsh/defaults/topology/network/3_net_openvswitch.yml:33:      ip_address: "172.16.{{ net }}.1"
plugins/virsh/defaults/topology/network/3_net_openvswitch.yml:38:          start: "172.16.{{ net }}.2"
plugins/virsh/defaults/topology/network/3_net_openvswitch.yml:39:          end: "172.16.{{ net }}.100"
[145 further matches not shown; files: plugins/tripleo-overcloud/roles/loadbalancer/templates/haproxy.cfg.j2=28, plugins/virsh/defaults/topology/network/4_nets.yml=21, plugins/virsh/defaults/topology/network/3_nets.yml=14, plugins/virsh/defaults/topology/network/3_nets_ipv4.yml=14, plugins/virsh/defaults/topology/network/3_nets_vswitch.yml=14, plugins/virsh/defaults/topology/network/4_nets_baremetal.yml=14, plugins/virsh/defaults/topology/network/3_nets_tiny_ext_pool.yml=12, plugins/virsh/defaults/topology/network/3_nets_tiny_ext_pool2.yml=12, plugins/virsh/defaults/topology/network/3_net_openvswitch.yml=7, plugins/virsh/defaults/topology/network/3_nets_4_leafs_openvswitch.yml=7]
```

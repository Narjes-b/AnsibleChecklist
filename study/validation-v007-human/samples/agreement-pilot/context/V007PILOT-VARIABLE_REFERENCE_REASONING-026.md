# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-026

- Repository: `bluebanquise/bluebanquise`
- Commit: `fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `collections/infrastructure/roles/nic/tasks/nmcli.yml` (reported anchor line 7)
- Object: `variable` `6b458983da4495c7c80d945c9a5e17ea0460e7545012c80d8f44b5e77c81a9e3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–134 of 134:

```text
    1 | ---
    2 | 
    3 | - name: block <|> Force connection name to be the same as device name
    4 |   when: nic_nmcli_device_is_connection_name
    5 |   block:
    6 | 
    7 |     - name: command <|> Gather devices device and name
    8 |       ansible.builtin.command: nmcli --terse -f device,name,type con show  # Gather devices and related name in a parsable way
    9 |       register: nic_nmcli_con_show
   10 |       changed_when: False
   11 | 
   12 |     - name: command <|> Rename interfaces if needed
   13 |       ansible.builtin.command: "nmcli connection modify '{{ item.name }}' connection.id '{{ item.device }}'"
   14 |       loop: "{{ nic_j2_nmcli_device_name_type | flatten(levels=1) }}"
   15 |       register: nic_nmcli_result
   16 |       when:
   17 |         - item.apply
   18 |         - item.type in ['802-3-ethernet', 'ethernet']
   19 |         - item.name != item.device
   20 |       changed_when: nic_nmcli_result.rc == 0
   21 | 
   22 | - name: nmcli <|> Set NICs configuration # noqa args[module]
   23 |   retries: 3
   24 |   delay: 5
   25 |   community.general.nmcli:
   26 |     # Tuned
   27 |     conn_name: "{{ item.conn_name | default(item.interface) | string }}"
   28 |     ifname: "{{ item.ifname | default(item.physical_device) | default(omit) }}"
   29 |     ip4: "{{ nic_j2_ip4 | trim | default(omit,true) }}"
   30 |     gw4: "{{ nic_j2_gw4 | trim | default(omit,true) }}"
   31 |     routes4: "{{ nic_j2_routes4 | trim | default(omit,true) }}"
   32 |     route_metric4: "{{ nic_j2_route_metric4 | trim | default(omit,true) }}"
   33 |     never_default4: "{{ nic_j2_never_default4 | trim | default(omit,true) }}"
   34 |     dns4: "{{ nic_j2_dns4 | trim | default(omit,true) }}"
   35 |     dns4_search: "{{ nic_j2_dns4_search | trim | default(omit,true) }}"
   36 |     ip6: "{{ nic_j2_ip6 | trim | default(omit,true) }}"
   37 |     gw6: "{{ nic_j2_gw6 | trim | default(omit,true) }}"
   38 |     mtu: "{{ nic_j2_mtu | trim | default(omit,true) }}"
   39 |     type: "{{ item.type | default('ethernet') }}"  # Even if in the documentation type is optional, it is in fact mandatory. Default to ethernet.
   40 |     # Standard
   41 |     state: "{{ item.state | default('present') }}"
   42 |     autoconnect: "{{ item.autoconnect | default(omit) }}"
   43 |     ageingtime: "{{ item.ageingtime | default(omit) }}"
   44 |     arp_interval: "{{ item.arp_interval | default(omit) }}"
   45 |     arp_ip_target: "{{ item.arp_ip_target | default(omit) }}"
   46 |     dhcp_client_id: "{{ item.dhcp_client_id | default(omit) }}"
   47 |     dns6: "{{ item.dns6 | default(omit) }}"
   48 |     dns6_search: "{{ item.dns6_search | default(omit) }}"
   49 |     downdelay: "{{ item.downdelay | default(omit) }}"
   50 |     egress: "{{ item.egress | default(omit) }}"
   51 |     flags: "{{ item.flags | default(omit) }}"
   52 |     forwarddelay: "{{ item.forwarddelay | default(omit) }}"
   53 |     hairpin: "{{ item.hairpin | default(omit) }}"
   54 |     hellotime: "{{ item.hellotime | default(omit) }}"
   55 |     ingress: "{{ item.ingress | default(omit) }}"
   56 |     ip_tunnel_dev: "{{ item.ip_tunnel_dev | default(omit) }}"
   57 |     ip_tunnel_local: "{{ item.ip_tunnel_local | default(omit) }}"
   58 |     ip_tunnel_remote: "{{ item.ip_tunnel_remote | default(omit) }}"
   59 |     mac: "{{ item.force_mac | default(omit) }}"
   60 |     master: "{{ item.master | default(omit) }}"
   61 |     maxage: "{{ item.maxage | default(omit) }}"
   62 |     mode: "{{ item.mode | default(omit) }}"
   63 |     miimon: "{{ item.miimon | default(omit) }}"
   64 |     path_cost: "{{ item.path_cost | default(omit) }}"
   65 |     primary: "{{ item.primary | default(omit) }}"
   66 |     priority: "{{ item.priority | default(omit) }}"
   67 |     slavepriority: "{{ item.slavepriority | default(omit) }}"
   68 |     stp: "{{ item.stp | default(omit) }}"
   69 |     updelay: "{{ item.updelay | default(omit) }}"
   70 |     vlandev: "{{ item.vlandev | default(omit) }}"
   71 |     vlanid: "{{ item.vlanid | default(omit) }}"
   72 |     vxlan_id: "{{ item.vxlan_id | default(omit) }}"
   73 |     vxlan_local: "{{ item.vxlan_local | default(omit) }}"
   74 |     vxlan_remote: "{{ item.vxlan_remote | default(omit) }}"
   75 |     zone: "{{ item.zone | default(omit) }}"
   76 |     method4: "{{ item.method4 | default(omit) }}"
   77 |     method6: "{{ item.method6 | default(omit) }}"
   78 |     addr_gen_mode6: "{{ item.addr_gen_mode6 | default(omit) }}"
   79 |     dns4_ignore_auto: "{{ item.dns4_ignore_auto | default(omit) }}"
   80 |     dns6_ignore_auto: "{{ item.dns6_ignore_auto | default(omit) }}"
   81 |     gsm: "{{ item.gsm | default(omit) }}"
   82 |     gw4_ignore_auto: "{{ item.gw4_ignore_auto | default(omit) }}"
   83 |     gw6_ignore_auto: "{{ item.gw6_ignore_auto | default(omit) }}"
   84 |     ignore_unsupported_suboptions: "{{ item.ignore_unsupported_suboptions | default(omit) }}"
   85 |     ip_privacy6: "{{ item.ip_privacy6 | default(omit) }}"
   86 |     ip_tunnel_input_key: "{{ item.ip_tunnel_input_key | default(omit) }}"
   87 |     ip_tunnel_output_key: "{{ item.ip_tunnel_output_key | default(omit) }}"
   88 |     may_fail4: "{{ item.may_fail4 | default(omit) }}"
   89 |     route_metric6: "{{ item.route_metric6 | default(omit) }}"
   90 |     routes4_extended: "{{ item.routes4_extended | default(omit) }}"
   91 |     routes6: "{{ item.routes6 | default(omit) }}"
   92 |     routes6_extended: "{{ item.routes6_extended | default(omit) }}"
   93 |     routing_rules4: "{{ item.routing_rules4 | default(omit) }}"
   94 |     runner: "{{ item.runner | default(omit) }}"
   95 |     runner_fast_rate: "{{ item.runner_fast_rate | default(omit) }}"
   96 |     runner_hwaddr_policy: "{{ item.runner_hwaddr_policy | default(omit) }}"
   97 |     ssid: "{{ item.ssid | default(omit) }}"
   98 |     transport_mode: "{{ item.transport_mode | default(omit) }}"
   99 |     infiniband_mac: "{{ item.infiniband_mac | default(omit) }}"
  100 |     vpn: "{{ item.vpn | default(omit) }}"
  101 |     wifi: "{{ item.wifi | default(omit) }}"
  102 |     wifi_sec: "{{ item.wifi_sec | default(omit) }}"
  103 |     wireguard: "{{ item.wireguard | default(omit) }}"
  104 |     xmit_hash_policy: "{{ item.xmit_hash_policy | default(omit) }}"
  105 |     slave_type: "{{ item.slave_type | default(omit) }}"
  106 |   notify:
  107 |     - command <|> Reload connections
  108 |     - service <|> Restart nic services
  109 |   loop: "{{ network_interfaces }}"
  110 |   register: nic_apply
  111 |   when: item.skip is not defined or (item.skip is defined and not item.skip)
  112 |   tags:
  113 |     - identify
  114 | 
  115 | - name: meta <|> Run handler tasks to reload connections
  116 |   ansible.builtin.meta: flush_handlers
  117 | 
  118 | - name: shell <|> Force apply nic settings
  119 |   ansible.builtin.shell: "nmcli con down {{ item.item.interface }} && sleep {{ nic_restart_timeout }} && nmcli con up {{ item.item.interface }}"
  120 |   loop: "{{ nic_apply.results }}"
  121 |   when:  # noqa no-handler
  122 |     - nic_force_nic_restart
  123 |     - item.changed
  124 | 
  125 | - name: reboot <|> Reboot system to ensure apply nic configuration
  126 |   ansible.builtin.reboot:
  127 |     reboot_timeout: "{{ nic_reboot_timeout }}"
  128 |   register: nic_reboot_status
  129 |   loop: "{{ nic_apply.results }}"
  130 |   when:  # noqa no-handler
  131 |     - nic_force_reboot
  132 |     - item.changed
  133 |     - not (nic_reboot_status.changed | d(false))
  134 |     - nic_allow_reboot | bool
```

## Visible variable references

```text
fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0:collections/infrastructure/roles/nic/tasks/nmcli.yml:9:      register: nic_nmcli_con_show
fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0:collections/infrastructure/roles/nic/vars/main.yml:5:{%- for device in (nic_nmcli_con_show.stdout | split('\n')) -%}
```

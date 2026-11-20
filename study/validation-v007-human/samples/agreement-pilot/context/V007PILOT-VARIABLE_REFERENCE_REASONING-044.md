# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-044

- Repository: `cradle8810/ansible_hayaworld`
- Commit: `d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/common/tasks/main.yml` (reported anchor line 14)
- Object: `variable` `65aa95a6905b32edf837d29639a546396b66cd35b83023029e15e15cf1bc4a68`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–139 of 139:

```text
    1 | ---
    2 | - name: "Common / Set user facts"
    3 |   ansible.builtin.import_tasks:
    4 |     file: tasks/set-users-facts.yml
    5 | 
    6 | - name: "Common / Networking"
    7 |   when:
    8 |     ansible_facts.virtualization_type != 'lxc'
    9 |   tags:
   10 |     - network
   11 |   block:
   12 |     - name: "Common / Set Hostname"
   13 |       ansible.builtin.hostname:
   14 |         name: "{{ common_hostinfo.hostname }}"
   15 | 
   16 |     - name: "Common / Setting Network"
   17 |       ansible.builtin.import_tasks:
   18 |         file: tasks/netplan.yml
   19 | 
   20 |     - name: "Common / Add own hostname record to hosts(5)"
   21 |       ansible.builtin.import_tasks:
   22 |         file: tasks/hostname_etc_hosts.yml
   23 | 
   24 |     - name: "Common / Scale up for nf_conntrack_max"
   25 |       ansible.builtin.import_tasks:
   26 |         file: tasks/increase-nf_conntrack_max.yml
   27 | 
   28 | - name: "Common / Stop Systemd-resolved"
   29 |   ansible.builtin.import_tasks:
   30 |     file: tasks/stop-systemd-resolved.yml
   31 | 
   32 | - name: "Common / Locale Settings"
   33 |   block:
   34 |     - name: "Common / Set timezone to Asia/Tokyo"
   35 |       community.general.timezone:
   36 |         name: Asia/Tokyo
   37 | 
   38 |     - name: "Common / Install locale en_US"
   39 |       ansible.builtin.apt:
   40 |         name: "{{ item }}"
   41 |         state: present
   42 |         update_cache: true
   43 |         cache_valid_time: "{{ common_apt.cache_valid_time }}"
   44 |       loop:
   45 |         - locales-all
   46 |         - language-pack-en
   47 |       when: common_install_langs
   48 | 
   49 |     - name: "Common / Set locale as en_US.UTF-8"
   50 |       community.general.locale_gen:
   51 |         name: "en_US.UTF-8"
   52 |         state: present
   53 | 
   54 | - name: "Common / NTP Settings"
   55 |   ansible.builtin.import_role:
   56 |     name: geerlingguy.ntp
   57 |   vars:
   58 |     ntp_package: chrony
   59 |     ntp_config_file: /etc/chrony/chrony.conf
   60 |     ntp_cron_daemon: chrony
   61 |     ntp_daemon: chrony
   62 |     ntp_enabled: true
   63 |     ntp_timezone: "Asia/Tokyo"
   64 |     ntp_servers: "{{ common_ntp.ntp_servers }}"
   65 |     ntp_tinker_panic: true
   66 |     ntp_manage_config: true
   67 |   tags:
   68 |     - ntp
   69 | 
   70 | - name: "Common / Set Firewall"
   71 |   ansible.builtin.import_tasks:
   72 |     file: tasks/firewall.yml
   73 |   tags:
   74 |     - firewall
   75 | 
   76 | - name: "Common / Apt install"
   77 |   ansible.builtin.import_tasks:
   78 |     file: tasks/apt.yml
   79 | 
   80 | - name: "Common / QEMU VM Setting"
   81 |   ansible.builtin.apt:
   82 |     name: qemu-guest-agent
   83 |     state: present
   84 |     update_cache: true
   85 |     cache_valid_time: "{{ common_apt.cache_valid_time }}"
   86 |   when:
   87 |     - ansible_facts.virtualization_type == 'kvm'
   88 |     - ansible_virtualization_role == 'guest'
   89 |   notify: "Restart qemu-guest-agent"
   90 | 
   91 | - name: "Common / Users Settings"
   92 |   when: common_install_users
   93 |   tags:
   94 |     - users
   95 |   block:
   96 |     - name: "Common / Usermod"
   97 |       ansible.builtin.import_tasks:
   98 |         file: tasks/usermod.yml
   99 |       tags:
  100 |         - users
  101 | 
  102 |     - name: "Common / Put authorized Key for hayato"
  103 |       ansible.builtin.import_tasks:
  104 |         file: tasks/authorized_keys.yml
  105 |       tags:
  106 |         - users
  107 | 
  108 |     - name: "Common / Increase User file descriptors"
  109 |       ansible.builtin.import_tasks:
  110 |         file: tasks/increase-fd.yml
  111 |       tags:
  112 |         - users
  113 | 
  114 | - name: "Common / Hayaworld Root CA install"
  115 |   ansible.builtin.import_tasks:
  116 |     file: tasks/hayaworld_rootCA.yml
  117 |   tags:
  118 |     - ca
  119 | 
  120 | - name: "Common / Stop Unused services (Common)"
  121 |   ansible.builtin.import_tasks:
  122 |     file: tasks/stop-services.yml
  123 |   tags:
  124 |     - stop_services
  125 | 
  126 | - name: "Common / Configure Restart When Kernel Panic happened"
  127 |   when:
  128 |     ansible_facts.virtualization_type != 'lxc'
  129 |   ansible.builtin.import_tasks:
  130 |     file: tasks/restart_when_panic.yml
  131 |   tags:
  132 |     - panic
  133 | 
  134 | - name: "Common / Install Cron"
  135 |   ansible.builtin.apt:
  136 |     name: cron
  137 |     state: present
  138 |     update_cache: true
  139 |     cache_valid_time: "{{ common_apt.cache_valid_time }}"
```

## Visible variable references

```text
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:dns.yml:170:            scrutiny_collector_server_id: "{{ common_hostinfo.shortname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:dns.yml:186:            ipaddr: "{{ common_hostinfo.ipv4 }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:iso.yml:62:            hostname: "{{ common_hostinfo.hostname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:log.yml:49:        graylog_hostname: "{{ common_hostinfo.shortname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:proxmox.yml:18:        common_hostinfo: "{{ network | selectattr('ipv4', 'eq', mgmt_ipv4) | first }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:proxmox.yml:28:        proxmox_macaddr: "{{ common_hostinfo.macaddress }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:proxmox.yml:58:        scrutiny_collector_server_id: "{{ common_hostinfo.shortname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/defaults/main.yml:7:common_network_interface: "{{ common_hostinfo.interface }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/defaults/main.yml:8:common_network_ipv4: "{{ common_hostinfo.ipv4 }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/defaults/main.yml:12:common_network_mtu: "{{ common_hostinfo.mtu }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:3:  when: common_hostinfo.self_org is true
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:32:  when: common_hostinfo.self_org is false
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:36:        path: "/home/{{ common_hostinfo.sshuser }}/.ssh/"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:38:        owner: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:39:        group: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:47:        dest: "/home/{{ common_hostinfo.sshuser }}/.ssh/authorized_keys"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:48:        owner: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/authorized_keys.yml:49:        group: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/hostname_etc_hosts.yml:10:    h: "{{ common_hostinfo }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/main.yml:14:        name: "{{ common_hostinfo.hostname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/set-users-facts.yml:4:    common_hostinfo: "{{ network | selectattr('ipv4', 'eq', common_mgmt_ipv4) | first }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/common/tasks/usermod.yml:15:    - common_hostinfo.self_org is true
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/pihole/templates/root/pihole/docker-compose.yml.j2:3:    hostname: "{{ common_hostinfo.shortname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/proxmox/defaults/main.yml:17:# Use common_hostinfo.macaddress
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/proxmox/tasks/main.yml:5:  when: common_hostinfo.shortname in proxmox_xe_nodes
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/tailscale_install/tasks/main.yml:55:        msg: "{{ tailscale_nodename_retval }}, {{ common_hostinfo.shortname }}.{{ tailscale_domain }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/tailscale_install/tasks/main.yml:60:          tailscale set --hostname "{{ common_hostinfo.shortname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:roles/tailscale_install/tasks/main.yml:64:        - tailscale_nodename_retval.stdout != (common_hostinfo.shortname ~ "." ~ tailscale_domain)
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:skylark.yml:19:        common_hostinfo: "{{ network | selectattr('ipv4', 'eq', mgmt_ipv4) | first }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:skylark.yml:29:        scrutiny_collector_server_id: "{{ common_hostinfo.shortname }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:3:  when: common_hostinfo.self_org is true
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:32:  when: common_hostinfo.self_org is false
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:36:        path: "/home/{{ common_hostinfo.sshuser }}/.ssh/"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:38:        owner: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:39:        group: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:47:        dest: "/home/{{ common_hostinfo.sshuser }}/.ssh/authorized_keys"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:48:        owner: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/authorized_keys.yml:49:        group: "{{ common_hostinfo.sshuser }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/all/set-users-facts.yml:4:    common_hostinfo: "{{ network | selectattr('ipv4', 'eq', mgmt_ipv4) | first }}"
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/zabbix-agent2.yml:5:  when: common_hostinfo.proxmox is undefined
d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597:tasks/zabbix-agent2.yml:30:      value: "{{ common_hostinfo.shortname }}.hayaworld.home"
```

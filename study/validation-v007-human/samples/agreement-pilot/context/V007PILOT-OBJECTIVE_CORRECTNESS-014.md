# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-014

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: Objective correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `onecloud/roles/k3s/prereq/tasks/main.yml` (reported anchor line 9)
- Object: `task` `0a33d474fc084b45fe35f7ca404b9a1dfbcf338ab2f93b9bc37124a02e7a467e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–200 of 200:

```text
    1 | ---
    2 | - name: Install Dependent Ubuntu Packages
    3 |   when: ansible_distribution in ['Ubuntu']
    4 |   ansible.builtin.apt:
    5 |     name: policycoreutils  # Used by install script to restore SELinux context
    6 |     update_cache: true
    7 | 
    8 | - name: Enable IPv4 forwarding
    9 |   sysctl:
   10 |     name: net.ipv4.ip_forward
   11 |     value: "1"
   12 |     state: present
   13 |     reload: true
   14 | 
   15 | - name: Enable IPv6 forwarding
   16 |   sysctl:
   17 |     name: net.ipv6.conf.all.forwarding
   18 |     value: "1"
   19 |     state: present
   20 |     reload: true
   21 |   when: ip_type is defined and ip_type == 'ipv6' or ansible_all_ipv6_addresses
   22 | 
   23 | - name: Populate service facts
   24 |   ansible.builtin.service_facts:
   25 | 
   26 | # - name: Allow UFW Exceptions
   27 | #   when:
   28 | #     - ansible_facts.services['ufw'] is defined
   29 | #     - ansible_facts.services['ufw'].state == 'running'
   30 | #   block:
   31 | #     - name: Get ufw status
   32 | #       ansible.builtin.command:
   33 | #         cmd: ufw status
   34 | #       changed_when: false
   35 | #       register: ufw_status
   36 | #
   37 | #     - name: If ufw enabled, open api port
   38 | #       when:
   39 | #         - ufw_status['stdout'] == "Status':' active"
   40 | #       community.general.ufw:
   41 | #         rule: allow
   42 | #         port: "{{ api_port }}"
   43 | #         proto: tcp
   44 | #
   45 | #     - name: If ufw enabled, open etcd ports
   46 | #       when:
   47 | #         - ufw_status['stdout'] == "Status':' active"
   48 | #         - groups['server'] | length > 1
   49 | #       community.general.ufw:
   50 | #         rule: allow
   51 | #         port: "2379:2381"
   52 | #         proto: tcp
   53 | #
   54 | #     - name: If ufw enabled, allow default CIDRs
   55 | #       when:
   56 | #         - ufw_status['stdout'] == "Status':' active"
   57 | #       community.general.ufw:
   58 | #         rule: allow
   59 | #         src: '{{ item }}'
   60 | #       loop:
   61 | #         - 10.42.0.0/16  # Pods
   62 | #         - 10.43.0.0/16  # Services
   63 | 
   64 | # - name: Allow Firewalld Exceptions
   65 | #   when:
   66 | #     - ansible_facts.services['firewalld.service'] is defined
   67 | #     - ansible_facts.services['firewalld.service'].state == 'running'
   68 | #   block:
   69 | #     - name: If firewalld enabled, open api port
   70 | #       ansible.posix.firewalld:
   71 | #         port: "{{ api_port }}/tcp"
   72 | #         zone: trusted
   73 | #         state: enabled
   74 | #         permanent: true
   75 | #         immediate: true
   76 | #
   77 | #     - name: If firewalld enabled, open etcd ports
   78 | #       when: groups['server'] | length > 1
   79 | #       ansible.posix.firewalld:
   80 | #         port: "2379-2381/tcp"
   81 | #         zone: trusted
   82 | #         state: enabled
   83 | #         permanent: true
   84 | #         immediate: true
   85 | #
   86 | #     - name: If firewalld enabled, allow default CIDRs
   87 | #       ansible.posix.firewalld:
   88 | #         source: "{{ item }}"
   89 | #         zone: trusted
   90 | #         state: enabled
   91 | #         permanent: true
   92 | #         immediate: true
   93 | #       loop:
   94 | #         - 10.42.0.0/16  # Pods
   95 | #         - 10.43.0.0/16  # Services
   96 | 
   97 | - name: Disable nm-cloud-setup.service for k3s service
   98 |   ansible.builtin.systemd:
   99 |     name: nm-cloud-setup.service
  100 |     state: stopped
  101 |     enabled: false
  102 |   ignore_errors: true
  103 | 
  104 | - name: Add br_netfilter to /etc/modules-load.d/
  105 |   ansible.builtin.copy:
  106 |     content: "br_netfilter"
  107 |     dest: /etc/modules-load.d/br_netfilter.conf
  108 |     mode: "u=rw,g=,o="
  109 |   when: (ansible_os_family == 'RedHat' or ansible_distribution == 'Archlinux')
  110 | 
  111 | - name: Load br_netfilter
  112 |   modprobe:
  113 |     name: br_netfilter
  114 |     state: present
  115 |   when: (ansible_os_family == 'RedHat' or ansible_distribution == 'Archlinux')
  116 | 
  117 | - name: Set bridge-nf-call-iptables (just to be sure)
  118 |   sysctl:
  119 |     name: "{{ item }}"
  120 |     value: "1"
  121 |     state: present
  122 |     reload: true
  123 |   when: (ansible_os_family == 'RedHat' or ansible_distribution == 'Archlinux')
  124 |   loop:
  125 |     - net.bridge.bridge-nf-call-iptables
  126 |     - net.bridge.bridge-nf-call-ip6tables
  127 | 
  128 | - name: Check for Apparmor existence
  129 |   ansible.builtin.stat:
  130 |     path: /sys/module/apparmor/parameters/enabled
  131 |   register: apparmor_enabled
  132 | 
  133 | - name: Check if Apparmor is enabled
  134 |   when: apparmor_enabled.stat.exists
  135 |   ansible.builtin.command: cat /sys/module/apparmor/parameters/enabled
  136 |   register: apparmor_status
  137 |   changed_when: false
  138 | 
  139 | - name: Install Apparmor Parser [Suse]
  140 |   when:
  141 |     - ansible_os_family == 'Suse'
  142 |     - apparmor_status is defined
  143 |     - apparmor_status.stdout == "Y"
  144 |   ansible.builtin.package:
  145 |     name: apparmor-parser
  146 |     state: present
  147 | 
  148 | - name: Install Apparmor Parser [Debian]
  149 |   when:
  150 |     - ansible_distribution == 'Debian'
  151 |     - ansible_facts['distribution_major_version'] == "11"
  152 |     - apparmor_status is defined
  153 |     - apparmor_status.stdout == "Y"
  154 |   ansible.builtin.package:
  155 |     name: apparmor
  156 |     state: present
  157 | 
  158 | - name: Gather the package facts
  159 |   ansible.builtin.package_facts:
  160 |     manager: auto
  161 | 
  162 | # Iptables v1.8.0-1.8.4 have a specific bug with K3s. https://github.com/k3s-io/k3s/issues/3117
  163 | - name: If iptables v1.8.0-1.8.4, warn user  # noqa ignore-errors
  164 |   when:
  165 |     - ansible_facts.packages['iptables'] is defined
  166 |     - ansible_facts.packages['iptables'][0]['version'] is version('1.8.5', '<')
  167 |     - ansible_facts.packages['iptables'][0]['version'] is version('1.7.9', '>')
  168 |   ansible.builtin.fail:
  169 |     msg:
  170 |       - "Warning: Iptables {{ ansible_facts.packages['iptables'][0]['version'] }} found."
  171 |       - "Add '--prefer-bundled-bin' to extra_server_args variable to use the bundled iptables binary."
  172 |   ignore_errors: true
  173 | 
  174 | - name: Add /usr/local/bin to sudo secure_path
  175 |   ansible.builtin.lineinfile:
  176 |     line: 'Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin'
  177 |     regexp: "Defaults(\\s)*secure_path(\\s)*="
  178 |     state: present
  179 |     insertafter: EOF
  180 |     path: /etc/sudoers
  181 |     validate: 'visudo -cf %s'
  182 |   when: ansible_os_family == 'RedHat'
  183 | 
  184 | - name: Setup alternative K3s directory
  185 |   when:
  186 |     - k3s_server_location is defined
  187 |     - k3s_server_location != "/var/lib/rancher/k3s"
  188 |   block:
  189 |     - name: Make rancher directory
  190 |       ansible.builtin.file:
  191 |         path: "/var/lib/rancher"
  192 |         mode: 0755
  193 |         state: directory
  194 |     - name: Create symlink
  195 |       ansible.builtin.file:
  196 |         dest: /var/lib/rancher/k3s
  197 |         src: "{{ k3s_server_location }}"
  198 |         force: true
  199 |         state: link
  200 | 
```

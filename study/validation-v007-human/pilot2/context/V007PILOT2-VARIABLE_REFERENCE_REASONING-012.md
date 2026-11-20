# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-012

- Repository: `konstruktoid/ansible-role-hardening`
- Commit: `4dc09871ed38322eb6e4cdda8e2c77b79892d73d`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `tasks/packages.yml` (reported anchor line 104)
- Flagged construct: not named by the finding; the anchor line 104 lies in the task at line 104, name `Get needrestart restart value`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–221 of 221:

```text
    1 | ---
    2 | - name: Gather the package facts
    3 |   ansible.builtin.package_facts:
    4 |     manager: auto
    5 | 
    6 | - name: Intersect installed packages with blocklist
    7 |   ansible.builtin.set_fact:
    8 |     blocked_installed_packages: "{{ ansible_facts.packages.keys() | intersect(packages_blocklist) }}"
    9 | 
   10 | - name: Generic package removal
   11 |   become: true
   12 |   ansible.builtin.package:
   13 |     name: "{{ item }}"
   14 |     state: absent
   15 |   loop: "{{ blocked_installed_packages }}"
   16 |   when: blocked_installed_packages | length > 0
   17 | 
   18 | - name: Debian family package management
   19 |   become: true
   20 |   environment:
   21 |     DEBIAN_FRONTEND: noninteractive
   22 |   when:
   23 |     - ansible_facts.os_family == "Debian"
   24 |   block:
   25 |     - name: Debian family package installation
   26 |       ansible.builtin.apt:
   27 |         name: "{{ packages_debian }}"
   28 |         state: present
   29 |         install_recommends: false
   30 |         update_cache: true
   31 |       when:
   32 |         - ansible_facts.os_family == "Debian"
   33 |         - packages_debian | length > 0
   34 |       notify:
   35 |         - Run apt-get clean
   36 |         - Run apt-get autoremove
   37 | 
   38 |     - name: Ubuntu package installation
   39 |       ansible.builtin.apt:
   40 |         name: "{{ packages_ubuntu }}"
   41 |         state: present
   42 |         install_recommends: false
   43 |       when:
   44 |         - ansible_facts.distribution == "Ubuntu"
   45 |         - packages_ubuntu | length > 0
   46 |       notify:
   47 |         - Run apt-get clean
   48 |         - Run apt-get autoremove
   49 | 
   50 |     - name: Install unattended-upgrades support package
   51 |       ansible.builtin.apt:
   52 |         name: "{{ 'apt-config-auto-update' if (ansible_facts.distribution == 'Debian') else 'update-notifier-common' }}"
   53 |         state: present
   54 |         install_recommends: false
   55 |       notify:
   56 |         - Run apt-get clean
   57 |         - Run apt-get autoremove
   58 | 
   59 |     - name: Run apt purge
   60 |       become: true
   61 |       ansible.builtin.apt:
   62 |         name: "{{ packages_blocklist }}"
   63 |         state: absent
   64 |         purge: true
   65 |       register: apt_purge
   66 |       failed_when:
   67 |         - apt_purge is not success
   68 |         - not "No package" in apt_purge.msg
   69 |       notify:
   70 |         - Run apt-get clean
   71 |         - Run apt-get autoremove
   72 | 
   73 | - name: RedHat family package installation
   74 |   become: true
   75 |   ansible.builtin.dnf:
   76 |     name: "{{ packages_redhat }}"
   77 |     state: present
   78 |     update_cache: true
   79 |   when:
   80 |     - ansible_facts.os_family == "RedHat"
   81 |     - packages_redhat | length > 0
   82 |   notify:
   83 |     - Run dnf autoremove
   84 | 
   85 | - name: Populate package facts
   86 |   ansible.builtin.package_facts:
   87 | 
   88 | - name: Populate service facts
   89 |   ansible.builtin.service_facts:
   90 | 
   91 | - name: Configure needrestart
   92 |   become: true
   93 |   when:
   94 |     - '"needrestart" in ansible_facts.packages'
   95 |   block:
   96 |     - name: Create needrestart directory
   97 |       ansible.builtin.file:
   98 |         path: /etc/needrestart/conf.d
   99 |         state: directory
  100 |         owner: root
  101 |         group: root
  102 |         mode: "0755"
  103 | 
  104 |     - name: Get needrestart restart value
  105 |       ansible.builtin.command:
  106 |         cmd: grep -Rqo "$nrconf{restart} = 'l';" /etc/needrestart/conf.d/
  107 |       register: needrestart_restart_set
  108 |       changed_when: false
  109 |       failed_when: false
  110 | 
  111 |     - name: Configure needrestart
  112 |       ansible.builtin.lineinfile:
  113 |         path: /etc/needrestart/conf.d/00-restart.conf
  114 |         line: $nrconf{restart} = 'l';
  115 |         create: true
  116 |         owner: root
  117 |         group: root
  118 |         mode: "0644"
  119 |       when:
  120 |         - needrestart_restart_set.rc != 0
  121 | 
  122 | - name: VirtualBox guest packages installation
  123 |   become: true
  124 |   ansible.builtin.apt:
  125 |     name: "{{ packages }}"
  126 |     state: present
  127 |     install_recommends: false
  128 |   vars:
  129 |     packages:
  130 |       - virtualbox-guest-dkms
  131 |       - virtualbox-guest-utils
  132 |   register: virtualbox_packages
  133 |   when:
  134 |     - ansible_facts.virtualization_type == "VirtualBox"
  135 |     - ansible_facts.distribution == "Ubuntu"
  136 |   failed_when:
  137 |     - virtualbox_packages is not success
  138 |     - not "No package matching" in virtualbox_packages.msg
  139 | 
  140 | - name: VMWare package installation
  141 |   become: true
  142 |   ansible.builtin.package:
  143 |     name: open-vm-tools
  144 |     state: present
  145 |   when:
  146 |     - ansible_facts.virtualization_type == "VMware"
  147 | 
  148 | - name: QEMU package installation
  149 |   become: true
  150 |   ansible.builtin.package:
  151 |     name: qemu-guest-agent
  152 |     state: present
  153 |   when:
  154 |     - ansible_facts.system_vendor == "QEMU"
  155 | 
  156 | - name: Install and start rngd
  157 |   become: true
  158 |   when:
  159 |     - ansible_facts.flags is defined
  160 |     - "'rdrand' in ansible_facts.flags"
  161 |     - ansible_facts.virtualization_type not in ["container", "docker", "podman"]
  162 |   block:
  163 |     - name: Install rng-tools5
  164 |       ansible.builtin.apt:
  165 |         name: rng-tools5
  166 |         state: present
  167 |       when:
  168 |         - ansible_facts.os_family == "Debian"
  169 | 
  170 |     - name: Install rng-tools
  171 |       ansible.builtin.dnf:
  172 |         name: rng-tools
  173 |         state: present
  174 |         disable_plugin:
  175 |           - needrestart
  176 |       when:
  177 |         - ansible_facts.os_family == "RedHat"
  178 | 
  179 |     - name: Start and enable rngd service
  180 |       ansible.builtin.systemd_service:
  181 |         name: rngd
  182 |         state: started
  183 |         enabled: true
  184 | 
  185 | - name: Stat sysstat default
  186 |   become: true
  187 |   ansible.builtin.stat:
  188 |     path: /etc/default/sysstat
  189 |   register: default_sysstat
  190 | 
  191 | - name: Enable sysstat
  192 |   become: true
  193 |   ansible.builtin.lineinfile:
  194 |     regexp: ^ENABLED
  195 |     line: ENABLED="true"
  196 |     dest: /etc/default/sysstat
  197 |     mode: "0644"
  198 |     state: present
  199 |     create: false
  200 |     backrefs: true
  201 |   when:
  202 |     - default_sysstat.stat.exists
  203 | 
  204 | - name: Remove unneeded Debian dependencies
  205 |   become: true
  206 |   ansible.builtin.apt:
  207 |     autoclean: true
  208 |     autoremove: true
  209 |     clean: true
  210 |   changed_when: false
  211 |   when:
  212 |     - ansible_facts.os_family == "Debian"
  213 | 
  214 | - name: Run dnf autoremove
  215 |   become: true
  216 |   ansible.builtin.dnf:
  217 |     autoremove: true
  218 |     disable_plugin:
  219 |       - needrestart
  220 |   when:
  221 |     - ansible_facts.os_family == "RedHat"
```

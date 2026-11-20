# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-004

- Repository: `axivo/k3s-cluster`
- Commit: `f0e3a56f57f0e13f9f8624af2bb370c7eb92063f`
- Family: maintainability_complexity
- Rule: `ansibleguard/excessive-nesting`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `roles/cluster/tasks/configuration.yaml` (reported anchor line 79)
- Flagged construct: not named by the finding; the anchor line 79 lies in the task at line 79, name `Create device rule`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–350 of 350:

```text
    1 | ---
    2 | - name: Hardware Configuration
    3 |   notify: Reboot
    4 |   block:
    5 |     - name: Raspberry Pi Configuration
    6 |       when: cluster_vars.hardware.product | lower == 'raspberry pi'
    7 |       block:
    8 |         - name: Set service facts
    9 |           ansible.builtin.service_facts:
   10 | 
   11 |         - name: Bluetooth Configuration
   12 |           when: cluster_vars.service.bluetooth.enabled is falsy
   13 |           block:
   14 |             - name: Disable bluetooth service
   15 |               ansible.builtin.systemd_service:
   16 |                 name: bluetooth.service
   17 |                 state: stopped
   18 |                 enabled: false
   19 |               when: ansible_facts.services['bluetooth.service'] is defined
   20 | 
   21 |             - name: Disable hciuart service
   22 |               ansible.builtin.systemd_service:
   23 |                 name: hciuart.service
   24 |                 state: stopped
   25 |                 enabled: false
   26 |               when: ansible_facts.services['hciuart.service'] is defined
   27 | 
   28 |         - name: WiFi Configuration
   29 |           when: cluster_vars.service.wifi.enabled is falsy
   30 |           block:
   31 |             - name: Disable wifi service
   32 |               ansible.builtin.systemd_service:
   33 |                 name: wpa_supplicant.service
   34 |                 state: stopped
   35 |                 enabled: false
   36 |               when: ansible_facts.services['wpa_supplicant.service'] is defined
   37 | 
   38 |         - name: Create firmware purge configuration
   39 |           ansible.builtin.copy:
   40 |             content: |
   41 |               DPkg::Post-Invoke {"/usr/bin/find /boot/firmware -type f -name '*.bak' -delete 2>/dev/null || true";};
   42 |             dest: /etc/apt/apt.conf.d/90rpi-firmware-purge
   43 |             owner: root
   44 |             group: root
   45 |             mode: '644'
   46 | 
   47 |     - name: USB Device Configuration
   48 |       when: cluster_vars.device.enabled is truthy
   49 |       block:
   50 |         - name: Set device id
   51 |           ansible.builtin.command:
   52 |             cmd: lsusb -s {{ cluster_vars.device.id }}
   53 |           changed_when: false
   54 |           register: cluster_device_id
   55 | 
   56 |         - name: Device Trim
   57 |           when: cluster_device_id.stdout.find(cluster_vars.device.name) != -1
   58 |           block:
   59 |             - name: Set device attributes fact
   60 |               ansible.builtin.set_fact:
   61 |                 cluster_device_attributes: "{{ cluster_device | join | trim | split(':') }}"
   62 |               vars:
   63 |                 cluster_device: "{{ cluster_device_id.stdout | regex_search('ID\\s+([\\w:]+)\\s+' + cluster_vars.device.name, '\\1') }}"
   64 | 
   65 |             - name: Device Rule Setup
   66 |               when:
   67 |                 - cluster_device_attributes is iterable
   68 |                 - cluster_device_attributes | length == 2
   69 |               block:
   70 |                 - name: Set device rule fact
   71 |                   ansible.builtin.set_fact:
   72 |                     cluster_device_rule:
   73 |                       - ACTION=="add|change"
   74 |                       - ATTRS{idVendor}=="{{ cluster_device_attributes[0] }}"
   75 |                       - ATTRS{idProduct}=="{{ cluster_device_attributes[1] }}"
   76 |                       - SUBSYSTEM=="scsi_disk"
   77 |                       - ATTR{provisioning_mode}="unmap"
   78 | 
   79 |                 - name: Create device rule
   80 |                   ansible.builtin.lineinfile:
   81 |                     path: /etc/udev/rules.d/10-unmap.fstrim.rules
   82 |                     line: "{{ cluster_device_rule | join(', ') }}"
   83 |                     regexp: ^ACTION
   84 |                     owner: root
   85 |                     group: root
   86 |                     mode: '644'
   87 |                     create: true
   88 | 
   89 |     - name: Mounted Filesystem
   90 |       block:
   91 |         - name: Start service
   92 |           ansible.builtin.systemd_service:
   93 |             name: fstrim.timer
   94 |             state: started
   95 |             daemon_reload: true
   96 |             enabled: true
   97 | 
   98 |         - name: Discard unused blocks on mounted filesystem
   99 |           ansible.builtin.command:
  100 |             cmd: fstrim -vA
  101 |           changed_when: cluster_command.stdout.find('trimmed') != -1
  102 |           register: cluster_command
  103 | 
  104 | - name: OS Configuration
  105 |   block:
  106 |     - name: Get host fqdn
  107 |       ansible.builtin.command:
  108 |         cmd: hostname --fqdn
  109 |       changed_when: false
  110 |       register: cluster_host_fqdn
  111 | 
  112 |     - name: Get host all fqdns
  113 |       ansible.builtin.command:
  114 |         cmd: hostname --all-fqdns
  115 |       changed_when: false
  116 |       register: cluster_host_all_fqdns
  117 | 
  118 |     - name: Set cluster host fact
  119 |       ansible.builtin.set_fact:
  120 |         cluster_host:
  121 |           extension: "{{ cluster_host_all_fqdns.stdout | split | first | split('.') | last | default('local') }}"
  122 |           fqdn: '{{ cluster_host_all_fqdns.stdout | split | first }}'
  123 |           ipv4: "{{ ansible_default_ipv4['address'] }}"
  124 |           name: '{{ ansible_host }}'
  125 | 
  126 |     - name: Set host fqdn
  127 |       ansible.builtin.replace:
  128 |         path: /etc/hosts
  129 |         regexp: ^127.0.1.1\s.+\s{{ cluster_host['name'] }}$
  130 |         replace: 127.0.1.1 {{ cluster_host['fqdn'] }} {{ cluster_host['name'] }}
  131 |       notify: Reboot
  132 |       when: cluster_host_fqdn.stdout != cluster_host['fqdn']
  133 | 
  134 |     - name: Set root full name
  135 |       ansible.builtin.command:
  136 |         cmd: chfn -f "{{ cluster_host['name'] }}" root
  137 |       changed_when: false
  138 | 
  139 |     - name: Disable access time updates
  140 |       ansible.builtin.replace:
  141 |         path: /etc/fstab
  142 |         regexp: defaults\t0
  143 |         replace: defaults,noatime\t0
  144 |       notify: Reboot
  145 | 
  146 |     - name: Disable cloud-init service
  147 |       ansible.builtin.file:
  148 |         path: /etc/cloud/cloud-init.disabled
  149 |         access_time: preserve
  150 |         modification_time: preserve
  151 |         state: touch
  152 |         owner: root
  153 |         group: root
  154 |         mode: '644'
  155 |       notify: Reboot
  156 |       when: cluster_vars.service.cloud_init.enabled is falsy
  157 | 
  158 |     - name: Disable firewall service
  159 |       ansible.builtin.systemd_service:
  160 |         name: ufw.service
  161 |         state: stopped
  162 |         enabled: false
  163 | 
  164 |     - name: Disable snapd services
  165 |       ansible.builtin.systemd_service:
  166 |         name: '{{ item }}'
  167 |         state: stopped
  168 |         enabled: false
  169 |       loop:
  170 |         - snapd.apparmor.service
  171 |         - snapd.service
  172 |         - snapd.seeded.service
  173 |         - snapd.socket
  174 |       when: cluster_vars.service.snapd.enabled is falsy
  175 | 
  176 |     - name: Install cifs utilities package
  177 |       ansible.builtin.apt:
  178 |         name: cifs-utils
  179 |         autoremove: true
  180 |         update_cache: true
  181 | 
  182 |     - name: Load kernel modules
  183 |       ansible.builtin.copy:
  184 |         content: |
  185 |           br_netfilter
  186 |           overlay
  187 |         dest: /etc/modules-load.d/kubernetes.conf
  188 |         owner: root
  189 |         group: root
  190 |         mode: '644'
  191 |       notify: Reboot
  192 | 
  193 |     - name: Unattended Upgrades
  194 |       notify: Restart unattended upgrades service
  195 |       when: cluster_vars.service.unattended_upgrades.enabled is truthy
  196 |       block:
  197 |         - name: Install history notification package
  198 |           ansible.builtin.apt:
  199 |             name: apt-listchanges
  200 |             autoremove: true
  201 |             update_cache: true
  202 | 
  203 |         - name: Update unattended upgrades configuration
  204 |           ansible.builtin.replace:
  205 |             path: /etc/apt/apt.conf.d/50unattended-upgrades
  206 |             regexp: '{{ item.regexp }}'
  207 |             replace: '{{ item.replace }}'
  208 |           loop:
  209 |             - regexp: ^(?:.*)(\"\${distro_id}:\${distro_codename}-updates\";)$
  210 |               replace: \t\g<1>
  211 |             - regexp: ^(?:.*)(Unattended-Upgrade::Mail)\s.*;$
  212 |               replace: '\g<1> "{{ global_map.credentials.cluster.postfix.user.alias }}";'
  213 |             - regexp: ^(?:.*)(Unattended-Upgrade::MailReport)\s.*;$
  214 |               replace: '\g<1> "{{ cluster_vars.service.unattended_upgrades.mail_report }}";'
  215 |             - regexp: ^(?:.*)(Unattended-Upgrade::Remove-Unused-Dependencies)\s.*;$
  216 |               replace: '\g<1> "{{ cluster_vars.service.unattended_upgrades.remove_deps }}";'
  217 | 
  218 | - name: Mail Configuration
  219 |   notify: Reload postfix service
  220 |   when: cluster_vars.service.postfix.enabled is truthy
  221 |   block:
  222 |     - name: Set mail configuration
  223 |       ansible.builtin.debconf:
  224 |         name: postfix
  225 |         question: postfix/{{ item.question }}
  226 |         value: '{{ item.value }}'
  227 |         vtype: '{{ item.vtype }}'
  228 |       when: item.enabled is truthy
  229 |       loop:
  230 |         # General mail configuration type
  231 |         - question: main_mailer_type
  232 |           value: 'Satellite system'
  233 |           vtype: select
  234 |           enabled: true
  235 |         # System mail name
  236 |         - question: mailname
  237 |           value: "{{ cluster_host['fqdn'] }}"
  238 |           vtype: string
  239 |           enabled: true
  240 |         # SMTP relay host
  241 |         - question: relayhost
  242 |           value: '[{{ cluster_vars.service.postfix.relay.host }}]:{{ cluster_vars.service.postfix.relay.port }}'
  243 |           vtype: string
  244 |           enabled: true
  245 |         # Recipient for root and postmaster mail
  246 |         - question: root_address
  247 |           value: "root@{{ cluster_host['fqdn'] }}"
  248 |           vtype: string
  249 |           enabled: true
  250 |         # Other destinations to accept mail for (blank for none)
  251 |         # Disabled, host name wrongly set as fqdn by postfix
  252 |         - question: destinations
  253 |           value: "$myhostname, {{ cluster_host['name'] }}, localhost.{{ cluster_host['extension'] }}, localhost"
  254 |           vtype: string
  255 |           enabled: false
  256 |         # Force synchronous updates on mail queue
  257 |         - question: chattr
  258 |           value: 'true'
  259 |           vtype: boolean
  260 |           enabled: true
  261 |         # Local networks
  262 |         - question: mynetworks
  263 |           value: "127.0.0.1/32, 127.0.1.1/32, {{ cluster_host['ipv4'] }}/32"
  264 |           vtype: string
  265 |           enabled: true
  266 |         # Local address extension character
  267 |         # Disabled, using default value, kept as reference
  268 |         - question: recipient_delim
  269 |           value: '+'
  270 |           vtype: string
  271 |           enabled: false
  272 |         # Mailbox size limit (bytes)
  273 |         - question: mailbox_limit
  274 |           value: '51200000'
  275 |           vtype: string
  276 |           enabled: true
  277 |         # Internet protocols to use
  278 |         - question: protocols
  279 |           value: '{{ cluster_vars.service.postfix.protocols }}'
  280 |           vtype: select
  281 |           enabled: true
  282 | 
  283 |     - name: Install mail package
  284 |       ansible.builtin.apt:
  285 |         name: bsd-mailx
  286 |         autoremove: true
  287 |         update_cache: true
  288 |       environment:
  289 |         DEBIAN_FRONTEND: noninteractive
  290 | 
  291 |     - name: Create generic map
  292 |       ansible.builtin.copy:
  293 |         content: "root@{{ cluster_host['fqdn'] }} {{ global_map.credentials.cluster.postfix.user.alias }}\n"
  294 |         dest: /etc/postfix/generic
  295 |         owner: root
  296 |         group: root
  297 |         mode: '600'
  298 | 
  299 |     - name: Set sasl password fact
  300 |       ansible.builtin.set_fact:
  301 |         cluster_sasl_password:[REDACTED VALUE BLOCK]
  302 |           [REDACTED ENCRYPTED VALUE]
      [... 2 further identical redacted lines, through 304]
  305 | 
  306 |     - name: Create sasl password map
  307 |       ansible.builtin.copy:
  308 |         content: "{{ cluster_sasl_password | join(':') }}\n"
  309 |         dest: /etc/postfix/sasl/password
  310 |         owner: root
  311 |         group: root
  312 |         mode: '600'
  313 | 
  314 |     - name: Initialize map database
  315 |       ansible.builtin.command:
  316 |         cmd: postmap {{ item }}
  317 |       changed_when: false
  318 |       loop:
  319 |         - /etc/postfix/generic
  320 |         - /etc/postfix/sasl/password
  321 | 
  322 |     - name: Set map file permissions
  323 |       ansible.builtin.file:
  324 |         path: '{{ item }}'
  325 |         owner: root
  326 |         group: root
  327 |         mode: '600'
  328 |       loop:
  329 |         - /etc/postfix/generic.db
  330 |         - /etc/postfix/sasl/password.db
  331 | 
  332 |     - name: Update mail configuration
  333 |       ansible.builtin.command:
  334 |         cmd: postconf -e '{{ item.name }} = {{ item.value }}'
  335 |       changed_when: false
  336 |       loop:
  337 |         - name: mydestination
  338 |           value: $myhostname, {{ cluster_host['name'] }}, localhost.{{ cluster_host['extension'] }}, localhost
  339 |         - name: smtp_generic_maps
  340 |           value: hash:/etc/postfix/generic
  341 |         - name: smtp_sasl_auth_enable
  342 |           value: 'yes'
  343 |         - name: smtp_sasl_password_maps
  344 |           value: hash:/etc/postfix/sasl/password
  345 |         - name: smtp_sasl_security_options
  346 |           value: noanonymous
  347 |         - name: smtp_tls_CAfile
  348 |           value: /etc/ssl/certs/ca-certificates.crt
  349 |         - name: smtp_tls_security_level
  350 |           value: encrypt
```

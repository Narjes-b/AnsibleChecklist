# Frozen source context: V007PILOT2-SECURITY-013

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: security
- Rule: `ansibleguard/unsafe-file-write`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `automation/roles/consul/tasks/dnsmasq.yml` (reported anchor line 87)
- Flagged construct: not named by the finding; the anchor line 87 lies in the task at line 87, name `Add a nameserver entry poining to localhost for dnsmasq`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–97 of 97:

```text
    1 | ---
    2 | # File: dnsmasq.yml - Dnsmasq tasks for Consul
    3 | 
    4 | - name: Install Dnsmasq package
    5 |   ansible.builtin.package:
    6 |     name: "{{ dnsmasq_package }}"
    7 |     state: present
    8 |   register: package_status
    9 |   until: package_status is success
   10 |   delay: 5
   11 |   retries: 3
   12 |   become: true
   13 |   tags: dnsmasq, installation
   14 | 
   15 | - name: Create Dnsmasq configuration directory
   16 |   ansible.builtin.file:
   17 |     path: /usr/local/etc/dnsmasq.d
   18 |     state: directory
   19 |     owner: root
   20 |     group: wheel
   21 |     mode: "0700"
   22 |   become: true
   23 |   when: ansible_os_family == "FreeBSD"
   24 |   tags: dnsmasq
   25 | 
   26 | - name: Include Dnsmasq configuration directory
   27 |   ansible.builtin.lineinfile:
   28 |     dest: /usr/local/etc/dnsmasq.conf
   29 |     line: "conf-dir=/usr/local/etc/dnsmasq.d/,*.conf"
   30 |   become: true
   31 |   notify: restart dnsmasq
   32 |   when: ansible_os_family == "FreeBSD"
   33 |   tags: dnsmasq
   34 | 
   35 | - name: Create Dnsmasq configuration
   36 |   ansible.builtin.template:
   37 |     src: dnsmasq-10-consul.j2
   38 |     dest: "{{ dnsmasq_item.dest }}"
   39 |     owner: root
   40 |     group: "{{ dnsmasq_item.group }}"
   41 |     mode: "0644"
   42 |   become: true
   43 |   notify: restart dnsmasq
   44 |   when: "{{ dnsmasq_item.when }}" # noqa no-jinja-when
   45 |   loop:
   46 |     - { dest: "/etc/dnsmasq.d/10-consul", group: "root", when: ansible_os_family|lower != "freebsd" }
   47 |     - { dest: "/usr/local/etc/dnsmasq.d/consul.conf", group: "wheel", when: ansible_os_family|lower == "freebsd" }
   48 |   loop_control:
   49 |     loop_var: dnsmasq_item
   50 |   tags: dnsmasq
   51 | 
   52 | - name: Disable systemd-resolved
   53 |   when: ansible_service_mgr == "systemd"
   54 |   block:
   55 |     - name: Check if systemd-resolved service exists
   56 |       ansible.builtin.stat:
   57 |         path: /lib/systemd/system/systemd-resolved.service
   58 |       register: systemd_resolved_service
   59 | 
   60 |     - name: Disable systemd-resolved service
   61 |       ansible.builtin.service:
   62 |         name: systemd-resolved
   63 |         enabled: false
   64 |         state: stopped
   65 |       become: true
   66 |       when: systemd_resolved_service.stat.exists
   67 | 
   68 |     - name: Check if resolv.conf is pointing to systemd-resolved
   69 |       ansible.builtin.stat:
   70 |         path: /etc/resolv.conf
   71 |       register: resolv_dot_conf
   72 | 
   73 |     - block:
   74 |         - name: Remove resolv.conf association with systemd-resolved
   75 |           ansible.builtin.file:
   76 |             path: /etc/resolv.conf
   77 |             state: absent
   78 | 
   79 |         - name: Create /etc/resolv.conf
   80 |           ansible.builtin.file:
   81 |             path: /etc/resolv.conf
   82 |             state: touch
   83 |             owner: root
   84 |             group: root
   85 |             mode: u=rw,g=r,o=r
   86 | 
   87 |         - name: Add a nameserver entry poining to localhost for dnsmasq
   88 |           ansible.builtin.lineinfile:
   89 |             path: /etc/resolv.conf
   90 |             regexp: "^nameserver 127.0.0.1"
   91 |             line: "nameserver 127.0.0.1"
   92 |             unsafe_writes: true # to prevent failures in CI
   93 |       become: true
   94 |       when:
   95 |         - resolv_dot_conf.stat.islnk is defined
   96 |         - resolv_dot_conf.stat.islnk
   97 |         - resolv_dot_conf.stat.lnk_source == "/run/systemd/resolve/stub-resolv.conf"
```

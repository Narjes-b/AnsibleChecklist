# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-011

- Repository: `sebdanielsson/infra`
- Commit: `abc768b1d6cd78d1e2feef1262645bb2769fb5df`
- Family: Objective correctness
- Rule: `ansibleguard/missing-handler`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/bpi-r4.yml` (reported anchor line 67)
- Object: `source_location` `ff61b9eefdc314566feb8750b707a1a9a731763821edefc95e5cd63191b70c47`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–113 of 113:

```text
    1 | ---
    2 | - name: Configure home gateway
    3 |   hosts: bpi-r4
    4 |   become: true
    5 | 
    6 |   vars:
    7 |     ansible_python_interpreter: /usr/bin/python3
    8 |     service_account_token: "{{ lookup('env', 'OP_SERVICE_ACCOUNT_TOKEN') }}"
    9 | 
   10 |   handlers:
   11 |     - name: Import handlers
   12 |       ansible.builtin.import_tasks: handlers/main.yml
   13 | 
   14 |   tasks:
   15 |     - name: Remove `ra_slaac` from DHCP configuration if it exists
   16 |       ansible.builtin.shell: |
   17 |         if /sbin/uci get dhcp.lan.ra_slaac >/dev/null 2>&1; then
   18 |           /sbin/uci del dhcp.lan.ra_slaac && echo "Removed ra_slaac from DHCP configuration"
   19 |         fi
   20 |       register: dhcp_lan_ra_slaac
   21 |       changed_when: "'Removed ra_slaac from DHCP configuration' in dhcp_lan_ra_slaac.stdout"
   22 |       notify: UCI commit changes
   23 | 
   24 |     - name: Set Dropbear interface to LAN if not set
   25 |       ansible.builtin.shell: |
   26 |         if [ "$(/sbin/uci get dropbear.main.Interface 2>/dev/null)" != "lan" ]; then
   27 |           /sbin/uci set dropbear.main.Interface='lan' && echo "Set Dropbear interface to LAN"
   28 |         fi
   29 |       register: dropbear_main_interface
   30 |       changed_when: "'Set dropbear interface to LAN' in dropbear_main_interface.stdout"
   31 |       notify: UCI commit changes
   32 | 
   33 |     - name: Set LAN IP address if different
   34 |       ansible.builtin.shell: |
   35 |         if [ "$(/sbin/uci get network.lan.ipaddr 2>/dev/null)" != "192.168.1.1" ]; then
   36 |           /sbin/uci set network.lan.ipaddr='192.168.1.1' && echo "Set LAN IP address to 192.168.1.1"
   37 |         fi
   38 |       register: network_lan_ipaddr
   39 |       changed_when: "'Set LAN IP address to 192.168.1.1' in network_lan_ipaddr.stdout"
   40 |       notify: UCI commit changes
   41 | 
   42 |     - name: Set hostname if different
   43 |       ansible.builtin.shell: |
   44 |         if [ "$(/sbin/uci get system.cfg01e48a.hostname 2>/dev/null)" != "bpi-r4" ]; then
   45 |           /sbin/uci set system.cfg01e48a.hostname='bpi-r4' && echo "Set hostname to bpi-r4"
   46 |         fi
   47 |       register: system_cfg01e48a_hostname
   48 |       changed_when: "'Set hostname to bpi-r4' in system_cfg01e48a_hostname.stdout"
   49 |       notify: UCI commit changes
   50 | 
   51 |     - name: Set console log level if different
   52 |       ansible.builtin.shell: |
   53 |         if [ "$(/sbin/uci get system.cfg01e48a.conloglevel 2>/dev/null)" != "6" ]; then
   54 |           /sbin/uci set system.cfg01e48a.conloglevel='6' && echo "Set console log level to 6"
   55 |         fi
   56 |       register: system_cfg01e48a_conloglevel
   57 |       changed_when: "'Set console log level to 6' in system_cfg01e48a_conloglevel.stdout"
   58 |       notify: UCI commit changes
   59 | 
   60 |     - name: Enable HTTPS redirect in uHTTPd if not set
   61 |       ansible.builtin.shell: |
   62 |         if [ "$(/sbin/uci get uhttpd.main.redirect_https 2>/dev/null)" != "1" ]; then
   63 |           /sbin/uci set uhttpd.main.redirect_https='1' && echo "Enabled HTTPS redirect in uHTTPd"
   64 |         fi
   65 |       register: uhttpd_main_redirect_https
   66 |       changed_when: "'Enabled HTTPS redirect in uHTTPd' in uhttpd_main_redirect_https.stdout"
   67 |       notify: UCI commit changes
   68 | 
   69 |     - name: Install packages
   70 |       community.general.apk:
   71 |         name:
   72 |           - bash
   73 |           - luci-proto-wireguard
   74 |           - luci-app-https-dns-proxy
   75 |           - luci-app-acme
   76 |           - acme-acmesh-dnsapi
   77 |           - tailscale
   78 |           - curl
   79 |         update_cache: true
   80 |         state: latest
   81 | 
   82 |     - name: Enable and start service https-dns-proxy
   83 |       community.general.openwrt_init:
   84 |         name: https-dns-proxy
   85 |         enabled: true
   86 |         state: started
   87 | 
   88 |     - name: Enable and start service tailscale
   89 |       community.general.openwrt_init:
   90 |         name: tailscale
   91 |         enabled: true
   92 |         state: started
   93 | 
   94 |     - name: Check Tailscale status
   95 |       ansible.builtin.command: /usr/sbin/tailscale status
   96 |       register: tailscale_status
   97 |       changed_when: false
   98 |       check_mode: false
   99 |       failed_when: tailscale_status.rc not in [0, 1]
  100 | 
  101 |     - name: Login to Tailscale
  102 |       ansible.builtin.command: /usr/sbin/tailscale up --ssh --authkey "{{ lookup('env', 'TAILSCALE_AUTHKEY_ROUTER') }}"
  103 |       when: '"Logged out" in tailscale_status.stdout or "Tailscale is stopped" in tailscale_status.stdout'
  104 |       register: tailscale_login
  105 |       changed_when: tailscale_login.stdout != ''
  106 | 
  107 |     - name: SSH authorized key for 'root'
  108 |       ansible.posix.authorized_key:
  109 |         user: root
  110 |         key: "{{ lookup('env', 'SEBASTIAN_SSH_PUBLIC_KEY') }}"
  111 |         path: /etc/dropbear/authorized_keys
  112 |         manage_dir: false
  113 |         state: present
```

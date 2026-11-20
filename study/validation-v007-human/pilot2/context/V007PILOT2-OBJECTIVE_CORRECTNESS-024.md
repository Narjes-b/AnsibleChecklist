# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-024

- Repository: `cradle8810/ansible_hayaworld`
- Commit: `d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597`
- Family: objective_correctness
- Rule: `ansibleguard/missing-handler`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `diskmon.yml` (reported anchor line 77)
- Flagged construct: not named by the finding; the anchor line 77 lies in the task at line 69, name `Set Swappiness`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–98 of 98:

```text
    1 | ---
    2 | - name: Play for Diskmonitor using Scrutiny
    3 |   hosts: diskmon
    4 |   remote_user: ansible
    5 |   gather_facts: true
    6 |   become: true
    7 | 
    8 |   vars_files:
    9 |     - host_vars/networks.yml
   10 | 
   11 |   handlers:
   12 |     - name: Restart handler tasks
   13 |       ansible.builtin.import_tasks:
   14 |         file: handlers/main.yml
   15 | 
   16 |   tasks:
   17 |     - name: Common Settings
   18 |       ansible.builtin.import_role:
   19 |         name: common
   20 |       vars:
   21 |         common_firewall: "{{ firewall }}"
   22 |         common_pkg: "{{ apt }}"
   23 |         common_install_users: true
   24 | 
   25 |     - name: "Configure Scrutiny"
   26 |       ansible.builtin.import_role:
   27 |         name: scrutiny_server
   28 |       vars:
   29 |         scrutiny_server_mail_address: "{{ scrutiny.mail.address }}"
   30 |         scrutiny_server_mail_app_passwd: "{{ scrutiny.mail.app_passwd }}"
   31 |         scrutiny_server_mail_smtp_server: "smtp.gmail.com"
   32 |         scrutiny_server_mail_smtp_port: "587"
   33 |         scrutiny_server_discord_webhook_id: "ID"
   34 |         scrutiny_server_discord_webhook_token: [REDACTED_LITERAL]
   35 |         docker_drive_is_opt_docker: true
   36 |         docker_btrfs: true
   37 |         docker_drive_uuid: "5603a159-0211-4591-8be0-f61ab1007c60"
   38 |         docker_users:
   39 |           - ansible
   40 |           - hayato
   41 |       tags:
   42 |         - scrutiny
   43 | 
   44 |     - name: APC UPS Settings
   45 |       ansible.builtin.import_role:
   46 |         name: apcupsd
   47 |       vars:
   48 |         apcupsd_role: "slave"
   49 |         apcupsd_timeout: 60
   50 |       tags:
   51 |         - apc
   52 |         - ups
   53 | 
   54 |     - name: "Configure Rsyslog"
   55 |       ansible.builtin.import_role:
   56 |         name: rsyslog_client
   57 |       vars:
   58 |         rsyslog_client_additional_actions: "{{ rsyslog.rsyslog_client_additional_actions }}"
   59 |         rsyslog_client_journald_persistent: false
   60 |       tags:
   61 |         - rsyslog
   62 | 
   63 |     - name: Install Zabbix agent
   64 |       ansible.builtin.import_tasks:
   65 |         file: tasks/zabbix-agent2.yml
   66 |       tags:
   67 |         - zabbix
   68 | 
   69 |     - name: "Set Swappiness"
   70 |       community.general.ini_file:
   71 |         path: "/etc/sysctl.d/99-swappiness.conf"
   72 |         option: "vm.swappiness"
   73 |         value: "{{ swappiness }}"
   74 |         state: present
   75 |         no_extra_spaces: true
   76 |         mode: "644"
   77 |       notify: "swappiness sysctl"
   78 |       tags:
   79 |         - swap
   80 | 
   81 |     - name: "Install BorgBackup and Configuration Backup"
   82 |       ansible.builtin.import_role:
   83 |         name: borg
   84 |       vars:
   85 |         borg_device: "/mnt/backup/Service_Backups/diskmon"
   86 |         borg_sources:
   87 |           - src: influxdb
   88 |             dest: influxdb
   89 |           - src: scrutiny_influxdb
   90 |             dest: scrutiny_influxdb
   91 |       tags:
   92 |         - borg
   93 | 
   94 |     - name: Install/Config Zramswap
   95 |       ansible.builtin.import_role:
   96 |         name: zramswap
   97 |       tags:
   98 |         - zram
```

## Handler files of the role (all, including imported)

```text
### handlers/main.yml (103 lines)
    1 | ---
    2 | - name: Restart avahi-daemon
    3 |   ansible.builtin.systemd_service:
    4 |     name: avahi-daemon
    5 |     state: restarted
    6 |   listen: "Restart avahi-daemon"
    7 | 
    8 | - name: Restart rsyslog
    9 |   ansible.builtin.systemd_service:
   10 |     name: rsyslog
   11 |     state: restarted
   12 |   listen: "Restart rsyslog"
   13 | 
   14 | - name: Restart systemd-journald
   15 |   ansible.builtin.systemd_service:
   16 |     name: systemd-journald
   17 |     state: restarted
   18 |   listen: "Restart systemd-journald"
   19 | 
   20 | - name: Restart multipathd
   21 |   ansible.builtin.systemd_service:
   22 |     name: multipathd
   23 |     state: restarted
   24 |   listen: "Restart multipathd"
   25 | 
   26 | - name: "Restart systemd-resolved.service"
   27 |   ansible.builtin.systemd_service:
   28 |     name: systemd-resolved.service
   29 |     state: restarted
   30 |     enabled: true
   31 |   listen: "Restart systemd-resolved"
   32 | 
   33 | - name: "Reconfigure netplan"
   34 |   ansible.builtin.command:
   35 |     cmd: "netplan apply -f"
   36 |   register: retval
   37 |   changed_when: retval.rc == 0
   38 |   listen: "Reconfigure netplan"
   39 | 
   40 | - name: "Swappiness setting for nuc sysctl restart"
   41 |   ansible.builtin.command:
   42 |     cmd: "sysctl -p /etc/sysctl.d/00-localbind.conf"
   43 |   register: retval
   44 |   changed_when: retval.rc == 0
   45 |   listen: "localbind sysctl"
   46 | 
   47 | - name: "Restart ksmtuned"
   48 |   ansible.builtin.systemd_service:
   49 |     name: hdd_prevent_sleeping.service
   50 |     state: restarted
   51 |     enabled: true
   52 |   listen: "hdd_prevent_sleeping"
   53 | 
   54 | - name: "Restart NGiNX"
   55 |   ansible.builtin.systemd_service:
   56 |     name: nginx.service
   57 |     state: restarted
   58 |     enabled: true
   59 |   listen: "Restart NGiNX"
   60 | 
   61 | - name: "Restart cron"
   62 |   ansible.builtin.systemd_service:
   63 |     name: cron.service
   64 |     state: restarted
   65 |     enabled: true
   66 |   listen: "Restart cron"
   67 | 
   68 | - name: Restart zabbix-agent2
   69 |   ansible.builtin.systemd_service:
   70 |     name: zabbix-agent2
   71 |     state: restarted
   72 |     enabled: true
   73 |     daemon_reload: true
   74 |   listen: "Restart zabbix-agent2"
   75 | 
   76 | - name: Restart snmpd
   77 |   ansible.builtin.systemd_service:
   78 |     name: zabbix-agent2
   79 |     state: restarted
   80 |     enabled: true
   81 |     daemon_reload: true
   82 |   listen: "Restart snmpd"
   83 | 
   84 | - name: "Common / Reload sysctl"
   85 |   ansible.builtin.command:
   86 |     cmd: "sysctl -p"
   87 |   register: retval
   88 |   changed_when: retval.rc == 0
   89 |   listen: "Reload sysctl"
   90 | 
   91 | - name: "Enable Huge Page setting for nuc sysctl restart"
   92 |   ansible.builtin.command:
   93 |     cmd: "sysctl -p /etc/sysctl.d/99-hugepage.conf"
   94 |   register: retval
   95 |   changed_when: retval.rc == 0
   96 |   listen: "hugepage sysctl"
   97 | 
   98 | - name: "Initialize Borgbackup destination dir"
   99 |   ansible.builtin.command:
  100 |     cmd: "locale-gen ja_JP.UTF-8"
  101 |   register: retval
  102 |   changed_when: retval.rc == 0
  103 |   listen: "locale gen for skylark"
```

# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-019

- Repository: `cradle8810/ansible_hayaworld`
- Commit: `d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597`
- Family: maintainability_complexity
- Rule: `ansibleguard/large-play`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `k8s.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`k8s.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–68 of 68:

```text
    1 | - name: Play for k8s cluster nodes
    2 |   hosts: k8s
    3 |   remote_user: ansible
    4 |   gather_facts: true
    5 |   become: true
    6 | 
    7 |   vars_files:
    8 |     - host_vars/networks.yml
    9 | 
   10 |   handlers:
   11 |     - name: Restart handler tasks
   12 |       ansible.builtin.import_tasks:
   13 |         file: handlers/main.yml
   14 | 
   15 |   tasks:
   16 |     - name: Common Settings
   17 |       ansible.builtin.import_role:
   18 |         name: common
   19 |       vars:
   20 |         common_firewall: "{{ firewall }}"
   21 |         common_install_users: true
   22 | 
   23 |     - name: "Setup Tailscale Endpoint"
   24 |       ansible.builtin.import_role:
   25 |         name: tailscale_install
   26 |       vars:
   27 |         tailscale_install_tags:
   28 |           - k8s
   29 |         tailscale_install_args: "--accept-dns=true"
   30 |       tags:
   31 |         - tailscale
   32 | 
   33 |     - name: Install k8s
   34 |       ansible.builtin.include_role:
   35 |         name: k8s
   36 |         apply:
   37 |           tags:
   38 |             - k8s
   39 |       vars:
   40 |         k8s_drive_is_opt_docker: true
   41 |         k8s_btrfs: true
   42 |         k8s_drive_uuid: "397a73b4-c584-4a22-a093-15df469b5360"
   43 |       tags:
   44 |         - k8s
   45 | 
   46 |     - name: APC UPS Settings
   47 |       ansible.builtin.import_role:
   48 |         name: apcupsd
   49 |       vars:
   50 |         apcupsd_role: "slave"
   51 |         apcupsd_timeout: 60
   52 |       tags:
   53 |         - apc
   54 |         - ups
   55 | 
   56 |     - name: "Configure Rsyslog"
   57 |       ansible.builtin.import_role:
   58 |         name: rsyslog_client
   59 |       vars:
   60 |         rsyslog_client_journald_persistent: false
   61 |       tags:
   62 |         - rsyslog
   63 | 
   64 |     - name: Install Zabbix agent
   65 |       ansible.builtin.import_tasks:
   66 |         file: tasks/zabbix-agent2.yml
   67 |       tags:
   68 |         - zabbix
```

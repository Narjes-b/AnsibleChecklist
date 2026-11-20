# Frozen source context: V007PILOT2-STRUCTURE_REUSE-012

- Repository: `adoptium/infrastructure`
- Commit: `d31f47293b3a0166a4f9d7b8c51475d548999408`
- Family: structure_reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_core.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_core.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–77 of 77:

```text
    1 | ---
    2 | 
    3 | - name: Ensure that cfg_dir includes `/usr/local/nagios/etc/servers`
    4 |   lineinfile:
    5 |     path: /usr/local/nagios/etc/nagios.cfg
    6 |     regexp: '#cfg_dir=/usr/local/nagios/etc/servers'
    7 |     line: 'cfg_dir=/usr/local/nagios/etc/servers'
    8 |   become: yes
    9 | 
   10 | - name: Add Host Groups Configuration File Entry To Nagios Config`
   11 |   lineinfile:
   12 |     path: /usr/local/nagios/etc/nagios.cfg
   13 |     insertafter: '# You can specify individual object config files as shown below:'
   14 |     line: 'cfg_file=/usr/local/nagios/etc/objects/hostgroups.cfg'
   15 |   become: yes
   16 | 
   17 | - name: Register The Nagios Server Host Groups Config File
   18 |   stat:
   19 |     path: /usr/local/nagios/etc/objects/hostgroups.cfg
   20 |   register: nagios_host_group_config
   21 | 
   22 | - name: Create Base HostGroups Config File
   23 |   file:
   24 |     path: /usr/local/nagios/etc/objects/hostgroups.cfg
   25 |     state: touch
   26 |   become: yes
   27 |   when: nagios_host_group_config.stat.exists == false
   28 | 
   29 | - name: Add Host Groups Configuration File Entry To Nagios Config`
   30 |   lineinfile:
   31 |     path: /usr/local/nagios/etc/nagios.cfg
   32 |     insertafter: '# You can specify individual object config files as shown below:'
   33 |     line: 'cfg_file=/usr/local/nagios/etc/objects/servicegroups.cfg'
   34 |   become: yes
   35 | 
   36 | - name: Register The Nagios Service Groups Config File
   37 |   stat:
   38 |     path: /usr/local/nagios/etc/objects/servicegroups.cfg
   39 |   register: nagios_service_group_config
   40 | 
   41 | - name: Create Base ServiceGroups Config File
   42 |   file:
   43 |     path: /usr/local/nagios/etc/objects/servicegroups.cfg
   44 |     state: touch
   45 |     owner: nagios
   46 |     group: nagios
   47 |   become: yes
   48 |   when: nagios_service_group_config.stat.exists == false
   49 | 
   50 | - name: Create servers folder
   51 |   file:
   52 |     path: /usr/local/nagios/etc/servers
   53 |     state: directory
   54 |     owner: nagios
   55 |     group: nagios
   56 |   become: yes
   57 | 
   58 | - name: Update Lock File Path
   59 |   lineinfile:
   60 |     path: /usr/local/nagios/etc/nagios.cfg
   61 |     regexp: 'lock_file=/run/nagios.lock'
   62 |     line: 'lock_file=/usr/local/nagios/var/nagios.lock'
   63 |   become: yes
   64 | 
   65 | - name: Disable Flapping
   66 |   lineinfile:
   67 |     path: /usr/local/nagios/etc/nagios.cfg
   68 |     regexp: 'enable_flap_detection=1'
   69 |     line: 'enable_flap_detection=0'
   70 |   become: yes
   71 | 
   72 | - name: Restart Nagios
   73 |   service:
   74 |     name: nagios
   75 |     state: restarted
   76 |     enabled: yes
   77 |   become: yes
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `ansible/playbooks/nagios/roles/Nagios_Server`; 32 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

ansible/playbooks/nagios/roles/Nagios_Server/README.md
ansible/playbooks/nagios/roles/Nagios_Server/defaults/main.yml
ansible/playbooks/nagios/roles/Nagios_Server/files/commands.cfg
ansible/playbooks/nagios/roles/Nagios_Server/files/contacts.cfg
ansible/playbooks/nagios/roles/Nagios_Server/files/nagios_server_plugins/check_agent
ansible/playbooks/nagios/roles/Nagios_Server/files/nagios_server_plugins/check_inventory
ansible/playbooks/nagios/roles/Nagios_Server/files/nagios_server_plugins/check_nagios_sync
ansible/playbooks/nagios/roles/Nagios_Server/files/nagios_server_plugins/excluded_ips.list
ansible/playbooks/nagios/roles/Nagios_Server/files/nagios_server_plugins/setup_ssh.sh
ansible/playbooks/nagios/roles/Nagios_Server/files/templates.cfg
ansible/playbooks/nagios/roles/Nagios_Server/files/timeperiods.cfg
ansible/playbooks/nagios/roles/Nagios_Server/files/windows.cfg
ansible/playbooks/nagios/roles/Nagios_Server/scripts/commands.cfg
ansible/playbooks/nagios/roles/Nagios_Server/scripts/nagios_host_group_add.sh
ansible/playbooks/nagios/roles/Nagios_Server/scripts/nagios_host_group_remove.sh
ansible/playbooks/nagios/roles/Nagios_Server/scripts/slack_nagios.pl
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_commands.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_contacts.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_core.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_server_crontab.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_server_monitoring.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_templates.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_timeperiods.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/configure_nagios_windows.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/install_nagios_core.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/install_nagios_plugins.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/install_nagios_scripts.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/install_nagiosgraph.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/install_pnp4nagios.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/main.yml
ansible/playbooks/nagios/roles/Nagios_Server/tasks/restart_nagios_server.yml
ansible/playbooks/nagios/roles/Nagios_Server/vars/Ubuntu.yml
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- leaf tasks (not counting block containers): 11 (the rule needs more than 10)
- include/import task or role, or play-level roles, present: no
```

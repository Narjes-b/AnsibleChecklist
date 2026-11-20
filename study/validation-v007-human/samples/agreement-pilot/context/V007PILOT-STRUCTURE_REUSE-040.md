# Frozen source context: V007PILOT-STRUCTURE_REUSE-040

- Repository: `ConnectBox/connectbox-pi`
- Commit: `e69eabdecfa2e39b2751acdb928bfafb2f8f28f6`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/roles/connectbox-pi/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `0afbed1de5e3bb51eae7688b946d4b523ff21b16b9a79b6490f3d5bdafd1611c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–102 of 102:

```text
    1 | ---
    2 | - name: expire chat messages
    3 |   cron:
    4 |     name: expire_chat
    5 |     minute: "0,15,30,45"
    6 |     job: "curl -XDELETE http://127.0.0.1:{{ gunicorn_listen_port }}/chat/messages > /dev/null"
    7 | 
    8 | - name: ensure PxUSBm is running
    9 |   cron:
   10 |     name: PxUSBM test for running
   11 |     day: "*"
   12 |     hour: "*"
   13 |     minute: "*"
   14 |     month: "*"
   15 |     weekday: "*"
   16 |     user: root
   17 |     job:  "python3 /usr/local/connectbox/bin/TestPxUSBm.py > /dev/null"
   18 | 
   19 | - name: install connectbox-access-log-analyzer
   20 |   git:
   21 |     repo: '{{ access_log_analyzer_repo }}'
   22 |     dest: /usr/local/access-log-analyzer
   23 |     version: '{{ access_log_repo_rev }}'
   24 | 
   25 | - name: Make access-log-analyzer etc directory
   26 |   file:
   27 |     state: directory
   28 |     path: /usr/local/access-log-analyzer/etc
   29 |     owner: _connectbox
   30 |     group: _connectbox
   31 |     mode: 0755
   32 | 
   33 | - name: Make access-log-analyzer var directory
   34 |   file:
   35 |     state: directory
   36 |     path: /usr/local/access-log-analyzer/var
   37 |     owner: _connectbox
   38 |     group: _connectbox
   39 |     mode: 0755
   40 | 
   41 | - name: Make access-log-analyzer config overrides
   42 |   template:
   43 |     src: access-log-analyzer.conf.j2
   44 |     dest: /usr/local/access-log-analyzer/etc/access-log-analyzer.conf
   45 |     backup: yes
   46 |     owner: _connectbox
   47 |     group: _connectbox
   48 |     mode: 0644
   49 | 
   50 | #- name: Clean up the Reports Device hostname
   51 | #  command: sed -i 's/ConnectBox/{{ connectbox_pretty_hostname }}/g' /usr/local/access-log-analyzer/published/index.html
   52 | 
   53 | #- name: Clean up the Reports Device hostname 2
   54 | #  command:  sed -i 's/ConnectBox/{{ connectbox_pretty_hostname }}/g' /usr/local/access-log-analyzer/public/index.html
   55 | 
   56 | - name: Make hourly logrotate config
   57 |   template:
   58 |     src: logrotate.hourly.conf.j2
   59 |     dest: /etc/logrotate.hourly.conf
   60 |     backup: yes
   61 |     owner: root
   62 |     group: root
   63 |     mode: 0644
   64 | 
   65 | - name: Configure hourly logrotate for connectbox access logrotate
   66 |   copy:
   67 |     content: "#!/bin/sh\n/usr/sbin/logrotate /etc/logrotate.hourly.conf"
   68 |     dest: "/etc/cron.hourly/logrotate-hourly"
   69 |     mode: 0755
   70 |     owner: root
   71 |     group: root
   72 | 
   73 | # If the system is updated before any iptables modules are loaded
   74 | #  the system can't find the modules and iptables rules can't be
   75 | #  loaded first time. (A repeat ansible run seems to fix it, though).
   76 | # Let's avoid a first-time failure by doing the upgrade after the
   77 | #  iptables rules have been updated.
   78 | # Consistent with: https://serverfault.com/questions/593263/iptables-nat-does-not-exist
   79 | - name: Update existing packages
   80 |   apt:
   81 |     upgrade: safe
   82 |   tags:
   83 |   - full-build-only
   84 | 
   85 | # sshd forks child processes to handle connections, so stopping and disabling
   86 | #  sshd doesn't disconnect the session that's actually doing the stopping and
   87 | #  disabling (or the control session if pipelining is in use)
   88 | - name: Schedule disabling of sshd
   89 |   set_fact:
   90 |     final_command: "systemctl disable ssh"
   91 |   when: not developer_mode
   92 | 
   93 | # Run the final commands in a handler so any disabling is performed right at
   94 | #  the end of the playbook run, to extent that we can influence it. While
   95 | #  handlers are run in the order that they are defined within a role, it's
   96 | #  unclear how handlers are ordered when multiple roles fire handlers.
   97 | #
   98 | # This is a no-op force the handler to run (assuming the conditional passes)
   99 | - name: Trigger final disabling commands if final_command is set
  100 |   command: "true"  # A no-op command that always succeeds
  101 |   when: final_command | length > 0
  102 |   notify: Run final disabling commands
```

## Frozen tracked paths in the relevant role/scope

```text
ansible/roles/connectbox-pi/defaults/main.yml
ansible/roles/connectbox-pi/handlers/main.yml
ansible/roles/connectbox-pi/meta/main.yml
ansible/roles/connectbox-pi/tasks/main.yml
ansible/roles/connectbox-pi/templates/access-log-analyzer.conf.j2
ansible/roles/connectbox-pi/templates/connectbox.conf.j2
ansible/roles/connectbox-pi/templates/logrotate.hourly.conf.j2
```

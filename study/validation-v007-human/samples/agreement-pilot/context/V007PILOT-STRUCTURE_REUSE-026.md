# Frozen source context: V007PILOT-STRUCTURE_REUSE-026

- Repository: `NLNOG/ring-ansible`
- Commit: `b8a7aede6730b3fa3fc3065e187ace979ceedd01`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `playbook.yml` (reported anchor line 1)
- Object: `source_location` `eea96f060edcbba6ac141a23df0509c3ef6cc1d7418b764f982793d9e1dbc028`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–158 of 158:

```text
    1 | - hosts: ringnode
    2 |   tasks:
    3 |     - include_vars: "vault/ringnode.yml"
    4 |   tags:
    5 |     - always
    6 | 
    7 | - hosts: infranode
    8 |   tasks:
    9 |     - include_vars: "{{ item }}"
   10 |       with_first_found:
   11 |         - "vault/{{ inventory_hostname}}.yml"
   12 |         - "vault/infranode.yml"
   13 |   tags:
   14 |     - always
   15 | 
   16 | - import_playbook: ubuntu_upgrade.yml
   17 |   when: '"ringnode" in group_names and ansible_distribution_release != "jammy"'
   18 | 
   19 | - hosts: all
   20 |   become: true
   21 |   become_user: root
   22 |   roles:
   23 |     - { role: apt, tags: apt }
   24 |     - { role: resolving, tags: resolving }
   25 |     - { role: etcfiles, tags: etcfiles }
   26 |     - { role: syslog, tags: syslog }
   27 |     - { role: sysctl, tags: sysctl }
   28 |     - { role: lang, tags: lang }
   29 |     - { role: ansible, tags: ansible }
   30 |     - { role: software, tags: software }
   31 |     - { role: ntp, tags: ntp }
   32 |     - { role: motd, tags: motd }
   33 |     - { role: munin-node, tags: munin-node }
   34 |     - { role: dhcp, tags: dhcp }
   35 |     - { role: fail2ban, tags: fail2ban }
   36 |     - { role: postfix, tags: postfix }
   37 |     - { role: userscripts, tags: userscripts }
   38 |     - { role: adminscripts, tags: adminscripts }
   39 |     - { role: users, class: ring-admins, tags: ring-admins }
   40 |     - { role: users, class: local, tags: local-users }
   41 |     - { role: openssh, tags: openssh }
   42 | 
   43 | - hosts: ringnode:auth.infra.ring.nlnog.net
   44 |   become: true
   45 |   become_user: root
   46 |   roles:
   47 |     - { role: users, class: ring-users, tags: ring-users }
   48 | 
   49 | - hosts: ringnode:~staging[0-9]*\.ring\.nlnog\.net
   50 |   become: true
   51 |   become_user: root
   52 |   roles:
   53 |     - { role: nginx, tags: nginx }
   54 |     - { role: ring_health, tags: ring_health }
   55 |     - { role: scamper, tags: scamper }
   56 |     - { role: ripe-atlas, tags: ripe-atlas }
   57 |     - { role: ring_sqa, tags: ring_sqa }
   58 | 
   59 | - hosts: infranode
   60 |   become: true
   61 |   become_user: root
   62 |   roles:
   63 |     - { role: nftables, tags: nftables }
   64 |     - { role: backup-client, tags: backup-client }
   65 | 
   66 | - hosts: ~container[0-9]*\.infra\.ring\.nlnog.net
   67 |   become: true
   68 |   become_user: root
   69 |   roles:
   70 |     - { role: container, tags: container }
   71 | 
   72 | - hosts: compute01.infra.ring.nlnog.net
   73 |   become: true
   74 |   become_user: root
   75 |   roles:
   76 |     - { role: apache2, tags: apache2 }
   77 |     - { role: munin-master, tags: munin-master }
   78 | 
   79 | - hosts: lg02.infra.ring.nlnog.net
   80 |   become: true
   81 |   become_user: root
   82 |   roles:
   83 |     - { role: ansible, tags: ansible, mitogen: no }
   84 |     - { role: openbgpd, tags: openbgpd }
   85 | 
   86 | - hosts: public02.infra.ring.nlnog.net
   87 |   become: true
   88 |   become_user: root
   89 |   roles:
   90 |     - { role: haproxy, profile: relay, tags: haproxy }
   91 |     - { role: inframail, tags: inframail }
   92 | 
   93 | - hosts: public03.infra.ring.nlnog.net
   94 |   become: true
   95 |   become_user: root
   96 |   roles:
   97 |     - { role: letsencrypt, tags: letsencrypt }
   98 |     - { role: mysql, tags: mysql }
   99 |     - { role: apache2, tags: apache2 }
  100 |     - { role: pdns-server, tags: pdns-server }
  101 |     - { role: map, tags: map }
  102 |     - { role: apt-repository, tags: apt-repository }
  103 | 
  104 | - hosts: public04.infra.ring.nlnog.net
  105 |   become: true
  106 |   become_user: root
  107 |   roles:
  108 |     - { role: letsencrypt, tags: letsencrypt }
  109 |     - { role: mysql, tags: mysql }
  110 |     - { role: apache2, tags: apache2 }
  111 |     - { role: hugo, tags: hugo }
  112 |     - { role: paster, tags: paster }
  113 | 
  114 | - hosts: public05.infra.ring.nlnog.net
  115 |   become: true
  116 |   become_user: root
  117 |   roles:
  118 |     - { role: letsencrypt, tags: letsencrypt }
  119 |     - { role: apache2, tags: apache2 }
  120 |     - { role: nlnog-lg, tags: nlnog-lg }
  121 | 
  122 | - hosts: backup.infra.ring.nlnog.net:storage01.infra.ring.nlnog.net
  123 |   become: true
  124 |   become_user: root
  125 |   roles:
  126 |     - { role: backup-server, tags: backup-server }
  127 | 
  128 | - hosts: auth.infra.ring.nlnog.net
  129 |   become: true
  130 |   become_user: root
  131 |   roles:
  132 |     - { role: ring_auth, tags: ring_auth }
  133 | 
  134 | - hosts: dbmaster.infra.ring.nlnog.net
  135 |   become: true
  136 |   become_user: root
  137 |   roles:
  138 |     - { role: letsencrypt, tags: letsencrypt }
  139 |     - { role: mysql, tags: mysql }
  140 |     - { role: apache2, tags: apache2 }
  141 |     - { role: ring_api, tags: ring_api }
  142 | 
  143 | - hosts: dbbackup.infra.ring.nlnog.net
  144 |   become: true
  145 |   become_user: root
  146 |   roles:
  147 |     - { role: letsencrypt, tags: letsencrypt }
  148 |     - { role: mysql, tags: mysql }
  149 |     - { role: apache2, tags: apache2 }
  150 |     - { role: ring_api, tags: ring_api }
  151 | 
  152 | - hosts: sqa-collector.infra.ring.nlnog.net
  153 |   become: true
  154 |   become_user: root
  155 |   roles:
  156 |     - { role: mysql, tags: mysql }
  157 |     - { role: apache2, tags: apache2 }
  158 |     - { role: sqa-collector, tags: sqa-collector }
```

## Frozen tracked paths in the relevant role/scope

```text
.github/workflows/yamllint.yml
.gitignore
filter_plugins/determrand.py
group_vars/all.yml
group_vars/infranode.yml
group_vars/ringnode.yml
host_vars/amazon10.ring.nlnog.net
host_vars/amazon17.ring.nlnog.net
host_vars/auth.infra.ring.nlnog.net
host_vars/backup.infra.ring.nlnog.net
host_vars/compute01.infra.ring.nlnog.net
host_vars/dbbackup.infra.ring.nlnog.net
host_vars/dbmaster.infra.ring.nlnog.net
host_vars/grifon01.ring.nlnog.net
host_vars/keklolwtf01.ring.nlnog.net
host_vars/lg02.infra.ring.nlnog.net
host_vars/public02.infra.ring.nlnog.net
host_vars/public03.infra.ring.nlnog.net
host_vars/public04.infra.ring.nlnog.net
host_vars/public05.infra.ring.nlnog.net
host_vars/quanza01.ring.nlnog.net
host_vars/sqa-collector.infra.ring.nlnog.net
host_vars/staging01.ring.nlnog.net
host_vars/staging02.ring.nlnog.net
host_vars/storage01.infra.ring.nlnog.net
nodes
nodes.active
open-the-vault.sh
playbook.yml
provision-ring-user.yml
provision-vault-pass.yml
provision.yml
roles/adminscripts/defaults/main.yml
roles/adminscripts/files/geotrshell
roles/adminscripts/files/intraceshell
roles/adminscripts/files/ring-admin
roles/adminscripts/files/ring-fetch-nodes-json
roles/adminscripts/files/ring-pdns
roles/adminscripts/tasks/dbmaster.yml
roles/adminscripts/tasks/main.yml
roles/adminscripts/tasks/pdnsmaster.yml
roles/adminscripts/templates/cron.d/node_down_deactivation.j2
roles/adminscripts/templates/cron.d/node_down_reminders.j2
roles/adminscripts/templates/cron.d/regenerate-txt.j2
roles/adminscripts/templates/cron.d/ring-fetch-nodes-json.j2
roles/adminscripts/templates/cron.d/ssh_keyscan.j2
roles/adminscripts/templates/cron.d/update-sshfp.j2
roles/ansible/defaults/main.yml
roles/ansible/files/ansible-reaper
roles/ansible/files/ansible.cfg
roles/ansible/files/ansible_mitogen.cfg
roles/ansible/files/mitogen_remove
roles/ansible/tasks/main.yml
roles/ansible/tasks/master.yml
roles/ansible/templates/ansible-cron.j2
roles/ansible/templates/ansible-distupgrade.j2
roles/ansible/templates/ansible.pref.j2
roles/ansible/templates/cron.d/ansible.j2
roles/ansible/templates/cron.d/ansible_master.j2
roles/ansible/templates/cron.d/ansible_virtualenv.j2
roles/ansible/templates/ring_callback.py.j2
roles/ansible/templates/run-ansible.j2
roles/ansible/vars/main.yml
roles/apache2/files/apache2.conf
roles/apache2/files/api-vhost.conf
roles/apache2/files/api4-vhost.conf
roles/apache2/files/api6-vhost.conf
roles/apache2/files/apt-vhost.conf
roles/apache2/files/lg-vhost.conf
roles/apache2/files/lg02.infra-vhost.conf
roles/apache2/files/map-vhost.conf
roles/apache2/files/paste-vhost.conf
roles/apache2/files/sqa-collector-vhost.conf
roles/apache2/files/webdev-vhost.conf
roles/apache2/files/www-vhost.conf
roles/apache2/handlers/main.yml
roles/apache2/tasks/main.yml
roles/apache2/templates/wsgi_daemons.conf.j2
roles/apt-repository/files/deb2repo
roles/apt-repository/files/distributions
roles/apt-repository/meta/main.yml
roles/apt-repository/tasks/main.yml
roles/apt-repository/templates/priv.key.j2
roles/apt/files/10periodic
roles/apt/files/50unattended-upgrades
roles/apt/files/apt-daily-upgrade.timer
roles/apt/files/sources.list
roles/apt/handlers/main.yml
roles/apt/tasks/main.yml
roles/backup-client/files/validate-rsync-backup
roles/backup-client/tasks/main.yml
roles/backup-server/files/check-backup-age
roles/backup-server/files/cron.d/ring_backup
roles/backup-server/files/start-backup
roles/backup-server/files/systemd/zrbackup.service
roles/backup-server/files/zfs_health_check
roles/backup-server/files/zrbackup
roles/backup-server/handlers/main.yml
roles/backup-server/tasks/main.yml
roles/backup-server/templates/backup-hosts.j2
roles/container/tasks/main.yml
roles/dhcp/defaults/main.yml
roles/dhcp/files/dhclient.conf
roles/dhcp/tasks/main.yml
roles/etcfiles/files/adduser.conf
roles/etcfiles/files/bash.bashrc
roles/etcfiles/files/blacklist-ring.conf
roles/etcfiles/files/fstrim
roles/etcfiles/files/hostnamed_override.conf
roles/etcfiles/files/pam_atd
roles/etcfiles/files/pam_common-auth
roles/etcfiles/files/pam_cron
roles/etcfiles/files/pam_login
roles/etcfiles/files/pam_sshd
roles/etcfiles/files/pam_su
roles/etcfiles/files/smartd.conf
roles/etcfiles/files/ssh_known_hosts
roles/etcfiles/files/timezone
roles/etcfiles/files/upstart-job
roles/etcfiles/handlers/main.yml
[listing truncated after 120 paths]
```

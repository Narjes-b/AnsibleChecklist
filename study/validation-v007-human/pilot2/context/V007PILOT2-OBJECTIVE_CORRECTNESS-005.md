# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-005

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: objective_correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `onecloud/roles/mariadb-ha/tasks/keepalived.yml` (reported anchor line 3)
- Flagged construct: task `modify sysctl.conf`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–40 of 40:

```text
    1 | ---
    2 | - name: modify sysctl.conf
    3 |   sysctl:
    4 |     name: "{{ item.name }}"
    5 |     value: "{{ item.value }}"
    6 |   loop:
    7 |     - name: net.ipv4.ip_forward
    8 |       value: 1
    9 |     - name: net.ipv4.ip_nonlocal_bind
   10 |       value: 1
   11 |     
   12 | - name: install keepalived
   13 |   package:
   14 |     name: keepalived
   15 |     state: present
   16 | 
   17 | - name: copy keepalived config
   18 |   template:
   19 |     dest: /etc/keepalived/keepalived.conf
   20 |     src: keepalived.conf.j2
   21 |     backup: yes
   22 |   register: conf_status
   23 | 
   24 | - name: Copy check_interface scripts
   25 |   template:
   26 |     dest: /etc/keepalived/check_interface.sh
   27 |     src: check_interface.sh.j2
   28 |     mode: '0755'
   29 | 
   30 | - name: start keepalived
   31 |   systemd:
   32 |     name: keepalived
   33 |     state: started
   34 |     enabled: yes
   35 | 
   36 | - name: restart keepalived if config changed
   37 |   systemd:
   38 |     name: keepalived
   39 |     state: restarted
   40 |   when: conf_status is changed
```

# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-007

- Repository: `cfpb/aurora`
- Commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Family: Objective correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `deploy/roles/iptables/tasks/main.yml` (reported anchor line 17)
- Object: `source_location` `f58fd85d19a78400bdb56fd271cd8b63587964c55e49ff6ddf2b3590036f2196`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–89 of 89:

```text
    1 | # main.yml - Establishes baseline IP Tables rules
    2 | 
    3 | # Basically, allows outgoing trafic and established connections,
    4 | # but blocks all incoming traffic except SSH.  This is meant to be replaced
    5 | # by more complex rules.
    6 | 
    7 | ---
    8 | - import_tasks: rhel_7.yml
    9 |   when: ansible_distribution_major_version == "7"
   10 | 
   11 | - name: Temporarily allow all
   12 |   command: "iptables -P INPUT ACCEPT"
   13 | 
   14 | - name: Flush existing rules
   15 |   command: "iptables -F"
   16 | 
   17 | - name: Create logging iptables_chain
   18 |   command: "iptables -N LOGDROP"
   19 |   ignore_errors: yes
   20 | 
   21 | - name: Create custom chain
   22 |   command: "iptables -N {{ iptables_chain }}"
   23 |   ignore_errors: yes
   24 | 
   25 | - name: Send INPUT to custom chain
   26 |   command: "iptables -A INPUT -j {{ iptables_chain }}"
   27 | 
   28 | - name: Send FORWARD to custom chain
   29 |   command: "iptables -A FORWARD -j {{ iptables_chain }}"
   30 | 
   31 | - name: Setup TCP logging
   32 |   command: "iptables -A LOGDROP -p tcp -m limit --limit 2/min --limit-burst 10 -j LOG --log-prefix 'TCP LOGDROP: ' --log-level 4"
   33 | 
   34 | - name: Setup UDP logging
   35 |   command: "iptables -A LOGDROP -p udp -m limit --limit 2/min --limit-burst 10 -j LOG --log-prefix 'UDP LOGDROP: ' --log-level 4"
   36 | 
   37 | - name: Setup ICMP logging
   38 |   command: "iptables -A LOGDROP -p icmp -m limit --limit 2/min --limit-burst 10 -j LOG --log-prefix 'ICMP LOGDROP: ' --log-level 4"
   39 | 
   40 | - name: Setup Fragment logging
   41 |   command: "iptables -A LOGDROP -f -p all -m limit --limit 2/min --limit-burst 10 -j LOG --log-prefix 'FRAGMENT LOGDROP: ' --log-level 4"
   42 | 
   43 | - name: Drop after logging
   44 |   command: "iptables -A LOGDROP -p all -j DROP"
   45 | 
   46 | - name: Allow localhost
   47 |   command: "iptables -A {{ iptables_chain }} -i lo -j ACCEPT"
   48 | 
   49 | - name: Allow ICMP type 255
   50 |   command: "iptables -A {{ iptables_chain }} -p icmp -m icmp --icmp-type 255 -j ACCEPT"
   51 | 
   52 | - name: Allow established and related
   53 |   command: "iptables -A {{ iptables_chain }} -m state --state ESTABLISHED,RELATED -j ACCEPT"
   54 | 
   55 | - name: Allow each port listed in iptables_common group variable
   56 |   command: "iptables -A {{ iptables_chain }}{% if 'state' in item %} -m state --state {{ item.state }}{% endif %} -p {{ item.protocol }} -m {{ item.protocol }}{% if 'port' in item %} --dport {{ item.port }}{% endif %}{% if 'extra' in item %} {{ item.extra }}{% endif %}{% if 'source' in item %} -s {{ item.source }}{% endif %} -j ACCEPT"
   57 |   with_items: "{{ iptables_standard }}"
   58 | 
   59 | - name: Allow ssh access from "Terminals"
   60 |   command: "iptables -A {{ iptables_chain }} -m state --state NEW -p tcp -m tcp --dport 22 -s {{ hostvars[item]['ansible_ssh_host'] }} -j ACCEPT"
   61 |   with_items: "{{ groups['terminals']|default(omit) }}"
   62 |   when: '"terminals" in groups'
   63 | 
   64 | - name: Allow SSH access from internal subnet
   65 |   command: "iptables -A {{ iptables_chain }} -m state --state NEW -p tcp -m tcp --dport 22 -s {{ subnet }} -j ACCEPT"
   66 |   become: yes
   67 |   become_method: sudo
   68 |   when: iptables_config and is_terminal and deploy_iptables
   69 | 
   70 | - name: LOGDROP all others
   71 |   command: "iptables -A {{ iptables_chain }} -p all -j LOGDROP"
   72 | 
   73 | - name: Set INPUT policy to DROP
   74 |   command: "iptables -P INPUT DROP"
   75 | 
   76 | - name: Set FORWARD policy to DROP
   77 |   command: "iptables -P FORWARD DROP"
   78 | 
   79 | - name: Allow outgoing
   80 |   command: "iptables -P OUTPUT ACCEPT"
   81 | 
   82 | # We need initscripts so we can call /sbin/service in the next task
   83 | - name: Ensure initscripts is installed
   84 |   command:
   85 |     cmd: yum -y install initscripts
   86 |     creates: /sbin/service
   87 | 
   88 | - name: Save new rules
   89 |   command: "/sbin/service iptables save"
```

# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-001

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: objective_correctness
- Rule: `ansibleguard/invalid-task-attribute-type`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/cockpit/tasks/deploy.yml` (reported anchor line 3)
- Flagged construct: attribute `gather_facts`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–93 of 93:

```text
    1 | ---
    2 | # tasks file for cockpit
    3 | - name: gather facts
    4 |   gather_facts:
    5 | 
    6 | - name: Gather package facts
    7 |   package_facts:
    8 |     manager: auto
    9 | 
   10 | - name: Gather service facts
   11 |   service_facts:
   12 | 
   13 | - name: Install cockpit
   14 |   block:
   15 |   - name: Ensure cockpit packages exist
   16 |     package:
   17 |       name: "{{ item }}"
   18 |       state: latest
   19 |     with_items:
   20 |     - cockpit
   21 |     - cockpit-dashboard
   22 |     - cockpit-shell
   23 |     - cockpit-system
   24 |     - cockpit-ws
   25 |     - subscription-manager-cockpit
   26 | 
   27 |   - name: Add extra packages when on RHEL 8 (with podman)
   28 |     package:
   29 |       name: "{{ item }}"
   30 |       state: latest
   31 |     with_items:
   32 |     - cockpit-composer
   33 |     - cockpit-session-recording
   34 |     - cockpit-machines
   35 |     - cockpit-packagekit
   36 |     - cockpit-podman
   37 |     - cockpit-storaged
   38 |     when: ansible_distribution == 'RedHat' and ansible_distribution_major_version == '8' and podman_install == true
   39 | 
   40 |   - name: Add extra packages when on RHEL 8 (without podman)
   41 |     package:
   42 |       name: "{{ item }}"
   43 |       state: latest
   44 |     with_items:
   45 |     - cockpit-composer
   46 |     - cockpit-session-recording
   47 |     - cockpit-machines
   48 |     - cockpit-packagekit
   49 |     - cockpit-storaged
   50 |     when: ansible_distribution == 'RedHat' and ansible_distribution_major_version == '8' and podman_install == false
   51 | 
   52 | - when: ansible_facts.packages["firewalld"] is defined
   53 |   block:
   54 | 
   55 |   - name: open cockpit port in firewalld (permanent)
   56 |     ansible.posix.firewalld:
   57 |       service: "cockpit"
   58 |       state: enabled
   59 |       permanent: yes
   60 | 
   61 |   - name: open cockpit port in firewalld (immediate)
   62 |     ansible.posix.firewalld:
   63 |       service: "cockpit"
   64 |       state: enabled
   65 |       immediate: yes
   66 |     when: ansible_facts.services["firewalld.service"].state == "running"
   67 | 
   68 | - when: ansible_facts.packages["firewalld"] is undefined
   69 |   block:
   70 | 
   71 |   - name: open cockpit port in iptables
   72 |     iptables:
   73 |       chain: INPUT
   74 |       protocol: tcp
   75 |       destination_port: 9090
   76 |       jump: ACCEPT
   77 |     when: ansible_facts.packages["iptables"] is defined
   78 | 
   79 | - name: Ensure pmlogger is started (for cockpit-pcp)
   80 |   systemd:
   81 |     name: "pmlogger.service"
   82 |     state: "started"
   83 |     enabled: true
   84 |   when: ansible_facts.services["pmlogger.service"] is defined
   85 | 
   86 | - name: Ensure cockpit is started
   87 |   systemd:
   88 |     name: "cockpit.socket"
   89 |     state: "started"
   90 |     enabled: true
   91 |     daemon_reload: true
   92 | 
   93 | ...
```

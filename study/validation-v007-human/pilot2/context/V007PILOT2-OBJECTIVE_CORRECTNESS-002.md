# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-002

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: objective_correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/sno_node_prep/tasks/60_enabled_services.yml` (reported anchor line 2)
- Flagged construct: not named by the finding; the anchor line 2 lies in the task at line 2, name `Enable and restart Services`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–35 of 35:

```text
    1 | ---
    2 | - name: "Enable and restart Services"
    3 |   ansible.builtin.service:
    4 |     name: "{{ item }}"
    5 |     state: restarted
    6 |     enabled: true
    7 |   become: true
    8 |   with_items:
    9 |     - libvirtd
   10 |   when:
   11 |     - sno_install_type | default("virtual") == "virtual"
   12 |   tags: services
   13 | 
   14 | - name: "Enable Services (iptables)"
   15 |   ansible.builtin.service:
   16 |     name: "{{ item }}"
   17 |     state: restarted
   18 |     enabled: true
   19 |   become: true
   20 |   with_items:
   21 |     - "{{ firewall }}"
   22 |   when: firewall == "iptables"
   23 |   tags: services
   24 | 
   25 | - name: "Enable Services (firewalld)"
   26 |   ansible.builtin.service:
   27 |     name: "{{ item }}"
   28 |     state: started
   29 |     enabled: true
   30 |   become: true
   31 |   with_items:
   32 |     - "{{ firewall }}"
   33 |   when: firewall != "iptables"
   34 |   tags: services
   35 | ...
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-032

- Repository: `IAreKyleW00t/k2net`
- Commit: `63cf522a122691ae38ec90146c10a6d332231d00`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `ansible/roles/k3s/tasks/setup/agent.yaml` (reported anchor line 2)
- Object: `task` `badf973d5a93a938a78856480ecaa194beac4b561aec7953aa98f0cb2b0bd191`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–26 of 26:

```text
    1 | ---
    2 | - name: Setup | Agent
    3 |   block:
    4 |     - name: Setup | Agent | Download {{ k3s_version }} k3s install script
    5 |       ansible.builtin.get_url:
    6 |         url: https://get.k3s.io
    7 |         dest: /tmp/k3s-install.sh
    8 |         owner: root
    9 |         group: root
   10 |         mode: "0755"
   11 | 
   12 |     - name: Setup | Agent | Run k3s install script
   13 |       ansible.builtin.shell: |
   14 |         INSTALL_K3S_SKIP_START=true INSTALL_K3S_VERSION={{ k3s_version }} K3S_URL={{ k3s_url }} K3S_TOKEN={{ k3s_token }} sh /tmp/k3s-install.sh {{ k3s_node_type }} {{ k3s_agent_args | join(' ') }}
   15 |       notify:
   16 |         - Start k3s service
   17 | 
   18 |     - name: Setup | Agent | Delete old k3s intsall script
   19 |       ansible.builtin.file:
   20 |         path: /tmp/k3s-install.sh
   21 |         state: absent
   22 |   become: true
   23 |   tags:
   24 |     - agent
   25 |     - setup
   26 |     - k3s
```

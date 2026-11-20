# Frozen source context: V007PILOT-SECURITY-001

- Repository: `ric03uec/clawrium`
- Commit: `77274d5ca3d71b5a057df332482dd678446d9544`
- Family: Security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `src/clawrium/platform/registry/ethos/playbooks/memory_info.yaml` (reported anchor line 6)
- Object: `source_location` `58a2855f1a0ab304d764efa8d9f79a96d3686c10952b539130dab72fe08fdfdf`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–44 of 44:

```text
    1 | ---
    2 | # Ethos memory model:
    3 | #   - MEMORY.md  (agent notes, ≤ 2200 chars) → ~/.ethos/personalities/default/
    4 | #   - USER.md    (user profile, ≤ 1375 chars) → ~/.ethos/personalities/default/
    5 | #   - SOUL.md    (agent identity, ≤ 3000 chars) → ~/.ethos/personalities/default/
    6 | - hosts: all
    7 |   become: yes
    8 |   gather_facts: false
    9 |   vars:
   10 |     memory_top_level_files:
   11 |       - { name: "MEMORY.md", path: "/home/{{ agent_name }}/.ethos/personalities/default/MEMORY.md" }
   12 |       - { name: "USER.md", path: "/home/{{ agent_name }}/.ethos/personalities/default/USER.md" }
   13 |       - { name: "SOUL.md", path: "/home/{{ agent_name }}/.ethos/personalities/default/SOUL.md" }
   14 |   tasks:
   15 |     - name: Validate agent_name (defense-in-depth)
   16 |       ansible.builtin.fail:
   17 |         msg: "Invalid agent_name"
   18 |       when:
   19 |         - agent_name is not match('^[a-z][a-z0-9_-]{0,31}$')
   20 | 
   21 |     - name: Set workspace path
   22 |       ansible.builtin.set_fact:
   23 |         memory_workspace_path: "/home/{{ agent_name }}/.ethos/personalities/default"
   24 | 
   25 |     - name: Stat memory files
   26 |       ansible.builtin.stat:
   27 |         path: "{{ item.path }}"
   28 |       register: top_level_stats
   29 |       loop: "{{ memory_top_level_files }}"
   30 |       loop_control:
   31 |         label: "{{ item.name }}"
   32 | 
   33 |     - name: Emit workspace path
   34 |       ansible.builtin.debug:
   35 |         msg: "WORKSPACE_PATH={{ memory_workspace_path }}"
   36 | 
   37 |     - name: Emit top-level file stats
   38 |       ansible.builtin.debug:
   39 |         msg: >-
   40 |           TOP {{ item.item.name }}
   41 |           {{ (item.stat.size | default(-1)) if item.stat.exists else -1 }}
   42 |       loop: "{{ top_level_stats.results }}"
   43 |       loop_control:
   44 |         label: "{{ item.item.name }}"
```

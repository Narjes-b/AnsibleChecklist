# Frozen source context: V007PILOT-STYLE_POLICY-050

- Repository: `ric03uec/clawrium`
- Commit: `77274d5ca3d71b5a057df332482dd678446d9544`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `src/clawrium/platform/registry/openclaw/playbooks/logs.yaml` (reported anchor line 4)
- Object: `source_location` `ee4281b05e2adb234621ca513790863397d6bd26bb6eefe862fece1e9df2d9b3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–48 of 48:

```text
    1 | ---
    2 | # Phase 3 of #11 (#945): read-only log retrieval from the NemoClaw
    3 | # sandbox backing an openclaw agent.
    4 | - hosts: all
    5 |   become: yes
    6 |   vars:
    7 |     nemoclaw_binary: "/usr/local/bin/nemoclaw"
    8 |   tasks:
    9 |     - name: Refuse to run on non-Linux hosts (dispatcher contract)
   10 |       ansible.builtin.fail:
   11 |         msg: logs.yaml invoked against non-Linux host for NemoClaw-backed openclaw
   12 |       when: ansible_os_family == "Darwin"
   13 | 
   14 |     - name: Assert sandbox_name extravar is provided
   15 |       ansible.builtin.assert:
   16 |         that:
   17 |           - sandbox_name is defined
   18 |           - sandbox_name | length > 0
   19 |         fail_msg: >-
   20 |           `sandbox_name` extravar is required for NemoClaw-backed
   21 |           openclaw logs. This is a legacy bare record; remove +
   22 |           re-create the agent per docs/releases/26.7.3/CHANGELOG.md.
   23 | 
   24 |     - name: Assert nemoclaw binary is present on host
   25 |       ansible.builtin.stat:
   26 |         path: "{{ nemoclaw_binary }}"
   27 |       register: nemoclaw_stat
   28 | 
   29 |     - name: Fail if nemoclaw binary is missing
   30 |       ansible.builtin.fail:
   31 |         msg: >-
   32 |           nemoclaw binary not found at {{ nemoclaw_binary }}. Re-run
   33 |           `clawctl host prepare <host>` before reading openclaw logs.
   34 |       when: not nemoclaw_stat.stat.exists
   35 | 
   36 |     - name: Read NemoClaw sandbox {{ sandbox_name }} logs
   37 |       ansible.builtin.command:
   38 |         argv:
   39 |           - "{{ nemoclaw_binary }}"
   40 |           - logs
   41 |           - "{{ sandbox_name }}"
   42 |       register: nemoclaw_logs_result
   43 |       changed_when: false
   44 |       failed_when: nemoclaw_logs_result.rc != 0
   45 | 
   46 |     - name: Display NemoClaw sandbox logs
   47 |       ansible.builtin.debug:
   48 |         msg: "{{ nemoclaw_logs_result.stdout }}"
```

# Frozen source context: V007PILOT2-SECURITY-014

- Repository: `ric03uec/clawrium`
- Commit: `77274d5ca3d71b5a057df332482dd678446d9544`
- Family: security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `src/clawrium/platform/registry/openclaw/playbooks/remove.yaml` (reported anchor line 2)
- Flagged construct: not named by the finding; the anchor line 2 lies in the task at line 2, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–148 of 148:

```text
    1 | ---
    2 | - hosts: all
    3 |   become: yes
    4 |   become_method: sudo
    5 |   vars:
    6 |     nemoclaw_binary: "/usr/local/bin/nemoclaw"
    7 |   tasks:
    8 |     # Phase 3 of #11 (issue #945): tear down the NemoClaw sandbox
    9 |     # BEFORE uninstalling the host-side openclaw bits. `sandbox_name`
   10 |     # is threaded in by `_run_lifecycle_playbook` for every openclaw
   11 |     # op (see `core/lifecycle.py`). Legacy bare records predating
   12 |     # Phase 3 have no `sandbox_name` — for `remove` we tolerate the
   13 |     # missing var and skip the sandbox teardown, then proceed with
   14 |     # host-side residue cleanup so the migration workflow completes
   15 |     # (ATX iter-1 B1). Missing nemoclaw binary (never installed) is
   16 |     # a fast-skip, not a failure, so `remove` still succeeds against
   17 |     # a half-installed host.
   18 |     - name: Note legacy bare record (no sandbox_name)
   19 |       ansible.builtin.debug:
   20 |         msg: >-
   21 |           openclaw remove: no sandbox_name in hosts.json config.
   22 |           This is a legacy bare openclaw record predating Phase 3
   23 |           of #11 (issue #945). Skipping NemoClaw sandbox teardown
   24 |           and proceeding with host-side cleanup. See
   25 |           docs/releases/26.7.3/CHANGELOG.md for migration steps to
   26 |           re-create this agent on the NemoClaw substrate.
   27 |       when: sandbox_name is not defined or (sandbox_name | length) == 0
   28 | 
   29 |     - name: Check nemoclaw binary is present
   30 |       ansible.builtin.stat:
   31 |         path: "{{ nemoclaw_binary }}"
   32 |       register: nemoclaw_stat
   33 | 
   34 |     - name: Destroy NemoClaw sandbox {{ sandbox_name | default('') }}
   35 |       ansible.builtin.command:
   36 |         argv:
   37 |           - "{{ nemoclaw_binary }}"
   38 |           - destroy
   39 |           - "{{ sandbox_name }}"
   40 |       register: nemoclaw_destroy_result
   41 |       # ATX iter-2 W1: fail-open on the destroy task. The primary
   42 |       # goal of `remove` is that the operator can always evict the
   43 |       # agent — a stubborn destroy MUST NOT block host-side residue
   44 |       # cleanup or hosts.json eviction. nemoclaw's exit-code/stderr
   45 |       # contract for "sandbox not found" is not stable at this pin;
   46 |       # once upstream stabilizes, tighten to `failed_when: rc not in
   47 |       # [0, <not-found-rc>]` so a real destroy failure surfaces
   48 |       # again. Failures are still visible in the ansible log via
   49 |       # `register: nemoclaw_destroy_result`.
   50 |       changed_when: nemoclaw_destroy_result.rc == 0
   51 |       failed_when: false
   52 |       when:
   53 |         - nemoclaw_stat.stat.exists
   54 |         - sandbox_name is defined
   55 |         - (sandbox_name | length) > 0
   56 | 
   57 |     - name: Warn when NemoClaw destroy returned non-zero
   58 |       ansible.builtin.debug:
   59 |         msg: >-
   60 |           nemoclaw destroy exited non-zero (rc={{ nemoclaw_destroy_result.rc }}).
   61 |           Continuing with host-side cleanup — inspect stderr in the ansible
   62 |           log if the sandbox still exists on the host:
   63 |           {{ nemoclaw_destroy_result.stderr | default('') }}
   64 |       when:
   65 |         - nemoclaw_destroy_result is defined
   66 |         - nemoclaw_destroy_result.rc is defined
   67 |         - nemoclaw_destroy_result.rc != 0
   68 | 
   69 |     - name: Check if systemd service exists
   70 |       ansible.builtin.stat:
   71 |         path: "/etc/systemd/system/{{ agent_type }}-{{ agent_name }}.service"
   72 |       register: service_file
   73 | 
   74 |     - name: Stop openclaw service if running
   75 |       ansible.builtin.systemd:
   76 |         name: "{{ agent_type }}-{{ agent_name }}"
   77 |         state: stopped
   78 |       when: service_file.stat.exists
   79 |       ignore_errors: yes
   80 | 
   81 |     - name: Disable openclaw service
   82 |       ansible.builtin.systemd:
   83 |         name: "{{ agent_type }}-{{ agent_name }}"
   84 |         enabled: no
   85 |       when: service_file.stat.exists
   86 |       ignore_errors: yes
   87 | 
   88 |     - name: Remove systemd service file
   89 |       ansible.builtin.file:
   90 |         path: "/etc/systemd/system/{{ agent_type }}-{{ agent_name }}.service"
   91 |         state: absent
   92 |       notify: Reload systemd
   93 | 
   94 |     - name: Check if openclaw installation exists
   95 |       ansible.builtin.stat:
   96 |         path: "/home/{{ agent_name }}/openclaw"
   97 |       register: install_dir
   98 | 
   99 |     - name: Remove openclaw installation directory
  100 |       ansible.builtin.file:
  101 |         path: "/home/{{ agent_name }}/openclaw"
  102 |         state: absent
  103 |       when: install_dir.stat.exists
  104 | 
  105 |     - name: Check if openclaw runtime prefix exists
  106 |       ansible.builtin.stat:
  107 |         path: "/home/{{ agent_name }}/.openclaw"
  108 |       register: runtime_prefix_dir
  109 | 
  110 |     - name: Remove openclaw runtime prefix
  111 |       ansible.builtin.file:
  112 |         path: "/home/{{ agent_name }}/.openclaw"
  113 |         state: absent
  114 |       when: runtime_prefix_dir.stat.exists
  115 | 
  116 |     - name: Check if workspace directory exists
  117 |       ansible.builtin.stat:
  118 |         path: "/home/{{ agent_name }}/workspace"
  119 |       register: workspace_dir
  120 | 
  121 |     - name: Remove workspace directory
  122 |       ansible.builtin.file:
  123 |         path: "/home/{{ agent_name }}/workspace"
  124 |         state: absent
  125 |       when: workspace_dir.stat.exists
  126 | 
  127 |     - name: Check if agent user exists
  128 |       ansible.builtin.getent:
  129 |         database: passwd
  130 |         key: "{{ agent_name }}"
  131 |       register: user_check
  132 |       ignore_errors: yes
  133 | 
  134 |     - name: Remove agent user account
  135 |       ansible.builtin.user:
  136 |         name: "{{ agent_name }}"
  137 |         state: absent
  138 |         remove: yes
  139 |       when: user_check is not failed
  140 | 
  141 |     - name: Display success message
  142 |       ansible.builtin.debug:
  143 |         msg: "OpenClaw removed successfully"
  144 | 
  145 |   handlers:
  146 |     - name: Reload systemd
  147 |       ansible.builtin.systemd:
  148 |         daemon_reload: yes
```

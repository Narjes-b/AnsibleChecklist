# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-008

- Repository: `ric03uec/clawrium`
- Commit: `77274d5ca3d71b5a057df332482dd678446d9544`
- Family: maintainability_complexity
- Rule: `ansibleguard/large-playbook`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `src/clawrium/platform/registry/hermes/playbooks/skills_apply.yaml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`src/clawrium/platform/registry/hermes/playbooks/skills_apply.yaml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–169 of 169:

```text
    1 | ---
    2 | # Hermes skills_apply — reconciles ~/.hermes/skills/clawrium/ with the
    3 | # clawrium desired state for one agent.
    4 | #
    5 | # Inputs (extravars):
    6 | #   - agent_name:           unix user that owns the hermes install
    7 | #   - staging_dir:          control-machine path with one
    8 | #                           `<name>/SKILL.md` per desired skill
    9 | #   - desired_skill_names:  list of slug names currently in desired state
   10 | #                           (empty list = uninstall everything we own)
   11 | #
   12 | # Invariants:
   13 | #   - Only ever reads/writes under ~/.hermes/skills/clawrium/. Other
   14 | #     directories under ~/.hermes/skills/ (upstream bundled skills,
   15 | #     user-authored skills, other categories) are never touched.
   16 | #   - Every install is idempotent: re-running with the same state is a
   17 | #     no-op aside from `changed` flags on files whose content drifted on
   18 | #     the remote.
   19 | #   - The hermes daemon may concurrently read SKILL.md files. Writes
   20 | #     stage to a tempfile in the dest dir and rename atomically (this is
   21 | #     `ansible.builtin.copy`'s default), so a concurrent reader sees
   22 | #     either the old or new content, never a partial write.
   23 | - hosts: all
   24 |   become: yes
   25 |   gather_facts: false
   26 |   vars:
   27 |     skills_root: "/home/{{ agent_name }}/.hermes/skills/clawrium"
   28 |   tasks:
   29 |     # ----------------------- input validation (runs FIRST) ------------------
   30 |     # Python core/skills.py + core/skills_state.py already validate
   31 |     # `agent_name` and every entry in `desired_skill_names` before they
   32 |     # are placed into the inventory, but the playbook re-validates them
   33 |     # so a tampered Ansible inventory (or a direct ansible-runner
   34 |     # invocation that bypasses the Python entry point) cannot use any
   35 |     # field as a path-traversal vector. Validation runs *before* any
   36 |     # task that interpolates a validated field into a path.
   37 | 
   38 |     - name: Assert agent_name matches the safe slug pattern
   39 |       ansible.builtin.assert:
   40 |         that:
   41 |           - agent_name is string
   42 |           - agent_name is match('^[a-z][a-z0-9_-]{0,31}$')
   43 |         fail_msg: "Invalid agent_name: {{ agent_name | default('<unset>') }}"
   44 |         quiet: true
   45 | 
   46 |     - name: Assert desired_skill_names is a list
   47 |       ansible.builtin.assert:
   48 |         that:
   49 |           - desired_skill_names is iterable
   50 |           - desired_skill_names is not string
   51 |           - desired_skill_names is not mapping
   52 |         fail_msg: "desired_skill_names must be a list"
   53 |         quiet: true
   54 | 
   55 |     - name: Assert every desired skill name matches the safe slug pattern
   56 |       ansible.builtin.assert:
   57 |         that:
   58 |           - item is string
   59 |           - item is match('^[a-z0-9][a-z0-9_-]*$')
   60 |         fail_msg: "Unsafe skill name in desired_skill_names: {{ item }}"
   61 |         quiet: true
   62 |       loop: "{{ desired_skill_names }}"
   63 |       loop_control:
   64 |         label: "{{ item }}"
   65 | 
   66 |     - name: Assert staging_dir is a non-empty absolute path under the clawrium staging tree
   67 |       # Defense-in-depth: the Python entry point always passes a
   68 |       # `tempfile.mkdtemp` path under `${clawrium_config}/staging/skills/`,
   69 |       # so a tampered inventory pointing at `/etc` or `/root` would not
   70 |       # match the expected substring and the playbook bails before the
   71 |       # `copy` task runs. The `clawrium/staging/skills/` substring is
   72 |       # the canonical prefix carved out by `_stage_skills` and is
   73 |       # stable across XDG_CONFIG_HOME values.
   74 |       ansible.builtin.assert:
   75 |         that:
   76 |           - staging_dir is string
   77 |           - staging_dir | length > 0
   78 |           - staging_dir.startswith('/')
   79 |           - "'/clawrium/staging/skills/' in staging_dir"
   80 |         fail_msg: >-
   81 |           staging_dir must be an absolute path under
   82 |           `${clawrium_config}/staging/skills/` (got '{{ staging_dir }}')
   83 |         quiet: true
   84 | 
   85 |     # ----------------------- materialize ------------------------------------
   86 | 
   87 |     - name: Ensure clawrium-managed skills root exists
   88 |       ansible.builtin.file:
   89 |         path: "{{ skills_root }}"
   90 |         state: directory
   91 |         owner: "{{ agent_name }}"
   92 |         group: "{{ agent_name }}"
   93 |         mode: "0755"
   94 | 
   95 |     - name: List existing clawrium-managed skill directories on host
   96 |       # `depth: 1` so we only enumerate (and therefore only ever delete)
   97 |       # the immediate children of skills_root. `follow: false` prevents
   98 |       # a symlink at skills_root/<name> -> /home/agent/.ssh from being
   99 |       # treated as a managed dir and then `state: absent`-ed in the
  100 |       # prune loop.
  101 |       ansible.builtin.find:
  102 |         paths: "{{ skills_root }}"
  103 |         file_type: directory
  104 |         depth: 1
  105 |         follow: false
  106 |       register: existing_skill_dirs
  107 | 
  108 |     - name: Compute set of skill directories to prune
  109 |       # `extras` = (on-host names) - (desired names). Pruning is bounded
  110 |       # to this set; we never compute a delete list from anywhere else.
  111 |       ansible.builtin.set_fact:
  112 |         skills_to_prune: >-
  113 |           {{ existing_skill_dirs.files
  114 |              | map(attribute='path')
  115 |              | map('basename')
  116 |              | difference(desired_skill_names) }}
  117 |       # Pure computation — no host state changes here; suppress the
  118 |       # spurious `changed` flag this task would otherwise emit on every
  119 |       # apply.
  120 |       changed_when: false
  121 | 
  122 |     - name: Prune skill directories no longer in desired state
  123 |       ansible.builtin.file:
  124 |         path: "{{ skills_root }}/{{ item }}"
  125 |         state: absent
  126 |       loop: "{{ skills_to_prune }}"
  127 |       loop_control:
  128 |         label: "{{ item }}"
  129 |       # Each `item` is a basename of an entry found by `find` above
  130 |       # (already depth: 1, follow: false), but we re-assert the slug
  131 |       # pattern here so a future change to the find step cannot widen
  132 |       # the blast radius.
  133 |       when:
  134 |         - item is match('^[a-z0-9][a-z0-9_-]*$')
  135 | 
  136 |     - name: Ensure per-skill directory exists for each desired skill
  137 |       ansible.builtin.file:
  138 |         path: "{{ skills_root }}/{{ item }}"
  139 |         state: directory
  140 |         owner: "{{ agent_name }}"
  141 |         group: "{{ agent_name }}"
  142 |         mode: "0755"
  143 |       loop: "{{ desired_skill_names }}"
  144 |       loop_control:
  145 |         label: "{{ item }}"
  146 | 
  147 |     - name: Materialize SKILL.md for each desired skill
  148 |       # `copy` writes to a tempfile in the dest dir and renames into
  149 |       # place — atomic against a concurrent hermes daemon read.
  150 |       # `src` lives on the control machine inside our process-owned
  151 |       # staging dir (0700, freshly created); Ansible reads it locally
  152 |       # and ships the bytes.
  153 |       #
  154 |       # `no_log: true` keeps the rendered SKILL.md body (which may grow
  155 |       # to include provider config / API config in later skills) out
  156 |       # of ansible-runner stdout, the `artifacts/` cache, and journald
  157 |       # if the runner is wrapped by a systemd unit. `loop_control.label`
  158 |       # still surfaces the skill name in task status so failures remain
  159 |       # diagnosable.
  160 |       ansible.builtin.copy:
  161 |         src: "{{ staging_dir }}/{{ item }}/SKILL.md"
  162 |         dest: "{{ skills_root }}/{{ item }}/SKILL.md"
  163 |         owner: "{{ agent_name }}"
  164 |         group: "{{ agent_name }}"
  165 |         mode: "0644"
  166 |       loop: "{{ desired_skill_names }}"
  167 |       loop_control:
  168 |         label: "{{ item }}"
  169 |       no_log: true
```

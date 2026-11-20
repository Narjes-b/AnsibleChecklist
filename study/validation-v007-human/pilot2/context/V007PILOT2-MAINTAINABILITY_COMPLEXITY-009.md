# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-009

- Repository: `dryvist/ansible-proxmox-apps`
- Commit: `b179574eb875a6b7be09df83d001f623a68a2681`
- Family: maintainability_complexity
- Rule: `ansibleguard/large-task`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `roles/openbao/tasks/init/08-rbac-policies.yml` (reported anchor line 236)
- Flagged construct: task `write the rbac policies that are missing or changed`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–257 of 257:

```text
    1 | ---
    2 | # Each Terrakube workspace policy references its workspace BY LIST INDEX
    3 | # (openbao_terrakube_workspaces[N]) while carrying the workspace's name in its
    4 | # own `name`. Nothing structural keeps the two in step: inserting a workspace
    5 | # anywhere but the end, or mistyping an index, silently points a policy at a
    6 | # DIFFERENT workspace — which grants that workspace's KV paths to the wrong
    7 | # job identity and reads as a working converge.
    8 | #
    9 | # Compare the two ORDERED lists rather than their sets: a set comparison passes
   10 | # on exactly the swap this is guarding against, since both names are still
   11 | # present.
   12 | - name: Assert every Terrakube workspace policy names the workspace it points at
   13 |   ansible.builtin.assert:
   14 |     that:
   15 |       - _tk_policy_names == _tk_workspace_derived_names
   16 |     fail_msg: >-
   17 |       A Terrakube workspace policy references the wrong entry in
   18 |       openbao_terrakube_workspaces. Declared policy names:
   19 |       {{ _tk_policy_names }}; names derived from the workspaces each one
   20 |       actually points at: {{ _tk_workspace_derived_names }}.
   21 |     success_msg: "All {{ _tk_policy_names | length }} Terrakube workspace policies point at their own workspace."
   22 |   vars:
   23 |     _tk_policies: "{{ openbao_base_policies | selectattr('workspace', 'defined') | list }}"
   24 |     _tk_policy_names: "{{ _tk_policies | map(attribute='name') | list }}"
   25 |     _tk_workspace_derived_names: >-
   26 |       {{ _tk_policies | map(attribute='workspace.name')
   27 |          | map('regex_replace', '^', 'terrakube-') | list }}
   28 |   run_once: true
   29 |   delegate_to: localhost
   30 |   become: false
   31 | 
   32 | # A reconcile-mode run may manage only what its OWN policy grants. That policy
   33 | # is excluded from the set reconcile can rewrite (it cannot widen its own
   34 | # grants), so the live policy drifts BEHIND the declared set the moment a new
   35 | # policy is declared -- and every read/write of the new name then 403s.
   36 | #
   37 | # Ask the server what this token can actually do rather than inferring it from
   38 | # the declared set, and fail LOUDLY naming the shortfall. Silently narrowing to
   39 | # what happens to work is the exact false green this block exists to prevent:
   40 | # a declared policy would never be written and nothing would say so.
   41 | # The prefix is added by matching '^' rather than capturing the whole name and
   42 | # substituting \1. A backreference does not survive the trip: YAML, Jinja and
   43 | # `command`'s shlex.split each get a say in what a backslash means, and the net
   44 | # effect was that all 60 paths rendered as the single literal
   45 | # `sys/policies/acl/1` -- a policy that does not exist, so the server answered
   46 | # `deny` and the gate concluded the identity could write nothing. It had never
   47 | # once asked about a real path.
   48 | - name: Ask the server which declared policies this identity may actually write
   49 |   ansible.builtin.command:
   50 |     cmd: >-
   51 |       bao write -format=json sys/capabilities-self
   52 |       {{ openbao_manageable_policies
   53 |          | map(attribute='name')
   54 |          | map('regex_replace', '^', 'paths=sys/policies/acl/')
   55 |          | join(' ') }}
   56 |   environment:
   57 |     BAO_ADDR: "{{ openbao_api_addr }}"
   58 |     BAO_TOKEN: "{{ openbao_bootstrap_token }}"
   59 |   register: openbao_policy_capabilities
   60 |   changed_when: false
   61 |   failed_when: false
   62 |   no_log: true
   63 |   when:
   64 |     - openbao_bootstrap_token is defined
   65 |     - openbao_reconcile_mode | default(false)
   66 | 
   67 | # sys/capabilities-self returns the per-path capability lists BOTH at the top
   68 | # level and under `data`, and which of the two a given client surfaces is not
   69 | # something to bet a hard failure on. Reading only `data` yielded an empty dict
   70 | # against a live policy that demonstrably grants create/read/update on every
   71 | # path asked about -- and an empty dict reads as "denied everything", so the
   72 | # gate blocked a converge that should have proceeded.
   73 | - name: Resolve what the server said this identity may write
   74 |   ansible.builtin.set_fact:
   75 |     openbao_policy_caps: >-
   76 |       {{ (_body.get('data', {}) | combine(_body)) | dict2items
   77 |          | selectattr('key', 'match', '^sys/policies/acl/') | items2dict }}
   78 |   vars:
   79 |     _body: "{{ openbao_policy_capabilities.stdout | default('{}') | from_json }}"
   80 |   # Keep only real policy paths, rather than removing a hand-listed set of
   81 |   # envelope keys. The response also carries `capabilities`, `mount_type`,
   82 |   # `mount_class` and friends, and any future field would join them -- a
   83 |   # denylist would have to grow to stay correct. A stray key surviving here
   84 |   # would be compared against declared policy NAMES below (the prefix is
   85 |   # stripped, not filtered, at that point), so a collision would mark a policy
   86 |   # writable that is not: a false green in the guard built to prevent one.
   87 |   when:
   88 |     - openbao_bootstrap_token is defined
   89 |     - openbao_reconcile_mode | default(false)
   90 |     - (openbao_policy_capabilities.rc | default(1)) == 0
   91 | 
   92 | # An uninformative probe is NOT a denial. If the response carried capability
   93 | # entries for FEWER paths than were asked about, the probe itself is broken (a
   94 | # shape change, a malformed request) and reading the gap as a permission finding
   95 | # would be a confident false red -- the same absent-vs-denied confusion this
   96 | # whole block exists to eliminate. Fail, but say which failure it is.
   97 | #
   98 | # The count, not merely zero: the backreference bug asked about one literal path
   99 | # and got ONE well-formed entry back, so a `== 0` arm did not fire and the gate
  100 | # went on to report a unanimous false denial. A short answer is the direct
  101 | # signature of a probe that asked the wrong question, and neither a zero-check
  102 | # nor a type-check sees it -- the values were valid capability lists, just for a
  103 | # path nobody declared.
  104 | - name: FAIL -- the capability probe did not answer about every path it asked about
  105 |   ansible.builtin.fail:
  106 |     msg: >-
  107 |       Asked sys/capabilities-self about
  108 |       {{ openbao_manageable_policies | length }} policy paths and the response
  109 |       carried a capability entry for only
  110 |       {{ openbao_policy_caps | default({}) | length }} of them. That is a broken
  111 |       probe, not a permission finding -- do not read a short answer as "this
  112 |       identity may write nothing". Check the request shape and the response
  113 |       envelope before concluding anything about grants.
  114 |   when:
  115 |     - openbao_bootstrap_token is defined
  116 |     - openbao_reconcile_mode | default(false)
  117 |     - (openbao_policy_capabilities.rc | default(1)) == 0
  118 |     - openbao_manageable_policies | length > 0
  119 |     - >-
  120 |       (openbao_policy_caps | default({}) | length)
  121 |       < (openbao_manageable_policies | length)
  122 | 
  123 | - name: FAIL -- the reconcile identity cannot manage every declared policy
  124 |   vars:
  125 |     _caps: "{{ openbao_policy_caps | default({}) }}"
  126 |     _unwritable: >-
  127 |       {{ openbao_manageable_policies | map(attribute='name') | reject('in',
  128 |          (_caps | dict2items
  129 |                 | selectattr('value', 'contains', 'update')
  130 |                 | map(attribute='key')
  131 |                 | map('regex_replace', '^sys/policies/acl/', '')
  132 |                 | list)) | list | sort }}
  133 |   ansible.builtin.fail:
  134 |     msg: >-
  135 |       The openbao-reconcile identity is declared as managing
  136 |       {{ openbao_manageable_policies | length }} policies but the live
  137 |       openbao-reconcile policy grants update on none of these
  138 |       {{ _unwritable | length }}: {{ _unwritable | join(', ') }}.
  139 |       Reconcile CANNOT widen its own grants -- openbao-reconcile is in
  140 |       openbao_reconcile_excluded_policies by design -- so this only clears with
  141 |       one operator-token run (OPENBAO_PROVISIONING_TOKEN), which rewrites the
  142 |       reconcile policy from the current declared set. Refusing to continue:
  143 |       writing only the reachable subset would leave the rest declared but never
  144 |       written, with the converge still reporting success.
  145 |   when:
  146 |     - openbao_bootstrap_token is defined
  147 |     - openbao_reconcile_mode | default(false)
  148 |     - (openbao_policy_capabilities.rc | default(1)) == 0
  149 |     - _unwritable | length > 0
  150 | 
  151 | # Rendered on the CONTROLLER, not the target. The previous shape wrote each
  152 | # policy to the guest with `template`, read it back with `slurp`, and deleted it
  153 | # again -- three remote round trips per policy purely to move content this
  154 | # process already had in memory. Over 60 policies that is 180 operations on a
  155 | # proxmox_pct_remote connection, and each one is a full paramiko connect plus a
  156 | # `pct exec`: the render step alone measured 776 SECONDS (12.9 min, ~13s per
  157 | # policy) writing a few KB per file.
  158 | #
  159 | # `lookup('template', ...)` resolves against the same role templates/ directory
  160 | # the module used and renders with the same variable context, so the content is
  161 | # identical -- it just never leaves the controller. The write below feeds it to
  162 | # `bao policy write` on stdin, so no file is created and none has to be cleaned
  163 | # up. Remote operations for this phase: 180 -> 0.
  164 | - name: Render the RBAC policies on the controller
  165 |   ansible.builtin.set_fact:
  166 |     openbao_rendered_policy_map: >-
  167 |       {{ openbao_rendered_policy_map | default({})
  168 |          | combine({ item.name: lookup('template', item.template) | trim }) }}
  169 |   loop: "{{ openbao_manageable_policies }}"
  170 |   loop_control:
  171 |     label: "{{ item.name }}"
  172 |   no_log: true
  173 |   when: openbao_bootstrap_token is defined
  174 | 
  175 | - name: List existing policies
  176 |   ansible.builtin.command:
  177 |     cmd: bao policy list -format=json
  178 |   environment:
  179 |     BAO_ADDR: "{{ openbao_api_addr }}"
  180 |     BAO_TOKEN: "{{ openbao_bootstrap_token }}"
  181 |   register: openbao_policies_raw
  182 |   no_log: true
  183 |   changed_when: false
  184 |   when: openbao_bootstrap_token is defined
  185 | 
  186 | - name: Read existing RBAC policy contents
  187 |   ansible.builtin.command:
  188 |     cmd: "bao policy read -format=json {{ item.name }}"
  189 |   environment:
  190 |     BAO_ADDR: "{{ openbao_api_addr }}"
  191 |     BAO_TOKEN: "{{ openbao_bootstrap_token }}"
  192 |   loop: "{{ openbao_manageable_policies }}"
  193 |   loop_control:
  194 |     label: "{{ item.name }}"
  195 |   register: openbao_existing_policy_reads
  196 |   no_log: true
  197 |   changed_when: false
  198 |   # Every other probe in this file tolerates a non-zero rc; this one did not, so
  199 |   # a single denied read aborted the whole block before any policy was written.
  200 |   # The map build below already guards on `rc == 0`, so a failed read is an
  201 |   # expected, handled input -- not a reason to stop. The capability gate above
  202 |   # is what turns a genuine scope shortfall into a loud failure.
  203 |   failed_when: false
  204 |   when:
  205 |     - openbao_bootstrap_token is defined
  206 |     - item.name in (openbao_policies_raw.stdout | from_json)
  207 | 
  208 | # Both sides are `trim`ed and read from the CORRECT key, because the write below
  209 | # is a no-op only when the two compare equal -- and it was never equal:
  210 | #
  211 | #   * `bao policy read -format=json` returns {"policy": ...} at TOP LEVEL. The
  212 | #     old expression read `.data.policy`, which does not exist, so every entry
  213 | #     resolved to '' and every policy looked changed on every converge.
  214 | #   * The server appends a trailing newline on write, so even with the right key
  215 | #     the stored text is the rendered text plus "\n" and an exact != is always
  216 | #     true.
  217 | #
  218 | # Measured live: rendered 475 bytes vs stored 476, differing only in that
  219 | # newline, `stripped_equal` true on every sampled policy. Either defect alone
  220 | # rewrites all 56 policies on every run while honestly reporting "changed", so
  221 | # fixing only one would have looked like a fix and changed nothing.
  222 | - name: Build the existing RBAC policy content map
  223 |   ansible.builtin.set_fact:
  224 |     openbao_existing_policy_map: >-
  225 |       {{ openbao_existing_policy_map | default({})
  226 |          | combine({ item.item.name: ((item.stdout | default('{}') | from_json).policy | default('')) | trim }) }}
  227 |   loop: "{{ openbao_existing_policy_reads.results | default([]) }}"
  228 |   loop_control:
  229 |     label: "{{ item.item.name }}"
  230 |   no_log: true
  231 |   when:
  232 |     - openbao_bootstrap_token is defined
  233 |     - not (item.skipped | default(false))
  234 |     - (item.rc | default(1)) == 0
  235 | 
  236 | - name: Write the RBAC policies that are missing or changed
  237 |   ansible.builtin.command:
  238 |     cmd: "bao policy write {{ item.name }} -"
  239 |     stdin: "{{ (openbao_rendered_policy_map | default({}))[item.name] }}"
  240 |   environment:
  241 |     BAO_ADDR: "{{ openbao_api_addr }}"
  242 |     BAO_TOKEN: "{{ openbao_bootstrap_token }}"
  243 |   loop: "{{ openbao_manageable_policies }}"
  244 |   loop_control:
  245 |     label: "{{ item.name }}"
  246 |   no_log: true
  247 |   changed_when: true
  248 |   when:
  249 |     - openbao_bootstrap_token is defined
  250 |     - >-
  251 |       item.name not in (openbao_policies_raw.stdout | from_json)
  252 |       or
  253 |       (openbao_existing_policy_map | default({})).get(item.name, '')
  254 |       !=
  255 |       (openbao_rendered_policy_map | default({})).get(item.name, '')
  256 | 
  257 | # --- AppRole auth method (add-if-missing) -----------------------------------
```

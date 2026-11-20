# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-010

- Repository: `ric03uec/clawrium`
- Commit: `77274d5ca3d71b5a057df332482dd678446d9544`
- Family: Maintainability/complexity
- Rule: `ansibleguard/shell-instead-of-module`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `src/clawrium/platform/registry/openclaw/playbooks/install.yaml` (reported anchor line 351)
- Object: `task` `8fe311dc5bebe3b4d930e1546cf18c9657e47f04ca228608c074a804fb8d571b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–419 of 419:

```text
    1 | ---
    2 | # Phase 2 of #11 (issue #944): every openclaw install runs on a
    3 | # host prepped for the NemoClaw runtime substrate. Prereqs
    4 | # (Ubuntu >= 24.04 + docker + node) land first via a dedicated
    5 | # playbook, then the nemoclaw runtime binary via its own single-
    6 | # purpose playbook (also invocable at sync time by
    7 | # `_openclaw_nemoclaw_onboard`). Both are Linux-only. The macOS
    8 | # siblings currently refuse loudly per plan §7.2 (option b) — we
    9 | # still import them here rather than skipping so a darwin host
   10 | # gets a clear failure at install time instead of silently
   11 | # skipping the NemoClaw substrate.
   12 | # NB: `when:` on `import_playbook` is a static import — Ansible
   13 | # evaluates it at parse time and silently ignores the condition
   14 | # (>= 2.8). Each imported runbook enforces its own OS gate via a
   15 | # task-0 `Refuse to run on non-Linux hosts` dispatcher-contract
   16 | # guard (per AGENTS.md "Integration Binary Install" Rule 2). A
   17 | # darwin host reaches these plays and fails loudly at task 0
   18 | # rather than blowing up opaquely on `apt`.
   19 | - import_playbook: install_prereqs.yaml
   20 | - import_playbook: install_nemoclaw.yaml
   21 | 
   22 | - hosts: all
   23 |   become: yes
   24 |   tasks:
   25 |     # W3 (ATX iter-4): a direct `ansible-playbook install.yaml` run
   26 |     # (no `operator_platform` extravar) would otherwise pass these
   27 |     # tasks and crash deep in the pair step with an opaque
   28 |     # `AnsibleUndefinedVariable`. Fail early with a hint pointing at
   29 |     # `clawctl agent create`, which is the only supported entry.
   30 |     - name: Assert operator_platform is provided (set by core/install.py)
   31 |       ansible.builtin.assert:
   32 |         that:
   33 |           - operator_platform is defined
   34 |           - operator_platform | length > 0
   35 |         fail_msg: >-
   36 |           `operator_platform` extravar is required; the openclaw
   37 |           pair script records it on the daemon's device entry. This
   38 |           playbook is invoked by `clawctl agent create`
   39 |           (core/install.py), which sets it from the operator
   40 |           machine's `sys.platform`. A direct `ansible-playbook
   41 |           install.yaml` invocation is not supported.
   42 | 
   43 |     - name: Normalize target OpenClaw version
   44 |       ansible.builtin.set_fact:
   45 |         openclaw_target_version: "{{ (claw_version | default('v2026.6.8')) | regex_replace('^v', '') }}"
   46 | 
   47 |     - name: Create agent user
   48 |       ansible.builtin.user:
   49 |         name: "{{ agent_name }}"
   50 |         state: present
   51 |         create_home: yes
   52 |         shell: /bin/bash
   53 | 
   54 |     # ATX iter-3 B2: `install_prereqs.yaml` adds the SSH user to the
   55 |     # `docker` group at prereqs-time (agent user doesn't exist yet
   56 |     # there); the agent user itself needs `docker` membership so
   57 |     # nemoclaw sandbox tooling can talk to the Docker socket. Add it
   58 |     # right after user creation so ownership of subsequent per-agent
   59 |     # files sits with the right groups.
   60 |     - name: Add agent user to docker group
   61 |       ansible.builtin.user:
   62 |         name: "{{ agent_name }}"
   63 |         groups: docker
   64 |         append: yes
   65 | 
   66 |     - name: Check per-agent openclaw binary
   67 |       ansible.builtin.stat:
   68 |         path: "/home/{{ agent_name }}/.openclaw/bin/openclaw"
   69 |       register: openclaw_per_agent_stat
   70 | 
   71 |     - name: Discover openclaw binary in PATH
   72 |       ansible.builtin.command: which openclaw
   73 |       register: openclaw_which_result
   74 |       changed_when: false
   75 |       failed_when: false
   76 | 
   77 |     # W2: a zero-byte or non-executable per-agent file (e.g. crashed mid-flight
   78 |     # install artifact) must NOT be accepted as a working binary — that would
   79 |     # silently produce an ExecStart that crash-loops under systemd's Restart=always.
   80 |     - name: Resolve openclaw binary (per-agent preferred, PATH fallback)
   81 |       ansible.builtin.set_fact:
   82 |         openclaw_discovered_binary: >-
   83 |           {{ ('/home/' ~ agent_name ~ '/.openclaw/bin/openclaw')
   84 |              if (openclaw_per_agent_stat.stat.exists
   85 |                  and openclaw_per_agent_stat.stat.executable | default(false)
   86 |                  and (openclaw_per_agent_stat.stat.size | default(0)) > 0)
   87 |              else (openclaw_which_result.stdout
   88 |                    if (openclaw_which_result.rc | default(1)) == 0
   89 |                    else '') }}
   90 | 
   91 |     # The validator runs unconditionally on the RESOLVED binary — not on the
   92 |     # raw `which` result and not gated on stat existence. Round 2 ATX flagged
   93 |     # that gating on `not openclaw_per_agent_stat.stat.exists` creates a
   94 |     # security gap: a zero-byte or non-executable per-agent file is rejected
   95 |     # by W2's executable+size check, falls through to the PATH binary, but
   96 |     # would then bypass this validator. Validating the resolved variable
   97 |     # closes that path. The per-agent /home/... case trivially passes the
   98 |     # allowlist — that's correct, not a no-op.
   99 |     - name: Validate discovered binary path
  100 |       ansible.builtin.fail:
  101 |         msg: "Discovered openclaw binary at unsafe path: {{ openclaw_discovered_binary }}. Expected under /usr/local/bin/, /usr/bin/, or /home/."
  102 |       when: >
  103 |         (openclaw_discovered_binary | length) > 0 and
  104 |         not (openclaw_discovered_binary.startswith('/usr/local/bin/') or
  105 |              openclaw_discovered_binary.startswith('/usr/bin/') or
  106 |              openclaw_discovered_binary.startswith('/home/'))
  107 | 
  108 |     - name: Get installed openclaw version
  109 |       ansible.builtin.command: "{{ openclaw_discovered_binary }} --version"
  110 |       register: openclaw_version_check
  111 |       changed_when: false
  112 |       failed_when: false
  113 |       when: (openclaw_discovered_binary | length) > 0
  114 | 
  115 |     # Defensive parse: empty string on no-match means a version check failure
  116 |     # is treated as "version unknown" -> not a match -> reinstall (safe default).
  117 |     - name: Parse installed openclaw version
  118 |       ansible.builtin.set_fact:
  119 |         openclaw_installed_version: "{{ (openclaw_version_check.stdout | default('')) | regex_search('([0-9]+\\.[0-9]+\\.[0-9]+)') | default('', true) }}"
  120 |       when:
  121 |         - openclaw_version_check is defined
  122 |         - (openclaw_version_check.rc | default(1)) == 0
  123 | 
  124 |     - name: Set install skip condition
  125 |       ansible.builtin.set_fact:
  126 |         openclaw_already_installed: >-
  127 |           {{ (openclaw_discovered_binary | length) > 0
  128 |              and (openclaw_installed_version | default('')) == openclaw_target_version
  129 |              and not (force_install | default(false) | bool) }}
  130 |         openclaw_runtime_binary: "{{ openclaw_discovered_binary if (openclaw_discovered_binary | length) > 0 else '/home/' ~ agent_name ~ '/.openclaw/bin/openclaw' }}"
  131 | 
  132 |     - name: Mark install as skipped when already installed
  133 |       ansible.builtin.debug:
  134 |         msg: "OpenClaw v{{ openclaw_installed_version | default('unknown') }} already installed at {{ openclaw_discovered_binary }}. Skipping binary install."
  135 |       when: openclaw_already_installed
  136 | 
  137 |     - name: Note that --force was supplied (overriding skip)
  138 |       ansible.builtin.debug:
  139 |         msg: "force=true: reinstalling OpenClaw at {{ openclaw_discovered_binary | default('<no prior install>') }}"
  140 |       when:
  141 |         - (openclaw_discovered_binary | length) > 0
  142 |         - force_install | default(false) | bool
  143 | 
  144 |     - name: Download OpenClaw installer script
  145 |       ansible.builtin.get_url:
  146 |         url: https://openclaw.ai/install-cli.sh
  147 |         dest: "/home/{{ agent_name }}/openclaw-install.sh"
  148 |         mode: "0700"
  149 |         owner: "{{ agent_name }}"
  150 |         group: "{{ agent_name }}"
  151 |         force: yes
  152 |         timeout: 30
  153 |         # Variable name must match `claw_sha256` injected by
  154 |         # `core/install.py` (issue #592 ATX B1). Older revisions used
  155 |         # `installer_checksum` which never resolved, silently dropping
  156 |         # the checksum gate via `default(omit)`. Manifest entries that
  157 |         # omit the `sha256:` field still bypass verification — adding
  158 |         # it per platform entry is tracked as a separate hardening
  159 |         # follow-up because the openclaw installer URL is unpinned and
  160 |         # the digest rotates upstream without a manifest bump.
  161 |         checksum: "{{ ('sha256:' + claw_sha256) if claw_sha256 else omit }}"
  162 |       when: not openclaw_already_installed
  163 | 
  164 |     - name: Install OpenClaw CLI runtime
  165 |       ansible.builtin.command:
  166 |         argv:
  167 |           - /bin/bash
  168 |           - "/home/{{ agent_name }}/openclaw-install.sh"
  169 |           - --prefix
  170 |           - "/home/{{ agent_name }}/.openclaw"
  171 |           - --install-method
  172 |           - npm
  173 |           - --version
  174 |           - "{{ openclaw_target_version }}"
  175 |           - --no-onboard
  176 |       become_user: "{{ agent_name }}"
  177 |       when: not openclaw_already_installed
  178 | 
  179 |     - name: Clean up installer script
  180 |       ansible.builtin.file:
  181 |         path: "/home/{{ agent_name }}/openclaw-install.sh"
  182 |         state: absent
  183 |       when: not openclaw_already_installed
  184 | 
  185 |     - name: Create workspace directory
  186 |       ansible.builtin.file:
  187 |         path: "/home/{{ agent_name }}/workspace"
  188 |         state: directory
  189 |         owner: "{{ agent_name }}"
  190 |         group: "{{ agent_name }}"
  191 |         mode: "0700"
  192 | 
  193 |     - name: Create OpenClaw config directory
  194 |       ansible.builtin.file:
  195 |         path: "/home/{{ agent_name }}/.openclaw"
  196 |         state: directory
  197 |         owner: "{{ agent_name }}"
  198 |         group: "{{ agent_name }}"
  199 |         mode: "0700"
  200 | 
  201 |     - name: Resolve per-instance gateway port from inventory (issue #533)
  202 |       ansible.builtin.set_fact:
  203 |         openclaw_port: "{{ config.gateway.port }}"
  204 | 
  205 |     # Skip on already-installed path: rewriting openclaw.json would rotate the
  206 |     # gateway token in the running daemon and invalidate the credentials cached
  207 |     # in hosts.json. The existing config on disk is preserved verbatim.
  208 |     - name: Write openclaw config (pre-rendered)
  209 |       ansible.builtin.copy:
  210 |         content: "{{ prerendered_openclaw_config_json }}"
  211 |         dest: "/home/{{ agent_name }}/.openclaw/openclaw.json"
  212 |         owner: "{{ agent_name }}"
  213 |         group: "{{ agent_name }}"
  214 |         mode: "0600"
  215 |       when: not openclaw_already_installed
  216 |       # ATX iter-1 B1: openclaw.json embeds the gateway bearer token.
  217 |       # Every other secret-touching task in this playbook already carries
  218 |       # `no_log: true`; this copy write must too so `-v` ansible-runner
  219 |       # logs don't leak the rendered file path / contents into the artifact
  220 |       # directory.
  221 |       no_log: true
  222 | 
  223 |     - name: Write exec approvals policy from template
  224 |       ansible.builtin.template:
  225 |         src: "{{ template_path }}/exec-approvals.json.j2"
  226 |         dest: "/home/{{ agent_name }}/.openclaw/exec-approvals.json"
  227 |         owner: "{{ agent_name }}"
  228 |         group: "{{ agent_name }}"
  229 |         mode: "0600"
  230 |         # W6 (ATX iter-2): `backup: yes` accumulates
  231 |         # `exec-approvals.json.NNNN~` siblings on every install/reconfigure
  232 |         # with no rotation; the previous value is recoverable from the
  233 |         # template anyway.
  234 |       no_log: true
  235 | 
  236 |     - name: Verify exec approvals JSON is valid
  237 |       ansible.builtin.command:
  238 |         cmd: python3 -m json.tool /home/{{ agent_name }}/.openclaw/exec-approvals.json
  239 |       changed_when: false
  240 | 
  241 |     - name: Create environment file for agent
  242 |       # Fix #1 (post-Phase-4 provider-strip regression): when the
  243 |       # operator passed --provider at create time, `install.py`
  244 |       # pre-renders the .openclaw/env body via
  245 |       # `_prerender_openclaw_install_stub` with the resolved provider
  246 |       # bearer + model already wired, and threads it here as
  247 |       # `prerendered_openclaw_env`. When empty (provider-less bootstrap
  248 |       # or non-openclaw code path), fall back to the previous empty-file
  249 |       # behavior so a subsequent `agent configure` can still populate.
  250 |       # `force: yes` because the operator's --provider intent is the
  251 |       # source of truth — a stale env from a prior install must be
  252 |       # replaced.
  253 |       ansible.builtin.copy:
  254 |         dest: "/home/{{ agent_name }}/.openclaw/env"
  255 |         content: "{{ prerendered_openclaw_env | default('') }}"
  256 |         owner: "{{ agent_name }}"
  257 |         group: "{{ agent_name }}"
  258 |         mode: "0600"
  259 |         force: "{{ prerendered_openclaw_env | default('') | length > 0 }}"
  260 |       no_log: "{{ (prerendered_openclaw_env | default('') | length) > 0 }}"
  261 | 
  262 |     - name: Create systemd service file
  263 |       ansible.builtin.copy:
  264 |         dest: "/etc/systemd/system/{{ agent_type }}-{{ agent_name }}.service"
  265 |         content: |
  266 |           [Unit]
  267 |           Description=OpenClaw AI Assistant ({{ agent_name }})
  268 |           After=network.target
  269 | 
  270 |           [Service]
  271 |           Type=simple
  272 |           User={{ agent_name }}
  273 |           WorkingDirectory=/home/{{ agent_name }}/workspace
  274 |           EnvironmentFile=/home/{{ agent_name }}/.openclaw/env
  275 |           ExecStart={{ openclaw_runtime_binary }} gateway run --allow-unconfigured
  276 |           Restart=always
  277 |           RestartSec=5
  278 | 
  279 |           [Install]
  280 |           WantedBy=multi-user.target
  281 |         mode: "0644"
  282 |       register: openclaw_unit_file_result
  283 | 
  284 |     # B3: when the unit file's ExecStart changes (e.g., binary path shifts from
  285 |     # /usr/local/bin/openclaw to /home/<agent>/.openclaw/bin/openclaw), the next
  286 |     # `state: started` is a no-op on already-active services. Force a restart so
  287 |     # the daemon picks up the new binary without waiting for a reboot.
  288 |     - name: Restart openclaw service on ExecStart change
  289 |       ansible.builtin.systemd:
  290 |         name: "{{ agent_type }}-{{ agent_name }}"
  291 |         state: restarted
  292 |         enabled: yes
  293 |         daemon_reload: yes
  294 |       when: openclaw_unit_file_result.changed
  295 | 
  296 |     - name: Enable and start openclaw service
  297 |       ansible.builtin.systemd:
  298 |         name: "{{ agent_type }}-{{ agent_name }}"
  299 |         enabled: yes
  300 |         state: started
  301 |         daemon_reload: yes
  302 | 
  303 |     - name: Wait for gateway port to be listening
  304 |       ansible.builtin.wait_for:
  305 |         port: "{{ openclaw_port }}"
  306 |         host: "{{ ansible_host }}"
  307 |         timeout: 60
  308 |       delegate_to: localhost
  309 |       become: no
  310 | 
  311 |     # The pairing block below is gated on `not openclaw_already_installed` so
  312 |     # we don't re-pair (and rotate device credentials) on every re-install.
  313 |     # `npm install ws` alone is the dominant cost; pairing also generates new
  314 |     # device credentials that would invalidate any cached client tokens.
  315 |     - name: Read gateway authentication token from config file
  316 |       ansible.builtin.slurp:
  317 |         src: "/home/{{ agent_name }}/.openclaw/openclaw.json"
  318 |       register: openclaw_config_raw
  319 |       no_log: true
  320 |       when: not openclaw_already_installed
  321 | 
  322 |     - name: Parse gateway token from config
  323 |       ansible.builtin.set_fact:
  324 |         gateway_token_result_stdout: "{{ (openclaw_config_raw.content | b64decode | from_json).gateway.auth.token }}"
  325 |       no_log: true
  326 |       when: not openclaw_already_installed
  327 | 
  328 |     - name: Validate gateway token format
  329 |       ansible.builtin.fail:
  330 |         msg: "Gateway token not found or invalid format"
  331 |       when:
  332 |         - not openclaw_already_installed
  333 |         - gateway_token_result_stdout is not defined or
  334 |           gateway_token_result_stdout | length < 32 or
  335 |           not (gateway_token_result_stdout is regex('^[a-zA-Z0-9_-]+$'))
  336 |       # ATX iter-2 B1: every adjacent task touching gateway_token_result_stdout
  337 |       # carries no_log: true. At -v / -vvv, ansible-runner writes the
  338 |       # evaluated when-condition into the artifacts directory before
  339 |       # _cleanup_ansible_artifacts runs.
  340 |       no_log: true
  341 | 
  342 |     - name: Copy device pairing script
  343 |       ansible.builtin.copy:
  344 |         src: "{{ playbook_dir }}/../scripts/pair_device.mjs"
  345 |         dest: "/home/{{ agent_name }}/pair_device.mjs"
  346 |         owner: "{{ agent_name }}"
  347 |         group: "{{ agent_name }}"
  348 |         mode: "0700"
  349 |       when: not openclaw_already_installed
  350 | 
  351 |     - name: Install ws package for pairing script
  352 |       ansible.builtin.command:
  353 |         cmd: npm install ws
  354 |         chdir: "/home/{{ agent_name }}"
  355 |       become_user: "{{ agent_name }}"
  356 |       changed_when: true
  357 |       when: not openclaw_already_installed
  358 | 
  359 |     - name: Run device pairing via localhost
  360 |       # Pass the OPERATOR's platform (the clawctl machine that drove
  361 |       # this install) as the 3rd arg so the daemon's paired record
  362 |       # carries the same `platform` value the chat client will send
  363 |       # on subsequent connects. Without this the daemon flags
  364 |       # later connects as "device identity changed" and demands UI
  365 |       # re-approval.
  366 |       ansible.builtin.command:
  367 |         argv:
  368 |           - node
  369 |           - pair_device.mjs
  370 |           - "ws://127.0.0.1:{{ openclaw_port }}"
  371 |           - "{{ gateway_token_result_stdout }}"
  372 |           - "{{ operator_platform }}"
  373 |         chdir: "/home/{{ agent_name }}"
  374 |       become_user: "{{ agent_name }}"
  375 |       register: pairing_result
  376 |       no_log: true
  377 |       when: not openclaw_already_installed
  378 | 
  379 |     - name: Parse device credentials
  380 |       ansible.builtin.set_fact:
  381 |         device_credentials: "{{ pairing_result.stdout | from_json }}"
  382 |       no_log: true
  383 |       when: not openclaw_already_installed
  384 | 
  385 |     - name: Validate device credentials
  386 |       ansible.builtin.fail:
  387 |         msg: "Device pairing failed: {{ device_credentials.error | default('unknown error') }}"
  388 |       when:
  389 |         - not openclaw_already_installed
  390 |         - device_credentials.deviceToken is not defined or device_credentials.deviceToken | length < 10
  391 |       # ATX iter-1 W5: consistency with surrounding `no_log: true` tasks.
  392 |       # `when` clause evaluation may surface the token length in verbose logs.
  393 |       no_log: true
  394 | 
  395 |     - name: Clean up pairing script
  396 |       ansible.builtin.file:
  397 |         path: "/home/{{ agent_name }}/pair_device.mjs"
  398 |         state: absent
  399 | 
  400 |     - name: Clean up node_modules from pairing
  401 |       ansible.builtin.file:
  402 |         path: "/home/{{ agent_name }}/node_modules"
  403 |         state: absent
  404 | 
  405 |     - name: Save all credentials to fact for retrieval
  406 |       ansible.builtin.set_fact:
  407 |         openclaw_gateway_token: "{{ gateway_token_result_stdout }}"
  408 |         # ATX iter-1 W4: scheme is hardcoded `ws://`. Operators fronting the
  409 |         # gateway with TLS need `wss://` here; today they get a confusing
  410 |         # connection error from `clawctl chat <openclaw>`. Tracked as a known
  411 |         # limitation; safe to address in a follow-up since openclaw deploys
  412 |         # are LAN-only today (no TLS termination in the documented topology).
  413 |         openclaw_gateway_url: "ws://{{ ansible_host }}:{{ openclaw_port }}"
  414 |         openclaw_device_id: "{{ device_credentials.deviceId }}"
  415 |         openclaw_device_token: "{{ device_credentials.deviceToken }}"
  416 |         openclaw_device_private_key: "{{ device_credentials.privateKeyPem }}"
  417 |         cacheable: true
  418 |       no_log: true
  419 |       when: not openclaw_already_installed
```

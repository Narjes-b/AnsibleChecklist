# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-021

- Repository: `chrisshaiman/lamware`
- Commit: `09f919635087b38354bce34c9bc48e7c6517b463`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `ansible/roles/inetsim/tasks/main.yml` (reported anchor line 90)
- Flagged construct: not named by the finding; the anchor line 90 lies in the task at line 90, name `Patch INetSim DNS to use loop_once instead of main_loop (#464)`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–256 of 256:

```text
    1 | ---
    2 | # =============================================================================
    3 | # roles/inetsim/tasks/main.yml
    4 | # Installs and configures INetSim on the bare metal sandbox host.
    5 | #
    6 | # INetSim is a network simulation daemon that intercepts DNS, HTTP, HTTPS,
    7 | # SMTP, and FTP traffic from guest VMs and returns synthetic responses.
    8 | # It runs on the host, bound to the virbr-det bridge gateway IP, so guests
    9 | # can reach it but it is not reachable from the internet or management VPN.
   10 | #
   11 | # Execution order:
   12 | #   1. Install the inetsim package (Ubuntu universe repo)
   13 | #   2. Create log and report directories
   14 | #   3. Deploy inetsim.conf (bind address, services, log paths)
   15 | #   4. Install a systemd drop-in that orders INetSim after libvirtd
   16 | #      (so the virbr-det bridge IP exists before INetSim tries to bind)
   17 | #   5. Enable and start the inetsim service
   18 | #
   19 | # Dependency on virbr-det:
   20 | #   INetSim binds to {{ detonation_gateway }} (the virbr-det bridge IP).
   21 | #   This IP only exists after libvirtd starts and brings up the detonation
   22 | #   network. The systemd drop-in (step 4) enforces this ordering at boot.
   23 | #   During the Ansible run, the networking role runs before this role, so
   24 | #   the bridge is already up by the time this role executes.
   25 | #
   26 | # Author: Christopher Shaiman
   27 | # License: Apache 2.0
   28 | # =============================================================================
   29 | 
   30 | # -------------------------------------------------------------------------
   31 | # Install
   32 | # -------------------------------------------------------------------------
   33 | 
   34 | - name: Install inetsim
   35 |   ansible.builtin.apt:
   36 |     name: inetsim
   37 |     state: present
   38 |     update_cache: false
   39 |   # inetsim is in Ubuntu universe; ensure universe is enabled before running Ansible.
   40 |   # Command if needed: add-apt-repository universe
   41 | 
   42 | - name: Install dig (used to prove INetSim's DNS actually answers)
   43 |   ansible.builtin.apt:
   44 |     name: bind9-dnsutils
   45 |     state: present
   46 |     update_cache: false
   47 | 
   48 | # -------------------------------------------------------------------------
   49 | # Net::DNS compatibility patch (#464)
   50 | # -------------------------------------------------------------------------
   51 | # INetSim 1.3.2 (May 2020, and upstream has not released since) calls the
   52 | # historical Net::DNS::Nameserver::main_loop, which is now:
   53 | #
   54 | #     sub main_loop { carp 'deprecated...'; &start_server; exit; }
   55 | #
   56 | # and start_server begins:
   57 | #
   58 | #     my $pid = $$;                                    # FILE-scoped, set at load
   59 | #     croak '...in a subprocess' unless $$ == $pid;    # Nameserver.pm:542
   60 | #
   61 | # $pid is captured when the module is compiled — in INetSim's parent. INetSim
   62 | # forks a child per service, so the DNS child always fails that test, croaks,
   63 | # and exits 25. It had logged "started" one line earlier and never logs
   64 | # "stopped"; its stderr is not wired to the journal. The result is a service
   65 | # that reports itself up and has never answered a single query, which is why
   66 | # every analysis recorded `answers: []` (#456).
   67 | #
   68 | # loop_once is the other historical entry point: it does not call start_server,
   69 | # carries no pid guard, and creates its own sockets lazily. Verified on the host
   70 | # by replicating INetSim's structure (module loaded in parent, fork, child runs
   71 | # loop_once): the child survived, bound udp/5300, and answered a query with the
   72 | # gateway address.
   73 | #
   74 | # This edits a distro-owned file, so it is written to be self-healing: `replace`
   75 | # re-applies after any apt upgrade that restores the original, and the assertion
   76 | # below fails the deploy if the anchor ever stops matching. Neither is the real
   77 | # guard — that is the live query at the end of this file, because a file that
   78 | # looks right is not a DNS server that answers.
   79 | 
   80 | # DNS.pm is ISO-8859, not UTF-8: one byte, 0xfc, the 'ü' in the German comment
   81 | # "IP-Adressen für MX in Additional Section". ansible.builtin.replace and
   82 | # lineinfile both decode the whole file as UTF-8 and abort:
   83 | #
   84 | #   'utf-8' codec can't decode byte 0xfc in position 7746: invalid start byte
   85 | #
   86 | # sed edits bytes, so it does not care. LC_ALL=C keeps it that way — under a
   87 | # UTF-8 locale, GNU tools can treat a file with an invalid sequence as binary
   88 | # and quietly decline to match.
   89 | 
   90 | - name: Patch INetSim DNS to use loop_once instead of main_loop (#464)
   91 |   ansible.builtin.shell:
   92 |     cmd: |
   93 |       set -eu
   94 |       export LC_ALL=C
   95 |       f=/usr/share/perl5/INetSim/DNS.pm
   96 |       if grep -qF 'loop_once(10)' "$f"; then
   97 |           echo unchanged
   98 |           exit 0
   99 |       fi
  100 |       # Only reached when unpatched, so the backup is always of a pristine file
  101 |       # — including after an apt upgrade restores the original.
  102 |       cp -a "$f" "$f.lamware.bak"
  103 |       # '#' is the s/// delimiter here because ansible-lint's risky-shell-pipe
  104 |       # heuristic reads a vertical bar anywhere in a shell task as a pipeline
  105 |       # and demands pipefail — misleading to add to a task with no pipe in it.
  106 |       sed -i 's#^\([[:space:]]*\)\$server->main_loop;[[:space:]]*$#\1while (1) { $server->loop_once(10); }#' "$f"
  107 |       # sed exits 0 when its pattern matches nothing. That silent no-op is the
  108 |       # entire failure mode this task exists to avoid, so confirm the edit.
  109 |       grep -qF 'loop_once(10)' "$f"
  110 |       echo patched
  111 |     executable: /bin/bash
  112 |   register: inetsim_dns_patch
  113 |   changed_when: inetsim_dns_patch.stdout is search('patched')
  114 |   notify: Restart inetsim
  115 | 
  116 | - name: Assert the DNS patch applied (a silent no-op here is the whole failure mode)
  117 |   ansible.builtin.shell:
  118 |     cmd: |
  119 |       set -eu
  120 |       export LC_ALL=C
  121 |       f=/usr/share/perl5/INetSim/DNS.pm
  122 |       # Present in its patched form...
  123 |       grep -qF 'loop_once(10)' "$f"
  124 |       # ...and the croaking call is gone.
  125 |       ! grep -qE '^[[:space:]]*\$server->main_loop;' "$f"
  126 |     executable: /bin/bash
  127 |   changed_when: false
  128 | 
  129 | # -------------------------------------------------------------------------
  130 | # Log and report directories
  131 | # -------------------------------------------------------------------------
  132 | 
  133 | - name: Create inetsim log directory
  134 |   ansible.builtin.file:
  135 |     path: "{{ inetsim_log_dir }}"
  136 |     state: directory
  137 |     owner: inetsim
  138 |     group: inetsim
  139 |     mode: "0750"
  140 | 
  141 | - name: Create inetsim report directory
  142 |   ansible.builtin.file:
  143 |     path: "{{ inetsim_report_dir }}"
  144 |     state: directory
  145 |     owner: inetsim
  146 |     group: inetsim
  147 |     mode: "0750"
  148 | 
  149 | # -------------------------------------------------------------------------
  150 | # Configuration
  151 | # -------------------------------------------------------------------------
  152 | 
  153 | - name: Deploy inetsim.conf
  154 |   ansible.builtin.template:
  155 |     src: inetsim.conf.j2
  156 |     dest: /etc/inetsim/inetsim.conf
  157 |     owner: root
  158 |     group: inetsim
  159 |     mode: "0640"
  160 |   notify: Restart inetsim
  161 | 
  162 | # -------------------------------------------------------------------------
  163 | # Systemd drop-in — order INetSim after libvirtd
  164 | # -------------------------------------------------------------------------
  165 | # INetSim binds to the virbr-det bridge gateway IP. That IP only exists
  166 | # after libvirtd starts and activates the detonation network. Without this
  167 | # ordering, INetSim starts at boot before the bridge is up and fails to bind,
  168 | # leaving guests with no network simulation until the service is manually restarted.
  169 | 
  170 | - name: Create systemd drop-in directory for inetsim
  171 |   ansible.builtin.file:
  172 |     path: /etc/systemd/system/inetsim.service.d
  173 |     state: directory
  174 |     owner: root
  175 |     group: root
  176 |     mode: "0755"
  177 | 
  178 | - name: Install inetsim systemd drop-in (require libvirtd)
  179 |   ansible.builtin.copy:
  180 |     dest: /etc/systemd/system/inetsim.service.d/after-libvirtd.conf
  181 |     owner: root
  182 |     group: root
  183 |     mode: "0644"
  184 |     content: |
  185 |       # Ansible-managed: ensure virbr-det bridge IP exists before INetSim binds.
  186 |       # libvirtd brings up the detonation network (and its gateway IP) at startup.
  187 |       [Unit]
  188 |       Requires=libvirtd.service
  189 |       After=libvirtd.service
  190 |   notify:
  191 |     - Reload systemd daemon
  192 |     - Restart inetsim
  193 | 
  194 | # -------------------------------------------------------------------------
  195 | # Enable and start
  196 | # -------------------------------------------------------------------------
  197 | 
  198 | # The unit is generated from a SysV script whose `stop` kills only the PID in
  199 | # the pidfile and never removes it (init script line 81: `#rm -f $PIDFILE`).
  200 | # When the main process dies without cleanup the pidfile outlives it, the
  201 | # service children keep their ports, and every later start is a no-op that
  202 | # reports success. Observed here: the unit read `inactive` for 19 days while
  203 | # four children served traffic, and the #459 deploy could not restart over it.
  204 | # Full supervision fix is #463; this clears the specific state that makes a
  205 | # restart silently do nothing.
  206 | 
  207 | - name: Clear a wedged INetSim (stale pidfile, orphaned service children)
  208 |   ansible.builtin.shell:
  209 |     cmd: |
  210 |       pid=$(cat /var/run/inetsim.pid 2>/dev/null || true)
  211 |       if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
  212 |           echo healthy
  213 |           exit 0
  214 |       fi
  215 |       rm -f /var/run/inetsim.pid
  216 |       pkill -f '^inetsim_' 2>/dev/null || true
  217 |       echo cleaned
  218 |   register: inetsim_wedge
  219 |   changed_when: inetsim_wedge.stdout is search('cleaned')
  220 | 
  221 | - name: Enable and start inetsim service
  222 |   ansible.builtin.systemd:
  223 |     name: inetsim
  224 |     state: started
  225 |     enabled: true
  226 |     daemon_reload: true
  227 | 
  228 | - name: Flush handlers so the check below tests the restarted service
  229 |   ansible.builtin.meta: flush_handlers
  230 | 
  231 | # The guard that matters. `systemctl is-active` was wrong in both directions on
  232 | # this host — `inactive` while four children served traffic, then `active` with
  233 | # no DNS at all — and a config file with the right port in it proves nothing.
  234 | # Ask the question the rest of the platform depends on: does a query get an
  235 | # answer? This is the check that would have caught #456 on day one.
  236 | 
  237 | - name: Verify INetSim DNS actually answers
  238 |   ansible.builtin.shell:
  239 |     cmd: >-
  240 |       set -o pipefail;
  241 |       dig +short +tries=1 +time=3 -p {{ inetsim_dns_port }}
  242 |       @{{ detonation_gateway }} inetsim-deploy-probe.invalid
  243 |       | grep -Eo '^[0-9]{1,3}(\.[0-9]{1,3}){3}$' | head -1
  244 |     executable: /bin/bash
  245 |   register: inetsim_dns_probe
  246 |   changed_when: false
  247 |   failed_when: false
  248 |   # `dig +short` prints connection failures to stdout, so the grep is what makes
  249 |   # an empty result mean "nothing answered" rather than "answered with an error
  250 |   # string". failed_when: false because a non-answer must drive the retry below,
  251 |   # not abort on the first attempt.
  252 |   retries: 6
  253 |   delay: 3
  254 |   until: inetsim_dns_probe.stdout | trim == inetsim_dns_default_ip
  255 |   # .invalid is reserved (RFC 2606), so a real resolver could never answer this
  256 |   # and a pass cannot come from anywhere but INetSim.
```

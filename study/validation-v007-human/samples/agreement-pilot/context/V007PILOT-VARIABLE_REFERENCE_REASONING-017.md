# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-017

- Repository: `compscidr/iac`
- Commit: `350e7b8162778ad7beab8e2da8be53ea24a1127a`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `ansible/roles/mailu/tasks/main.yml` (reported anchor line 169)
- Object: `variable` `63992c76cdbfaab3d205bb5ef05add27f104fff0ea1e6918f1aea28d5c53e7ea`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–329 of 329:

```text
    1 | ---
    2 | # Mailu mail server deployment (consolidated on www with nginx-proxy)
    3 | 
    4 | - name: Create Mailu directory
    5 |   become: true
    6 |   ansible.builtin.file:
    7 |     path: "{{ mailu_install_path }}"
    8 |     state: directory
    9 |     mode: "755"
   10 | 
   11 | - name: Create Mailu data directories
   12 |   become: true
   13 |   ansible.builtin.file:
   14 |     path: "{{ mailu_install_path }}/{{ item }}"
   15 |     state: directory
   16 |     mode: "755"
   17 |   loop:
   18 |     - data
   19 |     - dkim
   20 |     - mail
   21 |     - overrides
   22 |     - overrides/nginx
   23 |     - overrides/dovecot
   24 |     - overrides/postfix
   25 |     - overrides/rspamd
   26 |     - overrides/roundcube
   27 |     - redis
   28 |     - webmail
   29 |     - filter
   30 |     - mailqueue
   31 | 
   32 | - name: Deploy mailu.env
   33 |   become: true
   34 |   ansible.builtin.template:
   35 |     src: mailu.env.j2
   36 |     dest: "{{ mailu_install_path }}/mailu.env"
   37 |     mode: "600"
   38 |   notify: Restart Mailu
   39 | 
   40 | - name: Deploy docker-compose.yml
   41 |   become: true
   42 |   ansible.builtin.template:
   43 |     src: docker-compose.yml.j2
   44 |     dest: "{{ mailu_install_path }}/docker-compose.yml"
   45 |     mode: "644"
   46 |   notify: Restart Mailu
   47 | 
   48 | # nginx-proxy stores certs as <domain>.crt/<domain>.key
   49 | # Mailu expects cert.pem/key.pem - create symlinks
   50 | - name: Create cert.pem symlink for Mailu
   51 |   become: true
   52 |   ansible.builtin.file:
   53 |     src: "{{ mailu_hostname }}.crt"
   54 |     dest: /var/lib/docker/volumes/certs/_data/cert.pem
   55 |     state: link
   56 |     force: true
   57 | 
   58 | - name: Create key.pem symlink for Mailu
   59 |   become: true
   60 |   ansible.builtin.file:
   61 |     src: "{{ mailu_hostname }}.key"
   62 |     dest: /var/lib/docker/volumes/certs/_data/key.pem
   63 |     state: link
   64 |     force: true
   65 | 
   66 | - name: Start Mailu stack
   67 |   become: true
   68 |   community.docker.docker_compose_v2:
   69 |     project_src: "{{ mailu_install_path }}"
   70 |     state: present
   71 |     pull: always
   72 | 
   73 | - name: Wait for Mailu to be ready
   74 |   become: true
   75 |   ansible.builtin.wait_for:
   76 |     port: 443 # nginx-proxy handles HTTPS
   77 |     delay: 10
   78 |     timeout: 120
   79 | 
   80 | - name: Create admin user
   81 |   become: true
   82 |   ansible.builtin.command:
   83 |     cmd: >
   84 |       docker compose exec -T admin flask mailu admin
   85 |       {{ mailu_admin_user }} {{ mailu_domain }} {{ mailu_admin_password }}
   86 |   args:
   87 |     chdir: "{{ mailu_install_path }}"
   88 |   register: mailu_admin_result
   89 |   changed_when: "'created' in mailu_admin_result.stdout"
   90 |   failed_when: false # May fail if user exists
   91 |   no_log: true # Hide admin password
   92 | 
   93 | - name: Create mail users
   94 |   become: true
   95 |   ansible.builtin.command:
   96 |     cmd: >
   97 |       docker compose exec -T admin flask mailu user
   98 |       {{ item.user }} {{ mailu_domain }} {{ item.password }}
   99 |   args:
  100 |     chdir: "{{ mailu_install_path }}"
  101 |   loop: "{{ mailu_users }}"
  102 |   register: mailu_user_result
  103 |   changed_when: false # Can't reliably detect from looped command
  104 |   failed_when: false # May fail if user exists
  105 |   no_log: true # Hide passwords
  106 | 
  107 | # These DKIM tasks loop over domain NAMES, not the mailu_additional_domains
  108 | # entries themselves. The entries nest user passwords, and Ansible echoes the
  109 | # loop item for every skipped or registered result - which printed live
  110 | # mailbox credentials in plaintext. Looping over names keeps secrets out of
  111 | # the output without needing no_log, which would also hide the DKIM keys these
  112 | # tasks exist to surface.
  113 | - name: Check if additional domain DKIM key exists
  114 |   become: true
  115 |   ansible.builtin.stat:
  116 |     path: "{{ mailu_install_path }}/dkim/{{ item }}.dkim.key"
  117 |   loop: "{{ mailu_additional_domains | default([]) | map(attribute='domain') | list }}"
  118 |   register: mailu_additional_dkim_stat
  119 | 
  120 | - name: Import additional domains with DKIM key generation (first time only)
  121 |   become: true
  122 |   ansible.builtin.shell:
  123 |     cmd: |
  124 |       set -o pipefail
  125 |       echo 'domain:
  126 |         - name: {{ item.item }}
  127 |           dkim_key: -generate-
  128 |       ' | docker compose exec -T admin flask mailu config-import --update
  129 |   args:
  130 |     chdir: "{{ mailu_install_path }}"
  131 |     executable: /bin/bash
  132 |   loop: "{{ mailu_additional_dkim_stat.results | default([]) }}"
  133 |   when: not item.stat.exists
  134 |   register: mailu_domain_result_new
  135 |   changed_when: "'updated' in mailu_domain_result_new.stdout | default('')"
  136 |   failed_when: false
  137 | 
  138 | - name: Import additional domains without regenerating DKIM key
  139 |   become: true
  140 |   ansible.builtin.shell:
  141 |     cmd: |
  142 |       set -o pipefail
  143 |       echo 'domain:
  144 |         - name: {{ item.item }}
  145 |       ' | docker compose exec -T admin flask mailu config-import --update
  146 |   args:
  147 |     chdir: "{{ mailu_install_path }}"
  148 |     executable: /bin/bash
  149 |   loop: "{{ mailu_additional_dkim_stat.results | default([]) }}"
  150 |   when: item.stat.exists
  151 |   register: mailu_domain_result_existing
  152 |   changed_when: "'updated' in mailu_domain_result_existing.stdout | default('')"
  153 |   failed_when: false
  154 | 
  155 | - name: Create additional domain users
  156 |   become: true
  157 |   ansible.builtin.command:
  158 |     cmd: >
  159 |       docker compose exec -T admin flask mailu user
  160 |       {{ item.1.user }} {{ item.0.domain }} {{ item.1.password }}
  161 |   args:
  162 |     chdir: "{{ mailu_install_path }}"
  163 |   loop: "{{ mailu_additional_domains | default([]) | subelements('users') }}"
  164 |   register: mailu_user_result
  165 |   changed_when: false
  166 |   failed_when: false # May fail if user exists
  167 |   no_log: true # Hide passwords
  168 | 
  169 | - name: Create mail aliases
  170 |   become: true
  171 |   ansible.builtin.command:
  172 |     cmd: >
  173 |       docker compose exec -T admin flask mailu alias
  174 |       {{ item.local }} {{ item.domain }} {{ item.destination }}
  175 |   args:
  176 |     chdir: "{{ mailu_install_path }}"
  177 |   loop: "{{ mailu_aliases | default([]) }}"
  178 |   register: mailu_alias_result
  179 |   changed_when: false # Can't reliably detect from looped command
  180 |   failed_when: false # May fail if alias exists
  181 |   # No no_log here, unlike the user-creation tasks above: local/domain/destination
  182 |   # are an alias routing rule, not a credential - nothing here is a secret worth
  183 |   # hiding from the run output.
  184 | 
  185 | # `<domain>.dkim.key` is the PRIVATE key. These tasks used to cat it and print
  186 | # the result labelled "add this to DNS", which both leaked the signing key to
  187 | # stdout/CI logs and was useless as a DNS value. Derive the public half
  188 | # instead - that is what belongs in the TXT record.
  189 | - name: Get DKIM public key
  190 |   become: true
  191 |   ansible.builtin.shell:
  192 |     cmd: >
  193 |       set -o pipefail &&
  194 |       openssl rsa -in "{{ mailu_install_path }}/dkim/{{ mailu_domain }}.dkim.key"
  195 |       -pubout -outform DER 2>/dev/null | base64 -w0
  196 |   args:
  197 |     executable: /bin/bash
  198 |   register: mailu_dkim_key
  199 |   changed_when: false
  200 |   failed_when: false
  201 | 
  202 | - name: Display DKIM key for DNS
  203 |   ansible.builtin.debug:
  204 |     msg: |
  205 |       Add this DKIM record to DNS:
  206 |       Name: dkim._domainkey.{{ mailu_domain }}
  207 |       Type: TXT
  208 |       Value: v=DKIM1; k=rsa; p={{ mailu_dkim_key.stdout | trim }}
  209 |   when: mailu_dkim_key.stdout | default('') | trim | length > 0
  210 | 
  211 | # The lookup above sets failed_when: false, so a missing key or an openssl failure is
  212 | # silent. Without this, "no key yet" and "key printed fine" look identical in the run
  213 | # output — on a role whose entire purpose here is surfacing the record an operator has
  214 | # to paste into DNS. Say so explicitly rather than skipping quietly.
  215 | - name: Report that the DKIM key is not available yet
  216 |   ansible.builtin.debug:
  217 |     msg: >-
  218 |       No DKIM public key could be read for {{ mailu_domain }}
  219 |       ({{ mailu_install_path }}/dkim/{{ mailu_domain }}.dkim.key).
  220 |       Mailu generates it on first start of the admin container, so this is expected on a
  221 |       fresh install — re-run this play once it is up to get the DNS record.
  222 |   when: mailu_dkim_key.stdout | default('') | trim | length == 0
  223 | 
  224 | - name: Get DKIM public keys for additional domains
  225 |   become: true
  226 |   ansible.builtin.shell:
  227 |     cmd: >
  228 |       set -o pipefail &&
  229 |       openssl rsa -in "{{ mailu_install_path }}/dkim/{{ item }}.dkim.key"
  230 |       -pubout -outform DER 2>/dev/null | base64 -w0
  231 |   args:
  232 |     executable: /bin/bash
  233 |   loop: "{{ mailu_additional_domains | default([]) | map(attribute='domain') | list }}"
  234 |   register: mailu_additional_dkim_keys
  235 |   changed_when: false
  236 |   failed_when: false
  237 | 
  238 | - name: Display DKIM keys for additional domains
  239 |   ansible.builtin.debug:
  240 |     msg: |
  241 |       Add this DKIM record to DNS:
  242 |       Name: dkim._domainkey.{{ item.item }}
  243 |       Type: TXT
  244 |       Value: v=DKIM1; k=rsa; p={{ item.stdout | trim }}
  245 |   loop: "{{ mailu_additional_dkim_keys.results | default([]) }}"
  246 |   loop_control:
  247 |     label: "{{ item.item }}"
  248 |   when: item.stdout | default('') | trim | length > 0
  249 | 
  250 | # Same reasoning as the primary domain: silence must not be mistaken for success.
  251 | # loop_control.label keeps the loop output to the domain name — the item here is a
  252 | # command result, and printing it whole is how this role leaked secrets before.
  253 | - name: Report additional domains whose DKIM key is not available yet
  254 |   ansible.builtin.debug:
  255 |     msg: >-
  256 |       No DKIM public key could be read for {{ item.item }}. Mailu generates it on first
  257 |       start of the admin container — re-run this play once it is up.
  258 |   loop: "{{ mailu_additional_dkim_keys.results | default([]) }}"
  259 |   loop_control:
  260 |     label: "{{ item.item }}"
  261 |   when: item.stdout | default('') | trim | length == 0
  262 | 
  263 | # --- Nightly mailu -> nas backup (issue #479) ------------------------------
  264 | #
  265 | # dkim keys, admin sqlite db, mailboxes, and mailu.env - the parts the April
  266 | # server wipe permanently lost. Same pipeline shape as goblog-backup
  267 | # (jasonernst_com role): sqlite snapshot + additive rsync to the nas' rsync
  268 | # daemon over the tailnet. The nas-side prune cron for the db snapshots
  269 | # lives in rustd_backup_nas (nas.yml).
  270 | - name: Ensure sqlite3 and rsync are installed
  271 |   tags: backup
  272 |   become: true
  273 |   ansible.builtin.apt:
  274 |     name: [sqlite3, rsync]
  275 |     state: present
  276 | 
  277 | - name: Create mailu backup directory
  278 |   tags: backup
  279 |   become: true
  280 |   ansible.builtin.file:
  281 |     path: "{{ mailu_backup_local_dir }}"
  282 |     state: directory
  283 |     mode: "700"
  284 |     owner: root
  285 |     group: root
  286 | 
  287 | - name: Write the nas rsync-daemon password file
  288 |   tags: backup
  289 |   become: true
  290 |   ansible.builtin.copy:
  291 |     dest: "{{ mailu_backup_rsync_password_file }}"
  292 |     content: "{{ mailu_backup_nas_rsync_password }}\n"
  293 |     owner: root
  294 |     group: root
  295 |     mode: "0600"
  296 |   no_log: true
  297 | 
  298 | - name: Deploy the backup script
  299 |   tags: backup
  300 |   become: true
  301 |   ansible.builtin.template:
  302 |     src: mailu-backup.sh.j2
  303 |     dest: "{{ mailu_install_path }}/mailu-backup.sh"
  304 |     mode: "0700"
  305 | 
  306 | - name: Deploy the backup systemd service
  307 |   tags: backup
  308 |   become: true
  309 |   ansible.builtin.template:
  310 |     src: mailu-backup.service.j2
  311 |     dest: /etc/systemd/system/mailu-backup.service
  312 |     mode: "0644"
  313 | 
  314 | - name: Deploy the backup systemd timer
  315 |   tags: backup
  316 |   become: true
  317 |   ansible.builtin.template:
  318 |     src: mailu-backup.timer.j2
  319 |     dest: /etc/systemd/system/mailu-backup.timer
  320 |     mode: "0644"
  321 | 
  322 | - name: Enable and start the backup timer
  323 |   tags: backup
  324 |   become: true
  325 |   ansible.builtin.systemd_service:
  326 |     name: mailu-backup.timer
  327 |     enabled: true
  328 |     state: started
  329 |     daemon_reload: true
```

## Visible variable references

```text
350e7b8162778ad7beab8e2da8be53ea24a1127a:ansible/roles/mailu/tasks/main.yml:178:  register: mailu_alias_result
```

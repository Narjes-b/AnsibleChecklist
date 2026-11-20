# Frozen source context: V007PILOT-STRUCTURE_REUSE-043

- Repository: `dryvist/ansible-proxmox-apps`
- Commit: `b179574eb875a6b7be09df83d001f623a68a2681`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/postgres/tasks/pgbackrest.yml` (reported anchor line 1)
- Object: `source_location` `06985f2077afa3e863f920019b55029743cae23b9728591f415a63f7a3e0a25a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–359 of 359:

```text
    1 | ---
    2 | # Object-storage PITR tier: pgBackRest archives WAL continuously and takes
    3 | # scheduled base backups to an S3-compatible endpoint (repo1 = RustFS, and the
    4 | # offsite repo2 when enabled — pgBackRest writes both itself; an out-of-band
    5 | # mirror used to fill that role and silently copied a truncated subset, #1027).
    6 | # Archiving and base backups are primary-only — a standby's WAL arrives via
    7 | # streaming, and archive_command runs on the primary. The standby still gets the
    8 | # config file, and gives up any backup timer it kept from an earlier primary
    9 | # role; see the standby block below. Statically imported from
   10 | # main.yml after the cluster is up and the version fact is set, so inner block
   11 | # tags (never,pgbackrest_restore) behave exactly like inline tasks.
   12 | 
   13 | - name: Configure pgBackRest object-storage PITR backups
   14 |   when:
   15 |     - postgres_pgbackrest_enabled | bool
   16 |     - postgres_role == 'primary'
   17 |   block:
   18 |     - name: Assert the pgBackRest S3 endpoint and credentials are set
   19 |       ansible.builtin.assert:
   20 |         that:
   21 |           - postgres_backup_s3_endpoint | length > 0
   22 |           - postgres_backup_s3_access_key_id | length > 0
   23 |           - postgres_backup_s3_secret_access_key | length > 0
   24 |         fail_msg: >-
   25 |           pgBackRest is enabled but the S3 endpoint/credentials are unset. Set
   26 |           POSTGRES_BACKUP_S3_ENDPOINT, POSTGRES_BACKUP_S3_ACCESS_KEY_ID, and
   27 |           POSTGRES_BACKUP_S3_SECRET_ACCESS_KEY.
   28 |         quiet: true
   29 | 
   30 |     - name: Assert the offsite (repo2) endpoint and credentials are set
   31 |       ansible.builtin.assert:
   32 |         that:
   33 |           - postgres_backup_repo2_s3_endpoint | length > 0
   34 |           - postgres_backup_repo2_s3_access_key_id | length > 0
   35 |           - postgres_backup_repo2_s3_secret_access_key | length > 0
   36 |         fail_msg: >-
   37 |           The offsite repo2 is enabled but its endpoint/credentials are unset.
   38 |           Set POSTGRES_BACKUP_REPO2_S3_ENDPOINT,
   39 |           POSTGRES_BACKUP_REPO2_S3_ACCESS_KEY_ID, and
   40 |           POSTGRES_BACKUP_REPO2_S3_SECRET_ACCESS_KEY.
   41 |         quiet: true
   42 |       when: postgres_pgbackrest_repo2_enabled | bool
   43 | 
   44 |     # A cipher with an empty passphrase is worse than no cipher: pgBackRest
   45 |     # would refuse at stanza-create, and if it did not, every backup written
   46 |     # under it would be unrecoverable. Fail here rather than render a config
   47 |     # that promises encryption it cannot deliver.
   48 |     - name: Assert a cipher passphrase exists wherever a cipher is enabled
   49 |       ansible.builtin.assert:
   50 |         that:
   51 |           - >-
   52 |             postgres_pgbackrest_repo1_cipher_type == 'none'
   53 |             or postgres_pgbackrest_repo1_cipher_pass | length > 0
   54 |           - >-
   55 |             postgres_pgbackrest_repo2_cipher_type == 'none'
   56 |             or postgres_pgbackrest_repo2_cipher_pass | length > 0
   57 |         fail_msg: >-
   58 |           A pgBackRest cipher type is set but its passphrase is empty. Set
   59 |           POSTGRES_PGBACKREST_REPO1_CIPHER_PASS and/or
   60 |           POSTGRES_PGBACKREST_REPO2_CIPHER_PASS. Store the passphrase OFF the
   61 |           guest and confirm it is readable BEFORE the stanza is created — a
   62 |           passphrase that lives only on the guest makes every backup
   63 |           unreadable the moment the guest is lost.
   64 |         quiet: true
   65 | 
   66 |     - name: Install pgBackRest
   67 |       ansible.builtin.apt:
   68 |         name: pgbackrest
   69 |         state: present
   70 |         update_cache: true
   71 | 
   72 |     - name: Create the pgBackRest config directory
   73 |       ansible.builtin.file:
   74 |         path: /etc/pgbackrest
   75 |         state: directory
   76 |         owner: postgres
   77 |         group: postgres
   78 |         mode: "0750"
   79 | 
   80 |     # Async archiving writes its acknowledgement files here (not WAL — the
   81 |     # background process reads segments from pg_wal directly). pgBackRest does
   82 |     # not create it, and archive-push fails outright if it is missing.
   83 |     - name: Create the pgBackRest spool directory
   84 |       ansible.builtin.file:
   85 |         path: "{{ postgres_pgbackrest_spool_path }}"
   86 |         state: directory
   87 |         owner: postgres
   88 |         group: postgres
   89 |         mode: "0750"
   90 |       when: postgres_pgbackrest_archive_async | bool
   91 | 
   92 |     - name: Deploy the pgBackRest configuration
   93 |       ansible.builtin.template:
   94 |         src: pgbackrest.conf.j2
   95 |         dest: /etc/pgbackrest/pgbackrest.conf
   96 |         owner: postgres
   97 |         group: postgres
   98 |         mode: "0640"
   99 |       no_log: true
  100 | 
  101 |     - name: Configure WAL archiving GUCs for pgBackRest
  102 |       become: true
  103 |       become_user: postgres
  104 |       block:
  105 |         - name: Ensure wal_level supports archiving
  106 |           community.postgresql.postgresql_set:
  107 |             name: wal_level
  108 |             value: replica
  109 |           notify: Restart postgresql
  110 | 
  111 |         - name: Enable WAL archiving
  112 |           community.postgresql.postgresql_set:
  113 |             name: archive_mode
  114 |             value: "on"
  115 |           notify: Restart postgresql
  116 | 
  117 |         - name: Point archive_command at pgBackRest
  118 |           community.postgresql.postgresql_set:
  119 |             name: archive_command
  120 |             value: "pgbackrest --stanza={{ postgres_pgbackrest_stanza }} archive-push %p"
  121 |           notify: Restart postgresql
  122 | 
  123 |         # Reload, not restart: archive_timeout is SIGHUP-settable, unlike
  124 |         # archive_mode above.
  125 |         - name: Bound the archive lag on an idle cluster
  126 |           community.postgresql.postgresql_set:
  127 |             name: archive_timeout
  128 |             value: "{{ postgres_archive_timeout }}"
  129 |           notify: Reload postgresql
  130 | 
  131 |     # archive_mode only takes effect after a restart, and stanza-create/check
  132 |     # below need archiving live, so flush the restart before touching the repo.
  133 |     - name: Apply pending archiving restart
  134 |       ansible.builtin.meta: flush_handlers
  135 | 
  136 |     # stanza-create is idempotent and PER-REPO: on an existing host it reports
  137 |     # "stanza '<name>' already exists on repo1 and is valid" (rc=0) while still
  138 |     # initializing any repo that lacks it. So it runs unconditionally.
  139 |     #
  140 |     # It used to be gated on `pgbackrest info`, which broke two ways. `info`
  141 |     # reports the stanza as present if it exists in ANY repo, so enabling repo2
  142 |     # on an existing host skipped creation and left the offsite repo
  143 |     # uninitialized. And `info` exits 0 with a stub for a missing stanza, so on a
  144 |     # fresh host the gate never fired at all (#1037).
  145 |     - name: Create the pgBackRest stanza in every configured repo
  146 |       become: true
  147 |       become_user: postgres
  148 |       ansible.builtin.command:
  149 |         argv:
  150 |           - pgbackrest
  151 |           - --stanza={{ postgres_pgbackrest_stanza }}
  152 |           - stanza-create
  153 |       register: postgres_pgbackrest_stanza_create
  154 |       changed_when: >-
  155 |         'already exists' not in
  156 |         ((postgres_pgbackrest_stanza_create.stdout | default(''))
  157 |          ~ (postgres_pgbackrest_stanza_create.stderr | default('')))
  158 | 
  159 |     # `check` validates archiving against every configured repo, so enabling
  160 |     # repo2 extends this gate to the offsite copy automatically. Do NOT swap it
  161 |     # for `pgbackrest verify`: verify exits 0 against a repo it cannot read at
  162 |     # all, printing only "No usable backup.info file" — a wrong-credential
  163 |     # negative control produced output identical to a real run (#1027).
  164 |     - name: Verify pgBackRest archiving is healthy
  165 |       become: true
  166 |       become_user: postgres
  167 |       ansible.builtin.command:
  168 |         argv:
  169 |           - pgbackrest
  170 |           - --stanza={{ postgres_pgbackrest_stanza }}
  171 |           - check
  172 |       changed_when: false
  173 | 
  174 |     # WAL alone restores nothing — replay needs a base backup to replay ONTO.
  175 |     # The timers below only schedule one (the first full lands at the next
  176 |     # Sunday 01:00), so a stanza created on a Monday archives WAL for six days
  177 |     # while being completely unrestorable. `check` does not catch it: it
  178 |     # validates archiving, not the presence of a backup.
  179 |     #
  180 |     # `info --output=json` is safe here specifically because stanza-create ran
  181 |     # first — the "info stubs a missing stanza" trap (#1037) needs a stanza that
  182 |     # was never created. A fresh stanza reports an empty `backup` list.
  183 |     - name: Check whether the stanza already holds a base backup
  184 |       become: true
  185 |       become_user: postgres
  186 |       ansible.builtin.command:
  187 |         argv:
  188 |           - pgbackrest
  189 |           - --stanza={{ postgres_pgbackrest_stanza }}
  190 |           - --output=json
  191 |           - info
  192 |       register: postgres_pgbackrest_info
  193 |       changed_when: false
  194 | 
  195 |     # Only ever on an empty stanza, so this is a one-time cost at bring-up, not
  196 |     # something every converge pays. Expect it to take as long as a full base
  197 |     # backup of the cluster.
  198 |     - name: Take the initial full backup so PITR has a base to replay onto
  199 |       become: true
  200 |       become_user: postgres
  201 |       ansible.builtin.command:
  202 |         argv:
  203 |           - pgbackrest
  204 |           - --stanza={{ postgres_pgbackrest_stanza }}
  205 |           - --type=full
  206 |           - backup
  207 |       # No `first`: info returns a bare [] for a stanza it cannot see, and
  208 |       # indexing that raises instead of taking the branch. The default('[]')
  209 |       # keeps check mode (where the command above is skipped and registers no
  210 |       # stdout) from erroring here too.
  211 |       when: >-
  212 |         ((postgres_pgbackrest_info.stdout | default('[]', true) | from_json
  213 |           | map(attribute='backup') | flatten | length) == 0)
  214 |       changed_when: true
  215 | 
  216 |     - name: Deploy the instanced pgBackRest backup service
  217 |       ansible.builtin.template:
  218 |         src: pgbackrest-backup@.service.j2
  219 |         dest: /etc/systemd/system/pgbackrest-backup@.service
  220 |         owner: root
  221 |         group: root
  222 |         mode: "0644"
  223 | 
  224 |     - name: Deploy a pgBackRest backup timer per schedule
  225 |       ansible.builtin.template:
  226 |         src: pgbackrest-backup@.timer.j2
  227 |         dest: "/etc/systemd/system/pgbackrest-backup@{{ item.type }}.timer"
  228 |         owner: root
  229 |         group: root
  230 |         mode: "0644"
  231 |       loop: "{{ postgres_pgbackrest_schedules }}"
  232 |       loop_control:
  233 |         label: "{{ item.type }}"
  234 | 
  235 |     - name: Enable and start each pgBackRest backup timer
  236 |       ansible.builtin.systemd:
  237 |         name: "pgbackrest-backup@{{ item.type }}.timer"
  238 |         state: started
  239 |         enabled: true
  240 |         daemon_reload: true
  241 |       loop: "{{ postgres_pgbackrest_schedules }}"
  242 |       loop_control:
  243 |         label: "{{ item.type }}"
  244 | 
  245 | # =============================================================================
  246 | # Standby side of the same tier. Only the primary archives WAL and takes base
  247 | # backups — a standby's WAL arrives by streaming — but the standby is NOT left
  248 | # unmanaged, because two things follow it across a role change and both write to
  249 | # the repo if ignored.
  250 | #
  251 | # The config file: a standby bootstrapped from a base backup inherits the
  252 | # primary's archive_command, naming the CLUSTER's stanza. Skipping the standby
  253 | # leaves its config file defining some other stanza, so the two disagree until
  254 | # the host is promoted — at which point it archives under a name its own config
  255 | # does not define. Rendering the same template here makes the file agree with
  256 | # the archive_command the host already carries, and makes a promotion continue
  257 | # the cluster's existing backup history instead of opening a second stanza.
  258 | #
  259 | # The timers: a host demoted from primary to standby keeps whatever backup
  260 | # timers it was given, and goes on running base backups against a stanza it no
  261 | # longer owns. Nothing else removes them, so this does.
  262 | # =============================================================================
  263 | - name: Keep pgBackRest consistent but inert on a standby
  264 |   when:
  265 |     - postgres_pgbackrest_enabled | bool
  266 |     - postgres_role == 'standby'
  267 |   block:
  268 |     - name: Install pgBackRest
  269 |       ansible.builtin.apt:
  270 |         name: pgbackrest
  271 |         state: present
  272 |         update_cache: true
  273 | 
  274 |     - name: Create the pgBackRest config directory
  275 |       ansible.builtin.file:
  276 |         path: /etc/pgbackrest
  277 |         state: directory
  278 |         owner: postgres
  279 |         group: postgres
  280 |         mode: "0750"
  281 | 
  282 |     - name: Deploy the pgBackRest configuration
  283 |       ansible.builtin.template:
  284 |         src: pgbackrest.conf.j2
  285 |         dest: /etc/pgbackrest/pgbackrest.conf
  286 |         owner: postgres
  287 |         group: postgres
  288 |         mode: "0640"
  289 |       no_log: true
  290 | 
  291 |     # Discovered rather than derived from postgres_pgbackrest_schedules: the
  292 |     # schedule list may have changed since this host was a primary, and a timer
  293 |     # for a since-removed schedule is exactly the one left running.
  294 |     - name: Find pgBackRest backup timers left over from a primary role
  295 |       ansible.builtin.find:
  296 |         paths: /etc/systemd/system
  297 |         patterns: pgbackrest-backup@*.timer
  298 |       register: postgres_pgbackrest_stale_timers
  299 | 
  300 |     - name: Stop and disable each leftover pgBackRest backup timer
  301 |       ansible.builtin.systemd:
  302 |         name: "{{ item.path | basename }}"
  303 |         state: stopped
  304 |         enabled: false
  305 |       loop: "{{ postgres_pgbackrest_stale_timers.files }}"
  306 |       loop_control:
  307 |         label: "{{ item.path | basename }}"
  308 | 
  309 |     - name: Remove the leftover pgBackRest backup units
  310 |       ansible.builtin.file:
  311 |         path: "{{ item }}"
  312 |         state: absent
  313 |       loop: >-
  314 |         {{ (postgres_pgbackrest_stale_timers.files | map(attribute='path') | list)
  315 |            + ['/etc/systemd/system/pgbackrest-backup@.service'] }}
  316 |       notify: Reload systemd daemon
  317 | 
  318 | # =============================================================================
  319 | # PITR restore (explicit invocation only — the object-storage tier's restore
  320 | # drill). Restores the repo into PGDATA and replays WAL to the latest committed
  321 | # transaction, or to a pinned target when postgres_pgbackrest_restore_target is
  322 | # set:
  323 | #   ansible-playbook ... --tags pgbackrest_restore \
  324 | #     -e postgres_pgbackrest_enabled=true -e postgres_pgbackrest_restore=true \
  325 | #     [-e postgres_pgbackrest_restore_target='2026-07-16 12:00:00+00']
  326 | # Point a drill at a scratch cluster/stanza — restoring here overwrites PGDATA.
  327 | # =============================================================================
  328 | # Var-gated in addition to the `never` tag: the role include's `postgres` tag is
  329 | # inherited here, so a plain `--tags postgres` converge would otherwise select
  330 | # it; the postgres_pgbackrest_restore=false default is what keeps it inert.
  331 | - name: Restore PostgreSQL from pgBackRest
  332 |   when:
  333 |     - postgres_pgbackrest_enabled | bool
  334 |     - postgres_role == 'primary'
  335 |     - postgres_pgbackrest_restore | bool
  336 |   tags:
  337 |     - never
  338 |     - pgbackrest_restore
  339 |   block:
  340 |     - name: Stop the cluster before restoring
  341 |       ansible.builtin.systemd:
  342 |         name: "postgresql@{{ postgres_cluster_version }}-{{ postgres_cluster_name }}"
  343 |         state: stopped
  344 | 
  345 |     - name: Restore the repository into PGDATA (delta)
  346 |       become: true
  347 |       become_user: postgres
  348 |       ansible.builtin.command:
  349 |         argv: >-
  350 |           {{ ['pgbackrest', '--stanza=' ~ postgres_pgbackrest_stanza, '--delta', 'restore']
  351 |              + (['--type=' ~ postgres_pgbackrest_restore_target_type,
  352 |                  '--target=' ~ postgres_pgbackrest_restore_target]
  353 |                 if (postgres_pgbackrest_restore_target | length > 0) else []) }}
  354 |       changed_when: true
  355 | 
  356 |     - name: Start the cluster to replay WAL
  357 |       ansible.builtin.systemd:
  358 |         name: "postgresql@{{ postgres_cluster_version }}-{{ postgres_cluster_name }}"
  359 |         state: started
```

## Frozen tracked paths in the relevant role/scope

```text
roles/postgres/defaults/main/00-install-and-backup.yml
roles/postgres/defaults/main/01-replication.yml
roles/postgres/defaults/main/02-pgbackrest.yml
roles/postgres/handlers/main.yml
roles/postgres/meta/main.yml
roles/postgres/tasks/main.yml
roles/postgres/tasks/main/cluster_config.yml
roles/postgres/tasks/main/health_check.yml
roles/postgres/tasks/main/install_and_create_cluster.yml
roles/postgres/tasks/main/install_pgdg.yml
roles/postgres/tasks/main/pg_dump_backups.yml
roles/postgres/tasks/main/pitr_and_dr.yml
roles/postgres/tasks/main/replication_primary.yml
roles/postgres/tasks/main/roles_and_databases.yml
roles/postgres/tasks/main/standby_bootstrap.yml
roles/postgres/tasks/main/verify_topology.yml
roles/postgres/tasks/pgbackrest.yml
roles/postgres/templates/pg-backup.service.j2
roles/postgres/templates/pg-backup.sh.j2
roles/postgres/templates/pg-backup.timer.j2
roles/postgres/templates/pgbackrest-backup@.service.j2
roles/postgres/templates/pgbackrest-backup@.timer.j2
roles/postgres/templates/pgbackrest.conf.j2
```

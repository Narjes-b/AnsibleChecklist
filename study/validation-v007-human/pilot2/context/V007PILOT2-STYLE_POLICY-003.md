# Frozen source context: V007PILOT2-STYLE_POLICY-003

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: style_policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `automation/roles/common/defaults/main.yml` (reported anchor line 519)
- Flagged construct: not named by the finding; the anchor line 519 lies in the task at line 510, name `pg_auto_reindexer: weekdays`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 419–619 of 1448:

```text
  419 |   - { option: "track_activity_query_size", value: "4096" }
  420 |   - { option: "track_counts", value: "on" }
  421 |   - { option: "track_functions", value: "all" }
  422 |   - { option: "log_lock_waits", value: "on" }
  423 |   - { option: "log_temp_files", value: "0" }
  424 |   - { option: "log_checkpoints", value: "on" }
  425 |   - { option: "log_rotation_age", value: "1d" }
  426 |   - { option: "log_rotation_size", value: "0" }
  427 |   - { option: "log_line_prefix", value: "%t [%p-%l] %r %q%u@%d " }
  428 |   - { option: "log_filename", value: "postgresql-%a.log" }
  429 |   - { option: "log_directory", value: "{{ postgresql_log_dir }}" }
  430 |   - { option: "log_truncate_on_rotation", value: "on" }
  431 |   - { option: "logging_collector", value: "on" }
  432 |   - { option: "jit", value: "off" }
  433 |   - { option: "max_files_per_process", value: "4096" }
  434 |   - { option: "max_worker_processes", value: "{{ [ansible_processor_vcpus | int, 16] | max }}" }
  435 |   - { option: "max_parallel_workers", value: "{{ [(ansible_processor_vcpus | int // 2), 8] | max }}" }
  436 |   - { option: "max_parallel_workers_per_gather", value: "2" }
  437 |   - { option: "max_parallel_maintenance_workers", value: "2" }
  438 |   - { option: "tcp_keepalives_count", value: "10" }
  439 |   - { option: "tcp_keepalives_idle", value: "300" }
  440 |   - { option: "tcp_keepalives_interval", value: "30" }
  441 |   - { option: "idle_in_transaction_session_timeout", value: "10min" } # reduce this timeout if possible
  442 | #  - { option: "", value: "" }
  443 | 
  444 | # PostgreSQL parameter overrides (cluster-wide, stored in DCS).
  445 | # Use this to add or override a small number of options without redefining the full 'postgresql_parameters' list.
  446 | postgresql_parameters_overrides: []
  447 | #  - { option: "transaction_timeout", value: "10min" } # reduce this timeout if possible
  448 | #  - { option: "statement_timeout", value: "1min" } # reduce this timeout if possible
  449 | #  - { option: "lock_timeout", value: "10s" } # reduce this timeout if possible
  450 | #  - { option: "deadlock_timeout", value: "2s" }
  451 | #  - { option: "", value: "" }
  452 | 
  453 | # Host-level PostgreSQL parameters are defined locally in patroni.yml and override the common ones stored in DCS.
  454 | local_postgresql_parameters: []
  455 | # - { option: "shared_buffers", value: "{{ (ansible_memtotal_mb * 0.25) | int }}MB" }
  456 | # - { option: "effective_cache_size", value: "{{ (ansible_memtotal_mb * 0.75) | int }}MB" }
  457 | 
  458 | # Final PostgreSQL parameters (cluster-wide, stored in DCS).
  459 | postgresql_parameters_dcs: >-
  460 |   {{
  461 |     postgresql_parameters | default([])
  462 |     | community.general.lists_mergeby(postgresql_parameters_overrides | default([]), 'option')
  463 |   }}
  464 | 
  465 | # Set this variable to 'true' if you want the cluster to be automatically restarted
  466 | # after changing the 'postgresql_parameters' variable that requires a restart in the 'config_pgcluster.yml' playbook.
  467 | # By default, the cluster will not be automatically restarted.
  468 | pending_restart: false
  469 | 
  470 | # specify additional hosts that will be added to the pg_hba.conf
  471 | postgresql_pg_hba:
  472 |   - { type: "local", database: "all", user: "{{ patroni_superuser_username }}", address: "", method: "trust" }
  473 |   - { type: "local", database: "all", user: "{{ pgbouncer_auth_username }}", address: "", method: "trust" }
  474 |   - { type: "local", database: "all", user: "all", address: "", method: "{{ postgresql_password_encryption_algorithm }}" }
  475 |   - { type: "host", database: "all", user: "all", address: "127.0.0.1/32", method: "{{ postgresql_password_encryption_algorithm }}" }
  476 |   - { type: "host", database: "all", user: "all", address: "::1/128", method: "{{ postgresql_password_encryption_algorithm }}" }
  477 |   - { type: "{{ host_type }}", database: "all", user: "all", address: "0.0.0.0/0", method: "{{ postgresql_password_encryption_algorithm }}" }
  478 | #  - { type: "{{ host_type }}", database: "mydatabase", user: "mydb-user", address: "192.168.0.0/24", method: "{{ postgresql_password_encryption_algorithm }}" }
  479 | #  - { type: "{{ host_type }}", database: "all", user: "all", address: "192.168.0.0/24", method: "ident", options: "map=main" }  # use pg_ident
  480 | 
  481 | # Specify authentication method for local connections: via socket if enabled, or 127.0.0.1
  482 | # Replace with "{{ postgresql_password_encryption_algorithm }}" to require a password for local connections to the replication user
  483 | postgresql_local_replication_auth_method: "trust"
  484 | 
  485 | host_type: "{{ 'hostssl' if tls_cert_generate | bool else 'host' }}"
  486 | 
  487 | # list of lines that Patroni will use to generate pg_ident.conf
  488 | postgresql_pg_ident: []
  489 | #  - { mapname: "main", system_username: "postgres", pg_username: "backup" }
  490 | #  - { mapname: "", system_username: "", pg_username: "" }
  491 | 
  492 | # the password file (~/.pgpass)
  493 | postgresql_pgpass:[REDACTED VALUE BLOCK]
  494 |   [REDACTED ENCRYPTED VALUE]
      [... 2 further identical redacted lines, through 496]
  497 | #  - hostname:port:database:username:password
  498 | 
  499 | # Index maintenance
  500 | # Automatic reindexing of PostgreSQL indexes (bloat cleanup) using pg_auto_reindexer
  501 | postgresql_index_maintenance:
  502 |   enabled: "{{ postgresql_index_maintenance_enabled | default(true) }}"
  503 |   start: "0000" # start time for index maintenance in HHMM format
  504 |   stop: "0600" # stop time for index maintenance in HHMM format
  505 |   bloat_threshold: 30 # percentage of bloat for reindexing
  506 |   size_threshold: 1024 # index size in MB for reindexing
  507 |   jobs: 1 # number of parallel workers (no more than max_parallel_workers parameter)
  508 | 
  509 | postgresql_index_maintenance_cron_jobs:
  510 |   - name: "pg_auto_reindexer: weekdays"
  511 |     user: "root"
  512 |     file: "/etc/cron.d/pg_auto_reindexer"
  513 |     minute: "{{ postgresql_index_maintenance.start[2:4] }}"
  514 |     hour: "{{ postgresql_index_maintenance.start[0:2] }}"
  515 |     day: "*"
  516 |     month: "*"
  517 |     weekday: "1-5"
  518 |     state: "{{ 'present' if postgresql_index_maintenance.enabled | bool else 'absent' }}"
  519 |     job: "/usr/local/bin/pg_auto_reindexer --jobs={{ postgresql_index_maintenance.jobs }} --index-bloat={{ postgresql_index_maintenance.bloat_threshold }} --index-maxsize={{ postgresql_index_maintenance.size_threshold }} --maintenance-start={{ postgresql_index_maintenance.start }} --maintenance-stop={{ postgresql_index_maintenance.stop }}" # yamllint disable rule:line-length
  520 |   - name: "pg_auto_reindexer: weekends"
  521 |     user: "root"
  522 |     file: "/etc/cron.d/pg_auto_reindexer"
  523 |     minute: "{{ postgresql_index_maintenance.start[2:4] }}"
  524 |     hour: "{{ postgresql_index_maintenance.start[0:2] }}"
  525 |     day: "*"
  526 |     month: "*"
  527 |     weekday: "6,0"
  528 |     state: "{{ 'present' if postgresql_index_maintenance.enabled | bool else 'absent' }}"
  529 |     job: "/usr/local/bin/pg_auto_reindexer --jobs={{ postgresql_index_maintenance.jobs }} --index-bloat={{ postgresql_index_maintenance.bloat_threshold }} --index-minsize={{ postgresql_index_maintenance.size_threshold }} --maintenance-start={{ postgresql_index_maintenance.start }} --maintenance-stop={{ postgresql_index_maintenance.stop }}" # yamllint disable rule:line-length
  530 | 
  531 | ############################################################
  532 | # PgBouncer parameters
  533 | ############################################################
  534 | 
  535 | pgbouncer_install: true # or 'false' if you do not want to install and configure the pgbouncer service
  536 | pgbouncer_processes: 1 # Number of pgbouncer processes to be used. Multiple processes use the so_reuseport option for better performance.
  537 | pgbouncer_conf_dir: "/etc/pgbouncer"
  538 | pgbouncer_log_dir: "/var/log/pgbouncer"
  539 | pgbouncer_listen_addr: "0.0.0.0" # Listen on all interfaces. Or use "{{ bind_address }}" to listen on a specific IP address.
  540 | pgbouncer_listen_port: 6432
  541 | pgbouncer_max_client_conn: 100000
  542 | pgbouncer_max_db_connections: 10000
  543 | pgbouncer_max_prepared_statements: 1024
  544 | pgbouncer_query_wait_timeout: 120
  545 | pgbouncer_default_pool_size: 100
  546 | pgbouncer_default_pool_mode: "session"
  547 | pgbouncer_admin_users: "{{ patroni_superuser_username }}" # comma-separated list of users, who are allowed to change settings
  548 | pgbouncer_stats_users: "{{ patroni_superuser_username }}" # comma-separated list of users who are just allowed to use SHOW command
  549 | pgbouncer_ignore_startup_parameters: "extra_float_digits,geqo,search_path"
  550 | pgbouncer_auth_type: "{{ postgresql_password_encryption_algorithm }}"
  551 | pgbouncer_auth_user: true # or 'false' if you want to manage the list of users for authentication in the database via userlist.txt
  552 | pgbouncer_auth_username: pgbouncer # user who can query the database via the user_search function
  553 | pgbouncer_auth_password: [REDACTED_LITERAL]
  554 | pgbouncer_auth_dbname: "postgres"
  555 | pgbouncer_tls_dir: "{{ tls_dir }}"
  556 | pgbouncer_client_tls_sslmode: "{{ 'require' if tls_cert_generate | bool else 'disable' }}"
  557 | pgbouncer_client_tls_key_file: "{{ tls_privatekey }}"
  558 | pgbouncer_client_tls_cert_file: "{{ tls_cert }}"
  559 | pgbouncer_client_tls_ca_file: "{{ tls_ca_cert }}"
  560 | pgbouncer_client_tls_protocols: "secure" # allowed values: tlsv1.0, tlsv1.1, tlsv1.2, tlsv1.3, all, secure (tlsv1.2,tlsv1.3)
  561 | pgbouncer_client_tls_ciphers: "secure" # allowed values: default, secure, fast, normal, all (not recommended)
  562 | pgbouncer_server_tls_sslmode: "{{ 'require' if tls_cert_generate | bool else 'disable' }}"
  563 | pgbouncer_server_tls_protocols: "secure"
  564 | pgbouncer_server_tls_ciphers: "secure"
  565 | pgbouncer_server_tls_key_file: "{{ tls_privatekey }}"
  566 | pgbouncer_server_tls_cert_file: "{{ tls_cert }}"
  567 | pgbouncer_server_tls_ca_file: "{{ tls_ca_cert }}"
  568 | 
  569 | pgbouncer_pools:
  570 |   - { name: "postgres", dbname: "postgres", pool_parameters: "" }
  571 | #  - { name: "mydatabase", dbname: "mydatabase", pool_parameters: "pool_size=20 pool_mode=transaction" }
  572 | #  - { name: "", dbname: "", pool_parameters: "" }
  573 | #  - { name: "", dbname: "", pool_parameters: "" }
  574 | 
  575 | ############################################################
  576 | # Patroni parameters
  577 | ############################################################
  578 | 
  579 | patroni_restapi_protocol: "{{ 'https' if tls_cert_generate | bool else 'http' }}"
  580 | patroni_restapi_certfile: "{{ tls_dir ~ '/' ~ tls_cert if patroni_restapi_protocol == 'https' else omit }}"
  581 | patroni_restapi_keyfile: "{{ tls_dir ~ '/' ~ tls_privatekey if patroni_restapi_protocol == 'https' else omit }}"
  582 | patroni_restapi_cafile: "{{ tls_dir ~ '/' ~ tls_ca_cert if patroni_restapi_protocol == 'https' else omit }}"
  583 | # patroni_restapi_connect_addr: "{{ ansible_hostname }}" # or 'ansible_fqdn'. Set if you need connection to be established by domain name, not IP.
  584 | patroni_restapi_listen_addr: "0.0.0.0" # Listen on all interfaces. Or use "{{ bind_address }}" to listen on a specific IP address.
  585 | patroni_restapi_port: 8008
  586 | patroni_restapi_username: "patroni"
  587 | patroni_restapi_password: [REDACTED_LITERAL]
  588 | patroni_restapi_request_queue_size: 5
  589 | patroni_ttl: 30
  590 | patroni_loop_wait: 10
  591 | patroni_retry_timeout: 10
  592 | patroni_master_start_timeout: 300
  593 | patroni_maximum_lag_on_failover: 1048576 # (1MB) the maximum bytes a follower may lag to be able to participate in leader election.
  594 | patroni_maximum_lag_on_replica: "100MB" # the maximum of lag that replica can be in order to be available for read-only queries.
  595 | patroni_failsafe_mode: true # enable Patroni DCS failsafe mode
  596 | 
  597 | patroni_use_unix_socket: true # specifies that Patroni should prefer to use unix sockets to connect to the cluster.
  598 | patroni_use_unix_socket_repl: true # specifies that Patroni should prefer to use unix sockets for replication user cluster connection.
  599 | 
  600 | # https://patroni.readthedocs.io/en/latest/yaml_configuration.html#postgresql
  601 | patroni_callbacks: []
  602 | #  - {action: "on_role_change", script: ""}
  603 | #  - {action: "on_stop", script: ""}
  604 | #  - {action: "on_restart", script: ""}
  605 | #  - {action: "on_reload", script: ""}
  606 | #  - {action: "on_role_change", script: ""}
  607 | 
  608 | # https://patroni.readthedocs.io/en/latest/standby_cluster.html
  609 | # Note: In case the remote site doesn’t provide a single endpoint that connects to a primary,
  610 | # one could list all hosts of the source cluster in the patroni_standby_cluster.host (separated by commas).
  611 | patroni_standby_cluster:
  612 |   host: "{{ source_cluster_host | default('') }}" # Source Cluster host (IP address)
  613 |   port: "{{ source_cluster_port | default(5432) }}" # Source Cluster port
  614 | #  primary_slot_name: ""  # which slot on the remote master to use for replication (optional)
  615 | #  restore_command: ""  # command to restore WAL records from the remote master to standby leader (optional)
  616 | #  recovery_min_apply_delay: ""  # how long to wait before actually apply WAL records on a standby leader (optional)
  617 | 
  618 | patroni_standby_cluster_auto_hba: true # automatically add the standby cluster nodes to pg_hba.conf of the source cluster.
  619 | # Note: this is a temporary rule and may be overwritten by future source cluster reconfiguration.
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).

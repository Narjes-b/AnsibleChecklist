# Frozen source context: V007PILOT-STRUCTURE_REUSE-024

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: Structure/reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `automation/roles/upgrade/defaults/main.yml` (reported anchor line 1)
- Object: `source_location` `bd393d784af216205d2a680a5cf7b788af0258e2ab70f86777e34c6115e638f2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–132 of 132:

```text
    1 | # yamllint disable rule:line-length
    2 | ---
    3 | # Variables for the pg_upgrade.yml playbook
    4 | 
    5 | ############################################################
    6 | # Upgrade settings (for both methods)
    7 | ############################################################
    8 | 
    9 | # PostgreSQL versions
   10 | pg_old_version: "" # specify the current (old) version of PostgreSQL
   11 | pg_new_version: "" # specify the target version of PostgreSQL for the upgrade
   12 | 
   13 | # Paths for old and new PostgreSQL versions
   14 | # Adjust these variables if the paths are different from the default value.
   15 | 
   16 | # Directory containing binaries for the old PostgreSQL version.
   17 | pg_old_bindir: "{{ postgresql_bin_dir | regex_replace('(/$)', '') | replace(postgresql_version | string, pg_old_version | string) }}"
   18 | # Data directory path for the old PostgreSQL version.
   19 | pg_old_datadir: "{{ postgresql_data_dir | regex_replace('(/$)', '') | replace(postgresql_version | string, pg_old_version | string) }}"
   20 | # Configuration directory path for the old PostgreSQL version.
   21 | pg_old_confdir: "{{ postgresql_conf_dir | regex_replace('(/$)', '') | replace(postgresql_version | string, pg_old_version | string) }}"
   22 | 
   23 | # Directory containing binaries for the new PostgreSQL version.
   24 | pg_new_bindir: "{{ postgresql_bin_dir | regex_replace('(/$)', '') | replace(postgresql_version | string, pg_new_version | string) }}"
   25 | # Data directory path for the new PostgreSQL version.
   26 | pg_new_datadir: "{{ postgresql_data_dir | regex_replace('(/$)', '') | replace(postgresql_version | string, pg_new_version | string) }}"
   27 | # Configuration directory path for the new PostgreSQL version.
   28 | pg_new_confdir: "{{ postgresql_conf_dir | regex_replace('(/$)', '') | replace(postgresql_version | string, pg_new_version | string) }}"
   29 | # Custom WAL directory for the new PostgreSQL version (symlink will be created) [optional].
   30 | pg_new_wal_dir: "{{ postgresql_wal_dir | regex_replace('(/$)', '') | replace(postgresql_version | string, pg_new_version | string) }}"
   31 | 
   32 | # pg_upper_datadir: Specifies the top-level directory containing both old and new PostgreSQL data directories.
   33 | # The variable is derived from pg_new_datadir by removing any trailing slash and getting its grandparent directory.
   34 | # Adjust if the data directory location differs from the default.
   35 | # Example: /var/lib/postgresql, /var/lib/pgsql, /pgdata
   36 | pg_upper_datadir: "{{ pg_new_datadir | regex_replace('/$', '') | dirname | dirname }}"
   37 | 
   38 | # List of package names for the new PostgreSQL version to be installed.
   39 | # automatically detects the list of packages based on the 'postgresql_packages' variable
   40 | pg_new_packages: "{{ postgresql_packages | map('regex_replace', postgresql_version | string, pg_new_version | string) | list }}"
   41 | 
   42 | # Alternatively, you can explicitly specify the list of new packages to install.
   43 | # This gives you more control and should be used if the automatic update does not meet your needs.
   44 | # Uncomment and modify the following lines according to your requirements. Example:
   45 | # pg_new_packages:
   46 | #  - postgresql-{{ pg_new_version }}
   47 | #  - postgresql-client-{{ pg_new_version }}
   48 | #  - postgresql-server-dev-{{ pg_new_version }}
   49 | #  - postgresql-contrib-{{ pg_new_version }}
   50 | #  - postgresql-{{ pg_new_version }}-repack"
   51 | 
   52 | pg_old_packages_remove: true # remove old postgresql packages after upgrade
   53 | 
   54 | # Timeout (in seconds) to be used when starting/stopping PostgreSQL during the upgrade.
   55 | pg_start_stop_timeout: 1800 # 30 minutes
   56 | 
   57 | # Patroni configuration file path.
   58 | patroni_config_file: /etc/patroni/patroni.yml
   59 | 
   60 | schema_compatibility_check: true # If 'true', a compatibility check of the database schema with the new PostgreSQL version will be performed before the upgrade.
   61 | schema_compatibility_check_port: "{{ (postgresql_port | int) + 1 }}" # Port used to run a temporary PostgreSQL instance for schema compatibility checking.
   62 | schema_compatibility_check_timeout: 3600 # Maximum duration (in seconds) for the compatibility check (using pg_dumpall --schema-only).
   63 | 
   64 | update_extensions: true # if 'true', try to update extensions automatically
   65 | 
   66 | vacuumdb_parallel_jobs: "{{ [ansible_processor_vcpus | int // 2, 1] | max }}" # use 50% CPU cores
   67 | vacuumdb_analyze_timeout: 3600 # seconds. The maximum duration of analyze command (soft limit, exceeding won't halt playbook)
   68 | # terminate active queries that are longer than the specified time (in seconds) during the collection of statistics.
   69 | vacuumdb_analyze_terminate_treshold: 0 # (0 = do not terminate active backends)
   70 | 
   71 | # Do not perform an upgrade/switchover if
   72 | max_replication_lag_bytes: 104857600 # 100 MiB - Maximum allowed replication lag in bytes
   73 | max_transaction_sec: 15 # Maximum allowed duration for a transactions in seconds
   74 | 
   75 | # (optional) Copy any files located in the "files" directory to all servers
   76 | # example for Postgres Full-Text Search (FTS) files
   77 | upgrade_copy_files_to_all_server: []
   78 | #  - { src: "files/numbers.syn", dest: "/usr/share/postgresql/{{ pg_new_version }}/tsearch_data/numbers.syn", owner: "root", group: "root", mode: "0644" }
   79 | #  - { src: "files/part_of_speech_russian.stop", dest: "/usr/share/postgresql/{{ pg_new_version }}/tsearch_data/part_of_speech_russian.stop", owner: "root", group: "root", mode: "0644" }
   80 | #  - { src: "files/ru_ru.affix", dest: "/usr/share/postgresql/{{ pg_new_version }}/tsearch_data/ru_ru.affix", owner: "root", group: "root", mode: "0644" }
   81 | #  - { src: "files/ru_ru.dict", dest: "/usr/share/postgresql/{{ pg_new_version }}/tsearch_data/ru_ru.dict", owner: "root", group: "root", mode: "0644" }
   82 | 
   83 | # if 'pgbouncer_install' is 'true'
   84 | pgbouncer_pool_pause: true # or 'false' if you don't want to pause pgbouncer pools during upgrade.
   85 | # the maximum waiting time (in seconds) for the pool to be paused. For each iteration of the loop when trying to pause all pools.
   86 | pgbouncer_pool_pause_timeout: 2
   87 | # the time (in seconds) after which instead of waiting for the completion of the active queries, the script terminates the slow active queries.
   88 | pgbouncer_pool_pause_terminate_after: 30
   89 | # the time (in seconds) after which the script exit with an error if it was not possible to pause all pgbouncer pools.
   90 | pgbouncer_pool_pause_stop_after: 60
   91 | # wait for the completion of active queries that are executed longer than the specified time (in milliseconds) before trying to pause the pool.
   92 | pg_slow_active_query_treshold: 1000
   93 | # terminate active queries that longer than the specified time (in milliseconds) after reaching "pgbouncer_pool_pause_terminate_after" before trying to pause the pool.
   94 | pg_slow_active_query_treshold_to_terminate: 100 # (0 = terminate all active backends)
   95 | 
   96 | # if 'pgbackrest_install' is 'true'
   97 | pgbackrest_stanza_upgrade: true # perform the "stanza-upgrade" command after the upgrade.
   98 | 
   99 | ############################################################
  100 | # Blue-green deployment method settings
  101 | ############################################################
  102 | 
  103 | pg_replication_database: "all" # database name for the replication, 'all' for the entire database cluster.
  104 | 
  105 | pg_allow_replica_identity_full: true # set REPLICA IDENTITY FULL on tables without primary key.
  106 | 
  107 | pg_publication_count: 1 # number of publications, replication slots and subscriptions to be created for logical replication (source -> target).
  108 | pg_publication_name: "pg_upgrade_publication"
  109 | pg_subscription_name: "pg_upgrade_subscription"
  110 | pg_subscription_slot_name: "{{ pg_subscription_name }}_slot" # base prefix for logical replication slot names; each slot name includes the database name (and _01, _02, ... suffix if pg_publication_count > 1)
  111 | 
  112 | pg_wal_keep_gigabytes: 100 # or 'none' to not change the wal_keep_segments/wal_keep_size parameter.
  113 | # pg_wal_keep_gigabytes - the number of WAL files (in gigabytes) to hold in the source cluster.
  114 | # To guarantee that the necessary WAL files are available to reach recovery_target_lsn via streaming replication for the leader of the target cluster.
  115 | # After performing the upgrade procedure, the parameter will be reset to original state.
  116 | 
  117 | # --------------------------------------
  118 | # Switchover (pg_logical_switchover.yml)
  119 | # --------------------------------------
  120 | pg_switchover_max_replication_lag_bytes: 16777216 # (16 MB) to ensure minimal lag before switchover
  121 | pg_switchover_no_lag_wait_timeout: 10 # (seconds) "Plan A": wait until the logical replication lag is 0 bytes.
  122 | pg_switchover_force_mode: false # "Plan B": switch traffic with a small replication lag.
  123 | pg_switchover_force_mode_lag_bytes: 1048576 # 1 MiB. Allowed lag (in bytes) in force mode.
  124 | 
  125 | # Reverse logical replication (rollback without losing changes)
  126 | pg_reverse_logical_replication: true # enable reverse logical replication (source <- target).
  127 | pg_reverse_publication_name: "reverse_{{ pg_publication_name }}"
  128 | pg_reverse_subscription_name: "reverse_{{ pg_subscription_name }}"
  129 | pg_reverse_subscription_slot_name: "reverse_{{ pg_subscription_slot_name }}"
  130 | 
  131 | # Sequences
  132 | pg_sequences_increase_value: 1000000 # add +N to the current value of the sequences (received from the old cluster) in the new cluster.
```

## Frozen tracked paths in the relevant role/scope

```text
automation/roles/upgrade/README.md
automation/roles/upgrade/defaults/main.yml
automation/roles/upgrade/inventory.example.yml
automation/roles/upgrade/meta/main.yml
automation/roles/upgrade/tasks/checkpoint_location.yml
automation/roles/upgrade/tasks/create_publication.yml
automation/roles/upgrade/tasks/create_subscription.yml
automation/roles/upgrade/tasks/custom_wal_dir.yml
automation/roles/upgrade/tasks/dcs_remove_cluster.yml
automation/roles/upgrade/tasks/drop_publication.yml
automation/roles/upgrade/tasks/drop_replication_slot.yml
automation/roles/upgrade/tasks/drop_subscription.yml
automation/roles/upgrade/tasks/extensions.yml
automation/roles/upgrade/tasks/increase_sequences.yml
automation/roles/upgrade/tasks/initdb.yml
automation/roles/upgrade/tasks/maintenance_disable.yml
automation/roles/upgrade/tasks/maintenance_enable.yml
automation/roles/upgrade/tasks/packages.yml
automation/roles/upgrade/tasks/pgbouncer_pause.yml
automation/roles/upgrade/tasks/pgbouncer_redirect.yml
automation/roles/upgrade/tasks/pgbouncer_restart.yml
automation/roles/upgrade/tasks/pgbouncer_restore.yml
automation/roles/upgrade/tasks/pgbouncer_resume.yml
automation/roles/upgrade/tasks/post_checks.yml
automation/roles/upgrade/tasks/post_upgrade.yml
automation/roles/upgrade/tasks/pre_checks.yml
automation/roles/upgrade/tasks/pre_checks_switchover.yml
automation/roles/upgrade/tasks/publication.yml
automation/roles/upgrade/tasks/read_only_mode_disable.yml
automation/roles/upgrade/tasks/read_only_mode_enable.yml
automation/roles/upgrade/tasks/recovery_target.yml
automation/roles/upgrade/tasks/replica_identity.yml
automation/roles/upgrade/tasks/replication_slot_advance.yml
automation/roles/upgrade/tasks/replication_slot_lag.yml
automation/roles/upgrade/tasks/rollback.yml
automation/roles/upgrade/tasks/schema_compatibility.yml
automation/roles/upgrade/tasks/sequences.yml
automation/roles/upgrade/tasks/source_databases.yml
automation/roles/upgrade/tasks/ssh-keys.yml
automation/roles/upgrade/tasks/start_services.yml
automation/roles/upgrade/tasks/statistics.yml
automation/roles/upgrade/tasks/stop_services.yml
automation/roles/upgrade/tasks/stop_target_primary.yml
automation/roles/upgrade/tasks/subscription.yml
automation/roles/upgrade/tasks/update_config.yml
automation/roles/upgrade/tasks/update_extensions.yml
automation/roles/upgrade/tasks/upgrade_check.yml
automation/roles/upgrade/tasks/upgrade_primary.yml
automation/roles/upgrade/tasks/upgrade_secondary.yml
automation/roles/upgrade/templates/haproxy-no-http-checks.cfg.j2
```

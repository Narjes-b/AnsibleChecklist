# Frozen source context: V007PILOT-STRUCTURE_REUSE-014

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `src/commcare_cloud/ansible/deploy_hq.yml` (reported anchor line 1)
- Object: `source_location` `2ab9d6547ed26b647fe067f42c56b2b7c8e45607aa4e2a139162b0f97f2d1520`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–137 of 137:

```text
    1 | # NOTE this playbook can be used to deploy a new version of commcare-hq. The
    2 | # similarly named deploy_commcarehq.yml playbook is used to configure machines
    3 | # to run commcare-hq, and is expected to be run less frequently than this one.
    4 | 
    5 | - name: Check hosts Ubuntu version
    6 |   hosts:
    7 |     - all
    8 |   tasks:
    9 |     - import_role: {name: upgrade_warning}
   10 |       tags: upgrade_warning
   11 | 
   12 | - name: Deploy CommCare HQ
   13 |   hosts:
   14 |     - webworkers
   15 |     - celery
   16 |     - pillowtop
   17 |     - proxy
   18 |     - django_manage
   19 |   any_errors_fatal: true
   20 |   tasks:
   21 |     - import_role: {name: deploy_hq}
   22 |       vars:
   23 |         if_not_done: setup_release_common
   24 |       tags: private_release
   25 | 
   26 |     - import_role: {name: deploy_hq}
   27 |       vars:
   28 |         if_not_done: setup_release
   29 | 
   30 | - name: Copy static JS
   31 |   hosts: proxy
   32 |   any_errors_fatal: true
   33 |   tasks:
   34 |     - include_role: {name: deploy_hq}
   35 |       vars:
   36 |         if_not_done: copy_release_files
   37 |         item: staticfiles/CACHE/js
   38 | 
   39 | - name: Install javascript dependencies
   40 |   hosts: [webworkers, celery, proxy]
   41 |   any_errors_fatal: true
   42 |   tasks:
   43 |     - import_role: {name: deploy_hq}
   44 |       vars:
   45 |         if_not_done: yarn_install
   46 | 
   47 | - name: Collect static files
   48 |   hosts: [webworkers, proxy]
   49 |   any_errors_fatal: true
   50 |   tasks:
   51 |     - import_role: {name: deploy_hq}
   52 |       vars:
   53 |         if_not_done: staticfiles_collect
   54 | 
   55 | - name: Compress static files
   56 |   hosts: proxy[0]
   57 |   any_errors_fatal: true
   58 |   tasks:
   59 |     - import_role: {name: deploy_hq}
   60 |       vars:
   61 |         if_not_done: staticfiles_compress
   62 | 
   63 | - name: Update translations
   64 |   hosts:
   65 |     - webworkers
   66 |     - celery
   67 |     - pillowtop
   68 |     - proxy
   69 |     - django_manage
   70 |   any_errors_fatal: true
   71 |   tasks:
   72 |     - import_role: {name: deploy_hq}
   73 |       vars:
   74 |         if_not_done: update_translations
   75 | 
   76 | - name: Run migrations
   77 |   hosts: webworkers[0]
   78 |   any_errors_fatal: true
   79 |   tasks:
   80 |     - import_role: {name: deploy_hq}
   81 |       vars:
   82 |         if_not_done: run_migrations
   83 | 
   84 | - name: Pull staticfiles manifest
   85 |   hosts: webworkers
   86 |   any_errors_fatal: true
   87 |   tasks:
   88 |     - import_role: {name: deploy_hq}
   89 |       vars:
   90 |         if_not_done: staticfiles_pull_manifest
   91 | 
   92 | - name: Pull staticfiles cache
   93 |   hosts: proxy[1:]
   94 |   any_errors_fatal: true
   95 |   tasks:
   96 |     - import_role: {name: deploy_hq}
   97 |       vars:
   98 |         if_not_done: staticfiles_pull_cache
   99 | 
  100 | - name: Pre-restart tasks
  101 |   hosts:
  102 |     - webworkers
  103 |     - celery
  104 |     - pillowtop
  105 |     - proxy
  106 |     - django_manage
  107 |   vars_files:
  108 |     - roles/deploy_hq/vars/main.yml
  109 |   become: true
  110 |   become_user: '{{ cchq_user }}'
  111 |   any_errors_fatal: true
  112 |   tasks:
  113 |     - import_role: {name: deploy_hq}
  114 |       vars:
  115 |         if_not_done: clean_releases
  116 | 
  117 |     - name: Check release
  118 |       command:
  119 |         cmd: ./manage.py check {{ item }}
  120 |         chdir: '{{ code_source }}'
  121 |       register: stop_loop_hack
  122 |       when: not stop_loop_hack.failed | default(False)
  123 |       run_once: true
  124 |       loop:
  125 |         - '--deploy'
  126 |         - '--deploy -t database'
  127 | 
  128 |     - name: Update current symlink
  129 |       become: true
  130 |       become_user: '{{ cchq_user }}'
  131 |       file:
  132 |         src: '{{ code_source }}'
  133 |         path: '{{ code_home }}'
  134 |         state: link
  135 |         force: true
  136 | 
  137 | - import_playbook: restart_commcare_services.yml
```

## Frozen tracked paths in the relevant role/scope

```text
.adr-dir
.ansible-lint
.ansible-lint-ignore
.flake8
.github/PULL_REQUEST_TEMPLATE.md
.github/workflows/ansible-lint.yml
.github/workflows/claude-dependabot.yml
.github/workflows/codeql.yml
.github/workflows/linter.yml
.github/workflows/tests.yml
.github/workflows/trivy.yml
.gitignore
.gitmodules
.isort.cfg
.python-version
.readthedocs.yml
.tests/environments/_authorized_keys/testuser.pub
.tests/environments/_users/testusers.yml
.tests/environments/testenv/app-processes.yml
.tests/environments/testenv/fab-settings.yml
.tests/environments/testenv/inventory.ini
.tests/environments/testenv/meta.yml
.tests/environments/testenv/postgresql.yml
.tests/environments/testenv/private.yml
.tests/environments/testenv/proxy.yml
.tests/environments/testenv/public.yml
.tests/secrets/.aws/config
.tests/secrets/.aws/credentials
.tests/secrets/.ssh/commcarehq_testing.pem
.tests/spec.yml
.tests/tests.sh
CONTRIBUTING.md
LICENSE
Makefile
README.md
Vagrantfile
changelog/0001-add-encrypted-tmp.yml
changelog/0002-supervisor-service-definitions.yml
changelog/0003-update-supervisor.yml
changelog/0004-add-analytics-queue.yml
changelog/0005-support-multiple-kafak-brokers.yml
changelog/0006-new-case-importer-celery-queue.yml
changelog/0007-reorganize-pillows.yml
changelog/0008-blob-metadata-part-1.yml
changelog/0009-blob-metadata-part-2.yml
changelog/0010-letsencrypt-restart-nginx.yml
changelog/0011-fix-encrypted-tmp-permissions.yml
changelog/0012-generalize-load-case-from-fixture.yml
changelog/0013-java-upgrade-for-formplayer.yml
changelog/0014-add-tag-to-datadog-http-checks.yml
changelog/0015-separate-celery-datadog-http-check.yml
changelog/0016-invoke-celery-directly.yml
changelog/0017-monitor-specific-rabbitmq-queues.yml
changelog/0018-split_pgbouncer_postgresql_vars.yml
changelog/0019-remove-celery-results-backend-from-localsettings.yml
changelog/0020-update-rabbitmq-logging.yml
changelog/0021-fix-letsencrypt-restart-nginx.yml
changelog/0022-install-pango.yml
changelog/0023-upgrade-to-python-3.yml
changelog/0024-define-management-commands.yml
changelog/0025-rename-management-commands.yml
changelog/0026-move-remaining-management-commands.yml
changelog/0027-fix-python3-virtualenv.yml
changelog/0028-remove-riak.yml
changelog/0029-add-deploy-command.yml
changelog/0030-upgrade-sentry.yml
changelog/0031-update-formplayer-config.yml
changelog/0032-upgrade-to-elasticsearch-2.4.6.yml
changelog/0033-update-deploy-args.yml
changelog/0034-update-git.yml
changelog/0035-new-js-package-manager.yml
changelog/0036-clean-2fa-sessions.yml
changelog/0037-update-supervisor-confs.yml
changelog/0038-update-postgresql-monit-conf.yml
changelog/0039-update-letsencrypt-to-alternate-chain.yml
changelog/0040-install-new-apt-requirements.yml
changelog/0041-python3-support.yml
changelog/0042-update_formplayer_request_mapping.yml
changelog/0043-optionally-configure-auditcare-db.yml
changelog/0044-migrate-forms-to-sql.yml
changelog/0045-upgrade-to-python-39.yml
changelog/0046-upgrade_node_14x_npm_7x.yml
changelog/0047-pgbouncer-multiprocess.yml
changelog/0048-update-supervisor-confs.yml
changelog/0049-upgrade-to-postgres-10.yml
changelog/0050-remove-report-indices.yml
changelog/0051-historical-auditcare-data-migration.yml
changelog/0052-upgrade-ansible.yml
changelog/0053-upgrade-redis.yml
changelog/0054-upgrade-zookeeper_3.7.1.yml
changelog/0055-bootstrap-userrole-auditing.yml
changelog/0056-upgrade-kafka_3.2.0.yml
changelog/0057-update-prometheus-variable.yml
changelog/0058-RabbitMQ_upgrade_to_3.10.7_version.yml
changelog/0059-postgres-v14-upgrade.yml
changelog/0060-upgrade-to-python-3-10.yml
changelog/0061-install-elasticsearch-phonetic-analysis-plugin.yml
changelog/0062-kafka-upgrade-to-3.2.3.yml
changelog/0063-backfill_sms_event_data_for_api_performance.yml
changelog/0064-new-script-for-venv-activation.yml
changelog/0065-Populate_repeater_names.yml
changelog/0066-remove-unused-elastic-settings.yml
changelog/0067-dropping-3.6-support.yml
changelog/0068-install-dart-sass.yml
changelog/0069-configure-java-17-for-formplayer.yml
changelog/0070-update-node-to-v16.yml
changelog/0071-upgrade_to_ubuntu_22.04.yml
changelog/0072-upgrade-redis-to-v7.yml
changelog/0073-prepare-for-cle-ga.yml
changelog/0074-update-to-python-3.9.18.yml
changelog/0075-reindex-all-indexes-for-es-upgrade.yml
changelog/0076-upgrade-to-es-5.yml
changelog/0077-sql-repeatrecord-pr1.yml
changelog/0078-upgrade-to-node-20.yml
changelog/0079-sql-repeatrecord-addendum.yml
changelog/0080-copy-invitation-supply-point-fields-to-location.yml
changelog/0081-delete-receiverwrapper-couch-db.yml
changelog/0082-unicel-sms-gateway-removal.yml
changelog/0083-database_backup_retention_change.yml
changelog/0084-add-geospatial-queue.yml
[listing truncated after 120 paths]
```

# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-024

- Repository: `Sunbird-Obsrv/sunbird-data-pipeline`
- Commit: `eb1e1a1c3533c549693dda32cd92c667754aaea9`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `ansible/redis-backup.yml` (reported anchor line 6)
- Flagged construct: variable `sunbird_management_storage_account_name`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–10 of 10:

```text
    1 | - hosts: redisall
    2 |   become: yes
    3 |   vars_files:
    4 |     - ['{{inventory_dir}}/secrets.yml']
    5 |   environment:
    6 |     AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
    7 |     AZURE_STORAGE_KEY: "{{sunbird_management_storage_account_key}}"
    8 |   roles:
    9 |    - redis-multiprocess-backup
   10 |   run_once: true
```

## Visible variable references

```text
Whole-word search for `sunbird_management_storage_account_name`: 16 matches in 14 files; 0 look like definitions (key assignment, register, set_fact) and are listed first.
No definition-like match (key assignment, register, set_fact) found.

Other references:
ansible/cassandra-backup.yml:6:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/cassandra-restore.yml:6:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/es_azure_plugin.yml:21:        - 'cloud.azure.storage.default.account: {{sunbird_management_storage_account_name}}'
ansible/influxdb_backup.yml:8:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/redis-backup.yml:6:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/roles/influxdb_restore/tasks/main.yml:10:  shell: "az storage blob download --container-name {{ influxdb_backup_azure_container_name }} --file {{ influxdb_restore_file_name }} --name {{ influxdb_restore_file_name }} --account-name {{sunbird_management_storage_account_name}} --account-key {{sunbird_management_storage_account_key}}"
ansible/roles/postgres-azure-managed-service/tasks/main.yml:36:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/roles/postgres-azure-managed-service/tasks/main.yml:42:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/roles/postgresql-backup/defaults/main.yml:4:postgresql_backup_azure_storage_account_name: {{sunbird_management_storage_account_name}}
ansible/roles/postgresql-backup/tasks/main.yml:20:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/roles/postgresql-backup/tasks/main.yml:26:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/roles/postgresql-restore/defaults/main.yml:7:postgresql_restore_azure_storage_account_name: {{sunbird_management_storage_account_name}}
ansible/roles/postgresql-restore/tasks/main.yml:10:    AZURE_STORAGE_ACCOUNT: "{{sunbird_management_storage_account_name}}"
ansible/roles/redis-multiprocess-restore/tasks/main.yml:12:  shell: "az storage blob download --container-name {{ redis_backup_azure_container_name }} --file {{ item }}/{{ redis_restore_file_name }} --name {{ item }}/{{ redis_restore_file_name }} --account-name {{sunbird_management_storage_account_name}} --account-key {{sunbird_management_storage_account_key}}"
ansible/roles/redis-restore/tasks/main.yml:4:  shell: "az storage blob download --container-name {{ redis_backup_azure_container_name }} --file {{ redis_restore_file_name }} --name {{ redis_restore_file_name }} --account-name {{sunbird_management_storage_account_name}} --account-key {{sunbird_management_storage_account_key}}"
ansible/samza_logs_upload.yml:6:   - command: "./upload_samza_logs.sh {{CONTAINER_NAME_SAMZA}} {{sunbird_management_storage_account_name}} {{sunbird_management_storage_account_key}}"
```

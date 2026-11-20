# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-040

- Repository: `os-migrate/os-migrate`
- Commit: `60e4123dd2391233d23149d7dfb6ebe4b0870590`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unnecessary-set-fact`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/import_workloads/tasks/main.yml` (reported anchor line 32)
- Object: `variable` `c5dea70ae37188f579b73607a29bf848588f193999696d97781c5747ef94cd94`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–44 of 44:

```text
    1 | - name: Read workloads resource file
    2 |   os_migrate.os_migrate.read_resources:
    3 |     path: "{{ os_migrate_data_dir }}/workloads.yml"
    4 |   register: read_workloads
    5 | 
    6 | - name: Include the conversion hosts inventory
    7 |   ansible.builtin.include_role:
    8 |     name: os_migrate.os_migrate.conversion_host
    9 |     tasks_from: conv_hosts_inventory.yml
   10 | 
   11 | - name: Filter workloads to import
   12 |   ansible.builtin.set_fact:
   13 |     filtered_workloads: "{{ (read_workloads.resources
   14 |       | from_yaml
   15 |       | os_migrate.os_migrate.stringfilter(os_migrate_workloads_filter,
   16 |        attribute='params.name')) }}"
   17 | 
   18 | - name: Create directory for workload migration logs
   19 |   ansible.builtin.file:
   20 |     path: "{{ os_migrate_data_dir }}/workload_logs"
   21 |     state: directory
   22 |     mode: '0750'
   23 | 
   24 | - name: Check if any workload requires data copy
   25 |   ansible.builtin.set_fact:
   26 |     os_migrate_requires_conversion_hosts: >-
   27 |       {{ filtered_workloads | selectattr('_migration_params.data_copy', 'defined') |
   28 |          selectattr('_migration_params.data_copy', 'equalto', true) | list | length > 0 }}
   29 | 
   30 | - name: Check if src conversion host is needed based on data copy and nbdkit direct usage
   31 |   ansible.builtin.set_fact:
   32 |     os_migrate_requires_src_conversion_host: >-
   33 |       {{ filtered_workloads | selectattr('_migration_params.use_nbdkit_direct', 'defined') |
   34 |          selectattr('_migration_params.use_nbdkit_direct', 'equalto', false) | list | length > 0 }}
   35 | 
   36 | - name: Check data copy state and run conversion host operations
   37 |   ansible.builtin.include_role:
   38 |     name: os_migrate.os_migrate.conversion_host
   39 |     tasks_from: conv_host_details.yml
   40 |   when: os_migrate_requires_conversion_hosts | bool
   41 | 
   42 | - name: Import workloads
   43 |   ansible.builtin.include_tasks: workload.yml
   44 |   loop: "{{ filtered_workloads }}"
```

## Visible variable references

```text
60e4123dd2391233d23149d7dfb6ebe4b0870590:roles/conversion_host/tasks/conv_host_details.yml:16:        - os_migrate_requires_src_conversion_host|default(true)
60e4123dd2391233d23149d7dfb6ebe4b0870590:roles/conversion_host/tasks/conv_host_details.yml:27:        - os_migrate_requires_src_conversion_host|default(true)
60e4123dd2391233d23149d7dfb6ebe4b0870590:roles/conversion_host/tasks/conv_host_details.yml:34:        - os_migrate_requires_src_conversion_host|default(true)
60e4123dd2391233d23149d7dfb6ebe4b0870590:roles/conversion_host/tasks/conv_host_details.yml:86:        - os_migrate_requires_src_conversion_host|default(true)
60e4123dd2391233d23149d7dfb6ebe4b0870590:roles/import_workloads/tasks/main.yml:32:    os_migrate_requires_src_conversion_host: >-
```

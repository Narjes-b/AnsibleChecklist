# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-023

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: maintainability_complexity
- Rule: `ansibleguard/undocumented-complex-task`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `automation/roles/pre_checks/tasks/extensions.yml` (reported anchor line 42)
- Flagged construct: not named by the finding; the anchor line 42 lies in the task at line 42, name `ParadeDB | Checking supported operating system and version`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–103 of 103:

```text
    1 | # yamllint disable rule:line-length
    2 | ---
    3 | # Extension Auto-Setup: pre-checks and shared_preload_libraries
    4 | 
    5 | # pre-checks
    6 | - name: TimescaleDB | Checking PostgreSQL version
    7 |   ansible.builtin.fail:
    8 |     msg:
    9 |       - "The current PostgreSQL version ({{ postgresql_version }}) is not supported by the TimescaleDB."
   10 |       - "PostgreSQL version must be {{ timescale_minimal_pg_version | default(12) }} or higher."
   11 |   when:
   12 |     - (enable_timescale | default(false) | bool) or (enable_timescaledb | default(false) | bool)
   13 |     - postgresql_version | string is version(timescale_minimal_pg_version | default(12) | string, '<')
   14 | 
   15 | - name: Timescale (pgvectorscale) | Checking PostgreSQL version
   16 |   ansible.builtin.fail:
   17 |     msg:
   18 |       - "The current PostgreSQL version ({{ postgresql_version }}) is not supported by the pgvectorscale."
   19 |       - "PostgreSQL version must be {{ pgvectorscale_minimal_pg_version | default(13) }} or higher."
   20 |   when:
   21 |     - enable_pgvectorscale | default(false) | bool
   22 |     - postgresql_version | string is version(pgvectorscale_minimal_pg_version | default(13) | string, '<')
   23 | 
   24 | - name: Timescale (pgvectorscale) | Checking supported operating system and version
   25 |   ansible.builtin.fail:
   26 |     msg:
   27 |       - "pgvectorscale is not supported on {{ ansible_distribution }} {{ ansible_distribution_release }}."
   28 |       - "Note: packages on the timescale/pgvectorscale github repository are available only for Debian-based distros."
   29 |   when:
   30 |     - enable_pgvectorscale | default(false) | bool
   31 |     - not ansible_os_family == "Debian"
   32 | 
   33 | - name: ParadeDB | Checking PostgreSQL version
   34 |   ansible.builtin.fail:
   35 |     msg:
   36 |       - "The current PostgreSQL version ({{ postgresql_version }}) is not supported by the ParadeDB (pg_search)."
   37 |       - "PostgreSQL version must be {{ paradedb_minimal_pg_version | default(14) }} or higher."
   38 |   when:
   39 |     - (enable_paradedb | default(false) | bool) or (enable_pg_search | default(false) | bool)
   40 |     - postgresql_version | string is version(paradedb_minimal_pg_version | default(14) | string, '<')
   41 | 
   42 | - name: ParadeDB | Checking supported operating system and version
   43 |   ansible.builtin.fail:
   44 |     msg:
   45 |       - "ParadeDB (pg_search) is not supported on {{ ansible_distribution }} {{ ansible_distribution_release }}."
   46 |       - "Note: packages on the paradedb github repository are available only for Debian 12/13, Ubuntu 22.04/24.04 or RedHat 8/9."
   47 |   when:
   48 |     - (enable_paradedb | default(false) | bool) or (enable_pg_search | default(false) | bool)
   49 |     - not (
   50 |       (ansible_os_family == "Debian" and ansible_distribution_release in ['bullseye', 'bookworm', 'jammy', 'noble']) or
   51 |       (ansible_os_family == "RedHat" and ansible_distribution_major_version in ['8', '9'])
   52 |       )
   53 | 
   54 | # shared_preload_libraries
   55 | - name: Create a list of extensions
   56 |   ansible.builtin.set_fact:
   57 |     extensions: >-
   58 |       {{
   59 |         (extensions | default([]))
   60 |         + (['timescaledb'] if ((enable_timescale | default(false) | bool) or (enable_timescaledb | default(false) | bool)) else [])
   61 |         + (['citus'] if (enable_citus | default(false) | bool and postgresql_version | int >= 11 and ansible_architecture in ["x86_64", "amd64"]) else [])
   62 |         + (['pg_cron'] if (enable_pg_cron | default(false) | bool) else [])
   63 |         + (['pgaudit'] if (enable_pgaudit | default(false) | bool) else [])
   64 |         + (['pg_stat_statements'] if (enable_pg_stat_kcache | default(false) | bool) else [])
   65 |         + (['pg_stat_kcache'] if (enable_pg_stat_kcache | default(false) | bool) else [])
   66 |         + (['pg_wait_sampling'] if (enable_pg_wait_sampling | default(false) | bool) else [])
   67 |         + (['pg_partman_bgw'] if (enable_pg_partman | default(false) | bool) else [])
   68 |         + (['pg_search'] if ((enable_paradedb | default(false) | bool) or (enable_pg_search | default(false) | bool)) else [])
   69 |         + (['pg_analytics'] if ((enable_paradedb | default(false) | bool) or (enable_pg_analytics | default(false) | bool)) else [])
   70 |       }}
   71 | 
   72 | - name: Add required extensions to 'shared_preload_libraries' (if missing)
   73 |   ansible.builtin.set_fact:
   74 |     # This complex line does several things:
   75 |     # 1. It takes the current list of PostgreSQL parameters,
   76 |     # 2. Removes any item where the option is 'shared_preload_libraries',
   77 |     # 3. Then appends a new 'shared_preload_libraries' item at the end.
   78 |     # The new value of this item is based on whether extension is already present in the old value.
   79 |     # If it is not present, it appends ',<extension_name>' to the old value. Otherwise, it leaves the value unchanged.
   80 |     postgresql_parameters: >-
   81 |       {{ postgresql_parameters | rejectattr('option', 'equalto', 'shared_preload_libraries') | list
   82 |       + [{'option': 'shared_preload_libraries', 'value': new_value}] }}
   83 |   vars:
   84 |     # Find the last item in postgresql_parameters where the option is 'shared_preload_libraries'
   85 |     shared_preload_libraries_item: >-
   86 |       {{
   87 |         postgresql_parameters
   88 |         | selectattr('option', 'equalto', 'shared_preload_libraries')
   89 |         | list | last | default({'value': ''})
   90 |       }}
   91 |     # Ensure that all required extensions are added to the 'shared_preload_libraries' parameter.
   92 |     # 1. If the 'citus' extension is not yet added to 'shared_preload_libraries', it's added to the beginning of the list.
   93 |     #    This is necessary as 'citus' needs to be first in the list as per Citus documentation.
   94 |     # 2. For all other extensions: if they are not yet added, they are appended to the end of the list.
   95 |     new_value: >-
   96 |       {{
   97 |         (item ~ ',' ~ shared_preload_libraries_item.value if item == 'citus' and item not in shared_preload_libraries_item.value.split(',') else
   98 |         (shared_preload_libraries_item.value ~ (',' if shared_preload_libraries_item.value else '')
   99 |         if item not in shared_preload_libraries_item.value.split(',') else shared_preload_libraries_item.value))
  100 |         ~ (item if item not in shared_preload_libraries_item.value.split(',') and item != 'citus' else '')
  101 |       }}
  102 |   loop: "{{ extensions | default([]) | unique }}"
  103 |   when: extensions | default([]) | length > 0
```

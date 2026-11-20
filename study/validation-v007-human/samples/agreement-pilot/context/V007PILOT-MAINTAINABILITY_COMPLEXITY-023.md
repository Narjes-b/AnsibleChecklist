# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-023

- Repository: `ansible/galaxy-operator`
- Commit: `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc`
- Family: Maintainability/complexity
- Rule: `ansibleguard/undocumented-complex-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/postgres/tasks/main.yml` (reported anchor line 111)
- Object: `source_location` `fdb2772544125b87ca208b65257b08574c05aac4678e5924ab8d72c5e80b09a7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–192 of 192:

```text
    1 | ---
    2 | 
    3 | - operator_sdk.util.k8s_status:
    4 |     api_version: "{{ api_version }}"
    5 |     kind: "{{ kind }}"
    6 |     name: "{{ ansible_operator_meta.name }}"
    7 |     namespace: "{{ ansible_operator_meta.namespace }}"
    8 |     conditions:
    9 |       - type: "{{ deployment_type | capitalize }}-Operator-Finished-Execution"
   10 |         message: "{{ deployment_type | capitalize }} operator tasks running"
   11 |         reason: OperatorRunning
   12 |         status: "False"
   13 |         lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
   14 | 
   15 | - name: Set node affinity
   16 |   set_fact:
   17 |     _node_affinity: "{{ raw_spec['affinity']['node_affinity'] | default({}) }}"
   18 |   when: affinity is defined and affinity.node_affinity is defined
   19 | 
   20 | - name: Obtain custom resource information
   21 |   set_fact:
   22 |     custom_resource: "{{ hostvars[inventory_hostname][custom_resource_key] }}"
   23 |     custom_resource_status: "{{ hostvars[inventory_hostname][custom_resource_key]['status'] | default({}) }}"
   24 | 
   25 | - name: Set postgres label if not defined by user
   26 |   set_fact:
   27 |     postgres_label_selector: "app.kubernetes.io/instance=postgres-{{ ansible_operator_meta.name }}"
   28 |   when: postgres_label_selector is not defined
   29 | 
   30 | # It is possible that N-2 postgres pods may still be present in the namespace from previous upgrades.
   31 | # So we have to take that into account and preferentially set the most recent one.
   32 | - name: Get the old postgres pod (N-1)
   33 |   kubernetes.core.k8s_info:
   34 |     kind: Pod
   35 |     api_version: v1
   36 |     namespace: "{{ ansible_operator_meta.namespace }}"
   37 |     label_selectors:
   38 |       - "{{ postgres_label_selector }}"
   39 |     field_selectors:
   40 |       - status.phase=Running
   41 |   register: _running_pods
   42 | 
   43 | - block:
   44 |     - name: Filter pods by name
   45 |       set_fact:
   46 |         filtered_old_postgres_pods: "{{ _running_pods.resources |
   47 |           selectattr('metadata.name', 'match', ansible_operator_meta.name + '-postgres.*-0') |
   48 |           rejectattr('metadata.name', 'search', '-' + supported_pg_version | string + '-0') |
   49 |           list }}"
   50 | 
   51 |     # Sort pods by name in reverse order (most recent PG version first) and set
   52 |     - name: Set info for previous postgres pod
   53 |       set_fact:
   54 |         sorted_old_postgres_pods: "{{ filtered_old_postgres_pods |
   55 |           sort(attribute='metadata.name') |
   56 |           reverse | list }}"
   57 |       when: filtered_old_postgres_pods | length
   58 | 
   59 |     - name: Set info for previous postgres pod
   60 |       set_fact:
   61 |         old_postgres_pod: "{{ sorted_old_postgres_pods | first }}"
   62 |       when: filtered_old_postgres_pods | length
   63 |   when: _running_pods.resources | length
   64 | 
   65 | # NetworkPolicy must be applied before the StatefulSet so deny is in place
   66 | # before any database pod starts.
   67 | - name: Apply PostgreSQL NetworkPolicy
   68 |   import_tasks: networkpolicy.yml
   69 |   when: managed_database
   70 | 
   71 | - block:
   72 |     - operator_sdk.util.k8s_status:
   73 |         api_version: "{{ api_version }}"
   74 |         kind: "{{ kind }}"
   75 |         name: "{{ ansible_operator_meta.name }}"
   76 |         namespace: "{{ ansible_operator_meta.namespace }}"
   77 |         conditions:
   78 |           - type: Database-Ready
   79 |             message: Creating database StatefulSet resource
   80 |             reason: CreatingStatefulSet
   81 |             status: "False"
   82 |             lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
   83 | 
   84 |     - name: Create postgresql.conf ConfigMap
   85 |       k8s:
   86 |         apply: true
   87 |         definition: "{{ lookup('template', 'postgres_extra_settings.configmap.yaml.j2') }}"
   88 |       when: postgres_extra_settings | length
   89 | 
   90 |     - name: Create Database if no database is specified
   91 |       k8s:
   92 |         apply: true
   93 |         definition: "{{ lookup('template', 'postgres.yaml.j2') }}"
   94 |   when: managed_database
   95 | 
   96 | - name: Look up details for this deployment
   97 |   kubernetes.core.k8s_info:
   98 |     api_version: "{{ api_version }}"
   99 |     kind: "{{ kind }}"
  100 |     name: "{{ ansible_operator_meta.name }}"
  101 |     namespace: "{{ ansible_operator_meta.namespace }}"
  102 |   register: this_galaxy
  103 | 
  104 | # If this deployment has been upgraded before or if upgrade has already been started, set this var
  105 | - name: Set previous PG version var
  106 |   set_fact:
  107 |     _previous_upgraded_pg_version: "{{ this_galaxy['resources'][0]['status']['upgradedPostgresVersion'] | default(false) }}"
  108 |   when:
  109 |     - "'upgradedPostgresVersion' in this_galaxy['resources'][0]['status']"
  110 | 
  111 | - name: Check if postgres pod is running and version 12
  112 |   block:
  113 |     - name: Set path to PG_VERSION file for given container image
  114 |       set_fact:
  115 |         path_to_pg_version: '{{ _postgres_data_path }}/PG_VERSION'
  116 |         path_to_pg_version_old: '/var/lib/postgresql/data/pgdata/PG_VERSION'
  117 | 
  118 |     - name: Get old PostgreSQL version (Checking old pg data path too)
  119 |       kubernetes.core.k8s_exec:
  120 |         namespace: "{{ ansible_operator_meta.namespace }}"
  121 |         pod: "{{ old_postgres_pod['metadata']['name'] }}"
  122 |         command: |
  123 |           bash -c '
  124 |           if [ -f {{ path_to_pg_version }} ]; then
  125 |             cat {{ path_to_pg_version }}
  126 |           elif [ -f {{ path_to_pg_version_old }} ]; then
  127 |             cat {{ path_to_pg_version_old }}
  128 |           else
  129 |             echo "Neither file exists"
  130 |           fi
  131 |           '
  132 |       register: _old_pg_version
  133 | 
  134 |     - debug:
  135 |         msg: "--- Upgrading from {{ old_postgres_pod['metadata']['name'] | default('NONE')}} Pod ---"
  136 | 
  137 |     - name: Migrate from md5 to scram-sha-256
  138 |       k8s_exec:
  139 |         namespace: "{{ ansible_operator_meta.namespace }}"
  140 |         pod: "{{ old_postgres_pod['metadata']['name'] }}"
  141 |         command: |
  142 |           bash -c "
  143 |           psql -U postgres -c \"ALTER SYSTEM SET password_encryption = [REDACTED_LITERAL]
  144 |           psql -U postgres -c \"SELECT pg_reload_conf();\" &&
  145 |           psql -U postgres -c \"ALTER USER \\\"{{ postgres_user }}\\\" WITH PASSWORD '{{ postgres_pass }}';\"
  146 |           "
  147 |       register: _migration_output
  148 |       no_log: "{{ no_log }}"
  149 |       when:
  150 |         - postgres_scram_migration_enabled
  151 |         - (_old_pg_version.stdout | default(0) | int ) == 13
  152 | 
  153 | 
  154 |     - name: Upgrade data dir from old Postgres to {{ supported_pg_version }} if applicable
  155 |       include_tasks: upgrade_postgres.yml
  156 |       when:
  157 |         - (_old_pg_version.stdout | default(0) | int ) < supported_pg_version
  158 |   when:
  159 |     - managed_database
  160 |     - (_previous_upgraded_pg_version | default(false)) | ternary(_previous_upgraded_pg_version | int < supported_pg_version, true)
  161 |     - old_postgres_pod | length  # If empty, then old pg pod has been removed and we can assume the upgrade is complete
  162 | 
  163 | - name: Migrate data from old Openshift instance
  164 |   import_tasks: migrate_data.yml
  165 |   when:
  166 |     - old_pg_config['resources'] is defined
  167 |     - old_pg_config['resources'] | length
  168 |     - not database_status_present
  169 | 
  170 | - name: Check PostgreSQL status
  171 |   kubernetes.core.k8s_info:
  172 |     api_version: apps/v1
  173 |     kind: StatefulSet
  174 |     namespace: "{{ ansible_operator_meta.namespace }}"
  175 |     name: "{{ ansible_operator_meta.name }}-postgres-{{ supported_pg_version }}"
  176 |   register: _pg_sts_status
  177 |   until: _pg_sts_status['resources'][0]['status']['availableReplicas'] == _pg_sts_status['resources'][0]['status']['replicas']
  178 |   retries: 20
  179 |   delay: 10
  180 |   when: managed_database | bool
  181 | 
  182 | - operator_sdk.util.k8s_status:
  183 |     api_version: "{{ api_version }}"
  184 |     kind: "{{ kind }}"
  185 |     name: "{{ ansible_operator_meta.name }}"
  186 |     namespace: "{{ ansible_operator_meta.namespace }}"
  187 |     conditions:
  188 |       - type: Database-Ready
  189 |         message: All Postgres tasks ran successfully
  190 |         reason: DatabaseTasksFinished
  191 |         status: "True"
  192 |         lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
```

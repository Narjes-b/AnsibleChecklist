# Frozen source context: V007PILOT2-STYLE_POLICY-005

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: style_policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `src/commcare_cloud/ansible/setup_pg_logical_replication.yml` (reported anchor line 151)
- Flagged construct: not named by the finding; the anchor line 151 lies in the task at line 151, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–225 of 225:

```text
    1 | ---
    2 | 
    3 | # Install pglogical extension
    4 | - hosts:
    5 |     - shard_dbs
    6 |   become: yes
    7 |   vars_files:
    8 |     - roles/postgresql_base/defaults/main.yml
    9 |   tasks:
   10 |     - name: Create pglogical extension (providers)
   11 |       become: yes
   12 |       become_user: postgres
   13 |       vars:
   14 |         ansible_ssh_pipelining: true
   15 |       postgresql_ext:
   16 |         name: pglogical
   17 |         db: "{{item.source_db_name}}"
   18 |         port: "{{ postgresql_port }}"
   19 |       with_items: "{{ replications }}"
   20 |       when: item.source_host == inventory_hostname
   21 | 
   22 |     - name: Create pglogical extension (subscribers)
   23 |       become: yes
   24 |       become_user: postgres
   25 |       vars:
   26 |         ansible_ssh_pipelining: true
   27 |       postgresql_ext:
   28 |         name: pglogical
   29 |         db: "{{item.target_db_name}}"
   30 |         port: "{{ replications }}"
   31 |       with_items: "{{ replications }}"
   32 |       when: item.target_host == inventory_hostname
   33 | 
   34 | # Set up provider nodes
   35 | - hosts:
   36 |     - shard_dbs
   37 |   become: yes
   38 |   become_user: postgres
   39 |   vars_files:
   40 |     - roles/postgresql_base/defaults/main.yml
   41 |   vars:
   42 |     - form_processor_replication_tables:
   43 |         - table_name: form_processor_xforminstancesql
   44 |           hash_fn: "hash_string(form_id, ''siphash24'')"
   45 |         - table_name: form_processor_xformoperationsql
   46 |           hash_fn: "hash_string(form_id, ''siphash24'')"
   47 |         - table_name: form_processor_xformattachmentsql
   48 |           hash_fn: "hash_string(form_id, ''siphash24'')"
   49 |         - table_name: form_processor_commcarecasesql
   50 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   51 |         - table_name: form_processor_commcarecaseindexsql
   52 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   53 |         - table_name: form_processor_caseattachmentsql
   54 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   55 |         - table_name: form_processor_casetransaction
   56 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   57 |         - table_name: form_processor_ledgervalue
   58 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   59 |         - table_name: form_processor_ledgertransaction
   60 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   61 |         - table_name: scheduling_casealertscheduleinstance
   62 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   63 |         - table_name: scheduling_casetimedscheduleinstance
   64 |           hash_fn: "hash_string(case_id, ''siphash24'')"
   65 |         - table_name: scheduling_alertscheduleinstance
   66 |           hash_fn: "hash_string(decode(replace(schedule_instance_id::text, ''-'', ''''), ''hex''), ''siphash24'')"
   67 |         - table_name: scheduling_timedscheduleinstance
   68 |           hash_fn: "hash_string(decode(replace(schedule_instance_id::text, ''-'', ''''), ''hex''), ''siphash24'')"
   69 |         - table_name: blobs_blobmeta
   70 |           hash_fn: "hash_string(parent_id, ''siphash24'')"
   71 |         - table_name: blobs_deletedblobmeta
   72 |           hash_fn: "hash_string(parent_id, ''siphash24'')"
   73 |   tasks:
   74 |     - name: Create node
   75 |       postgresql_query:
   76 |         db: '{{ item.source_db_name }}'
   77 |         query: "SELECT pglogical.create_node(node_name := '{{ item.source_db_name }}_provider', dsn := 'host={{ item.source_host }} port=5432 dbname={{ item.source_db_name }} user={{ postgres_users.replication.username}} password={{ postgres_users.replication.password }}')"
   78 |       with_items: "{{ replications }}"
   79 |       when: item.source_host == inventory_hostname
   80 |       register: result
   81 |       failed_when:
   82 |         - result.failed
   83 |         - '"node {{ item.source_db_name }}_provider already exists" not in result.msg'
   84 |         - '"current database is already configured as pglogical node" not in result.msg'
   85 | 
   86 |     - name: Create replication set
   87 |       postgresql_query:
   88 |         db: '{{ item.source_db_name }}'
   89 |         query: "SELECT pglogical.create_replication_set(set_name := '{{ item.source_db_name }}_{{ item.replication_set.0 }}_{{ item.replication_set.1 }}')"
   90 |       with_items: "{{ replications }}"
   91 |       when: item.source_host == inventory_hostname
   92 |       register: result
   93 |       failed_when:
   94 |         - result.failed
   95 |         - '"replication set {{ item.source_db_name }}_{{ item.replication_set.0 }}_{{ item.replication_set.1 }} already exists" not in result.msg'
   96 | 
   97 |     - name: Add tables to replication set
   98 |       postgresql_query:
   99 |         db: '{{ item.0.source_db_name }}'
  100 |         query: "SELECT pglogical.replication_set_add_table(set_name := '{{ item.0.source_db_name }}_{{ item.0.replication_set.0 }}_{{ item.0.replication_set.1 }}',relation := '{{ item.1.table_name }}',row_filter := '{{ item.1.hash_fn }} & 1023 BETWEEN {{ item.0.replication_set.0}} AND {{ item.0.replication_set.1}}')"
  101 |       loop: "{{ replications|product(form_processor_replication_tables)|list }}"
  102 |       when: item.0.source_host == inventory_hostname
  103 |       register: result
  104 |       failed_when:
  105 |         - result.failed
  106 |         - '"duplicate key value violates unique constraint" not in result.msg'
  107 | 
  108 |     - name: Add sequences to replication set
  109 |       postgresql_query:
  110 |         db: '{{ item.source_db_name }}'
  111 |         query: "SELECT pglogical.replication_set_add_all_sequences(set_name := '{{ item.source_db_name }}_{{ item.replication_set.0 }}_{{ item.replication_set.1 }}',schema_names := ARRAY['public'])"
  112 |       loop: "{{ replications }}"
  113 |       when: item.source_host == inventory_hostname
  114 | 
  115 | # Set up subscriber nodes
  116 | - hosts:
  117 |     - shard_dbs
  118 |   become: yes
  119 |   become_user: postgres
  120 |   vars_files:
  121 |     - roles/postgresql_base/defaults/main.yml
  122 |   tasks:
  123 |     - name: Create node
  124 |       postgresql_query:
  125 |         db: '{{ item.target_db_name }}'
  126 |         query: "SELECT pglogical.create_node(node_name := '{{ item.target_db_name }}_subscriber', dsn := 'host={{ item.target_host }} port=5432 dbname={{ item.target_db_name }} user={{ postgres_users.replication.username }} password={{ postgres_users.replication.password }}');"
  127 |       loop: "{{ replications }}"
  128 |       when: item.target_host == inventory_hostname
  129 |       register: result
  130 |       failed_when:
  131 |         - result.failed
  132 |         - '"node {{ item.name }}_subscriber already exists" not in result.msg'
  133 |         - '"current database is already configured as pglogical node" not in result.msg'
  134 | 
  135 |     - name: Subscribe to replication set and begin synchronization
  136 |       postgresql_query:
  137 |         db: '{{ item.target_db_name }}'
  138 |         query: "SELECT pglogical.create_subscription(subscription_name := '{{ item.source_db_name }}_{{ item.replication_set.0 }}_{{ item.replication_set.1 }}_sub',provider_dsn := 'host={{ item.source_host }} port=5432 dbname={{ item.source_db_name}} user={{ postgres_users.replication.username}} password={{ postgres_users.replication.password }}',replication_sets := '{ {{ item.source_db_name }}_{{ item.replication_set.0 }}_{{ item.replication_set.1 }} }', synchronize_structure := 'true',synchronize_data := 'true');"
  139 |       loop: "{{ replications }}"
  140 |       when: item.target_host == inventory_hostname
  141 |       register: result
  142 | 
  143 |     - name: Grant usage to hq user
  144 |       postgresql_query:
  145 |         db: '{{ item.target_db_name }}'
  146 |         query: "GRANT USAGE ON SCHEMA pglogical TO {{ postgres_users.commcare }};"
  147 |       loop: "{{ replications }}"
  148 |       when: item.target_host == inventory_hostname
  149 | 
  150 | # status
  151 | - hosts:
  152 |     - shard_dbs
  153 |   become: yes
  154 |   become_user: postgres
  155 |   vars_files:
  156 |     - roles/postgresql_base/defaults/main.yml
  157 |   tasks:
  158 |     - name: Query provider status
  159 |       postgresql_query:
  160 |         db: '{{ item.source_db_name }}'
  161 |         query: "select application_name, sent_location, replay_location from pg_stat_replication where application_name = '{{ item.source_db_name }}_{{ item.replication_set.0 }}_{{ item.replication_set.1 }}_sub'"
  162 |       loop: "{{ replications }}"
  163 |       when: item.source_host == inventory_hostname
  164 |       register: result
  165 |       tags: status
  166 |     - name: All provider status
  167 |       debug:
  168 |         msg: "{{ result.results | reject(\"skipped\") | map(attribute=\"query_result\") | list }}"
  169 |       when: result.results | reject("skipped") | map(attribute="query_result") | list
  170 |       tags: status
  171 |     - name: Query subscriber status
  172 |       postgresql_query:
  173 |         db: '{{ item.target_db_name }}'
  174 |         query: "select pglogical.show_subscription_status('{{ item.source_db_name }}_{{ item.replication_set.0 }}_{{ item.replication_set.1 }}_sub')"
  175 |       loop: "{{ replications }}"
  176 |       when: item.target_host == inventory_hostname
  177 |       register: result
  178 |       tags: status
  179 |     - name: All subscriber status
  180 |       debug:
  181 |         msg: "{{ result.results | reject(\"skipped\") | map(attribute=\"query_result\") | list }}"
  182 |       when: result.results | reject("skipped") | map(attribute="query_result") | list
  183 |       tags: status
  184 |     - name: Query row count (provider)
  185 |       postgresql_query:
  186 |         db: '{{ item.source_db_name }}'
  187 |         query: "select count(*) from form_processor_ledgervalue"
  188 |       loop: "{{ replications | unique(attribute=\"source_host\") }}"
  189 |       when: item.source_host == inventory_hostname
  190 |       register: result
  191 |       tags: status
  192 |     - name: All provider rows
  193 |       debug:
  194 |         msg: "{{ result.results | reject(\"skipped\") | map(attribute=\"query_result\")  | first | map(attribute=\"count\") | first }}"
  195 |       when: result.results | reject("skipped") | map(attribute="query_result") | list
  196 |       tags: status
  197 |     - name: Query row count (sub)
  198 |       postgresql_query:
  199 |         db: '{{ item.target_db_name }}'
  200 |         query: "select count(*) from form_processor_ledgervalue"
  201 |       loop: "{{ replications }}"
  202 |       when: item.target_host == inventory_hostname
  203 |       register: result
  204 |       tags: status
  205 |     - name: All subscriber status
  206 |       debug:
  207 |         msg: "{{ result.results | reject(\"skipped\") | map(attribute=\"query_result\")  | first | map(attribute=\"count\") | first }}"
  208 |       when: result.results | reject("skipped") | map(attribute="query_result") | list
  209 |       tags: status
  210 | 
  211 | # synchronize sequences
  212 | - hosts:
  213 |     - shard_dbs
  214 |   become: yes
  215 |   become_user: postgres
  216 |   vars_files:
  217 |     - roles/postgresql_base/defaults/main.yml
  218 |   tasks:
  219 |     - name: Query provider status
  220 |       postgresql_query:
  221 |         db: '{{ item.source_db_name }}'
  222 |         query: "SELECT pglogical.synchronize_sequence( seqoid ) FROM pglogical.sequence_state"
  223 |       loop: "{{ replications }}"
  224 |       when: item.source_host == inventory_hostname
  225 |       tags: synchronize_sequences
```

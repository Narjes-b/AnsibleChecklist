# Frozen source context: V007PILOT2-STYLE_POLICY-001

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: style_policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `ansible/roles/solr/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`ansible/roles/solr/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–184 of 184:

```text
    1 | ---
    2 | - include_tasks: ../../common/tasks/setfacts.yml
    3 |   tags:
    4 |     - solr
    5 |     - solr_create_cores
    6 |     - properties
    7 |     - solr_check_running
    8 | 
    9 | - name: Select JTS version
   10 |   set_fact:
   11 |     jts_version: >-
   12 |       {% if solr_version is version('7', '>=') and solr_version is version('8', '<') %}1.15.0
   13 |       {% elif solr_version is version('8', '>=') and solr_version is version('9', '<') %}1.19.0
   14 |       {% elif solr_version is version('9', '>=') %}1.19.0{% endif %}
   15 |     solr_in: >-
   16 |       {% if solr_version is version('7', '>=') and solr_version is version('8', '<') %}solr.in.sh.solr7
   17 |       {% elif solr_version is version('8', '>=') and solr_version is version('9', '<') %}solr.in.sh.solr8
   18 |       {% elif solr_version is version('9', '>=') %}solr.in.sh.solr8{% endif %}
   19 | 
   20 | - name: Download SOLR {{ solr_version }}
   21 |   get_url: url="https://archive.apache.org/dist/lucene/solr/{{ solr_version }}/solr-{{ solr_version }}.tgz" dest=/tmp/solr-{{ solr_version }}.tgz
   22 |   tags:
   23 |     - solr
   24 | 
   25 | - name: Extract the install script
   26 |   shell: "tar xzf /tmp/solr-{{ solr_version }}.tgz solr-{{ solr_version }}/bin/install_solr_service.sh --strip-components=2"
   27 |   tags:  
   28 |     - solr
   29 | 
   30 | - name: ensure target directories exist [data subdirectories etc.
   31 |   file: path={{item}} state=directory
   32 |   with_items:
   33 |     - "{{data_dir}}/solr/"
   34 |   tags:
   35 |     - solr
   36 |     - properties
   37 | 
   38 | - name: Run install script
   39 |   shell: "./install_solr_service.sh /tmp/solr-{{ solr_version }}.tgz -d /data/solr -f"
   40 |   become: yes
   41 |   tags:  
   42 |     - solr
   43 | 
   44 | - name: Download and install jts-core
   45 |   ansible.builtin.get_url:
   46 |     url: "https://repo1.maven.org/maven2/org/locationtech/jts/jts-core/{{ jts_version | trim }}/jts-core-{{ jts_version | trim }}.jar"
   47 |     dest: "/opt/solr/server/lib/ext/jts-core-{{ jts_version | trim }}.jar"
   48 |     mode: '0644'
   49 |     validate_certs: yes
   50 |     timeout: 30
   51 | 
   52 | - name: Download and install jst-io
   53 |   ansible.builtin.get_url:
   54 |     url: "https://repo1.maven.org/maven2/org/locationtech/jts/io/jts-io-common/{{ jts_version | trim }}/jts-io-common-{{ jts_version | trim }}.jar"
   55 |     dest: "/opt/solr/server/lib/ext/jts-io-common-{{ jts_version | trim }}.jar"
   56 |     mode: '0644'
   57 |     validate_certs: yes
   58 |     timeout: 30
   59 | 
   60 | - name: set SOLR directory ownership [all data is owned by solr]
   61 |   file: path=/opt/solr/ owner=solr  group=solr recurse=true
   62 |   tags:
   63 |     - solr
   64 | 
   65 | - name: Stop solr
   66 |   shell: "service solr stop"
   67 |   tags:
   68 |     - solr
   69 |     - solr_restart
   70 | 
   71 | - name: copy SOLR config
   72 |   template: src={{ solr_in | trim }} dest=/opt/solr/bin/solr.in.sh force=yes
   73 |   tags:
   74 |     - solr
   75 |     - properties
   76 | 
   77 | - name: copy SOLR config /etc/default
   78 |   template: src={{ solr_in | trim }} dest=/etc/default/solr.in.sh force=yes
   79 |   tags:
   80 |     - solr
   81 |     - properties
   82 | 
   83 | - name: ensure target directories exist [data subdirectories etc.
   84 |   file: path={{item}} state=directory owner=solr  group=solr
   85 |   with_items:
   86 |     - "{{data_dir}}/solr/data/biocache/conf"
   87 |     - "{{data_dir}}/solr/data/bie/conf"
   88 |     - "{{data_dir}}/solr/data/bie-offline/conf"
   89 |     - "{{data_dir}}/solr/data/biocache/data"
   90 |     - "{{data_dir}}/solr/data/bie/data"
   91 |     - "{{data_dir}}/solr/data/bie-offline/data"
   92 |   tags:
   93 |     - solr
   94 |     - properties
   95 | 
   96 | - name: copy SOLR config files for BIE and Biocache
   97 |   copy: src={{ role_path }}/../solrcloud_config/files/{{ item }}/conf dest={{ data_dir }}/solr/data/{{ item }}/ owner=solr  group=solr
   98 |   with_items:
   99 |     - "biocache"
  100 |     - "bie"
  101 |     - "bie-offline"
  102 |   tags:
  103 |     - solr
  104 |     - properties
  105 |     - solr_create_cores
  106 | 
  107 | - name: Set up SOLR Biocache schema (non doc values)
  108 |   template: src={{ role_path }}/../solrcloud_config/templates/biocache_schema.xml dest={{ data_dir }}/solr/data/biocache/conf/schema.xml owner=solr group=solr
  109 |   when: use_docvalues is not defined or use_docvalues|bool == false
  110 |   tags:
  111 |     - solr
  112 |     - properties
  113 |     - solr_create_cores
  114 | 
  115 | - name: Set up SOLR Biocache schema (with doc values)
  116 |   template: src={{ role_path }}/../solrcloud_config/templates/biocache_schema_docvalues.xml dest={{ data_dir }}/solr/data/biocache/conf/schema.xml owner=solr group=solr
  117 |   when: use_docvalues is defined and use_docvalues|bool == true
  118 |   tags:
  119 |     - solr
  120 |     - properties
  121 |     - solr_create_cores
  122 | 
  123 | - name: Set up SOLR Biocache schema
  124 |   template: src={{ role_path}}//../solrcloud_config/templates/biocache_schema.xml dest={{ data_dir }}/solr/data/biocache/conf/biocache_schema_docvalues.xml owner=solr group=solr
  125 |   tags:
  126 |     - solr
  127 |     - properties
  128 |     - solr_create_cores
  129 | 
  130 | - name: set data ownership [all data is owned by the unix user solr]
  131 |   file: path="{{ data_dir }}/solr/" owner=solr  group=solr recurse=true
  132 |   tags:
  133 |     - solr
  134 |     - properties
  135 | 
  136 | - name: Start solr
  137 |   service:
  138 |     name: solr
  139 |     state: restarted
  140 |     enabled: "yes"
  141 |   tags:
  142 |     - solr
  143 |     - solr_restart
  144 |     - solr_create_cores
  145 | 
  146 | - name: Ensure SOLR is running
  147 |   wait_for: host="{{ solr_host }}" port="{{ solr_port }}" delay=1 timeout=300
  148 |   tags:
  149 |     - solr
  150 |     - solr_check_running
  151 | 
  152 | - name: Get SOLR cores status
  153 |   uri:
  154 |     url: "{{ solr_base_url }}/solr/admin/cores?action=STATUS&wt=json"
  155 |     method: GET
  156 |     timeout: 30
  157 |     return_content: yes
  158 |   register: solr_status
  159 |   ignore_errors: yes
  160 |   tags:
  161 |     - solr
  162 |     - solr_create_cores
  163 | 
  164 | - name: Extract existing cores from SOLR status
  165 |   set_fact:
  166 |     existing_cores: "{{ (solr_status.json.status | default({}) | dict2items | map(attribute='key') | list) if solr_status.status == 200 else [] }}"
  167 |   tags:
  168 |     - solr
  169 |     - solr_create_cores
  170 | 
  171 | - name: Create missing SOLR cores
  172 |   get_url:
  173 |     url: "{{ solr_base_url }}/solr/admin/cores?action=CREATE&name={{ item }}&instanceDir={{ data_dir }}/solr/data/{{ item }}&config=solrconfig.xml&dataDir=data"
  174 |     force: yes
  175 |     timeout: 30
  176 |     dest: "/tmp/solr-output-{{ item }}"
  177 |   when: item not in existing_cores
  178 |   with_items:
  179 |     - "biocache"
  180 |     - "bie"
  181 |     - "bie-offline"
  182 |   tags:
  183 |     - solr
  184 |     - solr_create_cores
```

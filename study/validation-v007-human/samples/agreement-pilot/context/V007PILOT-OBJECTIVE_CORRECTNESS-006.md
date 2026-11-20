# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-006

- Repository: `IDR/deployment`
- Commit: `77f7a7e438a41ca775e85b629c0f84cc636ffad7`
- Family: Objective correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/management-fluentd.yml` (reported anchor line 58)
- Object: `task` `a5c5ae5ec1837fa5a6cee03b037e3815054e2bdf475167bece626fe9394065ab`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–198 of 198:

```text
    1 | # Fluentd log handling
    2 | # + Elasticsearch + Kibana in Docker
    3 | # https://www.fluentd.org/guides/recipes/elasticsearch-and-s3
    4 | 
    5 | # This assumes docker has already been installed
    6 | # (by management-prometheus.yml)
    7 | - hosts: "{{ idr_environment | default('idr') }}-management-hosts"
    8 | 
    9 |   tasks:
   10 | 
   11 |   - name: Create fluentd server configuration directory
   12 |     become: yes
   13 |     file:
   14 |       path: /etc/fluentd
   15 |       recurse: yes
   16 |       state: directory
   17 | 
   18 |   - name: Create data top level directory
   19 |     become: yes
   20 |     file:
   21 |       path: /data
   22 |       state: directory
   23 |       owner: root
   24 |       group: root
   25 | 
   26 |   - name: Create fluentd aggregated logs directory
   27 |     become: yes
   28 |     file:
   29 |       path: /data/fluentd
   30 |       state: directory
   31 |       owner: "{{ fluentd_uid }}"
   32 |       group: "{{ fluentd_uid }}"
   33 | 
   34 |   - name: Copy fluentd server configuration files
   35 |     become: yes
   36 |     template:
   37 |       src: files/fluentd-server/fluent.conf.j2
   38 |       dest: /etc/fluentd/fluent.conf
   39 |     register: fluent_conf_status
   40 | 
   41 |   - name: Create elasticsearch directory
   42 |     become: yes
   43 |     file:
   44 |       path: /data/elasticsearch
   45 |       state: directory
   46 |       # User id in elasticsearch Docker image
   47 |       owner: 1000
   48 |       group: 1000
   49 | 
   50 |   - name: Create docker network
   51 |     become: yes
   52 |     docker_network:
   53 |       name: fluent-es-kb
   54 |       state: present
   55 | 
   56 |   - name: Run docker elasticsearch
   57 |     become: yes
   58 |     docker_container:
   59 |       image: "{{ elasticsearch_docker_image }}"
   60 |       name: elasticsearch
   61 |       cleanup: True
   62 |       env:
   63 |         discovery.type: single-node
   64 |         ES_JAVA_OPTS: "-Xmx4096m"
   65 |       networks:
   66 |       - name: fluent-es-kb
   67 |       published_ports:
   68 |       - "9200:9200"
   69 |       #- "9300:9300"
   70 |       state: started
   71 |       restart_policy: always
   72 |       volumes:
   73 |       - /data/elasticsearch:/usr/share/elasticsearch/data
   74 | 
   75 |   - name: Run docker fluentd
   76 |     become: yes
   77 |     docker_container:
   78 |       image: "{{ fluentd_docker_image }}"
   79 |       name: fluentd
   80 |       cleanup: True
   81 |       env:
   82 |         FLUENT_UID: "{{ fluentd_uid }}"
   83 |       networks:
   84 |       - name: fluent-es-kb
   85 |       published_ports:
   86 |       - "24224:24224/udp"
   87 |       - "24224:24224"
   88 |       restart: "{{ fluent_conf_status is changed }}"
   89 |       state: started
   90 |       restart_policy: always
   91 |       volumes:
   92 |       - /etc/fluentd/fluent.conf:/fluentd/etc/fluent.conf:ro
   93 |       - /data/fluentd:/data/fluentd
   94 | 
   95 |   - name: Run docker kibana
   96 |     become: yes
   97 |     docker_container:
   98 |       image: "{{ kibana_docker_image }}"
   99 |       name: kibana
  100 |       cleanup: True
  101 |       networks:
  102 |       - name: fluent-es-kb
  103 |       published_ports:
  104 |       - "5601:5601"
  105 |       state: started
  106 |       restart_policy: always
  107 | 
  108 |   - name: Run elasticsearch curator
  109 |     become: yes
  110 |     docker_container:
  111 |       image: "{{ elasticsearch_curator_docker_image }}"
  112 |       name: elasticsearch-curator
  113 |       cleanup: True
  114 |       env:
  115 |         OLDER_THAN_IN_DAYS: "{{ elasticsearch_expire_logs_days }}"
  116 |         INTERVAL_IN_HOURS: "24"
  117 |       networks:
  118 |       - name: fluent-es-kb
  119 |       state: started
  120 |       restart_policy: always
  121 | 
  122 |   vars:
  123 |     fluentd_shared_key: "{{ idr_secret_fluentd_shared_key | default('fluentd') }}"
  124 |     fluentd_slack_token: "{{ idr_secret_management_slack_token | default(None) }}"
  125 |     fluentd_slack_channel: "{{ idr_logs_slack_channel | default('idr-logs') }}"
  126 |     fluentd_elasticsearch_host: elasticsearch
  127 |     fluentd_uid: "1010"
  128 |     elasticsearch_docker_image: "docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.1"
  129 |     elasticsearch_curator_docker_image: "openmicroscopy/elasticsearch-curator:5.4.1"
  130 |     elasticsearch_expire_logs_days: "14"
  131 |     fluentd_docker_image: "openmicroscopy/fluentd:0.1.0"
  132 |     kibana_docker_image: "docker.elastic.co/kibana/kibana-oss:6.1.1"
  133 | 
  134 | 
  135 | # Load hostvars for management server
  136 | - hosts: >-
  137 |     {{ idr_environment | default('idr') }}-management-hosts
  138 |     {{ idr_parent_environment | default('idr') }}-management-hosts
  139 | 
  140 | 
  141 | - hosts: >
  142 |     {{ idr_environment | default('idr') }}-proxy-hosts
  143 |     {{ idr_environment | default('idr') }}-omero-hosts
  144 | 
  145 |   # TODO: Ideally we'd use the `validate:` option to check these config
  146 |   # files, but it's not possible to validate only a fragment.
  147 |   # Instead we need to create these files before applying the role
  148 |   # However, we can only trigger the restart handler if the agent is
  149 |   # already installed.
  150 |   pre_tasks:
  151 | 
  152 |   - name: Check if td-agent already installed
  153 |     stat:
  154 |       path: /etc/init.d/td-agent
  155 |     register: _td_agent_st
  156 | 
  157 |   - name: Create fluentd conf.d
  158 |     become: yes
  159 |     file:
  160 |       path: /etc/td-agent/conf.d
  161 |       recurse: yes
  162 |       state: directory
  163 | 
  164 |   - name: Configure fluentd forwarding
  165 |     become: yes
  166 |     template:
  167 |       src: files/fluentd/forward-conf.j2
  168 |       dest: /etc/td-agent/conf.d/forward.conf
  169 |     notify:
  170 |     - restart fluentd if installed
  171 | 
  172 |   - name: Copy fluentd configuration
  173 |     become: yes
  174 |     copy:
  175 |       src: "{{ item }}"
  176 |       dest: "/etc/td-agent/conf.d/{{ item | basename }}"
  177 |     with_items:
  178 |     # These are specifc to each host-group
  179 |     - "{{ fluentd_source_configs }}"
  180 |     notify:
  181 |     - restart fluentd if installed
  182 | 
  183 |   handlers:
  184 |   - name: restart fluentd if installed
  185 |     become: yes
  186 |     systemd:
  187 |       daemon_reload: yes
  188 |       name: td-agent
  189 |       state: restarted
  190 |     when: _td_agent_st.stat.exists
  191 | 
  192 |   roles:
  193 |   - role: ome.fluentd
  194 | 
  195 |   vars:
  196 |     _monitoring_idr_environment: "{{ idr_parent_environment | default(idr_environment | default('idr')) + '-management-hosts' }}"
  197 |     fluentd_server_address: "{{ hostvars[groups[_monitoring_idr_environment][0]]['ansible_' + (idr_net_iface | default('eth0'))]['ipv4']['address'] }}"
  198 |     fluentd_shared_key: "{{ idr_secret_fluentd_shared_key | default('fluentd') }}"
```

# Frozen source context: V007PILOT-SECURITY-007

- Repository: `dryvist/ansible-proxmox-apps`
- Commit: `b179574eb875a6b7be09df83d001f623a68a2681`
- Family: Security
- Rule: `ansibleguard/unsafe-file-write`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/prometheus_stack/tasks/main.yml` (reported anchor line 30)
- Object: `source_location` `1a6701b499ba1eafcec36b9acba0eaef6c1f4bff574dbb93eed8fa50f3f7bbc9`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–163 of 163:

```text
    1 | ---
    2 | # prometheus_stack — Prometheus + blackbox_exporter as ONE Docker-in-LXC compose
    3 | # stack. One Docker bootstrap, one compose project, two services. Both run on host
    4 | # networking: blackbox needs it for ICMP source-routing + NET_RAW, Prometheus to
    5 | # reach exporters across VLANs and scrape blackbox on 127.0.0.1.
    6 | #
    7 | # daemon.json is intentionally NOT written here. The registry-mirror play in
    8 | # site.yml is the single owner of /etc/docker/daemon.json on docker LXCs (it sets
    9 | # storage-driver + registry mirror together). A per-role write would clobber the
   10 | # mirror — see the "single owner" note in site.yml.
   11 | 
   12 | # Docker itself (docker-ce + compose plugin, LXC-conditional fuse-overlayfs) is
   13 | # installed by the docker_engine meta dependency (meta/main.yml). No daemon.json
   14 | # (see above) and no venv: the stack deploys via docker_compose_v2, which uses the
   15 | # docker compose CLI (not the docker SDK), so compose runs under the system
   16 | # interpreter.
   17 | 
   18 | # =============================================================================
   19 | # Config + compose (single project, two services)
   20 | # =============================================================================
   21 | 
   22 | - name: Create prometheus stack data directory
   23 |   ansible.builtin.file:
   24 |     path: "{{ prometheus_stack_data_dir }}"
   25 |     state: directory
   26 |     owner: root
   27 |     group: root
   28 |     mode: "0755"
   29 | 
   30 | - name: Render prometheus.yml scrape configuration
   31 |   ansible.builtin.template:
   32 |     src: prometheus.yml.j2
   33 |     dest: "{{ prometheus_stack_data_dir }}/prometheus.yml"
   34 |     owner: root
   35 |     group: root
   36 |     mode: "0644"
   37 |     unsafe_writes: true
   38 |   notify: Reload prometheus config
   39 | 
   40 | - name: Render blackbox exporter configuration
   41 |   ansible.builtin.template:
   42 |     src: blackbox.yml.j2
   43 |     dest: "{{ prometheus_stack_data_dir }}/blackbox.yml"
   44 |     owner: root
   45 |     group: root
   46 |     mode: "0644"
   47 |   notify: Restart prometheus stack
   48 | 
   49 | - name: Deploy prometheus stack docker-compose template
   50 |   ansible.builtin.template:
   51 |     src: docker-compose.yml.j2
   52 |     dest: "{{ prometheus_stack_data_dir }}/docker-compose.yml"
   53 |     owner: root
   54 |     group: root
   55 |     mode: "0644"
   56 |   notify: Restart prometheus stack
   57 | 
   58 | - name: Deploy and verify the prometheus stack
   59 |   block:
   60 |     # One-time migration: the previous design ran blackbox-exporter as its own
   61 |     # compose project. Tear it down so its fixed container_name is free for the
   62 |     # merged project to recreate.
   63 |     - name: Check for the legacy standalone blackbox compose project
   64 |       ansible.builtin.stat:
   65 |         path: "{{ prometheus_stack_legacy_blackbox_dir }}/docker-compose.yml"
   66 |       register: prometheus_stack_legacy_blackbox
   67 | 
   68 |     - name: Tear down the legacy standalone blackbox compose project
   69 |       community.docker.docker_compose_v2:
   70 |         project_src: "{{ prometheus_stack_legacy_blackbox_dir }}"
   71 |         state: absent
   72 |       when: prometheus_stack_legacy_blackbox.stat.exists
   73 | 
   74 |     - name: Remove the legacy standalone blackbox project directory
   75 |       ansible.builtin.file:
   76 |         path: "{{ prometheus_stack_legacy_blackbox_dir }}"
   77 |         state: absent
   78 |       when: prometheus_stack_legacy_blackbox.stat.exists
   79 | 
   80 |     - name: Deploy the prometheus stack via docker compose
   81 |       community.docker.docker_compose_v2:
   82 |         project_src: "{{ prometheus_stack_data_dir }}"
   83 |         state: present
   84 | 
   85 |     # =========================================================================
   86 |     # Health checks — prove BOTH containers run, both serve, the exporter
   87 |     # actually completes a probe, AND Prometheus has scraped probe_success into
   88 |     # the TSDB (the full pipeline, not just "containers up").
   89 |     # =========================================================================
   90 |     - name: Verify both stack containers are running
   91 |       ansible.builtin.command: >-
   92 |         docker ps -q --filter name={{ item }} --filter status=running
   93 |       register: prometheus_stack_running
   94 |       changed_when: false
   95 |       retries: 6
   96 |       delay: 5
   97 |       until: prometheus_stack_running.stdout != ''
   98 |       loop:
   99 |         - "{{ prometheus_stack_container_name }}"
  100 |         - "{{ prometheus_stack_blackbox_container_name }}"
  101 | 
  102 |     - name: Verify prometheus is healthy and ready
  103 |       ansible.builtin.uri:
  104 |         url: "http://127.0.0.1:{{ prometheus_stack_port }}/-/ready"
  105 |         status_code: 200
  106 |       register: prometheus_stack_ready
  107 |       retries: 12
  108 |       delay: 5
  109 |       until: prometheus_stack_ready.status | default(0) == 200
  110 |       changed_when: false
  111 | 
  112 |     - name: Verify the blackbox exporter answers /-/healthy
  113 |       ansible.builtin.uri:
  114 |         url: "http://127.0.0.1:{{ prometheus_stack_blackbox_port }}/-/healthy"
  115 |         status_code: 200
  116 |       register: prometheus_stack_bb_healthy
  117 |       retries: 6
  118 |       delay: 5
  119 |       until: prometheus_stack_bb_healthy.status | default(0) == 200
  120 |       changed_when: false
  121 | 
  122 |     # Real probe: the exporter must run a module and emit metrics, not just answer
  123 |     # its own health endpoint. A broken module config or missing NET_RAW fails here.
  124 |     - name: Verify the blackbox exporter completes an ICMP probe
  125 |       ansible.builtin.uri:
  126 |         url: >-
  127 |           http://{{ prometheus_stack_blackbox_address }}/probe?target={{ prometheus_stack_smoke_target }}&module=icmp
  128 |         return_content: true
  129 |         status_code: 200
  130 |       register: prometheus_stack_probe
  131 |       retries: 6
  132 |       delay: 5
  133 |       until: "'probe_success' in (prometheus_stack_probe.content | default(''))"
  134 |       changed_when: false
  135 | 
  136 |     # End-to-end: Prometheus must have scraped the exporter and stored
  137 |     # probe_success. Exercises scrape + relabel + TSDB, not just service liveness.
  138 |     - name: Verify Prometheus has scraped probe_success into the TSDB
  139 |       ansible.builtin.uri:
  140 |         url: "http://127.0.0.1:{{ prometheus_stack_port }}/api/v1/query?query=probe_success"
  141 |         status_code: 200
  142 |       register: prometheus_stack_query
  143 |       retries: 12
  144 |       delay: 5
  145 |       until: (prometheus_stack_query.json.data.result | default([]) | length) > 0
  146 |       changed_when: false
  147 | 
  148 |   rescue:
  149 |     - name: Capture stack diagnostics on failure
  150 |       ansible.builtin.command: "{{ item }}"
  151 |       loop:
  152 |         - "docker ps -a"
  153 |         - "docker logs --tail 50 {{ prometheus_stack_container_name }}"
  154 |         - "docker logs --tail 50 {{ prometheus_stack_blackbox_container_name }}"
  155 |       register: prometheus_stack_diag
  156 |       changed_when: false
  157 |       failed_when: false
  158 | 
  159 |     - name: Fail with stack diagnostics
  160 |       ansible.builtin.fail:
  161 |         msg: |-
  162 |           prometheus stack failed to deploy/verify on {{ inventory_hostname }}.
  163 |           {{ prometheus_stack_diag.results | default([]) | map(attribute='stdout') | join('\n--- next ---\n') }}
```

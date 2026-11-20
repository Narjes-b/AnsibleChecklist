# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-023

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: objective_correctness
- Rule: `ansibleguard/invalid-numeric-value`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/custom/matrix-synapse/tasks/synapse/workers/init.yml` (reported anchor line 162)
- Flagged construct: attribute `port`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–218 of 218:

```text
    1 | # SPDX-FileCopyrightText: 2021 - 2023 Slavi Pantaleev
    2 | # SPDX-FileCopyrightText: 2022 Marko Weltzer
    3 | # SPDX-FileCopyrightText: 2022 Michael Hollister
    4 | # SPDX-FileCopyrightText: 2024 Charles Wright
    5 | #
    6 | # SPDX-License-Identifier: AGPL-3.0-or-later
    7 | 
    8 | ---
    9 | # Below is a huge hack for dynamically building a list of workers and finally assigning it to `matrix_synapse_workers_enabled_list`.
   10 | #
   11 | # set_fact within a loop does not work reliably in Ansible (it only executes on the first iteration for some reason),
   12 | # so we're forced to do something much uglier.
   13 | 
   14 | - name: Build room workers
   15 |   ansible.builtin.set_fact:
   16 |     worker:
   17 |       id: "room-worker-{{ item }}"
   18 |       name: "matrix-synapse-worker-room-{{ item }}"
   19 |       type: 'room_worker'
   20 |       app: 'generic_worker'
   21 |       webserving: true
   22 |       port: "{{ matrix_synapse_workers_room_workers_port_range_start + item }}"
   23 |       metrics_port: "{{ matrix_synapse_workers_room_workers_metrics_range_start + item }}"
   24 |   register: "matrix_synapse_workers_list_results_room_workers"
   25 |   loop: "{{ range(0, matrix_synapse_workers_room_workers_count | int) | list }}"
   26 | 
   27 | - name: Build client sync workers
   28 |   ansible.builtin.set_fact:
   29 |     worker:
   30 |       id: "sync-worker-{{ item }}"
   31 |       name: "matrix-synapse-worker-sync-{{ item }}"
   32 |       type: 'sync_worker'
   33 |       app: 'generic_worker'
   34 |       webserving: true
   35 |       port: "{{ matrix_synapse_workers_sync_workers_port_range_start + item }}"
   36 |       metrics_port: "{{ matrix_synapse_workers_sync_workers_metrics_range_start + item }}"
   37 |   register: "matrix_synapse_workers_list_results_sync_workers"
   38 |   loop: "{{ range(0, matrix_synapse_workers_sync_workers_count | int) | list }}"
   39 | 
   40 | - name: Build client reader workers
   41 |   ansible.builtin.set_fact:
   42 |     worker:
   43 |       id: "client-reader-{{ item }}"
   44 |       name: "matrix-synapse-worker-client-reader-{{ item }}"
   45 |       type: 'client_reader'
   46 |       app: 'generic_worker'
   47 |       webserving: true
   48 |       port: "{{ matrix_synapse_workers_client_reader_workers_port_range_start + item }}"
   49 |       metrics_port: "{{ matrix_synapse_workers_client_reader_workers_metrics_range_start + item }}"
   50 |   register: "matrix_synapse_workers_list_results_client_reader_workers"
   51 |   loop: "{{ range(0, matrix_synapse_workers_client_reader_workers_count | int) | list }}"
   52 | 
   53 | - name: Build federation reader workers
   54 |   ansible.builtin.set_fact:
   55 |     worker:
   56 |       id: "federation-reader-{{ item }}"
   57 |       name: "matrix-synapse-worker-federation-reader-{{ item }}"
   58 |       type: 'federation_reader'
   59 |       app: 'generic_worker'
   60 |       webserving: true
   61 |       port: "{{ matrix_synapse_workers_federation_reader_workers_port_range_start + item }}"
   62 |       metrics_port: "{{ matrix_synapse_workers_federation_reader_workers_metrics_range_start + item }}"
   63 |   register: "matrix_synapse_workers_list_results_federation_reader_workers"
   64 |   loop: "{{ range(0, matrix_synapse_workers_federation_reader_workers_count | int) | list }}"
   65 | 
   66 | - name: Build generic workers
   67 |   ansible.builtin.set_fact:
   68 |     worker:
   69 |       id: "generic-worker-{{ item }}"
   70 |       name: "matrix-synapse-worker-generic-{{ item }}"
   71 |       type: 'generic_worker'
   72 |       app: 'generic_worker'
   73 |       webserving: true
   74 |       port: "{{ matrix_synapse_workers_generic_workers_port_range_start + item }}"
   75 |       metrics_port: "{{ matrix_synapse_workers_generic_workers_metrics_range_start + item }}"
   76 |   register: "matrix_synapse_workers_list_results_generic_workers"
   77 |   loop: "{{ range(0, matrix_synapse_workers_generic_workers_count | int) | list }}"
   78 | 
   79 | - name: Build stream writer workers
   80 |   ansible.builtin.set_fact:
   81 |     worker:
   82 |       id: "stream-writer-{{ idx }}-{{ item.stream }}"
   83 |       # Names must not include underscores. Certain stream writer streams (to_device, account_data, ..) do, so we fix them up.
   84 |       name: "matrix-synapse-worker-stream-writer-{{ idx }}-{{ item.stream | replace('_', '-') }}"
   85 |       type: 'stream_writer'
   86 |       app: "generic_worker"
   87 |       webserving: "{{ item.stream in matrix_synapse_workers_webserving_stream_writer_types }}"
   88 |       stream_writer_stream: "{{ item.stream }}"
   89 |       port: "{{ matrix_synapse_workers_stream_writer_workers_http_port_range_start + idx }}"
   90 |       replication_port: "{{ matrix_synapse_workers_stream_writer_workers_replication_port_range_start + idx }}"
   91 |       metrics_port: "{{ matrix_synapse_workers_stream_writer_workers_metrics_range_start + idx }}"
   92 |   register: "matrix_synapse_workers_list_results_stream_writer_workers"
   93 |   loop: "{{ matrix_synapse_workers_stream_writers }}"
   94 |   loop_control:
   95 |     index_var: idx
   96 | 
   97 | - name: Populate matrix_synapse_stream_writers from enabled stream writer workers list
   98 |   ansible.builtin.set_fact:
   99 |     matrix_synapse_stream_writers: "{{ matrix_synapse_stream_writers | combine({item.ansible_facts.worker.stream_writer_stream: [item.ansible_facts.worker.name]}, list_merge='append') }}"
  100 |   with_items: "{{ matrix_synapse_workers_list_results_stream_writer_workers.results }}"
  101 | 
  102 | - name: Build federation sender workers
  103 |   ansible.builtin.set_fact:
  104 |     worker:
  105 |       id: "federation-sender-{{ item }}"
  106 |       name: "matrix-synapse-worker-federation-sender-{{ item }}"
  107 |       type: 'federation_sender'
  108 |       app: 'generic_worker'
  109 |       webserving: false
  110 |       port: 0
  111 |       metrics_port: "{{ matrix_synapse_workers_federation_sender_workers_metrics_range_start + item }}"
  112 |   register: "matrix_synapse_workers_list_results_federation_sender_workers"
  113 |   loop: "{{ range(0, matrix_synapse_workers_federation_sender_workers_count | int) | list }}"
  114 | 
  115 | - name: Populate matrix_synapse_federation_sender_instances from enabled federation sender workers list
  116 |   ansible.builtin.set_fact:
  117 |     matrix_synapse_federation_sender_instances: "{{ matrix_synapse_federation_sender_instances + [item.ansible_facts.worker.name] }}"
  118 |   with_items: "{{ matrix_synapse_workers_list_results_federation_sender_workers.results }}"
  119 | 
  120 | - name: Build pusher workers
  121 |   ansible.builtin.set_fact:
  122 |     worker:
  123 |       id: "pusher-{{ item }}"
  124 |       name: "matrix-synapse-worker-pusher-{{ item }}"
  125 |       type: 'pusher'
  126 |       app: 'generic_worker'
  127 |       webserving: false
  128 |       port: 0
  129 |       metrics_port: "{{ matrix_synapse_workers_pusher_workers_metrics_range_start + item }}"
  130 |   register: "matrix_synapse_workers_list_results_pusher_workers"
  131 |   loop: "{{ range(0, matrix_synapse_workers_pusher_workers_count | int) | list }}"
  132 | 
  133 | # This type of worker can only have a count of 1, at most
  134 | - name: Build appservice workers
  135 |   ansible.builtin.set_fact:
  136 |     worker:
  137 |       id: "appservice-{{ item }}"
  138 |       name: "matrix-synapse-worker-appservice-{{ item }}"
  139 |       type: 'appservice'
  140 |       app: 'generic_worker'
  141 |       webserving: false
  142 |       port: 0
  143 |       metrics_port: "{{ matrix_synapse_workers_appservice_workers_metrics_range_start + item }}"
  144 |   register: "matrix_synapse_workers_list_results_appservice_workers"
  145 |   loop: "{{ range(0, matrix_synapse_workers_appservice_workers_count | int) | list }}"
  146 | 
  147 | # This type of worker can only have a count of 1, at most
  148 | - name: Build user_dir workers
  149 |   ansible.builtin.set_fact:
  150 |     worker:
  151 |       id: "user-dir-{{ item }}"
  152 |       name: "matrix-synapse-worker-user-dir-{{ item }}"
  153 |       type: 'user_dir'
  154 |       app: 'generic_worker'
  155 |       webserving: true
  156 |       port: "{{ matrix_synapse_workers_user_dir_workers_port_range_start + item }}"
  157 |       metrics_port: "{{ matrix_synapse_workers_user_dir_workers_metrics_range_start + item }}"
  158 |   register: "matrix_synapse_workers_list_results_user_dir_workers"
  159 |   loop: "{{ range(0, matrix_synapse_workers_user_dir_workers_count | int) | list }}"
  160 | 
  161 | # This type of worker can only have a count of 1, at most
  162 | - name: Build background workers
  163 |   ansible.builtin.set_fact:
  164 |     worker:
  165 |       id: "background-{{ item }}"
  166 |       name: "matrix-synapse-worker-background-{{ item }}"
  167 |       type: 'background'
  168 |       app: 'generic_worker'
  169 |       webserving: false
  170 |       port: 0
  171 |       metrics_port: "{{ matrix_synapse_workers_background_workers_metrics_range_start + item }}"
  172 |   register: "matrix_synapse_workers_list_results_background_workers"
  173 |   loop: "{{ range(0, matrix_synapse_workers_background_workers_count | int) | list }}"
  174 | 
  175 | - name: Build media_repository workers
  176 |   ansible.builtin.set_fact:
  177 |     worker:
  178 |       id: "media-repository-{{ item }}"
  179 |       name: "matrix-synapse-worker-media-repository-{{ item }}"
  180 |       type: 'media_repository'
  181 |       app: 'media_repository'
  182 |       webserving: true
  183 |       port: "{{ matrix_synapse_workers_media_repository_workers_port_range_start + item }}"
  184 |       metrics_port: "{{ matrix_synapse_workers_media_repository_workers_metrics_range_start + item }}"
  185 |   register: "matrix_synapse_workers_list_results_media_repository_workers"
  186 |   loop: "{{ range(0, matrix_synapse_workers_media_repository_workers_count | int) | list }}"
  187 | 
  188 | - ansible.builtin.set_fact:
  189 |     matrix_synapse_dynamic_workers_list: "{{ matrix_synapse_dynamic_workers_list | default([]) + [item.ansible_facts.worker] }}"
  190 |   with_items: |
  191 |     {{
  192 |       matrix_synapse_workers_list_results_room_workers.results
  193 |       +
  194 |       matrix_synapse_workers_list_results_sync_workers.results
  195 |       +
  196 |       matrix_synapse_workers_list_results_client_reader_workers.results
  197 |       +
  198 |       matrix_synapse_workers_list_results_federation_reader_workers.results
  199 |       +
  200 |       matrix_synapse_workers_list_results_generic_workers.results
  201 |       +
  202 |       matrix_synapse_workers_list_results_stream_writer_workers.results
  203 |       +
  204 |       matrix_synapse_workers_list_results_federation_sender_workers.results
  205 |       +
  206 |       matrix_synapse_workers_list_results_pusher_workers.results
  207 |       +
  208 |       matrix_synapse_workers_list_results_appservice_workers.results
  209 |       +
  210 |       matrix_synapse_workers_list_results_user_dir_workers.results
  211 |       +
  212 |       matrix_synapse_workers_list_results_media_repository_workers.results
  213 |       +
  214 |       matrix_synapse_workers_list_results_background_workers.results
  215 |     }}
  216 | 
  217 | - ansible.builtin.set_fact:
  218 |     matrix_synapse_workers_enabled_list: "{{ matrix_synapse_dynamic_workers_list }}"
```

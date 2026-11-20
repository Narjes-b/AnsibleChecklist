# Frozen source context: V007PILOT-SECURITY-009

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/custom/matrix-synapse/tasks/rust-synapse-compress-state/compress_room.yml` (reported anchor line 12)
- Object: `task` `7e74d09c20a86e8f436cab8f550390a754d06eeea4a0ca56b46ccb8d7177ceeb`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–61 of 61:

```text
    1 | # SPDX-FileCopyrightText: 2020 - 2024 Slavi Pantaleev
    2 | # SPDX-FileCopyrightText: 2021 Béla Becker
    3 | # SPDX-FileCopyrightText: 2022 Marko Weltzer
    4 | #
    5 | # SPDX-License-Identifier: AGPL-3.0-or-later
    6 | 
    7 | ---
    8 | 
    9 | - ansible.builtin.debug:
   10 |     msg: "Compressing room `{{ room_details.room_id }}` having {{ room_details.count }} state group rows"
   11 | 
   12 | - name: Generate rust-synapse-compress-state room compression command
   13 |   ansible.builtin.set_fact:
   14 |     matrix_synapse_rust_synapse_compress_state_compress_room_command: >-
   15 |       {{ devture_systemd_docker_base_host_command_docker }} run --rm --name matrix-rust-synapse-compress-state-compress-room
   16 |       --user={{ matrix_synapse_uid }}:{{ matrix_synapse_gid }}
   17 |       --cap-drop=ALL
   18 |       --network={{ postgres_container_network }}
   19 |       --mount type=bind,src={{ matrix_synapse_rust_synapse_compress_state_base_path }},dst=/work
   20 |       {{ matrix_synapse_rust_synapse_compress_state_container_image }}
   21 |       {{ matrix_synapse_rust_synapse_compress_state_synapse_compress_state_in_container_path }} -t -o /work/state-compressor.sql
   22 |       -p "host={{ matrix_synapse_database_host }} user={{ matrix_synapse_database_user }} password={{ matrix_synapse_database_password }} dbname={{ matrix_synapse_database_database }}"
   23 |       -r '{{ room_details.room_id }}'
   24 | 
   25 | - name: Run rust-synapse-compress-state room compression command (SQL generation)
   26 |   ansible.builtin.command: "{{ matrix_synapse_rust_synapse_compress_state_compress_room_command }}"
   27 |   async: "{{ matrix_synapse_rust_synapse_compress_state_compress_room_time }}"
   28 |   poll: 10
   29 |   register: matrix_synapse_rust_synapse_compress_state_compress_room_command_result
   30 |   failed_when: not matrix_synapse_rust_synapse_compress_state_compress_room_command_result.finished or matrix_synapse_rust_synapse_compress_state_compress_room_command_result.rc != 0
   31 |   changed_when: matrix_synapse_rust_synapse_compress_state_compress_room_command_result.finished and matrix_synapse_rust_synapse_compress_state_compress_room_command_result.rc == 0
   32 | 
   33 | - ansible.builtin.debug:
   34 |     var: "matrix_synapse_rust_synapse_compress_state_compress_room_command_result"
   35 | 
   36 | - name: Generate Postgres compression SQL import command
   37 |   ansible.builtin.set_fact:
   38 |     matrix_synapse_rust_synapse_compress_state_psql_import_command: >-
   39 |       {{ devture_systemd_docker_base_host_command_docker }} run --rm --name matrix-rust-synapse-compress-state-psql-import
   40 |       --user={{ postgres_uid }}:{{ postgres_gid }}
   41 |       --cap-drop=ALL
   42 |       --network={{ postgres_container_network }}
   43 |       --env-file={{ postgres_base_path }}/env-postgres-psql
   44 |       --mount type=bind,src={{ matrix_synapse_rust_synapse_compress_state_base_path }},dst=/work,ro
   45 |       --entrypoint=/bin/sh
   46 |       {{ postgres_container_image_latest }}
   47 |       -c "cat /work/state-compressor.sql |
   48 |       psql -v ON_ERROR_STOP=1 -h {{ postgres_connection_hostname }} -d {{ matrix_synapse_database_database }}"
   49 | 
   50 | - name: Import compression SQL into Postgres
   51 |   ansible.builtin.command: "{{ matrix_synapse_rust_synapse_compress_state_psql_import_command }}"
   52 |   async: "{{ matrix_synapse_rust_synapse_compress_state_psql_import_time }}"
   53 |   poll: 10
   54 |   register: matrix_synapse_rust_synapse_compress_state_psql_import_command_result
   55 |   failed_when: not matrix_synapse_rust_synapse_compress_state_psql_import_command_result.finished
   56 |   changed_when: matrix_synapse_rust_synapse_compress_state_psql_import_command_result.finished and matrix_synapse_rust_synapse_compress_state_psql_import_command_result.rc == 0
   57 | 
   58 | - name: Clean up
   59 |   ansible.builtin.file:
   60 |     path: "{{ matrix_synapse_rust_synapse_compress_state_base_path }}/state-compressor.sql"
   61 |     state: absent
```

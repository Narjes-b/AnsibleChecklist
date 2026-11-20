# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-037

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/custom/matrix-bridge-mautrix-gvoice/tasks/setup_install.yml` (reported anchor line 149)
- Object: `source_location` `81694a606fc5939607e5933f072e3f63f7128176f9d24c9c74f2e2af87686635`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–186 of 186:

```text
    1 | # SPDX-FileCopyrightText: 2026 MDAD project contributors
    2 | # SPDX-FileCopyrightText: 2026 Nikita Chernyi
    3 | #
    4 | # SPDX-License-Identifier: AGPL-3.0-or-later
    5 | 
    6 | ---
    7 | 
    8 | - ansible.builtin.set_fact:
    9 |     matrix_bridge_mautrix_gvoice_migration_requires_restart: false
   10 | 
   11 | - when: "matrix_bridge_mautrix_gvoice_database_engine == 'postgres'"
   12 |   block:
   13 |     - name: Check if an SQLite database already exists
   14 |       ansible.builtin.stat:
   15 |         path: "{{ matrix_bridge_mautrix_gvoice_sqlite_database_path_local }}"
   16 |       register: matrix_bridge_mautrix_gvoice_sqlite_database_path_local_stat_result
   17 | 
   18 |     - when: "matrix_bridge_mautrix_gvoice_sqlite_database_path_local_stat_result.stat.exists | bool"
   19 |       block:
   20 |         - ansible.builtin.include_role:
   21 |             name: galaxy/postgres
   22 |             tasks_from: migrate_db_to_postgres
   23 |           vars:
   24 |             postgres_db_migration_request:
   25 |               src: "{{ matrix_bridge_mautrix_gvoice_sqlite_database_path_local }}"
   26 |               dst: "{{ matrix_bridge_mautrix_gvoice_database_connection_string }}"
   27 |               caller: "{{ role_path | basename }}"
   28 |               engine_variable_name: 'matrix_bridge_mautrix_gvoice_database_engine'
   29 |               engine_old: 'sqlite'
   30 |               systemd_services_to_stop: ['matrix-mautrix-gvoice.service']
   31 |               pgloader_options: ['--with "quote identifiers"']
   32 | 
   33 |         - ansible.builtin.set_fact:
   34 |             matrix_bridge_mautrix_gvoice_migration_requires_restart: true
   35 | 
   36 | - name: Ensure Mautrix gvoice paths exists
   37 |   ansible.builtin.file:
   38 |     path: "{{ item.path }}"
   39 |     state: directory
   40 |     mode: '0750'
   41 |     owner: "{{ matrix_user_name }}"
   42 |     group: "{{ matrix_group_name }}"
   43 |   with_items:
   44 |     - {path: "{{ matrix_bridge_mautrix_gvoice_base_path }}", when: true}
   45 |     - {path: "{{ matrix_bridge_mautrix_gvoice_config_path }}", when: true}
   46 |     - {path: "{{ matrix_bridge_mautrix_gvoice_data_path }}", when: true}
   47 |     - {path: "{{ matrix_bridge_mautrix_gvoice_container_src_files_path }}", when: "{{ matrix_bridge_mautrix_gvoice_container_image_self_build }}"}
   48 |   when: item.when | bool
   49 | 
   50 | - name: Ensure Mautrix gvoice image is pulled
   51 |   community.docker.docker_image_pull:
   52 |     name: "{{ matrix_bridge_mautrix_gvoice_container_image }}"
   53 |     pull: always
   54 |   when: not matrix_bridge_mautrix_gvoice_container_image_self_build
   55 |   register: matrix_bridge_mautrix_gvoice_container_image_pull_result
   56 |   retries: "{{ devture_playbook_help_container_retries_count }}"
   57 |   delay: "{{ devture_playbook_help_container_retries_delay }}"
   58 |   until: matrix_bridge_mautrix_gvoice_container_image_pull_result is not failed
   59 | 
   60 | # A checkout owned by a different user (a uid change, an earlier clone by another user, etc.) would make the git task below fail on ownership or permissions.
   61 | - name: Ensure Mautrix gvoice repository ownership is correct on self-build
   62 |   ansible.builtin.file:
   63 |     path: "{{ matrix_bridge_mautrix_gvoice_container_src_files_path }}"
   64 |     state: directory
   65 |     owner: "{{ matrix_user_name }}"
   66 |     group: "{{ matrix_group_name }}"
   67 |     recurse: true
   68 |   when: "matrix_bridge_mautrix_gvoice_container_image_self_build | bool"
   69 | 
   70 | - name: Ensure Mautrix gvoice repository is present on self-build
   71 |   ansible.builtin.git:
   72 |     repo: "{{ matrix_bridge_mautrix_gvoice_container_image_self_build_repo }}"
   73 |     dest: "{{ matrix_bridge_mautrix_gvoice_container_src_files_path }}"
   74 |     version: "{{ matrix_bridge_mautrix_gvoice_container_image_self_build_branch }}"
   75 |     force: "yes"
   76 |   become: true
   77 |   become_user: "{{ matrix_user_name }}"
   78 |   register: matrix_bridge_mautrix_gvoice_git_pull_results
   79 |   when: "matrix_bridge_mautrix_gvoice_container_image_self_build | bool"
   80 | 
   81 | - name: Ensure Mautrix gvoice Docker image is built
   82 |   community.docker.docker_image_build:
   83 |     name: "{{ matrix_bridge_mautrix_gvoice_container_image }}"
   84 |     dockerfile: Dockerfile
   85 |     path: "{{ matrix_bridge_mautrix_gvoice_container_src_files_path }}"
   86 |     pull: true
   87 |     rebuild: "{{ 'always' if matrix_bridge_mautrix_gvoice_git_pull_results.changed | bool else 'never' }}"
   88 |   when: "matrix_bridge_mautrix_gvoice_container_image_self_build | bool"
   89 |   register: matrix_bridge_mautrix_gvoice_container_image_build_result
   90 | 
   91 | - name: Check if an old database file exists
   92 |   ansible.builtin.stat:
   93 |     path: "{{ matrix_bridge_mautrix_gvoice_base_path }}/mautrix-gvoice.db"
   94 |   register: matrix_bridge_mautrix_gvoice_stat_database
   95 | 
   96 | - name: Check if an old Matrix state file exists
   97 |   ansible.builtin.stat:
   98 |     path: "{{ matrix_bridge_mautrix_gvoice_base_path }}/mx-state.json"
   99 |   register: matrix_bridge_mautrix_gvoice_stat_mx_state
  100 | 
  101 | - name: (Data relocation) Ensure matrix-mautrix-gvoice.service is stopped
  102 |   ansible.builtin.service:
  103 |     name: matrix-mautrix-gvoice
  104 |     state: stopped
  105 |     enabled: false
  106 |     daemon_reload: true
  107 |   failed_when: false
  108 |   when: "matrix_bridge_mautrix_gvoice_stat_database.stat.exists"
  109 | 
  110 | - name: (Data relocation) Move mautrix-gvoice database file to ./data directory
  111 |   ansible.builtin.command:
  112 |     cmd: "mv {{ matrix_bridge_mautrix_gvoice_base_path }}/mautrix-gvoice.db {{ matrix_bridge_mautrix_gvoice_data_path }}/mautrix-gvoice.db"
  113 |     creates: "{{ matrix_bridge_mautrix_gvoice_data_path }}/mautrix-gvoice.db"
  114 |     removes: "{{ matrix_bridge_mautrix_gvoice_base_path }}/mautrix-gvoice.db"
  115 |   when: "matrix_bridge_mautrix_gvoice_stat_database.stat.exists"
  116 | 
  117 | - name: (Data relocation) Move mautrix-gvoice mx-state file to ./data directory
  118 |   ansible.builtin.command:
  119 |     cmd: "mv {{ matrix_bridge_mautrix_gvoice_base_path }}/mx-state.json {{ matrix_bridge_mautrix_gvoice_data_path }}/mx-state.json"
  120 |     creates: "{{ matrix_bridge_mautrix_gvoice_data_path }}/mx-state.json"
  121 |     removes: "{{ matrix_bridge_mautrix_gvoice_base_path }}/mx-state.json"
  122 |   when: "matrix_bridge_mautrix_gvoice_stat_mx_state.stat.exists"
  123 | 
  124 | - name: Ensure mautrix-gvoice config.yaml installed
  125 |   ansible.builtin.copy:
  126 |     content: "{{ matrix_bridge_mautrix_gvoice_configuration | to_nice_yaml(indent=2, width=999999) }}"
  127 |     dest: "{{ matrix_bridge_mautrix_gvoice_config_path }}/config.yaml"
  128 |     mode: '0644'
  129 |     owner: "{{ matrix_user_name }}"
  130 |     group: "{{ matrix_group_name }}"
  131 |   register: matrix_bridge_mautrix_gvoice_config_result
  132 | 
  133 | - name: Ensure mautrix-gvoice registration.yaml installed
  134 |   ansible.builtin.copy:
  135 |     content: "{{ matrix_bridge_mautrix_gvoice_registration | to_nice_yaml(indent=2, width=999999) }}"
  136 |     dest: "{{ matrix_bridge_mautrix_gvoice_config_path }}/registration.yaml"
  137 |     mode: '0644'
  138 |     owner: "{{ matrix_user_name }}"
  139 |     group: "{{ matrix_group_name }}"
  140 |   register: matrix_bridge_mautrix_gvoice_registration_result
  141 | 
  142 | - name: Ensure matrix-mautrix-gvoice.service installed
  143 |   ansible.builtin.template:
  144 |     src: "{{ role_path }}/templates/systemd/matrix-mautrix-gvoice.service.j2"
  145 |     dest: "{{ devture_systemd_docker_base_systemd_path }}/matrix-mautrix-gvoice.service"
  146 |     mode: '0644'
  147 |   register: matrix_bridge_mautrix_gvoice_systemd_service_result
  148 | 
  149 | - name: Ensure mautrix-gvoice support files installed
  150 |   ansible.builtin.template:
  151 |     src: "{{ role_path }}/templates/{{ item }}.j2"
  152 |     dest: "{{ matrix_bridge_mautrix_gvoice_base_path }}/{{ item }}"
  153 |     mode: '0640'
  154 |     owner: "{{ matrix_user_name }}"
  155 |     group: "{{ matrix_group_name }}"
  156 |   with_items:
  157 |     - labels
  158 |   register: matrix_bridge_mautrix_gvoice_support_files_result
  159 | 
  160 | - name: Ensure matrix-mautrix-gvoice container network is created
  161 |   when: matrix_bridge_mautrix_gvoice_container_network != 'host'
  162 |   community.general.docker_network:
  163 |     enable_ipv6: "{{ devture_systemd_docker_base_ipv6_enabled }}"
  164 |     name: "{{ matrix_bridge_mautrix_gvoice_container_network }}"
  165 |     driver: bridge
  166 |     driver_options: "{{ devture_systemd_docker_base_container_networks_driver_options }}"
  167 | 
  168 | - name: Determine whether matrix-mautrix-gvoice needs a restart
  169 |   ansible.builtin.set_fact:
  170 |     matrix_bridge_mautrix_gvoice_restart_necessary: >-
  171 |       {{
  172 |         matrix_bridge_mautrix_gvoice_migration_requires_restart | default(false)
  173 |         or matrix_bridge_mautrix_gvoice_config_result.changed | default(false)
  174 |         or matrix_bridge_mautrix_gvoice_registration_result.changed | default(false)
  175 |         or matrix_bridge_mautrix_gvoice_support_files_result.changed | default(false)
  176 |         or matrix_bridge_mautrix_gvoice_systemd_service_result.changed | default(false)
  177 |         or matrix_bridge_mautrix_gvoice_container_image_pull_result.changed | default(false)
  178 |         or matrix_bridge_mautrix_gvoice_container_image_build_result.changed | default(false)
  179 |       }}
  180 | 
  181 | - name: Ensure matrix-mautrix-gvoice.service restarted, if necessary
  182 |   ansible.builtin.service:
  183 |     name: "matrix-mautrix-gvoice.service"
  184 |     state: restarted
  185 |     daemon_reload: true
  186 |   when: "matrix_bridge_mautrix_gvoice_migration_requires_restart | bool"
```

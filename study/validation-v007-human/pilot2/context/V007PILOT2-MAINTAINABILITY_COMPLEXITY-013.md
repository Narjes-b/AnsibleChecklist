# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-013

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: maintainability_complexity
- Rule: `ansibleguard/complex-expression`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `roles/custom/matrix-bridge-heisenbridge/tasks/setup_install.yml` (reported anchor line 70)
- Flagged construct: not named by the finding; the anchor line 70 lies in the task at line 67, name `Determine whether matrix-heisenbridge needs a restart`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–75 of 75:

```text
    1 | # SPDX-FileCopyrightText: 2021 Toni Spets
    2 | # SPDX-FileCopyrightText: 2022 - 2024 Slavi Pantaleev
    3 | # SPDX-FileCopyrightText: 2022 Jim Myhrberg
    4 | # SPDX-FileCopyrightText: 2022 Marko Weltzer
    5 | # SPDX-FileCopyrightText: 2022 Nikita Chernyi
    6 | # SPDX-FileCopyrightText: 2022 Sebastian Gumprich
    7 | # SPDX-FileCopyrightText: 2024 David Mehren
    8 | #
    9 | # SPDX-License-Identifier: AGPL-3.0-or-later
   10 | 
   11 | ---
   12 | 
   13 | - name: Ensure Heisenbridge image is pulled
   14 |   community.docker.docker_image_pull:
   15 |     name: "{{ matrix_bridge_heisenbridge_container_image }}"
   16 |     pull: always
   17 |   register: matrix_bridge_heisenbridge_container_image_pull_result
   18 |   retries: "{{ devture_playbook_help_container_retries_count }}"
   19 |   delay: "{{ devture_playbook_help_container_retries_delay }}"
   20 |   until: matrix_bridge_heisenbridge_container_image_pull_result is not failed
   21 | 
   22 | - name: Ensure Heisenbridge paths exist
   23 |   ansible.builtin.file:
   24 |     path: "{{ item }}"
   25 |     state: directory
   26 |     mode: '0750'
   27 |     owner: "{{ matrix_user_name }}"
   28 |     group: "{{ matrix_group_name }}"
   29 |   with_items:
   30 |     - "{{ matrix_bridge_heisenbridge_base_path }}"
   31 | 
   32 | - name: Ensure Heisenbridge registration.yaml installed if provided
   33 |   ansible.builtin.copy:
   34 |     content: "{{ matrix_bridge_heisenbridge_registration | to_nice_yaml(indent=2, width=999999) }}"
   35 |     dest: "{{ matrix_bridge_heisenbridge_base_path }}/registration.yaml"
   36 |     mode: '0644'
   37 |     owner: "{{ matrix_user_name }}"
   38 |     group: "{{ matrix_group_name }}"
   39 |   register: matrix_bridge_heisenbridge_registration_result
   40 | 
   41 | - name: Ensure Heisenbridge support files installed
   42 |   ansible.builtin.template:
   43 |     src: "{{ role_path }}/templates/{{ item }}.j2"
   44 |     dest: "{{ matrix_bridge_heisenbridge_base_path }}/{{ item }}"
   45 |     mode: '0640'
   46 |     owner: "{{ matrix_user_name }}"
   47 |     group: "{{ matrix_group_name }}"
   48 |   with_items:
   49 |     - labels
   50 |   register: matrix_bridge_heisenbridge_support_files_result
   51 | 
   52 | - name: Ensure Heisenbridge container network is created
   53 |   when: matrix_bridge_heisenbridge_container_network != 'host'
   54 |   community.general.docker_network:
   55 |     enable_ipv6: "{{ devture_systemd_docker_base_ipv6_enabled }}"
   56 |     name: "{{ matrix_bridge_heisenbridge_container_network }}"
   57 |     driver: bridge
   58 |     driver_options: "{{ devture_systemd_docker_base_container_networks_driver_options }}"
   59 | 
   60 | - name: Ensure matrix-heisenbridge.service installed
   61 |   ansible.builtin.template:
   62 |     src: "{{ role_path }}/templates/systemd/matrix-heisenbridge.service.j2"
   63 |     dest: "{{ devture_systemd_docker_base_systemd_path }}/matrix-heisenbridge.service"
   64 |     mode: '0644'
   65 |   register: matrix_bridge_heisenbridge_systemd_service_result
   66 | 
   67 | - name: Determine whether matrix-heisenbridge needs a restart
   68 |   ansible.builtin.set_fact:
   69 |     matrix_bridge_heisenbridge_restart_necessary: >-
   70 |       {{
   71 |         matrix_bridge_heisenbridge_registration_result.changed | default(false)
   72 |         or matrix_bridge_heisenbridge_support_files_result.changed | default(false)
   73 |         or matrix_bridge_heisenbridge_systemd_service_result.changed | default(false)
   74 |         or matrix_bridge_heisenbridge_container_image_pull_result.changed | default(false)
   75 |       }}
```

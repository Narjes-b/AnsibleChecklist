# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-022

- Repository: `ethpandaops/ansible-collection-general`
- Commit: `15a1f3490258357c4652b96b80f0a92636fa4135`
- Family: Maintainability/complexity
- Rule: `ansibleguard/shell-instead-of-module`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/grandine/tasks/setup.yaml` (reported anchor line 32)
- Object: `task` `7a5a8c831af830baa46c5a251c08b097b78ea103b882e64c3b20e7f8194ec063`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–75 of 75:

```text
    1 | - name: Add grandine user
    2 |   ansible.builtin.user:
    3 |     name: "{{ grandine_user }}"
    4 |   register: grandine_user_meta
    5 | 
    6 | - name: Create data dir
    7 |   ansible.builtin.file:
    8 |     path: "{{ grandine_datadir }}"
    9 |     state: directory
   10 |     mode: "0750"
   11 |     owner: "{{ grandine_user }}"
   12 |     group: "{{ grandine_user }}"
   13 | 
   14 | - name: Set permissions
   15 |   ansible.builtin.command: "chown -R {{ grandine_user }}:{{ grandine_user }} {{ grandine_datadir }}" # noqa no-free-form
   16 |   failed_when: false
   17 |   changed_when: false
   18 | 
   19 | - name: Create validator data dir
   20 |   ansible.builtin.file:
   21 |     path: "{{ item }}"
   22 |     state: directory
   23 |     mode: "0750"
   24 |     owner: "{{ grandine_user }}"
   25 |     group: "{{ grandine_user }}"
   26 |   loop:
   27 |     - "{{ grandine_validator_datadir }}"
   28 |     - "{{ grandine_validator_datadir }}/keys"
   29 |     - "{{ grandine_validator_datadir }}/secrets"
   30 |   when: grandine_validator_enabled
   31 | 
   32 | - name: Set permissions for validator data dir
   33 |   ansible.builtin.command: "chown -R {{ grandine_user }}:{{ grandine_user }} {{ grandine_validator_datadir }}" # noqa no-free-form
   34 |   failed_when: false
   35 |   changed_when: false
   36 |   when: grandine_validator_enabled
   37 | 
   38 | - name: Run grandine container
   39 |   community.docker.docker_container:
   40 |     name: "{{ grandine_container_name }}"
   41 |     image: "{{ grandine_container_image }}"
   42 |     image_name_mismatch: recreate
   43 |     state: started
   44 |     restart_policy: always
   45 |     stop_timeout: "{{ grandine_container_stop_timeout }}"
   46 |     ports: "{{ grandine_container_ports }}"
   47 |     volumes: "{{ grandine_container_volumes + (grandine_validator_enabled | ternary(grandine_container_validator_volumes, [])) }}"
   48 |     env: "{{ grandine_container_env }}"
   49 |     networks: "{{ grandine_container_networks }}"
   50 |     entrypoint: "{{ grandine_container_entrypoint | default(omit) }}"
   51 |     command: >-
   52 |       {{
   53 |         grandine_container_command +
   54 |         (grandine_validator_enabled | ternary(grandine_container_validator_args +
   55 |           (grandine_mev_boost_enabled | ternary(grandine_mev_boost_beacon_command,[])),
   56 |         [])) +
   57 |         (grandine_checkpoint_sync_enabled | ternary(
   58 |           grandine_container_command_extra_args + grandine_container_command_checkpoint_args,
   59 |           grandine_container_command_extra_args
   60 |         ))
   61 |       }}
   62 |     user: "{{ grandine_user_meta.uid }}"
   63 |     pull: "{{ grandine_container_pull | bool }}"
   64 |     security_opts: "{{ grandine_container_security_opts }}"
   65 |     memory: "{{ grandine_container_memory | default(omit) }}"
   66 |     memory_reservation: "{{ grandine_container_memory_reservation | default(omit) }}"
   67 |     memory_swap: "{{ grandine_container_memory_swap | default(omit) }}"
   68 |     memory_swappiness: "{{ grandine_container_memory_swappiness | default(omit) }}"
   69 |     kernel_memory: "{{ grandine_container_kernel_memory | default(omit) }}"
   70 |     cpus: "{{ grandine_container_cpus | default(omit) }}"
   71 |     cpuset_cpus: "{{ grandine_container_cpuset_cpus | default(omit) }}"
   72 |     cpuset_mems: "{{ grandine_container_cpuset_mems | default(omit) }}"
   73 |     cpu_shares: "{{ grandine_container_cpu_shares | default(omit) }}"
   74 |     cpu_quota: "{{ grandine_container_cpu_quota | default(omit) }}"
   75 |     cpu_period: "{{ grandine_container_cpu_period | default(omit) }}"
```

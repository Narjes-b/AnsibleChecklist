# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-004

- Repository: `ethpandaops/ansible-collection-general`
- Commit: `15a1f3490258357c4652b96b80f0a92636fa4135`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/lighthouse/tasks/setup.yaml` (reported anchor line 73)
- Object: `source_location` `061c8c11f582fd96842fb044d562760b8d261f5b90351c5dd9face36b5b2c7e1`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–110 of 110:

```text
    1 | - name: Add lighthouse user
    2 |   ansible.builtin.user:
    3 |     name: "{{ lighthouse_user }}"
    4 |   register: lighthouse_user_meta
    5 | 
    6 | - name: Configure lighthouse beacon client
    7 |   when: lighthouse_enabled
    8 |   block:
    9 |     - name: Create data dir
   10 |       ansible.builtin.file:
   11 |         path: "{{ lighthouse_datadir }}"
   12 |         state: directory
   13 |         mode: "0750"
   14 |         owner: "{{ lighthouse_user }}"
   15 |         group: "{{ lighthouse_user }}"
   16 | 
   17 |     - name: Set permissions
   18 |       ansible.builtin.command: "chown -R {{ lighthouse_user }}:{{ lighthouse_user }} {{ lighthouse_datadir }}" # noqa no-free-form
   19 |       failed_when: false
   20 |       changed_when: false
   21 | 
   22 |     - name: Run lighthouse container
   23 |       community.docker.docker_container:
   24 |         name: "{{ lighthouse_container_name }}"
   25 |         image: "{{ lighthouse_container_image }}"
   26 |         image_name_mismatch: recreate
   27 |         state: started
   28 |         restart_policy: always
   29 |         stop_timeout: "{{ lighthouse_container_stop_timeout }}"
   30 |         ports: "{{ lighthouse_container_ports }}"
   31 |         volumes: "{{ lighthouse_container_volumes }}"
   32 |         env: "{{ lighthouse_container_env }}"
   33 |         networks: "{{ lighthouse_container_networks }}"
   34 |         entrypoint: "{{ lighthouse_container_entrypoint | default(omit) }}"
   35 |         command: >-
   36 |           {{
   37 |             lighthouse_container_command +
   38 |             lighthouse_container_command_extra_args +
   39 |             (lighthouse_checkpoint_sync_enabled | ternary(lighthouse_container_command_checkpoint_args, [])) +
   40 |             (lighthouse_mev_boost_enabled | ternary(lighthouse_mev_boost_beacon_command, []))
   41 |           }}
   42 |         user: "{{ lighthouse_user_meta.uid }}"
   43 |         pull: "{{ lighthouse_container_pull | bool }}"
   44 |         security_opts: "{{ lighthouse_container_security_opts }}"
   45 |         memory: "{{ lighthouse_container_memory | default(omit) }}"
   46 |         memory_reservation: "{{ lighthouse_container_memory_reservation | default(omit) }}"
   47 |         memory_swap: "{{ lighthouse_container_memory_swap | default(omit) }}"
   48 |         memory_swappiness: "{{ lighthouse_container_memory_swappiness | default(omit) }}"
   49 |         kernel_memory: "{{ lighthouse_container_kernel_memory | default(omit) }}"
   50 |         cpus: "{{ lighthouse_container_cpus | default(omit) }}"
   51 |         cpuset_cpus: "{{ lighthouse_container_cpuset_cpus | default(omit) }}"
   52 |         cpuset_mems: "{{ lighthouse_container_cpuset_mems | default(omit) }}"
   53 |         cpu_shares: "{{ lighthouse_container_cpu_shares | default(omit) }}"
   54 |         cpu_quota: "{{ lighthouse_container_cpu_quota | default(omit) }}"
   55 |         cpu_period: "{{ lighthouse_container_cpu_period | default(omit) }}"
   56 | 
   57 | 
   58 | - name: Configure lighthouse validator client
   59 |   when: lighthouse_validator_enabled
   60 |   block:
   61 |     - name: Create validator data dir
   62 |       ansible.builtin.file:
   63 |         path: "{{ item }}"
   64 |         state: directory
   65 |         mode: "0750"
   66 |         owner: "{{ lighthouse_user }}"
   67 |         group: "{{ lighthouse_user }}"
   68 |       loop:
   69 |         - "{{ lighthouse_validator_datadir }}"
   70 |         - "{{ lighthouse_validator_datadir }}/keys"
   71 |         - "{{ lighthouse_validator_datadir }}/secrets"
   72 | 
   73 |     - name: Set permissions for validator data dir
   74 |       ansible.builtin.command: "chown -R {{ lighthouse_user }}:{{ lighthouse_user }} {{ lighthouse_validator_datadir }}" # noqa no-free-form
   75 |       failed_when: false
   76 |       changed_when: false
   77 | 
   78 |     - name: Run lighthouse validator container
   79 |       community.docker.docker_container:
   80 |         name: "{{ lighthouse_validator_container_name }}"
   81 |         image: "{{ lighthouse_validator_container_image }}"
   82 |         image_name_mismatch: recreate
   83 |         state: started
   84 |         restart_policy: always
   85 |         stop_timeout: "{{ lighthouse_validator_container_stop_timeout }}"
   86 |         ports: "{{ lighthouse_validator_container_ports }}"
   87 |         volumes: "{{ lighthouse_validator_container_volumes }}"
   88 |         env: "{{ lighthouse_validator_container_env }}"
   89 |         networks: "{{ lighthouse_validator_container_networks }}"
   90 |         entrypoint: "{{ lighthouse_validator_container_entrypoint | default(omit) }}"
   91 |         command: >-
   92 |           {{
   93 |             lighthouse_validator_container_command +
   94 |             lighthouse_validator_container_command_extra_args +
   95 |             (lighthouse_mev_boost_enabled | ternary(lighthouse_mev_boost_validator_command, []))
   96 |           }}
   97 |         user: "{{ lighthouse_user_meta.uid }}"
   98 |         pull: "{{ lighthouse_container_pull | bool }}"
   99 |         security_opts: "{{ lighthouse_validator_container_security_opts }}"
  100 |         memory: "{{ lighthouse_validator_container_memory | default(omit) }}"
  101 |         memory_reservation: "{{ lighthouse_validator_container_memory_reservation | default(omit) }}"
  102 |         memory_swap: "{{ lighthouse_validator_container_memory_swap | default(omit) }}"
  103 |         memory_swappiness: "{{ lighthouse_validator_container_memory_swappiness | default(omit) }}"
  104 |         kernel_memory: "{{ lighthouse_validator_container_kernel_memory | default(omit) }}"
  105 |         cpus: "{{ lighthouse_validator_container_cpus | default(omit) }}"
  106 |         cpuset_cpus: "{{ lighthouse_validator_container_cpuset_cpus | default(omit) }}"
  107 |         cpuset_mems: "{{ lighthouse_validator_container_cpuset_mems | default(omit) }}"
  108 |         cpu_shares: "{{ lighthouse_validator_container_cpu_shares | default(omit) }}"
  109 |         cpu_quota: "{{ lighthouse_validator_container_cpu_quota | default(omit) }}"
  110 |         cpu_period: "{{ lighthouse_validator_container_cpu_period | default(omit) }}"
```

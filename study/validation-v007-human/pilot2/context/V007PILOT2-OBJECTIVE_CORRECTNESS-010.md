# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-010

- Repository: `ethpandaops/ansible-collection-general`
- Commit: `15a1f3490258357c4652b96b80f0a92636fa4135`
- Family: objective_correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/ethereum_genesis/tasks/generate_genesis.yaml` (reported anchor line 92)
- Flagged construct: not named by the finding; the anchor line 92 lies in the task at line 92, name `Move tmp output to final output dir`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–116 of 116:

```text
    1 | - name: "Run genesis generation"
    2 |   vars:
    3 |     ansible_connection: local
    4 |   delegate_to: 127.0.0.1
    5 |   run_once: true
    6 |   become: false
    7 |   block:
    8 |     - name: Create temporary config directory
    9 |       ansible.builtin.tempfile:
   10 |         state: directory
   11 |         suffix: ethereum-genesis-config-input
   12 |       register: ethereum_genesis_generator_tmp_config_dir_register
   13 | 
   14 |     - name: Create temporary output directory
   15 |       ansible.builtin.tempfile:
   16 |         state: directory
   17 |         suffix: ethereum-genesis-config-output
   18 |       register: ethereum_genesis_generator_tmp_output_dir_register
   19 | 
   20 |     - name: Create config file directories
   21 |       ansible.builtin.file:
   22 |         path: "{{ ethereum_genesis_generator_tmp_config_dir_register.path }}/{{ item.key | dirname }}"
   23 |         state: directory
   24 |         mode: '0755'
   25 |       loop: "{{ ethereum_genesis_generator_config_files | dict2items }}"
   26 | 
   27 |     - name: Copy config files
   28 |       ansible.builtin.copy:
   29 |         content: "{{ item.value }}"
   30 |         dest: "{{ ethereum_genesis_generator_tmp_config_dir_register.path }}/{{ item.key }}"
   31 |         mode: "0644"
   32 |       loop: "{{ ethereum_genesis_generator_config_files | dict2items }}"
   33 | 
   34 |     - name: Check if Docker is rootless
   35 |       ansible.builtin.command: docker info -f '{{ "{{json .SecurityOptions}}" }}'
   36 |       register: ethereum_genesis_docker_secopts
   37 |       changed_when: false
   38 | 
   39 |     - name: Set rootless fact
   40 |       ansible.builtin.set_fact:
   41 |         ethereum_genesis_docker_is_rootless: "{{ 'name=rootless' in ethereum_genesis_docker_secopts.stdout }}"
   42 | 
   43 |     - name: Compute docker user flag
   44 |       ansible.builtin.set_fact:
   45 |         ethereum_genesis_docker_user_flag: >-
   46 |           {{ ethereum_genesis_docker_is_rootless | ternary('', '-u ' ~ lookup('ansible.builtin.pipe', 'id -u')) }}
   47 | 
   48 |     - name: Run genesis generator
   49 |       ansible.builtin.shell: >
   50 |         docker run --rm -t {{ ethereum_genesis_docker_user_flag }}
   51 |         -v {{ ethereum_genesis_generator_tmp_output_dir_register.path }}:/data
   52 |         -v {{ ethereum_genesis_generator_tmp_config_dir_register.path }}:/config
   53 |         {{ ethereum_genesis_generator_container_image }} all
   54 |       register: ethereum_genesis_generator_cmd
   55 |       changed_when: false
   56 |       failed_when: (ethereum_genesis_generator_cmd.rc != 0) or (ethereum_genesis_generator_cmd.stdout == "")
   57 | 
   58 |     - name: Removes extended attr from config.yaml, breaks on linux due to perms if present
   59 |       ansible.builtin.command: xattr -c "{{ ethereum_genesis_generator_tmp_output_dir_register.path }}/metadata/config.yaml"
   60 |       changed_when: true
   61 |       when: ansible_os_family == "Darwin"
   62 | 
   63 |     - name: Set config.yaml to the right permissions post attribute change
   64 |       ansible.builtin.file:
   65 |         path: "{{ ethereum_genesis_generator_tmp_output_dir_register.path }}/metadata/config.yaml"
   66 |         mode: '0644'
   67 |       when: ansible_os_family == "Darwin"
   68 | 
   69 |     - name: Create final output directory
   70 |       ansible.builtin.file:
   71 |         path: "{{ ethereum_genesis_generator_output_dir }}"
   72 |         state: directory
   73 |         mode: '0755'
   74 | 
   75 |     - name: Create final output directory
   76 |       ansible.builtin.file:
   77 |         path: "{{ ethereum_genesis_generator_output_dir }}/metadata"
   78 |         state: directory
   79 |         mode: '0755'
   80 | 
   81 |     - name: Create final output directory
   82 |       ansible.builtin.file:
   83 |         path: "{{ ethereum_genesis_generator_output_dir }}/parsed"
   84 |         state: directory
   85 |         mode: '0755'
   86 | 
   87 |     - name: Move tmp output to final output dir
   88 |       ansible.builtin.shell: >
   89 |         mv {{ ethereum_genesis_generator_tmp_output_dir_register.path }}/metadata/* {{ ethereum_genesis_generator_output_dir }}/metadata/
   90 |       changed_when: true
   91 | 
   92 |     - name: Move tmp output to final output dir
   93 |       ansible.builtin.shell: >
   94 |         mv {{ ethereum_genesis_generator_tmp_output_dir_register.path }}/parsed/* {{ ethereum_genesis_generator_output_dir }}/parsed/
   95 |       changed_when: true
   96 | 
   97 |     - name: Cleanup tmp dirs
   98 |       ansible.builtin.file:
   99 |         path: "{{ item }}"
  100 |         state: absent
  101 |       loop:
  102 |         - "{{ ethereum_genesis_generator_tmp_config_dir_register.path }}"
  103 |         - "{{ ethereum_genesis_generator_tmp_output_dir_register.path }}"
  104 | 
  105 |     - name: Info
  106 |       ansible.builtin.debug:
  107 |         msg: "Genesis configs can be found in the following directory: {{ ethereum_genesis_generator_output_dir }}"
  108 |   always:
  109 |     - name: Inform of failure
  110 |       ansible.builtin.debug:
  111 |         msg: |
  112 |           Something went wrong. Some useful information that can be used to debug the problem:
  113 |           - Temp config dir: {{ ethereum_genesis_generator_tmp_config_dir_register.path }}
  114 |           - Temp output dir: {{ ethereum_genesis_generator_tmp_output_dir_register.path }}
  115 |       when: >-
  116 |         (ethereum_genesis_generator_cmd.rc | default('')  != 0)
```

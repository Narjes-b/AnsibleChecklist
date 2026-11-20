# Frozen source context: V007PILOT2-STRUCTURE_REUSE-017

- Repository: `redhat-cop/aap_configuration_extended`
- Commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Family: structure_reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/offline_sync/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/offline_sync/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–80 of 80:

```text
    1 | ---
    2 | - name: Create directory to work in
    3 |   ansible.builtin.file:
    4 |     path: "{{ hub_configuration_working_dir }}"
    5 |     state: directory
    6 |     mode: "0755"
    7 | 
    8 | - name: Check for ansible.cfg
    9 |   ansible.builtin.stat:
   10 |     path: "{{ hub_configuration_working_dir }}/ansible.cfg"
   11 |   register: r_ansible_cfg
   12 | 
   13 | - name: Figuring out AH token
   14 |   when: (not r_ansible_cfg['stat']['exists']) and (aap_token is not defined or ah_token['token'] is defined)
   15 |   block:
   16 |     - name: Authenticate and get an API token from Automation Hub
   17 |       ansible.hub.ah_token:[REDACTED VALUE BLOCK]
   18 |         [REDACTED ENCRYPTED VALUE]
      [... 4 further identical redacted lines, through 22]
   23 |       register: r_aap_token
   24 | 
   25 |     - name: Fixing format
   26 |       ansible.builtin.set_fact:
   27 |         aap_token: "{{ ah_token['token'] }}"
   28 |       when: r_aap_token['changed']  # noqa: no-handler
   29 | 
   30 | - name: Create ansible.cfg
   31 |   ansible.builtin.template:
   32 |     src: ansible.cfg.j2
   33 |     dest: "{{ hub_configuration_working_dir }}/ansible.cfg"
   34 |     mode: "0755"
   35 |   when: not r_ansible_cfg['stat']['exists']
   36 | 
   37 | - name: Get list of all collections
   38 |   ansible.builtin.uri:
   39 |     url: "https://{{ aap_hostname | default(hub_host) }}/api/galaxy/pulp/api/v3/ansible/collections/?limit=1000"
   40 |     user: "{{ aap_username }}"
   41 |     password: "{{ aap_password }}"
   42 |     method: GET
   43 |     force_basic_auth: true
   44 |     validate_certs: "{{ aap_validate_certs }}"
   45 |   register: r_collections
   46 | 
   47 | - name: Create requirements.yml
   48 |   ansible.builtin.template:
   49 |     src: collections.yml.j2
   50 |     dest: "{{ hub_configuration_working_dir }}/requirements.yml"
   51 |     mode: "0755"
   52 | 
   53 | - name: Create directory to put all collections
   54 |   ansible.builtin.file:
   55 |     path: "{{ hub_configuration_working_dir }}/collections"
   56 |     state: directory
   57 |     mode: "0755"
   58 | 
   59 | - name: Download all collections
   60 |   ansible.builtin.command: ansible-galaxy collection download {% if hub_configuration_no_deps %}--no-deps{% endif %} -r requirements.yml -p "{{ hub_configuration_working_dir }}/collections"
   61 |   changed_when: true
   62 | 
   63 | - name: Find all relevant built collection files
   64 |   ansible.builtin.find:
   65 |     paths: "{{ collection_dir }}"
   66 |     patterns: "{{ (collection_dir) | ternary('*.tar.gz', (collection_dir | basename)) }}"
   67 |   register: __ah_collections_find_results
   68 |   vars:
   69 |     collection_dir: "{{ hub_configuration_working_dir }}/collections/"
   70 | 
   71 | - name: Create collections list
   72 |   ansible.builtin.template:
   73 |     src: collections_list.yml.j2
   74 |     dest: "{{ hub_configuration_working_dir }}/collections.yml"
   75 |     mode: "0755"
   76 |   vars:
   77 |     _namespaces: "{{ r_collections['json']['results'] | map(attribute='namespace') | flatten | sort | unique }}"
   78 |     _collections: "{{ (__ah_collections_find_results['files'] | flatten) | map(attribute='path') | flatten | sort | unique }}"
   79 | 
   80 | ...
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/offline_sync`; 9 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: no

roles/offline_sync/README.md
roles/offline_sync/defaults/main.yml
roles/offline_sync/meta/argument_specs.yml
roles/offline_sync/meta/main.yml
roles/offline_sync/tasks/main.yml
roles/offline_sync/templates/ansible.cfg.j2
roles/offline_sync/templates/collections.yml.j2
roles/offline_sync/templates/collections_list.yml.j2
roles/offline_sync/tests/test.yml
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- leaf tasks (not counting block containers): 11 (the rule needs more than 10)
- include/import task or role, or play-level roles, present: no
```

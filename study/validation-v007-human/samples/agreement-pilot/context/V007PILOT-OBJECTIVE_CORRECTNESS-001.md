# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-001

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: Objective correctness
- Rule: `ansibleguard/invalid-task-attribute-type`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `plugins/tripleo-undercloud/tasks/prepare_uc_images_external.yml` (reported anchor line 1)
- Object: `attribute` `0ba60551948aef3c7acf9be0a2d11283ce18100d9ecd87657a1fd8215463dcb2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–55 of 55:

```text
    1 | ---
    2 | - block:
    3 |     - name: download the script when it looks like a fetch url
    4 |       get_url:
    5 |           url: "{{ script_url }}"
    6 |           dest: "{{ script_target }}"
    7 |       become: true
    8 |       retries: 3
    9 |       delay: 3
   10 |       when:
   11 |           - script_url|regex_search('^https?://.*')
   12 |     - name: copy script from host
   13 |       copy:
   14 |           src: "{{ script_url }}"
   15 |           dest: "{{ script_target }}"
   16 |           mode: "0755"
   17 |       when:
   18 |           - not script_url|regex_search('^https?:/.*')
   19 |     - name: execute the custom registry script
   20 |       become: true
   21 |       become_user: root
   22 |       shell: |
   23 |               chmod 755 {{ script_target }}
   24 |               {{ script_target }} {{ script_args }} 2>&1 | tee -a "{{ script_log_target }}"
   25 |       environment:
   26 |               IR_CALL_ENV: "{{ conf|to_nice_json }}"
   27 |       args:
   28 |           warn: no
   29 |       tags: skip_ansible_lint
   30 | 
   31 |     - name: fetch registries fact
   32 |       become: true
   33 |       become_user: root
   34 |       shell: |
   35 |           cat {{ working_dir }}/ir_registry_facts.json
   36 |       register: registry_facts
   37 |       tags: skip_ansible_lint
   38 | 
   39 |     - debug:
   40 |          msg: "registry script facts '''{{ registry_facts.stdout }}'''"
   41 | 
   42 |       # insecure_registry_hosts is the expected one
   43 |       # insecure_registry_hosts is an array of strings
   44 |       # with_dict looks required
   45 |       # ignore_errors: until we drop py27 and old ansible support
   46 |     - name: Set registry facts from the script
   47 |       set_fact: {"{{ item.key }}":"{{ item.value }}"}
   48 |       with_dict: "{{ registry_facts.stdout|from_json }}"
   49 |       ignore_errors: "{{ ansible_version.full is version('2.9', '<') }}"
   50 |   vars:
   51 |       - conf: "{{ install|default({}) }}"
   52 |       - script_target: '{{ working_dir }}/custom_registry_script'
   53 |       - script_log_target: '/var/log/custom_registry_script.log'
   54 |       - script_url: "{{ install.get('registry', {}).get('custom', {}).get('script', {}).get('url', {})|default('') }}"
   55 |       - script_args: "{{ install.get('registry', {}).get('custom', {}).get('script', {}).get('args', {})|default('') }}"
```

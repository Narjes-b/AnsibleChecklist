# Frozen source context: V007PILOT2-STYLE_POLICY-014

- Repository: `ansible/awx-operator`
- Commit: `45363a1a0d312d16f740c626407a7521bbe3a31c`
- Family: style_policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/restore/tasks/main.yml` (reported anchor line 24)
- Flagged construct: task `build `additional_labels_items` labels from `additional_labels``
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–61 of 61:

```text
    1 | ---
    2 | - name: Patching labels to {{ kind }} kind
    3 |   k8s:
    4 |     state: present
    5 |     definition:
    6 |       apiVersion: '{{ api_version }}'
    7 |       kind: '{{ kind }}'
    8 |       name: '{{ ansible_operator_meta.name }}'
    9 |       namespace: '{{ ansible_operator_meta.namespace }}'
   10 |       metadata:
   11 |         name: '{{ ansible_operator_meta.name }}'
   12 |         namespace: '{{ ansible_operator_meta.namespace }}'
   13 |         labels: '{{ lookup("template", "../common/templates/labels/common.yaml.j2") | from_yaml }}'
   14 |   when: set_self_labels | bool
   15 | 
   16 | - name: Look up details for this restore object
   17 |   k8s_info:
   18 |     api_version: "{{ api_version }}"
   19 |     kind: "{{ kind }}"
   20 |     name: "{{ ansible_operator_meta.name }}"
   21 |     namespace: "{{ ansible_operator_meta.namespace }}"
   22 |   register: this_restore
   23 | 
   24 | - name: Build `additional_labels_items` labels from `additional_labels`
   25 |   set_fact:
   26 |     additional_labels_items: >-
   27 |       {{ this_restore['resources'][0]['metadata']['labels']
   28 |          | dict2items | selectattr('key', 'in', additional_labels)
   29 |       }}
   30 |   when:
   31 |   - additional_labels | length
   32 |   - this_restore['resources'][0]['metadata']['labels']
   33 | 
   34 | - block:
   35 |   - include_tasks: init.yml
   36 | 
   37 |   - include_tasks: import_vars.yml
   38 | 
   39 |   - include_tasks: secrets.yml
   40 | 
   41 |   - include_tasks: deploy_awx.yml
   42 | 
   43 |   - include_tasks: set_database_config.yml
   44 | 
   45 |   - include_tasks: check_postgres_backup.yml
   46 |     when: awx_postgres_type == 'unmanaged'
   47 | 
   48 |   - include_tasks: postgres.yml
   49 |     when: not postgres_skip_data | bool or awx_postgres_type == 'managed'
   50 | 
   51 |   - name: Set flag signifying this restore was successful
   52 |     set_fact:
   53 |       tower_restore_complete: True
   54 | 
   55 |   - include_tasks: cleanup.yml
   56 | 
   57 |   when:
   58 |   - this_restore['resources'][0]['status']['restoreComplete'] is not defined
   59 | 
   60 | - name: Update status variables
   61 |   include_tasks: update_status.yml
```

# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-009

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: Objective correctness
- Rule: `ansibleguard/invalid-task-attribute-type`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `src/commcare_cloud/ansible/roles/commcare-audit/tasks/main.yml` (reported anchor line 14)
- Object: `attribute` `2e5b801328d5dc7f891ace37879fcee0a6600bf4f3bc2bf9dce1bd8ed1b0635a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–27 of 27:

```text
    1 | ---
    2 | - name: Set host's audit directory
    3 |   set_fact:
    4 |     host_audit_directory: "{{ audit_path }}/{{ ansible_hostname }}"
    5 | 
    6 | - name: Create host's audit directory
    7 |   delegate_to: localhost
    8 |   become_user: "{{ control_user }}"
    9 |   file:
   10 |     path: "{{ host_audit_directory }}/"
   11 |     state: directory
   12 |     mode: '0755'
   13 | 
   14 | - name: Store disk usage stats
   15 |   include_tasks: disk_usage.yml
   16 |   vars:
   17 |     - audit_directory: "{{ host_audit_directory }}"
   18 | 
   19 | - name: Store data directory permissions
   20 |   include_tasks: file_permissions.yml
   21 |   vars:
   22 |     - audit_directory: "{{ host_audit_directory }}"
   23 | 
   24 | - name: Store filesystem stats
   25 |   include_tasks: filesystem_health.yml
   26 |   vars:
   27 |     - audit_directory: "{{ host_audit_directory }}"
```

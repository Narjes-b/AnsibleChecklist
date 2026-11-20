# Frozen source context: V007PILOT-SECURITY-028

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: Security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `src/commcare_cloud/ansible/pg_upgrade_rollback.yml` (reported anchor line 1)
- Object: `source_location` `651063ac9dc3515781c526d1033f1d07dacc27dc86bdad73d9c71944d2946064`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–62 of 62:

```text
    1 | ---
    2 | # Rollback playbook for use in recovering from a failure during upgrade.
    3 | #
    4 | # Usage:
    5 | #   commcare-cloud <env> ansible-playbook pg_upgrade_rollback.yml --limit pg0,pg1 \
    6 | #     -e old_version=9.6 -e new_version=12
    7 | #
    8 | - hosts:
    9 |     - all
   10 |   any_errors_fatal: true
   11 |   become: yes
   12 |   vars:
   13 |     new_version_service: "postgresql@{{ new_version }}-main.service"
   14 |   vars_prompt:
   15 |     - name: confirm_upgrade
   16 |       prompt: |
   17 | 
   18 |         ===================================================================================
   19 |         Are you sure you want to rollback a PostgreSQL upgrade?
   20 | 
   21 |         This can only be done if the v{{ new_version }} cluster has not been started yet.
   22 |         ===================================================================================
   23 |         Respond with [y/N]
   24 |       private: no
   25 |   tasks:
   26 |     - name: assert response
   27 |       assert:
   28 |         that: confirm_upgrade == 'y'
   29 | 
   30 |     - service_facts:
   31 | 
   32 |     - assert:
   33 |         that: new_version_service not in ansible_facts.services or ansible_facts.services.get(new_version_service).state == 'stopped'
   34 |         msg: "{{ new_version_service }} is running. Rollback is not possible."
   35 | 
   36 |     - name: Check upgrade in progress
   37 |       become: yes
   38 |       stat:
   39 |         path: "/opt/data/postgresql/{{ old_version }}/main/global/pg_control.old"
   40 |       register: pg_control
   41 |       check_mode: no
   42 | 
   43 |     - assert:
   44 |         that: "pg_control.stat.exists"
   45 |         msg: "pg_control.old does not exist for version specified. Is v{{ old_version }} cluster already rolled back?"
   46 | 
   47 |     - name: revert pg_control.old
   48 |       become: yes
   49 |       become_user: postgres
   50 |       command: "mv /opt/data/postgresql/{{ old_version }}/main/global/pg_control.old /opt/data/postgresql/{{ old_version }}/main/global/pg_control"
   51 | 
   52 |     - name: Start Postgresql
   53 |       become: yes
   54 |       service:
   55 |         name: "postgresql@{{ old_version }}-main"
   56 |         state: started
   57 | 
   58 |     - name: Re-enable monit for v{{ old_version }}
   59 |       become: yes
   60 |       monit_tmp:
   61 |         name: "postgresql_{{ old_version }}"
   62 |         state: monitored
```

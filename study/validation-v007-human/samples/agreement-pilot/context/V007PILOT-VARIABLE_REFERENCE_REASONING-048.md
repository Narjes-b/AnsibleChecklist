# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-048

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `src/commcare_cloud/ansible/roles/postgresql_base/tasks/check_standby_in_sync.yml` (reported anchor line 2)
- Object: `variable` `a48427e33375ab1eec67dadb7f76b9bbdc865da1783d1f21d801478487098c75`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–36 of 36:

```text
    1 | # Verify standbys are up to date with primaries
    2 | - name: Get primary checkpoint location
    3 |   delegate_to: "{{ hot_standby_master }}"
    4 |   shell: |
    5 |     set -o pipefail
    6 |     /usr/lib/postgresql/{{ old_version }}/bin/pg_controldata -D /opt/data/postgresql/{{ old_version }}/main | grep 'Latest checkpoint location' | awk '{ print $4 }'
    7 |   args:
    8 |     executable: /bin/bash
    9 |   register: primary_checkpoint
   10 |   check_mode: no
   11 |   when: retry_count == 0 or not checkpoints_match
   12 | 
   13 | - name: Get standby checkpoint location
   14 |   shell: |
   15 |     set -o pipefail
   16 |     /usr/lib/postgresql/{{ old_version }}/bin/pg_controldata -D /opt/data/postgresql/{{ old_version }}/main | grep 'Latest checkpoint location' | awk '{ print $4 }'
   17 |   args:
   18 |     executable: /bin/bash
   19 |   register: standby_checkpoint
   20 |   check_mode: no
   21 |   when: retry_count == 0 or not checkpoints_match
   22 | 
   23 | - name: Show primary and standby checkpoint locations
   24 |   debug: msg="Primary = {{ primary_checkpoint.stdout }}, Standby = {{ standby_checkpoint.stdout }}"
   25 |   when: retry_count == 0 or not checkpoints_match
   26 | 
   27 | - name: Record whether checkpoints match
   28 |   set_fact:
   29 |     checkpoints_match: "{{ primary_checkpoint.stdout == standby_checkpoint.stdout }}"
   30 |   when: retry_count == 0 or not checkpoints_match
   31 | 
   32 | - name: Wait before re-checking standby sync
   33 |   pause:
   34 |     seconds: 5
   35 |     prompt: "Primary and standby are out of sync. Waiting 5s before re-checking."
   36 |   when: not checkpoints_match and retry_count != 5
```

## Visible variable references

```text
f184ea5721b60efd0efce1cc96ce251bcf60df08:src/commcare_cloud/ansible/roles/postgresql_base/tasks/check_standby_in_sync.yml:11:  when: retry_count == 0 or not checkpoints_match
f184ea5721b60efd0efce1cc96ce251bcf60df08:src/commcare_cloud/ansible/roles/postgresql_base/tasks/check_standby_in_sync.yml:21:  when: retry_count == 0 or not checkpoints_match
f184ea5721b60efd0efce1cc96ce251bcf60df08:src/commcare_cloud/ansible/roles/postgresql_base/tasks/check_standby_in_sync.yml:25:  when: retry_count == 0 or not checkpoints_match
f184ea5721b60efd0efce1cc96ce251bcf60df08:src/commcare_cloud/ansible/roles/postgresql_base/tasks/check_standby_in_sync.yml:29:    checkpoints_match: "{{ primary_checkpoint.stdout == standby_checkpoint.stdout }}"
f184ea5721b60efd0efce1cc96ce251bcf60df08:src/commcare_cloud/ansible/roles/postgresql_base/tasks/check_standby_in_sync.yml:30:  when: retry_count == 0 or not checkpoints_match
f184ea5721b60efd0efce1cc96ce251bcf60df08:src/commcare_cloud/ansible/roles/postgresql_base/tasks/check_standby_in_sync.yml:36:  when: not checkpoints_match and retry_count != 5
```

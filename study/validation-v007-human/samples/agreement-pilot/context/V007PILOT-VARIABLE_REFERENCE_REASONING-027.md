# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-027

- Repository: `UtrechtUniversity/yoda`
- Commit: `a9175010319fee30fb056665e9821937f0ec07c5`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/postgresql_repository/tasks/main.yml` (reported anchor line 4)
- Object: `variable` `f07935ba8d0f158c54407aeb6fccca3075922a4511d9fec91a17e8098cd45e28`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–11 of 11:

```text
    1 | ---
    2 | # copyright Utrecht University
    3 | 
    4 | - name: Run postgresql_repository tasks if role has not run yet
    5 |   ansible.builtin.include_tasks: main-tasks.yml
    6 |   when: '"yoda_postgresql_repository_role_has_run" not in hostvars[inventory_hostname]'
    7 | 
    8 | - name: Register that postgresql_repository role has run
    9 |   ansible.builtin.set_fact:
   10 |     yoda_postgresql_repository_role_has_run: true
   11 |   when: '"yoda_postgresql_repository_role_has_run" not in hostvars[inventory_hostname]'
```

## Visible variable references

```text
a9175010319fee30fb056665e9821937f0ec07c5:roles/postgresql_repository/tasks/main.yml:6:  when: '"yoda_postgresql_repository_role_has_run" not in hostvars[inventory_hostname]'
a9175010319fee30fb056665e9821937f0ec07c5:roles/postgresql_repository/tasks/main.yml:10:    yoda_postgresql_repository_role_has_run: true
a9175010319fee30fb056665e9821937f0ec07c5:roles/postgresql_repository/tasks/main.yml:11:  when: '"yoda_postgresql_repository_role_has_run" not in hostvars[inventory_hostname]'
```

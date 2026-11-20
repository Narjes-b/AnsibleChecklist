# Frozen source context: V007PILOT2-SECURITY-020

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `src/commcare_cloud/ansible/perform_system_checks.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`src/commcare_cloud/ansible/perform_system_checks.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–39 of 39:

```text
    1 | - hosts: django_manage
    2 | 
    3 |   # uncomment these and comment the "become" lines below for local debugging
    4 |   #connection: local
    5 |   #vars:
    6 |   #  code_home: '{{ "~/code/commcare-hq" | expanduser}}'
    7 |   #  virtualenv_home: ../virtualenvs/hq
    8 | 
    9 |   become: true
   10 |   become_user: cchq
   11 |   gather_facts: no
   12 |   tasks:
   13 |   - command:
   14 |       cmd: ./manage.py check --deploy
   15 |       chdir: '{{ code_home }}'
   16 |     register: deploy_check
   17 |     failed_when: false
   18 |     changed_when: deploy_check.rc
   19 |   - name: "display output: manage.py check --deploy"
   20 |     debug: var=deploy_check.stdout_lines
   21 |     when: deploy_check.stdout_lines
   22 |   - name: "display errors: manage.py check --deploy"
   23 |     debug: var=deploy_check.stderr_lines
   24 |     when: deploy_check.rc or deploy_check.stderr_lines
   25 |     failed_when: deploy_check.rc
   26 | 
   27 |   - command:
   28 |       cmd: ./manage.py check --deploy -t database
   29 |       chdir: '{{ code_home }}'
   30 |     register: database_check
   31 |     failed_when: false
   32 |     changed_when: database_check.rc
   33 |   - name: "display output: manage.py check --deploy -t database"
   34 |     debug: var=database_check.stdout_lines
   35 |     when: database_check.stdout_lines
   36 |   - name: "display errors: manage.py check --deploy -t database"
   37 |     debug: var=database_check.stderr_lines
   38 |     when: database_check.rc or database_check.stderr_lines
   39 |     failed_when: database_check.rc
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-017

- Repository: `Linuxfabrik/lfops`
- Commit: `9b51b59db61b87e01cc75adef892e5345a5bf4b1`
- Family: Maintainability/complexity
- Rule: `ansibleguard/high-coupling`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/clamav.yml` (reported anchor line 1)
- Object: `source_location` `1ff392dbc33ebd3f5af3f762d4fb2cfeed2a911ccebbb97a0a107026637021ef`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–68 of 68:

```text
    1 | - name: 'Playbook linuxfabrik.lfops.clamav'
    2 |   hosts:
    3 |     - 'lfops_clamav'
    4 | 
    5 |   pre_tasks:
    6 |     - ansible.builtin.import_role:
    7 |         name: 'shared'
    8 |         tasks_from: 'log-start.yml'
    9 |       tags:
   10 |         - 'always'
   11 | 
   12 |     - ansible.builtin.import_role:
   13 |         name: 'shared'
   14 |         tasks_from: 'global-variables.yml'
   15 |       tags:
   16 |         - 'always'
   17 | 
   18 | 
   19 |   roles:
   20 | 
   21 |     # On Rocky 9+, CRB (now in the Rocky default repo file, formerly in EPEL) must be
   22 |     # enabled so python3-virtualenv can be installed.
   23 |     - role: 'linuxfabrik.lfops.repo_baseos'
   24 |       repo_baseos__crb_repo_enabled__dependent_var: '{{
   25 |           repo_epel__repo_baseos__crb_repo_enabled__dependent_var
   26 |         }}'
   27 |       when:
   28 |         - 'ansible_facts["distribution"] == "Rocky" and ansible_facts["distribution_major_version"] | int >= 9'
   29 |         - 'not clamav__skip_repo_baseos | d(false)'
   30 | 
   31 |     - role: 'linuxfabrik.lfops.repo_epel'
   32 |       when:
   33 |         - 'ansible_facts["os_family"] == "RedHat" and ansible_facts["distribution"] != "Fedora"'
   34 |         - 'not clamav__skip_repo_epel | d(false)'
   35 | 
   36 |     - role: 'linuxfabrik.lfops.policycoreutils'
   37 |       when:
   38 |         - 'ansible_facts["os_family"] == "RedHat"'
   39 |         - 'not clamav__skip_policycoreutils | d(false)'
   40 | 
   41 |     - role: 'linuxfabrik.lfops.selinux'
   42 |       selinux__booleans__dependent_var: '{{
   43 |           clamav__selinux__booleans__dependent_var
   44 |         }}'
   45 |       when:
   46 |         - 'ansible_facts["os_family"] == "RedHat"'
   47 |         - 'not clamav__skip_selinux | d(false)'
   48 | 
   49 |     - role: 'linuxfabrik.lfops.python_venv'
   50 |       python_venv__venvs__dependent_var: '{{
   51 |           fangfrisch__python_venv__venvs__dependent_var
   52 |         }}'
   53 |       when:
   54 |         - 'not clamav__skip_python_venv | d(false)'
   55 | 
   56 |     - role: 'linuxfabrik.lfops.clamav'
   57 | 
   58 |     - role: 'linuxfabrik.lfops.fangfrisch'
   59 |       when:
   60 |         - 'not clamav__skip_fangfrisch | d(false)'
   61 | 
   62 | 
   63 |   post_tasks:
   64 |     - ansible.builtin.import_role:
   65 |         name: 'shared'
   66 |         tasks_from: 'log-end.yml'
   67 |       tags:
   68 |         - 'always'
```

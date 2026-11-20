# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-008

- Repository: `redhat-cop/infra.aap_configuration`
- Commit: `f84d6a61e4b18aa135d707fe539371587bc92931`
- Family: Objective correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/controller_instances/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `297b75e3ffd00e8bea52009cb2724466361475f79819076520848669c7b91fb4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–46 of 46:

```text
    1 | ---
    2 | galaxy_info:
    3 |   role_name: instances
    4 |   author: Sean Sullivan
    5 |   description: An Ansible Role to create instances in Ansible Controller.
    6 |   company: Red Hat
    7 | 
    8 |   # If the issue tracker for your role is not on github, uncomment the
    9 |   # next line and provide a value
   10 |   # issue_tracker_url: http://example.com/issue/tracker
   11 |   license: GPL-3.0-or-later
   12 | 
   13 |   min_ansible_version: 2.16.0
   14 | 
   15 |   # Optionally specify the branch Galaxy will use when accessing the GitHub
   16 |   # repo for this role. During role install, if no tags are available,
   17 |   # Galaxy will use this branch. During import Galaxy will access files on
   18 |   # this branch. If Travis integration is configured, only notifications for this
   19 |   # branch will be accepted. Otherwise, in all cases, the repo's default branch
   20 |   # (usually master) will be used.
   21 | 
   22 |   # github_branch:
   23 | 
   24 |   #
   25 |   # platforms is a list of platforms, and each platform has a name and a list of versions.
   26 |   #
   27 |   platforms:
   28 |     - name: EL
   29 |       versions:
   30 |         - all
   31 | 
   32 |   galaxy_tags:
   33 |     - controller
   34 |     - aap
   35 |     - awx
   36 |     - instance
   37 |     - instances
   38 | 
   39 | collections:
   40 |   - ansible.controller
   41 | 
   42 | dependencies:
   43 |   # List your role dependencies here, one per line. Be sure to remove the '[]' above,
   44 |   # if you add dependencies to this list.
   45 |   - role: meta_dependency_check
   46 | ...
```

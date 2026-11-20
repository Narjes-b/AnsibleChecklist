# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-021

- Repository: `redhat-cop/infra.aap_configuration`
- Commit: `f84d6a61e4b18aa135d707fe539371587bc92931`
- Family: objective_correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/controller_job_templates/meta/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/controller_job_templates/meta/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–46 of 46:

```text
    1 | ---
    2 | galaxy_info:
    3 |   role_name: job_templates
    4 |   author: Sean Sulivan
    5 |   description: An Ansible Role to create Job Templates in Ansible Controller.
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
   21 |   # github_branch:
   22 | 
   23 |   #
   24 |   # platforms is a list of platforms, and each platform has a name and a list of versions.
   25 |   #
   26 |   platforms:
   27 |     - name: EL
   28 |       versions:
   29 |         - all
   30 | 
   31 |   galaxy_tags:
   32 |     - controller
   33 |     - aap
   34 |     - awx
   35 |     - configuration
   36 |     - jobtemplates
   37 | 
   38 | collections:
   39 |   - ansible.controller
   40 | 
   41 | dependencies:
   42 |   # List your role dependencies here, one per line. Be sure to remove the '[]' above,
   43 |   # if you add dependencies to this list.
   44 |   - role: global_vars
   45 |   - role: meta_dependency_check
   46 | ...
```

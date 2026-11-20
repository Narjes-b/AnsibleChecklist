# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-042

- Repository: `redhat-cop/aap_configuration_extended`
- Commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Family: Objective correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/object_diff/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `ab726333076e85a1ca94a5bac1e27b8a73f30f30f49210bdab68edc64090543a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–48 of 48:

```text
    1 | ---
    2 | galaxy_info:
    3 |   author: Automation Iberia
    4 |   description: AAP Configuration as Code - Desidered State
    5 |   company: Automation Iberia
    6 | 
    7 |   # If the issue tracker for your role is not on github, uncomment the
    8 |   # next line and provide a value
    9 |   # issue_tracker_url: http://example.com/issue/tracker
   10 | 
   11 |   # Choose a valid license ID from https://spdx.org - some suggested licenses:
   12 |   # - BSD-3-Clause (default)
   13 |   # - MIT
   14 |   # - GPL-2.0-or-later
   15 |   # - GPL-3.0-only
   16 |   # - Apache-2.0
   17 |   # - CC-BY-4.0
   18 |   license: GPL-3.0-or-later
   19 | 
   20 |   min_ansible_version: 2.15.0
   21 | 
   22 |   # If this a Container Enabled role, provide the minimum Ansible Container version.
   23 |   # min_ansible_container_version:
   24 | 
   25 |   #
   26 |   # Provide a list of supported platforms, and for each platform a list of versions.
   27 |   # If you don't wish to enumerate all versions for a particular platform, use 'all'.
   28 |   # To view available platforms and versions (or releases), visit:
   29 |   # https://galaxy.ansible.com/api/v1/platforms/
   30 |   #
   31 |   platforms:
   32 |     - name: "EL"
   33 |       versions:
   34 |         - "all"
   35 | 
   36 |   galaxy_tags: []
   37 |   # List tags for your role here, one per line. A tag is a keyword that describes
   38 |   # and categorizes the role. Users find roles by searching for tags. Be sure to
   39 |   # remove the '[]' above, if you add tags to this list.
   40 |   #
   41 |   # NOTE: A tag is limited to a single word comprised of alphanumeric characters.
   42 |   #       Maximum 20 tags per role.
   43 | 
   44 | dependencies:
   45 |   # List your role dependencies here, one per line. Be sure to remove the '[]' above,
   46 |   # if you add dependencies to this list.
   47 |   - role: infra.aap_configuration.meta_dependency_check
   48 | ...
```

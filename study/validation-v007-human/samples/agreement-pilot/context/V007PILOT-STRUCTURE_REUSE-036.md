# Frozen source context: V007PILOT-STRUCTURE_REUSE-036

- Repository: `wonderbird/ansible-all-my-things`
- Commit: `4993019d9dfb175eef6cb40fce4ea56138e6a374`
- Family: Structure/reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/windows_common/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `0c62c02d4b9ff396bbd55f9f5248848fca563f3f1523cb2962479e1c239d3869`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–19 of 19:

```text
    1 | #SPDX-License-Identifier: MIT-0
    2 | galaxy_info:
    3 |   author: Stefan Boos
    4 |   description: Basic Windows configuration, e.g. reboot if pending
    5 |   company: n.a.
    6 |   issue_tracker_url: http://github.com/wonderbird/ansible-all-my-things/issues
    7 |   license: MIT
    8 |   min_ansible_version: 2.1
    9 |   galaxy_tags: []
   10 |     # List tags for your role here, one per line. A tag is a keyword that describes
   11 |     # and categorizes the role. Users find roles by searching for tags. Be sure to
   12 |     # remove the '[]' above, if you add tags to this list.
   13 |     #
   14 |     # NOTE: A tag is limited to a single word comprised of alphanumeric characters.
   15 |     #       Maximum 20 tags per role.
   16 | 
   17 | dependencies: []
   18 |   # List your role dependencies here, one per line. Be sure to remove the '[]' above,
   19 |   # if you add dependencies to this list.
```

## Frozen tracked paths in the relevant role/scope

```text
roles/windows_common/README.md
roles/windows_common/meta/main.yml
roles/windows_common/tasks/reboot-if-pending.yml
```

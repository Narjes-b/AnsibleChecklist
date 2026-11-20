# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-016

- Repository: `ansible/galaxy-operator`
- Commit: `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc`
- Family: Objective correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/galaxy-route/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `a45ccc0b8ab97a79470baae1177982a08e62e5f0c3f1577b560fddada82e8356`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–17 of 17:

```text
    1 | ---
    2 | galaxy_info:
    3 |   author: Galaxy-Operator Team
    4 |   description: A role to setup Galaxy routes service
    5 |   issue_tracker_url: https://github.com/ansible/galaxy-operator/issues/new
    6 |   license: GPL-2.0-or-later
    7 |   company: Red Hat
    8 |   galaxy_tags:
    9 |     - galaxy
   10 |     - pulp
   11 |     - pulpcore
   12 | dependencies: []
   13 |   # List your role dependencies here, one per line. Be sure to remove the '[]' above,
   14 |   # if you add dependencies to this list.
   15 | collections:
   16 | - operator_sdk.util
   17 | - kubernetes.core
```

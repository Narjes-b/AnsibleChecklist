# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-010

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: maintainability_complexity
- Rule: `ansibleguard/shell-instead-of-module`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `roles/pulmirror/handlers/main.yml` (reported anchor line 4)
- Flagged construct: task `reload nginx`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–6 of 6:

```text
    1 | #SPDX-License-Identifier: MIT-0
    2 | ---
    3 | # handlers file for roles/pulmirror
    4 | - name: reload nginx
    5 |   ansible.builtin.command: service nginx reload
    6 |   changed_when: true
```

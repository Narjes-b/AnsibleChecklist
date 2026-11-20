# Frozen source context: V007PILOT-STYLE_POLICY-008

- Repository: `osism/ansible-collection-services`
- Commit: `131734f2c007d0009a7fc218849f4ede66c7c899`
- Family: Style/policy
- Rule: `ansibleguard/molecule-test-absent`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/dnsdist/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `e7ecbb32dea55cc139b375e42f2b83f594bc1d5c1ce4137f7ce84c7716ca7b04`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–8 of 8:

```text
    1 | ---
    2 | - name: Include config tasks
    3 |   ansible.builtin.include_tasks: config.yml
    4 |   tags: config
    5 | 
    6 | - name: Include service tasks
    7 |   ansible.builtin.include_tasks: service.yml
    8 |   tags: service
```

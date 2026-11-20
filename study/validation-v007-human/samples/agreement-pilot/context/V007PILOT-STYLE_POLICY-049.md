# Frozen source context: V007PILOT-STYLE_POLICY-049

- Repository: `michnmi/ansible_internal`
- Commit: `25f44a7ad44d44b7b91837256958ff443ba28a1e`
- Family: Style/policy
- Rule: `ansibleguard/molecule-test-absent`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/services/kavita/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `58ebb27ada12c5723789ce7e16efe580cb7ccba1c88c22c28e7e1daa10006896`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–5 of 5:

```text
    1 | ---
    2 | - name: 'Main: Prepare host'
    3 |   ansible.builtin.import_tasks: 'pre-setup.yml'
    4 | - name: 'Main: Setup Kavita as a service'
    5 |   ansible.builtin.import_tasks: 'setup-kavita.yml'
```

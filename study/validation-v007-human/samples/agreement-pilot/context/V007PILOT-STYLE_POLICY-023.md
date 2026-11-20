# Frozen source context: V007PILOT-STYLE_POLICY-023

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: Style/policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/ocp_logging/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `7a70efc5b0e936338dcde3198043083121655a65a9e49faf951c05dae88d3035`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–21 of 21:

```text
    1 | ---
    2 | - name: "Install the cluster Logging stack"
    3 |   when:
    4 |     - ol_action == 'install'
    5 |   block:
    6 |     - name: "Pre-run validations"
    7 |       ansible.builtin.include_tasks: pre-run.yml
    8 | 
    9 |     - name: "Set up the cluster logging subsystem"
   10 |       ansible.builtin.include_tasks: setup-logging.yml
   11 | 
   12 |     - name: "Validate_ cluster logging subsystem"
   13 |       ansible.builtin.include_tasks: validate-stack.yml
   14 | 
   15 | - name: "Cleanup Logging stack resources"
   16 |   when:
   17 |     - ol_action == 'cleanup'
   18 |   block:
   19 |     - name: "Cleanup Logging stack resources"
   20 |       ansible.builtin.include_tasks: clean-resources.yml
   21 | ...
```

# Frozen source context: V007PILOT-STYLE_POLICY-035

- Repository: `freeipa/ansible-freeipa`
- Commit: `5ba9b59d5b614abdb0af70fc9f2d336e5479e833`
- Family: Style/policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `playbooks/hostgroup/rename-hostgroup.yml` (reported anchor line 7)
- Object: `task` `9c703ae97b6af009b0ea0086eac372750f25daa17fc8e26ed1145aff6f990aa5`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–12 of 12:

```text
    1 | ---
    2 | - name: Playbook to handle hostgroups
    3 |   hosts: ipaserver
    4 |   become: yes
    5 | 
    6 |   tasks:
    7 |   - name: Rename host-group from `databases` to `datalake`
    8 |     ipahostgroup:
    9 |       ipaadmin_password: [REDACTED_LITERAL]
   10 |       name: databases
   11 |       rename: datalake
   12 |       state: renamed
```

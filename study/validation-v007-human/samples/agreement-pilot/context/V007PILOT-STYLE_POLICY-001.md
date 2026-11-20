# Frozen source context: V007PILOT-STYLE_POLICY-001

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: Style/policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/nfs_verify/tasks/check.yml` (reported anchor line 1)
- Object: `source_location` `8ea6b680939dcab2ec37062fa005341eed985b84b0f1b6cbb935c73502bc4dc4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–14 of 14:

```text
    1 | ---
    2 | - name: postcheck | Check if NFS is running
    3 |   shell:
    4 |    cmd: "{{ scale_command_path }}mmces service list|grep NFS"
    5 |   register: scale_nfs_status
    6 |   when: inventory_hostname in scale_nfs_nodes_list
    7 |   failed_when: false
    8 | 
    9 | - name: postcheck | Check if NFS is running
   10 |   assert:
   11 |    that:
   12 |    - scale_nfs_status.rc == 0
   13 |    fail_msg: "NFS is not active on {{ ansible_hostname }}"
   14 |   when: inventory_hostname in scale_nfs_nodes_list
```

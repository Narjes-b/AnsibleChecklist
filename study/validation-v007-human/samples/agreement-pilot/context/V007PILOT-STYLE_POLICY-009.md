# Frozen source context: V007PILOT-STYLE_POLICY-009

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `onecloud/upgrade-cluster-final.yml` (reported anchor line 5)
- Object: `source_location` `3ea46bcb8312600f4f1f2b3b572644ca5970a8ed03f437178fe9309eec6c860b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–20 of 20:

```text
    1 | - hosts: all
    2 |   roles:
    3 |     - { role: utils/detect-os }
    4 | 
    5 | - hosts: primary_master_node
    6 |   roles:
    7 |     - { role: upgrade/primary_master_node }
    8 |     - { role: utils/k8s/addons }
    9 | 
   10 | - hosts: master_nodes
   11 |   roles:
   12 |     - { role: upgrade/master_nodes }
   13 | 
   14 | - hosts: worker_nodes
   15 |   roles:
   16 |     - { role: upgrade/worker_nodes }
   17 | 
   18 | - hosts: primary_master_node:master_nodes:worker_nodes
   19 |   roles:
   20 |     - { role: utils/gpu-init }
```

# Frozen source context: V007PILOT-STYLE_POLICY-041

- Repository: `ricsanfre/pi-cluster`
- Commit: `f55c4ba0659fd1409389f39026d91441bb0cf6d0`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-task`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `kubernetes/platform/grafana/instance/components/persistence/grafana-patch.yaml` (reported anchor line 37)
- Object: `source_location` `0e3d878393ddc19418376f3ad9258b38d875448760d275813198cc9a830895a0`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–40 of 40:

```text
    1 | - op: add
    2 |   path: /spec/persistentVolumeClaim
    3 |   value:
    4 |     spec:
    5 |       accessModes:
    6 |         - ReadWriteOnce
    7 |       storageClassName: ${STORAGE_CLASS:=longhorn}
    8 |       resources:
    9 |         requests:
   10 |           storage: 5Gi
   11 | - op: add
   12 |   path: /spec/deployment/spec/template/spec/securityContext
   13 |   value:
   14 |     runAsNonRoot: true
   15 |     runAsUser: 1000
   16 |     runAsGroup: 1000
   17 |     fsGroup: 1000
   18 |     fsGroupChangePolicy: OnRootMismatch
   19 | - op: add
   20 |   path: /spec/deployment/spec/template/spec/containers/0/securityContext
   21 |   value:
   22 |     allowPrivilegeEscalation: false
   23 |     readOnlyRootFilesystem: true
   24 |     capabilities:
   25 |       drop:
   26 |         - ALL
   27 | - op: add
   28 |   path: /spec/deployment/spec/template/spec/containers/0/readinessProbe
   29 |   value:
   30 |     failureThreshold: 3
   31 | - op: add
   32 |   path: /spec/deployment/spec/template/spec/volumes
   33 |   value:
   34 |     - name: grafana-data
   35 |       persistentVolumeClaim:
   36 |         claimName: grafana-pvc
   37 | - op: add
   38 |   path: /spec/deployment/spec/strategy
   39 |   value:
   40 |     type: Recreate
```

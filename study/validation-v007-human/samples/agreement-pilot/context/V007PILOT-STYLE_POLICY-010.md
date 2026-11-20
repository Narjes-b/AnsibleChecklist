# Frozen source context: V007PILOT-STYLE_POLICY-010

- Repository: `kubevirt/project-infra`
- Commit: `2b204a6ee9bcf983613baf20f122fe2272dbcf3e`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-task`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `github/ci/prow-deploy/kustom/components/docker-mirror-proxy/pv/patches/JsonRFC6902/deployment.yaml` (reported anchor line 14)
- Object: `source_location` `79e1d4372433e8980fa89b8116207265941666e8a25493d0862c776ef6128acc`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–18 of 18:

```text
    1 | ---
    2 | # sets up dynamic provisioned PV
    3 | - op: add
    4 |   path: /spec/template/spec/containers/0/volumeMounts/0
    5 |   value:
    6 |     name: storage
    7 |     mountPath: /docker_mirror_cache
    8 | - op: add
    9 |   path: /spec/template/spec/volumes/0
   10 |   value:
   11 |     name: storage
   12 |     persistentVolumeClaim:
   13 |       claimName: docker-mirror-proxy
   14 | - op: add
   15 |   path: /spec/template/spec/securityContext
   16 |   value:
   17 |       runAsUser: 0
   18 |       runAsGroup: 0
```

# Frozen source context: V007PILOT-SECURITY-017

- Repository: `kubevirt/project-infra`
- Commit: `2b204a6ee9bcf983613baf20f122fe2272dbcf3e`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `github/ci/prow-deploy/vars/kubevirtci-testing/kubevirtci-testing.yml` (reported anchor line 14)
- Object: `source_location` `b4c92c5f517a890177ce0adb906bbd0c14644208a0365cad0dd9c6faee536958`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–14 of 14:

```text
    1 | # Test provisioning
    2 | prowUrl: prow.prowdeploy.ci
    3 | 
    4 | testinfra_dir: /tmp/test-infra
    5 | 
    6 | secrets_dir: '{{ project_infra_root }}/github/ci/prow-deploy/kustom/overlays/kubevirtci-testing/secrets/'
    7 | components_dir: '{{ project_infra_root }}/github/ci/prow-deploy/kustom/components'
    8 | 
    9 | node_name: node01
   10 | 
   11 | ansible_python_interpreter: /usr/bin/python3
   12 | 
   13 | githubUnprivileged:
   14 |   token: "test"
```

# Frozen source context: V007PILOT2-SECURITY-006

- Repository: `kubevirt/project-infra`
- Commit: `2b204a6ee9bcf983613baf20f122fe2272dbcf3e`
- Family: security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `github/ci/prow-deploy/vars/kubevirtci-testing/secrets.yml` (reported anchor line 20)
- Flagged construct: variable `coverallsToken`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–36 of 36:

```text
    1 | # variables that come from secrets
    2 | githubCommenterToken: [REDACTED_LITERAL]
    3 | githubBotreviewToken: [REDACTED_LITERAL]
    4 | 
    5 | gcswebUrl: gcsweb.prowdeploy.ci
    6 | 
    7 | virtciGCSServiceAccount: |
    8 |   {
    9 |     "type": "service_account"
   10 |   }
   11 | 
   12 | prowNamespace: kubevirt-prow
   13 | prowJobsNamespace: kubevirt-prow-jobs
   14 | 
   15 | prowAdmins: ["admin1@example.com", "admin2@example.com"]
   16 | 
   17 | masterClusterContext: kubernetes-admin@kubernetes
   18 | 
   19 | installerPullToken: [REDACTED_LITERAL]
   20 | 
   21 | coverallsToken: [REDACTED_LITERAL]
   22 | containerizedDataImporterCoverallsToken: [REDACTED_LITERAL]
   23 | 
   24 | bootstrap_full_config: true
   25 | rescale_pushgateway_deployment: true
   26 | rescale_deck_deployment: true
   27 | delete_priority_classes: false
   28 | 
   29 | kubeconfig_path: /root/.kube/config
   30 | 
   31 | windowsProductKeys:
   32 |   sysprep-001: "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE"
   33 | 
   34 | fossaToken: [REDACTED_LITERAL]
   35 | 
   36 | prowKubevirtbotSSHPrivateKey: [REDACTED_LITERAL]
```

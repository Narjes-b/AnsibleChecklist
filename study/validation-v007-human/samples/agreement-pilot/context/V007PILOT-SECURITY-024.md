# Frozen source context: V007PILOT-SECURITY-024

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `ansible/roles/install_launcher/defaults/main.yml` (reported anchor line 14)
- Object: `source_location` `a31729bd4355119c5e38170c68be35623e17daf6210b66a8bacc8e0b1b68f384`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–26 of 26:

```text
    1 | launcher_project_name: devex
    2 | 
    3 | # Please provide your username/token as openshift parameter
    4 | launcher_github_username:
    5 | launcher_github_token:[REDACTED VALUE BLOCK]
    6 | 
    7 | # For local usage, you can use this address : http://launcher-keycloak:8080/auth
    8 | launcher_keycloak_url:
    9 | # For local usage, you can use this realm : launch
   10 | launcher_keycloak_realm:
   11 | 
   12 | # Check these values as they could be different for your cluster
   13 | launcher_openshift_user: admin
   14 | launcher_openshift_pwd: admin
   15 | 
   16 | launcher_template_version: master
   17 | launcher_template_name: fabric8-launcher
   18 | launcher_template_url: https://raw.githubusercontent.com/fabric8-launcher/launcher-openshift-templates/{{ launcher_template_version }}/openshift/launcher-template.yaml
   19 | 
   20 | launcher_catalog_git_repo: https://github.com/fabric8-launcher/launcher-booster-catalog.git
   21 | launcher_catalog_git_branch: master
   22 | 
   23 | launcher_openshift_console_url:
   24 | launcher_openshift_api_url: https://openshift.default.svc.cluster.local
   25 | 
   26 | launcher_catalog_filter:
```

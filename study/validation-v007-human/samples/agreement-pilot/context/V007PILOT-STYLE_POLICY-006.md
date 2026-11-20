# Frozen source context: V007PILOT-STYLE_POLICY-006

- Repository: `azimuth-cloud/ansible-collection-azimuth-ops`
- Commit: `396972118edcecb213e69497f9f2c70e7abd0611`
- Family: Style/policy
- Rule: `ansibleguard/missing-file-extension`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `playbooks/provision.yml` (reported anchor line 1)
- Object: `source_location` `23527d2b402e7118f61e314206012e6bdc9e85c48d83feafa65eac208e1449b9`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–20 of 20:

```text
    1 | ---
    2 | #####
    3 | # This playbook uses Terraform and Cluster API to provision infrastructure onto which Azimuth is deployed
    4 | #####
    5 | # Provision the Kubernetes cluster onto which Azimuth will be deployed
    6 | - name: Provision Kubernetes cluster for Azimuth
    7 |   import_playbook: azimuth_cloud.azimuth_ops.provision_cluster
    8 | 
    9 | # Install Azimuth
   10 | - name: Install and configure Azimuth
   11 |   import_playbook: azimuth_cloud.azimuth_ops.deploy
   12 |   vars:
   13 |     # In HA mode, use the kubeconfig for the HA cluster
   14 |     # In single node mode, use the default kubeconfig file
   15 |     kubeconfig_path: >-
   16 |       {{-
   17 |         "{}/kubeconfig-{}.yaml".format(ansible_env.HOME, capi_cluster_release_name)
   18 |         if install_mode == 'ha'
   19 |         else ""
   20 |       }}
```

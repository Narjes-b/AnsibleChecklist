# Frozen source context: V007PILOT2-STRUCTURE_REUSE-009

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: structure_reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/argocd_config/defaults/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/argocd_config/defaults/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–42 of 42:

```text
    1 | ---
    2 | ac_server_api: https://kubernetes.default.svc
    3 | ac_namespace: openshift-gitops
    4 | ac_app_dir_recurse: false
    5 | ac_hide_secrets: [REDACTED_LITERAL]
    6 | ac_cluster_role: "openshift-gitops-{{ ac_namespace }}-argocd-application-controller"
    7 | ac_permissions_def:
    8 |   apiVersion: rbac.authorization.k8s.io/v1
    9 |   kind: ClusterRoleBinding
   10 |   metadata:
   11 |     name: gitops-cluster
   12 |   roleRef:
   13 |     apiGroup: rbac.authorization.k8s.io
   14 |     kind: ClusterRole
   15 |     name: "{{ ac_cluster_role }}"
   16 |   subjects:
   17 |     - kind: ServiceAccount
   18 |       name: openshift-gitops-argocd-application-controller
   19 |       namespace: "{{ ac_namespace }}"
   20 | ac_project: project
   21 | ac_project_def:
   22 |   apiVersion: argoproj.io/v1alpha1
   23 |   kind: AppProject
   24 |   metadata:
   25 |     name: "{{ ac_project }}"
   26 |     namespace: "{{ ac_namespace }}"
   27 |   spec:
   28 |     clusterResourceWhitelist:
   29 |       - group: ''
   30 |         kind: Namespace
   31 |     namespaceResourceWhitelist:
   32 |       - group: '*'
   33 |         kind: '*'
   34 |     destinations:
   35 |       - namespace: "{{ ac_app_namespace }}"
   36 |         server: "{{ ac_server_api }}"
   37 |     sourceRepos:
   38 |       - "{{ ac_repo }}"
   39 | ac_repo_revision: main
   40 | ac_ssh_port: 22
   41 | ac_wait_retries: 30
   42 | ac_wait_delay: 10
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/argocd_config`; 11 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

roles/argocd_config/README.md
roles/argocd_config/defaults/main.yml
roles/argocd_config/meta/argument_specs.yml
roles/argocd_config/tasks/config-app-create.yml
roles/argocd_config/tasks/config-app-delete.yml
roles/argocd_config/tasks/config-app-sync.yml
roles/argocd_config/tasks/config-app.yml
roles/argocd_config/tasks/config-permissions.yml
roles/argocd_config/tasks/config-project.yml
roles/argocd_config/tasks/config-repo.yml
roles/argocd_config/tasks/wait-for-healthy.yml
```

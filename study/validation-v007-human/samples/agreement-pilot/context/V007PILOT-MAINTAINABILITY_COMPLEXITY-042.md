# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-042

- Repository: `azimuth-cloud/ansible-collection-azimuth-ops`
- Commit: `396972118edcecb213e69497f9f2c70e7abd0611`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/capi_cluster/tasks/capi-cluster-service-account.yml` (reported anchor line 1)
- Object: `source_location` `58e30a394939d9aa348941df9cc2ac87220324f3159a050ce316141247265220`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–124 of 124:

```text
    1 | - name: Create namespace for a new service account
    2 |   ansible.builtin.command: kubectl create namespace {{ capi_cluster_service_account_namespace }}
    3 |   register: magnum_create_namespace
    4 |   changed_when: magnum_create_namespace.rc == 0
    5 |   failed_when: >-
    6 |     magnum_create_namespace.rc != 0 and
    7 |     'AlreadyExists' not in magnum_create_namespace.stderr
    8 | 
    9 | - name: Delete service account
   10 |   ansible.builtin.command: >-
   11 |     kubectl delete serviceaccount
   12 |     -n {{ capi_cluster_service_account_namespace }}
   13 |     {{ capi_cluster_service_account_name }}
   14 |   register: magnum_delete_service_account
   15 |   changed_when: magnum_delete_service_account.rc == 0
   16 |   failed_when: >-
   17 |     magnum_delete_service_account.rc != 0 and
   18 |     'NotFound' not in magnum_delete_service_account.stderr
   19 |   when: capi_cluster_service_account_rotate_secret
   20 | 
   21 | - name: Create service account
   22 |   ansible.builtin.command: kubectl apply -f -
   23 |   args:
   24 |     stdin: "{{ sa_definition | to_nice_yaml }}"
   25 |   vars:
   26 |     sa_definition:
   27 |       apiVersion: v1
   28 |       kind: ServiceAccount
   29 |       metadata:
   30 |         name: "{{ capi_cluster_service_account_name }}"
   31 |         namespace: "{{ capi_cluster_service_account_namespace }}"
   32 |   changed_when: false
   33 | 
   34 | - name: Create token secret for service account
   35 |   ansible.builtin.command: kubectl apply -f -
   36 |   args:
   37 |     stdin: "{{ sa_secret_definition | to_nice_yaml }}"
   38 |   vars:
   39 |     sa_secret_definition:[REDACTED VALUE BLOCK]
   40 |       [REDACTED ENCRYPTED VALUE]
   41 |       [REDACTED ENCRYPTED VALUE]
   42 |       [REDACTED ENCRYPTED VALUE]
   43 |       [REDACTED ENCRYPTED VALUE]
   44 |         [REDACTED ENCRYPTED VALUE]
   45 |         [REDACTED ENCRYPTED VALUE]
   46 |         [REDACTED ENCRYPTED VALUE]
   47 |           [REDACTED ENCRYPTED VALUE]
   48 |   register: token_based_secret_applied
   49 |   until: token_based_secret_applied is succeeded
   50 |   retries: 30
   51 |   delay: 10
   52 |   changed_when: false
   53 | 
   54 | # Grant cluster-admin permissions via ClusterRoleBinding to allow generation of all Helm releases.
   55 | # Strict access control isn’t enforced here, as the user can escalate privileges using ServiceAccounts, Roles, and RoleBindings anyway.
   56 | # which is necessary for the management cluster to operate on resources.
   57 | - name: Create cluster role binding of cluster-admin configuration for kubeconfig service account
   58 |   ansible.builtin.command: kubectl apply -f -
   59 |   args:
   60 |     stdin: "{{ sa_clusterrolebinding | to_nice_yaml }}"
   61 |   vars:
   62 |     sa_clusterrolebinding:
   63 |       apiVersion: rbac.authorization.k8s.io/v1
   64 |       kind: ClusterRoleBinding
   65 |       metadata:
   66 |         name: "{{ capi_cluster_clusterrolebinding_name }}"
   67 |       subjects:
   68 |         - kind: ServiceAccount
   69 |           name: "{{ capi_cluster_service_account_name }}"
   70 |           namespace: "{{ capi_cluster_service_account_namespace }}"
   71 |       roleRef:
   72 |         kind: ClusterRole
   73 |         name: "{{ capi_cluster_service_account_role_name }}"
   74 |         apiGroup: rbac.authorization.k8s.io
   75 |   changed_when: false
   76 | 
   77 | - name: Extract token for the service account
   78 |   no_log: true
   79 |   ansible.builtin.command: >-
   80 |     kubectl get secret
   81 |     -n {{ capi_cluster_service_account_namespace }}
   82 |     {{ capi_cluster_service_account_secret_name }}
   83 |     -o jsonpath='{.data.token}'
   84 |   register: sa_token_encoded
   85 |   changed_when: false
   86 | 
   87 | - name: Decode token for service account
   88 |   no_log: true
   89 |   ansible.builtin.set_fact:
   90 |     sa_token: "{{ sa_token_encoded.stdout | b64decode }}"
   91 | 
   92 | - name: Read saved kubeconfig file
   93 |   no_log: true
   94 |   ansible.builtin.slurp:
   95 |     src: "{{ capi_cluster_kubeconfig_path }}"
   96 |   register: kubeconfig_file_raw
   97 | 
   98 | - name: Decode kubeconfig content from base64
   99 |   no_log: true
  100 |   ansible.builtin.set_fact:
  101 |     kubeconfig_content: "{{ kubeconfig_file_raw.content | b64decode | from_yaml }}"
  102 | 
  103 | - name: Strip client cert/key and add token to create token-based kubeconfig
  104 |   no_log: true
  105 |   ansible.builtin.set_fact:
  106 |     modified_kubeconfig: >-
  107 |       {{
  108 |         kubeconfig_content | combine({
  109 |           "users": [
  110 |             {
  111 |               "name": kubeconfig_content.users[0].name,
  112 |               "user": {
  113 |                 "token": [REDACTED_LITERAL]
  114 |               }
  115 |             }
  116 |           ]
  117 |         }, recursive=True)
  118 |       }}
  119 | 
  120 | - name: Save token-based kubeconfig to capi cluster kubeconfig path
  121 |   ansible.builtin.copy:
  122 |     content: "{{ modified_kubeconfig | to_nice_yaml }}"
  123 |     dest: "{{ capi_cluster_kubeconfig_path }}"
  124 |     mode: '0600'
```

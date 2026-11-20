# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-004

- Repository: `theopenlab/openlab-zuul-jobs`
- Commit: `0d133dc0879296c0aacd0b70344515c94137a8ec`
- Family: objective_correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/install-cpo-occm/tasks/main.yml` (reported anchor line 114)
- Flagged construct: not named by the finding; the anchor line 114 lies in the task at line 114, name `Wait for openstack-cloud-controller-manager up and running`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–142 of 142:

```text
    1 | - name: Prepare openstack-cloud-controller-manager config
    2 |   shell:
    3 |     executable: /bin/bash
    4 |     cmd: |
    5 |       set -ex
    6 | 
    7 |       set +x; source {{ devstack_workdir }}/openrc admin admin > /dev/null; set -x
    8 |       tenant_id=$(openstack project show demo -c id -f value)
    9 |       sudnet_id=$(openstack subnet show private-subnet -c id -f value)
   10 |       external_network_id=$(openstack network list --external -c ID -f value)
   11 | 
   12 |       set +x; source {{ devstack_workdir }}/openrc demo demo > /dev/null; set -x
   13 |       cat <<EOF > {{ ansible_user_dir }}/cloud.conf
   14 |       [Global]
   15 |       auth-url=${OS_AUTH_URL}/v3
   16 |       username=${OS_USERNAME}
   17 |       password=${OS_PASSWORD}
   18 |       region=${OS_REGION_NAME}
   19 |       tenant-id=$tenant_id
   20 |       domain-id=default
   21 | 
   22 |       [LoadBalancer]
   23 |       use-octavia=true
   24 |       subnet-id=$sudnet_id
   25 |       floating-network-id=$external_network_id
   26 | 
   27 |       [BlockStorage]
   28 |       bs-version=v2
   29 |       EOF
   30 | 
   31 |       kubectl --kubeconfig {{ ansible_user_dir }}/.kube/config create secret -n kube-system generic cloud-config --from-file={{ ansible_user_dir }}/cloud.conf
   32 | 
   33 | - name: Create secret for pulling the image
   34 |   no_log: yes
   35 |   shell:
   36 |     executable: /bin/bash
   37 |     cmd: |
   38 |       kubectl -n kube-system get secret openlab || kubectl -n kube-system create secret docker-registry openlab --docker-server={{ swr_registry }} --docker-username=ap-southeast-3@{{ swr_ak }} --docker-password={{ swr_sk }}
   39 | 
   40 | - name: Deploy openstack-cloud-controller-manager
   41 |   shell:
   42 |     executable: /bin/bash
   43 |     cmd: |
   44 |       set -x
   45 | 
   46 |       cat <<EOF | kubectl apply -f -
   47 |       ---
   48 |       apiVersion: v1
   49 |       kind: ServiceAccount
   50 |       metadata:
   51 |         name: cloud-controller-manager
   52 |         namespace: kube-system
   53 |       ---
   54 |       apiVersion: rbac.authorization.k8s.io/v1
   55 |       kind: ClusterRoleBinding
   56 |       metadata:
   57 |         name: system:cloud-controller-manager
   58 |       roleRef:
   59 |         apiGroup: rbac.authorization.k8s.io
   60 |         kind: ClusterRole
   61 |         name: cluster-admin
   62 |       subjects:
   63 |       - kind: ServiceAccount
   64 |         name: cloud-controller-manager
   65 |         namespace: kube-system
   66 |       ---
   67 |       apiVersion: apps/v1
   68 |       kind: Deployment
   69 |       metadata:
   70 |         name: openstack-cloud-controller-manager
   71 |         namespace: kube-system
   72 |         labels:
   73 |           k8s-app: openstack-cloud-controller-manager
   74 |       spec:
   75 |         replicas: 1
   76 |         selector:
   77 |           matchLabels:
   78 |             k8s-app: openstack-cloud-controller-manager
   79 |         template:
   80 |           metadata:
   81 |             labels:
   82 |               k8s-app: openstack-cloud-controller-manager
   83 |           spec:
   84 |             tolerations:
   85 |             - key: node.cloudprovider.kubernetes.io/uninitialized
   86 |               value: "true"
   87 |               effect: NoSchedule
   88 |             - key: node-role.kubernetes.io/master
   89 |               effect: NoSchedule
   90 |             serviceAccountName: cloud-controller-manager
   91 |             imagePullSecrets:[REDACTED VALUE BLOCK]
   92 |             - name: openlab
   93 |             containers:
   94 |               - name: openstack-cloud-controller-manager
   95 |                 image: {{ swr_registry }}/{{ swr_account }}/openstack-cloud-controller-manager-amd64:{{ occm_image_tag }}
   96 |                 args:
   97 |                   - /bin/openstack-cloud-controller-manager
   98 |                   - --v=4
   99 |                   - --cloud-config=/etc/config/cloud.conf
  100 |                   - --cloud-provider=openstack
  101 |                   - --use-service-account-credentials=[REDACTED_LITERAL]
  102 |                   - --bind-address=127.0.0.1
  103 |                 volumeMounts:
  104 |                   - mountPath: /etc/config
  105 |                     name: cloud-config-volume
  106 |                     readOnly: true
  107 |             hostNetwork: true
  108 |             volumes:
  109 |             - name: cloud-config-volume
  110 |               secret:[REDACTED VALUE BLOCK]
  111 |                 [REDACTED ENCRYPTED VALUE]
  112 |       EOF
  113 | 
  114 | - name: Wait for openstack-cloud-controller-manager up and running
  115 |   shell:
  116 |     executable: /bin/bash
  117 |     cmd: |
  118 |       kubectl -n kube-system get pod | grep openstack-cloud-controller-manager | grep Running
  119 |   register: check_occm
  120 |   until: check_occm.rc == 0
  121 |   retries: 24
  122 |   delay: 5
  123 |   ignore_errors: yes
  124 | 
  125 | - name: Gather additional evidence if openstack-cloud-controller-manager failed to come up
  126 |   when: check_occm.failed
  127 |   block:
  128 |     - name: Describe failed openstack-cloud-controller-manager
  129 |       shell:
  130 |         executable: /bin/bash
  131 |         cmd: |
  132 |           kubectl -n kube-system describe daemonset openstack-cloud-controller-manager
  133 |       register: describe_occm
  134 |       changed_when: false
  135 | 
  136 |     - name: Log failed openstack-cloud-controller-manager daemonset
  137 |       debug:
  138 |         var: describe_occm.stdout_lines
  139 | 
  140 |     - name: &failmsg Stop due to prior failure of openstack-cloud-controller-manager
  141 |       fail:
  142 |         msg: *failmsg
```

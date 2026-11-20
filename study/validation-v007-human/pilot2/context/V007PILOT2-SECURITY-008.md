# Frozen source context: V007PILOT2-SECURITY-008

- Repository: `theopenlab/openlab-zuul-jobs`
- Commit: `0d133dc0879296c0aacd0b70344515c94137a8ec`
- Family: security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `playbooks/cloud-provider-openstack-acceptance-test-e2e-conformance/run.yaml` (reported anchor line 42)
- Flagged construct: not named by the finding; the anchor line 42 lies in the task at line 41, name `bootstrap kubernetes master`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–221 of 221:

```text
    1 | - hosts: k8s-master
    2 |   name: prepare configuration of kubeadm
    3 |   become: yes
    4 | 
    5 |   tasks:
    6 |     - name: create /etc/kubernetes
    7 |       file:
    8 |         path: /etc/kubernetes
    9 |         state: directory
   10 | 
   11 |     - name: ship kubeadm.yaml
   12 |       copy:
   13 |         dest: /etc/kubernetes/kubeadm.yaml
   14 |         content: |
   15 |           apiVersion: kubeadm.k8s.io/v1beta2
   16 |           kind: ClusterConfiguration
   17 |           networking:
   18 |             podSubnet: 10.244.0.0/16
   19 |           kubernetesVersion: {{ kubernetes_version | default('latest') }}
   20 |           apiServer:
   21 |             extraArgs:
   22 |               "cloud-provider": "external"
   23 |           controllerManager:
   24 |             extraArgs:
   25 |               "cloud-provider": "external"
   26 | 
   27 | - hosts: all
   28 |   name: kubelet cloud-provider external
   29 |   become: yes
   30 | 
   31 |   roles:
   32 |     - cloud-instance-hostname
   33 | 
   34 |   tasks:
   35 |     - name: ship /etc/default/kubelet
   36 |       copy:
   37 |         dest: /etc/default/kubelet
   38 |         content: |
   39 |           KUBELET_EXTRA_ARGS=--cloud-provider=external
   40 | 
   41 | - hosts: k8s-master
   42 |   name: bootstrap kubernetes master
   43 |   become: yes
   44 | 
   45 |   roles:
   46 |     - config-golang
   47 |     - export-cloud-openrc
   48 |     - role: create-multinodes-k8s-cluster-with-kubeadm
   49 |       k8s_role_to_deploy: ["master"]
   50 | 
   51 |   tasks:
   52 |     - name: Prepare base alpine image
   53 |       shell:
   54 |          cmd: |
   55 |            docker login -u ap-southeast-3@{{ swr.ak }} -p {{ swr.sk }} swr.ap-southeast-3.myhuaweicloud.com
   56 |            docker pull swr.ap-southeast-3.myhuaweicloud.com/openlab/alpine:3.11
   57 |            docker tag swr.ap-southeast-3.myhuaweicloud.com/openlab/alpine:3.11 alpine:3.11
   58 |            docker logout swr.ap-southeast-3.myhuaweicloud.com
   59 |       no_log: yes
   60 | 
   61 |     - name: Build openstack-cloud-controller-manager image
   62 |       environment: '{{ global_env }}'
   63 |       shell:
   64 |         executable: /bin/bash
   65 |         chdir: '{{ k8s_os_provider_src_dir }}'
   66 |         cmd: |
   67 |           set -o pipefail
   68 |           set -ex
   69 | 
   70 |           export ARCH=amd64
   71 |           export IMAGE_NAMES=openstack-cloud-controller-manager
   72 |           export VERSION=latest
   73 |           # To be compatible with old releases, using make image-controller-manager
   74 |           make image-controller-manager
   75 | 
   76 |     - name: Tag image
   77 |       environment: '{{ global_env }}'
   78 |       shell:
   79 |         executable: /bin/bash
   80 |         chdir: '{{ k8s_os_provider_src_dir }}'
   81 |         cmd: |
   82 |           set -o pipefail
   83 |           set -ex
   84 | 
   85 |           export ARCH=amd64
   86 |           export IMAGE_NAMES=openstack-cloud-controller-manager
   87 | 
   88 |           # The previous CPO makefile doesn't support arch
   89 |           docker tag k8scloudprovider/${IMAGE_NAMES}-${ARCH}:latest k8scloudprovider/${IMAGE_NAMES}:latest
   90 |       ignore_errors: yes
   91 | 
   92 |     - name: create cloud-config
   93 |       environment: '{{ global_env }}'
   94 |       shell:
   95 |         chdir: '{{ k8s_os_provider_src_dir }}'
   96 |         executable: /bin/bash
   97 |         cmd: |
   98 |           set -o pipefail
   99 |           set -ex
  100 | 
  101 |           cat > /etc/kubernetes/cloud-config <<EOF
  102 |           [Global]
  103 |           domain-name = $OS_USER_DOMAIN_NAME
  104 |           tenant-id = $OS_PROJECT_ID
  105 |           auth-url = $OS_AUTH_URL
  106 |           password = [REDACTED_LITERAL]
  107 |           username = $OS_USERNAME
  108 |           region = $OS_REGION_NAME
  109 |           [BlockStorage]
  110 |           bs-version = v3
  111 |           ignore-volume-az = yes
  112 |           EOF
  113 | 
  114 |           # Create cloud-config
  115 |           kubectl -n kube-system create secret generic cloud-config --from-file=cloud.conf=/etc/kubernetes/cloud-config -oyaml
  116 | 
  117 |     - name: depoy openstack cloud controller manager
  118 |       shell:
  119 |         chdir: '{{ k8s_os_provider_src_dir }}'
  120 |         executable: /bin/bash
  121 |         cmd: |
  122 |           set -ex
  123 | 
  124 |           kubectl apply -f manifests/controller-manager/cloud-controller-manager-roles.yaml
  125 |           kubectl apply -f manifests/controller-manager/cloud-controller-manager-role-bindings.yaml
  126 |           kubectl apply -f manifests/controller-manager/openstack-cloud-controller-manager-ds.yaml
  127 | 
  128 |     - name: get kubeadm join command
  129 |       shell: kubeadm token create --print-join-command 2>/dev/null
  130 |       register: kubeadm_join_cmd
  131 | 
  132 | - hosts: k8s-node-1,k8s-node-2
  133 |   name: join kubernetes nodes
  134 |   become: yes
  135 |   roles:
  136 |     - role: create-multinodes-k8s-cluster-with-kubeadm
  137 |       k8s_role_to_deploy:
  138 |         - node
  139 |       kubeadm_join_cmd: "{{ hostvars['k8s-master']['kubeadm_join_cmd']['stdout'] }}"
  140 |   tasks:
  141 |     - name: Prepare base alpine image
  142 |       shell:
  143 |          cmd: |
  144 |            docker login -u ap-southeast-3@{{ swr.ak }} -p {{ swr.sk }} swr.ap-southeast-3.myhuaweicloud.com
  145 |            docker pull swr.ap-southeast-3.myhuaweicloud.com/openlab/alpine:3.11
  146 |            docker tag swr.ap-southeast-3.myhuaweicloud.com/openlab/alpine:3.11 alpine:3.11
  147 |            docker logout swr.ap-southeast-3.myhuaweicloud.com
  148 |       no_log: yes
  149 | 
  150 | - hosts: k8s-master
  151 |   name: Run conformance test
  152 |   become: yes
  153 | 
  154 |   tasks:
  155 |     - name: Wait for nodes ready
  156 |       shell:
  157 |         executable: /bin/bash
  158 |         cmd: kubectl get nodes | grep Ready | wc -l
  159 |       register: result
  160 |       until: result.stdout | int == 3
  161 |       retries: 30
  162 |       delay: 10
  163 | 
  164 |     - name: Install kubetest
  165 |       environment: '{{ global_env }}'
  166 |       shell:
  167 |         executable: /bin/bash
  168 |         cmd: |
  169 |           set -o pipefail
  170 |           set -ex
  171 | 
  172 |           git clone https://github.com/kubernetes/test-infra --depth 1
  173 |           cd test-infra
  174 |           go install ./kubetest
  175 | 
  176 |     - name: Run conformance test
  177 |       environment: '{{ global_env }}'
  178 |       shell:
  179 |         executable: /bin/bash
  180 |         cmd: |
  181 |           set -ex
  182 | 
  183 |           K8S_VERSION=$(kubectl version -o json | jq -r '.serverVersion.gitVersion')
  184 |           export KUBERNETES_CONFORMANCE_TEST=y
  185 | 
  186 |           mkdir -p '{{ k8s_log_dir }}'
  187 |           export LOG_DIR='{{ k8s_log_dir }}'
  188 |           sudo chmod 777 $LOG_DIR
  189 |           export KUBE_MASTER_IP=$(ip route get 1.1.1.1 | awk '{print $7}')
  190 |           export KUBE_MASTER=k8s-master
  191 |           export MASTER_NAME=k8s-master
  192 |           export DUMP_ONLY_MASTER_LOGS=true
  193 | 
  194 |           kubetest --dump=$LOG_DIR \
  195 |             --test \
  196 |             --provider=skeleton \
  197 |             --ginkgo-parallel=1 \
  198 |             --test_args="--ginkgo.focus=\\[Conformance\\] --ginkgo.noColor=true --ginkgo.v=true --ginkgo.trace=true --disable-log-dump=true --ginkgo.skip=\\[sig\\-apps\\]\\sDaemon\\sset\\s\\[Serial\\]\\sshould\\srollback\\swithout\\sunnecessary\\srestarts\\s\\[Conformance\\]|\\[sig\\-network\\]\\sServices\\sshould\\sbe\\sable\\sto\\schange\\sthe\\stype\\sfrom\\sExternalName\\sto\\sNodePort\\s\\[Conformance\\]|\\[sig\\-network\\]\\sServices\\sshould\\sbe\\sable\\sto\\screate\\sa\\sfunctioning\\sNodePort\\sservice\\s\\[Conformance\\]|\\[sig\\-network\\]\\sServices\\sshould\\shave\\ssession\\saffinity\\swork\\sfor\\sNodePort\\sservice\\s\\[LinuxOnly\\]\\s\\[Conformance\\]|\\[sig\\-network\\]\\sServices\\sshould\\sbe\\sable\\sto\\sswitch\\ssession\\saffinity\\sfor\\sNodePort\\sservice\\s\\[LinuxOnly\\]\\s\\[Conformance\\]|\\[sig\\-network\\]\\sServices\\sshould\\shave\\ssession\\saffinity\\stimeout\\swork\\sfor\\sNodePort\\sservice\\s\\[LinuxOnly\\]\\s\\[Conformance\\]" \
  199 |             --extract ${K8S_VERSION} \
  200 |             --timeout=150m | tee $LOG_DIR/e2e.log
  201 | 
  202 |     - name: Run image build and publish for cloud-provider-openstack
  203 |       shell:
  204 |         cmd: |
  205 |           if [ '{{ zuul.pipeline }}' == 'periodic-14' ] && [ '{{ zuul.branch }}' == 'master' ]; then
  206 |             set -ex
  207 |             set -o pipefail
  208 | 
  209 |             docker login -u ap-southeast-3@{{ swr.ak }} -p {{ swr.sk }} swr.ap-southeast-3.myhuaweicloud.com
  210 | 
  211 |             export LOG_DIR='{{ k8s_log_dir }}'
  212 |             export REGISTRY=${REGISTRY:-swr.ap-southeast-3.myhuaweicloud.com/openlab}
  213 |             export ARCHS=${ARCHS:-amd64}
  214 |             export VERSION=${VERSION:-latest}
  215 |             make upload-images 2>&1 | tee $LOG_DIR/image-build-upload.log
  216 |           else
  217 |             exit 0;
  218 |           fi
  219 |         executable: /bin/bash
  220 |         chdir: '{{ k8s_os_provider_src_dir }}'
  221 |       environment: '{{ global_env }}'
```

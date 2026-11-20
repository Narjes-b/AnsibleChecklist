# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-044

- Repository: `Kubeinit/kubeinit`
- Commit: `da6fec314d5594b6bd97ef2e4e71f9098a85e63c`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `kubeinit/roles/kubeinit_openshift/tasks/main.yml` (reported anchor line 47)
- Object: `source_location` `acf446d2d02570c3da8308f17ee52b6a2a49cf102ce508c61f01b74f0d0eff03`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–206 of 206:

```text
    1 | ---
    2 | # Copyright kubeinit contributors
    3 | # All Rights Reserved.
    4 | #
    5 | # Licensed under the Apache License, Version 2.0 (the "License"); you may
    6 | # not use this file except in compliance with the License. You may obtain
    7 | # a copy of the License at
    8 | #
    9 | #     http://www.apache.org/licenses/LICENSE-2.0
   10 | #
   11 | # Unless required by applicable law or agreed to in writing, software
   12 | # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
   13 | # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
   14 | # License for the specific language governing permissions and limitations
   15 | # under the License.
   16 | 
   17 | - name: Deploy the cluster bootstrap and any other extra nodes requested
   18 |   ansible.builtin.include_role:
   19 |     name: kubeinit.kubeinit.kubeinit_libvirt
   20 |     tasks_from: deploy_{{ hostvars[kubeinit_deployment_node_name].os }}_guest.yml
   21 |     public: yes
   22 |   loop: "{{ groups['all_extra_nodes'] }}"
   23 |   loop_control:
   24 |     loop_var: kubeinit_deployment_node_name
   25 |   vars:
   26 |     kubeinit_deployment_delegate: "{{ hostvars[kubeinit_deployment_node_name].target }}"
   27 |     kubeinit_ignition_name: "{{ 'bootstrap' if kubeinit_deployment_node_name == 'bootstrap' else omit }}"
   28 |     kubeinit_coreos_initrd: "{{ kubeinit_openshift_coreos_initrd if kubeinit_deployment_node_name == 'bootstrap' else omit }}"
   29 |     kubeinit_coreos_raw: "{{ kubeinit_openshift_coreos_raw if kubeinit_deployment_node_name == 'bootstrap' else omit }}"
   30 |     kubeinit_coreos_rootfs: "{{ kubeinit_openshift_coreos_rootfs if kubeinit_deployment_node_name == 'bootstrap' else omit }}"
   31 | 
   32 | - name: Deploy the cluster controller nodes
   33 |   ansible.builtin.include_role:
   34 |     name: kubeinit.kubeinit.kubeinit_libvirt
   35 |     tasks_from: deploy_coreos_guest.yml
   36 |     public: yes
   37 |   loop: "{{ groups['all_controller_nodes'] }}"
   38 |   loop_control:
   39 |     loop_var: kubeinit_deployment_node_name
   40 |   vars:
   41 |     kubeinit_deployment_delegate: "{{ hostvars[kubeinit_deployment_node_name].target }}"
   42 |     kubeinit_ignition_name: master
   43 |     kubeinit_coreos_initrd: "{{ kubeinit_openshift_coreos_initrd }}"
   44 |     kubeinit_coreos_raw: "{{ kubeinit_openshift_coreos_raw }}"
   45 |     kubeinit_coreos_rootfs: "{{ kubeinit_openshift_coreos_rootfs }}"
   46 | 
   47 | - name: Verify that controller nodes are ok
   48 |   ansible.builtin.shell: |
   49 |     set -o pipefail
   50 |     export KUBECONFIG=~/install_dir/auth/kubeconfig; \
   51 |     oc get nodes | grep master | grep " Ready"
   52 |   args:
   53 |     executable: /bin/bash
   54 |   register: _result
   55 |   changed_when: "_result.rc == 0"
   56 |   retries: 60
   57 |   delay: 60
   58 |   delegate_to: "{{ kubeinit_provision_service_node }}"
   59 |   until: _result.stdout_lines | default([]) | list | length == kubeinit_controller_count|int
   60 | 
   61 | - name: Use single node cluster
   62 |   ansible.builtin.shell: |
   63 |     set -o pipefail
   64 |     export KUBECONFIG=~/install_dir/auth/kubeconfig
   65 |     oc get nodes
   66 |     oc patch etcd cluster -p='{"spec": {"unsupportedConfigOverrides": {"useUnsupportedUnsafeNonHANonProductionUnstableEtcd": true }}}' --type=merge
   67 |     oc patch authentications.operator.openshift.io cluster -p='{"spec": {"unsupportedConfigOverrides": {"useUnsupportedUnsafeNonHANonProductionUnstableOAuthServer": true }}}' --type=merge
   68 |   args:
   69 |     executable: /bin/bash
   70 |   register: _result
   71 |   changed_when: "_result.rc == 0"
   72 |   delegate_to: "{{ kubeinit_provision_service_node }}"
   73 |   when: kubeinit_controller_count|int == 1
   74 | 
   75 | # This can take a lot of time until the cluster converges
   76 | - name: Wait for bootstrap to complete
   77 |   ansible.builtin.shell: |
   78 |     openshift-install gather --dir install_dir bootstrap --bootstrap {{ hostvars[groups['all_extra_nodes'][0]].ansible_host }} \
   79 |         {% for node in groups['all_controller_nodes'] %}{% raw %} --master {% endraw %}{{ hostvars[node].ansible_host }}{% endfor %}
   80 | 
   81 |     openshift-install --dir=install_dir/ wait-for bootstrap-complete --log-level info
   82 |   args:
   83 |     executable: /bin/bash
   84 |   register: _result
   85 |   changed_when: "_result.rc == 0"
   86 |   retries: 5
   87 |   delay: 20
   88 |   delegate_to: "{{ kubeinit_provision_service_node }}"
   89 |   until: _result.rc == 0
   90 | 
   91 | - name: Remove bootstrap node from haproxy config
   92 |   ansible.builtin.command: |
   93 |     podman --remote --connection {{ hostvars[kubeinit_haproxy_service_node].target }} exec {{ kubeinit_haproxy_service_name }} sed -i '/bootstrap/s/^/#/' /usr/local/etc/haproxy/haproxy.cfg
   94 |   register: _result
   95 |   changed_when: "_result.rc == 0"
   96 |   delegate_to: localhost
   97 | 
   98 | - name: Restart haproxy container
   99 |   ansible.builtin.systemd:
  100 |     name: "{{ kubeinit_haproxy_service_name }}"
  101 |     state: restarted
  102 |     enabled: yes
  103 |     scope: user
  104 |   delegate_to: "{{ hostvars[kubeinit_haproxy_service_node].target }}"
  105 | 
  106 | # To run in the hypervisor where the bootstrap machine is deployed
  107 | - name: Remove boostrap node
  108 |   block:
  109 | 
  110 |     - name: Destroy bootstrap node VM
  111 |       community.libvirt.virt:
  112 |         name: "{{ hostvars[kubeinit_deployment_node_name].guest_name }}"
  113 |         command: destroy
  114 | 
  115 |     - name: Undefine bootstrap node VM
  116 |       community.libvirt.virt:
  117 |         name: "{{ hostvars[kubeinit_deployment_node_name].guest_name }}"
  118 |         command: undefine
  119 | 
  120 |     - name: Remove bootstrap node VM storage
  121 |       ansible.builtin.file:
  122 |         state: absent
  123 |         path: "{{ kubeinit_libvirt_target_image_dir }}/{{ hostvars[kubeinit_deployment_node_name].guest_name }}.qcow2"
  124 | 
  125 |   vars:
  126 |     kubeinit_deployment_node_name: "{{ groups['all_extra_nodes'][0] }}"
  127 |   delegate_to: "{{ hostvars[kubeinit_deployment_node_name].target }}"
  128 | 
  129 | - name: Deploy the cluster compute nodes
  130 |   ansible.builtin.include_role:
  131 |     name: kubeinit.kubeinit.kubeinit_libvirt
  132 |     tasks_from: deploy_coreos_guest.yml
  133 |     public: yes
  134 |   loop: "{{ groups['all_compute_nodes'] | default([]) }}"
  135 |   loop_control:
  136 |     loop_var: kubeinit_deployment_node_name
  137 |   vars:
  138 |     kubeinit_deployment_delegate: "{{ hostvars[kubeinit_deployment_node_name].target }}"
  139 |     kubeinit_ignition_name: worker
  140 |     kubeinit_coreos_initrd: "{{ kubeinit_openshift_coreos_initrd }}"
  141 |     kubeinit_coreos_raw: "{{ kubeinit_openshift_coreos_raw }}"
  142 |     kubeinit_coreos_rootfs: "{{ kubeinit_openshift_coreos_rootfs }}"
  143 | 
  144 | - name: Complete the cluster deployment on the provision service node
  145 |   block:
  146 | 
  147 |     - name: Wait until all nodes are ready
  148 |       ansible.builtin.shell: |
  149 |         set -o pipefail
  150 |         export KUBECONFIG=~/install_dir/auth/kubeconfig; \
  151 |         oc get csr -o json | jq -r '.items[] | .metadata.name' | xargs oc adm certificate approve >/dev/null 2>&1; \
  152 |         oc get nodes | grep " Ready"
  153 |       args:
  154 |         executable: /bin/bash
  155 |       register: _result
  156 |       changed_when: "_result.rc == 0"
  157 |       retries: 60
  158 |       delay: 60
  159 |       until: _result.stdout_lines | default([]) | list | length == kubeinit_cluster_node_count|int
  160 | 
  161 |     - name: Copy the kubeconfig
  162 |       ansible.builtin.shell: |
  163 |         cp ~/install_dir/auth/kubeconfig ~/.kube/config
  164 |       args:
  165 |         executable: /bin/bash
  166 |       register: _result
  167 |       changed_when: "_result.rc == 0"
  168 | 
  169 |     - name: Install kustomize
  170 |       ansible.builtin.shell: |
  171 |         curl -sL https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv5.1.0/kustomize_v5.1.0_linux_amd64.tar.gz > kustomize.tar.gz
  172 |         tar xzf ./kustomize.tar.gz
  173 |         mv ./kustomize /bin/
  174 |       args:
  175 |         executable: /bin/bash
  176 |       register: _result
  177 |       changed_when: "_result.rc == 0"
  178 | 
  179 |     - name: Get some final cluster information
  180 |       ansible.builtin.shell: |
  181 |         set -eo pipefail
  182 |         export KUBECONFIG=~/install_dir/auth/kubeconfig
  183 |         oc get nodes
  184 |       args:
  185 |         executable: /bin/bash
  186 |       ignore_errors: yes
  187 |       register: _result_cluster_info
  188 |       changed_when: "_result_cluster_info.rc == 0"
  189 | 
  190 |     - name: Display final debug info
  191 |       ansible.builtin.debug:
  192 |         var: _result_cluster_info
  193 | 
  194 |     - name: Print some final data
  195 |       vars:
  196 |         msg: |
  197 |           Get the kubeadmin password from the services machine
  198 |             cat ~/install_dir/auth/kubeadmin-password
  199 |           The OpenShift UI endpoint is:
  200 |             console-openshift-console.apps.{{ kubeinit_cluster_fqdn }}
  201 |       ansible.builtin.debug:
  202 |         msg: "{{ msg.split('\n') }}"
  203 | 
  204 |   vars:
  205 |     kubeinit_deployment_node_name: "{{ kubeinit_provision_service_node }}"
  206 |   delegate_to: "{{ kubeinit_deployment_node_name }}"
```

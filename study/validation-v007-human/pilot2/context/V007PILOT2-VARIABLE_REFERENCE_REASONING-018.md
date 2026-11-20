# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-018

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `ansible/roles/k8s_cluster/tasks/install.yml` (reported anchor line 83)
- Flagged construct: variable `k8s_add_repo_alt_res`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–228 of 228:

```text
    1 | ---
    2 | - set_fact:
    3 |     api_server: "{{ ansible_ssh_host }}"
    4 |   when: apiserver_address is undefined
    5 | 
    6 | - set_fact:
    7 |     api_server: "{{ apiserver_address }}"
    8 |   when: (apiserver_address is defined) and (apiserver_address|length > 0)
    9 | 
   10 | - name: "Include firewalld handlers"
   11 |   include_role:
   12 |     name: "sec/firewalld"
   13 | 
   14 | - name: "Add masquerade to trusted zone"
   15 |   firewalld:
   16 |     masquerade: True | bool
   17 |     zone: "trusted"
   18 |     permanent: yes
   19 |     state: enabled
   20 |   notify: Restart firewalld
   21 |   become: true
   22 | 
   23 | - name: Add source network to trusted sources
   24 |   firewalld:
   25 |     source: "{{ item }}"
   26 |     zone: "trusted"
   27 |     permanent: yes
   28 |     state: enabled
   29 |   loop:
   30 |     - "{{ pod_subnet }}"
   31 |     - "{{ service_subnet }}"
   32 |   notify: Restart firewalld
   33 |   become: true
   34 | 
   35 | - name: Open k8s known ports
   36 |   firewalld:
   37 |     port: "{{ item }}"
   38 |     zone: "public"
   39 |     permanent: yes
   40 |     state: enabled
   41 |   loop: "{{ firewalld_public_ports }}"
   42 |   notify: Restart firewalld
   43 |   become: true
   44 | 
   45 | - name: Open k8s known services
   46 |   firewalld:
   47 |     service: "{{ item }}"
   48 |     zone: "public"
   49 |     permanent: yes
   50 |     state: enabled
   51 |   loop: "{{ firewalld_public_services }}"
   52 |   notify: Restart firewalld
   53 |   become: true
   54 | 
   55 | - name: "Flush handlers"
   56 |   meta: flush_handlers
   57 | 
   58 | - name: "Disable selinux"
   59 |   shell: |
   60 |     setenforce 0
   61 |     sed -i 's/^SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config
   62 |     getenforce
   63 |   become: true
   64 | 
   65 | - name: "Custom installation for Fedora"
   66 |   include_tasks: "install_Fedora.yml"
   67 |   when: "ansible_distribution == 'Fedora'"
   68 | 
   69 | - name: "Add kubernetes repository"
   70 |   yum_repository:
   71 |     name: kubernetes
   72 |     description: Kubernetes
   73 |     baseurl: https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
   74 |     gpgcheck: true
   75 |     repo_gpgcheck: true
   76 |     gpgkey: https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
   77 |     exclude: kube*
   78 |     state: present
   79 |   become: true
   80 |   register: k8s_add_repo_res
   81 |   failed_when: "k8s_add_repo_res.rc is defined and k8s_add_repo_res.rc > 0 and k8s_add_repo_res.stderr is defined and 'signature could not be verified for kubernetes' not in k8s_add_repo_res.stderr"
   82 | 
   83 | - name: "Add kubernetes repository alternative to GPG key failure"
   84 |   yum_repository:
   85 |     name: kubernetes
   86 |     description: Kubernetes
   87 |     baseurl: https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
   88 |     gpgcheck: false
   89 |     repo_gpgcheck: false
   90 |     gpgkey: https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
   91 |     exclude: kube*
   92 |     state: present
   93 |   become: true
   94 |   register: k8s_add_repo_alt_res
   95 |   when: "k8s_add_repo_res is not defined or (k8s_add_repo_res.rc is defined and k8s_add_repo_res.rc > 0 and k8s_add_repo_res.stderr is defined and 'signature could not be verified for kubernetes' in k8s_add_repo_res.stderr)"
   96 | 
   97 | - name: "Install Kubernetes packages - {{ k8s_version }}"
   98 |   package:
   99 |     name: "{{ packages }}"
  100 |     state: present
  101 |     disable_excludes: kubernetes
  102 |   vars:
  103 |     packages:
  104 |       - kubectl-{{ k8s_version }}
  105 |       - kubeadm-{{ k8s_version }}
  106 |       - kubelet-{{ k8s_version }}
  107 |   become: true
  108 | 
  109 | - name: Disable selinux
  110 |   shell: |
  111 |     setenforce 0
  112 |     sed -i 's/^SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config
  113 |     getenforce
  114 |   become: true
  115 | 
  116 | - name: Start kubelet
  117 |   systemd:
  118 |     state: started
  119 |     name: kubelet
  120 |     daemon_reload: yes
  121 |     enabled: yes
  122 |   become: true
  123 | 
  124 | - name: Create k8s conf file
  125 |   template:
  126 |     src: "k8s.conf.j2"
  127 |     dest: /etc/sysctl.d/k8s.conf
  128 |   register: k8s_conf_file
  129 |   become: true
  130 | 
  131 | - name: Make k8s conf file take effect
  132 |   command: "sysctl --system"
  133 |   become: true
  134 |   when: k8s_conf_file.changed
  135 | 
  136 | - name: Remove CRI plugin disable from containerd toml
  137 |   ansible.builtin.replace:
  138 |     path: /etc/containerd/config.toml
  139 |     # regexp: '^disabled_plugins\ =\ \["cri"\]'
  140 |     # replace: '#disabled_plugins = ["cri"]'
  141 |     regexp: '^(disabled_plugins)(.*)("cri")(.*)'
  142 |     replace: '\1\2\4'
  143 |   register: enable_cri_plugin
  144 |   become: true
  145 | 
  146 | - name: Restart containerd
  147 |   ansible.builtin.service:
  148 |     name: containerd
  149 |     state: restarted
  150 |   become: true
  151 |   when: enable_cri_plugin.changed
  152 | 
  153 | - name: Pull k8s linux images for version {{ k8s_version }}
  154 |   command: "kubeadm config images pull --kubernetes-version {{ k8s_version }}"
  155 |   become: true
  156 | 
  157 | - name: "Checks k8s bootstrap status"
  158 |   stat: 
  159 |     path: "/etc/kubernetes/admin.conf"
  160 |   register: k8s_config_file
  161 | 
  162 | - name: "Initialize cluster for k8s - {{ k8s_version }}"
  163 |   command: "kubeadm init --pod-network-cidr={{ pod_subnet }} --apiserver-advertise-address={{ api_server }} --kubernetes-version {{ k8s_version }}"
  164 |   register: kubeadm_init_res
  165 |   changed_when: "kubeadm_init_res.rc == 0"
  166 |   failed_when: "kubeadm_init_res.rc != 0  and 'already exists' not in kubeadm_init_res.stderr"
  167 |   become: true
  168 |   when: "not k8s_config_file.stat.exists"
  169 | 
  170 | - name: "Checks k8s bootstrap status"
  171 |   stat: 
  172 |     path: ".kube/config"
  173 |   register: home_k8s_config_file
  174 | 
  175 | - name: "Copy config file"
  176 |   include_role:
  177 |     name: k8s_config
  178 |   vars:
  179 |     state: "present"
  180 |   when: "not home_k8s_config_file.stat.exists"
  181 | 
  182 | - name: "Install CNI < 1.24"
  183 |   ansible.builtin.include_tasks: install_cni_l124.yml
  184 |   when: k8s_version is version('1.24.0', '<')
  185 | 
  186 | - name: "Install CNI >= 1.24"
  187 |   ansible.builtin.include_tasks: install_cni.yml
  188 |   when: k8s_version is version('1.24.0', '>=')
  189 | 
  190 | - name: "Check if nodes are already tainted"
  191 |   shell: |
  192 |     kubectl get nodes -o jsonpath="{.items[].spec.taints[?(@.key=='node-role.kubernetes.io/{{ cp_name }}')]}"
  193 |   register: kc_check_tainted_nodes
  194 |   ignore_errors: True
  195 | 
  196 | - name: "Print taint output"
  197 |   debug: 
  198 |     msg: "kc_check_tainted_nodes: {{ kc_check_tainted_nodes }}"
  199 |   when: "kc_check_tainted_nodes is defined"
  200 | 
  201 | - name: Taint the nodes
  202 |   command: |
  203 |     kubectl taint nodes --all node-role.kubernetes.io/{{ cp_name }}-
  204 |   register: kc_taint_node_res
  205 |   failed_when: "kc_taint_node_res.rc != 0 and 'not found' not in kc_taint_node_res.stderr"
  206 | 
  207 | - name: "Print taint output"
  208 |   debug: 
  209 |     msg: "kc_taint_node_res: {{ kc_taint_node_res }}"
  210 |   when: "kc_taint_node_res is defined"
  211 | 
  212 | - name: "Generate ClusterRole file for the sa default and namespace kube-system"
  213 |   template:
  214 |     src: "clusterrole-admin.j2"
  215 |     dest: /tmp/clusterrole-admin.yml
  216 |   become: True
  217 | 
  218 | - name: "Grant Cluster Admin role to the serviceaccount default of kube-system"
  219 |   shell: |
  220 |     kubectl apply -f /tmp/clusterrole-admin.yml
  221 | 
  222 | - name: Create persistence volume
  223 |   include_tasks: create_single_pv.yml
  224 |   vars:
  225 |     volume_name: "pv{{ item }}"
  226 |   with_sequence: start=1 count=5 format=%03d
  227 | 
  228 | ...
```

## Visible variable references

```text
Whole-word search for `k8s_add_repo_alt_res`: 1 matches in 1 files; 1 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
ansible/roles/k8s_cluster/tasks/install.yml:94:  register: k8s_add_repo_alt_res

Other references:
```

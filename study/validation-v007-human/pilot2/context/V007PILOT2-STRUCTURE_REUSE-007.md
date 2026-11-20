# Frozen source context: V007PILOT2-STRUCTURE_REUSE-007

- Repository: `kubernetes-sigs/kubespray`
- Commit: `9ee6f9b27981b251d77302fd6cf631f330e0ec39`
- Family: structure_reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/kubernetes/control-plane/tasks/kubeadm-secondary.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/kubernetes/control-plane/tasks/kubeadm-secondary.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–141 of 141:

```text
    1 | ---
    2 | - name: Set kubeadm_discovery_address
    3 |   set_fact:
    4 |     # noqa: jinja[spacing]
    5 |     kubeadm_discovery_address: >-
    6 |       {%- if "127.0.0.1" in kube_apiserver_endpoint or "localhost" in kube_apiserver_endpoint -%}
    7 |       {{ first_kube_control_plane_address | ansible.utils.ipwrap }}:{{ kube_apiserver_port }}
    8 |       {%- else -%}
    9 |       {{ kube_apiserver_endpoint | regex_replace('https://', '') }}
   10 |       {%- endif %}
   11 |   tags:
   12 |     - facts
   13 | 
   14 | - name: Obtain kubeadm certificate key for joining control planes nodes
   15 |   when:
   16 |     - not kube_external_ca_mode
   17 |   run_once: true
   18 |   block:
   19 |     - name: Upload certificates so they are fresh and not expired
   20 |       command: >-
   21 |         {{ bin_dir }}/kubeadm init phase
   22 |         --config {{ kube_config_dir }}/kubeadm-config.yaml
   23 |         upload-certs
   24 |         --upload-certs
   25 |       register: kubeadm_upload_cert
   26 |       delegate_to: "{{ first_kube_control_plane }}"
   27 | 
   28 |     - name: Parse certificate key if not set
   29 |       set_fact:
   30 |         kubeadm_certificate_key: "{{ kubeadm_upload_cert.stdout_lines[-1] | trim }}"
   31 | 
   32 | - name: Wait for k8s apiserver
   33 |   wait_for:
   34 |     host: "{{ kubeadm_discovery_address | regex_replace('\\]?:\\d+$', '') | regex_replace('^\\[', '') }}"
   35 |     port: "{{ kubeadm_discovery_address.split(':')[-1] }}"
   36 |     timeout: 180
   37 | 
   38 | 
   39 | - name: Check already run
   40 |   debug:
   41 |     msg: "{{ kubeadm_already_run.stat.exists }}"
   42 | 
   43 | - name: Reset cert directory
   44 |   shell: >-
   45 |     if [ -f /etc/kubernetes/manifests/kube-apiserver.yaml ]; then
   46 |     {{ bin_dir }}/kubeadm reset -f --cert-dir {{ kube_cert_dir }};
   47 |     fi
   48 |   environment:
   49 |     PATH: "{{ bin_dir }}:{{ ansible_env.PATH }}"
   50 |   when:
   51 |     - inventory_hostname != first_kube_control_plane
   52 |     - kubeadm_already_run is not defined or not kubeadm_already_run.stat.exists
   53 |     - not kube_external_ca_mode
   54 | 
   55 | - name: Get kubeconfig for join discovery process
   56 |   command: "{{ kubectl }} -n kube-public get cm cluster-info -o jsonpath='{.data.kubeconfig}'"
   57 |   register: kubeconfig_file_discovery
   58 |   run_once: true
   59 |   delegate_to: "{{ groups['kube_control_plane'] | first }}"
   60 |   when:
   61 |     - kubeadm_use_file_discovery
   62 |     - kubeadm_already_run is not defined or not kubeadm_already_run.stat.exists
   63 | 
   64 | - name: Copy discovery kubeconfig
   65 |   copy:
   66 |     dest: "{{ kube_config_dir }}/cluster-info-discovery-kubeconfig.yaml"
   67 |     content: "{{ kubeconfig_file_discovery.stdout }}"
   68 |     owner: "root"
   69 |     mode: "0644"
   70 |   when:
   71 |     - inventory_hostname != first_kube_control_plane
   72 |     - kubeadm_use_file_discovery
   73 |     - kubeadm_already_run is not defined or not kubeadm_already_run.stat.exists
   74 | 
   75 | - name: Create kubeadm ControlPlane config
   76 |   template:
   77 |     src: "kubeadm-controlplane.yaml.j2"
   78 |     dest: "{{ kube_config_dir }}/kubeadm-controlplane.yaml"
   79 |     mode: "0640"
   80 |     backup: true
   81 |     validate: "{{ kubeadm_config_validate_enabled | ternary(bin_dir + '/kubeadm config validate --config %s', omit) }}"
   82 |   when:
   83 |     - inventory_hostname != first_kube_control_plane
   84 |     - not kubeadm_already_run.stat.exists
   85 | 
   86 | - name: Joining control plane node to the cluster.
   87 |   when:
   88 |     - inventory_hostname != first_kube_control_plane
   89 |     - kubeadm_already_run is not defined or not kubeadm_already_run.stat.exists
   90 |   environment:
   91 |     PATH: "{{ bin_dir }}:{{ ansible_env.PATH }}"
   92 |   block:
   93 |     - name: Joining control plane node to the cluster. (1st try)
   94 |       command: >-
   95 |         {{ bin_dir }}/kubeadm join
   96 |         --config {{ kube_config_dir }}/kubeadm-controlplane.yaml
   97 |         --ignore-preflight-errors={{ kubeadm_ignore_preflight_errors | join(',') }}
   98 |         --skip-phases={{ kubeadm_join_phases_skip | join(',') }}
   99 |       register: kubeadm_join_control_plane
  100 |       throttle: 1
  101 |   rescue:
  102 |     - name: Reset cert directory before retrying control plane join
  103 |       command: "{{ bin_dir }}/kubeadm reset -f --cert-dir {{ kube_cert_dir }}"
  104 |       environment:
  105 |         PATH: "{{ bin_dir }}:{{ ansible_env.PATH }}"
  106 |     - name: Joining control plane node to the cluster. (retry)
  107 |       command: >-
  108 |         {{ bin_dir }}/kubeadm join
  109 |         --config {{ kube_config_dir }}/kubeadm-controlplane.yaml
  110 |         --ignore-preflight-errors={{ _ignore_errors | flatten | join(',') }}
  111 |         --skip-phases={{ kubeadm_join_phases_skip | join(',') }}
  112 |       vars:
  113 |         _errors_from_first_try:
  114 |           - 'FileAvailable--etc-kubernetes-manifests-kube-controller-manager.yaml'
  115 |           - 'FileAvailable--etc-kubernetes-manifests-kube-scheduler.yaml'
  116 |           - 'FileAvailable--etc-kubernetes-manifests-kube-apiserver.yaml'
  117 |           - 'Port-10250'
  118 |         _ignore_errors:
  119 |           - "{{ kubeadm_ignore_preflight_errors }}"
  120 |           - "{{ _errors_from_first_try if 'all' not in kubeadm_ignore_preflight_errors else [] }}"
  121 |       register: kubeadm_join_control_plane
  122 |       retries: 2
  123 |       until: kubeadm_join_control_plane is succeeded
  124 |       throttle: 1
  125 | 
  126 | - name: Wait for new control plane nodes to be Ready
  127 |   when:
  128 |     - kubeadm_already_run.stat.exists
  129 |     - kube_network_plugin not in ['cni', 'none']
  130 |   run_once: true
  131 |   command: >
  132 |     {{ kubectl }} get nodes --selector node-role.kubernetes.io/control-plane
  133 |     -o jsonpath-as-json="{.items[*].status.conditions[?(@.type == 'Ready')]}"
  134 |   register: control_plane_node_ready_conditions
  135 |   retries: "{{ control_plane_node_become_ready_tries }}"
  136 |   delay: 5
  137 |   delegate_to: "{{ groups['kube_control_plane'][0] }}"
  138 |   until: >
  139 |     control_plane_node_ready_conditions.stdout
  140 |     | from_json | selectattr('status', '==', 'True')
  141 |     | length == (groups['kube_control_plane'] | length)
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/kubernetes/control-plane`; 33 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: no
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: no

roles/kubernetes/control-plane/defaults/main/etcd.yml
roles/kubernetes/control-plane/defaults/main/kube-proxy.yml
roles/kubernetes/control-plane/defaults/main/kube-scheduler.yml
roles/kubernetes/control-plane/defaults/main/main.yml
roles/kubernetes/control-plane/handlers/main.yml
roles/kubernetes/control-plane/meta/main.yml
roles/kubernetes/control-plane/tasks/check-api.yml
roles/kubernetes/control-plane/tasks/encrypt-at-rest.yml
roles/kubernetes/control-plane/tasks/kubeadm-backup.yml
roles/kubernetes/control-plane/tasks/kubeadm-etcd.yml
roles/kubernetes/control-plane/tasks/kubeadm-secondary.yml
roles/kubernetes/control-plane/tasks/kubeadm-setup.yml
roles/kubernetes/control-plane/tasks/kubeadm-upgrade.yml
roles/kubernetes/control-plane/tasks/main.yml
roles/kubernetes/control-plane/tasks/pre-upgrade.yml
roles/kubernetes/control-plane/templates/admission-controls.yaml.j2
roles/kubernetes/control-plane/templates/apiserver-audit-policy.yaml.j2
roles/kubernetes/control-plane/templates/apiserver-audit-webhook-config.yaml.j2
roles/kubernetes/control-plane/templates/apiserver-tracing.yaml.j2
roles/kubernetes/control-plane/templates/eventratelimit.yaml.j2
roles/kubernetes/control-plane/templates/k8s-certs-renew.service.j2
roles/kubernetes/control-plane/templates/k8s-certs-renew.sh.j2
roles/kubernetes/control-plane/templates/k8s-certs-renew.timer.j2
roles/kubernetes/control-plane/templates/kubeadm-config.v1beta4.yaml.j2
roles/kubernetes/control-plane/templates/kubeadm-controlplane.yaml.j2
roles/kubernetes/control-plane/templates/kubescheduler-config.yaml.j2
roles/kubernetes/control-plane/templates/podnodeselector.yaml.j2
roles/kubernetes/control-plane/templates/podsecurity.yaml.j2
roles/kubernetes/control-plane/templates/resourcequota.yaml.j2
roles/kubernetes/control-plane/templates/secrets_encryption.yaml.j2
roles/kubernetes/control-plane/templates/webhook-authorization-config.yaml.j2
roles/kubernetes/control-plane/templates/webhook-token-auth-config.yaml.j2
roles/kubernetes/control-plane/vars/main.yaml
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- leaf tasks (not counting block containers): 13 (the rule needs more than 10)
- include/import task or role, or play-level roles, present: no
```

# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-036

- Repository: `ethpandaops/ansible-collection-general`
- Commit: `15a1f3490258357c4652b96b80f0a92636fa4135`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/missing-bool-filters`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/k3s/tasks/calico/verify.yaml` (reported anchor line 1)
- Object: `source_location` `d0c4e61727a5cc9e87c153d38bdc43b53d8fe29039c6dd1eef36cb1d4e59d4df`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–175 of 175:

```text
    1 | ---
    2 | # Wait for Calico API to be ready
    3 | - name: Wait for Calico API server to be ready
    4 |   ansible.builtin.command:
    5 |     cmd: "k3s kubectl wait --for=condition=available apiservice v3.projectcalico.org --timeout=300s"
    6 |   register: k3s_wait_api
    7 |   retries: 10
    8 |   delay: 15
    9 |   until: k3s_wait_api is succeeded
   10 |   failed_when: false
   11 |   changed_when: false
   12 | 
   13 | # Ensure all pods are running
   14 | - name: Ensure all calico-system pods are running
   15 |   ansible.builtin.command:
   16 |     cmd: "k3s kubectl -n calico-system wait --for=condition=Ready pods --all --timeout=300s"
   17 |   register: k3s_calico_pods_ready
   18 |   retries: 5
   19 |   delay: 30
   20 |   until: k3s_calico_pods_ready is succeeded
   21 |   failed_when: false
   22 |   changed_when: false
   23 | 
   24 | # Handle problematic pods
   25 | - name: Handle problematic pods (if any)
   26 |   block:
   27 |     - name: Check for problematic calico pods
   28 |       ansible.builtin.shell:
   29 |         cmd: >
   30 |           set -o pipefail && k3s kubectl get pods -n calico-system |
   31 |           grep -E 'CrashLoop|Error|0/1' | awk '{print $1}'
   32 |       register: k3s_problematic_pods
   33 |       failed_when: false
   34 |       changed_when: false
   35 | 
   36 |     - name: Force restart problematic pods
   37 |       ansible.builtin.command:
   38 |         cmd: "k3s kubectl delete pod -n calico-system {{ item }}"
   39 |       with_items: "{{ k3s_problematic_pods.stdout_lines }}"
   40 |       when: k3s_problematic_pods.stdout_lines | length > 0
   41 |       failed_when: false
   42 |       changed_when: k3s_problematic_pods.stdout_lines | length > 0
   43 | 
   44 |     - name: Wait for pods to be recreated
   45 |       ansible.builtin.pause:
   46 |         seconds: 10
   47 |       when: k3s_problematic_pods.stdout_lines | length > 0
   48 | 
   49 |     - name: Re-check pod status after restart
   50 |       ansible.builtin.command:
   51 |         cmd: "k3s kubectl -n calico-system wait --for=condition=Ready pods --all --timeout=180s"
   52 |       register: k3s_calico_pods_ready_retry
   53 |       retries: 3
   54 |       delay: 20
   55 |       until: k3s_calico_pods_ready_retry is succeeded
   56 |       failed_when: false
   57 |       changed_when: false
   58 |       when: k3s_problematic_pods.stdout_lines | length > 0
   59 | 
   60 | # Verify Calico installation status
   61 | - name: Verify Calico installation
   62 |   block:
   63 |     - name: Check Calico controller status
   64 |       ansible.builtin.command:
   65 |         cmd: "k3s kubectl get tigerastatus -o json"
   66 |       register: k3s_calico_status
   67 |       failed_when: false
   68 |       changed_when: false
   69 | 
   70 |     - name: Parse Calico status (when available)
   71 |       ansible.builtin.set_fact:
   72 |         k3s_calico_status_json: "{{ k3s_calico_status.stdout | from_json }}"
   73 |       when: k3s_calico_status is succeeded and k3s_calico_status.stdout | length > 0
   74 | 
   75 |     - name: Display Calico component availability
   76 |       ansible.builtin.debug:
   77 |         msg: >-
   78 |           Calico Component {{ item.kind | default('Unknown') }}/{{ item.metadata.name | default('Unknown') }}
   79 |           availability: {{ (item.status.conditions | selectattr('type', 'equalto', 'Available') | first).status | default('Unknown')
   80 |           if item.status.conditions is defined else 'Unknown' }}
   81 |       loop: "{{ k3s_calico_status_json['items'] | default([]) }}"
   82 |       when: k3s_calico_status_json is defined
   83 |       loop_control:
   84 |         label: "{{ item.kind | default('Unknown') }}/{{ item.metadata.name | default('Unknown') }}"
   85 | 
   86 |     - name: Identify unavailable Calico components
   87 |       ansible.builtin.debug:
   88 |         msg: "Warning: Calico component {{ item.kind | default('Unknown') }}/{{ item.metadata.name | default('Unknown') }} is not available"
   89 |       when: |
   90 |         k3s_calico_status_json is defined and
   91 |         item.status is defined and
   92 |         item.status.conditions is defined and
   93 |         item.status.conditions | selectattr('type', 'equalto', 'Available') | list | length > 0 and
   94 |         (item.status.conditions | selectattr('type', 'equalto', 'Available') | first).status != 'True'
   95 |       loop: "{{ k3s_calico_status_json['items'] | default([]) }}"
   96 |       loop_control:
   97 |         label: "{{ item.kind | default('Unknown') }}/{{ item.metadata.name | default('Unknown') }}"
   98 | 
   99 | # Health checks for CNI pods
  100 | - name: Perform CNI pod health check validation
  101 |   block:
  102 |     - name: Get Calico CNI pods
  103 |       ansible.builtin.command:
  104 |         cmd: "k3s kubectl get pods -n calico-system -o json"
  105 |       register: k3s_cni_pods
  106 |       failed_when: false
  107 |       changed_when: false
  108 | 
  109 |     - name: Parse CNI pod data
  110 |       ansible.builtin.set_fact:
  111 |         k3s_cni_pods_json: "{{ k3s_cni_pods.stdout | from_json }}"
  112 |       when: k3s_cni_pods is succeeded and k3s_cni_pods.stdout | length > 0
  113 | 
  114 |     - name: Check CNI pod resource consumption
  115 |       ansible.builtin.command:
  116 |         cmd: "k3s kubectl top pods -n calico-system"
  117 |       register: k3s_cni_resource_usage
  118 |       failed_when: false
  119 |       changed_when: false
  120 | 
  121 |     - name: Display resource usage
  122 |       ansible.builtin.debug:
  123 |         msg: "{{ k3s_cni_resource_usage.stdout }}"
  124 |       when: k3s_cni_resource_usage is succeeded
  125 | 
  126 |     - name: Get pod names
  127 |       ansible.builtin.command:
  128 |         cmd: "k3s kubectl get pods -n calico-system -o name"
  129 |       register: k3s_pod_list_raw
  130 |       failed_when: false
  131 |       changed_when: false
  132 | 
  133 |     - name: Set pod names from raw command output
  134 |       ansible.builtin.set_fact:
  135 |         k3s_pod_names: "{{ k3s_pod_list_raw.stdout_lines | default([]) }}"
  136 |       when: k3s_pod_list_raw is defined and k3s_pod_list_raw.stdout is defined
  137 | 
  138 |     - name: Get restart count for each pod
  139 |       ansible.builtin.command:
  140 |         cmd: "k3s kubectl get {{ item }} -n calico-system -o jsonpath='{.status.containerStatuses[*].restartCount}'"
  141 |       register: k3s_pod_restart_counts
  142 |       loop: "{{ k3s_pod_names | default([]) }}"
  143 |       loop_control:
  144 |         label: "{{ item }}"
  145 |       when: k3s_pod_names is defined and k3s_pod_names
  146 |       failed_when: false
  147 |       changed_when: false
  148 | 
  149 |     - name: Display pods with high restart counts
  150 |       ansible.builtin.debug:
  151 |         msg: "Warning: {{ item.item }} has restart count: {{ item.stdout }}"
  152 |       loop: "{{ k3s_pod_restart_counts.results | default([]) }}"
  153 |       loop_control:
  154 |         label: "{{ item.item | default('unknown') }}"
  155 |       when:
  156 |         - item.stdout is defined
  157 |         - item.stdout | int > 5
  158 | 
  159 | # Validate connectivity between Calico components
  160 | - name: Validate connectivity between Calico components
  161 |   ansible.builtin.command:
  162 |     cmd: "k3s kubectl -n calico-system exec deployment/calico-typha -- calico-typha status"
  163 |   register: k3s_typha_status
  164 |   failed_when: false
  165 |   changed_when: false
  166 | 
  167 | - name: Display Typha status
  168 |   ansible.builtin.debug:
  169 |     msg: "Typha status: {{ k3s_typha_status.stdout | default('Unable to retrieve status') }}"
  170 |   when: k3s_typha_status is defined
  171 | 
  172 | # Summary of verification
  173 | - name: Set verification complete fact
  174 |   ansible.builtin.set_fact:
  175 |     k3s_calico_verification_complete: true
```

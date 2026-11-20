# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-023

- Repository: `openstack-k8s-operators/edpm-ansible`
- Commit: `9d5d672bb0787dc3e8b8ccc829bb101c28e4ee26`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/edpm_ovs_dpdk/tasks/configure.yml` (reported anchor line 233)
- Object: `variable` `17048c26adbb49d5fb583deb335b87ad21e060ac7b07e671675624d633651bd4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–237 of 237:

```text
    1 | ---
    2 | # Copyright 2023 Red Hat, Inc.
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
   17 | - name: Check valid input for edpm_ovs_dpdk_pmd_core_list
   18 |   ansible.builtin.fail:
   19 |     msg: "List of PMD cores cannot be empty - edpm_ovs_dpdk_pmd_core_list"
   20 |   when: edpm_ovs_dpdk_pmd_core_list|string|length == 0 or edpm_ovs_dpdk_pmd_core_list == 'null'
   21 | 
   22 | - name: PMD cores config
   23 |   when: edpm_ovs_dpdk_pmd_core_list|string|length > 0
   24 |   block:
   25 |     - name: Apply PMD cores config
   26 |       ansible.builtin.set_fact:
   27 |         pmd_cpu_mask:
   28 |           pmd-cpu-mask: "{{ edpm_ovs_dpdk_pmd_core_list | osp.edpm.cpu_mask }}"
   29 | 
   30 |     - name: Append other_config with PMD cores
   31 |       ansible.builtin.set_fact:
   32 |         edpm_ovs_other_config: "{{ {} | combine(pmd_cpu_mask) }}"
   33 | 
   34 | - name: Add memory channels to dpdk extra
   35 |   ansible.builtin.set_fact:
   36 |     edpm_ovs_dpdk_extra_internal: "{{ edpm_ovs_dpdk_extra }} -n {{ edpm_ovs_dpdk_memory_channels }}"
   37 | 
   38 | - name: Set DPDK extra
   39 |   block:
   40 |     - name: Apply DPDK extra
   41 |       ansible.builtin.set_fact:
   42 |         dpdk_extra:
   43 |           dpdk-extra: "'{{ edpm_ovs_dpdk_extra_internal }}'"
   44 | 
   45 |     - name: Append other_config with DPDK extra
   46 |       ansible.builtin.set_fact:
   47 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(dpdk_extra) }}"
   48 | 
   49 | - name: Set socket-mem and socket-limit config
   50 |   when: edpm_ovs_dpdk_socket_memory|string|length > 0
   51 |   block:
   52 |     - name: Apply socket-mem config
   53 |       ansible.builtin.set_fact:
   54 |         dpdk_socket_mem:
   55 |           dpdk-socket-mem: "{{ edpm_ovs_dpdk_socket_memory }}"
   56 | 
   57 |     - name: Apply socket-limit config
   58 |       ansible.builtin.set_fact:
   59 |         dpdk_socket_limit:
   60 |           dpdk-socket-limit: "{{ edpm_ovs_dpdk_socket_memory }}"
   61 | 
   62 |     - name: Append other_config with socket-mem and socket-limit
   63 |       ansible.builtin.set_fact:
   64 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(dpdk_socket_mem) | combine(dpdk_socket_limit) }}"
   65 | 
   66 | - name: Set Revalidator threads config
   67 |   when: edpm_ovs_dpdk_revalidator_cores|string|length > 0
   68 |   block:
   69 |     - name: Apply Revalidator threads config
   70 |       ansible.builtin.set_fact:
   71 |         n_revalidator_threads:
   72 |           n-revalidator-threads: "{{ edpm_ovs_dpdk_revalidator_cores }}"
   73 | 
   74 |     - name: Append other_config with Revalidator threads
   75 |       ansible.builtin.set_fact:
   76 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(n_revalidator_threads) }}"
   77 | 
   78 | - name: Set Handler threads config
   79 |   when: edpm_ovs_dpdk_handler_cores|string|length > 0
   80 |   block:
   81 |     - name: Apply Handler threads config
   82 |       ansible.builtin.set_fact:
   83 |         n_handler_threads:
   84 |           n-handler-threads: "{{ edpm_ovs_dpdk_handler_cores }}"
   85 | 
   86 |     - name: Append other_config with Handler thread
   87 |       ansible.builtin.set_fact:
   88 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(n_handler_threads) }}"
   89 | 
   90 | - name: Set EMC Insertion Probability config
   91 |   when: edpm_ovs_dpdk_emc_insertion_probablity|string|length > 0
   92 |   block:
   93 |     - name: Apply EMC Insertion Probability config
   94 |       ansible.builtin.set_fact:
   95 |         emc_insert_inv_prob:
   96 |           emc-insert-inv-prob: "{{ edpm_ovs_dpdk_emc_insertion_probablity }}"
   97 | 
   98 |     - name: Append other_config with EMC Insertion Probability
   99 |       ansible.builtin.set_fact:
  100 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(emc_insert_inv_prob) }}"
  101 | 
  102 | - name: Enable TSO in datapath
  103 |   when: edpm_ovs_dpdk_enable_tso|bool
  104 |   block:
  105 |     - name: Enable TSO in datapath
  106 |       ansible.builtin.set_fact:
  107 |         userspace_tso_enable:
  108 |           userspace-tso-enable: "{{ edpm_ovs_dpdk_enable_tso }}"
  109 | 
  110 |     - name: Append other_config with TSO flag
  111 |       ansible.builtin.set_fact:
  112 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(userspace_tso_enable) }}"
  113 | 
  114 | - name: Enable postcopy support
  115 |   when: edpm_ovs_dpdk_vhost_postcopy_support|bool
  116 |   block:
  117 |     - name: Enable postcopy support
  118 |       ansible.builtin.set_fact:
  119 |         vhost_postcopy_support:
  120 |           vhost-postcopy-support: "{{ edpm_ovs_dpdk_vhost_postcopy_support }}"
  121 | 
  122 |     - name: Append other_config with postcopy support flag
  123 |       ansible.builtin.set_fact:
  124 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(vhost_postcopy_support) }}"
  125 | 
  126 |     - name: Disable mlockall in ovs
  127 |       ansible.builtin.replace:
  128 |         path: '/etc/sysconfig/openvswitch'
  129 |         regexp: '^OPTIONS.*'
  130 |         replace: 'OPTIONS="{{ edpm_ovs_dpdk_vhost_postcopy_ovs_options }}"'
  131 | 
  132 | - name: Return ovs OPTIONS to default
  133 |   when: not edpm_ovs_dpdk_vhost_postcopy_support|bool
  134 |   ansible.builtin.replace:
  135 |     path: '/etc/sysconfig/openvswitch'
  136 |     regexp: '^OPTIONS.*'
  137 |     replace: 'OPTIONS=""'
  138 | 
  139 | - name: Enable DPDK OVS PMD Auto Load Balance
  140 |   when: edpm_ovs_dpdk_pmd_auto_lb|bool
  141 |   block:
  142 |     - name: Enable DPDK OVS PMD Auto Load Balance
  143 |       ansible.builtin.set_fact:
  144 |         pmd_auto_lb:
  145 |           pmd-auto-lb: "{{ edpm_ovs_dpdk_pmd_auto_lb }}"
  146 | 
  147 |     - name: Append other_config with PMD Auto Load Balance
  148 |       ansible.builtin.set_fact:
  149 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(pmd_auto_lb) }}"
  150 | 
  151 | - name: Set minimum PMD thread load threshold
  152 |   when: edpm_ovs_dpdk_pmd_load_threshold|string|length > 0
  153 |   block:
  154 |     - name: Apply minimum PMD thread load threshold
  155 |       ansible.builtin.set_fact:
  156 |         pmd_auto_lb_load_threshold:
  157 |           pmd-auto-lb-load-threshold: "{{ edpm_ovs_dpdk_pmd_load_threshold }}"
  158 | 
  159 |     - name: Append other_config with minimum PMD thread load threshold
  160 |       ansible.builtin.set_fact:
  161 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(pmd_auto_lb_load_threshold) }}"
  162 | 
  163 | - name: Set PMD load variance improvement threshold
  164 |   when: edpm_ovs_dpdk_pmd_improvement_threshold|string|length > 0
  165 |   block:
  166 |     - name: Apply PMD load variance improvement threshold
  167 |       ansible.builtin.set_fact:
  168 |         pmd_auto_lb_improvement_threshold:
  169 |           pmd-auto-lb-improvement-threshold: "{{ edpm_ovs_dpdk_pmd_improvement_threshold }}"
  170 | 
  171 |     - name: Append other_config with PMD load variance improvement threshold
  172 |       ansible.builtin.set_fact:
  173 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(pmd_auto_lb_improvement_threshold) }}"
  174 | 
  175 | - name: Set PMD auto load balancing interval
  176 |   when: edpm_ovs_dpdk_pmd_rebal_interval|string|length > 0
  177 |   block:
  178 |     - name: Apply PMD auto load balancing interval
  179 |       ansible.builtin.set_fact:
  180 |         pmd_auto_lb_rebal_interval:
  181 |           pmd-auto-lb-rebal-interval: "{{ edpm_ovs_dpdk_pmd_rebal_interval }}"
  182 | 
  183 |     - name: Append other_config with PMD auto load balancing interval
  184 |       ansible.builtin.set_fact:
  185 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(pmd_auto_lb_rebal_interval) }}"
  186 | 
  187 | - name: OVN bridge datapath type config
  188 |   when: edpm_ovn_datapath_type|string|length > 0
  189 |   block:
  190 |     - name: Apply PMD cores config
  191 |       ansible.builtin.set_fact:
  192 |         ovn_bridge_datapath_type:
  193 |           ovn-bridge-datapath-type: "{{ edpm_ovn_datapath_type }}"
  194 | 
  195 |     - name: Append external_ids with ovn datapath type
  196 |       ansible.builtin.set_fact:
  197 |         edpm_ovs_external_ids: "{{ {} | combine(ovn_bridge_datapath_type) }}"
  198 | 
  199 | - name: Set shared memory pool config
  200 |   when: edpm_ovs_dpdk_shared_mem_pool|string|length > 0
  201 |   block:
  202 |     - name: Apply shared memory pool config
  203 |       ansible.builtin.set_fact:
  204 |         dpdk_shared_mem_pool:
  205 |           shared-mempool-config: "{{ edpm_ovs_dpdk_shared_mem_pool }}"
  206 | 
  207 |     - name: Append other_config with shared memory pool
  208 |       ansible.builtin.set_fact:
  209 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(dpdk_shared_mem_pool) }}"
  210 | 
  211 | - name: Set PMD maximum sleep time
  212 |   when: edpm_ovs_dpdk_pmd_sleep_max|string|length > 0
  213 |   block:
  214 |     - name: Apply PMD maximum sleep time
  215 |       ansible.builtin.set_fact:
  216 |         dpdk_pmd_sleep_max:
  217 |           pmd-maxsleep: "{{ edpm_ovs_dpdk_pmd_sleep_max }}"
  218 | 
  219 |     - name: Append other_config with max sleep time
  220 |       ansible.builtin.set_fact:
  221 |         edpm_ovs_other_config: "{{ edpm_ovs_other_config | combine(dpdk_pmd_sleep_max) }}"
  222 | 
  223 | - name: Configure OVS other_config
  224 |   ansible.builtin.shell: >
  225 |     ovs-vsctl set open . {% for key, value in edpm_ovs_other_config.items() %} other_config:{{ key }}={{ value }} {% endfor %}
  226 |   register: ovs_other_config
  227 |   changed_when: ovs_other_config.rc == 0
  228 |   failed_when: ovs_other_config.rc != 0
  229 |   when: edpm_ovs_other_config | length > 0
  230 | 
  231 | - name: Configure OVS external_ids
  232 |   ansible.builtin.shell: >
  233 |     ovs-vsctl set open . {% for key, value in edpm_ovs_external_ids.items() -%} external_ids:{{ key }}={{ value }} {% endfor %}
  234 |   register: ovs_external_ids
  235 |   changed_when: ovs_external_ids.rc == 0
  236 |   failed_when: ovs_external_ids.rc != 0
  237 |   when: edpm_ovs_external_ids | length > 0
```

## Visible variable references

```text
9d5d672bb0787dc3e8b8ccc829bb101c28e4ee26:roles/edpm_ovs_dpdk/tasks/configure.yml:197:        edpm_ovs_external_ids: "{{ {} | combine(ovn_bridge_datapath_type) }}"
9d5d672bb0787dc3e8b8ccc829bb101c28e4ee26:roles/edpm_ovs_dpdk/tasks/configure.yml:233:    ovs-vsctl set open . {% for key, value in edpm_ovs_external_ids.items() -%} external_ids:{{ key }}={{ value }} {% endfor %}
9d5d672bb0787dc3e8b8ccc829bb101c28e4ee26:roles/edpm_ovs_dpdk/tasks/configure.yml:237:  when: edpm_ovs_external_ids | length > 0
```

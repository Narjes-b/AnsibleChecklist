# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-036

- Repository: `igou-io/igou-ansible`
- Commit: `5dac3e63735e0e15407c172e0abd56d431fe4e47`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-expression`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/openshift/vm_worker_reprovision.yaml` (reported anchor line 197)
- Object: `source_location` `4518d6d4bdb92d16a3b53bb7e21596eb53fe802f2e3bafeca7900db4c723ba1c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–457 of 457:

```text
    1 | ---
    2 | # Reprovision a TrueNAS-hosted VM worker end-to-end, unattended:
    3 | #   1. configure_vms.yaml recreates THIS worker's VM with a blank zvol
    4 | #      (scoped via truenas_vms_only; other absent VMs are not recreated)
    5 | #   2. generate a full add-node ISO (`oc adm node-image create`, no
    6 | #      --pxe) for this worker only
    7 | #   3. copy the ISO to the TrueNAS host, attach/refresh it as the VM's
    8 | #      CDROM (order 1005) and demote the netboot RAW below it for the
    9 | #      install boot, then start the VM
   10 | #   4. approve this node's CSRs (scoped, incl. decoding bootstrapper CSR
   11 | #      subjects) until the node is Ready, then restore the netboot RAW
   12 | #      to its steady-state boot order
   13 | #
   14 | # Lifecycle gating: vm_worker_state (create|rebuild|destroy, default
   15 | # rebuild) lets this playbook sit in the linear
   16 | # ocp-truenas-worker-node-manage workflow:
   17 | #   destroy — every play here no-ops (teardown already happened)
   18 | #   create  — reconcile: if the worker is already a Ready cluster node
   19 | #             the run ends green without touching it; otherwise it is
   20 | #             provisioned from scratch (configure_vms is create-only,
   21 | #             so an existing VM is left untouched either way)
   22 | #   rebuild — full reprovision; the node must be absent (asserted)
   23 | # E2E tested via AAP 2026-07-31 (3 rebuild cycles).
   24 | #
   25 | # Boot design — no netboot-pin changes required: with the zvol blank,
   26 | # the install boot falls through disk(1001, blank) -> agent ISO CDROM
   27 | # (1005; the netboot RAW is temporarily demoted to 1006 so the install
   28 | # never depends on firmware advancing past a failed iPXE exit), RHCOS
   29 | # installs and reboots, and the installed disk then boots first forever
   30 | # after. After the node joins, the netboot RAW is restored to 1004.
   31 | # The stale ISO stays attached but is NOT a usable reinstall path (its
   32 | # embedded ignition token expires within ~24h) — to rebuild again,
   33 | # rerun this playbook.
   34 | #
   35 | # Usage:
   36 | #   export KUBECONFIG=<cluster kubeconfig>
   37 | #   ansible-playbook playbooks/openshift/vm_worker_reprovision.yaml \
   38 | #     -i igou-inventory/inventory.yaml -e vm_worker=truenas-w1.igou.systems
   39 | #
   40 | # Notes:
   41 | # - In rebuild mode the node must NOT currently exist in the cluster
   42 | #   (run vm_worker_destroy.yaml first); asserted below.
   43 | # - No CSI smoke test here by design — validate storage manually once
   44 | #   the democratic-csi driver migration completes.
   45 | 
   46 | - name: Validate vm_worker_state before touching anything
   47 |   hosts: localhost
   48 |   gather_facts: false
   49 |   tasks:
   50 | 
   51 |     - name: Assert vm_worker_state is valid
   52 |       ansible.builtin.assert:
   53 |         that: vm_worker_state | default('rebuild', true) in ['create', 'rebuild', 'destroy']
   54 |         fail_msg: >-
   55 |           vm_worker_state must be create, rebuild or destroy
   56 |           (got '{{ vm_worker_state }}').
   57 | 
   58 | - name: Recreate the VM with a blank zvol (create-only, scoped to this worker)
   59 |   import_playbook: ../truenas/configure_vms.yaml
   60 |   when: vm_worker_state | default('rebuild', true) != 'destroy'
   61 |   vars:
   62 |     truenas_vms_only: >-
   63 |       {{ truenas_vms | selectattr('openshift_node', 'defined')
   64 |          | selectattr('openshift_node', 'equalto',
   65 |                       vm_worker | default('truenas-w1.igou.systems', true))
   66 |          | map(attribute='name') | list }}
   67 | 
   68 | - name: Generate the add-node ISO
   69 |   hosts: "{{ target_cluster | default('ocp') }}"
   70 |   connection: local
   71 |   gather_facts: true
   72 |   vars:
   73 |     _cluster: "{{ target_cluster | default('ocp') }}"
   74 |     worker: "{{ vm_worker | default('truenas-w1.igou.systems', true) }}"
   75 |     openshift_add_node_work_dir: "{{ ansible_env.HOME }}/openshift-add-node-iso/{{ _cluster }}"
   76 |     # Full-ISO mode: suppress the PXE-only bootArtifactsBaseURL field in
   77 |     # the shared nodes-config template.
   78 |     openshift_add_node_pxe: false
   79 |   pre_tasks:
   80 | 
   81 |     - name: End play — vm_worker_state=destroy has nothing to provision
   82 |       ansible.builtin.meta: end_play
   83 |       when: vm_worker_state | default('rebuild', true) == 'destroy'
   84 | 
   85 |     - name: Assert KUBECONFIG is set in the environment
   86 |       ansible.builtin.assert:
   87 |         that: lookup('env', 'KUBECONFIG') | length > 0
   88 |         fail_msg: Export KUBECONFIG before running this playbook.
   89 | 
   90 |     - name: Discover nodes already joined to the cluster
   91 |       ansible.builtin.command:
   92 |         cmd: oc get nodes -o jsonpath={.items[*].metadata.name}
   93 |       register: _existing_nodes
   94 |       changed_when: false
   95 | 
   96 |     # Persisted as a fact (not task vars) so the later truenas-hosted
   97 |     # plays can gate on hostvars[<cluster>]._worker_joined.
   98 |     - name: Record whether the worker is already a cluster node
   99 |       vars:
  100 |         _joined: "{{ _existing_nodes.stdout.split() }}"
  101 |         _joined_short: "{{ _existing_nodes.stdout.split() | map('regex_replace', '[.].*$', '') | list }}"
  102 |         _worker_short: "{{ worker.split('.') | first }}"
  103 |       ansible.builtin.set_fact:
  104 |         _worker_joined: >-
  105 |           {{ (([worker] | intersect(_joined))
  106 |               + ([_worker_short] | intersect(_joined_short)))
  107 |              | length > 0 }}
  108 | 
  109 |     - name: Assert the worker is not currently a cluster node (rebuild mode)
  110 |       ansible.builtin.assert:
  111 |         that: not _worker_joined
  112 |         fail_msg: >-
  113 |           {{ worker }} is still a node in the cluster — run
  114 |           playbooks/openshift/vm_worker_destroy.yaml first (or launch
  115 |           with vm_worker_state=rebuild via the workflow).
  116 |       when: vm_worker_state | default('rebuild', true) != 'create'
  117 | 
  118 |     - name: End play — create mode and the worker is already joined (no-op)
  119 |       ansible.builtin.meta: end_play
  120 |       when:
  121 |         - vm_worker_state | default('rebuild', true) == 'create'
  122 |         - _worker_joined
  123 | 
  124 |     - name: Restrict nodes-config rendering to this worker
  125 |       ansible.builtin.set_fact:
  126 |         _pending_workers:
  127 |           - "{{ worker }}"
  128 | 
  129 |   tasks:
  130 | 
  131 |     - name: Wipe stale work dir
  132 |       ansible.builtin.file:
  133 |         path: "{{ openshift_add_node_work_dir }}"
  134 |         state: absent
  135 | 
  136 |     - name: Create fresh work dir
  137 |       ansible.builtin.file:
  138 |         path: "{{ openshift_add_node_work_dir }}"
  139 |         state: directory
  140 |         mode: "0700"
  141 | 
  142 |     - name: Fetch cluster pull secret to work dir
  143 |       ansible.builtin.shell: |
  144 |         set -o pipefail
  145 |         oc -n openshift-config get secret pull-secret \
  146 |           -o jsonpath='{.data.\.dockerconfigjson}' \
  147 |           | base64 -d > "{{ openshift_add_node_work_dir }}/auth.json"
  148 |       args:
  149 |         executable: /bin/bash
  150 |       changed_when: true
  151 |       no_log: true
  152 | 
  153 |     - name: Lock down pull secret file mode
  154 |       ansible.builtin.file:
  155 |         path: "{{ openshift_add_node_work_dir }}/auth.json"
  156 |         mode: "0600"
  157 | 
  158 |     - name: Render nodes-config.yaml (this worker only)
  159 |       ansible.builtin.template:
  160 |         src: templates/nodes-config.yaml.j2
  161 |         dest: "{{ openshift_add_node_work_dir }}/nodes-config.yaml"
  162 |         mode: "0644"
  163 | 
  164 |     - name: Run `oc adm node-image create` (full ISO)
  165 |       ansible.builtin.command:
  166 |         cmd: >-
  167 |           oc adm node-image create
  168 |           --dir {{ openshift_add_node_work_dir }}
  169 |           --registry-config {{ openshift_add_node_work_dir }}/auth.json
  170 |       changed_when: true
  171 | 
  172 |     - name: Verify the ISO exists
  173 |       ansible.builtin.stat:
  174 |         path: "{{ openshift_add_node_work_dir }}/node.{{ openshift_add_node_arch }}.iso"
  175 |       register: _iso_stat
  176 |       failed_when: not _iso_stat.stat.exists
  177 | 
  178 |     - name: Set fact for later plays — ISO path
  179 |       ansible.builtin.set_fact:
  180 |         openshift_add_node_iso:
  181 |           path: "{{ openshift_add_node_work_dir }}/node.{{ openshift_add_node_arch }}.iso"
  182 | 
  183 | - name: Attach the ISO and boot the VM
  184 |   hosts: truenas
  185 |   become: true
  186 |   gather_facts: false
  187 |   vars:
  188 |     _cluster: "{{ target_cluster | default('ocp') }}"
  189 |     worker: "{{ vm_worker | default('truenas-w1.igou.systems', true) }}"
  190 |     _iso_src: "{{ hostvars[_cluster]['openshift_add_node_iso']['path'] }}"
  191 |     _images_dir: /mnt/ssd/vms/images
  192 |   tasks:
  193 | 
  194 |     - name: End play — nothing to provision (destroy mode or node already joined)
  195 |       ansible.builtin.meta: end_play
  196 |       when: >-
  197 |         vm_worker_state | default('rebuild', true) == 'destroy'
  198 |         or hostvars[_cluster]._worker_joined | default(false)
  199 | 
  200 |     - name: Resolve the VM definition for this worker
  201 |       ansible.builtin.set_fact:
  202 |         _vm_def: >-
  203 |           {{ (truenas_vms | selectattr('openshift_node', 'defined')
  204 |               | selectattr('openshift_node', 'equalto', worker)
  205 |               | list + [{}]) | first }}
  206 | 
  207 |     - name: Assert the worker maps to a truenas_vms entry
  208 |       ansible.builtin.assert:
  209 |         that: _vm_def.name is defined
  210 |         fail_msg: >-
  211 |           No truenas_vms entry has openshift_node == {{ worker }} —
  212 |           add the mapping in group_vars/truenas.yml.
  213 | 
  214 |     - name: Query the VM (created by the configure_vms import)
  215 |       ansible.builtin.command:
  216 |         argv:
  217 |           - midclt
  218 |           - call
  219 |           - vm.query
  220 |           - "{{ [['name', '=', _vm_def.name]] | to_json }}"
  221 |       register: _vmq
  222 |       changed_when: false
  223 | 
  224 |     - name: Assert the VM exists and is stopped
  225 |       vars:
  226 |         _vm: "{{ (_vmq.stdout | from_json + [{}]) | first }}"
  227 |       ansible.builtin.assert:
  228 |         that:
  229 |           - _vm.id is defined
  230 |           - _vm.status.state == 'STOPPED'
  231 |         fail_msg: >-
  232 |           VM {{ _vm_def.name }} is missing or not STOPPED — expected a
  233 |           fresh, never-started VM from configure_vms.yaml.
  234 | 
  235 |     - name: Copy the add-node ISO to the host
  236 |       ansible.posix.synchronize:
  237 |         src: "{{ _iso_src }}"
  238 |         dest: "{{ _images_dir }}/{{ _vm_def.name }}-addnode.iso"
  239 |         rsync_opts:
  240 |           - "--chmod=F0644"
  241 | 
  242 |     # Query the VM's devices unfiltered and pick out dtypes client-side:
  243 |     # `attributes.dtype` is a path into a JSON column, and middleware
  244 |     # filter support for that is unverified — an ignored filter would
  245 |     # return ALL devices and a blind `first` would then rewrite the boot
  246 |     # disk or NIC. Jinja-side filtering is correct regardless.
  247 |     - name: Query the VM's devices
  248 |       ansible.builtin.command:
  249 |         argv:
  250 |           - midclt
  251 |           - call
  252 |           - vm.device.query
  253 |           - "{{ [['vm', '=', (_vmq.stdout | from_json | first).id]] | to_json }}"
  254 |       register: _devq
  255 |       changed_when: false
  256 | 
  257 |     - name: Index the VM's CDROM and netboot RAW devices
  258 |       ansible.builtin.set_fact:
  259 |         _cdroms: >-
  260 |           {{ _devq.stdout | from_json
  261 |              | selectattr('attributes.dtype', 'defined')
  262 |              | selectattr('attributes.dtype', 'equalto', 'CDROM') | list }}
  263 |         _netboot_raws: >-
  264 |           {{ _devq.stdout | from_json
  265 |              | selectattr('attributes.dtype', 'defined')
  266 |              | selectattr('attributes.dtype', 'equalto', 'RAW') | list }}
  267 | 
  268 |     - name: Attach the ISO as a new CDROM (order 1005)
  269 |       ansible.builtin.command:
  270 |         argv:
  271 |           - midclt
  272 |           - call
  273 |           - vm.device.create
  274 |           - >-
  275 |             {{ {'vm': (_vmq.stdout | from_json | first).id,
  276 |                 'order': 1005,
  277 |                 'attributes': {'dtype': 'CDROM',
  278 |                                'path': _images_dir ~ '/' ~ _vm_def.name ~ '-addnode.iso'}} | to_json }}
  279 |       when: _cdroms | length == 0
  280 |       changed_when: true
  281 | 
  282 |     - name: Point the existing CDROM at the fresh ISO
  283 |       ansible.builtin.command:
  284 |         argv:
  285 |           - midclt
  286 |           - call
  287 |           - vm.device.update
  288 |           - "{{ (_cdroms | first).id }}"
  289 |           - >-
  290 |             {{ {'attributes': {'dtype': 'CDROM',
  291 |                                'path': _images_dir ~ '/' ~ _vm_def.name ~ '-addnode.iso'}} | to_json }}
  292 |       when: _cdroms | length > 0
  293 |       changed_when: true
  294 | 
  295 |     # Whether UEFI advances to the next boot entry when the netboot
  296 |     # image's iPXE exits non-zero is firmware-dependent; don't bet the
  297 |     # unattended install on it. Demote the RAW below the CDROM so the
  298 |     # fresh agent ISO is the first fallback after the (blank) disk.
  299 |     # Restored to 1004 by the final play once the node has joined.
  300 |     - name: Demote the netboot RAW below the install CDROM (order 1006)
  301 |       ansible.builtin.command:
  302 |         argv:
  303 |           - midclt
  304 |           - call
  305 |           - vm.device.update
  306 |           - "{{ item.id }}"
  307 |           # TrueNAS 25.10 re-validates stored attributes on partial
  308 |           # updates and rejects a RAW device whose image exists while
  309 |           # attributes.exists is unset ("Path must not exist...") —
  310 |           # resend the attributes with exists=true alongside the order.
  311 |           - >-
  312 |             {{ {'order': 1006,
  313 |                 'attributes': item.attributes | combine({'exists': true})}
  314 |                | to_json }}
  315 |       loop: "{{ _netboot_raws }}"
  316 |       loop_control:
  317 |         label: "device {{ item.id }} (order {{ item.order }})"
  318 |       when: item.order != 1006
  319 |       changed_when: true
  320 | 
  321 |     - name: Start the VM (retries ride out transient zvol-open error 512)
  322 |       ansible.builtin.command:
  323 |         argv: [midclt, call, vm.start, "{{ (_vmq.stdout | from_json | first).id }}"]
  324 |       register: _start
  325 |       until: _start.rc == 0
  326 |       retries: 10
  327 |       delay: 15
  328 |       changed_when: true
  329 | 
  330 | - name: Approve CSRs and wait for the node to join
  331 |   hosts: "{{ target_cluster | default('ocp') }}"
  332 |   connection: local
  333 |   gather_facts: false
  334 |   vars:
  335 |     worker: "{{ vm_worker | default('truenas-w1.igou.systems', true) }}"
  336 |     join_timeout_minutes: 30
  337 |   tasks:
  338 | 
  339 |     - name: End play — nothing to provision (destroy mode or node already joined)
  340 |       ansible.builtin.meta: end_play
  341 |       when: >-
  342 |         vm_worker_state | default('rebuild', true) == 'destroy'
  343 |         or _worker_joined | default(false)
  344 | 
  345 |     - name: Approve this node's pending CSRs and probe readiness
  346 |       # Scoped approval only. Kubelet serving CSRs carry the node in
  347 |       # spec.username (system:node:<worker>). Bootstrapper client CSRs
  348 |       # all arrive as the shared node-bootstrapper SA with no node
  349 |       # identity in the requestor, so the CSR subject CN inside
  350 |       # spec.request is decoded and must name this worker — a pending
  351 |       # CSR from some other joining node is never approved.
  352 |       ansible.builtin.shell: |
  353 |         set -o pipefail
  354 |         approve=""
  355 |         while read -r name user; do
  356 |           [ -z "$name" ] && continue
  357 |           if [ "$user" = "system:node:{{ worker }}" ] \
  358 |              || [ "$user" = "system:node:{{ worker.split('.') | first }}" ]; then
  359 |             approve="$approve $name"
  360 |           elif [ "$user" = "system:serviceaccount:openshift-machine-config-operator:node-bootstrapper" ]; then
  361 |             subject=$(oc get csr "$name" -o jsonpath='{.spec.request}' | base64 -d | openssl req -noout -subject)
  362 |             case "$subject" in
  363 |               *"system:node:{{ worker }}"* | *"system:node:{{ worker.split('.') | first }}"*)
  364 |                 approve="$approve $name" ;;
  365 |             esac
  366 |           fi
  367 |         done <<EOF
  368 |         $(oc get csr -o go-template='{% raw %}{{range .items}}{{if not .status.conditions}}{{.metadata.name}} {{.spec.username}}{{"\n"}}{{end}}{{end}}{% endraw %}')
  369 |         EOF
  370 |         if [ -n "$approve" ]; then
  371 |           oc adm certificate approve $approve
  372 |         fi
  373 |         for n in {{ worker }} {{ worker.split('.') | first }}; do
  374 |           if [ "$(oc get node "$n" -o jsonpath='{range .status.conditions[?(@.type=="Ready")]}{.status}{end}' 2>/dev/null)" = "True" ]; then
  375 |             echo JOINED-READY
  376 |             break
  377 |           fi
  378 |         done
  379 |       args:
  380 |         executable: /bin/bash
  381 |       register: _join
  382 |       until: "'JOINED-READY' in _join.stdout"
  383 |       retries: "{{ join_timeout_minutes | int * 2 }}"
  384 |       delay: 30
  385 |       changed_when: "'approved' in _join.stdout"
  386 | 
  387 | - name: Restore the netboot RAW to its steady-state boot order
  388 |   hosts: truenas
  389 |   gather_facts: false
  390 |   vars:
  391 |     worker: "{{ vm_worker | default('truenas-w1.igou.systems', true) }}"
  392 |   tasks:
  393 | 
  394 |     - name: End play — nothing to provision (destroy mode or node already joined)
  395 |       ansible.builtin.meta: end_play
  396 |       when: >-
  397 |         vm_worker_state | default('rebuild', true) == 'destroy'
  398 |         or hostvars[target_cluster | default('ocp')]._worker_joined | default(false)
  399 | 
  400 |     - name: Resolve the VM definition for this worker
  401 |       ansible.builtin.set_fact:
  402 |         _vm_def: >-
  403 |           {{ (truenas_vms | selectattr('openshift_node', 'defined')
  404 |               | selectattr('openshift_node', 'equalto', worker)
  405 |               | list + [{}]) | first }}
  406 | 
  407 |     - name: Query the VM
  408 |       ansible.builtin.command:
  409 |         argv:
  410 |           - midclt
  411 |           - call
  412 |           - vm.query
  413 |           - "{{ [['name', '=', _vm_def.name]] | to_json }}"
  414 |       register: _vmq
  415 |       changed_when: false
  416 | 
  417 |     - name: Query the VM's devices
  418 |       ansible.builtin.command:
  419 |         argv:
  420 |           - midclt
  421 |           - call
  422 |           - vm.device.query
  423 |           - "{{ [['vm', '=', (_vmq.stdout | from_json | first).id]] | to_json }}"
  424 |       register: _devq
  425 |       changed_when: false
  426 | 
  427 |     - name: Restore demoted netboot RAW devices to order 1004
  428 |       ansible.builtin.command:
  429 |         argv:
  430 |           - midclt
  431 |           - call
  432 |           - vm.device.update
  433 |           - "{{ item.id }}"
  434 |           # See the demote task: partial updates must resend RAW
  435 |           # attributes with exists=true or 25.10 validation rejects.
  436 |           - >-
  437 |             {{ {'order': 1004,
  438 |                 'attributes': item.attributes | combine({'exists': true})}
  439 |                | to_json }}
  440 |       loop: >-
  441 |         {{ _devq.stdout | from_json
  442 |            | selectattr('attributes.dtype', 'defined')
  443 |            | selectattr('attributes.dtype', 'equalto', 'RAW')
  444 |            | selectattr('order', 'equalto', 1006) | list }}
  445 |       loop_control:
  446 |         label: "device {{ item.id }}"
  447 |       changed_when: true
  448 | 
  449 |     - name: Report result
  450 |       ansible.builtin.debug:
  451 |         msg: >-
  452 |           {{ worker }} rejoined and Ready; netboot RAW restored to its
  453 |           steady-state boot order. The add-node ISO remains attached but
  454 |           is NOT a usable reinstall path (its embedded ignition token
  455 |           expires within ~24h) — rerun this playbook to rebuild again.
  456 |           Deliberately NOT validated here: storage smoke tests — run one
  457 |           manually once the democratic-csi driver migration completes.
```

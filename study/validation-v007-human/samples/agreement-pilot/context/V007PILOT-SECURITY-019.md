# Frozen source context: V007PILOT-SECURITY-019

- Repository: `igou-io/igou-ansible`
- Commit: `5dac3e63735e0e15407c172e0abd56d431fe4e47`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `playbooks/kubevirt/test_netboot_pxe/test_netboot_pxe.yml` (reported anchor line 202)
- Object: `task` `66d1e9ccb2bfbeba6b4252dcaa1f5dc77297317e65cc07cc34581d06b0ddc883`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–303 of 303:

```text
    1 | ---
    2 | # Smoke-test the netboot.xyz custom binaries by spinning up diskless
    3 | # KubeVirt VMs (DHCP from rb5009) for each entry in pxe_test_arches
    4 | # and asserting that the matching binary's TFTP hit counter on the
    5 | # router increments. Catches regressions in the DHCP -> TFTP path that
    6 | # deploy_netboot_binaries.yml wires up.
    7 | #
    8 | # Per-entry fields (see pxe_test_arches below) override the playbook
    9 | # defaults, so a single run can mix architectures, firmware modes,
   10 | # CUDNs, MACs, and per-VM wait windows.
   11 | #
   12 | # Verification (two layers):
   13 | #   * TFTP hit counter on rb5009 increments for the expected bootstrap
   14 | #     iPXE binary (catches DHCP / matcher / TFTP regressions on rb5009).
   15 | #   * rb5009 /ip tftp hit counter for the per-host pin filename either
   16 | #     increments by 1 (pinned MAC: 'sent') or shows no matching row
   17 | #     exists at all (random MAC: 'not_found'). Pin storage lives at
   18 | #     {{ netboot_pin_flash_subdir }} on rb5009 flash, registered via
   19 | #     /ip tftp rows by playbooks/netboot/deploy_assets.yml. Substring
   20 | #     assertions on deployed pin bodies catch inventory drift at
   21 | #     preflight.
   22 | #   No per-entry override fields; expectations are fully derived from
   23 | #   inventory's netboot_host_pins (see _preflight.yml + _verify_tftp.yml).
   24 | #   Namespace selector label is hardcoded to vlan9; testing CUDNs
   25 | #     in other VLANs requires the namespace to already carry the
   26 | #     matching selector label.
   27 | #
   28 | # Namespace handling: the test namespace is ensured (created with the
   29 | # vlan9 CUDN selector label if missing) but never deleted -- removing
   30 | # CUDN-attached namespaces is currently fragile, and the namespace is
   31 | # safe to leave in place between runs. Each VM IS cleaned up via the
   32 | # block's always: clause, even on assertion failure.
   33 | #
   34 | # Example: two BIOS VMs with pinned MACs, run in parallel
   35 | # (matches static DHCP leases on rb5009):
   36 | #
   37 | #   ansible-navigator run \
   38 | #     playbooks/kubevirt/test_netboot_pxe/test_netboot_pxe.yml \
   39 | #     -i igou-inventory/inventory.yaml \
   40 | #     -e '{"pxe_test_parallel": true,
   41 | #          "pxe_test_arches": [
   42 | #            {"name": "pxe-test-host-a", "arch": "bios",
   43 | #             "binary": "netboot.xyz.kpxe", "mac": "52:54:00:de:ad:01"},
   44 | #            {"name": "pxe-test-host-b", "arch": "bios",
   45 | #             "binary": "netboot.xyz.kpxe", "mac": "52:54:00:de:ad:02"}
   46 | #          ]}'
   47 | 
   48 | - name: Test netboot.xyz custom binaries via KubeVirt VM PXE boot
   49 |   hosts: localhost
   50 |   connection: local
   51 |   gather_facts: false
   52 |   vars:
   53 |     pxe_test_namespace: netboot-pxe-test
   54 |     pxe_test_router: rb5009.igou.systems
   55 |     # Defaults applied to any pxe_test_arches entry that omits the
   56 |     # corresponding key. Per-entry fields take precedence.
   57 |     pxe_test_cudn: vlan9-no-ipam
   58 |     pxe_test_firmware: bios
   59 |     pxe_test_cores: 1
   60 |     pxe_test_memory: 1Gi
   61 |     # Time to wait between VM-Ready and the post-snapshot. SeaBIOS POST
   62 |     # plus the iPXE ROM's DHCP retry loop can run 60-90s on its own,
   63 |     # before TFTP even starts; 180s gives margin without dragging the
   64 |     # full per-arch cycle past 4 minutes.
   65 |     pxe_test_boot_wait_seconds: 180
   66 |     # When false (default), each entry's create/assert/teardown runs
   67 |     # serially. When true, all VMs are applied at once, asserted in a
   68 |     # single pass, then torn down -- noticeably faster for >2 entries
   69 |     # but harder to attribute failures.
   70 |     pxe_test_parallel: false
   71 |     # Default substring to grep for in each smoke pin's served body,
   72 |     # keyed by lowercase MAC. Drives only the preflight static check;
   73 |     # per-case substring assertion is dropped because preflight already
   74 |     # validates the body. Adding a new pinned smoke entry?  Add the
   75 |     # MAC -> substring pair here.
   76 |     pxe_test_substring_defaults:
   77 |       "02:00:00:50:58:01": "pxe-test pin: bios"
   78 |       "02:00:00:50:58:02": "pxe-test pin: uefi-x64"
   79 |     # Each entry must set: arch (free-form label, used in resource
   80 |     # labels and the default name), binary (TFTP filename to watch on
   81 |     # rb5009). All other fields are optional overrides:
   82 |     #   name              VM name (default: pxe-test-<arch>; required
   83 |     #                     when multiple entries share an arch)
   84 |     #   mac               pin the NIC MAC (else KubeVirt generates one)
   85 |     #   cudn              ClusterUserDefinedNetwork (default: pxe_test_cudn)
   86 |     #   firmware          'bios' or 'efi' (default: pxe_test_firmware)
   87 |     #   cores             vCPU count (default: pxe_test_cores)
   88 |     #   memory            guest memory (default: pxe_test_memory)
   89 |     #   boot_wait_seconds wait between Ready and the post-snapshot
   90 |     #                     (default: pxe_test_boot_wait_seconds; in
   91 |     #                     parallel mode the max effective wait wins)
   92 |     # Default mix: each arch is exercised twice -- once with a
   93 |     # KubeVirt-generated MAC (random, exercises the un-pinned path
   94 |     # where the iPXE binary's :tftpmenu MAC lookup misses on rb5009
   95 |     # and the HTTPS fallback to public.igou.systems/boot-files/menu.ipxe
   96 |     # serves the unpinned-host menu) and once with a fixed MAC that
   97 |     # has a matching netboot_host_pins entry in
   98 |     # igou-inventory/group_vars/all/netboot.yml (exercises the
   99 |     # bootstrap iPXE's native per-host MAC-<hexraw>.ipxe lookup against
  100 |     # rb5009 TFTP).
  101 |     pxe_test_arches:
  102 |       - name: pxe-test-bios-random
  103 |         arch: bios
  104 |         binary: netboot.xyz.kpxe
  105 |       - name: pxe-test-bios-pinned
  106 |         arch: bios
  107 |         binary: netboot.xyz.kpxe
  108 |         mac: '02:00:00:50:58:01'
  109 |       - name: pxe-test-uefi-x64-random
  110 |         arch: uefi-x64
  111 |         binary: netboot.xyz.efi
  112 |         firmware: efi
  113 |       - name: pxe-test-uefi-x64-pinned
  114 |         arch: uefi-x64
  115 |         binary: netboot.xyz.efi
  116 |         firmware: efi
  117 |         mac: '02:00:00:50:58:02'
  118 | 
  119 |   tasks:
  120 |     - name: Preflight -- netbootxyz HTTP-side checks
  121 |       ansible.builtin.include_tasks: _preflight.yml
  122 | 
  123 |     # --- Pre-flight (idempotent, never destructive) --------------------------
  124 | 
  125 |     - name: Read each ClusterUserDefinedNetwork referenced by pxe_test_arches
  126 |       kubernetes.core.k8s_info:
  127 |         api_version: k8s.ovn.org/v1
  128 |         kind: ClusterUserDefinedNetwork
  129 |         name: "{{ item }}"
  130 |         validate_certs: false
  131 |       register: _pxe_cudn_results
  132 |       loop: "{{ pxe_test_arches | map(attribute='cudn', default=pxe_test_cudn) | list | unique }}"
  133 | 
  134 |     - name: Assert every referenced CUDN is present
  135 |       ansible.builtin.assert:
  136 |         that:
  137 |           - item.resources | length == 1
  138 |         fail_msg: >-
  139 |           ClusterUserDefinedNetwork {{ item.item }} is not present in the
  140 |           current cluster. The test cannot attach VMs to it until the
  141 |           CUDN is synced (see clusters/ocp/udn/ in igou-openshift).
  142 |       loop: "{{ _pxe_cudn_results.results }}"
  143 |       loop_control:
  144 |         label: "{{ item.item }}"
  145 | 
  146 |     - name: Ensure test namespace exists with the vlan9 CUDN selector label
  147 |       kubernetes.core.k8s:
  148 |         state: present
  149 |         validate_certs: false
  150 |         definition:
  151 |           apiVersion: v1
  152 |           kind: Namespace
  153 |           metadata:
  154 |             name: "{{ pxe_test_namespace }}"
  155 |             labels:
  156 |               network.igou.systems/vlan9: "true"
  157 | 
  158 |     # --- Per-arch smoke test -------------------------------------------------
  159 |     # Two execution modes: serial (default) iterates and tears down
  160 |     # each VM in turn; parallel applies all VMs, asserts in one pass,
  161 |     # then tears them all down. Both honour the per-entry block/always
  162 |     # cleanup contract -- in parallel mode a single block wraps the
  163 |     # whole batch, so a mid-run failure still cleans up every VM.
  164 | 
  165 |     - name: Smoke-test architectures serially
  166 |       ansible.builtin.include_tasks: _arch_test.yml
  167 |       loop: "{{ pxe_test_arches }}"
  168 |       loop_control:
  169 |         label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  170 |       when: not (pxe_test_parallel | bool)
  171 | 
  172 |     - name: Smoke-test architectures in parallel
  173 |       when: pxe_test_parallel | bool
  174 |       block:
  175 |         - name: Snapshot rb5009 TFTP hits BEFORE boot (all, binary)
  176 |           community.routeros.command:
  177 |             commands:
  178 |               - >-
  179 |                 /ip tftp print detail without-paging where
  180 |                 req-filename="{{ item.binary }}"
  181 |           register: _pxe_tftp_pre_all
  182 |           changed_when: false
  183 |           delegate_to: "{{ pxe_test_router }}"
  184 |           loop: "{{ pxe_test_arches }}"
  185 |           loop_control:
  186 |             label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  187 | 
  188 |         - name: Snapshot rb5009 pin hits BEFORE boot (all, per pin MAC)
  189 |           community.routeros.command:
  190 |             commands:
  191 |               - >-
  192 |                 /ip tftp print detail without-paging where
  193 |                 req-filename="MAC-{{ (item.mac | default('00:00:00:00:00:00')) | regex_replace(':', '') | lower }}.ipxe"
  194 |           register: _pxe_pin_tftp_pre_all
  195 |           changed_when: false
  196 |           delegate_to: "{{ pxe_test_router }}"
  197 |           loop: "{{ pxe_test_arches }}"
  198 |           loop_control:
  199 |             label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  200 | 
  201 |         - name: Apply all diskless PXE-boot VMs (no per-VM wait)
  202 |           kubernetes.core.k8s:
  203 |             state: present
  204 |             validate_certs: false
  205 |             namespace: "{{ pxe_test_namespace }}"
  206 |             definition: "{{ lookup('ansible.builtin.template', 'vm.yaml.j2') | from_yaml }}"
  207 |             wait: false
  208 |           loop: "{{ pxe_test_arches }}"
  209 |           loop_control:
  210 |             label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  211 | 
  212 |         - name: Wait for all VMs to reach Ready
  213 |           kubernetes.core.k8s_info:
  214 |             api_version: kubevirt.io/v1
  215 |             kind: VirtualMachine
  216 |             namespace: "{{ pxe_test_namespace }}"
  217 |             name: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  218 |             validate_certs: false
  219 |             wait: true
  220 |             wait_condition:
  221 |               type: Ready
  222 |               status: "True"
  223 |             wait_timeout: 180
  224 |           loop: "{{ pxe_test_arches }}"
  225 |           loop_control:
  226 |             label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  227 | 
  228 |         - name: Resolve VM addressing for every VM (parallel)
  229 |           ansible.builtin.include_tasks: _dhcp_lease_lookup.yml
  230 |           vars:
  231 |             _vm_name: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  232 |           loop: "{{ pxe_test_arches }}"
  233 |           loop_control:
  234 |             label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  235 | 
  236 |         - name: Pause to let iPXE complete its boot attempts (longest effective wait)
  237 |           ansible.builtin.pause:
  238 |             seconds: >-
  239 |               {{ pxe_test_arches
  240 |                  | map(attribute='boot_wait_seconds', default=pxe_test_boot_wait_seconds)
  241 |                  | map('int') | max }}
  242 | 
  243 |         - name: Snapshot rb5009 TFTP hits AFTER boot (all)
  244 |           community.routeros.command:
  245 |             commands:
  246 |               - >-
  247 |                 /ip tftp print detail without-paging where
  248 |                 req-filename="{{ item.binary }}"
  249 |           register: _pxe_tftp_post_all
  250 |           changed_when: false
  251 |           delegate_to: "{{ pxe_test_router }}"
  252 |           loop: "{{ pxe_test_arches }}"
  253 |           loop_control:
  254 |             label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  255 | 
  256 |         - name: Assert TFTP hits incremented for each binary
  257 |           ansible.builtin.assert:
  258 |             that:
  259 |               - (_pxe_post_hits | int) > (_pxe_pre_hits | int)
  260 |             fail_msg: >-
  261 |               VM {{ item.0.item.name | default('pxe-test-' ~ item.0.item.arch) }}
  262 |               did not fetch {{ item.0.item.binary }} from rb5009. hits
  263 |               {{ _pxe_pre_hits }} -> {{ _pxe_post_hits }}. Check the VMI
  264 |               status, the DHCP offer to its MAC (`/log print where
  265 |               topics~"dhcp"` on rb5009), and that the matcher table
  266 |               still routes option-93 to the right binary.
  267 |           vars:
  268 |             _pxe_pre_hits: "{{ item.0.stdout[0] | regex_search('hits=\\d+') | default('hits=0') | regex_replace('^hits=', '') | int }}"
  269 |             _pxe_post_hits: "{{ item.1.stdout[0] | regex_search('hits=\\d+') | default('hits=0') | regex_replace('^hits=', '') | int }}"
  270 |           loop: "{{ _pxe_tftp_pre_all.results | zip(_pxe_tftp_post_all.results) | list }}"
  271 |           loop_control:
  272 |             label: "{{ item.0.item.name | default('pxe-test-' ~ item.0.item.arch) }}"
  273 | 
  274 |         - name: Verify TFTP dispatch for every VM (parallel)
  275 |           ansible.builtin.include_tasks: _verify_tftp.yml
  276 |           vars:
  277 |             _vm_name_inner: "{{ item.0.name | default('pxe-test-' ~ item.0.arch) }}"
  278 |             vm_name: "{{ _vm_name_inner }}"
  279 |             vm_mac: "{{ _pxe_vm_addr_map[_vm_name_inner].mac }}"
  280 |             expected_outcome: "{{ 'sent' if (_pxe_vm_addr_map[_vm_name_inner].mac in _pxe_pinned_macs) else 'not_found' }}"
  281 |             tftp_hits_pre: >-
  282 |               {{ (item.1.stdout[0] | default(''))
  283 |                  | regex_search('hits=\d+') | default('hits=0')
  284 |                  | regex_replace('^hits=', '') | int }}
  285 |           loop: "{{ pxe_test_arches | zip(_pxe_pin_tftp_pre_all.results) | list }}"
  286 |           loop_control:
  287 |             label: "{{ item.0.name | default('pxe-test-' ~ item.0.arch) }}"
  288 | 
  289 |       always:
  290 |         - name: Delete all test VMs
  291 |           when: not (pxe_test_keep_vms | default(false) | bool)
  292 |           kubernetes.core.k8s:
  293 |             state: absent
  294 |             api_version: kubevirt.io/v1
  295 |             kind: VirtualMachine
  296 |             namespace: "{{ pxe_test_namespace }}"
  297 |             name: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
  298 |             validate_certs: false
  299 |             wait: true
  300 |             wait_timeout: 120
  301 |           loop: "{{ pxe_test_arches }}"
  302 |           loop_control:
  303 |             label: "{{ item.name | default('pxe-test-' ~ item.arch) }}"
```

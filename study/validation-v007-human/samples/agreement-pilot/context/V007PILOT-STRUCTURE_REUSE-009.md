# Frozen source context: V007PILOT-STRUCTURE_REUSE-009

- Repository: `igou-io/igou-ansible`
- Commit: `5dac3e63735e0e15407c172e0abd56d431fe4e47`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `playbooks/routeros/tasks/netboot_upload.yml` (reported anchor line 1)
- Object: `source_location` `754019391af6fdbb300a8ca6268db906eecd0234c6f5023b146a9eb414a474be`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–236 of 236:

```text
    1 | ---
    2 | # Ship built iPXE binaries from the control node's build cache to
    3 | # flash:/netboot/ on the rb5009, then register each in /ip tftp so
    4 | # PXE clients can fetch them by their public names.
    5 | #
    6 | # Honors netboot_arches_resolved (set by netboot_build.yml). When this
    7 | # stage runs alone via --tags upload, the fact is recomputed from
    8 | # netboot_arches and the static arches map.
    9 | 
   10 | - name: Recompute arches map if running upload stage alone
   11 |   ansible.builtin.set_fact:
   12 |     _netboot_arches_map:
   13 |       bios:
   14 |         local_name: netboot.xyz.kpxe
   15 |         public_name: netboot.xyz.kpxe
   16 |       uefi-x64:
   17 |         # snponly flavor: the full-driver ipxe.efi attaches native USB
   18 |         # host-controller drivers (iPXE 2161e976) that kill USB keyboards
   19 |         # on AMI-based UEFI firmware; snponly carries no native drivers.
   20 |         # public_name stays netboot.xyz.efi (DHCP boot-file-name, /ip
   21 |         # tftp rows, and matchers are keyed on it). Must match the map in
   22 |         # tasks/netboot_build.yml.
   23 |         local_name: netboot.xyz-snponly.efi
   24 |         public_name: netboot.xyz.efi
   25 |       uefi-arm64:
   26 |         local_name: netboot.xyz-arm64.efi
   27 |         public_name: netboot.xyz-arm64.efi
   28 |   when: netboot_arches_resolved is not defined
   29 | 
   30 | - name: Recompute resolved arches list if running upload stage alone
   31 |   ansible.builtin.set_fact:
   32 |     netboot_arches_resolved: >-
   33 |       {{
   34 |         netboot_arches | map('extract', _netboot_arches_map) | list
   35 |       }}
   36 |   when: netboot_arches_resolved is not defined
   37 | 
   38 | - name: Stat each local binary
   39 |   ansible.builtin.stat:
   40 |     path: "{{ netboot_local_build_dir }}/output/ipxe/{{ item.local_name }}"
   41 |     checksum_algorithm: sha256
   42 |   delegate_to: localhost
   43 |   loop: "{{ netboot_arches_resolved }}"
   44 |   loop_control:
   45 |     label: "{{ item.public_name }}"
   46 |   register: _netboot_local_stat
   47 | 
   48 | - name: Assert each local binary exists
   49 |   ansible.builtin.assert:
   50 |     that:
   51 |       - item.stat.exists
   52 |     fail_msg: >-
   53 |       Local binary
   54 |       {{ netboot_local_build_dir }}/output/ipxe/{{ item.item.local_name }}
   55 |       is missing. Run the build stage first
   56 |       (--tags build).
   57 |   loop: "{{ _netboot_local_stat.results }}"
   58 |   loop_control:
   59 |     label: "{{ item.item.public_name }}"
   60 | 
   61 | - name: Count flash netboot directory
   62 |   community.routeros.command:
   63 |     commands:
   64 |       - '/file print count-only where name="{{ netboot_flash_dir }}" and type=directory'
   65 |   register: _netboot_flash_dir_count
   66 |   changed_when: false
   67 | 
   68 | - name: Create flash netboot directory
   69 |   community.routeros.command:
   70 |     commands:
   71 |       - "/file add name={{ netboot_flash_dir }} type=directory"
   72 |   when: (_netboot_flash_dir_count.stdout[0] | trim | int) == 0
   73 |   changed_when: true
   74 | 
   75 | # Compare local SHA256 against a sidecar .sha256 file on rb5009 (uploaded
   76 | # alongside each binary). Size-only is not enough: iPXE outputs are
   77 | # sector-padded, so a rebuild with a different embedded boot_domain can
   78 | # produce a byte-size-identical binary whose content differs (see the
   79 | # 2026-05-11 .efi staleness incident). The :do { } on-error={ } wrapper
   80 | # treats a missing sidecar as empty content -> always uploads, which
   81 | # also recovers gracefully on first run after this fix.
   82 | 
   83 | - name: Read router-side SHA256 sidecar for each binary
   84 |   community.routeros.command:
   85 |     commands:
   86 |       - >-
   87 |         :do { :put [/file get
   88 |         [find where name="{{ netboot_flash_dir }}/{{ item.public_name }}.sha256"]
   89 |         contents] } on-error={ :put "" }
   90 |   register: _netboot_router_sha256
   91 |   changed_when: false
   92 |   loop: "{{ netboot_arches_resolved }}"
   93 |   loop_control:
   94 |     label: "{{ item.public_name }}.sha256"
   95 | 
   96 | - name: Render local SHA256 sidecar alongside each binary
   97 |   ansible.builtin.copy:
   98 |     content: "{{ item.stat.checksum }}\n"
   99 |     dest: "{{ netboot_local_build_dir }}/output/ipxe/{{ item.item.local_name }}.sha256"
  100 |     mode: "0644"
  101 |   delegate_to: localhost
  102 |   loop: "{{ _netboot_local_stat.results }}"
  103 |   loop_control:
  104 |     label: "{{ item.item.public_name }}.sha256"
  105 | 
  106 | - name: Upload binary when local SHA256 differs from router sidecar
  107 |   ansible.netcommon.net_put:
  108 |     src: "{{ netboot_local_build_dir }}/output/ipxe/{{ item.0.local_name }}"
  109 |     dest: "{{ netboot_flash_dir }}/{{ item.0.public_name }}"
  110 |   vars:
  111 |     ansible_command_timeout: 300
  112 |     _local_hash: "{{ item.1.stat.checksum }}"
  113 |     _router_hash: >-
  114 |       {{ (_netboot_router_sha256.results[ansible_loop.index0].stdout[0]
  115 |           | default('')) | trim }}
  116 |   when: _local_hash != _router_hash
  117 |   loop: "{{ netboot_arches_resolved | zip(_netboot_local_stat.results) | list }}"
  118 |   loop_control:
  119 |     label: "{{ item.0.public_name }}"
  120 |     extended: true
  121 |   register: _netboot_uploads
  122 | 
  123 | - name: Upload SHA256 sidecar after binary upload
  124 |   ansible.netcommon.net_put:
  125 |     src: "{{ netboot_local_build_dir }}/output/ipxe/{{ item.0.local_name }}.sha256"
  126 |     dest: "{{ netboot_flash_dir }}/{{ item.0.public_name }}.sha256"
  127 |   vars:
  128 |     ansible_command_timeout: 30
  129 |     _local_hash: "{{ item.1.stat.checksum }}"
  130 |     _router_hash: >-
  131 |       {{ (_netboot_router_sha256.results[ansible_loop.index0].stdout[0]
  132 |           | default('')) | trim }}
  133 |   when: _local_hash != _router_hash
  134 |   loop: "{{ netboot_arches_resolved | zip(_netboot_local_stat.results) | list }}"
  135 |   loop_control:
  136 |     label: "{{ item.0.public_name }}.sha256"
  137 |     extended: true
  138 | 
  139 | - name: Count tftp rows for each arch
  140 |   community.routeros.command:
  141 |     commands:
  142 |       - >-
  143 |         /ip tftp print count-only where
  144 |         req-filename="{{ item.public_name }}" and
  145 |         real-filename="{{ netboot_flash_dir }}/{{ item.public_name }}"
  146 |   register: _netboot_tftp_count
  147 |   changed_when: false
  148 |   loop: "{{ netboot_arches_resolved }}"
  149 |   loop_control:
  150 |     label: "{{ item.public_name }}"
  151 | 
  152 | - name: Add /ip tftp row for each arch
  153 |   community.routeros.command:
  154 |     commands:
  155 |       - >-
  156 |         /ip tftp add
  157 |         req-filename="{{ item.public_name }}"
  158 |         real-filename="{{ netboot_flash_dir }}/{{ item.public_name }}"
  159 |         allow=yes read-only=yes
  160 |   when: (_netboot_tftp_count.results[ansible_loop.index0].stdout[0] | trim | int) == 0
  161 |   changed_when: true
  162 |   loop: "{{ netboot_arches_resolved }}"
  163 |   loop_control:
  164 |     label: "{{ item.public_name }}"
  165 |     extended: true
  166 | 
  167 | # --- menu.ipxe TFTP redirect ----------------------------------------------
  168 | # The embedded boot script in our binaries (templates/disks/netboot.xyz.j2
  169 | # upstream) tries `tftp://${tftp-server}/menu.ipxe` first; only when that
  170 | # fails does it fall through to https/http://${boot_domain}/menu.ipxe.
  171 | # Serving this tiny redirect from rb5009 makes the first TFTP attempt
  172 | # succeed and chain straight to the real menu on the public nginx —
  173 | # skipping the autoexec's slower retry ladder. The chain target MUST be
  174 | # {{ netboot_chainload_proto }}:// (https): the public nginx serves
  175 | # HTTP/HTTPS only, no TFTP listener. A tftp:// target here (pre-2026-07
  176 | # regression, left over from the retired TrueNAS netbootxyz container)
  177 | # black-holes into a UDP timeout on every fallback-menu fetch.
  178 | 
  179 | - name: Render menu.ipxe redirect locally
  180 |   ansible.builtin.copy:
  181 |     content: |
  182 |       #!ipxe
  183 |       # Generated by playbooks/routeros/tasks/netboot_upload.yml.
  184 |       # Redirects rb5009-served menu.ipxe TFTP requests to the real
  185 |       # fallback menu on the public nginx, so the binaries' embedded
  186 |       # TFTP-first chainload short-circuits before the autoexec's
  187 |       # https/http retry rounds.
  188 |       chain {{ netboot_chainload_proto }}://{{ netboot_chainload_host }}/menu.ipxe
  189 |     dest: "{{ netboot_local_build_dir }}/menu.ipxe"
  190 |     mode: "0644"
  191 |   delegate_to: localhost
  192 | 
  193 | - name: Stat local menu.ipxe redirect
  194 |   ansible.builtin.stat:
  195 |     path: "{{ netboot_local_build_dir }}/menu.ipxe"
  196 |   delegate_to: localhost
  197 |   register: _netboot_menu_local_stat
  198 | 
  199 | - name: Count router-side menu.ipxe matching local size
  200 |   community.routeros.command:
  201 |     commands:
  202 |       - >-
  203 |         /file print count-only where
  204 |         name="{{ netboot_flash_dir }}/menu.ipxe"
  205 |         and size={{ _netboot_menu_local_stat.stat.size }}
  206 |   register: _netboot_menu_size_match
  207 |   changed_when: false
  208 | 
  209 | - name: Upload menu.ipxe redirect if size differs
  210 |   ansible.netcommon.net_put:
  211 |     src: "{{ netboot_local_build_dir }}/menu.ipxe"
  212 |     dest: "{{ netboot_flash_dir }}/menu.ipxe"
  213 |   vars:
  214 |     ansible_command_timeout: 60
  215 |   when: (_netboot_menu_size_match.stdout[0] | trim | int) == 0
  216 | 
  217 | - name: Count tftp rows for menu.ipxe redirect
  218 |   community.routeros.command:
  219 |     commands:
  220 |       - >-
  221 |         /ip tftp print count-only where
  222 |         req-filename="menu.ipxe" and
  223 |         real-filename="{{ netboot_flash_dir }}/menu.ipxe"
  224 |   register: _netboot_menu_tftp_count
  225 |   changed_when: false
  226 | 
  227 | - name: Add /ip tftp row for menu.ipxe redirect
  228 |   community.routeros.command:
  229 |     commands:
  230 |       - >-
  231 |         /ip tftp add
  232 |         req-filename="menu.ipxe"
  233 |         real-filename="{{ netboot_flash_dir }}/menu.ipxe"
  234 |         allow=yes read-only=yes
  235 |   when: (_netboot_menu_tftp_count.stdout[0] | trim | int) == 0
  236 |   changed_when: true
```

## Frozen tracked paths in the relevant role/scope

```text
.ansible-lint
.gitattributes
.github/workflows/dependency-review.yml
.github/workflows/ee-build.yml
.github/workflows/igou-awx-ee-build.yml
.github/workflows/lint.yml
.github/workflows/scorecard.yml
.github/workflows/syntax-check.yml
.gitignore
.pre-commit-config.yaml
.tekton/README.md
.tekton/igou-aap-ee-rhel9-push.yml
.tekton/tasks/ansible-builder-task.yml
.tekton/tasks/buildah-galaxy-task.yml
.yamllint.yml
AGENTS.md
CLAUDE.md
Makefile
README.md
ansible-navigator.yml
ansible.cfg
docs/README.md
docs/armbian-boot-modes.md
docs/disaster-recovery.md
docs/examples/routeros_deploy_nginx_hello.yml
docs/execution-environments.md
docs/hermes-agent-runtime.md
docs/hermes-vm-lifecycle.md
docs/netboot-operations.md
docs/openshift-operations.md
docs/rpi-netboot-operations.md
docs/superpowers/plans/2026-05-06-openshift-add-node-iso-inventory.md
docs/superpowers/plans/2026-05-06-openshift-add-node-iso-netboot.md
docs/superpowers/plans/2026-05-07-routeros-playbooks.md
docs/superpowers/plans/2026-05-07-routeros-smoketest.md
docs/superpowers/plans/2026-05-08-netboot-asset-management.md
docs/superpowers/plans/2026-05-08-netboot-binaries-build.md
docs/superpowers/plans/2026-05-09-add-node-iso-host-pin-layout.md
docs/superpowers/plans/2026-05-09-test-netboot-pxe-headless.md
docs/superpowers/plans/2026-05-20-tekton-aap-ee-rhel9.md
docs/superpowers/plans/2026-05-21-aap-configuration-repeatability.md
docs/superpowers/plans/2026-05-22-aap-kubevirt-management.md
docs/superpowers/plans/2026-05-30-armbian-collection-consumption.md
docs/superpowers/plans/2026-06-02-routeros-declarative-firewall.md
docs/superpowers/plans/2026-06-03-routeros-firewall-enforce.md
docs/superpowers/specs/2026-05-06-openshift-add-node-iso-netboot-design.md
docs/superpowers/specs/2026-05-07-routeros-playbooks-design.md
docs/superpowers/specs/2026-05-07-routeros-smoketest-design.md
docs/superpowers/specs/2026-05-08-netboot-asset-management-design.md
docs/superpowers/specs/2026-05-08-netboot-binaries-build-design.md
docs/superpowers/specs/2026-05-09-add-node-iso-host-pin-layout-design.md
docs/superpowers/specs/2026-05-09-test-netboot-pxe-headless-design.md
docs/superpowers/specs/2026-05-20-tekton-aap-ee-rhel9-design.md
docs/superpowers/specs/2026-05-21-aap-configuration-design.md
docs/superpowers/specs/2026-05-22-aap-kubevirt-management-design.md
docs/superpowers/specs/2026-05-30-armbian-collection-consumption-design.md
docs/superpowers/specs/2026-06-02-routeros-declarative-firewall-design.md
docs/superpowers/specs/2026-06-03-routeros-firewall-enforce-design.md
docs/troubleshooting.md
docs/truenas-operations.md
docs/vps-lifecycle.md
execution-environments/igou-aap-ee-rhel9/execution-environment.yml
execution-environments/igou-aap-ee-rhel9/requirements.txt
execution-environments/igou-awx-ee/execution-environment.yml
execution-environments/igou-awx-ee/requirements.txt
hack/README.md
hack/ao-export.sh
hack/pac-sim.sh
molecule/README.md
molecule/default/converge.yml
molecule/default/create.yml
molecule/default/destroy.yml
molecule/default/molecule.yml
molecule/default/verify.yml
molecule/logic-kubevirt-vm-snapshot/converge.yml
molecule/logic-kubevirt-vm-snapshot/molecule.yml
molecule/logic-kubevirt-vm-snapshot/verify.yml
molecule/playbook-devenv-bootstrap/collections.yml
molecule/playbook-devenv-bootstrap/converge.yml
molecule/playbook-devenv-bootstrap/create.yml
molecule/playbook-devenv-bootstrap/destroy.yml
molecule/playbook-devenv-bootstrap/files/envs/molecule-bad.env
molecule/playbook-devenv-bootstrap/files/envs/molecule-k8s-token.env
molecule/playbook-devenv-bootstrap/files/envs/molecule-kubeconfig.env
molecule/playbook-devenv-bootstrap/files/envs/molecule-registry.env
molecule/playbook-devenv-bootstrap/files/envs/molecule-simple.env
molecule/playbook-devenv-bootstrap/inventory/group_vars/devenv.yml
molecule/playbook-devenv-bootstrap/inventory/group_vars/molecule.yml
molecule/playbook-devenv-bootstrap/inventory/hosts.yml
molecule/playbook-devenv-bootstrap/molecule.yml
molecule/playbook-devenv-bootstrap/prepare.yml
molecule/playbook-devenv-bootstrap/verify.yml
molecule/playbook-grafana-kiosk/collections.yml
molecule/playbook-grafana-kiosk/converge.yml
molecule/playbook-grafana-kiosk/create.yml
molecule/playbook-grafana-kiosk/destroy.yml
molecule/playbook-grafana-kiosk/inventory/group_vars/grafana_kiosk.yml
molecule/playbook-grafana-kiosk/inventory/group_vars/molecule.yml
molecule/playbook-grafana-kiosk/inventory/hosts.yml
molecule/playbook-grafana-kiosk/molecule.yml
molecule/playbook-grafana-kiosk/prepare.yml
molecule/playbook-grafana-kiosk/prepare_mock.yml
molecule/playbook-grafana-kiosk/verify.yml
molecule/playbook-truenas-configure_docker_containers/collections.yml
molecule/playbook-truenas-configure_docker_containers/converge.yml
molecule/playbook-truenas-configure_docker_containers/create.yml
molecule/playbook-truenas-configure_docker_containers/destroy.yml
molecule/playbook-truenas-configure_docker_containers/files/midclt.py
molecule/playbook-truenas-configure_docker_containers/inventory/group_vars/molecule.yml
molecule/playbook-truenas-configure_docker_containers/inventory/group_vars/truenas.yml
molecule/playbook-truenas-configure_docker_containers/inventory/hosts.yml
molecule/playbook-truenas-configure_docker_containers/molecule.yml
molecule/playbook-truenas-configure_docker_containers/prepare.yml
molecule/playbook-truenas-configure_docker_containers/verify.yml
molecule/playbook-windows-build_golden_image/README.md
molecule/playbook-windows-build_golden_image/converge.yml
molecule/playbook-windows-build_golden_image/create.yml
molecule/playbook-windows-build_golden_image/destroy.yml
molecule/playbook-windows-build_golden_image/molecule.yml
molecule/playbook-windows-build_golden_image/verify.yml
[listing truncated after 120 paths]
```

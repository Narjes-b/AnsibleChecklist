# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-035

- Repository: `silogen/cluster-bloom`
- Commit: `6122fdec7e1e0feed6081e46be0e44cd45d08809`
- Family: Maintainability/complexity
- Rule: `ansibleguard/unused-handler`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `pkg/ansible/runtime/playbooks/cluster-bloom.yaml` (reported anchor line 236)
- Object: `source_location` `f303924ace1e473064e9cf849de02d64301d255fd9eefdcb105bdd4cb1f5a846`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–292 of 292:

```text
    1 | ---
    2 | - name: Cluster Bloom - RKE2 Kubernetes Cluster Setup
    3 |   hosts: all
    4 |   become: yes
    5 |   gather_facts: false
    6 |   gather_subset:
    7 |     - min
    8 |     - network
    9 |   vars:
   10 |     # * * * * * * * * * * * * * 
   11 |     ### CLUSTERFORGE_RELEASE - SET THIS VALUE IN pkg/config/bloom.yaml.schema.yaml
   12 |     # * * * * * * * * * * * * *
   13 |     FIRST_NODE: true
   14 |     GPU_NODE: true
   15 |     CONTROL_PLANE: false
   16 |     DOMAIN: ""
   17 |     CLUSTER_SIZE: medium
   18 |     SERVER_IP: ""
   19 |     JOIN_TOKEN: [REDACTED VALUE BLOCK]
   20 |     NO_DISKS_FOR_CLUSTER: false
   21 |     CLUSTER_DISKS: ""
   22 |     CLUSTER_PREMOUNTED_DISKS: ""
   23 |     USE_CERT_MANAGER: false
   24 |     CERT_OPTION: ""
   25 |     TLS_CERT: ""
   26 |     TLS_KEY: ""
   27 |     ADDITIONAL_OIDC_PROVIDERS: []
   28 |     ADDITIONAL_TLS_SAN_URLS: []
   29 |     RKE2_VERSION: ""
   30 |     RKE2_EXTRA_CONFIG: ""
   31 |     
   32 |     # DNS Configuration (opt-in for safety)
   33 |     # FIX_DNS: Set to true to allow automatic DNS fixes if DNS is broken
   34 |     #          Only modifies /etc/resolv.conf if DNS tests fail AND external DNS works
   35 |     #          Creates backups before modification with automatic rollback on failure
   36 |     #          WARNING: Will overwrite /etc/resolv.conf if DNS is detected as broken
   37 |     FIX_DNS: false
   38 | 
   39 |     # PAUSE_K3S: Legacy force flag; k3s conflicts are paused automatically by default.
   40 |     # Set SKIP_K3S_PAUSE: true to fail instead of auto-pausing on loaned nodes.
   41 |     PAUSE_K3S: false
   42 |     SKIP_K3S_PAUSE: false
   43 |     RKE2_PRESERVE_EXISTING: false
   44 |     
   45 |     # DNS_SERVERS: Custom DNS servers for RKE2 cluster
   46 |     #              If set, these nameservers will be written to /etc/rancher/rke2/resolv.conf
   47 |     #              instead of copying host DNS. Format as YAML list (e.g., ["8.8.8.8", "1.1.1.1"])
   48 |     DNS_SERVERS: []
   49 |     
   50 |     CLUSTERFORGE_REPO: "https://github.com/silogen/cluster-forge.git"
   51 |     BLOOM_DIR: "/tmp/bloom"
   52 |     # Controller/login user that should own user-facing Bloom output. This
   53 |     # resolves to the pre-sudo user when ansible-playbook itself runs via sudo,
   54 |     # and to USER for normal local/exported execution.
   55 |     bloom_effective_user: >-
   56 |       {{
   57 |         lookup('env', 'SUDO_USER')
   58 |         | default(lookup('env', 'USER'), true)
   59 |         | default(ansible_user | default(ansible_user_id | default('root'), true), true)
   60 |       }}
   61 |     # EAI-5657: exact driver compatibility policy. These play-level defaults
   62 |     # also support direct ansible-playbook use when Bloom's Go layer is bypassed.
   63 |     GPU_INSTALL_HOST_TOOLS: true
   64 |     gpu_driver_default_version: "31.40"
   65 |     gpu_driver_default_build: "314000-1"
   66 |     gpu_driver_supported:
   67 |       - DriverRelease: "30.10.2"
   68 |         InstallerVersion: "7.0.2"
   69 |         InstallerBuild: "70002-1"
   70 |         DKMSModuleVersion: "6.14.14"
   71 |         DKMSBuild: "2226257"
   72 |         DKMSPackageCode: "30100200"
   73 |         PairedROCm: "7.0.2"
   74 |         HostToolsChannel: legacy
   75 |         HostToolsPackage: amd-smi-lib
   76 |       - DriverRelease: "30.20.1"
   77 |         InstallerVersion: "7.1.1"
   78 |         InstallerBuild: "70101-1"
   79 |         DKMSModuleVersion: "6.16.6"
   80 |         DKMSBuild: "2255209"
   81 |         DKMSPackageCode: "30200100"
   82 |         PairedROCm: "7.1.1"
   83 |         HostToolsChannel: legacy
   84 |         HostToolsPackage: amd-smi-lib
   85 |       - DriverRelease: "30.30.3"
   86 |         InstallerVersion: "7.2.3"
   87 |         InstallerBuild: "70203-1"
   88 |         DKMSModuleVersion: "6.16.13"
   89 |         DKMSBuild: "2327507"
   90 |         DKMSPackageCode: "30300300"
   91 |         PairedROCm: "7.2.3"
   92 |         HostToolsChannel: legacy
   93 |         HostToolsPackage: amd-smi-lib
   94 |       - DriverRelease: "30.30.4"
   95 |         InstallerVersion: "7.2.4"
   96 |         InstallerBuild: "70204-1"
   97 |         DKMSModuleVersion: "6.16.13"
   98 |         DKMSBuild: "2341068"
   99 |         DKMSPackageCode: "30300400"
  100 |         PairedROCm: "7.2.4"
  101 |         HostToolsChannel: legacy
  102 |         HostToolsPackage: amd-smi-lib
  103 |       - DriverRelease: "31.30.0"
  104 |         InstallerVersion: "31.30"
  105 |         InstallerBuild: "313000-1"
  106 |         DKMSModuleVersion: "6.19.4"
  107 |         DKMSBuild: "2337710"
  108 |         DKMSPackageCode: "31300000"
  109 |         PairedROCm: "7.13.0"
  110 |         HostToolsChannel: core
  111 |         HostToolsPackage: amdrocm-amdsmi7.13
  112 |       - DriverRelease: "31.40.0"
  113 |         InstallerVersion: "31.40"
  114 |         InstallerBuild: "314000-1"
  115 |         DKMSModuleVersion: "6.19.14"
  116 |         DKMSBuild: "2364437"
  117 |         DKMSPackageCode: "31400000"
  118 |         PairedROCm: "7.14.0"
  119 |         HostToolsChannel: core-multiarch
  120 |         HostToolsPackage: amdrocm-amdsmi7.14
  121 |       - DriverRelease: "31.40.1"
  122 |         InstallerVersion: "31.40.1"
  123 |         InstallerBuild: "314001-1"
  124 |         DKMSModuleVersion: "6.19.14"
  125 |         DKMSBuild: "2377056"
  126 |         DKMSPackageCode: "31400100"
  127 |         PairedROCm: "7.14.0"
  128 |         HostToolsChannel: core-multiarch
  129 |         HostToolsPackage: amdrocm-amdsmi7.14
  130 |     gpu_stack_family_resolved: instinct
  131 |     rke2_installation_url: "https://get.rke2.io"
  132 | 
  133 |     supported_ubuntu_versions:
  134 |       - "20.04"
  135 |       - "22.04"
  136 |       - "24.04"
  137 |       - "26.04"
  138 | 
  139 |     rke2_ports_tcp:
  140 |       - "80"
  141 |       - "443"
  142 |       - "2376"
  143 |       - "2379"
  144 |       - "2380"
  145 |       - "6443"
  146 |       - "9099"
  147 |       - "9345"
  148 |       - "10250"
  149 |       - "10254"
  150 |       - "30000:32767"
  151 | 
  152 |     rke2_ports_udp:
  153 |       - "8472"
  154 |       - "30000:32767"
  155 | 
  156 |     inotify_target_value: 512
  157 |     rancher_min_partition_gb: 500
  158 |     bloom_fstab_tag: "# managed by cluster-bloom"
  159 |     bloom_premounted_fstab_tag: "# premounted by cluster-bloom"
  160 |     bloom_rancher_fstab_tag: "# managed by cluster-bloom rancher-disk"
  161 |     bloom_fstab_section_header: "# # # this section is managed by AMD Enterprise AI tool cluster-bloom"
  162 |     bloom_fstab_section_footer: "# # # end of AMD Enterprise AI cluster-bloom"
  163 | 
  164 |   pre_tasks:
  165 |     - name: Check passwordless sudo is configured
  166 |       block:
  167 |         - name: Verify privilege escalation
  168 |           ansible.builtin.command: /bin/true
  169 |           become: true
  170 |           changed_when: false
  171 |       rescue:
  172 |         - name: Fail if passwordless sudo is not configured
  173 |           fail:
  174 |             msg: |
  175 |               ❌ Passwordless sudo is required but not configured for the current user.
  176 | 
  177 |               Fix: run the following command on the target host and then retry:
  178 | 
  179 |                 echo "$USER ALL=(ALL) NOPASSWD: [REDACTED_LITERAL]
  180 | 
  181 |     - name: Gather facts
  182 |       ansible.builtin.setup:
  183 |         gather_subset:
  184 |           - min
  185 |           - network
  186 | 
  187 |   tasks:
  188 |     - name: Pre-deployment Data Safety Validation
  189 |       tags: [pre_deployment]
  190 |       include_tasks: tasks/data_safety_check.yaml
  191 |       vars:
  192 |         validate_no_disks_for_cluster: "{{ NO_DISKS_FOR_CLUSTER | default(false) }}"
  193 |         validate_cluster_disks: "{{ CLUSTER_DISKS | default('') }}"
  194 |         validate_config_file: "{{ bloom_config_file | default('bloom.yaml') }}"
  195 | 
  196 |     - name: Pause conflicting k3s installation (loaned nodes)
  197 |       tags: [pre_deployment, k3s_pause]
  198 |       include_tasks: tasks/k3s_pause.yaml
  199 |       when: (k3s_pause_required | default(false) | bool) or (PAUSE_K3S | default(false) | bool)
  200 | 
  201 |     - name: Node Validation
  202 |       tags: [validate_node]
  203 |       import_tasks: tasks/validate_node/main.yaml
  204 | 
  205 |     - name: Node Preparation
  206 |       tags: [prepare_node]
  207 |       import_tasks: tasks/prepare_node/main.yaml
  208 | 
  209 |     # Every notifier of "Save iptables" has run by this point: the port rules
  210 |     # in prepare_node and the REJECT removals in validate_node. Flush here so
  211 |     # the snapshot is taken while the ruleset is still only ours. Without this
  212 |     # the handler runs at the end of the play, after RKE2 is up, and saves
  213 |     # kube-proxy's and Cilium's live rules as if they were static config. See
  214 |     # the "Save iptables" handler for what that breaks.
  215 |     - name: Persist iptables before RKE2 starts programming them
  216 |       tags: [prepare_node]
  217 |       ansible.builtin.meta: flush_handlers
  218 | 
  219 |     - name: Deploy Cluster Tasks
  220 |       tags: [deploy_cluster]
  221 |       import_tasks: tasks/deploy_cluster/main.yaml
  222 | 
  223 |     - name: Deploy Kubernetes Applications
  224 |       tags: [deploy_k8s_apps]
  225 |       import_tasks: tasks/deploy_k8s_apps/main.yaml
  226 | 
  227 |     - name: Deploy ClusterForge Platform
  228 |       tags: [deploy_clusterforge]
  229 |       import_tasks: tasks/deploy_clusterforge/main.yaml
  230 | 
  231 |     - name: Update Cluster Certificates
  232 |       tags: [update_cert]
  233 |       import_tasks: tasks/update_certificate/main.yaml
  234 | 
  235 |   handlers:
  236 |     - name: Restart multipathd
  237 |       service:
  238 |         name: multipathd
  239 |         state: restarted
  240 | 
  241 |     - name: Create iptables directory
  242 |       ansible.builtin.file:
  243 |         path: /etc/iptables
  244 |         state: directory
  245 |         owner: root
  246 |         group: root
  247 |         mode: '0755'
  248 | 
  249 |     # iptables-save is a whole-machine dump, so this is only safe while the
  250 |     # ruleset still belongs to us. It is flushed after prepare_node for that
  251 |     # reason. Run late, on a node where RKE2 is already up, it captures
  252 |     # kube-proxy's and Cilium's live rules and writes them to the file
  253 |     # netfilter-persistent replays at boot. Two things then go wrong:
  254 |     #
  255 |     #   - the replay happens ~23s before RKE2 starts, and kube-proxy's
  256 |     #     KUBE-FORWARD rule needs an nfacct object that only exists once
  257 |     #     kube-proxy has created it, so the restore fails with
  258 |     #     "RULE_APPEND failed (No such file or directory)" and the unit is
  259 |     #     left permanently failed
  260 |     #   - when it does not fail it is worse, because it replays a stale
  261 |     #     snapshot of another controller's state. On one int-test node the
  262 |     #     file had grown to 110 KB of KUBE-SVC-*/KUBE-SEP-* chains naming pod
  263 |     #     IPs from two months earlier
  264 |     #
  265 |     # A filter-table-only dump would be the smaller blast radius, but the
  266 |     # filter table is where KUBE-FORWARD lives, so it would not help. Timing
  267 |     # is the fix.
  268 |     - name: Save iptables
  269 |       shell: iptables-save > /etc/iptables/rules.v4
  270 |       ignore_errors: yes
  271 | 
  272 |     - name: Set permissions on iptables rules file
  273 |       ansible.builtin.file:
  274 |         path: /etc/iptables/rules.v4
  275 |         owner: root
  276 |         group: root
  277 |         mode: '0644'
  278 | 
  279 |     - name: Reload udev
  280 |       shell: |
  281 |         udevadm control --reload-rules
  282 |         udevadm trigger
  283 | 
  284 |     - name: Restart chronyd
  285 |       service:
  286 |         name: chronyd
  287 |         state: restarted
  288 | 
  289 |     - name: Restart rsyslog
  290 |       service:
  291 |         name: rsyslog
  292 |         state: restarted
```

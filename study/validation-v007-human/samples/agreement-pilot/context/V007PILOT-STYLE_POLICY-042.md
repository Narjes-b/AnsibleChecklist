# Frozen source context: V007PILOT-STYLE_POLICY-042

- Repository: `dfroberg/cluster`
- Commit: `7bc521db65db986a2deef35ea955704bb0621dbd`
- Family: Style/policy
- Rule: `ansibleguard/variable-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `provision/ansible/kubernetes/roles/xanmanning.k3s/defaults/main.yml` (reported anchor line 45)
- Object: `variable` `a609ff171fb393e7f80d876130b681084d0fe83d62fe2572b182c0db54cadb6a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–144 of 144:

```text
    1 | ---
    2 | 
    3 | ##
    4 | # Global/Cluster Configuration
    5 | ##
    6 | 
    7 | # k3s state, options: installed, started, stopped, restarted, uninstalled, validated
    8 | # (default: installed)
    9 | k3s_state: installed
   10 | 
   11 | # Use a specific k3s version, if set to "false" we will get the latest
   12 | # k3s_release_version: v1.19.3
   13 | k3s_release_version: false
   14 | 
   15 | # Location of the k3s configuration file
   16 | k3s_config_file: "/etc/rancher/k3s/config.yaml"
   17 | 
   18 | # Location of the k3s configuration directory
   19 | k3s_config_yaml_d_dir: "/etc/rancher/k3s/config.yaml.d"
   20 | 
   21 | # When multiple ansible_play_hosts are present, attempt to cluster the nodes.
   22 | # Using false will create multiple standalone nodes.
   23 | # (default: true)
   24 | k3s_build_cluster: true
   25 | 
   26 | # URL for GitHub project
   27 | k3s_github_url: https://github.com/k3s-io/k3s
   28 | 
   29 | # Skip all tasks that validate configuration
   30 | k3s_skip_validation: false
   31 | 
   32 | # Skip all tasks that check environment configuration
   33 | k3s_skip_env_checks: false
   34 | 
   35 | # Installation directory for k3s
   36 | k3s_install_dir: /usr/local/bin
   37 | 
   38 | # Install using hard links rather than symbolic links
   39 | k3s_install_hard_links: false
   40 | 
   41 | # A list of templates used for configuring the server.
   42 | k3s_server_config_yaml_d_files: []
   43 | 
   44 | # A list of templates used for configuring the agent.
   45 | k3s_agent_config_yaml_d_files: []
   46 | 
   47 | # A list of templates used for pre-configuring the cluster.
   48 | k3s_server_manifests_templates: []
   49 | 
   50 | # A list of URLs used for pre-configuring the cluster.
   51 | k3s_server_manifests_urls: []
   52 | #  - url: https://some/url/to/manifest.yml
   53 | #    filename: manifest.yml
   54 | 
   55 | # A list of templates used for installing static pod manifests on the control plane.
   56 | k3s_server_pod_manifests_templates: []
   57 | 
   58 | # A list of URLs used for installing static pod manifests on the control plane.
   59 | k3s_server_pod_manifests_urls: []
   60 | #  - url: https://some/url/to/manifest.yml
   61 | #    filename: manifest.yml
   62 | 
   63 | # Use experimental features in k3s?
   64 | k3s_use_experimental: false
   65 | 
   66 | # Allow for unsupported configurations in k3s?
   67 | k3s_use_unsupported_config: false
   68 | 
   69 | # Enable etcd embedded datastore
   70 | k3s_etcd_datastore: false
   71 | 
   72 | ##
   73 | # Systemd config
   74 | ##
   75 | 
   76 | # Start k3s on system boot
   77 | k3s_start_on_boot: true
   78 | 
   79 | # List of required systemd units to k3s service unit.
   80 | k3s_service_requires: []
   81 | 
   82 | # List of "wanted" systemd unit to k3s (weaker than "requires").
   83 | k3s_service_wants: []
   84 | 
   85 | # Start k3s before a defined list of systemd units.
   86 | k3s_service_before: []
   87 | 
   88 | # Start k3s after a defined list of systemd units.
   89 | k3s_service_after: []
   90 | 
   91 | ##
   92 | # Server Configuration
   93 | ##
   94 | 
   95 | k3s_server: {}
   96 | # k3s_server:
   97 | #  listen-port: 6443
   98 | 
   99 | ##
  100 | # Agent Configuration
  101 | ##
  102 | 
  103 | k3s_agent: {}
  104 | # k3s_agent:
  105 | #   node-label:
  106 | #     - "foo=bar"
  107 | #     - "bish=bosh"
  108 | 
  109 | ##
  110 | # Ansible Controller configuration
  111 | ##
  112 | 
  113 | # Use become privileges for
  114 | k3s_become_for_all: false
  115 | k3s_become_for_systemd: null
  116 | k3s_become_for_install_dir: null
  117 | k3s_become_for_directory_creation: null
  118 | k3s_become_for_usr_local_bin: null
  119 | k3s_become_for_package_install: null
  120 | k3s_become_for_kubectl: null
  121 | k3s_become_for_uninstall: null
  122 | 
  123 | # Private registry configuration.
  124 | # Rancher k3s documentation: https://rancher.com/docs/k3s/latest/en/installation/private-registry/
  125 | k3s_registries:
  126 | 
  127 |   mirrors:
  128 | #    docker.io:
  129 | #      endpoint:
  130 | #        - "https://mycustomreg.com:5000"
  131 |   configs:
  132 | #    "mycustomreg:5000":
  133 | #      auth:
  134 | #        # this is the registry username
  135 | #        username: xxxxxx
  136 | #        # this is the registry password
  137 | #        password: [REDACTED_LITERAL]
  138 | #      tls:
  139 | #        # path to the cert file used in the registry
  140 | #        cert_file:
  141 | #        # path to the key file used in the registry
  142 | #        key_file:
  143 | #        # path to the ca file used in the registry
  144 | #        ca_file:
```

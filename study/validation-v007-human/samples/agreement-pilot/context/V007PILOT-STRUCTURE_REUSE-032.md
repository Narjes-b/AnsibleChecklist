# Frozen source context: V007PILOT-STRUCTURE_REUSE-032

- Repository: `ricsanfre/pi-cluster`
- Commit: `f55c4ba0659fd1409389f39026d91441bb0cf6d0`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/reset_external_services.yml` (reported anchor line 1)
- Object: `source_location` `377a2ce2719e87c3ff3eb907b782d39353e738b81bcc1d28ab7fa385f980fe13`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–364 of 364:

```text
    1 | ---
    2 | - name: Stage 1 - Destroy S3 Terraform resources
    3 |   hosts: localhost
    4 |   gather_facts: false
    5 |   tags: [terraform, s3, stage1]
    6 |   vars:
    7 |     terraform_minio_dir: "../terraform/minio"
    8 |     terraform_minio_state_dir: "{{ terraform_minio_dir }}/.terraform"
    9 |     terraform_minio_state_file: "{{ terraform_minio_dir }}/terraform.tfstate"
   10 |     vault_secret_file: "{{ lookup('ansible.builtin.env', 'HOME') }}/.secrets/vault.env"
   11 | 
   12 |   pre_tasks:
   13 |     - name: Stage 1 banner
   14 |       ansible.builtin.debug:
   15 |         msg: "===== Stage 1/5: Destroy S3 Terraform resources ====="
   16 | 
   17 |     - name: Include picluster variables
   18 |       ansible.builtin.include_vars: "vars/picluster.yml"
   19 | 
   20 |     - name: Check Vault secret file exists
   21 |       ansible.builtin.stat:
   22 |         path: "{{ vault_secret_file }}"
   23 |       register: vault_secret_file_stat
   24 | 
   25 |     - name: Validate Vault secret file exists
   26 |       ansible.builtin.assert:
   27 |         that:
   28 |           - vault_secret_file_stat.stat.exists
   29 |           - vault_secret_file_stat.stat.isreg
   30 |         fail_msg: |
   31 |           Vault secret file not found: {{ vault_secret_file }}
   32 | 
   33 |           Run external services stage 1 first to generate it, or create it with:
   34 | 
   35 |             VAULT_ADDR=https://vault.example.com:8200
   36 |             VAULT_TOKEN=[REDACTED_LITERAL]
   37 |             VAULT_CACERT=/path/to/certificates/CA.pem
   38 | 
   39 |     - name: Get Vault environment from secret file
   40 |       ansible.builtin.set_fact:
   41 |         vault_addr: "{{ lookup('ansible.builtin.ini', 'VAULT_ADDR type=properties file=' ~ vault_secret_file) }}"
   42 |         vault_token: "{{ lookup('ansible.builtin.ini', 'VAULT_TOKEN type=properties file=' ~ vault_secret_file) }}"
   43 |         vault_cacert: "{{ lookup('ansible.builtin.ini', 'VAULT_CACERT type=properties file=' ~ vault_secret_file, errors='ignore') | default('', true) }}"
   44 | 
   45 |     - name: Validate Vault variables loaded from secret file
   46 |       ansible.builtin.assert:
   47 |         that:
   48 |           - vault_addr is defined and vault_addr != ""
   49 |           - vault_token is defined and vault_token != ""
   50 |         fail_msg: |
   51 |           Missing VAULT_ADDR or VAULT_TOKEN in {{ vault_secret_file }}
   52 | 
   53 |     - name: Fetch MinIO credentials from Vault
   54 |       community.hashi_vault.vault_kv2_get:
   55 |         url: "{{ vault_addr }}"
   56 |         token: "{{ vault_token }}"
   57 |         validate_certs: "{{ not (enable_letsencrypt | default(false)) }}"
   58 |         ca_cert: "{{ vault_cacert | default(omit) }}"
   59 |         mount_point: "secret"
   60 |         path: "s3/rustfsadmin"
   61 |       register: minio_vault_secret
   62 |       no_log: true
   63 | 
   64 |     - name: Set MinIO credentials from Vault
   65 |       ansible.builtin.set_fact:
   66 |         minio_root_user: "{{ (minio_vault_secret.secret | default({})).username | default('', true) }}"
   67 |         minio_root_password: "{{ (minio_vault_secret.secret | default({})).key | default('', true) }}"
   68 |       no_log: true
   69 | 
   70 |     - name: Validate MinIO credentials were retrieved from Vault
   71 |       ansible.builtin.assert:
   72 |         that:
   73 |           - minio_root_user is defined
   74 |           - minio_root_user | length > 0
   75 |           - minio_root_password is defined
   76 |           - minio_root_password | length > 0
   77 |         fail_msg: |
   78 |           Failed to retrieve MinIO credentials from Vault at path secret/minio/root
   79 |           Please ensure the secret exists and contains keys: username, key
   80 | 
   81 |   tasks:
   82 |     - name: Check MinIO Terraform state directory
   83 |       ansible.builtin.stat:
   84 |         path: "{{ terraform_minio_state_dir }}"
   85 |       register: minio_tf_state_dir
   86 | 
   87 |     - name: Check MinIO Terraform state file
   88 |       ansible.builtin.stat:
   89 |         path: "{{ terraform_minio_state_file }}"
   90 |       register: minio_tf_state_file
   91 | 
   92 |     - name: Skip MinIO Terraform destroy when state directory is missing
   93 |       ansible.builtin.debug:
   94 |         msg: "Skipping MinIO Terraform destroy because {{ terraform_minio_state_dir }} does not exist"
   95 |       when: not minio_tf_state_dir.stat.exists
   96 | 
   97 |     - name: Skip MinIO Terraform destroy when state file is missing
   98 |       ansible.builtin.debug:
   99 |         msg: "Skipping MinIO Terraform destroy because {{ terraform_minio_state_file }} does not exist"
  100 |       when: not minio_tf_state_file.stat.exists
  101 | 
  102 |     - name: Initialize MinIO Terraform project
  103 |       ansible.builtin.command:
  104 |         cmd: tofu init -no-color
  105 |         chdir: "{{ terraform_minio_dir }}"
  106 |       changed_when: false
  107 |       when:
  108 |         - minio_tf_state_dir.stat.exists
  109 |         - minio_tf_state_file.stat.exists
  110 | 
  111 |     - name: Destroy S3 Terraform resources
  112 |       ansible.builtin.command:
  113 |         cmd: tofu destroy -no-color -auto-approve
  114 |         chdir: "{{ terraform_minio_dir }}"
  115 |       environment:
  116 |         VAULT_ADDR: "{{ vault_addr }}"
  117 |         VAULT_TOKEN: "{{ vault_token }}"
  118 |         VAULT_CACERT: "{{ vault_cacert if (not enable_letsencrypt | default(false)) else '' }}"
  119 |         TF_VAR_minio_endpoint: "{{ minio_endpoint }}"
  120 |         TF_VAR_minio_use_ssl: "true"
  121 |         TF_VAR_minio_ssl_verify: "true"
  122 |         TF_VAR_minio_admin_user: "{{ minio_root_user }}"
  123 |         TF_VAR_minio_admin_password: "{{ minio_root_password }}"
  124 |         TF_VAR_vault_address: "{{ vault_addr }}"
  125 |         TF_VAR_vault_token: "{{ vault_token }}"
  126 |       register: terraform_minio_destroy
  127 |       changed_when: "'Destroy complete!' in terraform_minio_destroy.stdout"
  128 |       no_log: false
  129 |       when:
  130 |         - minio_tf_state_dir.stat.exists
  131 |         - minio_tf_state_file.stat.exists
  132 | 
  133 | - name: Stage 2 - Clean RustFS Installation
  134 |   hosts: s3
  135 |   become: true
  136 |   gather_facts: false
  137 |   tags: [s3, stage2]
  138 |   tasks:
  139 |     - name: Stage 2 banner
  140 |       ansible.builtin.debug:
  141 |         msg: "===== Stage 2/5: Clean RustFS installation ====="
  142 | 
  143 |     - name: Stop and disable RustFS Server
  144 |       ansible.builtin.systemd:
  145 |         name: rustfs
  146 |         state: stopped
  147 |         enabled: false
  148 |       become: true
  149 |     - name: Delete directories and files
  150 |       become: true
  151 |       ansible.builtin.file:
  152 |         state: absent
  153 |         path: "{{ item }}"
  154 |       with_items:
  155 |         - /storage/rustfs/
  156 |         - /etc/rustfs/
  157 |         - /var/log/rustfs/
  158 |         - /usr/local/bin/rustfs
  159 |         - /usr/local/bin/rc
  160 |         - /etc/systemd/system/rustfs.service
  161 |         - ~/.config/rc/
  162 |     - name: Reload systemd daemon
  163 |       ansible.builtin.systemd:
  164 |         daemon_reload: true
  165 | 
  166 | - name: Stage 3 - Destroy Vault Terraform resources
  167 |   hosts: localhost
  168 |   gather_facts: false
  169 |   tags: [terraform, vault, stage3]
  170 |   vars:
  171 |     terraform_vault_dir: "../terraform/vault"
  172 |     terraform_vault_state_dir: "{{ terraform_vault_dir }}/.terraform"
  173 |     terraform_vault_state_file: "{{ terraform_vault_dir }}/terraform.tfstate"
  174 |     vault_secret_file: "{{ lookup('ansible.builtin.env', 'HOME') }}/.secrets/vault.env"
  175 | 
  176 |   pre_tasks:
  177 |     - name: Stage 3 banner
  178 |       ansible.builtin.debug:
  179 |         msg: "===== Stage 3/5: Destroy Vault Terraform resources ====="
  180 | 
  181 |     - name: Include picluster variables
  182 |       ansible.builtin.include_vars: "vars/picluster.yml"
  183 | 
  184 |     - name: Check Vault secret file exists
  185 |       ansible.builtin.stat:
  186 |         path: "{{ vault_secret_file }}"
  187 |       register: vault_secret_file_stat
  188 | 
  189 |     - name: Validate Vault secret file exists
  190 |       ansible.builtin.assert:
  191 |         that:
  192 |           - vault_secret_file_stat.stat.exists
  193 |           - vault_secret_file_stat.stat.isreg
  194 |         fail_msg: |
  195 |           Vault secret file not found: {{ vault_secret_file }}
  196 | 
  197 |           Run external services stage 1 first to generate it, or create it with:
  198 | 
  199 |             VAULT_ADDR=https://vault.example.com:8200
  200 |             VAULT_TOKEN=[REDACTED_LITERAL]
  201 |             VAULT_CACERT=/path/to/certificates/CA.pem
  202 | 
  203 |     - name: Get Vault environment from secret file
  204 |       ansible.builtin.set_fact:
  205 |         vault_addr: "{{ lookup('ansible.builtin.ini', 'VAULT_ADDR type=properties file=' ~ vault_secret_file) }}"
  206 |         vault_token: "{{ lookup('ansible.builtin.ini', 'VAULT_TOKEN type=properties file=' ~ vault_secret_file) }}"
  207 |         vault_cacert: "{{ lookup('ansible.builtin.ini', 'VAULT_CACERT type=properties file=' ~ vault_secret_file, errors='ignore') | default('', true) }}"
  208 | 
  209 |     - name: Validate Vault variables loaded from secret file
  210 |       ansible.builtin.assert:
  211 |         that:
  212 |           - vault_addr is defined and vault_addr != ""
  213 |           - vault_token is defined and vault_token != ""
  214 |         fail_msg: |
  215 |           Missing VAULT_ADDR or VAULT_TOKEN in {{ vault_secret_file }}
  216 | 
  217 |   tasks:
  218 |     - name: Check Vault Terraform state directory
  219 |       ansible.builtin.stat:
  220 |         path: "{{ terraform_vault_state_dir }}"
  221 |       register: vault_tf_state_dir
  222 | 
  223 |     - name: Check Vault Terraform state file
  224 |       ansible.builtin.stat:
  225 |         path: "{{ terraform_vault_state_file }}"
  226 |       register: vault_tf_state_file
  227 | 
  228 |     - name: Skip Vault Terraform destroy when state directory is missing
  229 |       ansible.builtin.debug:
  230 |         msg: "Skipping Vault Terraform destroy because {{ terraform_vault_state_dir }} does not exist"
  231 |       when: not vault_tf_state_dir.stat.exists
  232 | 
  233 |     - name: Skip Vault Terraform destroy when state file is missing
  234 |       ansible.builtin.debug:
  235 |         msg: "Skipping Vault Terraform destroy because {{ terraform_vault_state_file }} does not exist"
  236 |       when: not vault_tf_state_file.stat.exists
  237 | 
  238 |     - name: Initialize Vault Terraform project
  239 |       ansible.builtin.command:
  240 |         cmd: tofu init -no-color
  241 |         chdir: "{{ terraform_vault_dir }}"
  242 |       environment:
  243 |         VAULT_ADDR: "{{ vault_addr }}"
  244 |         VAULT_TOKEN: "{{ vault_token }}"
  245 |         VAULT_CACERT: "{{ vault_cacert if (not enable_letsencrypt | default(false)) else '' }}"
  246 |         TF_VAR_vault_address: "{{ vault_addr }}"
  247 |         TF_VAR_vault_token: "{{ vault_token }}"
  248 |       changed_when: false
  249 |       when:
  250 |         - vault_tf_state_dir.stat.exists
  251 |         - vault_tf_state_file.stat.exists
  252 | 
  253 |     - name: Destroy Vault Terraform resources
  254 |       ansible.builtin.command:
  255 |         cmd: >-
  256 |           tofu destroy
  257 |           -no-color
  258 |           -auto-approve
  259 |           -var="enable_kubernetes_auth=false"
  260 |           -var="enable_policies=true"
  261 |           -var="enable_roles=true"
  262 |           -var="enable_secrets=[REDACTED_LITERAL]
  263 |         chdir: "{{ terraform_vault_dir }}"
  264 |       environment:
  265 |         VAULT_ADDR: "{{ vault_addr }}"
  266 |         VAULT_TOKEN: "{{ vault_token }}"
  267 |         VAULT_CACERT: "{{ vault_cacert if (not enable_letsencrypt | default(false)) else '' }}"
  268 |         TF_VAR_vault_address: "{{ vault_addr }}"
  269 |         TF_VAR_vault_token: "{{ vault_token }}"
  270 |       register: terraform_vault_destroy
  271 |       changed_when: "'Destroy complete!' in terraform_vault_destroy.stdout"
  272 |       when:
  273 |         - vault_tf_state_dir.stat.exists
  274 |         - vault_tf_state_file.stat.exists
  275 | 
  276 | - name: Stage 4 - Clean Vault Installation
  277 |   hosts: vault
  278 |   become: true
  279 |   gather_facts: false
  280 |   tags: [vault, stage4]
  281 |   tasks:
  282 |     - name: Stage 4 banner
  283 |       ansible.builtin.debug:
  284 |         msg: "===== Stage 4/5: Clean Vault installation ====="
  285 | 
  286 |     - name: Stop and disable Vault Server
  287 |       ansible.builtin.systemd:
  288 |         name: "{{ item }}"
  289 |         state: stopped
  290 |         enabled: false
  291 |       become: true
  292 |       with_items:
  293 |         - vault
  294 |         - vault-unseal
  295 |     - name: Delete directories and files
  296 |       become: true
  297 |       ansible.builtin.file:
  298 |         state: absent
  299 |         path: "{{ item }}"
  300 |       with_items:
  301 |         - /var/lib/vault/
  302 |         - /etc/vault/
  303 |         - /var/log/vault/
  304 |         - /usr/local/bin/vault
  305 |         - /etc/systemd/system/vault.service
  306 |         - /etc/systemd/system/vault-unseal.service
  307 |     - name: Reload systemd daemon
  308 |       ansible.builtin.systemd:
  309 |         daemon_reload: true
  310 | 
  311 | - name: Stage 5 - Clean Restic Installation
  312 |   hosts: picluster
  313 |   become: true
  314 |   gather_facts: false
  315 |   tags: [restic, stage5]
  316 |   tasks:
  317 |     - name: Stage 5 banner
  318 |       ansible.builtin.debug:
  319 |         msg: "===== Stage 5/5: Clean Restic installation ====="
  320 | 
  321 |     - name: Stop and disable restic backup service
  322 |       ansible.builtin.systemd:
  323 |         name: "{{ item }}"
  324 |         state: stopped
  325 |         enabled: false
  326 |       become: true
  327 |       with_items:
  328 |         - restic-backup.timer
  329 | 
  330 |     - name: Stop and disable restic clean service
  331 |       ansible.builtin.systemd:
  332 |         name: "{{ item }}"
  333 |         state: stopped
  334 |         enabled: false
  335 |       become: true
  336 |       when: restic_clean_service
  337 |       with_items:
  338 |         - restic-clean.timer
  339 | 
  340 |     - name: Delete directories and files
  341 |       become: true
  342 |       ansible.builtin.file:
  343 |         state: absent
  344 |         path: "{{ item }}"
  345 |       with_items:
  346 |         - /etc/restic/
  347 |         - /var/log/restic.log
  348 |         - /usr/local/bin/restic
  349 |         - /etc/systemd/system/restic-backup.service
  350 |         - /etc/systemd/system/restic-backup.timer
  351 | 
  352 |     - name: Delete clean service file
  353 |       become: true
  354 |       ansible.builtin.file:
  355 |         state: absent
  356 |         path: "{{ item }}"
  357 |       with_items:
  358 |         - /etc/systemd/system/restic-clean.timer
  359 |         - /etc/systemd/system/restic-clean.service
  360 |       when: restic_clean_service
  361 | 
  362 |     - name: Reload systemd daemon
  363 |       ansible.builtin.systemd:
  364 |         daemon_reload: true
```

## Frozen tracked paths in the relevant role/scope

```text
.github/renovate.json5
.github/renovate/clusters.json5
.github/renovate/customManagers.json5
.github/renovate/grafanaDashboards.json5
.github/renovate/groups.json5
.github/renovate/labels.json5
.github/workflows/ci.yml
.gitignore
.mise.toml
CLAUDE.md
LICENSE
Makefile
README.md
ansible-runner/Dockerfile
ansible-runner/Makefile
ansible-runner/ansible-runner.sh
ansible-runner/docker-compose.yaml
ansible/.ansible-lint
ansible/.python-version
ansible/.yamllint
ansible/ansible.cfg
ansible/backup_configuration.yml
ansible/configure_dns_authoritative.yml
ansible/configure_minio.yml
ansible/configure_pxe_server.yml
ansible/configure_static_ip_address.yml
ansible/configure_vault.yml
ansible/create_secret_files.yml
ansible/deploy_minio.yml
ansible/deploy_monitoring_agent.yml
ansible/deploy_rustfs.yml
ansible/deploy_vault.yml
ansible/external_services.yml
ansible/files/check_lh.sh
ansible/generate_gateway_tls_certificate.yml
ansible/group_vars/all.yml
ansible/group_vars/control.yml
ansible/group_vars/external.yml
ansible/group_vars/k3s_cluster.yml
ansible/group_vars/k3s_master.yml
ansible/host_vars/node-hp-1.yml
ansible/host_vars/node-hp-2.yml
ansible/host_vars/node-hp-3.yml
ansible/host_vars/node1.yml
ansible/install_utilities_localhost.yml
ansible/inventory.yml
ansible/k3s_bootstrap.yml
ansible/k3s_install.yml
ansible/k3s_reset.yml
ansible/k3s_start.yml
ansible/k3s_stop.yml
ansible/load_external_services_keys.yml
ansible/pyproject.toml
ansible/requirements.yml
ansible/reset_external_services.yml
ansible/roles/basic_setup/defaults/main.yaml
ansible/roles/basic_setup/handlers/main.yml
ansible/roles/basic_setup/scripts/pi_temp
ansible/roles/basic_setup/scripts/pi_throttling
ansible/roles/basic_setup/tasks/files/multipath.conf
ansible/roles/basic_setup/tasks/load_kernel_modules.yml
ansible/roles/basic_setup/tasks/main.yaml
ansible/roles/basic_setup/tasks/multipath_blacklist.yml
ansible/roles/basic_setup/tasks/raspberrypi_tasks.yml
ansible/roles/basic_setup/tasks/remove_snap.yaml
ansible/roles/basic_setup/tasks/remove_snap_packages.yml
ansible/roles/dns/handlers/main.yml
ansible/roles/dns/tasks/main.yml
ansible/roles/haproxy/defaults/main.yml
ansible/roles/haproxy/handlers/main.yml
ansible/roles/haproxy/tasks/main.yml
ansible/roles/haproxy/templates/haproxy.cfg.j2
ansible/roles/k3s/master/defaults/main.yml
ansible/roles/k3s/master/tasks/install_helm.yml
ansible/roles/k3s/master/tasks/installation.yml
ansible/roles/k3s/master/tasks/k3s_install.yml
ansible/roles/k3s/master/tasks/main.yml
ansible/roles/k3s/master/tasks/pre_configuration.yml
ansible/roles/k3s/master/tasks/wait_for_primary_master.yml
ansible/roles/k3s/master/templates/config.yml.j2
ansible/roles/k3s/master/templates/registry.yml.j2
ansible/roles/k3s/master/vars/main.yml
ansible/roles/k3s/prereq/handlers/main.yml
ansible/roles/k3s/prereq/tasks/disable_swap.yml
ansible/roles/k3s/prereq/tasks/main.yml
ansible/roles/k3s/worker/defaults/main.yml
ansible/roles/k3s/worker/tasks/main.yml
ansible/roles/k3s/worker/tasks/pre_configuration.yml
ansible/roles/k3s/worker/templates/config.yml.j2
ansible/roles/k3s/worker/templates/registry.yml.j2
ansible/roles/k3s/worker/vars/main.yml
ansible/roles/pxe-server/defaults/main.yml
ansible/roles/pxe-server/handlers/main.yml
ansible/roles/pxe-server/tasks/create_auto_install_files.yml
ansible/roles/pxe-server/tasks/create_pxe_config_files.yml
ansible/roles/pxe-server/tasks/install_ks_http_server.yml
ansible/roles/pxe-server/tasks/install_tftp_server.yml
ansible/roles/pxe-server/tasks/main.yml
ansible/roles/pxe-server/templates/cloud-init-autoinstall.yml.j2
ansible/roles/pxe-server/templates/cloud-init-metadata.yml.j2
ansible/roles/pxe-server/templates/grub.conf.j2
ansible/roles/pxe-server/templates/ks-server.conf.j2
ansible/roles/pxe-server/templates/pxelinux.conf.j2
ansible/setup_picluster.yml
ansible/shutdown.yml
ansible/tasks/cilium_config.yml
ansible/tasks/clean_cilium.yml
ansible/tasks/cleaning.yml
ansible/tasks/configure_velero_cli.yml
ansible/tasks/create_basic_auth_credentials.yml
ansible/tasks/create_minio_bearer_token.yml
ansible/tasks/create_rustfs_bearer_token.yml
ansible/tasks/ensure_k3s_stopped.yml
ansible/tasks/fluxcd_bootstrap.yml
ansible/tasks/generate_ca_signed_cert.yml
ansible/tasks/generate_custom_ca.yml
ansible/tasks/install_cli_utils.yml
ansible/tasks/install_fluxcd_cli.yml
ansible/tasks/install_istio_cli.yml
ansible/tasks/install_longhorn_cli.yml
[listing truncated after 120 paths]
```

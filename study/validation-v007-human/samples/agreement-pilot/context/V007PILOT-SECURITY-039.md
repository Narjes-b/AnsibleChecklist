# Frozen source context: V007PILOT-SECURITY-039

- Repository: `mageops/ansible-infrastructure`
- Commit: `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`
- Family: Security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `group_vars/vagrant.yml` (reported anchor line 85)
- Object: `variable` `143d9177009d32cd7d98ec322f49e84ee594c14cc0c9be31e70e587468268f56`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–110 of 110:

```text
    1 | mageops_app_host_group: vagrant
    2 | 
    3 | mageops_https_enable: no
    4 | mageops_packages_full_update: yes
    5 | mageops_trusted_cidr_blocks:
    6 |   - 127.0.0.0/8         # Loopback
    7 |   - 192.168.100.0/24    # Our VirtualBox / Vagrant Host-Only network
    8 |   - 192.168.57.0/16     # Our VirtualBox / Vagrant Host-Only network
    9 |   - 10.0.2.0/24         # Default VirtualBox / Vagrant NAT network
   10 | 
   11 | mageops_packages_app_node_extra:
   12 |   - ghostscript
   13 | 
   14 | unison_server_port: 5566
   15 | 
   16 | firewall_enable: yes
   17 | firewall_public_services:
   18 |     - http
   19 |     - https
   20 | firewall_public_ports:
   21 |     - 8080/tcp
   22 | firewall_trusted_networks: "{{ mageops_trusted_cidr_blocks }}"
   23 | firewall_guarded_services:
   24 |     - mysql
   25 |     - ftp
   26 |     - dns
   27 |     - smtp
   28 |     - smtps
   29 |     - nfs
   30 | firewall_guarded_ports:
   31 |     - 3306/tcp
   32 |     - 21/tcp
   33 |     - 53/tcp
   34 |     - 53/udp
   35 |     - 25/tcp
   36 |     - 446/tcp
   37 |     - 9200-9300/tcp
   38 |     - 2049/tcp
   39 |     - "{{ (mageops_elasticsearch_opensearch_flavor == 'elasticsearch') | ternary(elasticsearch_http_port ~ '/tcp', opensearch_http_port ~ '/tcp') }}"
   40 |     - "{{ (mageops_elasticsearch_opensearch_flavor == 'elasticsearch') | ternary(elasticsearch_transport_tcp_port ~ '/tcp', opensearch_transport_tcp_port ~ '/tcp') }}"
   41 |     - "{{ mageops_redis_port }}/tcp"
   42 |     - "{{ mageops_redis_sessions_port }}/tcp"
   43 |     - "{{ mageops_redis_port }}/tcp"
   44 |     - "{{ unison_server_port }}/tcp"
   45 |     - "{{ unison_server_port }}/udp"
   46 |     - "{{ rabbitmq_amqp_port }}/tcp"
   47 |     - "{{ rabbitmq_amqp_port }}/udp"
   48 |     - "{{ rabbitmq_http_port }}/tcp"
   49 | 
   50 | 
   51 | php_opcache_validate_timestamps: 1
   52 | php_opcache_consistency_checks: 1
   53 | php_opcache_file_update_protection: 2
   54 | 
   55 | php_opcache_revalidate_path: 1
   56 | php_opcache_revalidate_freq: 0
   57 | 
   58 | php_cli_opcache_file_cache_enable: yes
   59 | php_cli_opcache_file_cache_consistency_checks: 1
   60 | 
   61 | 
   62 | php_display_errors: On
   63 | php_http_request_max_execution_time: 600
   64 | 
   65 | 
   66 | 
   67 | 
   68 | mysql_public_root_access: yes
   69 | 
   70 | nginx_app_port: 80
   71 | 
   72 | mageops_rabbitmq_host: 127.0.0.1
   73 | mageops_mysql_host: 127.0.0.1
   74 | mageops_redis_host: 127.0.0.1
   75 | mageops_redis_sessions_host: 127.0.0.1
   76 | mageops_elasticsearch_host: 127.0.0.1
   77 | mageops_varnish_host: 127.0.0.1
   78 | mageops_varnish_port: 8080
   79 | mageops_varnish_backend_port: "{{ nginx_app_port }}"
   80 | 
   81 | varnish_standalone: false
   82 | 
   83 | magento_mode: default
   84 | magento_redis_cache: yes
   85 | magento_rabbitmq_password: [REDACTED_LITERAL]
   86 | magento_cron_disabled: yes
   87 | magento_nginx_rewrite_static_assets_version: yes
   88 | mageops_root_ssh_keys_global: []
   89 | 
   90 | sshd_password_auth: [REDACTED_LITERAL]
   91 | sshd_permit_root_login: yes
   92 | sshd_public_network_lockdown: yes
   93 | sshd_trusted_networks: "{{ ['127.0.0.0/8'] + mageops_trusted_cidr_blocks }}"
   94 | 
   95 | mageops_cli_user_groups: [wheel]
   96 | 
   97 | mageops_packages_mirrorlist_countrycode: pl
   98 | mageops_packages_vagrant_node:
   99 |   # Required for installing Virtualbox Guest Addons
  100 |   - kernel-devel
  101 |   # Required for patching Magento
  102 |   - patch
  103 |   # Required for some yarn modules
  104 |   - automake
  105 | 
  106 | nodejs_use_yarn: yes
  107 | nodejs_packages:
  108 |   - gulp-cli
  109 | 
  110 | nginx_static_files_expires: "off"
```

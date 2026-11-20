# Frozen source context: V007PILOT2-STRUCTURE_REUSE-006

- Repository: `cfpb/aurora`
- Commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Family: structure_reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `deploy/deploy_gocd.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`deploy/deploy_gocd.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–143 of 143:

```text
    1 | ---
    2 | - hosts: ci_server
    3 |   become: yes
    4 |   become_method: sudo
    5 |   roles:
    6 |     - common
    7 |     - {role: puppet_disable, when: "disable_puppet"}
    8 |     - {role: iptables, when: "iptables_config"}
    9 |     - gocd_server
   10 |     - gocd
   11 | 
   12 | - hosts: ci_agent
   13 |   become: yes
   14 |   become_method: sudo
   15 |   serial: 1
   16 |   max_fail_percentage: 10
   17 |   roles:
   18 |     - common
   19 |     - devtools
   20 |     - devtools7
   21 |     - {role: puppet_disable, when: "disable_puppet"}
   22 |     - {role: iptables, when: "iptables_config"}
   23 |     - gocd
   24 |     # - pentaho Per Tim 11.18.19 -- Pentaho not used.
   25 |     - {role: python, when: "custom_repo"}
   26 |     - {role: python-build, when: "not custom_repo"}
   27 |     - python36-scl
   28 |     - python-libs
   29 |     - odbc
   30 |     - {role: ruby, when: "install_ruby"}
   31 |     - sqitch
   32 |     - nodejs
   33 |     - maven
   34 |     - tesseract
   35 |     #- julia
   36 | 
   37 | - hosts: ci_agent
   38 |   become: yes
   39 |   become_method: sudo
   40 |   tasks:
   41 |     #- name: Activate Julia repo
   42 |     #  get_url:
   43 |     #    url: https://copr.fedoraproject.org/coprs/nalimilan/julia/repo/epel-6/nalimilan-julia-epel-6.repo
   44 |     #    dest: /etc/yum.repos.d/nalimilan-julia-epel-6.repo
   45 |     #  when: not 'production' in group_names
   46 | 
   47 |     - name: Install additional packages
   48 |       yum:
   49 |         name: "{{ item }}"
   50 |         state: present
   51 |       with_items:
   52 |         - "@development"
   53 |         - screen
   54 |         - p7zip
   55 |     #    - julia
   56 | 
   57 |     - name: Install Additional Database Automation packages
   58 |       yum:
   59 |         name: "{{ item }}"
   60 |         state: present
   61 |       with_items:
   62 |         - htop
   63 |         - rsync
   64 |         - unzip
   65 |         - gpg
   66 |         - pigz
   67 |         - facter
   68 |         - sysstat # sar, iostat, vmstat
   69 |         - systemtap # dtrace equivalent
   70 |         - ant
   71 | 
   72 |     - name: Install Database Automation custom packages
   73 |       yum:
   74 |         name: "{{ item }}"
   75 |         state: "{{ db_automation_package_state }}"
   76 |         disable_gpg_check: yes
   77 |       with_items: "{{ db_automation_custom_packages }}"
   78 |       when: db_automation_custom_packages is defined
   79 | 
   80 | - hosts: ci_terminal
   81 |   become: yes
   82 |   become_method: sudo
   83 |   roles:
   84 |     - common
   85 |     - devtools
   86 |     - {role: puppet_disable, when: "disable_puppet"}
   87 |     - {role: iptables, when: "iptables_config"}
   88 |     - {role: epel, when: "use_epel and not 'production' in group_names"}
   89 |     - eod
   90 |     #- talend # Talend goes here because it installs an older java
   91 |     - gocd
   92 |     - {role: python, when: "custom_repo"}
   93 |     - {role: python-build, when: "not custom_repo"}
   94 |     - python36-scl
   95 |     - python-libs
   96 |     - r-core
   97 |     - r-libs
   98 |     - {role: ruby, when: "install_ruby"}
   99 |     - pycharm
  100 |     - r-studio-desktop
  101 |     - clouseau
  102 |     #- {role: pentaho, when: "install_pentaho"}   Per Tim 11.18.19 Pentaho not used
  103 |     - sublime
  104 | #   - julia
  105 | 
  106 |   tasks:
  107 |     - name: Install development packages
  108 |       yum:
  109 |         name: "{{ item }}"
  110 |         state: present
  111 |         disable_gpg_check: yes
  112 |       with_items:
  113 |         - "@development"
  114 |         - gcc-gfortran
  115 |         - python-devel
  116 |         - nodejs
  117 | 
  118 |     - name: Install custom RPMs
  119 |       yum:
  120 |         name: "{{ item }}"
  121 |         state: present
  122 |         disable_gpg_check: yes
  123 |       with_items:
  124 |         - xsv
  125 |         - gnucobol
  126 |         - htop
  127 |         - p7zip
  128 |         - sf-dataloader
  129 |       when: custom_repo
  130 | 
  131 |     - name: Install Database Automation custom packages
  132 |       yum:
  133 |         name: "{{ item }}"
  134 |         state: "{{ db_automation_package_state }}"
  135 |         disable_gpg_check: yes
  136 |       with_items: "{{ db_automation_custom_packages }}"
  137 |       when: db_automation_custom_packages is defined
  138 | 
  139 | - hosts: hadoop_edge
  140 |   become: yes
  141 |   become_method: sudo
  142 |   roles:
  143 |     - gocd
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `.`; 442 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

Listing exceeds 400: paths beside the cited file, then a per-directory count of ALL paths.
deploy/Vagrantfile
deploy/ansible.cfg
deploy/audit_resources.yml
deploy/config_analytics_terminal.yml
deploy/config_citus_server.yml
deploy/config_elasticsearch.yml
deploy/config_file_server.yml
deploy/config_nginx_proxy_server.yml
deploy/config_proxy_server.yml
deploy/create_databases.yml
deploy/deploy_admin_terminal.yml
deploy/deploy_analytics_terminal.yml
deploy/deploy_app_server.yml
deploy/deploy_citus_server.yml
deploy/deploy_db_server.yml
deploy/deploy_db_terminal.yml
deploy/deploy_development_terminal.yml
deploy/deploy_elastic_search.yml
deploy/deploy_elk.yml
deploy/deploy_file_server.yml
deploy/deploy_gocd.yml
deploy/deploy_kerberos_server.yml
deploy/deploy_mesos_agent.yml
deploy/deploy_mesos_master.yml
deploy/deploy_neo4j_server.yml
deploy/deploy_nginx_proxy_server.yml
deploy/deploy_proxy_server.yml
deploy/deploy_r_terminal.yml
deploy/deploy_research_environment.yml
deploy/group_vars/all/main.yml
deploy/group_vars/all_db/main.yml
deploy/group_vars/citus_coordinator/main.yml
deploy/group_vars/citus_coordinator_standby/main.yml
deploy/group_vars/citus_worker/main.yml
deploy/library/__init__.py
deploy/library/postgresql_exec.py
deploy/monitor_research_environment.yml
deploy/roles/apache/defaults/main.yml
deploy/roles/apache/handlers/main.yml
deploy/roles/apache/meta/main.yml
deploy/roles/apache/tasks/main.yml
deploy/roles/apache/templates/httpd.conf.j2
deploy/roles/citus/defaults/main.yml
deploy/roles/citus/meta/main.yml
deploy/roles/citus/tasks/main.yml
deploy/roles/citus/templates/citus_cpu.conf.j2
deploy/roles/citus/templates/citus_limits.conf.j2
deploy/roles/citus/templates/citus_memory.conf.j2
deploy/roles/citus/templates/pgpass.j2
deploy/roles/citus_coordinator/defaults/main.yml
deploy/roles/citus_coordinator/tasks/main.yml
deploy/roles/citus_coordinator/templates/archive-wal-file.j2
deploy/roles/citus_coordinator_standby/defaults/main.yml
deploy/roles/citus_coordinator_standby/handlers/main.yml
deploy/roles/citus_coordinator_standby/tasks/main.yml
deploy/roles/citus_coordinator_standby/templates/recovery.conf.j2
deploy/roles/clouseau/tasks/main.yml
deploy/roles/common/defaults/main.yml
deploy/roles/common/tasks/main.yml
deploy/roles/devtools/tasks/main.yml
deploy/roles/devtools/templates/devtools-2.repo.j2
deploy/roles/devtools/templates/devtools-2.sh.j2
deploy/roles/devtools6/tasks/main.yml
deploy/roles/devtools6/templates/devtools-6.repo.j2
deploy/roles/devtools6/templates/devtools-6.sh.j2
deploy/roles/devtools7/tasks/main.yml
deploy/roles/devtools7/templates/devtools-7.repo.j2
deploy/roles/devtools7/templates/devtools-7.sh.j2
deploy/roles/elasticsearch-config/defaults/main.yml
deploy/roles/elasticsearch-config/meta/main.yml
deploy/roles/elasticsearch-config/tasks/main.yml
deploy/roles/elasticsearch-config/templates/99-elasticsearch.conf.j2
deploy/roles/elasticsearch-config/templates/elasticsearch.j2
deploy/roles/elasticsearch-config/templates/elasticsearch.yml.j2
deploy/roles/elasticsearch-config/templates/logging.yml.j2
deploy/roles/elasticsearch-config/templates/role_mapping.yml.j2
deploy/roles/elasticsearch-config/templates/roles.1.x.yml.j2
deploy/roles/elasticsearch-config/templates/roles.yml.j2
deploy/roles/elasticsearch-config/templates/shield_logging.yml.j2
deploy/roles/elasticsearch/defaults/main.yml
deploy/roles/elasticsearch/meta/main.yml
deploy/roles/elasticsearch/tasks/main.yml
deploy/roles/elasticsearch/templates/elasticsearch.repo
deploy/roles/emacs/tasks/main.yaml
deploy/roles/eod/defaults/main.yaml
deploy/roles/eod/handlers/main.yaml
deploy/roles/eod/tasks/install_eod.yaml
deploy/roles/eod/tasks/main.yaml
deploy/roles/eod/tasks/upgrade_eod.yaml
deploy/roles/eod/templates/20-no-show-proxy-dialog.pkla
deploy/roles/eod/templates/XDMCP_Query.cfg
deploy/roles/eod/templates/admin_settings.cfg.j2
deploy/roles/eod/templates/akeys
deploy/roles/eod/templates/cluster.cfg.j2
deploy/roles/eod/templates/custom.conf
deploy/roles/eod/templates/exceed-connection-server
deploy/roles/eod/templates/gdm.schemas.j2
deploy/roles/eod/templates/inittab
deploy/roles/eod/templates/install_eod_server.exp
deploy/roles/eod/templates/node.cfg.j2
deploy/roles/eod/templates/system-auth-ac
deploy/roles/eod/templates/xorg.conf
deploy/roles/epel/defaults/main.yml
deploy/roles/epel/tasks/main.yml
deploy/roles/evince/tasks/main.yaml
deploy/roles/gauss/defaults/main.yaml
deploy/roles/gauss/tasks/main.yaml
deploy/roles/gauss/templates/install_gauss.exp
deploy/roles/glusterfs/meta/main.yml
deploy/roles/glusterfs/tasks/main.yml
deploy/roles/gocd/defaults/main.yaml
deploy/roles/gocd/handlers/main.yml
deploy/roles/gocd/meta/main.yaml
deploy/roles/gocd/tasks/main.yaml
deploy/roles/gocd/templates/deployment.properties
deploy/roles/gocd/templates/go-agent
deploy/roles/gocd_server/defaults/main.yml
deploy/roles/gocd_server/handlers/main.yml
deploy/roles/gocd_server/meta/main.yml
deploy/roles/gocd_server/tasks/main.yml
deploy/roles/gocd_server/templates/go-server.j2
deploy/roles/intellij/defaults/main.yml
deploy/roles/intellij/files/idea.png
deploy/roles/intellij/meta/main.yml
deploy/roles/intellij/tasks/main.yml
deploy/roles/intellij/templates/idea.desktop.j2
deploy/roles/iptables/defaults/main.yml
deploy/roles/iptables/meta/main.yml
deploy/roles/iptables/tasks/main.yml
deploy/roles/iptables/tasks/rhel_7.yml
deploy/roles/jdbc/defaults/main.yml
deploy/roles/jdbc/meta/main.yml
deploy/roles/jdbc/tasks/main.yml
deploy/roles/jdk/defaults/main.yml
deploy/roles/jdk/tasks/main.yml
deploy/roles/jdk/templates/deployment.config
deploy/roles/jdk/templates/jdk.sh.j2
deploy/roles/julia/tasks/main.yml
deploy/roles/kerberos/defaults/main.yml
deploy/roles/kerberos/tasks/main.yml
deploy/roles/kerberos/templates/krb5.conf
deploy/roles/kerberos_apache/tasks/main.yml
deploy/roles/kerberos_server/defaults/main.yml
deploy/roles/kerberos_server/meta/main.yml
deploy/roles/kerberos_server/tasks/main.yml
deploy/roles/kerberos_server/templates/kdc.conf
deploy/roles/kerberos_server/templates/krb5.conf
deploy/roles/kibana-config/defaults/main.yml
deploy/roles/kibana-config/meta/main.yml
deploy/roles/kibana-config/tasks/main.yml
deploy/roles/kibana-config/templates/kibana.4.1.yml.j2
deploy/roles/kibana-config/templates/kibana.yml.j2
deploy/roles/kibana/defaults/main.yml
deploy/roles/kibana/meta/main.yml
deploy/roles/kibana/tasks/main.yml
deploy/roles/kibana/templates/kibana.conf
deploy/roles/kibana/templates/kibana.repo.j2
deploy/roles/log-courier/defaults/main.yml
deploy/roles/log-courier/meta/main.yml
deploy/roles/log-courier/tasks/main.yml
deploy/roles/log-courier/templates/log-courier.conf.j2
deploy/roles/log-courier/templates/log-courier.repo
deploy/roles/logstash-config/defaults/main.yml
deploy/roles/logstash-config/files/12-example-filter.conf
deploy/roles/logstash-config/meta/main.yml
deploy/roles/logstash-config/tasks/main.yml
deploy/roles/logstash-config/templates/01-logstash-courier-input.conf
deploy/roles/logstash-config/templates/02-tcp-input.conf
deploy/roles/logstash-config/templates/10-syslog.conf
deploy/roles/logstash-config/templates/20-elasticsearch-input.conf.j2
deploy/roles/logstash-config/templates/30-elasticsearch-output.1.5.conf.j2
deploy/roles/logstash-config/templates/30-elasticsearch-output.conf.j2
deploy/roles/logstash/defaults/main.yml
deploy/roles/logstash/meta/main.yml
deploy/roles/logstash/tasks/main.yml
deploy/roles/logstash/templates/logstash.repo
deploy/roles/math_lm/defaults/main.yml
deploy/roles/math_lm/tasks/main.yml
deploy/roles/math_lm/templates/mathpass
deploy/roles/matlab/defaults/main.yml
deploy/roles/matlab/tasks/main.yml
deploy/roles/matlab/templates/installer_input.txt
deploy/roles/matlab/templates/mlm.opt
deploy/roles/maven/defaults/main.yml
deploy/roles/maven/meta/main.yml
deploy/roles/maven/tasks/main.yml
deploy/roles/maven/templates/maven.sh.j2
deploy/roles/mesos_agent/defaults/main.yml
deploy/roles/mesos_agent/handlers/main.yml
deploy/roles/mesos_agent/meta/main.yml
deploy/roles/mesos_agent/tasks/main.yml
deploy/roles/mesos_agent/templates/default_container_dns.j2
deploy/roles/mesos_agent/templates/default_container_info.j2
deploy/roles/mesos_agent/templates/zk.j2
deploy/roles/mesos_master/defaults/main.yml
deploy/roles/mesos_master/handlers/main.yml
deploy/roles/mesos_master/meta/main.yml
deploy/roles/mesos_master/tasks/main.yml
deploy/roles/mesos_master/tasks/post_deploy_mesos_master.yml
deploy/roles/mesos_master/templates/marathon.j2
deploy/roles/mesos_master/templates/mesos_credentials.j2
deploy/roles/mesos_master/templates/myid
deploy/roles/mesos_master/templates/quorum.j2
deploy/roles/mesos_master/templates/zk.j2
deploy/roles/mesos_master/templates/zk.marathon.j2
deploy/roles/mesos_master/templates/zoo.cfg
deploy/roles/monitor-research/defaults/main.yml
deploy/roles/monitor-research/tasks/main.yml
deploy/roles/neo4j/defaults/main.yml
deploy/roles/neo4j/handlers/main.yml
deploy/roles/neo4j/meta/main.yml
deploy/roles/neo4j/tasks/main.yml
deploy/roles/neo4j/templates/neo4j-env.sh.j2
deploy/roles/neo4j/templates/neo4j.conf.j2
deploy/roles/neo4j/templates/neo4j.log.j2
deploy/roles/neo4j/templates/neo4j.pid.j2
deploy/roles/neo4j/templates/neo4j.upstart.j2
deploy/roles/nginx/defaults/main.yml
deploy/roles/nginx/handlers/main.yml
deploy/roles/nginx/meta/main.yml
deploy/roles/nginx/tasks/main.yml
deploy/roles/nginx/templates/default.conf.j2
deploy/roles/nginx/templates/nginx.conf.j2
deploy/roles/nginx/templates/nginx.j2
deploy/roles/nodejs/defaults/main.yml
deploy/roles/nodejs/meta/main.yml
deploy/roles/nodejs/tasks/main.yml
deploy/roles/nodejs/templates/nvm.sh.j2
deploy/roles/ntp/defaults/main.yml
deploy/roles/ntp/tasks/main.yml
deploy/roles/odbc/defaults/main.yaml
deploy/roles/odbc/meta/main.yml
deploy/roles/odbc/tasks/main.yaml
deploy/roles/odbc/templates/freetds.conf
deploy/roles/odbc/templates/odbc.ini
deploy/roles/odbc/templates/odbcinst.ini
deploy/roles/open_office/defaults/main.yaml
deploy/roles/open_office/tasks/main.yaml
deploy/roles/openldap/handlers/main.yml
deploy/roles/openldap/meta/main.yml
deploy/roles/openldap/tasks/main.yml
deploy/roles/openldap/templates/domain.ldif
deploy/roles/openldap/templates/ldap.conf.j2
deploy/roles/openldap/templates/slapd.access.j2
deploy/roles/openldap/templates/slapd.conf.j2
deploy/roles/pdfgrep/defaults/main.yml
deploy/roles/pdfgrep/tasks/main.yml
deploy/roles/pem-client/defaults/main.yml
deploy/roles/pem-client/tasks/main.yml
deploy/roles/pentaho/defaults/main.yml
deploy/roles/pentaho/meta/main.yml
deploy/roles/pentaho/tasks/main.yml
deploy/roles/pentaho/templates/pentaho.desktop.j2
deploy/roles/postgresql-client/defaults/main.yml
deploy/roles/postgresql-client/tasks/main.yml
deploy/roles/postgresql-client/templates/postgres.sh.j2
deploy/roles/postgresql-dbs/defaults/main.yml
deploy/roles/postgresql-dbs/tasks/main.yml
deploy/roles/postgresql-server-config/defaults/main.yml
deploy/roles/postgresql-server-config/handlers/main.yml
deploy/roles/postgresql-server-config/meta/main.yml
deploy/roles/postgresql-server-config/tasks/create_functions.yml
deploy/roles/postgresql-server-config/tasks/main.yml
deploy/roles/postgresql-server/README.md
deploy/roles/postgresql-server/defaults/main.yml
deploy/roles/postgresql-server/handlers/main.yml
deploy/roles/postgresql-server/meta/main.yml
deploy/roles/postgresql-server/tasks/install_edb.yml
deploy/roles/postgresql-server/tasks/main.yml
deploy/roles/postgresql-server/templates/config_param.j2
deploy/roles/postgresql-server/templates/environment.conf.j2
deploy/roles/postgresql-server/templates/pg_hba.conf.j2
deploy/roles/postgresql-server/templates/pg_ident.conf.j2
deploy/roles/postgresql-server/templates/pgplus_env.sh.j2
deploy/roles/postgresql-server/templates/postgresql.conf.10.j2
deploy/roles/postgresql-server/templates/postgresql.conf.94.j2
deploy/roles/postgresql-server/templates/postgresql.conf.95.j2
deploy/roles/postgresql-server/templates/postgresql.conf.96.j2
deploy/roles/postgresql-server/vars/edb.yml
deploy/roles/postgresql-server/vars/rhel_7.yml
deploy/roles/psql-authnz/tasks/main.yml
deploy/roles/puppet_disable/tasks/main.yml
deploy/roles/pycharm/defaults/main.yaml
deploy/roles/pycharm/meta/main.yml
deploy/roles/pycharm/tasks/main.yml
deploy/roles/python-build/defaults/main.yml
deploy/roles/python-build/tasks/main.yml
deploy/roles/python-libs/defaults/main.yml
deploy/roles/python-libs/tasks/main.yml
deploy/roles/python/defaults/main.yml
deploy/roles/python/tasks/main.yml
deploy/roles/python27-scl/README.md
deploy/roles/python27-scl/defaults/main.yml
deploy/roles/python27-scl/handlers/main.yml
deploy/roles/python27-scl/meta/main.yml
deploy/roles/python27-scl/tasks/main.yml
deploy/roles/python27-scl/templates/scl_enable-python27.sh.j2
deploy/roles/python27-scl/tests/inventory
deploy/roles/python27-scl/tests/test.yml
deploy/roles/python27-scl/vars/main.yml
deploy/roles/python36-scl/README.md
deploy/roles/python36-scl/defaults/main.yml
deploy/roles/python36-scl/handlers/main.yml
deploy/roles/python36-scl/meta/main.yml
deploy/roles/python36-scl/tasks/main.yml
deploy/roles/python36-scl/templates/scl_enable-python36.sh.j2
deploy/roles/python36-scl/tests/inventory
deploy/roles/python36-scl/tests/test.yml
deploy/roles/python36-scl/vars/main.yml
deploy/roles/r-core/defaults/main.yml
deploy/roles/r-core/meta/main.yml
deploy/roles/r-core/tasks/main.yml
deploy/roles/r-libs/defaults/main.yml
deploy/roles/r-libs/meta/main.yml
deploy/roles/r-libs/tasks/main.yml
deploy/roles/r-shiny-config/defaults/main.yml
deploy/roles/r-shiny-config/meta/main.yml
deploy/roles/r-shiny-config/tasks/main.yml
deploy/roles/r-shiny-config/templates/shiny-server.conf.j2
deploy/roles/r-shiny/defaults/main.yml
deploy/roles/r-shiny/handlers/main.yml
deploy/roles/r-shiny/meta/main.yml
deploy/roles/r-shiny/tasks/main.yml
deploy/roles/r-shiny/templates/shiny-server.conf.j2
deploy/roles/r-studio-desktop/tasks/main.yml
deploy/roles/r-studio-server-config/defaults/main.yml
deploy/roles/r-studio-server-config/meta/main.yml
deploy/roles/r-studio-server-config/tasks/main.yml
deploy/roles/r-studio-server-config/templates/ip-rules.j2
deploy/roles/r-studio-server-config/templates/login.html.j2
deploy/roles/r-studio-server-config/templates/rserver.conf.j2
deploy/roles/r-studio-server-config/templates/rsession.conf.j2
deploy/roles/r-studio-server-config/templates/rstudio_server.sh.j2
deploy/roles/r-studio-server-config/templates/secure-proxy-user-header.j2
deploy/roles/r-studio-server/defaults/main.yml
deploy/roles/r-studio-server/meta/main.yml
deploy/roles/r-studio-server/tasks/main.yml
deploy/roles/r/defaults/main.yml
deploy/roles/r/meta/main.yml
deploy/roles/r/tasks/main.yml
deploy/roles/redis/defaults/main.yml
deploy/roles/redis/meta/main.yml
deploy/roles/redis/tasks/main.yml
deploy/roles/redis/templates/redis.conf.j2
deploy/roles/revolution-r/defaults/main.yml
deploy/roles/revolution-r/tasks/main.yml
deploy/roles/revolution-r/templates/revor.sh.j2
deploy/roles/ruby/defaults/main.yml
deploy/roles/ruby/tasks/.main.yml.swo
deploy/roles/ruby/tasks/main.yml
deploy/roles/sas/defaults/main.yml
deploy/roles/sas/meta/main.yml
deploy/roles/sas/tasks/main.yml
deploy/roles/sas/templates/sas_init.d_template.j2
deploy/roles/sas/templates/sas_template.txt.j2
deploy/roles/scala/defaults/main.yml
deploy/roles/scala/meta/main.yml
deploy/roles/scala/tasks/main.yml
deploy/roles/scala/templates/sbt.sh.j2
deploy/roles/scala/templates/scala.sh.j2
deploy/roles/shared/handlers/main.yml
deploy/roles/shared/handlers/rhel6.yml
deploy/roles/shared/handlers/rhel7.yml
deploy/roles/spark/defaults/main.yml
deploy/roles/spark/meta/main.yml
deploy/roles/spark/tasks/main.yml
deploy/roles/spark/templates/log4j.properties
deploy/roles/spark/templates/spark-bin.j2
deploy/roles/spark/templates/spark-defaults.conf.j2
deploy/roles/spark/templates/spark-env.sh.j2
deploy/roles/sqitch/defaults/main.yml
deploy/roles/sqitch/tasks/main.yml
deploy/roles/stata/defaults/main.yaml
deploy/roles/stata/tasks/main.yaml
deploy/roles/stata/templates/configure_stata.sh
deploy/roles/stata/templates/stataupdate.do.j2
deploy/roles/stata/templates/sysprofile.do.j2
deploy/roles/stattransfer/defaults/main.yaml
deploy/roles/stattransfer/tasks/main.yaml
deploy/roles/stattransfer/templates/configure_stattransfer.sh
deploy/roles/stattransfer/templates/license1282.txt
deploy/roles/sublime/defaults/main.yaml
deploy/roles/sublime/tasks/main.yaml
deploy/roles/sublime/templates/sublime.desktop.j2
deploy/roles/talend/defaults/main.yml
deploy/roles/talend/tasks/main.yml
deploy/roles/talend/templates/TOS_DI-linux-gtk-x86.ini.j2
deploy/roles/talend/templates/talend.desktop.j2
deploy/roles/tesseract/defaults/main.yaml
deploy/roles/tesseract/tasks/main.yaml
deploy/roles/ultra-edit/defaults/main.yml
deploy/roles/ultra-edit/tasks/main.yml
deploy/roles/umask/tasks/main.yml
deploy/templates/enclave_proxy.conf
deploy/templates/enclave_proxy.php
deploy/templates/enclave_proxy_restricted.php
deploy/templates/proxy.conf
deploy/templates/proxy.html
deploy/upgrade_citus_enterprise.yml
deploy/upgrade_db_server.yml
[3 further paths beside the cited file not listed]

Per-directory path counts:
.: 9
.devcontainer: 10
.devcontainer/scripts: 1
deploy: 35
deploy/group_vars/all: 1
deploy/group_vars/all_db: 1
deploy/group_vars/citus_coordinator: 1
deploy/group_vars/citus_coordinator_standby: 1
deploy/group_vars/citus_worker: 1
deploy/library: 2
deploy/roles/apache/defaults: 1
deploy/roles/apache/handlers: 1
deploy/roles/apache/meta: 1
deploy/roles/apache/tasks: 1
deploy/roles/apache/templates: 1
deploy/roles/citus/defaults: 1
deploy/roles/citus/meta: 1
deploy/roles/citus/tasks: 1
deploy/roles/citus/templates: 4
deploy/roles/citus_coordinator/defaults: 1
deploy/roles/citus_coordinator/tasks: 1
deploy/roles/citus_coordinator/templates: 1
deploy/roles/citus_coordinator_standby/defaults: 1
deploy/roles/citus_coordinator_standby/handlers: 1
deploy/roles/citus_coordinator_standby/tasks: 1
deploy/roles/citus_coordinator_standby/templates: 1
deploy/roles/clouseau/tasks: 1
deploy/roles/common/defaults: 1
deploy/roles/common/tasks: 1
deploy/roles/devtools/tasks: 1
deploy/roles/devtools/templates: 2
deploy/roles/devtools6/tasks: 1
deploy/roles/devtools6/templates: 2
deploy/roles/devtools7/tasks: 1
deploy/roles/devtools7/templates: 2
deploy/roles/elasticsearch-config/defaults: 1
deploy/roles/elasticsearch-config/meta: 1
deploy/roles/elasticsearch-config/tasks: 1
deploy/roles/elasticsearch-config/templates: 8
deploy/roles/elasticsearch/defaults: 1
deploy/roles/elasticsearch/meta: 1
deploy/roles/elasticsearch/tasks: 1
deploy/roles/elasticsearch/templates: 1
deploy/roles/emacs/tasks: 1
deploy/roles/eod/defaults: 1
deploy/roles/eod/handlers: 1
deploy/roles/eod/tasks: 3
deploy/roles/eod/templates: 13
deploy/roles/epel/defaults: 1
deploy/roles/epel/tasks: 1
deploy/roles/evince/tasks: 1
deploy/roles/gauss/defaults: 1
deploy/roles/gauss/tasks: 1
deploy/roles/gauss/templates: 1
deploy/roles/glusterfs/meta: 1
deploy/roles/glusterfs/tasks: 1
deploy/roles/gocd/defaults: 1
deploy/roles/gocd/handlers: 1
deploy/roles/gocd/meta: 1
deploy/roles/gocd/tasks: 1
deploy/roles/gocd/templates: 2
deploy/roles/gocd_server/defaults: 1
deploy/roles/gocd_server/handlers: 1
deploy/roles/gocd_server/meta: 1
deploy/roles/gocd_server/tasks: 1
deploy/roles/gocd_server/templates: 1
deploy/roles/intellij/defaults: 1
deploy/roles/intellij/files: 1
deploy/roles/intellij/meta: 1
deploy/roles/intellij/tasks: 1
deploy/roles/intellij/templates: 1
deploy/roles/iptables/defaults: 1
deploy/roles/iptables/meta: 1
deploy/roles/iptables/tasks: 2
deploy/roles/jdbc/defaults: 1
deploy/roles/jdbc/meta: 1
deploy/roles/jdbc/tasks: 1
deploy/roles/jdk/defaults: 1
deploy/roles/jdk/tasks: 1
deploy/roles/jdk/templates: 2
deploy/roles/julia/tasks: 1
deploy/roles/kerberos/defaults: 1
deploy/roles/kerberos/tasks: 1
deploy/roles/kerberos/templates: 1
deploy/roles/kerberos_apache/tasks: 1
deploy/roles/kerberos_server/defaults: 1
deploy/roles/kerberos_server/meta: 1
deploy/roles/kerberos_server/tasks: 1
deploy/roles/kerberos_server/templates: 2
deploy/roles/kibana-config/defaults: 1
deploy/roles/kibana-config/meta: 1
deploy/roles/kibana-config/tasks: 1
deploy/roles/kibana-config/templates: 2
deploy/roles/kibana/defaults: 1
deploy/roles/kibana/meta: 1
deploy/roles/kibana/tasks: 1
deploy/roles/kibana/templates: 2
deploy/roles/log-courier/defaults: 1
deploy/roles/log-courier/meta: 1
deploy/roles/log-courier/tasks: 1
deploy/roles/log-courier/templates: 2
deploy/roles/logstash-config/defaults: 1
deploy/roles/logstash-config/files: 1
deploy/roles/logstash-config/meta: 1
deploy/roles/logstash-config/tasks: 1
deploy/roles/logstash-config/templates: 6
deploy/roles/logstash/defaults: 1
deploy/roles/logstash/meta: 1
deploy/roles/logstash/tasks: 1
deploy/roles/logstash/templates: 1
deploy/roles/math_lm/defaults: 1
deploy/roles/math_lm/tasks: 1
deploy/roles/math_lm/templates: 1
deploy/roles/matlab/defaults: 1
deploy/roles/matlab/tasks: 1
deploy/roles/matlab/templates: 2
deploy/roles/maven/defaults: 1
deploy/roles/maven/meta: 1
deploy/roles/maven/tasks: 1
deploy/roles/maven/templates: 1
deploy/roles/mesos_agent/defaults: 1
deploy/roles/mesos_agent/handlers: 1
deploy/roles/mesos_agent/meta: 1
deploy/roles/mesos_agent/tasks: 1
deploy/roles/mesos_agent/templates: 3
deploy/roles/mesos_master/defaults: 1
deploy/roles/mesos_master/handlers: 1
deploy/roles/mesos_master/meta: 1
deploy/roles/mesos_master/tasks: 2
deploy/roles/mesos_master/templates: 7
deploy/roles/monitor-research/defaults: 1
deploy/roles/monitor-research/tasks: 1
deploy/roles/neo4j/defaults: 1
deploy/roles/neo4j/handlers: 1
deploy/roles/neo4j/meta: 1
deploy/roles/neo4j/tasks: 1
deploy/roles/neo4j/templates: 5
deploy/roles/nginx/defaults: 1
deploy/roles/nginx/handlers: 1
deploy/roles/nginx/meta: 1
deploy/roles/nginx/tasks: 1
deploy/roles/nginx/templates: 3
deploy/roles/nodejs/defaults: 1
deploy/roles/nodejs/meta: 1
deploy/roles/nodejs/tasks: 1
deploy/roles/nodejs/templates: 1
deploy/roles/ntp/defaults: 1
deploy/roles/ntp/tasks: 1
deploy/roles/odbc/defaults: 1
deploy/roles/odbc/meta: 1
deploy/roles/odbc/tasks: 1
deploy/roles/odbc/templates: 3
deploy/roles/open_office/defaults: 1
deploy/roles/open_office/tasks: 1
deploy/roles/openldap/handlers: 1
deploy/roles/openldap/meta: 1
deploy/roles/openldap/tasks: 1
deploy/roles/openldap/templates: 4
deploy/roles/pdfgrep/defaults: 1
deploy/roles/pdfgrep/tasks: 1
deploy/roles/pem-client/defaults: 1
deploy/roles/pem-client/tasks: 1
deploy/roles/pentaho/defaults: 1
deploy/roles/pentaho/meta: 1
deploy/roles/pentaho/tasks: 1
deploy/roles/pentaho/templates: 1
deploy/roles/postgresql-client/defaults: 1
deploy/roles/postgresql-client/tasks: 1
deploy/roles/postgresql-client/templates: 1
deploy/roles/postgresql-dbs/defaults: 1
deploy/roles/postgresql-dbs/tasks: 1
deploy/roles/postgresql-server: 1
deploy/roles/postgresql-server-config/defaults: 1
deploy/roles/postgresql-server-config/handlers: 1
deploy/roles/postgresql-server-config/meta: 1
deploy/roles/postgresql-server-config/tasks: 2
deploy/roles/postgresql-server/defaults: 1
deploy/roles/postgresql-server/handlers: 1
deploy/roles/postgresql-server/meta: 1
deploy/roles/postgresql-server/tasks: 2
deploy/roles/postgresql-server/templates: 9
deploy/roles/postgresql-server/vars: 2
deploy/roles/psql-authnz/tasks: 1
deploy/roles/puppet_disable/tasks: 1
deploy/roles/pycharm/defaults: 1
deploy/roles/pycharm/meta: 1
deploy/roles/pycharm/tasks: 1
deploy/roles/python-build/defaults: 1
deploy/roles/python-build/tasks: 1
deploy/roles/python-libs/defaults: 1
deploy/roles/python-libs/tasks: 1
deploy/roles/python/defaults: 1
deploy/roles/python/tasks: 1
deploy/roles/python27-scl: 1
deploy/roles/python27-scl/defaults: 1
deploy/roles/python27-scl/handlers: 1
deploy/roles/python27-scl/meta: 1
deploy/roles/python27-scl/tasks: 1
deploy/roles/python27-scl/templates: 1
deploy/roles/python27-scl/tests: 2
deploy/roles/python27-scl/vars: 1
deploy/roles/python36-scl: 1
deploy/roles/python36-scl/defaults: 1
deploy/roles/python36-scl/handlers: 1
deploy/roles/python36-scl/meta: 1
deploy/roles/python36-scl/tasks: 1
deploy/roles/python36-scl/templates: 1
deploy/roles/python36-scl/tests: 2
deploy/roles/python36-scl/vars: 1
deploy/roles/r-core/defaults: 1
deploy/roles/r-core/meta: 1
deploy/roles/r-core/tasks: 1
deploy/roles/r-libs/defaults: 1
deploy/roles/r-libs/meta: 1
deploy/roles/r-libs/tasks: 1
deploy/roles/r-shiny-config/defaults: 1
deploy/roles/r-shiny-config/meta: 1
deploy/roles/r-shiny-config/tasks: 1
deploy/roles/r-shiny-config/templates: 1
deploy/roles/r-shiny/defaults: 1
deploy/roles/r-shiny/handlers: 1
deploy/roles/r-shiny/meta: 1
deploy/roles/r-shiny/tasks: 1
deploy/roles/r-shiny/templates: 1
deploy/roles/r-studio-desktop/tasks: 1
deploy/roles/r-studio-server-config/defaults: 1
deploy/roles/r-studio-server-config/meta: 1
deploy/roles/r-studio-server-config/tasks: 1
deploy/roles/r-studio-server-config/templates: 6
deploy/roles/r-studio-server/defaults: 1
deploy/roles/r-studio-server/meta: 1
deploy/roles/r-studio-server/tasks: 1
deploy/roles/r/defaults: 1
deploy/roles/r/meta: 1
deploy/roles/r/tasks: 1
deploy/roles/redis/defaults: 1
deploy/roles/redis/meta: 1
deploy/roles/redis/tasks: 1
deploy/roles/redis/templates: 1
deploy/roles/revolution-r/defaults: 1
deploy/roles/revolution-r/tasks: 1
deploy/roles/revolution-r/templates: 1
deploy/roles/ruby/defaults: 1
deploy/roles/ruby/tasks: 2
deploy/roles/sas/defaults: 1
deploy/roles/sas/meta: 1
deploy/roles/sas/tasks: 1
deploy/roles/sas/templates: 2
deploy/roles/scala/defaults: 1
deploy/roles/scala/meta: 1
deploy/roles/scala/tasks: 1
deploy/roles/scala/templates: 2
deploy/roles/shared/handlers: 3
deploy/roles/spark/defaults: 1
deploy/roles/spark/meta: 1
deploy/roles/spark/tasks: 1
deploy/roles/spark/templates: 4
deploy/roles/sqitch/defaults: 1
deploy/roles/sqitch/tasks: 1
deploy/roles/stata/defaults: 1
deploy/roles/stata/tasks: 1
deploy/roles/stata/templates: 3
deploy/roles/stattransfer/defaults: 1
deploy/roles/stattransfer/tasks: 1
deploy/roles/stattransfer/templates: 2
deploy/roles/sublime/defaults: 1
deploy/roles/sublime/tasks: 1
deploy/roles/sublime/templates: 1
deploy/roles/talend/defaults: 1
deploy/roles/talend/tasks: 1
deploy/roles/talend/templates: 2
deploy/roles/tesseract/defaults: 1
deploy/roles/tesseract/tasks: 1
deploy/roles/ultra-edit/defaults: 1
deploy/roles/ultra-edit/tasks: 1
deploy/roles/umask/tasks: 1
deploy/templates: 5
test: 5
test/files/gocd: 6
test/files/mesos: 5
test/files/mesos/simple_app_aci: 1
test/files/mesos/simple_app_aci/rootfs/bin: 1
test/files/mesos/simple_app_aci/rootfs/etc: 1
```

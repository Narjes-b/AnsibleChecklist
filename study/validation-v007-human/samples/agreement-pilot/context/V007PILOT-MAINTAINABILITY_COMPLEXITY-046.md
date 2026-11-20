# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-046

- Repository: `usegalaxy-eu/infrastructure-playbook`
- Commit: `13681d4e758b42aeeb7e12aac62243e76a5c04fb`
- Family: Maintainability/complexity
- Rule: `ansibleguard/unused-handler`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `sn09.yml` (reported anchor line 73)
- Object: `source_location` `b367613128b76fbab44391bdb59a4eafad373db905bcc625b93b117fc4ec27d0`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–410 of 410:

```text
    1 | ---
    2 | - name: UseGalaxy.eu
    3 |   hosts: sn09
    4 |   become: true
    5 |   become_user: root
    6 |   vars:
    7 |     # The full internal name.
    8 |     hostname: sn09.galaxyproject.eu
    9 |     # The nginx user needed into the galaxyproject.nginx role
   10 |     nginx_conf_user: galaxy
   11 |     # This server has multiple CNAMEs that are important. Additionally it
   12 |     # provides proxying for many of the other services run by Galaxy Europe.
   13 |     # These server_names are passed to certbot. They generally should not need
   14 |     # to be updated unless you add a new domain. They *only* work with the
   15 |     # route53 provider, so if we want to do usegalaxy.xy, it may require
   16 |     # refactoring / multiple certbot runs.
   17 |     #
   18 |     #
   19 |     # The best way to expand them is to run the playbook, it will leave a message with the command it would have run (look for `skipped, since /etc/letsencrypt/renewal/usegalaxy.eu.conf exists`)
   20 |     #
   21 |     # Then take this command to the command line (root@sn04) and run it with `--expand`. E.g. (DO NOT COPY PASTE (in case the config changes))
   22 |     #
   23 |     # $ /opt/certbot/bin/certbot certonly --non-interactive --dns-route53 \
   24 |     #     -m security@usegalaxy.eu --agree-tos -d 'usegalaxy.eu,*.usegalaxy.eu,galaxyproject.eu,*.galaxyproject.eu,*.interactivetoolentrypoint.interactivetool.usegalaxy.eu,*.interactivetoolentrypoint.interactivetool.live.usegalaxy.eu,*.interactivetoolentrypoint.interactivetool.test.usegalaxy.eu' --expand
   25 |     # Saving debug log to /var/log/letsencrypt/letsencrypt.log
   26 |     # Credentials found in config file: ~/.aws/config
   27 |     # ....
   28 |     # IMPORTANT NOTES:
   29 |     #  - Congratulations! Your certificate and chain have been saved at:
   30 |     #
   31 |     # And you're done expanding the certs.
   32 |     #
   33 |     # The nginx user needed into the galaxyproject.nginx role
   34 |     server_names:
   35 |       - 'usegalaxy.eu'
   36 |       - '*.usegalaxy.eu'
   37 |       - 'galaxyproject.eu'
   38 |       - '*.galaxyproject.eu'
   39 |       - '*.ep.interactivetool.usegalaxy.eu'
   40 |       - '*.ep.interactivetool.live.usegalaxy.eu'
   41 |       - '*.ep.interactivetool.test.usegalaxy.eu'
   42 |       - '*.aqua.usegalaxy.eu'
   43 |       - '*.ep.interactivetool.aqua.usegalaxy.eu'
   44 |       - '*.ecology.usegalaxy.eu'
   45 |       - '*.ep.interactivetool.ecology.usegalaxy.eu'
   46 |       - '*.earth-system.usegalaxy.eu'
   47 |       - '*.ep.interactivetool.earth-system.usegalaxy.eu'
   48 |       - '*.eirene.usegalaxy.eu'
   49 |       - '*.ep.interactivetool.eirene.usegalaxy.eu'
   50 |   vars_files:
   51 |     - group_vars/sn09/sn09.yml
   52 |     - group_vars/sn09/themes_conf.yml
   53 |     - group_vars/sn09/subdomains.yml
   54 |     - group_vars/sn09/toolmsg.yml
   55 |     - group_vars/tiaas.yml # All of the training infrastructure
   56 |     - group_vars/gxconfig.yml # The base galaxy configuration
   57 |     - group_vars/toolbox.yml # User controlled toolbox
   58 |     - secret_group_vars/sentry.yml # Sentry SDK init url
   59 |     - secret_group_vars/aws.yml # AWS creds
   60 |     - secret_group_vars/pulsar.yml # Pulsar + MQ Connections
   61 |     - secret_group_vars/oidc.yml # OIDC credentials (ELIXIR, keycloak)
   62 |     - secret_group_vars/object_store.yml # Object Store credentils (S3 etc ...)
   63 |     - secret_group_vars/db-main.yml # DB URL + some postgres stuff
   64 |     - secret_group_vars/file_sources.yml # file_sources_conf.yml creds
   65 |     - secret_group_vars/all.yml # All of the other assorted secrets...
   66 |     - secret_group_vars/keys.yml # SSH keys
   67 |     - templates/galaxy/config/job_conf.yml
   68 |     - mounts/dest/all.yml
   69 |     - mounts/mountpoints.yml
   70 |   collections:
   71 |     - devsec.hardening
   72 |   handlers:
   73 |     - name: Restart Galaxy
   74 |       ansible.builtin.shell: |
   75 |         cd /opt/galaxy/ && source /opt/galaxy/.bashrc  && /usr/bin/gxadmin gunicorn handler-restart && sudo -u galaxy /usr/bin/galaxy-sync-to-nfs && systemctl restart galaxy-handler@* && systemctl restart galaxy-workflow-scheduler@*
   76 |       listen: 'restart galaxy'
   77 |   pre_tasks:
   78 |     # This should be the 1st pretask as the rest of the tasks are dependent on it.
   79 |     - name: Install EPEL-release
   80 |       ansible.builtin.package:
   81 |         name: epel-release
   82 |         state: present
   83 | 
   84 |     - name: Install Dependencies
   85 |       ansible.builtin.dnf:
   86 |         name:
   87 |           [
   88 |             'git',
   89 |             'python3-psycopg2',
   90 |             'bc',
   91 |             'python3-devel',
   92 |             'rsyslog',
   93 |             'rsyslog-gnutls',
   94 |             'byobu',
   95 |           ]
   96 |         state: present
   97 | 
   98 |     - name: Install python3-virtualenv from enable crb repository (this repo is the one that provides the package)
   99 |       ansible.builtin.dnf:
  100 |         name: python3-virtualenv
  101 |         enablerepo: crb
  102 |         state: present
  103 | 
  104 |     - name: Disable SELinux
  105 |       selinux:
  106 |         state: disabled
  107 | 
  108 |     - name: Install repository key (PostgreSQL v11 and above)
  109 |       ansible.builtin.rpm_key:
  110 |         key: https://download.postgresql.org/pub/repos/yum/keys/PGDG-RPM-GPG-KEY-RHEL
  111 |         state: present
  112 | 
  113 |     - name: Install pgdg repository package (RedHat)
  114 |       ansible.builtin.yum:
  115 |         name: >-
  116 |           https://download.postgresql.org/pub/repos/yum/reporpms/{{ postgresql_pgdg_shortfamilies[ansible_distribution]
  117 |             | default("EL") }}-{{ ansible_distribution_major_version }}-{{ ansible_architecture }}/pgdg-{{
  118 |             postgresql_pgdg_families[ansible_distribution] | default("redhat") }}-repo-latest.noarch.rpm
  119 |       register: postgresql_yum_result
  120 |       until: postgresql_yum_result is succeeded
  121 |       retries: 5
  122 |       delay: 5
  123 | 
  124 |     - name: Install PostgreSQL client (RedHat >= 8)
  125 |       ansible.builtin.dnf:
  126 |         name: postgresql17
  127 |         disablerepo: AppStream
  128 | 
  129 |     - name: Add mosh service config for FirewallD
  130 |       ansible.builtin.copy:
  131 |         content: '{{ firewall_mosh_service }}'
  132 |         dest: /etc/firewalld/services/mosh.xml
  133 | 
  134 |     - name: Add HTcondor shared port service config for FirewallD
  135 |       ansible.builtin.copy:
  136 |         content: '{{ firewall_htcondor_shared_port_service }}'
  137 |         dest: /etc/firewalld/services/htcondor-shared-port.xml
  138 | 
  139 |     - name: Deploy security.txt
  140 |       ansible.builtin.copy:
  141 |         src: files/galaxy/config/security.txt
  142 |         dest: /etc/nginx/security.txt
  143 |         owner: root
  144 |         group: root
  145 |         mode: '0644'
  146 | 
  147 |     - name: Deploy robots.txt (block LLM crawlers)
  148 |       ansible.builtin.copy:
  149 |         src: files/galaxy/config/robots.txt
  150 |         dest: /etc/nginx/robots.txt
  151 |         owner: root
  152 |         group: root
  153 |         mode: '0644'
  154 | 
  155 |   post_tasks:
  156 |     - name: Write Galaxy __galaxy_client_build_version and __galaxy_current_commit_id
  157 |       delegate_to: 127.0.0.1
  158 |       ansible.builtin.copy:
  159 |         content: |
  160 |           client_build_version={{ __galaxy_client_build_version }}
  161 |           current_commit_id={{ __galaxy_current_commit_id }}
  162 |         dest: '{{ playbook_dir }}/galaxy_update.properties'
  163 | 
  164 |     - name: Append some users to the systemd-journal group
  165 |       user:
  166 |         name: '{{ item }}'
  167 |         groups: systemd-journal
  168 |         append: true
  169 |       loop:
  170 |         - '{{ galaxy_user.name }}'
  171 |         - 'telegraf'
  172 |         - 'stats' # special account to retrieve statistics from the server in read-only mode
  173 | 
  174 |     # Note (ToDo): We should ensure that the Gunicorn sockets are created with the correct SELinux
  175 |     # context to avoid adding or allowing unconfined contexts. This will further tighten
  176 |     # the security of the Galaxy instance. (Check the systemd role that is creating the sockets and
  177 |     # maybe include a task to set the SELinux context for the sockets, and then we can remove the
  178 |     # below tasks)
  179 |     # Add SELinux policy for nginx to interact with the gunicorn socket
  180 |     # - name: Check if nginx-gunicorn selinux policy is installed
  181 |     #   ansible.builtin.command: semodule --list=full | grep -q nginx_gunicorn_selinux
  182 |     #   register: nginx_gunicorn_selinux_policy
  183 |     #   failed_when: nginx_gunicorn_selinux_policy.rc > 1
  184 | 
  185 |     # - name: Add SELinux policy for nginx to interact with the gunicorn socket
  186 |     #   when: nginx_gunicorn_selinux_policy.rc == 1
  187 |     #   block:
  188 |     #     - name: Copy nginx-gunicorn selinux type enforcement file
  189 |     #       ansible.builtin.copy:
  190 |     #         src: 'files/galaxy/config/nginx_gunicorn_selinux.te'
  191 |     #         dest: '/tmp/nginx_gunicorn_selinux.te'
  192 | 
  193 |     #     - name: Compile nginx-gunicorn selinux module
  194 |     #       ansible.builtin.command: 'checkmodule -M -m -o /tmp/nginx_gunicorn_selinux.mod /tmp/nginx_gunicorn_selinux.te'
  195 | 
  196 |     #     - name: Compile nginx-gunicorn selinux policy package
  197 |     #       ansible.builtin.command: 'semodule_package -o /tmp/nginx_gunicorn_selinux.pp -m /tmp/nginx_gunicorn_selinux.mod'
  198 | 
  199 |     #     - name: Install nginx-gunicorn selinux policy package
  200 |     #       ansible.builtin.command: 'semodule -i /tmp/nginx_gunicorn_selinux.pp'
  201 | 
  202 |     #     - name: Clean up nginx-gunicorn selinux policy files
  203 |     #       ansible.builtin.file:
  204 |     #         path: '{{ item }}'
  205 |     #         state: absent
  206 |     #       with_items:
  207 |     #         - '/tmp/nginx_gunicorn_selinux.te'
  208 |     #         - '/tmp/nginx_gunicorn_selinux.mod'
  209 |     #         - '/tmp/nginx_gunicorn_selinux.pp'
  210 | 
  211 |     # - name: Ensure SELinux contexts for TIaaS deployment
  212 |     #   block:
  213 |     #     - name: Set SELinux context for /opt/tiaas2 to usr_t
  214 |     #       community.general.sefcontext:
  215 |     #         target: '{{ tiaas_dir }}(/.*)?'
  216 |     #         setype: usr_t
  217 |     #         state: present
  218 | 
  219 |     #     - name: Apply SELinux context to /opt/tiaas2
  220 |     #       command: restorecon -Rv "{{ tiaas_dir }}"
  221 | 
  222 |     #     - name: Label tiaas.sock as httpd_var_run_t for nginx SELinux access
  223 |     #       community.general.sefcontext:
  224 |     #         target: '{{ tiaas_socket }}'
  225 |     #         setype: httpd_var_run_t
  226 |     #         state: present
  227 | 
  228 |     #     - name: Apply SELinux context to tiaas.sock
  229 |     #       command: restorecon -v "{{ tiaas_socket }}"
  230 | 
  231 |     #     - name: Restart TIaaS service to apply SELinux context changes
  232 |     #       ansible.builtin.systemd:
  233 |     #         name: tiaas
  234 |     #         state: restarted
  235 |     #         enabled: true
  236 | 
  237 |     - name: Change compliance.log file ownership to the galaxy user
  238 |       ansible.builtin.file:
  239 |         path: '{{ galaxy_server_dir }}/compliance.log'
  240 |         owner: galaxy
  241 |         group: root
  242 |         mode: 0644
  243 | 
  244 |     - name: Ensure .config directory exists for galaxy user
  245 |       ansible.builtin.file:
  246 |         path: '{{ galaxy_root }}/.config'
  247 |         state: directory
  248 |         owner: galaxy
  249 |         group: galaxy
  250 |         mode: '0755'
  251 | 
  252 |     - name: "Ensure {{ galaxy_server_dir }}/database directory exists and is owned by galaxy user"
  253 |       ansible.builtin.file:
  254 |         path: "{{ galaxy_server_dir }}/database"
  255 |         state: directory
  256 |         owner: "{{ galaxy_user.name }}"
  257 |         group: "{{ galaxy_group.name }}"
  258 |         mode: "0750"
  259 | 
  260 |     - name: Add gxadmin local script
  261 |       ansible.builtin.copy:
  262 |         src: '{{ playbook_dir }}/files/galaxy/config/gxadmin-local.sh'
  263 |         dest: '{{ galaxy_root }}/.config/gxadmin-local.sh'
  264 |         owner: galaxy
  265 |         group: galaxy
  266 |         mode: '0755'
  267 | 
  268 |     # LLM Hub - We don't have any role to add this stuff
  269 |     - name: Copy LLM Hub Config File
  270 |       ansible.builtin.copy:
  271 |         src: '{{ playbook_dir }}/files/galaxy/config/llm/litellm_config.yml'
  272 |         dest: '/data/db/models/config/litellm_config.yml'
  273 |         owner: galaxy
  274 |         group: galaxy
  275 |         mode: '0644'
  276 | 
  277 |     - name: Copy location file for the LLM Hub
  278 |       ansible.builtin.copy:
  279 |         src: '{{ playbook_dir }}/files/galaxy/config/llm/genai_models.loc'
  280 |         dest: '{{ galaxy_root }}/tool-data/genai_models.loc'
  281 |         owner: galaxy
  282 |         group: galaxy
  283 |         mode: '0644'
  284 | 
  285 |     - name: Copy location file for huggingface models
  286 |       ansible.builtin.copy:
  287 |         src: '{{ playbook_dir }}/files/galaxy/config/llm/huggingface.loc'
  288 |         dest: '{{ galaxy_root }}/tool-data/huggingface.loc'
  289 |         owner: galaxy
  290 |         group: galaxy
  291 |         mode: '0644'
  292 | 
  293 |     - name: Download tool tag mappings from GitHub
  294 |       ansible.builtin.get_url:
  295 |         url: https://raw.githubusercontent.com/usegalaxy-eu/tool-annotations/main/tool_tag_mappings.yml
  296 |         dest: '{{ galaxy_config_dir }}/tool_tag_mappings.yml'
  297 |         owner: galaxy
  298 |         group: galaxy
  299 |         mode: '0644'
  300 | 
  301 |   roles:
  302 |     ## Starting configuration of the operating system
  303 |     - role: usegalaxy_eu.handy.os_setup
  304 |       vars:
  305 |         enable_hostname: true
  306 |         enable_powertools: true # geerlingguy.repo-epel role doesn't enable PowerTools repository
  307 |         enable_remap_user: true
  308 |         enable_exclude_packages: true
  309 |         enable_pam_limits: true # Prevent out of control processes
  310 |         enable_install_software: true # Some extra admin tools (*top, vim, etc)
  311 |     - geerlingguy.repo-epel # Install EPEL repository
  312 |     - influxdata.chrony # Keep our time in sync.
  313 | 
  314 |     ## Filesystems
  315 |     - usegalaxy-eu.autofs # Setup the mount points which will be needed later
  316 |     - galaxyproject.cvmfs # Galaxy datasets
  317 | 
  318 |     ## Monitoring
  319 |     - hxr.monitor-email
  320 |     - hxr.monitor-galaxy-journalctl
  321 | 
  322 |     # Setup Galaxy user
  323 |     - role: galaxyproject.galaxy
  324 |       vars:
  325 |         galaxy_create_user: true
  326 |         galaxy_manage_clone: false
  327 |         galaxy_manage_cleanup: false # we should use this
  328 |         galaxy_manage_download: false
  329 |         galaxy_manage_existing: true
  330 |         galaxy_manage_paths: true
  331 |         galaxy_manage_static_setup: false
  332 |         galaxy_manage_mutable_setup: false
  333 |         galaxy_manage_database: false
  334 |         galaxy_manage_subdomain_static: false
  335 |         galaxy_fetch_dependencies: false
  336 |         galaxy_build_client: false
  337 |         galaxy_manage_systemd: false # switch to gravity(?)
  338 |         galaxy_manage_gravity: false
  339 |     # The bashrc needs to be created for several later features.
  340 |     - usegalaxy-eu.bashrc
  341 | 
  342 |     ## Setup docker
  343 |     - geerlingguy.docker
  344 | 
  345 |     # Misc.
  346 |     - role: hxr.galaxy-nonreproducible-tools
  347 |       become: true
  348 |       become_user: galaxy
  349 |     - usegalaxy-eu.dynmotd # nicer MOTD/welcome message
  350 | 
  351 |     - usegalaxy-eu.rsync-to-nfs # sync codebase to NFS
  352 | 
  353 |     - role: usegalaxy-eu.webhooks # Clone webhook repository
  354 |       become: true
  355 |       become_user: galaxy
  356 |     - role: usegalaxy-eu.tours # Clone tour repository
  357 |       become: true
  358 |       become_user: galaxy
  359 | 
  360 |     ## SSL / Security
  361 |     # https://en.wikipedia.org/wiki/Trust_on_first_use
  362 |     - ssh-host-sign # Sign the server host key to prevent TOFU for SSH
  363 |     - hxr.aws-cli # Setup the AWS client that will be needed for route53 authentication of certbot. MUST come before nginx role
  364 | 
  365 |     ## GALAXY
  366 |     - hxr.postgres-connection
  367 |     - galaxyproject.gxadmin
  368 | 
  369 |     - usegalaxy_eu.ansible_nginx_upload_module
  370 |     - usegalaxy-eu.nginx
  371 | 
  372 |     - usegalaxy-eu.gapars-galaxy
  373 | 
  374 |     # The REAL galaxy role call that will install Galaxy and all of its dependencies.
  375 |     - role: galaxyproject.galaxy
  376 |       vars:
  377 |         galaxy_create_user: true
  378 |         galaxy_manage_clone: true
  379 |         galaxy_manage_cleanup: false # we should use this
  380 |         galaxy_manage_download: false
  381 |         galaxy_manage_existing: false
  382 |         galaxy_manage_static_setup: true
  383 |         galaxy_manage_mutable_setup: true
  384 |         galaxy_manage_database: true
  385 |         galaxy_manage_subdomain_static: true
  386 |         galaxy_manage_host_filters: false # test when themes work
  387 |         galaxy_manage_systemd: false # switch to gravity(?)
  388 |         galaxy_manage_gravity: false
  389 |         galaxy_fetch_dependencies: true
  390 |         galaxy_build_client: true
  391 |         galaxy_client_make_target: client-production
  392 | 
  393 |     - usegalaxy_eu.tpv_auto_lint
  394 |     - galaxyproject.tiaas2
  395 |     ## Extras!
  396 |     - usegalaxy-eu.fix-galaxy-server-dir # Fix details into the galaxy server dirs
  397 |     - hxr.install-to-venv # Some extra packages our site needs.
  398 |     - usegalaxy_eu.galaxy_systemd # Manage the Galaxy processes with SystemD
  399 |     - usegalaxy-eu.update-hosts # Update hosts list
  400 |     - usegalaxy_eu.gie_proxy # Setup the NodeJS proxy for GxIT
  401 |     - usegalaxy_eu.fs_maintenance # Filesystems maintenance
  402 |     - usegalaxy-eu.logrotate # Rotate logs
  403 |     - usegalaxy-eu.error-pages # Copy the NGINX error pages
  404 |     - usegalaxy-eu.fix-stuck-handlers # Restart handlers to prevent several classes of issues
  405 |     - usegalaxy-eu.log-cleaner # do not retain journalctl logs, they are unnecessary/risky under GDPR
  406 |     - dj-wasabi.telegraf
  407 |     - usegalaxy-eu.galaxy-procstat # Some custom telegraf monitoring that's templated
  408 |     - ssh_hardening #dev-sec.hardening collection
  409 |     - usegalaxy-eu.fix-stop-ITs
  410 |     - usegalaxy_eu.firewall
```

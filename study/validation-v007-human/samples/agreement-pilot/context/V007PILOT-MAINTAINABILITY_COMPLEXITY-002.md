# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-002

- Repository: `pjbriggs/ansible-palfinder-galaxy`
- Commit: `e77a4b2ccc9ade57dcbb71f2c2d3e25db01d2169`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `centaurus.yml` (reported anchor line 1)
- Object: `source_location` `03061c63b1e53607cc730833edbbc8a606ccfc98e1a1ca66d0c0b78d86ca53d2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–102 of 102:

```text
    1 | ---
    2 | - hosts: centaurus
    3 | 
    4 |   vars:
    5 |   # Ubuntu doesn't have Python2 by default
    6 |   # See e.g. https://www.toptechskills.com/ansible-tutorials-courses/how-to-fix-usr-bin-python-not-found-error-tutorial/
    7 |   - ansible_python_interpreter: /usr/bin/python3
    8 |   # Galaxy user and group on system
    9 |   - galaxy_user: "centaurus-galaxy"
   10 |   - galaxy_uid: 22223
   11 |   - galaxy_group: "galaxy"
   12 |   - galaxy_gid: 400
   13 |   # Extra groups to add Galaxy user to
   14 |   - extra_groups:
   15 |       - group: "ls-bcf"
   16 |         gid: 337111
   17 |   # System Python and PostgreSQL versions
   18 |   - python_version: "3.10.5"
   19 |   - postgresql_version: "14"
   20 |   # Postfix settings
   21 |   - postfix_host_name: "centaurus.itservices.manchester.ac.uk"
   22 |   - postfix_relay_host: "smtp.manchester.ac.uk"
   23 |   # Default job runner
   24 |   - galaxy_default_runner: "jse_drop_serial"
   25 | 
   26 |   # Base installation directory and other paths set in the
   27 |   # production_config.yml file for the 'production' instance
   28 | 
   29 |   # Options when migrating to a new VM
   30 |   # NB SQL database file should be on the remote server
   31 |   ##- galaxy_new_db_sql: "/home/centaurus-galaxy/pg_dump-2024-03-12.sql"
   32 |   ##- galaxy_reinstall_conda: yes
   33 | 
   34 |   # Options when updating Python version
   35 |   ##- galaxy_force_reinstall_python: yes
   36 |   ##- galaxy_force_reinstall_venv: yes
   37 | 
   38 |   # Options when updating Galaxy version
   39 |   ##- galaxy_remove_mako_templates: yes
   40 | 
   41 |   # Uncomment for faster tool installation
   42 |   # NB may cause issues with dependency installation
   43 |   - galaxy_install_tool_extra_args: "--no-wait"
   44 | 
   45 |   # Define proxy environment variables if needed
   46 |   ##- proxy_env:
   47 |   ##    http_proxy: 'http://updateproxy.manchester.ac.uk:3128'
   48 |   ##    https_proxy: 'https://updateproxy.manchester.ac.uk:3128
   49 | 
   50 |   vars_files:
   51 |   # Instance-specific variables
   52 |   - instances/centaurus/production_versions.yml
   53 |   - instances/centaurus/production_config.yml
   54 |   - instances/centaurus/production_resolvers.yml
   55 |   - instances/centaurus/production_local_tools.yml
   56 |   - instances/centaurus/{{ centaurus_secrets }}
   57 |   # Variables common to production and devel
   58 |   - instances/centaurus/job_conf.yml
   59 |   - instances/centaurus/shed_tools_{{ galaxy_install_mode }}.yml
   60 |   - instances/centaurus/tool_data_{{ galaxy_install_mode }}.yml
   61 |   - instances/centaurus/custom_scss.yml
   62 |   - instances/centaurus/tool_data_tables.yml
   63 |   - instances/centaurus/sanitize_whitelist.yml
   64 |   # SSL certs parameterised so use same YAML file
   65 |   # for production and devel
   66 |   - instances/centaurus/ssl_certs.yml
   67 | 
   68 |   roles:
   69 |   # Configure host VM
   70 |   - galaxy-user
   71 |   - python3
   72 |   - nginx
   73 |   - postgresql
   74 | 
   75 |   # SSL certificates
   76 |   - role: certbot
   77 |     when: enable_https
   78 | 
   79 |   # Postfix mail client
   80 |   - role: postfix-null-client
   81 |     when: enable_smtp
   82 | 
   83 |   # Local JSEDrop service
   84 |   - role: jsedrop
   85 |     jsedrop_drop_dir: "{{ galaxy_jse_drop_dir }}"
   86 |     when: enable_local_jse_drop
   87 | 
   88 |   # Install and configure Galaxy
   89 |   - galaxy-utils
   90 |   - galaxy
   91 | 
   92 |   # Set up users, tools etc
   93 |   - galaxy-create-users
   94 |   - galaxy-install-tools
   95 |   - galaxy-set-default-quota
   96 | 
   97 |   # Additional set up
   98 |   - galaxy-audit-report
   99 | 
  100 |   ## Use this to set environment variables on the remote
  101 |   ## when ansible tasks run (e.g. proxy settings)
  102 |   #environment: "{{ proxy_env }}"
```

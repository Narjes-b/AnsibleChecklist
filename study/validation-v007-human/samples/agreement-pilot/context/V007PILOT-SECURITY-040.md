# Frozen source context: V007PILOT-SECURITY-040

- Repository: `ARTbio/GalaxyKickStart`
- Commit: `d04bc40174594a2996a23a1c1b07155de4a694e4`
- Family: Security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `galaxy.yml` (reported anchor line 1)
- Object: `source_location` `a95a0e98fd99f8a13f713a0734254a3a42f1cf23292ef18faab103e960cc7153`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–117 of 117:

```text
    1 | - hosts: all
    2 |   become: yes
    3 |   gather_facts: true
    4 | 
    5 |   environment: "{{ proxy_env }}"
    6 | 
    7 |   handlers:
    8 |     - include_tasks: roles/handlers/galaxy.yml
    9 | 
   10 |   pre_tasks:
   11 |     - name: gather facts
   12 |       setup:
   13 |       tags:
   14 |         - always
   15 | 
   16 |     - name: Check ansible version
   17 |       fail: msg="Installed ansible version {{ ansible_version.full }}, but ansible version >= 2.7.4 required"
   18 |       when: ansible_version.full is version('2.7', '<')
   19 |       tags:
   20 |         - always
   21 | 
   22 |     - name: Install python if absent
   23 |       raw: test -e /usr/bin/python3 || (apt -y update && apt install -y python3-minimal)
   24 |       register: output
   25 |       changed_when: output.stdout
   26 |       tags:
   27 |         - always
   28 | 
   29 |     - name: Install psycopg2
   30 |       become: yes
   31 |       apt:
   32 |         name: python3-psycopg2
   33 |         state: present
   34 | 
   35 |     - name: get host ip in ipify_public_ip variable
   36 |       ipify_facts:
   37 |         timeout: 20
   38 |       tags:
   39 |         - always
   40 | 
   41 | 
   42 |   roles:
   43 | 
   44 |     - role: galaxyprojectdotorg.galaxy-os
   45 |       tags:
   46 |         - install_galaxy
   47 |         - install_packages
   48 | 
   49 |     - role: ensure_postgresql_up
   50 |       tags:
   51 |         - install_galaxy
   52 |         - manage_postgres
   53 |         - postgres_up
   54 | 
   55 |     - role: natefoo.postgresql_objects
   56 |       postgresql_objects_users:
   57 |         - name: "{{ galaxy_user_name }}"
   58 |           password: "{{ galaxy_user_name }}"
   59 |           encrypted: "yes"
   60 |       postgresql_objects_databases:
   61 |         - name: "{{ galaxy_user_name }}"
   62 |           owner: "{{ galaxy_user_name }}"
   63 |       become: yes
   64 |       become_user: postgres
   65 |       tags:
   66 |         - install_galaxy
   67 |         - manage_postgres
   68 | 
   69 |     - role: galaxyprojectdotorg.galaxy
   70 |       become: yes
   71 |       become_user: "{{ galaxy_user_name }}"
   72 |       tags:
   73 |         - configure_galaxy
   74 |         - install_galaxy
   75 |       vars:
   76 |         - ansible_check_mode: no # test tests
   77 | 
   78 |     - role: set_supervisor_env_vars
   79 |       tags: env_vars
   80 | 
   81 |     # Installs miniconda
   82 |     - role: miniconda-role
   83 |       become: yes
   84 |       become_user: "{{ galaxy_user_name }}"
   85 |       tags: conda
   86 | 
   87 |     # Installs supervisor, nginx and proftpd
   88 |     - role: galaxyprojectdotorg.galaxy-extras
   89 |       tags:
   90 |         - configure_server_stack
   91 |         - install_extras
   92 | 
   93 |     - role: ensure_postgresql_up
   94 |       tags:
   95 |         - manage_postgres
   96 |         - install_tools
   97 | 
   98 |     - role: copy_additional_files
   99 |       tags:
  100 |         - install_extras
  101 | 
  102 |     - role: galaxy.movedata
  103 |       tags:
  104 |         - persists_galaxy
  105 | 
  106 |     - role: galaxyprojectdotorg.trackster
  107 |       tags: configure_galaxy
  108 | 
  109 |   post_tasks:
  110 | 
  111 |     - name: Remove useless packages from the cache
  112 |       apt:
  113 |         autoclean: yes
  114 | 
  115 |     - name: Remove dependencies that are no longer required
  116 |       apt:
  117 |         autoremove: yes
```

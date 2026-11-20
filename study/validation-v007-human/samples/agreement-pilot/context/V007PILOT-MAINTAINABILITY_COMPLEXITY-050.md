# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-050

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: Maintainability/complexity
- Rule: `ansibleguard/high-coupling`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `src/commcare_cloud/ansible/deploy_proxy.yml` (reported anchor line 1)
- Object: `source_location` `63e2dfb150147156717bada5e5e8ac21e3b043092509247518bf6ce8f435c37d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–113 of 113:

```text
    1 | ---
    2 | - name: setup nginx
    3 |   hosts: proxy
    4 |   tasks:
    5 |     - name: Create static files home
    6 |       become: yes
    7 |       file: path="{{ nginx_static_home }}" owner="{{ cchq_user }}" group="{{ cchq_user }}" mode=0755 state=directory
    8 | 
    9 |     - name: install nginx
   10 |       import_role:
   11 |         name: nginx
   12 |         tasks_from: install
   13 |       when: not nginx_installed|default(False)
   14 |       tags: nginx
   15 | 
   16 |     - name: install nginx certs
   17 |       include_role:
   18 |         name: nginx
   19 |         tasks_from: certs
   20 |       tags:
   21 |         - nginx
   22 | 
   23 | - name: Proxy
   24 |   hosts: proxy
   25 |   tasks:
   26 |     - name: setup shared dir
   27 |       include_role:
   28 |         name: shared_dir
   29 | 
   30 |     - name: install error pages
   31 |       include_role:
   32 |         name: nginx
   33 |         tasks_from: errorpages
   34 | 
   35 |     - name: install cchq sites
   36 |       include_role:
   37 |         name: {name: nginx, tags: nginx_sites}
   38 |         tasks_from: site
   39 |       with_items:
   40 |         - {name: cchq_http, vars_file: cchq_http}
   41 |         - {name: cchq_ssl, vars_file: cchq_ssl}
   42 |       loop_control:
   43 |         loop_var: site_config
   44 |       tags: nginx_sites
   45 | 
   46 |     - name: install no www redirect sites
   47 |       include_role:
   48 |         name: {name: nginx, tags: nginx_sites}
   49 |         tasks_from: set_site_present
   50 |       vars:
   51 |         site_present: "{{ NO_WWW_SITE_HOST|default(None) is not none }}"
   52 |       with_items:
   53 |         - {name: cchq_www_redirect_insecure, vars_file: cchq_www_redirect_insecure}
   54 |         - {name: cchq_www_redirect_secure, vars_file: cchq_www_redirect_secure}
   55 |       loop_control:
   56 |         loop_var: site_config
   57 |       tags: nginx_sites
   58 | 
   59 |     - name: install j2me http site
   60 |       include_role:
   61 |         name: {name: nginx, tags: nginx_sites}
   62 |         tasks_from: set_site_present
   63 |       vars:
   64 |         site_present: "{{ J2ME_SITE_HOST|default(None) is not none }}"
   65 |       with_items:
   66 |         - {name: cchq_http_j2me, vars_file: cchq_http_j2me}
   67 |       loop_control:
   68 |         loop_var: site_config
   69 |       tags: nginx_sites
   70 | 
   71 |     - name: remove obsolete sites
   72 |       include_role:
   73 |         name: {name: nginx, tags: [nginx_sites, drop_old_sites]}
   74 |         tasks_from: set_site_present
   75 |       vars:
   76 |         site_present: False
   77 |         nginx_sites: [{server: {file_name: '{{ file_name }}'}}]
   78 |       with_items:
   79 |         - wiki
   80 |         - wiki_http
   81 |         - icds_tableau
   82 |         - icds_tableau_http
   83 |       loop_control:
   84 |         loop_var: file_name
   85 |       tags:
   86 |         - nginx_sites
   87 |         - drop_old_sites
   88 | 
   89 | - name: Nginx log rolling configurations
   90 |   hosts:
   91 |    - proxy
   92 |   become: true
   93 |   roles:
   94 |     - role: ansible-logrotate
   95 |       logrotate_scripts:
   96 |         - name: "{{ deploy_env }}"
   97 |           path: "{{ log_home }}/*.log"
   98 |           options:
   99 |             - weekly
  100 |             - size 750M
  101 |             - rotate 4
  102 |             - missingok
  103 |             - compress
  104 |             - nocreate
  105 |             - notifempty
  106 |             - sharedscripts
  107 |           scripts:
  108 |             postrotate: "[ -s /run/nginx.pid ] && kill -USR1 `cat /run/nginx.pid`"
  109 | 
  110 | - name: Setup Letsencrypt
  111 |   import_playbook: letsencrypt_cert.yml
  112 |   tags: setup_letsencrypt
  113 |   when: not fake_ssl_cert
```

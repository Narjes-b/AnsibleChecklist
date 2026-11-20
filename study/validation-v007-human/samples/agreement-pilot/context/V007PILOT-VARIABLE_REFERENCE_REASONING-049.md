# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-049

- Repository: `michnmi/ansible_internal`
- Commit: `25f44a7ad44d44b7b91837256958ff443ba28a1e`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/services/certbot/tasks/setup-certbot-structure.yml` (reported anchor line 67)
- Object: `variable` `4e2bca1a3b26a69d0074b79e1d716f2021eb0266601fa0331510a834e6fea43d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–75 of 75:

```text
    1 | ---
    2 | - name: 'Setup-certbot-structure: Install Certbot'
    3 |   ansible.builtin.apt:
    4 |     name: 'certbot'
    5 |     state: 'present'
    6 | 
    7 | - name: 'Setup-certbot-structure: Setup the certbot web root directory'
    8 |   ansible.builtin.file:
    9 |     path: "{{ certbot_well_known }}"
   10 |     owner: 'root'
   11 |     group: 'root'
   12 |     mode: '0755'
   13 |     state: 'directory'
   14 | 
   15 | - name: 'Setup-certbot-structure: Create archive and live directories (need 0700)'
   16 |   ansible.builtin.file:
   17 |     path: "{{ certbot_cert_path }}/{{ item }}"
   18 |     state: 'directory'
   19 |     mode: '0700'
   20 |   loop:
   21 |     - 'archive'
   22 |     - 'live'
   23 | 
   24 | - name: 'Setup-certbot-structure: Create the archive certificates directories'
   25 |   ansible.builtin.file:
   26 |     path: "{{ certbot_cert_path }}/archive/{{ domain.name }}"
   27 |     state: directory
   28 |     mode: '0755'
   29 |   loop: "{{ certbot_certificates }}"
   30 |   loop_control:
   31 |     loop_var: "domain"
   32 |   no_log: true
   33 | 
   34 | 
   35 | - name: 'Setup-certbot-structure: Create the live certificates directories'
   36 |   ansible.builtin.file:
   37 |     path: "{{ certbot_cert_path }}/live/{{ domain.name }}"
   38 |     state: directory
   39 |     mode: '0755'
   40 |   loop: "{{ certbot_certificates }}"
   41 |   loop_control:
   42 |     loop_var: "domain"
   43 |   no_log: true
   44 | 
   45 | - name: 'Setup-certbot-structure: Setup renewal directory'
   46 |   ansible.builtin.file:
   47 |     path: "{{ certbot_cert_path }}/renewal"
   48 |     owner: 'root'
   49 |     group: 'root'
   50 |     mode: '0755'
   51 |     state: 'directory'
   52 | 
   53 | - name: 'Setup-certbot-structure: Setup renewal configs'
   54 |   ansible.builtin.template:
   55 |     src: 'templates/etc_letsencrypt_renewal_conf.j2'
   56 |     dest: "{{ certbot_cert_path }}/renewal/{{ domain.name }}.conf"
   57 |     owner: 'root'
   58 |     group: 'root'
   59 |     mode: '0644'
   60 |   loop: "{{ certbot_certificates }}"
   61 |   loop_control:
   62 |     loop_var: "domain"
   63 |   no_log: true
   64 | 
   65 | - name: 'Setup-certbot-structure: Setup accounts (endpoints)'
   66 |   ansible.builtin.file:
   67 |     path: "{{ certbot_cert_path }}/accounts/{{ account.endpoint }}"
   68 |     owner: 'root'
   69 |     group: 'root'
   70 |     mode: '0700'
   71 |     state: directory
   72 |   loop: "{{ certbot_accounts }}"
   73 |   loop_control:
   74 |     loop_var: 'account'
   75 |   no_log: true
```

## Visible variable references

```text
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-accounts.yml:4:    path: "{{ certbot_cert_path }}/accounts/{{ account.endpoint }}/directory/{{ account.name }}"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-accounts.yml:17:    dest: "{{ certbot_cert_path }}/accounts/{{ account.endpoint }}/directory/{{ account.name }}/meta.json"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-accounts.yml:29:    dest: "{{ certbot_cert_path }}/accounts/{{ account.endpoint }}/directory/{{ account.name }}/private_key.json"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-accounts.yml:41:    dest: "{{ certbot_cert_path }}/accounts/{{ account.endpoint }}/directory/{{ account.name }}/regr.json"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certbot-structure.yml:17:    path: "{{ certbot_cert_path }}/{{ item }}"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certbot-structure.yml:26:    path: "{{ certbot_cert_path }}/archive/{{ domain.name }}"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certbot-structure.yml:37:    path: "{{ certbot_cert_path }}/live/{{ domain.name }}"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certbot-structure.yml:47:    path: "{{ certbot_cert_path }}/renewal"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certbot-structure.yml:56:    dest: "{{ certbot_cert_path }}/renewal/{{ domain.name }}.conf"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certbot-structure.yml:67:    path: "{{ certbot_cert_path }}/accounts/{{ account.endpoint }}"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:5:    dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/cert1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:17:    dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/chain1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:29:    dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/fullchain1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:41:    dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/privkey1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:52:    src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/cert1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:53:    dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/cert.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:62:    src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/chain1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:63:    dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/chain.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:72:    src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/fullchain1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:73:    dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/fullchain.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:82:    src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/privkey1.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/tasks/setup-certificates.yml:83:    dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/privkey.pem"
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/templates/etc_letsencrypt_renewal_conf.j2:3:archive_dir = {{ certbot_cert_path }}/archive/{{ domain.name }}
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/templates/etc_letsencrypt_renewal_conf.j2:4:cert = {{ certbot_cert_path }}/live/{{ domain.name }}/cert.pem
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/templates/etc_letsencrypt_renewal_conf.j2:5:privkey = {{ certbot_cert_path }}/live/{{ domain.name }}/privkey.pem
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/templates/etc_letsencrypt_renewal_conf.j2:6:chain = {{ certbot_cert_path }}/live/{{ domain.name }}/chain.pem
25f44a7ad44d44b7b91837256958ff443ba28a1e:roles/services/certbot/templates/etc_letsencrypt_renewal_conf.j2:7:fullchain = {{ certbot_cert_path }}/live/{{ domain.name }}/fullchain.pem
```

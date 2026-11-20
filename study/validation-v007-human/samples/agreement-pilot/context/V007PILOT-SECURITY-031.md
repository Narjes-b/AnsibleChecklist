# Frozen source context: V007PILOT-SECURITY-031

- Repository: `michnmi/ansible_internal`
- Commit: `25f44a7ad44d44b7b91837256958ff443ba28a1e`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/services/certbot/tasks/setup-certificates.yml` (reported anchor line 38)
- Object: `source_location` `8fdf4e83ba4a596bd61bd38899eb5ce2506898f1630c61a82a28caf841c5f679`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–88 of 88:

```text
    1 | ---
    2 | - name: 'Setup-certbot: Populate the archive certificates (cert)'
    3 |   ansible.builtin.template:
    4 |     src: etc_letsencrypt_certificate_skeletons/cert.pem.j2
    5 |     dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/cert1.pem"
    6 |     mode: '0644'
    7 |     owner: 'root'
    8 |     group: 'root'
    9 |   loop: "{{ certbot_certificates }}"
   10 |   loop_control:
   11 |     loop_var: "domain"
   12 |   no_log: true
   13 | 
   14 | - name: 'Setup-certbot: Populate the archive certificates (chain)'
   15 |   ansible.builtin.template:
   16 |     src: etc_letsencrypt_certificate_skeletons/chain.pem.j2
   17 |     dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/chain1.pem"
   18 |     mode: '0644'
   19 |     owner: 'root'
   20 |     group: 'root'
   21 |   loop: "{{ certbot_certificates }}"
   22 |   loop_control:
   23 |     loop_var: "domain"
   24 |   no_log: true
   25 | 
   26 | - name: 'Setup-certbot: Populate the archive certificates (fullchain)'
   27 |   ansible.builtin.template:
   28 |     src: etc_letsencrypt_certificate_skeletons/fullchain.pem.j2
   29 |     dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/fullchain1.pem"
   30 |     mode: '0644'
   31 |     owner: 'root'
   32 |     group: 'root'
   33 |   loop: "{{ certbot_certificates }}"
   34 |   loop_control:
   35 |     loop_var: "domain"
   36 |   no_log: true
   37 | 
   38 | - name: 'Setup-certbot: Populate the archive certificates (privkey)'
   39 |   ansible.builtin.template:
   40 |     src: etc_letsencrypt_certificate_skeletons/privkey.pem.j2
   41 |     dest: "{{ certbot_cert_path }}/archive/{{ domain.name }}/privkey1.pem"
   42 |     mode: '0644'
   43 |     owner: 'root'
   44 |     group: 'root'
   45 |   loop: "{{ certbot_certificates }}"
   46 |   loop_control:
   47 |     loop_var: "domain"
   48 |   no_log: true
   49 | 
   50 | - name: 'Setup-certbot: Populate the live certificates (cert)'
   51 |   ansible.builtin.file:
   52 |     src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/cert1.pem"
   53 |     dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/cert.pem"
   54 |     state: 'link'
   55 |   loop: "{{ certbot_certificates }}"
   56 |   loop_control:
   57 |     loop_var: "domain"
   58 |   no_log: true
   59 | 
   60 | - name: 'Setup-certbot: Populate the live certificates (chain)'
   61 |   ansible.builtin.file:
   62 |     src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/chain1.pem"
   63 |     dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/chain.pem"
   64 |     state: 'link'
   65 |   loop: "{{ certbot_certificates }}"
   66 |   loop_control:
   67 |     loop_var: "domain"
   68 |   no_log: true
   69 | 
   70 | - name: 'Setup-certbot: Populate the live certificates (fullchain)'
   71 |   ansible.builtin.file:
   72 |     src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/fullchain1.pem"
   73 |     dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/fullchain.pem"
   74 |     state: 'link'
   75 |   loop: "{{ certbot_certificates }}"
   76 |   loop_control:
   77 |     loop_var: "domain"
   78 |   no_log: true
   79 | 
   80 | - name: 'Setup-certbot: Populate the live certificates (privkey)'
   81 |   ansible.builtin.file:
   82 |     src: "{{ certbot_cert_path }}/archive/{{ domain.name }}/privkey1.pem"
   83 |     dest: "{{ certbot_cert_path }}/live/{{ domain.name }}/privkey.pem"
   84 |     state: 'link'
   85 |   loop: "{{ certbot_certificates }}"
   86 |   loop_control:
   87 |     loop_var: "domain"
   88 |   no_log: true
```

# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-018

- Repository: `theforeman/forklift`
- Commit: `ee24dec347fc0a785d22989fd1a183393fa4e054`
- Family: maintainability_complexity
- Rule: `ansibleguard/incomplete-task`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `roles/realm_join/tasks/prepare_httpd_mod_auth.yml` (reported anchor line 11)
- Flagged construct: not named by the finding; the anchor line 11 lies in the task at line 11, name `Create httpd conf dir to put keytab [Hack - remove once using gssproxy]`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–66 of 66:

```text
    1 | ---
    2 | - name: Create the config file to get keytab
    3 |   become: yes
    4 |   template:
    5 |     src: net-keytab.conf.j2
    6 |     dest: /etc/net-keytab.conf
    7 |     owner: root
    8 |     group: root
    9 |     mode: 0644
   10 | 
   11 | - name: Create httpd conf dir to put keytab [Hack - remove once using gssproxy]
   12 |   become: yes
   13 |   file:
   14 |     path: /etc/httpd/conf
   15 |     state: directory
   16 |     mode: '0775'
   17 |     recurse: yes
   18 | 
   19 | - name: Get the keytab
   20 |   become: yes
   21 |   environment:
   22 |     KRB5_KTNAME: 'FILE:/etc/httpd/conf/http.keytab'
   23 |   expect:
   24 |     command: "net ads keytab add HTTP -U {{ foreman_realm_directory_admin_name }} -d3 -s /etc/net-keytab.conf"
   25 |     responses:
   26 |       (?i)password: '{{ foreman_realm_directory_admin_password }}'
   27 |     creates: /etc/httpd/conf/http.keytab
   28 | 
   29 | - name: Change perms for keytab
   30 |   become: yes
   31 |   file:
   32 |     path: /etc/httpd/conf/http.keytab
   33 |     owner: root
   34 |     group: root
   35 |     mode: '0644'
   36 | 
   37 | - name: "[Irrelevant] add gssproxy config"
   38 |   become: yes
   39 |   copy:
   40 |     src: apache-gssproxy.conf
   41 |     dest: /etc/gssproxy/80-http.conf
   42 | 
   43 | - name: "[Irrelevant] start gssproxy service"
   44 |   become: yes
   45 |   service:
   46 |     name: gssproxy
   47 |     state: started
   48 |     enabled: yes
   49 | 
   50 | - name: "[Irrelevant] enable GSS_PROXY for httpd"
   51 |   become: yes
   52 |   copy:
   53 |     src: httpd-gssproxy.service
   54 |     dest: /etc/systemd/system/httpd.service
   55 | 
   56 | - name: Create fake IPA conf dir
   57 |   become: yes
   58 |   file:
   59 |     path: /etc/ipa
   60 |     state: directory
   61 | 
   62 | - name: Prepare fake IPA config used by Installer
   63 |   become: yes
   64 |   template:
   65 |     src: fake-ipa.conf.j2
   66 |     dest: /etc/ipa/default.conf
```

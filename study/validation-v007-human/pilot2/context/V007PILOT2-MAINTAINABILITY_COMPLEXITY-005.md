# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-005

- Repository: `cfpb/aurora`
- Commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Family: maintainability_complexity
- Rule: `ansibleguard/high-coupling`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `deploy/deploy_kerberos_server.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`deploy/deploy_kerberos_server.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–44 of 44:

```text
    1 | # kerberos_server.yml - Mock server to test Kerberos authentication
    2 | ---
    3 | - hosts: all
    4 |   become: yes
    5 |   become_method: sudo
    6 |   roles:
    7 |     - {role: puppet_disable, when: "disable_puppet"}
    8 |     - common
    9 |     - iptables
   10 |     - epel
   11 |     - ntp
   12 |     - openldap
   13 |     - kerberos_server
   14 |     - {role: log-courier, when: "install_logstash"}
   15 | 
   16 |   tasks:
   17 |     - name: Add LDAP to Kerberos
   18 |       command: kadmin -p {{ krb_service_user }}/admin -w {{ krb_service_user_password }} -q "addprinc -randkey ldap/{{ ansible_fqdn }}"
   19 |       args:
   20 |         creates: /etc/openldap/ldap.keytab
   21 | 
   22 |     - name: Generate keytab for LDAP
   23 |       command: kadmin -p {{ krb_service_user }}/admin -w {{ krb_service_user_password }} -q "ktadd -k /etc/openldap/ldap.keytab ldap/{{ ansible_fqdn }}"
   24 |       args:
   25 |         creates: /etc/openldap/ldap.keytab
   26 | 
   27 |     - name: Update keytab file settings
   28 |       file:
   29 |         dest: /etc/openldap/ldap.keytab
   30 |         owner: ldap
   31 |         group: ldap
   32 | 
   33 |     - name: Add keytab file to slapd's settings
   34 |       lineinfile:
   35 |         dest: /etc/default/slapd
   36 |         line: "export KRB5_KTNAME=/etc/ldap/ldap.keytab"
   37 |         regexp: "^export KRB5_KTNAME="
   38 |         state: present
   39 |         create: yes
   40 | 
   41 |     - name: Restart slapd
   42 |       service:
   43 |         name: slapd
   44 |         state: restarted
```

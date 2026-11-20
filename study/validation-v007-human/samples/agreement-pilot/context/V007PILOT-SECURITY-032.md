# Frozen source context: V007PILOT-SECURITY-032

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `vagrant/provisioning/roles/ldap/tasks/add-user.yml` (reported anchor line 3)
- Object: `task` `d05b45e257befdfc8ed22bf60e1a5d41db8b94582babbd8f1ff38f1a9125e207`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–92 of 92:

```text
    1 | - name: add {{ u.user_id }} user
    2 |   become: true
    3 |   ldap_entry:
    4 |     server_uri: "{{ ldap_url }}"
    5 |     validate_certs: no
    6 |     bind_dn: "{{ ldap_bind_user }}"
    7 |     bind_pw: "{{ ldap_bind_password }}"
    8 |     dn: CN={{ u.user_id }},{{ldap_user_base}}
    9 |     objectClass:
   10 |       - organizationalPerson
   11 |       - person
   12 |       - user
   13 |       - top
   14 |     attributes:
   15 |       # note, Samba doesn't let you set memberOf directory, you
   16 |       # have to create the user, then add them to the group.
   17 |       description: "{{ u.description }}"
   18 |       samAccountName: "{{ u.user_id }}"
   19 |       name: "{{ u.name }}"
   20 |       mail: "{{ u.mail }}"
   21 |       givenName: "{{ u.firstName }}"
   22 |       sn: "{{ u.lastName }}"
   23 |       cn: "{{ u.user_id }}"
   24 |       userPrincipalName: "{{ u.userPrincipalName | default(u.mail) }}"
   25 |   register: new_user 
   26 | 
   27 | - name: set {{ u.user_id }} password
   28 |   block:
   29 |     - name: base64 encode password
   30 |       shell: echo -n '"{{ u.password }}"' | iconv -f utf8 -t utf16le | base64 -w 0
   31 |       register: base64_password
   32 |       changed_when: false
   33 |     - name: copy change password ldif file
   34 |       become: yes
   35 |       copy:
   36 |         content: |
   37 |           dn: CN={{ u.user_id }},{{ ldap_user_base }}
   38 |           changetype: modify
   39 |           replace: unicodePwd
   40 |           unicodePwd:[REDACTED_LITERAL]
   41 |         dest: "{{ root_folder }}/install/password_change.ldif"
   42 |     - name: wait a few seconds
   43 |       pause:
   44 |         seconds: 15
   45 |     - name: execute password change
   46 |       shell: LDAPTLS_REQCERT=never ldapmodify -H {{ ldap_url }} -D "{{ ldap_bind_user }}" -w '{{ ldap_bind_password }}' -x -f {{ root_folder }}/install/password_change.ldif
   47 |     - name: wait a few more seconds
   48 |       pause:
   49 |         seconds: 15
   50 |   when: ldap_force_password_reset or new_user is changed
   51 | 
   52 | - name: enable {{ u.user_id }} account
   53 |   block:
   54 |     - name: copy enable user ldif file
   55 |       become: yes
   56 |       copy:
   57 |         content: |
   58 |           dn: CN={{ u.user_id }},{{ ldap_user_base }}
   59 |           changetype: modify
   60 |           replace: userAccountControl
   61 |           userAccountControl: 512
   62 |         dest: "{{ root_folder }}/install/activate_user.ldif"
   63 |     - name: enable user
   64 |       shell: LDAPTLS_REQCERT=never ldapmodify -H {{ ldap_url }} -D "{{ ldap_bind_user }}" -w '{{ ldap_bind_password }}' -x -f {{ root_folder }}/install/activate_user.ldif
   65 |   when: new_user is changed
   66 |       
   67 | - name: store user id
   68 |   set_fact: 
   69 |     user_id: "{{ u.user_id }}"
   70 | 
   71 | - name: add {{ u.user_id }} account to groups
   72 |   include_tasks: add-user-to-group.yml
   73 |   loop: "{{ u.groups }}"
   74 | 
   75 | ### so far we only know how to set non-expiring passwords for
   76 | ### local Samba users
   77 | - name: check status of pdbedit file
   78 |   stat:
   79 |     path: "{{ root_folder }}/app/samba/bin/pdbedit"
   80 |   register: pdbedit_file
   81 |   
   82 | - name: see if password is non-expiring already
   83 |   become: yes
   84 |   shell: '{{ root_folder }}/app/samba/bin/pdbedit -Lv {{ u.user_id }} | grep "Account Flags"'
   85 |   register: account_flags
   86 |   when: u.nonexpiring_password and ldap_host == internal_host and pdbedit_file.stat.exists
   87 |   changed_when: false
   88 | 
   89 | - name: set password to never expire
   90 |   become: yes
   91 |   command: '{{ root_folder }}/app/samba/bin/samba-tool user setexpiry {{ u.user_id }} --noexpiry'
   92 |   when: ldap_host == internal_host and pdbedit_file.stat.exists and u.nonexpiring_password and 'X' not in account_flags.stdout
```

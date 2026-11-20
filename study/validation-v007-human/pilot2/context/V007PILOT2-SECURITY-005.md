# Frozen source context: V007PILOT2-SECURITY-005

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `vagrant/provisioning/roles/ldap/tasks/main.yml` (reported anchor line 74)
- Flagged construct: task `add portal organizational units`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–199 of 199:

```text
    1 | - name: Python LDAP package (RHEL 8)
    2 |   ansible.builtin.set_fact:
    3 |     pkg_python_ldap: python3-ldap
    4 |   when: ansible_distribution in ["RedHat","Rocky"] and ansible_distribution_major_version == "8"
    5 | 
    6 | - name: Python LDAP package (CentOS 7)
    7 |   ansible.builtin.set_fact:
    8 |     pkg_python_ldap: python-ldap
    9 |   when: ansible_distribution == "CentOS" and ansible_distribution_major_version == "7"
   10 | 
   11 | - name: LDAP required packages
   12 |   become: true
   13 |   command: dnf install -y openldap-clients python3.12-devel
   14 | 
   15 | - name: install cryptography
   16 |   become: yes
   17 |   command: "{{ ansible_pip3 | default('pip3') }} install cryptography {{ pkg_python_ldap }}"
   18 | 
   19 | - name: List certs in the key store
   20 |   become: true
   21 |   ansible.builtin.command: keytool -v -list -keystore "{{ java_trust_store }}" -storepass "{{ java_trust_store_pass }}"
   22 |   register: cert_list
   23 |   changed_when: false
   24 | 
   25 | - name: Import the ldap cert to the ArkCase trust store
   26 |   become: true
   27 |   community.general.java_cert:
   28 |     cert_alias: "arkcase_ldap_cert"
   29 |     cert_url: "{{ ldap_host }}"
   30 |     cert_port: "{{ ldap_port | int }}"
   31 |     keystore_path: "{{ java_trust_store }}"
   32 |     keystore_pass: "{{ java_trust_store_pass }}"
   33 |     state: present
   34 |   when: "'arkcase_ldap_cert' not in cert_list.stdout"
   35 | 
   36 | - name: Add arkcase ancestors
   37 |   become: true
   38 |   community.general.ldap_entry:
   39 |     server_uri: "{{ ldap_url }}"
   40 |     validate_certs: false
   41 |     bind_dn: "{{ ldap_bind_user }}"
   42 |     bind_pw: "{{ ldap_bind_password }}"
   43 |     dn: "{{ item }}"
   44 |     objectClass:
   45 |       - organizationalUnit
   46 |       - top
   47 |     attributes:
   48 |       description: "{{ item }}"
   49 |   loop: "{{ ldap_ancestor_ous }}"
   50 |   vars:
   51 |     ansible_python_interpreter: "{{ ansible_python3 | default('/usr/bin/python2') }}"
   52 | 
   53 | - name: Add arkcase organizational units
   54 |   become: true
   55 |   community.general.ldap_entry:
   56 |     server_uri: "{{ ldap_url }}"
   57 |     validate_certs: false
   58 |     bind_dn: "{{ ldap_bind_user }}"
   59 |     bind_pw: "{{ ldap_bind_password }}"
   60 |     dn: "{{ item }}"
   61 |     objectClass:
   62 |       - organizationalUnit
   63 |       - top
   64 |     attributes:
   65 |       description: "{{ item }}"
   66 |   loop:
   67 |     - "{{ ldap_group_base }}"
   68 |     - "{{ ldap_user_base }}"
   69 |   vars:
   70 |     ansible_python_interpreter: "{{ ansible_python3 | default('/usr/bin/python2') }}"
   71 | 
   72 | - name: Add portal organizational units
   73 |   become: true
   74 |   community.general.ldap_entry:
   75 |     server_uri: "{{ ldap_url }}"
   76 |     validate_certs: false
   77 |     bind_dn: "{{ ldap_bind_user }}"
   78 |     bind_pw: "{{ ldap_bind_password }}"
   79 |     dn: "{{ item }}"
   80 |     objectClass:
   81 |       - organizationalUnit
   82 |       - top
   83 |     attributes:
   84 |       description: "{{ item }}"
   85 |   loop:
   86 |     - "{{ ldap_portal_group_no_base }},{{ ldap_base }}"
   87 |     - "{{ ldap_portal_user_no_base }},{{ ldap_base }}"
   88 |   when: foia_portal_context is defined
   89 |   vars:
   90 |     ansible_python_interpreter: "{{ ansible_python3 | default('/usr/bin/python2') }}"
   91 | 
   92 | - name: Add core portal organizational units
   93 |   become: true
   94 |   community.general.ldap_entry:
   95 |     server_uri: "{{ ldap_url }}"
   96 |     validate_certs: false
   97 |     bind_dn: "{{ ldap_bind_user }}"
   98 |     bind_pw: "{{ ldap_bind_password }}"
   99 |     dn: "{{ item }}"
  100 |     objectClass:
  101 |       - organizationalUnit
  102 |       - top
  103 |     attributes:
  104 |       description: "{{ item }}"
  105 |   loop:
  106 |     - "{{ ldap_core_portal_group_no_base }},{{ ldap_base }}"
  107 |     - "{{ ldap_core_portal_user_no_base }},{{ ldap_base }}"
  108 |   when: enable_microservices is defined and enable_microservices
  109 | 
  110 | - name: Add arkcase groups
  111 |   become: true
  112 |   community.general.ldap_entry:
  113 |     server_uri: "{{ ldap_url }}"
  114 |     validate_certs: false
  115 |     bind_dn: "{{ ldap_bind_user }}"
  116 |     bind_pw: "{{ ldap_bind_password }}"
  117 |     dn: "CN={{ item.name }},{{ ldap_group_base }}"
  118 |     objectClass:
  119 |       - group
  120 |       - top
  121 |     attributes:
  122 |       description: "{{ item.description }}"
  123 |       samAccountName: "{{ item.name }}"
  124 |       cn: "{{ item.name }}"
  125 |   loop: "{{ ldap_groups | flatten }}"
  126 |   vars:
  127 |     ansible_python_interpreter: "{{ ansible_python3 | default('/usr/bin/python2') }}"
  128 | 
  129 | - name: Remove portal group from ArkCase OU if exists
  130 |   become: true
  131 |   community.general.ldap_entry:
  132 |     server_uri: "{{ ldap_url }}"
  133 |     validate_certs: false
  134 |     bind_dn: "{{ ldap_bind_user }}"
  135 |     bind_pw: "{{ ldap_bind_password }}"
  136 |     dn: "CN={{ item.name }},{{ ldap_group_no_base }},{{ ldap_base }}"
  137 |     state: absent
  138 |     objectClass:
  139 |       - group
  140 |       - top
  141 |     attributes:
  142 |       description: "{{ item.description }}"
  143 |       samAccountName: "{{ item.name }}"
  144 |       cn: "{{ item.name }}"
  145 |   loop: "{{ ldap_portal_groups | flatten }}"
  146 |   when: foia_portal_context is defined
  147 |   vars:
  148 |     ansible_python_interpreter: "{{ ansible_python3 | default('/usr/bin/python2') }}"
  149 | 
  150 | - name: Add portal groups
  151 |   become: true
  152 |   community.general.ldap_entry:
  153 |     server_uri: "{{ ldap_url }}"
  154 |     validate_certs: false
  155 |     bind_dn: "{{ ldap_bind_user }}"
  156 |     bind_pw: "{{ ldap_bind_password }}"
  157 |     dn: "CN={{ item.name }},{{ ldap_portal_group_no_base }},{{ ldap_base }}"
  158 |     objectClass:
  159 |       - group
  160 |       - top
  161 |     attributes:
  162 |       description: "{{ item.description }}"
  163 |       samAccountName: "{{ item.name }}"
  164 |       cn: "{{ item.name }}"
  165 |   loop: "{{ ldap_portal_groups | flatten }}"
  166 |   when: foia_portal_context is defined
  167 |   vars:
  168 |     ansible_python_interpreter: "{{ ansible_python3 | default('/usr/bin/python2') }}"
  169 | 
  170 | - name: Add Core portal groups
  171 |   become: true
  172 |   community.general.ldap_entry:
  173 |     server_uri: "{{ ldap_url }}"
  174 |     validate_certs: false
  175 |     bind_dn: "{{ ldap_bind_user }}"
  176 |     bind_pw: "{{ ldap_bind_password }}"
  177 |     dn: "CN={{ item.name }},{{ ldap_core_portal_group_no_base }},{{ ldap_base }}"
  178 |     objectClass:
  179 |       - group
  180 |       - top
  181 |     attributes:
  182 |       description: "{{ item.description }}"
  183 |       samAccountName: "{{ item.name }}"
  184 |       cn: "{{ item.name }}"
  185 |   loop: "{{ ldap_core_portal_groups | flatten }}"
  186 |   when: enable_microservices is defined and enable_microservices
  187 | 
  188 | - name: Add users
  189 |   ansible.builtin.include_tasks: add-user.yml
  190 |   loop: "{{ ldap_users }}"
  191 |   loop_control:
  192 |     loop_var: u
  193 |   vars:
  194 |     ansible_python_interpreter: "{{ ansible_python3 | default('/usr/bin/python2') }}"
  195 | 
  196 | - name: Make sure Samba passwords never expire
  197 |   become: true
  198 |   ansible.builtin.command: '{{ root_folder }}/app/samba/bin/samba-tool domain passwordsettings set --max-pwd-age=[REDACTED_LITERAL]
  199 |   when: ldap_type == "samba"
```

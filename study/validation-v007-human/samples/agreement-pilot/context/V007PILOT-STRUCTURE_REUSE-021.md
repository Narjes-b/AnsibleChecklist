# Frozen source context: V007PILOT-STRUCTURE_REUSE-021

- Repository: `freeipa/ansible-freeipa`
- Commit: `5ba9b59d5b614abdb0af70fc9f2d336e5479e833`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/ipasmartcard_client/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `4eae30c094739ed7813640181f9ae52ef0c9ffc2437c66adce65982c2d76fb4e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–176 of 176:

```text
    1 | ---
    2 | # tasks file for ipasmartcard_client role
    3 | 
    4 | - name: Uninstall smartcard client
    5 |   ansible.builtin.fail:
    6 |     msg: "Uninstalling smartcard for IPA is not supported"
    7 |   when: state|default('present') == 'absent'
    8 | 
    9 | - name: Import variables specific to distribution
   10 |   ansible.builtin.include_vars: "{{ item }}"
   11 |   with_first_found:
   12 |     - "vars/{{ ansible_facts['distribution'] }}-{{ ansible_facts['distribution_version'] }}.yml"
   13 |     - "vars/{{ ansible_facts['distribution'] }}-{{ ansible_facts['distribution_major_version'] }}.yml"
   14 |     - "vars/{{ ansible_facts['distribution'] }}.yml"
   15 |     # os_family is used as a fallback for distros which are not currently
   16 |     # supported, but are based on a supported distro family. For example,
   17 |     # Oracle, Rocky, Alma and Alibaba linux, which are all "RedHat" based.
   18 |     - "vars/{{ ansible_facts['os_family'] }}-{{ ansible_facts['distribution_version'] }}.yml"
   19 |     - "vars/{{ ansible_facts['os_family'] }}-{{ ansible_facts['distribution_major_version'] }}.yml"
   20 |     - "vars/{{ ansible_facts['os_family'] }}.yml"
   21 |     # If neither distro nor family is supported, try a default configuration.
   22 |     - "vars/default.yml"
   23 | 
   24 | - name: Client configuration
   25 |   block:
   26 | 
   27 |   # CA CERTS
   28 | 
   29 |   # Use "ipasmartcard_server_ca_certs"
   30 | 
   31 |   - name: Use "ipasmartcard_server_ca_certs"
   32 |     ansible.builtin.set_fact:
   33 |       ipasmartcard_client_ca_certs: "{{ ipasmartcard_server_ca_certs }}"
   34 |     when: ipasmartcard_client_ca_certs is not defined and
   35 |           ipasmartcard_server_ca_certs is defined
   36 | 
   37 |   # Fail on empty "ipasmartcard_client_ca_certs"
   38 | 
   39 |   - name: Fail on empty "ipasmartcard_client_ca_certs"
   40 |     ansible.builtin.fail:
   41 |       msg: "No CA certs given in 'ipasmartcard_client_ca_certs'"
   42 |     when: ipasmartcard_client_ca_certs is not defined or
   43 |           ipasmartcard_client_ca_certs | length < 1
   44 | 
   45 |   # Validate ipasmartcard_client_ca_certs
   46 | 
   47 |   - name: Validate CA certs "{{ ipasmartcard_client_ca_certs }}"
   48 |     ipasmartcard_client_validate_ca_certs:
   49 |       ca_cert_files: "{{ ipasmartcard_client_ca_certs }}"
   50 |     register: result_validate_ca_certs
   51 | 
   52 |   # INSTALL needed packages: opensc, dconf and krb5-pkinit-openssl
   53 | 
   54 |   - name: Ensure needed packages are installed
   55 |     ansible.builtin.package:
   56 |       name: "{{ ipasmartcard_client_packages }}"
   57 |       state: present
   58 | 
   59 |   # REMOVE pam_pkcs11
   60 | 
   61 |   - name: Ensure pam_pkcs11 is missing
   62 |     ansible.builtin.package:
   63 |       name: "{{ ipasmartcard_client_remove_pam_pkcs11_packages }}"
   64 |       state: absent
   65 | 
   66 |   # KINIT
   67 | 
   68 |   - name: Set default principal if not given
   69 |     ansible.builtin.set_fact:
   70 |       ipaadmin_principal: admin
   71 |     when: ipaadmin_principal is undefined
   72 | 
   73 |   - name: Authenticate using kinit with password for "{{ ipaadmin_principal }}"
   74 |     ansible.builtin.command: kinit "{{ ipaadmin_principal }}"
   75 |     args:
   76 |       stdin: "{{ ipaadmin_password }}"
   77 |     when: ipaadmin_password is defined
   78 | 
   79 |   - name: Authenticate using kinit with keytab for "{{ ipaadmin_principal }}"
   80 |     ansible.builtin.command: kinit -kt "{{ ipaadmin_keytab }}" "{{ ipaadmin_principal }}"
   81 |     when: ipaadmin_keytab is defined
   82 | 
   83 |   # Enable and start smartcard daemon
   84 | 
   85 |   - name: Enable and start smartcard daemon
   86 |     ansible.builtin.service:
   87 |       name: pcscd
   88 |       enabled: true
   89 |       state: started
   90 | 
   91 |   # GET VARS FROM IPA
   92 | 
   93 |   - name: Get VARS from IPA
   94 |     ipasmartcard_client_get_vars:
   95 |     register: ipasmartcard_client_vars
   96 | 
   97 |   # Add pkcs11 module to systemwide db
   98 | 
   99 |   - name: Add pkcs11 module to systemwide db
  100 |     ansible.builtin.script: ipasmartcard_client_add_pkcs11_module_to_systemwide_db.sh
  101 |                             "{{ ipasmartcard_client_vars.NSS_DB_DIR }}"
  102 | 
  103 |   # Ensure /etc/sssd/pki exists
  104 | 
  105 |   - name: Prepare for authselect
  106 |     when: ipasmartcard_client_vars.USE_AUTHSELECT
  107 |     block:
  108 |     - name: Ensure /etc/sssd/pki exists
  109 |       ansible.builtin.file:
  110 |         path: /etc/sssd/pki
  111 |         state: directory
  112 |         mode: "0711"
  113 | 
  114 |     - name: Ensure /etc/sssd/pki/sssd_auth_ca_db.pem is absent
  115 |       ansible.builtin.file:
  116 |         path: /etc/sssd/pki/sssd_auth_ca_db.pem
  117 |         state: absent
  118 | 
  119 |   # Upload smartcard CA certificates to systemwide db
  120 | 
  121 |   - name: Upload smartcard CA certificates to systemwide db
  122 |     ansible.builtin.script: ipasmartcard_client_add_ca_to_systemwide_db.sh
  123 |                             "{{ item }}"
  124 |                             "{{ ipasmartcard_client_vars.NSS_DB_DIR }}"
  125 |     with_items: "{{ result_validate_ca_certs.ca_cert_files }}"
  126 | 
  127 |   # Newer version of sssd use OpenSSL and read the CA certs
  128 |   # from /etc/sssd/pki/sssd_auth_ca_db.pem
  129 | 
  130 |   - name: Add CA certs to /etc/sssd/pki/sssd_auth_ca_db.pem
  131 |     ansible.builtin.script: ipasmartcard_client_add_ca_to_sssd_auth_ca_db.sh
  132 |                             "{{ item }}"
  133 |                             /etc/sssd/pki/sssd_auth_ca_db.pem
  134 |     with_items: "{{ result_validate_ca_certs.ca_cert_files }}"
  135 |     when: ipasmartcard_client_vars.USE_AUTHSELECT
  136 | 
  137 |   # Update ipa CA certificate store
  138 | 
  139 |   - name: Update ipa CA certificate store
  140 |     ansible.builtin.command: ipa-certupdate
  141 | 
  142 |   # Run authselect or authconfig to configure smartcard auth
  143 | 
  144 |   - name: Use authselect to enable Smart Card authentication
  145 |     ansible.builtin.command: authselect enable-feature with-smartcard
  146 |     when: ipasmartcard_client_vars.USE_AUTHSELECT
  147 | 
  148 |   - name: Use authconfig to enable Smart Card authentication
  149 |     ansible.builtin.command: authconfig --enablesssd --enablesssdauth --enablesmartcard --smartcardmodule=sssd --smartcardaction=1 --updateall
  150 |     when: not ipasmartcard_client_vars.USE_AUTHSELECT
  151 | 
  152 |   # Set pam_cert_auth=True in /etc/sssd/sssd.conf
  153 | 
  154 |   - name: Store NSS OCSP upgrade state
  155 |     ansible.builtin.command: "{{ ipasmartcard_client_vars.python_interpreter }}"
  156 |     args:
  157 |       stdin: |
  158 |         from SSSDConfig import SSSDConfig
  159 |         c = SSSDConfig()
  160 |         c.import_config()
  161 |         c.set("pam", "pam_cert_auth", "True")
  162 |         c.write()
  163 |     when: ipasmartcard_client_vars.USE_AUTHSELECT
  164 | 
  165 |   # Restart sssd
  166 | 
  167 |   - name: Restart sssd
  168 |     ansible.builtin.service:
  169 |       name: sssd
  170 |       state: restarted
  171 | 
  172 |   ### ALWAYS ###
  173 | 
  174 |   always:
  175 |   - name: Destroy Kerberos tickets
  176 |     ansible.builtin.command: kdestroy -A
```

## Frozen tracked paths in the relevant role/scope

```text
roles/ipasmartcard_client/README.md
roles/ipasmartcard_client/defaults/main.yml
roles/ipasmartcard_client/files/ipasmartcard_client_add_ca_to_sssd_auth_ca_db.sh
roles/ipasmartcard_client/files/ipasmartcard_client_add_ca_to_systemwide_db.sh
roles/ipasmartcard_client/files/ipasmartcard_client_add_pkcs11_module_to_systemwide_db.sh
roles/ipasmartcard_client/library/ipasmartcard_client_get_vars.py
roles/ipasmartcard_client/library/ipasmartcard_client_validate_ca_certs.py
roles/ipasmartcard_client/meta/main.yml
roles/ipasmartcard_client/tasks/main.yml
roles/ipasmartcard_client/vars/default.yml
```

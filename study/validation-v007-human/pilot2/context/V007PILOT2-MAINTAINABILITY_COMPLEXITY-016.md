# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-016

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: maintainability_complexity
- Rule: `ansibleguard/excessive-nesting`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `roles/auth_upgrade/tasks/auth.yml` (reported anchor line 189)
- Flagged construct: not named by the finding; the anchor line 189 lies in the task at line 189, name `auth | Delete the tmp files`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–202 of 202:

```text
    1 | ---
    2 | - name: auth | check if auth is enable
    3 |   command: "{{ scale_command_path }}mmuserauth service list"
    4 |   register: scale_auth_status
    5 |   ignore_errors: true
    6 |   failed_when: false
    7 |   run_once: true
    8 | 
    9 | - block:
   10 |      - name: auth | Register value of FILE_AUTH_TYPE variable
   11 |        command: "{{ scale_command_path }}mmccr vget FILE_AUTH_TYPE"
   12 |        register: scale_file_auth_type
   13 |        ignore_errors: true
   14 |        failed_when: false
   15 |        run_once: true
   16 | 
   17 |      - block:
   18 |      
   19 |           - name: auth | Check if LDAPMAP_DOMAINS is already present
   20 |             command: "{{ scale_command_path }}mmccrnv authccr get LDAPMAP_DOMAINS"
   21 |             register: scale_temp
   22 |             ignore_errors: true
   23 |             failed_when: false
   24 |             run_once: true
   25 |  
   26 |           - name: auth | Setting new variable LDAPMAP_DOMAINS for Authentication
   27 |             command: "{{ scale_command_path }}mmccrnv authccr put LDAPMAP_DOMAINS none"
   28 |             when: scale_temp is failed
   29 | 
   30 |           - name: auth | Check if value of SERVERS is set
   31 |             command: "{{ scale_command_path }}mmccrnv authccr get SERVERS | grep -w '\"*\"'"
   32 |             register: scale_temp
   33 |             ignore_errors: true
   34 |             failed_when: false
   35 |             run_once: true
   36 |     
   37 |           - name: auth | Setting new variable SERVERS for Authentication
   38 |             command: "{{ scale_command_path }}mmccrnv authccr put SERVERS '\"*\"'"
   39 |             when: scale_temp.rc != 0
   40 |             run_once: true
   41 |             delegate_to: localhost
   42 | 
   43 |           - name: auth | Collect NETBIOS name
   44 |             command: "{{ scale_command_path }}mmccrnv authccr get NETBIOS_NAME"
   45 |             register: scale_auth_netbios
   46 |             run_once: true
   47 | 
   48 |           - name: auth | Check if USER_NAME is already set
   49 |             command: "{{ scale_command_path }}mmccrnv authccr get USER_NAME | sed 's/$$//' | egrep {{ scale_auth_netbios.stdout }}$"
   50 |             register: scale_temp
   51 |             ignore_errors: true
   52 |             failed_when: false
   53 |             run_once: true
   54 | 
   55 |           - name: auth | Setting new variable USER_NAME for Authentication
   56 |             command: "{{ scale_command_path }}mmccrnv authccr put USER_NAME {{ scale_auth_netbios.stdout }}'$'"
   57 |             when: scale_temp.rc != 0
   58 |             run_once: true
   59 |             delegate_to: localhost
   60 | 
   61 |           - name: auth | Check if UNIXMAP_DOMAINS contain none or domXX(10-20:unix) or domYY(30-40:win)
   62 |             command: "{{ scale_command_path }}mmccrnv authccr get UNIXMAP_DOMAINS"
   63 |             register: scale_temp
   64 |             ignore_errors: true
   65 |             failed_when: false
   66 |             run_once: true
   67 | 
   68 |           - block:
   69 |                - name: auth | Collect UNIXMAP_DOMAINS name
   70 |                  command: "{{ scale_command_path }}mmccrnv authccr get UNIXMAP_DOMAINS | tr -d ')')':win)'"
   71 |                  register: scale_unixmap_domain
   72 |                  run_once: true
   73 | 
   74 |                - name: auth | Set variable UNIXMAP_DOMAINS for Authentication
   75 |                  command: "{{ scale_command_path }}mmccrnv authccr put UNIXMAP_DOMAINS {{ scale_unixmap_domain.stdout }}')':win)"
   76 |                  run_once: true
   77 |                  delegate_to: localhost
   78 |             when: '"none" not in scale_temp.stdout and ":win" not in scale_temp.stdout and ":unix" not in scale_temp.stdout'
   79 | 
   80 |        when: '"ad" in scale_file_auth_type.stdout'
   81 | 
   82 |      - name: auth | Update the TLS_CIPHER_SUITE with proper string which will ensure minimum TLS version(1-2) is enforced
   83 |        set_fact:
   84 |            ldaptmppath : "/var/mmfs/tmp/LDAP_CONF_TMP_1"
   85 |            ldapnewpath : "/var/mmfs/tmp/LDAP_CONF_TMP_2"
   86 |            isFileAuth : false
   87 |            isTLSenabled : false
   88 |            getLDAPfile : false
   89 |            putLDAPfile : false
   90 |            isCipherPresent : false
   91 |            isProtoPresent : false
   92 |            searchstring1 : "TLS_CIPHER_SUITE"
   93 |            searchstring2 : "TLS_PROTOCOL_MIN"
   94 |            newTLSstring : ""
   95 |            newPROTstring : "TLS_PROTOCOL_MIN 3.3"
   96 |        run_once: true
   97 |        delegate_to: localhost
   98 | 
   99 |      - name: auth | Check current auth scheme
  100 |        set_fact:
  101 |            isFileAuth : true
  102 |        when: 'scale_file_auth_type.stdout is defined and "ldap" in scale_file_auth_type.stdout'
  103 |        run_once: true
  104 |        delegate_to: localhost
  105 | 
  106 |      - block:
  107 |           - name: auth | Check if TLS is enabled or not
  108 |             command: "{{ scale_command_path }}mmccrnv authccr get ENABLE_SERVER_TLS"
  109 |             register: scale_temp
  110 |             run_once: true
  111 |             delegate_to: localhost
  112 |             failed_when: false
  113 |             ignore_errors: true
  114 |             failed_when: false
  115 | 
  116 |           - name: auth | Set isTLSenabled flag
  117 |             set_fact:
  118 |                 isTLSenabled : true
  119 |             when: 'scale_temp.stdout is defined and "true" in scale_temp.stdout'
  120 | 
  121 |      - block:
  122 |           - name: auth | If auth scheme = LDAP and TLS is enabled, get the ldap.conf file from mmccr
  123 |             command: "{{ scale_command_path }}mmccr fget LDAP_CONF {{ ldaptmppath }}"
  124 |             register: scale_temp
  125 |             run_once: true
  126 |             delegate_to: localhost
  127 | 
  128 |           - name: auth | Set getLDAPfile flag
  129 |             set_fact:
  130 |                 getLDAPfile : true
  131 |             run_once: true
  132 |             delegate_to: localhost
  133 |             when: scale_temp.rc is defined and scale_temp.rc == 0 
  134 |             #need to change this condition while testing for ldap depending on what is the output for scale_temp of the previous task
  135 | 
  136 |           - name: auth | Set newTLSstring variable
  137 |             set_fact:
  138 |                 newTLSstring : "TLS_CIPHER_SUITE DEFAULT:!SSLv3:!TLSv1:!TLSv1.1:@STRENGTH"
  139 |             when: (ansible_distribution in scale_rhel_distribution and ansible_distribution_major_version == '7') or (ansible_distribution in scale_rhel_distribution and ansible_distribution_major_version == '8') or (ansible_distribution in scale_sles_distribution and ansible_distribution_major_version == '15')
  140 |             run_once: true
  141 |             delegate_to: localhost
  142 | 
  143 |           - name: auth | Set newTLSstring variable
  144 |             set_fact:
  145 |                 newTLSstring : "NORMAL:-VERS-ALL:+VERS-TLS1.3:+VERS-TLS1.2:-AES-128-CBC:-AES-256-CBC"
  146 |             when: ansible_distribution in scale_ubuntu_distribution and ansible_distribution_major_version == '20'
  147 |             run_once: true
  148 |             delegate_to: localhost
  149 | 
  150 |           - block:
  151 |               - name: auth | Go through line by line and check if our search strings macthes ,if matches, replace it, if not, add the new string to the file
  152 |                 include_tasks: parseFile.yml
  153 |                 loop: "{{ lookup('file', ldaptmppath, errors='ignore').splitline() }}"
  154 |                 run_once: true
  155 | 
  156 |               - name: auth | write newTLSstring to the file
  157 |                 lineinfile:
  158 |                     path: "{{ ldapnewpath }}"
  159 |                     create: true
  160 |                     line: "{{ newTLSstring }}"
  161 |                     state: present
  162 |                     insertafter: '\n'
  163 |                 when: not isCipherPresent|bool
  164 | 
  165 |               - name: auth | write newTLSstring to the file
  166 |                 lineinfile:
  167 |                      path: "{{ ldapnewpath }}"
  168 |                      create: true
  169 |                      line: "{{ newPROTstring }}"
  170 |                      state: present
  171 |                      insertafter: '\n'
  172 |                 when: not isProtoPresent|bool
  173 | 
  174 |               - name: auth | put back the new file to mmccr
  175 |                 command: "{{ scale_command_path }}mmccr fput LDAP_CONF {{ ldapnewpath }}"
  176 |                 register: scale_temp
  177 |                 run_once: true
  178 |                 delegate_to: localhost
  179 | 
  180 |               - name: auth | Set putLDAPfile flag
  181 |                 set_fact:
  182 |                     putLDAPfile : true
  183 |                 when: scale_temp.rc == 0
  184 |  
  185 |               - block:
  186 |                    - name: auth | Do callback for auth file change
  187 |                      command: "{{ scale_command_path }}mmcesop cesauthfilechange ldap"
  188 | 
  189 |                    - name: auth | Delete the tmp files
  190 |                      file:
  191 |                          path: "{{ ldapnewpath }}"
  192 |                          state: absent
  193 | 
  194 |                    - name: auth | Delete the tmp files
  195 |                      file:
  196 |                         path: "{{ ldaptmppath }}"
  197 |                         state: absent
  198 |                 when: putLDAPfile|bool
  199 |             when: getLDAPfile|bool
  200 |        when: isFileAuth|bool and isTLSenabled|bool
  201 |        ignore_errors: true
  202 |   when: scale_auth_status.rc == 0
```

# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-002

- Repository: `ansible-lockdown/RHEL8-CIS`
- Commit: `97a6a9aa80506900009129aa389759d6884d5ec5`
- Family: maintainability_complexity
- Rule: `ansibleguard/complex-playbook`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `tasks/section_5/cis_5.3.3.4.x.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`tasks/section_5/cis_5.3.3.4.x.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–195 of 195:

```text
    1 | ---
    2 | 
    3 | - name: "5.3.3.4.1 | PATCH | Ensure pam_unix does not include nullok"
    4 |   when: rhel8cis_rule_5_3_3_4_1
    5 |   tags:
    6 |     - level1-server
    7 |     - level1-workstation
    8 |     - automated
    9 |     - patch
   10 |     - pam
   11 |     - NIST800-53R5_CM-6
   12 |     - rule_5.3.3.4.1
   13 |   block:
   14 |     - name: "5.3.3.4.1 | PATCH | Ensure pam_unix does not include nullok | capture state"
   15 |       ansible.builtin.shell: |
   16 |         set -o pipefail
   17 |         grep -P -- '^\h*(auth|account|password|session)\h+(requisite|required|sufficient)\h+pam_unix\.so\b' /etc/pam.d/{password,system}-auth | grep -P -- '\bnullok\b'
   18 |       args:
   19 |         executable: "{{ rhel8cis_shell_executable }}"
   20 |       changed_when: false
   21 |       failed_when: discovered_pam_nullok.rc not in [ 0, 1 ]
   22 |       check_mode: false
   23 |       register: discovered_pam_nullok
   24 | 
   25 |     - name: "5.3.3.4.1 | PATCH | Ensure pam_unix does not include nullok | pam_files"
   26 |       when:
   27 |         - discovered_pam_nullok.stdout | length > 0
   28 |         - not rhel8cis_allow_authselect_updates
   29 |       ansible.builtin.replace:
   30 |         path: "/etc/pam.d/{{ item }}-auth"
   31 |         regexp: nullok
   32 |         replace: ''
   33 |       loop:
   34 |         - password
   35 |         - system
   36 | 
   37 |     - name: "5.3.3.4.1 | PATCH | Ensure pam_unix does not include nullok | update authselect"
   38 |       when:
   39 |         - discovered_pam_nullok is defined
   40 |         - discovered_pam_nullok.stdout | length > 0
   41 |         - rhel8cis_allow_authselect_updates
   42 |       ansible.builtin.command: authselect enable-feature without-nullok
   43 |       changed_when: true
   44 |       check_mode: false
   45 |       notify: Update authselect
   46 | 
   47 | - name: "5.3.3.4.2 | PATCH | Ensure pam_unix does not include remember"
   48 |   when: rhel8cis_rule_5_3_3_4_2
   49 |   tags:
   50 |     - level1-server
   51 |     - level1-workstation
   52 |     - automated
   53 |     - patch
   54 |     - NIST800-53R5_NA
   55 |     - pam
   56 |     - rule_5.3.3.4.2
   57 |   block:
   58 |     - name: "5.3.3.4.2 | AUDIT | Ensure pam_unix does not include remember | capture state"
   59 |       ansible.builtin.shell: |
   60 |         set -o pipefail
   61 |         grep -Pi '^\h*password\h+([^#\n\r]+\h+)?pam_unix\.so\b' /etc/pam.d/{password,system}-auth | grep -P '\bremember=\d\b'
   62 |       args:
   63 |         executable: "{{ rhel8cis_shell_executable }}"
   64 |       changed_when: false
   65 |       failed_when: discovered_pam_remember.rc not in [ 0, 1 ]
   66 |       check_mode: false
   67 |       register: discovered_pam_remember
   68 | 
   69 |     - name: "5.3.3.4.2 | PATCH | Ensure pam_unix does not include remember | pam_files"
   70 |       when:
   71 |         - discovered_pam_remember is defined
   72 |         - discovered_pam_remember | length > 0
   73 |         - not rhel8cis_allow_authselect_updates
   74 |       ansible.builtin.replace:
   75 |         path: "/etc/pam.d/{{ item }}-auth"
   76 |         regexp: ^(\s*password\s+(requisite|required|sufficient)\s+pam_unix\.so)(.*)remember\s*=\s*\d+(.*$)
   77 |         replace: \1\3\4
   78 |       loop:
   79 |         - password
   80 |         - system
   81 | 
   82 |     - name: "5.3.3.4.2 | PATCH | Ensure pam_unix does not include remember | authselect_files"
   83 |       when:
   84 |         - discovered_pam_remember is defined
   85 |         - discovered_pam_remember | length > 0
   86 |         - rhel8cis_allow_authselect_updates
   87 |         - "'example' not in rhel8cis_authselect_custom_profile_name"
   88 |       ansible.builtin.replace:
   89 |         path: "/etc/authselect/custom/{{ rhel8cis_authselect_custom_profile_name }}/{{ item }}-auth"
   90 |         regexp: ^(\s*password\s+(requisite|required|sufficient)\s+pam_unix\.so)(.*)remember\s*=\s*\d+(.*$)
   91 |         replace: \1\3\4
   92 |       loop:
   93 |         - password
   94 |         - system
   95 |       notify: Update authselect
   96 | 
   97 | - name: "5.3.3.4.3 | PATCH | Ensure pam_unix includes a strong password hashing algorithm"
   98 |   when: rhel8cis_rule_5_3_3_4_3
   99 |   tags:
  100 |     - level1-server
  101 |     - level1-workstation
  102 |     - automated
  103 |     - patch
  104 |     - NIST800-53R5_IA-5
  105 |     - pam
  106 |     - rule_5.3.3.4.3
  107 |   block:
  108 |     - name: "5.3.3.4.3 | AUDIT | Ensure pam_unix includes a strong password hashing algorithm | capture state"
  109 |       ansible.builtin.shell: |
  110 |         set -o pipefail
  111 |         grep -P -- '^\h*password\h+([^#\n\r]+)\h+pam_unix\.so\h+([^#\n\r]+\h+)?(sha512|yescrypt)\b' /etc/pam.d/{password,system}-auth | grep -v {{ rhel8cis_pam_pwhash }}
  112 |       args:
  113 |         executable: "{{ rhel8cis_shell_executable }}"
  114 |       changed_when: false
  115 |       failed_when: discovered_hash_state.rc not in [ 0, 1 ]
  116 |       check_mode: false
  117 |       register: discovered_hash_state
  118 | 
  119 |     - name: "5.3.3.4.3 | PATCH | Ensure pam_unix includes a strong password hashing algorithm | pam_files"
  120 |       when:
  121 |         - not rhel8cis_allow_authselect_updates
  122 |         - discovered_hash_state is defined
  123 |         - discovered_hash_state | length > 0
  124 |       ansible.builtin.replace:
  125 |         path: "/etc/pam.d/{{ item }}-auth"
  126 |         regexp: ^(\s*password\s+(requisite|required|sufficient)\s+pam_unix\.so)(.*)(sha512|yescrypt)(.*$)
  127 |         replace: \1\3\5 {{ rhel8cis_pam_pwhash }}
  128 |       loop:
  129 |         - password
  130 |         - system
  131 | 
  132 |     - name: "5.3.3.4.3 | PATCH | Ensure pam_unix includes a strong password hashing algorithm | authselect_files"
  133 |       when:
  134 |         - discovered_hash_state is defined
  135 |         - discovered_hash_state | length > 0
  136 |         - rhel8cis_allow_authselect_updates
  137 |         - "'example' not in rhel8cis_authselect_custom_profile_name"
  138 |       ansible.builtin.replace:
  139 |         path: "/etc/authselect/custom/{{ rhel8cis_authselect_custom_profile_name }}/{{ item }}-auth"
  140 |         regexp: ^(\s*password\s+(requisite|required|sufficient)\s+pam_unix\.so)(.*)(sha512|yescrypt)\s*=\s*\d+(.*$)
  141 |         replace: \1\3\5{{ rhel8cis_pam_pwhash }}
  142 |       loop:
  143 |         - password
  144 |         - system
  145 |       notify: Update authselect
  146 | 
  147 | - name: "5.3.3.4.4 | PATCH | Ensure pam_unix includes use_authtok"
  148 |   when: rhel8cis_rule_5_3_3_4_4
  149 |   tags:
  150 |     - level1-server
  151 |     - level1-workstation
  152 |     - automated
  153 |     - patch
  154 |     - NIST800-53R5_IA-5
  155 |     - pam
  156 |     - rule_5.3.3.4.4
  157 |   block:
  158 |     - name: "5.3.3.4.4 | PATCH | Ensure pam_unix includes use_authtok | capture state"
  159 |       ansible.builtin.shell: |
  160 |         set -o pipefail
  161 |         grep -P -- '^\h*password\h+([^#\n\r]+)\h+pam_unix\.so\h+([^#\n\r]+\h+)?use_authtok\b' /etc/pam.d/{password,system}-auth | grep -v use_authtok
  162 |       args:
  163 |         executable: "{{ rhel8cis_shell_executable }}"
  164 |       changed_when: false
  165 |       failed_when: discovered_pam_authtok.rc not in [ 0, 1 ]
  166 |       check_mode: false
  167 |       register: discovered_pam_authtok
  168 | 
  169 |     - name: "5.3.3.4.4 | PATCH | Ensure pam_unix includes use_authtok | pam_files"
  170 |       when:
  171 |         - not rhel8cis_allow_authselect_updates
  172 |         - discovered_pam_authtok is defined
  173 |         - discovered_pam_authtok | length > 0
  174 |       ansible.builtin.replace:
  175 |         path: "/etc/pam.d/{{ item }}-auth"
  176 |         regexp: ^(\s*password\s+(requisite|required|sufficient)\s+pam_unix\.so)(.*)(\s+use_authtok)\s*=\s*\d+(.*$)
  177 |         replace: \1\3\5 use_authtok
  178 |       loop:
  179 |         - password
  180 |         - system
  181 | 
  182 |     - name: "5.3.3.4.4 | PATCH | Ensure password same consecutive characters is configured | authselect_files"
  183 |       when:
  184 |         - discovered_pam_authtok is defined
  185 |         - discovered_pam_authtok | length > 0
  186 |         - rhel8cis_allow_authselect_updates
  187 |         - "'example' not in rhel8cis_authselect_custom_profile_name"
  188 |       ansible.builtin.replace:
  189 |         path: "/etc/authselect/custom/{{ rhel8cis_authselect_custom_profile_name }}/{{ item }}-auth"
  190 |         regexp: ^(\s*password\s+(requisite|required|sufficient)\s+pam_unix\.so)(.*)(\s+use_authtok)\s*=\s*\d+(.*$)
  191 |         replace: \1\3\5 use_authtok
  192 |       loop:
  193 |         - password
  194 |         - system
  195 |       notify: Update authselect
```

# Frozen source context: V007PILOT2-SECURITY-015

- Repository: `TechDufus/dotfiles`
- Commit: `abe3beabdf436c1a7aeeff66b6c2f5903f7b9878`
- Family: security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `pre_tasks/detect_sudo.yml` (reported anchor line 181)
- Flagged construct: task `set password-based sudo facts`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–255 of 255:

```text
    1 | ---
    2 | # Comprehensive sudo detection for cross-platform compatibility
    3 | # Sets facts that can be used throughout the playbook to handle privilege escalation
    4 | 
    5 | - name: Initialize sudo detection variables
    6 |   set_fact:
    7 |     has_sudo: false
    8 |     sudo_method: 'none'
    9 |     sudo_requires_password: [REDACTED_LITERAL]
   10 |     can_install_packages: false
   11 |     sudo_test_command: 'echo "sudo test successful"'
   12 |     detected_package_manager: ''
   13 |     privilege_escalation_available: false
   14 |     sudo_credentials_cached: [REDACTED_LITERAL]
   15 |     become_password_available: [REDACTED_LITERAL]
   16 |     sudo_password_based_available: [REDACTED_LITERAL]
   17 |     pkexec_available: false
   18 |     can_use_homebrew: false
   19 |     can_become: false
   20 | 
   21 | - name: Detect package manager based on OS
   22 |   block:
   23 |     - name: Set package manager for macOS
   24 |       set_fact:
   25 |         detected_package_manager: brew
   26 |       when:
   27 |         - ansible_facts['distribution'] == 'MacOSX'
   28 |         - ansible_facts['system'] == 'Darwin'
   29 | 
   30 |     - name: Set package manager for Ubuntu/Debian
   31 |       set_fact:
   32 |         detected_package_manager: apt
   33 |       when: ansible_facts['distribution'] in ['Ubuntu', 'Debian']
   34 | 
   35 |     - name: Set package manager for Arch
   36 |       set_fact:
   37 |         detected_package_manager: pacman
   38 |       when: ansible_facts['distribution'] == 'Archlinux'
   39 | 
   40 |     - name: Set package manager for modern Fedora/RHEL
   41 |       set_fact:
   42 |         detected_package_manager: dnf
   43 |       when:
   44 |         - ansible_facts['distribution'] in ['Fedora', 'RedHat', 'CentOS', 'AlmaLinux', 'Rocky']
   45 |         - ansible_facts['distribution'] == 'Fedora' or ansible_facts['distribution_major_version'] | int >= 8
   46 | 
   47 |     - name: Set package manager for older RHEL/CentOS
   48 |       set_fact:
   49 |         detected_package_manager: yum
   50 |       when:
   51 |         - ansible_facts['distribution'] in ['RedHat', 'CentOS']
   52 |         - ansible_facts['distribution_major_version'] | int < 8
   53 | 
   54 |     - name: Verify detected package manager exists
   55 |       command: "which {{ detected_package_manager }}"
   56 |       check_mode: false
   57 |       register: pm_check
   58 |       changed_when: false
   59 |       failed_when: false
   60 |       when: detected_package_manager is defined and detected_package_manager != ''
   61 | 
   62 |     - name: Reset package manager if not found
   63 |       set_fact:
   64 |         detected_package_manager: none
   65 |       when:
   66 |         - pm_check is defined
   67 |         - pm_check.rc is defined
   68 |         - pm_check.rc != 0
   69 | 
   70 | - name: Test passwordless sudo
   71 |   block:
   72 |     - name: Test sudo without password
   73 |       command: sudo -n {{ sudo_test_command }}
   74 |       check_mode: false
   75 |       register: sudo_nopass_test
   76 |       ignore_errors: true
   77 |       changed_when: false
   78 |       failed_when: false
   79 |       no_log: true
   80 | 
   81 |     - name: Set passwordless sudo facts
   82 |       set_fact:
   83 |         has_sudo: true
   84 |         sudo_method: 'sudo'
   85 |         sudo_requires_password: [REDACTED_LITERAL]
   86 |         sudo_credentials_cached: [REDACTED_LITERAL]
   87 |         privilege_escalation_available: true
   88 |       when: sudo_nopass_test.rc =[REDACTED_LITERAL]
   89 | 
   90 | - name: Test sudo with cached credentials
   91 |   when: not has_sudo
   92 |   block:
   93 |     - name: Check if sudo credentials are cached
   94 |       command: sudo -n -v
   95 |       check_mode: false
   96 |       register: sudo_cached_test
   97 |       ignore_errors: true
   98 |       changed_when: false
   99 |       failed_when: false
  100 |       no_log: true
  101 | 
  102 |     - name: Test sudo with potentially cached password
  103 |       command: sudo -n {{ sudo_test_command }}
  104 |       check_mode: false
  105 |       register: sudo_cached_exec
  106 |       ignore_errors: true
  107 |       changed_when: false
  108 |       failed_when: false
  109 |       when: sudo_cached_test.rc | default(1) == 0
  110 |       no_log: true
  111 | 
  112 |     - name: Set sudo with cached credentials facts
  113 |       set_fact:
  114 |         has_sudo: true
  115 |         sudo_method: 'sudo'
  116 |         sudo_requires_password: [REDACTED_LITERAL]
  117 |         sudo_credentials_cached: [REDACTED_LITERAL]
  118 |         privilege_escalation_available: true
  119 |       when:
  120 |         - sudo_cached_test.rc | default(1) == 0
  121 |         - sudo_cached_exec.rc | default(1) == 0
  122 | 
  123 | - name: Test alternative privilege escalation methods
  124 |   when: not has_sudo
  125 |   block:
  126 |     - name: Test doas (OpenBSD/some Linux)
  127 |       command: doas -n {{ sudo_test_command }}
  128 |       check_mode: false
  129 |       register: doas_test
  130 |       ignore_errors: true
  131 |       changed_when: false
  132 |       failed_when: false
  133 |       no_log: true
  134 | 
  135 |     - name: Set doas facts
  136 |       set_fact:
  137 |         has_sudo: true
  138 |         sudo_method: 'doas'
  139 |         sudo_requires_password: "{{ 'password' in doas_test.stderr | default('') }}"
  140 |         privilege_escalation_available: true
  141 |       when: doas_test.rc == 0
  142 | 
  143 |     - name: Test pkexec (PolicyKit)
  144 |       command: pkexec --disable-internal-agent {{ sudo_test_command }}
  145 |       check_mode: false
  146 |       register: pkexec_test
  147 |       ignore_errors: true
  148 |       changed_when: false
  149 |       failed_when: false
  150 |       when: not has_sudo
  151 |       no_log: true
  152 | 
  153 |     - name: Record pkexec availability
  154 |       set_fact:
  155 |         pkexec_available: true
  156 |       when:
  157 |         - not has_sudo
  158 |         - pkexec_test.rc | default(1) == 0
  159 | 
  160 | - name: Detect provided become password
  161 |   set_fact:
  162 |     become_password_available: [REDACTED VALUE BLOCK]
  163 |       [REDACTED ENCRYPTED VALUE]
  164 | 
  165 | - name: Detect password-based sudo availability
  166 |   when: not has_sudo
  167 |   block:
  168 |     - name: Check sudo binary for password-based escalation
  169 |       command: which sudo
  170 |       check_mode: false
  171 |       register: sudo_binary_check
  172 |       ignore_errors: true
  173 |       changed_when: false
  174 |       failed_when: false
  175 | 
  176 |     - name: Record password-based sudo availability
  177 |       set_fact:
  178 |         sudo_password_based_available: [REDACTED_LITERAL]
  179 |       when: sudo_binary_check.rc | default(1) == 0
  180 | 
  181 |     - name: Set password-based sudo facts
  182 |       set_fact:
  183 |         has_sudo: true
  184 |         sudo_method: 'sudo'
  185 |         sudo_requires_password: [REDACTED_LITERAL]
  186 |         sudo_credentials_cached: [REDACTED_LITERAL]
  187 |         privilege_escalation_available: true
  188 |       when:
  189 |         - sudo_binary_check.rc | default(1) == 0
  190 |         - become_password_available | default(false) | bool
  191 | 
  192 | - name: Determine package installation capability
  193 |   set_fact:
  194 |     can_use_homebrew: "{{ detected_package_manager == 'brew' }}"
  195 |     can_become: >-
  196 |       {{ has_sudo and
  197 |          ((not (sudo_requires_password | bool)) or
  198 |           (sudo_credentials_cached | default(false) | bool) or
  199 |           (become_password_available | default(false) | bool)) }}
  200 |     can_install_packages: >-
  201 |       {{ (detected_package_manager == 'brew') or
  202 |          (has_sudo and
  203 |           detected_package_manager in ['apt', 'pacman', 'dnf', 'yum'] and
  204 |           ((not (sudo_requires_password | bool)) or
  205 |            (sudo_credentials_cached | default(false) | bool) or
  206 |            (become_password_available | default(false) | bool))) }}
  207 | 
  208 | - name: Warn when sudo password is required
  209 |   ansible.builtin.debug:
  210 |     msg:
  211 |       - "Sudo is available, but no cached sudo credentials or Ansible become password were detected."
  212 |       - "Package roles will skip privileged installs unless you pre-cache sudo with `sudo -v` or run ansible-playbook with `--ask-become-pass`."
  213 |   when:
  214 |     - sudo_password_based_available | default(false) | bool
  215 |     - sudo_requires_password | bool
  216 |     - not (sudo_credentials_cached | default(false) | bool)
  217 |     - not (become_password_available | default(false) | bool)
  218 |     - detected_package_manager in ['apt', 'pacman', 'dnf', 'yum']
  219 | 
  220 | - name: Display privilege escalation detection results
  221 |   debug:
  222 |     msg:
  223 |       - "=== Privilege Escalation Detection Results ==="
  224 |       - "Has sudo/privilege access: {{ has_sudo }}"
  225 |       - "Method available: {{ sudo_method }}"
  226 |       - "Requires password: {{ sudo_requires_password }}"
  227 |       - "Can become: {{ can_become }}"
  228 |       - "Package manager: {{ detected_package_manager }}"
  229 |       - "Can install packages: {{ can_install_packages }}"
  230 |       - "============================================="
  231 | 
  232 | - name: Set Ansible become method based on detection
  233 |   set_fact:
  234 |     ansible_become_method: >-
  235 |       {%- if sudo_method == 'doas' -%}doas
  236 |       {%- elif sudo_method == 'sudo' -%}sudo
  237 |       {%- else -%}sudo{%- endif -%}
  238 |   when: has_sudo
  239 | 
  240 | - name: Note about Homebrew and sudo
  241 |   debug:
  242 |     msg: "Note: Homebrew on macOS does not require or accept sudo. Package installation is possible without privilege escalation."
  243 |   when:
  244 |     - detected_package_manager == 'brew'
  245 |     - ansible_facts['distribution'] == 'MacOSX'
  246 | 
  247 | - name: Warning when no privilege escalation available
  248 |   debug:
  249 |     msg:
  250 |       - "⚠️  WARNING: No privilege escalation method detected!"
  251 |       - "The playbook will continue but some tasks may be skipped."
  252 |       - "Package installation and system modifications will not be possible."
  253 |   when:
  254 |     - not has_sudo
  255 |     - detected_package_manager != 'brew'
```

# Frozen source context: V007PILOT-STRUCTURE_REUSE-027

- Repository: `chrisshaiman/lamware`
- Commit: `09f919635087b38354bce34c9bc48e7c6517b463`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `packer/ansible/roles/konstruktoid.hardening/tasks/sshconfig.yml` (reported anchor line 1)
- Object: `source_location` `dd96ec80685a3dd5724a061a6baf79201ae5d5373df761e4e5c37eb54fbb696a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–328 of 328:

```text
    1 | ---
    2 | - name: Get installed sshd version
    3 |   environment:
    4 |     PATH: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin/
    5 |   ansible.builtin.command:
    6 |     cmd: "{{ 'ssh -V' if ansible_facts.distribution == 'Debian' else 'sshd -V' }}"
    7 |   changed_when: false
    8 |   failed_when: false
    9 |   check_mode: false
   10 |   register: sshd_version
   11 | 
   12 | - name: Set ssh version as fact
   13 |   ansible.builtin.set_fact:
   14 |     ssh_installed_version: "{{ sshd_version.stderr_lines | regex_search('OpenSSH_([0-9+][0-9+].[0-9+]|[0-9+].[0-9]+)', '\\1') | first }}"
   15 | 
   16 | - name: Print SSH version fact
   17 |   ansible.builtin.debug:
   18 |     msg: "{{ ssh_installed_version }}"
   19 | 
   20 | - name: Ensure privilege separation directories exist
   21 |   become: true
   22 |   ansible.builtin.file:
   23 |     path: "{{ item.path }}"
   24 |     owner: root
   25 |     group: root
   26 |     state: directory
   27 |     mode: "{{ item.mode }}"
   28 |   register: privsep_dir
   29 |   changed_when:
   30 |     - privsep_dir is changed
   31 |     - not (item.path == '/run/sshd' and ansible_facts.distribution == 'Ubuntu')
   32 |   loop:
   33 |     - { path: /run/sshd, mode: "0755" }
   34 |     - { path: /usr/share/empty.sshd, mode: "0711" }
   35 |     - { path: /var/empty, mode: "0755" }
   36 |     - { path: /var/empty/sshd, mode: "0711" }
   37 | 
   38 | - name: Configure sshd using sshd_config.d
   39 |   become: true
   40 |   ansible.builtin.template:
   41 |     src: "{{ sshd_tmpfiles_template }}"
   42 |     dest: /usr/lib/tmpfiles.d/ssh.conf
   43 |     backup: true
   44 |     mode: "0644"
   45 |     owner: root
   46 |     group: root
   47 | 
   48 | - name: Stat sysconfig sshd configuration
   49 |   ansible.builtin.stat:
   50 |     path: /etc/sysconfig/sshd
   51 |   register: sysconfig_sshd
   52 | 
   53 | - name: Remove sshd system crypto policy
   54 |   become: true
   55 |   ansible.builtin.lineinfile:
   56 |     dest: /etc/sysconfig/sshd
   57 |     state: absent
   58 |     regexp: ^\s*CRYPTO_POLICY.*$
   59 |   when:
   60 |     - sysconfig_sshd.stat.exists
   61 | 
   62 | - name: Get sshd Include config
   63 |   become: true
   64 |   ansible.builtin.command:
   65 |     cmd: grep -E "^Include " /etc/ssh/sshd_config
   66 |   register: grep_include
   67 |   changed_when: false
   68 |   failed_when: false
   69 |   check_mode: false
   70 | 
   71 | - name: Check if sshd_config.d exits
   72 |   ansible.builtin.stat:
   73 |     path: /etc/ssh/sshd_config.d
   74 |   register: sshd_config_d
   75 | 
   76 | - name: Clear pre-existing custom configurations in /etc/ssh/sshd_config.d
   77 |   when:
   78 |     - sshd_config_d_force_clear | bool
   79 |     - sshd_config_d.stat.exists
   80 |   block:
   81 |     - name: Search pre-existing custom configurations in /etc/ssh/sshd_config.d
   82 |       become: true
   83 |       ansible.builtin.find:
   84 |         path: /etc/ssh/sshd_config.d
   85 |         patterns: "*"
   86 |       register: sshd_config_d_content
   87 | 
   88 |     - name: Clear pre-existing custom configurations in /etc/ssh/sshd_config.d
   89 |       become: true
   90 |       ansible.builtin.file:
   91 |         path: "{{ item.path }}"
   92 |         state: absent
   93 |       loop: "{{ sshd_config_d_content.files }}"
   94 | 
   95 | - name: Ensure /etc/ssh/sshd_config permissions
   96 |   become: true
   97 |   ansible.builtin.file:
   98 |     path: /etc/ssh/sshd_config
   99 |     owner: root
  100 |     group: root
  101 |     state: file
  102 |     mode: "0600"
  103 | 
  104 | - name: SSH moduli file
  105 |   become: true
  106 |   when:
  107 |     - sshd_update_moduli
  108 |   tags:
  109 |     - ssh
  110 |   block:
  111 |     - name: Stat moduli file
  112 |       ansible.builtin.stat:
  113 |         path: /etc/ssh/moduli
  114 |       register: ssh_moduli
  115 | 
  116 |     - name: Update moduli file
  117 |       ansible.builtin.get_url:
  118 |         url: "{{ sshd_update_moduli_url }}"
  119 |         dest: "{{ '/etc/ssh/' if ssh_moduli.stat.exists else '/etc/' }}"
  120 |         owner: root
  121 |         group: root
  122 |         mode: "0644"
  123 | 
  124 | - name: Find DSA host files
  125 |   become: true
  126 |   ansible.builtin.find:
  127 |     paths: /etc/ssh
  128 |     patterns: "*_host_dsa_key*"
  129 |   register: dsa_files
  130 | 
  131 | - name: Remove DSA host files
  132 |   become: true
  133 |   ansible.builtin.file:
  134 |     path: "{{ item.path }}"
  135 |     state: absent
  136 |   loop: "{{ dsa_files.files }}"
  137 | 
  138 | - name: Set default for sshd_host_keys_files if not supplied
  139 |   become: true
  140 |   when:
  141 |     - not sshd_host_keys_files
  142 |   block:
  143 |     - name: Generate SSH RSA keypair
  144 |       community.crypto.openssh_keypair:
  145 |         state: present
  146 |         type: rsa
  147 |         size: "{{ sshd_required_rsa_size }}"
  148 |         path: /etc/ssh/ssh_host_rsa_key
  149 | 
  150 |         mode: "{{ sshd_host_keys_mode }}"
  151 |         owner: "{{ sshd_host_keys_owner }}"
  152 |         group: "{{ 'ssh_keys' if (ansible_facts.os_family == 'RedHat' and ansible_facts.distribution_major_version < '10') else sshd_host_keys_group }}"
  153 |         regenerate: partial_idempotence
  154 | 
  155 |     - name: Generate SSH ECDSA keypair
  156 |       community.crypto.openssh_keypair:
  157 |         state: present
  158 |         type: ecdsa
  159 |         size: "{{ sshd_required_ecdsa_size }}"
  160 |         path: /etc/ssh/ssh_host_ecdsa_key
  161 |         mode: "{{ sshd_host_keys_mode }}"
  162 |         owner: "{{ sshd_host_keys_owner }}"
  163 |         group: "{{ 'ssh_keys' if (ansible_facts.os_family == 'RedHat' and ansible_facts.distribution_major_version < '10') else sshd_host_keys_group }}"
  164 |         regenerate: partial_idempotence
  165 |       when:
  166 |         - ssh_installed_version is version('6.0', '>=')
  167 | 
  168 |     - name: Generate SSH Ed25519 keypair
  169 |       community.crypto.openssh_keypair:
  170 |         state: present
  171 |         type: ed25519
  172 |         path: /etc/ssh/ssh_host_ed25519_key
  173 |         mode: "{{ sshd_host_keys_mode }}"
  174 |         owner: "{{ sshd_host_keys_owner }}"
  175 |         group: "{{ 'ssh_keys' if (ansible_facts.os_family == 'RedHat' and ansible_facts.distribution_major_version < '10') else sshd_host_keys_group }}"
  176 |         regenerate: partial_idempotence
  177 |       when:
  178 |         - ssh_installed_version is version('6.5', '>=')
  179 | 
  180 |     - name: Set hostkeys according to openssh-version if openssh >= 5.3
  181 |       ansible.builtin.set_fact:
  182 |         sshd_host_keys_files:
  183 |           - /etc/ssh/ssh_host_rsa_key
  184 |       when:
  185 |         - ssh_installed_version is version('5.3', '>=')
  186 |         - ssh_installed_version is version('6.0', '<')
  187 | 
  188 |     - name: Set hostkeys according to openssh-version if openssh >= 6.0
  189 |       ansible.builtin.set_fact:
  190 |         sshd_host_keys_files:
  191 |           - /etc/ssh/ssh_host_rsa_key
  192 |           - /etc/ssh/ssh_host_ecdsa_key
  193 |       when:
  194 |         - ssh_installed_version is version('6.0', '>=')
  195 |         - ssh_installed_version is version('6.5', '<')
  196 | 
  197 |     - name: Set hostkeys according to openssh-version if openssh >= 6.5
  198 |       ansible.builtin.set_fact:
  199 |         sshd_host_keys_files:
  200 |           - /etc/ssh/ssh_host_rsa_key
  201 |           - /etc/ssh/ssh_host_ecdsa_key
  202 |           - /etc/ssh/ssh_host_ed25519_key
  203 |       when:
  204 |         - ssh_installed_version is version('6.5', '>=')
  205 | 
  206 | - name: Disable PAM dynamic MOTD
  207 |   become: true
  208 |   community.general.pamd:
  209 |     name: sshd
  210 |     type: session
  211 |     control: optional
  212 |     module_path: pam_motd.so
  213 |     state: absent
  214 |     backup: true
  215 |   when:
  216 |     - sshd_use_pam | bool
  217 |     - not (sshd_print_pam_motd | bool)
  218 | 
  219 | - name: Check variable sshd_config_force_replace
  220 |   ansible.builtin.set_fact:
  221 |     sshd_config_force_replace: true
  222 |   when: >
  223 |     sshd_match_users is defined and sshd_match_users | length > 0 or
  224 |     sshd_match_groups is defined and sshd_match_groups | length > 0 or
  225 |     sshd_match_addresses is defined and sshd_match_addresses| length > 0 or
  226 |     sshd_match_local_ports is defined and sshd_match_local_ports | length > 0 or
  227 |     (sshd_sftp_only_group is defined and sshd_sftp_only_group | length != 0)
  228 | 
  229 | - name: Create trusted ca keys
  230 |   ansible.builtin.lineinfile:
  231 |     dest: "{{ sshd_trusted_user_ca_keys_file }}"
  232 |     line: |
  233 |       {{ sshd_trusted_user_ca_keys_base64 | b64decode }}
  234 |     create: true
  235 |     mode: "0600"
  236 |     owner: root
  237 |     group: root
  238 |   when:
  239 |     - sshd_trusted_user_ca_keys_base64 | length > 0
  240 |     - sshd_trusted_user_ca_keys_file
  241 | 
  242 | - name: Configure sshd
  243 |   become: true
  244 |   ansible.builtin.template:
  245 |     src: "{{ sshd_config_template }}"
  246 |     dest: /etc/ssh/sshd_config
  247 |     backup: true
  248 |     mode: "0600"
  249 |     owner: root
  250 |     group: root
  251 |     validate: /usr/sbin/sshd -T -C user=root -C host=localhost -C addr=localhost -C lport=22 -f %s
  252 |   when: >
  253 |     (sshd_config_force_replace | bool) or
  254 |     (not sshd_config_d.stat.exists) or
  255 |     (grep_include.rc != 0)
  256 |   notify:
  257 |     - Disable ssh service
  258 |     - Restart ssh socket
  259 |     - Restart ssh service
  260 | 
  261 | - name: Configure sshd using sshd_config.d
  262 |   become: true
  263 |   ansible.builtin.template:
  264 |     src: "{{ sshd_config_template }}"
  265 |     dest: /etc/ssh/sshd_config.d/01-hardening.conf
  266 |     backup: true
  267 |     mode: "0600"
  268 |     owner: root
  269 |     group: root
  270 |     validate: /usr/sbin/sshd -T -C user=root -C host=localhost -C addr=localhost -C lport=22 -f %s
  271 |   when:
  272 |     - not (sshd_config_force_replace | bool)
  273 |     - sshd_config_d.stat.exists
  274 |     - grep_include.rc == 0
  275 |   notify:
  276 |     - Disable ssh service
  277 |     - Restart ssh socket
  278 |     - Restart ssh service
  279 | 
  280 | - name: Remove possible Subsystem duplicate
  281 |   become: true
  282 |   ansible.builtin.lineinfile:
  283 |     path: /etc/ssh/sshd_config
  284 |     regexp: ^Subsystem.*
  285 |     state: absent
  286 |   when:
  287 |     - not (sshd_config_force_replace | bool)
  288 |     - sshd_config_d.stat.exists
  289 |     - grep_include.rc == 0
  290 | 
  291 | - name: Stat sshd host keys
  292 |   become: true
  293 |   ansible.builtin.find:
  294 |     paths: /etc/ssh
  295 |     file_type: file
  296 |     patterns: ssh_host_*
  297 |     excludes: "*.pub"
  298 |   register: ssh_host_keys
  299 | 
  300 | - name: Set sshd host key permissions
  301 |   become: true
  302 |   ansible.builtin.file:
  303 |     owner: "{{ sshd_host_keys_owner }}"
  304 |     group: "{{ sshd_host_keys_group }}"
  305 |     mode: "{{ sshd_host_keys_mode }}"
  306 |     path: "{{ item.path }}"
  307 |   loop: "{{ ssh_host_keys.files }}"
  308 |   loop_control:
  309 |     label: "{{ item.path }}"
  310 | 
  311 | - name: Configure ssh
  312 |   tags:
  313 |     - ssh
  314 |   block:
  315 |     - name: Check if ssh_config.d exits
  316 |       ansible.builtin.stat:
  317 |         path: /etc/ssh/ssh_config.d
  318 |       register: ssh_config_d
  319 | 
  320 |     - name: Configure ssh client
  321 |       become: true
  322 |       ansible.builtin.template:
  323 |         src: "{{ ssh_config_template }}"
  324 |         dest: /etc/ssh/ssh_config
  325 |         backup: true
  326 |         mode: "0644"
  327 |         owner: root
  328 |         group: root
```

## Frozen tracked paths in the relevant role/scope

```text
packer/ansible/roles/konstruktoid.hardening/.ansible-lint
packer/ansible/roles/konstruktoid.hardening/.ansible-lint-ignore
packer/ansible/roles/konstruktoid.hardening/.github/CODEOWNERS
packer/ansible/roles/konstruktoid.hardening/.github/FUNDING.yml
packer/ansible/roles/konstruktoid.hardening/.github/ISSUE_TEMPLATE.md
packer/ansible/roles/konstruktoid.hardening/.github/ISSUE_TEMPLATE/bug_report.md
packer/ansible/roles/konstruktoid.hardening/.github/dependabot.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/dependency-review.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/issues.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/lint.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/molecule.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/schedlint.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/schedmainlint.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/scorecards.yml
packer/ansible/roles/konstruktoid.hardening/.github/workflows/slsa.yml
packer/ansible/roles/konstruktoid.hardening/.gitignore
packer/ansible/roles/konstruktoid.hardening/.pre-commit-config.yaml
packer/ansible/roles/konstruktoid.hardening/CODEOWNERS
packer/ansible/roles/konstruktoid.hardening/LICENSE
packer/ansible/roles/konstruktoid.hardening/README.md
packer/ansible/roles/konstruktoid.hardening/SECURITY.md
packer/ansible/roles/konstruktoid.hardening/STRUCTURE.md
packer/ansible/roles/konstruktoid.hardening/TESTING.md
packer/ansible/roles/konstruktoid.hardening/Vagrantfile
packer/ansible/roles/konstruktoid.hardening/aar-doc_template.j2
packer/ansible/roles/konstruktoid.hardening/action-lint/Dockerfile
packer/ansible/roles/konstruktoid.hardening/action-lint/entrypoint.sh
packer/ansible/roles/konstruktoid.hardening/defaults/main.yml
packer/ansible/roles/konstruktoid.hardening/files/usr/share/dict/passwords.list
packer/ansible/roles/konstruktoid.hardening/generate_defaults.py
packer/ansible/roles/konstruktoid.hardening/generate_doc_defaults.sh
packer/ansible/roles/konstruktoid.hardening/generate_molecule_env.sh
packer/ansible/roles/konstruktoid.hardening/handlers/main.yml
packer/ansible/roles/konstruktoid.hardening/meta/.galaxy_install_info
packer/ansible/roles/konstruktoid.hardening/meta/argument_specs.yml
packer/ansible/roles/konstruktoid.hardening/meta/main.yml
packer/ansible/roles/konstruktoid.hardening/molecule/almalinux/molecule.yml
packer/ansible/roles/konstruktoid.hardening/molecule/custom/molecule.yml
packer/ansible/roles/konstruktoid.hardening/molecule/debian/molecule.yml
packer/ansible/roles/konstruktoid.hardening/molecule/default/converge.yml
packer/ansible/roles/konstruktoid.hardening/molecule/default/molecule.yml
packer/ansible/roles/konstruktoid.hardening/molecule/default/verify.yml
packer/ansible/roles/konstruktoid.hardening/molecule/docker/molecule.yml
packer/ansible/roles/konstruktoid.hardening/molecule/single/molecule.yml
packer/ansible/roles/konstruktoid.hardening/molecule/ubuntu/molecule.yml
packer/ansible/roles/konstruktoid.hardening/postChecks.sh
packer/ansible/roles/konstruktoid.hardening/renovate.json
packer/ansible/roles/konstruktoid.hardening/requirements-dev.txt
packer/ansible/roles/konstruktoid.hardening/requirements-upstream.txt
packer/ansible/roles/konstruktoid.hardening/requirements.yml
packer/ansible/roles/konstruktoid.hardening/runTests.sh
packer/ansible/roles/konstruktoid.hardening/tasks/adduser.yml
packer/ansible/roles/konstruktoid.hardening/tasks/aide.yml
packer/ansible/roles/konstruktoid.hardening/tasks/apparmor.yml
packer/ansible/roles/konstruktoid.hardening/tasks/apport.yml
packer/ansible/roles/konstruktoid.hardening/tasks/auditd.yml
packer/ansible/roles/konstruktoid.hardening/tasks/automatic_updates.yml
packer/ansible/roles/konstruktoid.hardening/tasks/compilers.yml
packer/ansible/roles/konstruktoid.hardening/tasks/compilers_dnf_post_transaction_actions_plugin.yml
packer/ansible/roles/konstruktoid.hardening/tasks/cron.yml
packer/ansible/roles/konstruktoid.hardening/tasks/ctrlaltdel.yml
packer/ansible/roles/konstruktoid.hardening/tasks/disablewireless.yml
packer/ansible/roles/konstruktoid.hardening/tasks/extras.yml
packer/ansible/roles/konstruktoid.hardening/tasks/facts.yml
packer/ansible/roles/konstruktoid.hardening/tasks/fstab.yml
packer/ansible/roles/konstruktoid.hardening/tasks/hosts.yml
packer/ansible/roles/konstruktoid.hardening/tasks/ipv6.yml
packer/ansible/roles/konstruktoid.hardening/tasks/issue.yml
packer/ansible/roles/konstruktoid.hardening/tasks/journalconf.yml
packer/ansible/roles/konstruktoid.hardening/tasks/kernel.yml
packer/ansible/roles/konstruktoid.hardening/tasks/kernelmodules.yml
packer/ansible/roles/konstruktoid.hardening/tasks/limits.yml
packer/ansible/roles/konstruktoid.hardening/tasks/lockroot.yml
packer/ansible/roles/konstruktoid.hardening/tasks/logindconf.yml
packer/ansible/roles/konstruktoid.hardening/tasks/logindefs.yml
packer/ansible/roles/konstruktoid.hardening/tasks/main.yml
packer/ansible/roles/konstruktoid.hardening/tasks/motdnews.yml
packer/ansible/roles/konstruktoid.hardening/tasks/mount.yml
packer/ansible/roles/konstruktoid.hardening/tasks/netplan.yml
packer/ansible/roles/konstruktoid.hardening/tasks/packagemgmt.yml
packer/ansible/roles/konstruktoid.hardening/tasks/packages.yml
packer/ansible/roles/konstruktoid.hardening/tasks/password.yml
packer/ansible/roles/konstruktoid.hardening/tasks/path.yml
packer/ansible/roles/konstruktoid.hardening/tasks/post.yml
packer/ansible/roles/konstruktoid.hardening/tasks/postfix.yml
packer/ansible/roles/konstruktoid.hardening/tasks/pre.yml
packer/ansible/roles/konstruktoid.hardening/tasks/prelink.yml
packer/ansible/roles/konstruktoid.hardening/tasks/resolvedconf.yml
packer/ansible/roles/konstruktoid.hardening/tasks/rkhunter.yml
packer/ansible/roles/konstruktoid.hardening/tasks/rootaccess.yml
packer/ansible/roles/konstruktoid.hardening/tasks/sshconfig.yml
packer/ansible/roles/konstruktoid.hardening/tasks/sudo.yml
packer/ansible/roles/konstruktoid.hardening/tasks/suid.yml
packer/ansible/roles/konstruktoid.hardening/tasks/sysctl.yml
packer/ansible/roles/konstruktoid.hardening/tasks/systemdconf.yml
packer/ansible/roles/konstruktoid.hardening/tasks/timesyncd.yml
packer/ansible/roles/konstruktoid.hardening/tasks/ufw.yml
packer/ansible/roles/konstruktoid.hardening/tasks/umask.yml
packer/ansible/roles/konstruktoid.hardening/tasks/usbguard.yml
packer/ansible/roles/konstruktoid.hardening/tasks/users.yml
packer/ansible/roles/konstruktoid.hardening/templates/etc/adduser.conf.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/ansible/facts.d/sshkeys.fact
packer/ansible/roles/konstruktoid.hardening/templates/etc/apt/apt.conf.d/52unattended-upgrades-local.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/apt/apt.conf.d/53unattended-upgrades-custom-origins.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/audit/rules.d/hardening.rules.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/default/rkhunter.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/default/useradd.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/hosts.allow.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/hosts.deny.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/issue.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/login.defs.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/logrotate.conf.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/motd.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/pam.d/common-account.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/pam.d/common-auth.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/pam.d/common-password.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/pam.d/login.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/profile.d/initpath.sh.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/security/faillock.conf.j2
packer/ansible/roles/konstruktoid.hardening/templates/etc/security/limits.conf.j2
[listing truncated after 120 paths]
```

# Frozen source context: V007PILOT2-STRUCTURE_REUSE-015

- Repository: `ansible-lockdown/RHEL8-STIG`
- Commit: `baa075468dfa59050141c99d99dcacd2e977248c`
- Family: structure_reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `tasks/Cat_3/RHEL-08-010xxx.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`tasks/Cat_3/RHEL-08-010xxx.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–245 of 245:

```text
    1 | ---
    2 | 
    3 | - name: "LOW | RHEL-08-010171 | PATCH | RHEL 8 must have policycoreutils package installed."
    4 |   when: rhel8stig_010171
    5 |   tags:
    6 |     - RHEL-08-010171
    7 |     - CAT3
    8 |     - CCI-001084
    9 |     - NIST800-53R4_SC-3
   10 |     - SRG-OS-000134-GPOS-00068
   11 |     - SV-230241r1017060_rule
   12 |     - V-230241
   13 |     - policycoreutils
   14 |   ansible.builtin.package:
   15 |     name: policycoreutils
   16 | 
   17 | - name: "LOW | RHEL-08-010292 | PATCH | RHEL 8 must ensure the SSH server uses strong entropy."
   18 |   when:
   19 |     - rhel8stig_010292
   20 |     - rhel8stig_ssh_required
   21 |   tags:
   22 |     - RHEL-08-010292
   23 |     - CAT3
   24 |     - CCI-000366
   25 |     - NIST800-53R4_CM-6
   26 |     - SRG-OS-000480-GPOS-00227
   27 |     - SV-230253r1044799_rule
   28 |     - V-230253
   29 |     - ssh
   30 |   ansible.builtin.lineinfile:
   31 |     path: /etc/sysconfig/sshd
   32 |     regexp: (?i)^#?\s*SSH_USE_STRONG_RNG='
   33 |     line: SSH_USE_STRONG_RNG=32
   34 |   notify: Restart sshd
   35 | 
   36 | - name: "LOW | RHEL-08-010375 | PATCH | RHEL 8 must restrict access to the kernel message buffer."
   37 |   when: rhel8stig_010375
   38 |   tags:
   39 |     - RHEL-08-010375
   40 |     - CAT3
   41 |     - CCI-001090
   42 |     - NIST800-53R4_SC-4
   43 |     - SRG-OS-000138-GPOS-00069
   44 |     - SV-230269r1184255_rule
   45 |     - V-230269
   46 |     - sysctl
   47 |   block:
   48 |     - name: "LOW | RHEL-08-010375 | AUIDT | RHEL 8 must restrict access to the kernel message buffer. | Find conflicting instances"
   49 |       ansible.builtin.shell: grep -rs "kernel.dmesg_restrict = 0" /run/sysctl.d/*.conf /usr/local/lib/sysctl.d/*.conf /usr/lib/sysctl.d/*.conf /lib/sysctl.d/*.conf /etc/sysctl.conf /etc/sysctl.d/*.conf | cut -d':' -f1
   50 |       changed_when: false
   51 |       check_mode: false
   52 |       failed_when: false
   53 |       register: discovered_kernel_dmesg_settings
   54 | 
   55 |     - name: "LOW | RHEL-08-010375 | PATCH | RHEL 8 must restrict access to the kernel message buffer. | Remove conflicting instances"
   56 |       when: discovered_kernel_dmesg_settings.stdout | length > 0
   57 |       ansible.builtin.lineinfile:
   58 |         path: "{{ item }}"
   59 |         regexp: ^kernel.dmesg_restrict\s*=\s*0
   60 |         state: absent
   61 |       loop: "{{ discovered_kernel_dmesg_settings.stdout_lines }}"
   62 | 
   63 |     - name: "LOW | RHEL-08-010375 | PATCH | RHEL 8 must restrict access to the kernel message buffer."
   64 |       ansible.posix.sysctl:
   65 |         name: kernel.dmesg_restrict
   66 |         value: 1
   67 |         state: present
   68 |         reload: "{{ rhel8stig_sysctl_reload }}"
   69 |         sysctl_set: true
   70 |         sysctl_file: "{{ rhel8stig_sysctl_file }}"
   71 | 
   72 | - name: "LOW | RHEL-08-010376 | PATCH | RHEL 8 must prevent kernel profiling by unprivileged users."
   73 |   when: rhel8stig_010376
   74 |   tags:
   75 |     - RHEL-08-010376
   76 |     - CAT3
   77 |     - CCI-001090
   78 |     - NIST800-53R4_SC-4
   79 |     - SRG-OS-000138-GPOS-00069
   80 |     - SV-230270r1184258_rule
   81 |     - V-230270
   82 |     - sysctl
   83 |   block:
   84 |     - name: "LOW | RHEL-08-010376 | AUDIT | RHEL 8 must prevent kernel profiling by unprivileged users. | Find conflicting instances"
   85 |       ansible.builtin.shell: grep -rs "kernel.perf_event_paranoid = [^2]" /run/sysctl.d/*.conf /usr/local/lib/sysctl.d/*.conf /usr/lib/sysctl.d/*.conf /lib/sysctl.d/*.conf /etc/sysctl.conf /etc/sysctl.d/*.conf | cut -d':' -f1
   86 |       changed_when: false
   87 |       check_mode: false
   88 |       failed_when: false
   89 |       register: discovered_kernel_paranoid_settings
   90 | 
   91 |     - name: "LOW | RHEL-08-010376 | PATCH | RHEL 8 must prevent kernel profiling by unprivileged users. | Remove conflicting instances"
   92 |       when: discovered_kernel_paranoid_settings.stdout | length > 0
   93 |       ansible.builtin.lineinfile:
   94 |         path: "{{ item }}"
   95 |         regexp: '^kernel.perf_event_paranoid = [^2]'
   96 |         state: absent
   97 |       loop: "{{ discovered_kernel_paranoid_settings.stdout_lines }}"
   98 | 
   99 |     - name: "LOW | RHEL-08-010376 | PATCH | RHEL 8 must prevent kernel profiling by unprivileged users."
  100 |       ansible.posix.sysctl:
  101 |         name: kernel.perf_event_paranoid
  102 |         value: 2
  103 |         state: present
  104 |         reload: "{{ rhel8stig_sysctl_reload }}"
  105 |         sysctl_set: true
  106 |         sysctl_file: "{{ rhel8stig_sysctl_file }}"
  107 | 
  108 | - name: "LOW | RHEL-08-010440 | PATCH | YUM must remove all software components after updated versions have been installed on RHEL 8."
  109 |   when: rhel8stig_010440
  110 |   tags:
  111 |     - RHEL-08-010440
  112 |     - CAT3
  113 |     - CCI-002617
  114 |     - NIST800-53R4_SI-2
  115 |     - SRG-OS-000437-GPOS-00194
  116 |     - SV-230281r958936_rule
  117 |     - V-230281
  118 |   block:
  119 |     - name: "LOW | RHEL-08-010440 | PATCH | YUM must remove all software components after updated versions have been installed on RHEL 8. | Find .conf files"
  120 |       ansible.builtin.find:
  121 |         paths: /etc
  122 |         recurse: true
  123 |         file_type: any
  124 |         depth: 2
  125 |         patterns:
  126 |           - yum.conf
  127 |           - dnf.conf
  128 |       register: discovered_pkg_mgr_settings
  129 | 
  130 |     - name: "LOW | RHEL-08-010440 | PATCH | YUM must remove all software components after updated versions have been installed on RHEL 8. | Set settings"
  131 |       ansible.builtin.lineinfile:
  132 |         path: "{{ item.path }}"
  133 |         regexp: '^.*clean_requirements_on_remove'
  134 |         line: 'clean_requirements_on_remove=True'
  135 |       loop: "{{ discovered_pkg_mgr_settings.files }}"
  136 |       loop_control:
  137 |         label: "{{ item.path }}"
  138 | 
  139 | - name: |
  140 |     "LOW | RHEL-08-010471 | PATCH | RHEL 8 must enable the hardware random number generator entropy gatherer service.
  141 |      LOW | RHEL-08-010472 | PATCH | RHEL 8 must have the packages required to use the hardware random number generator entropy gatherer service"
  142 |   when:
  143 |     - rhel8stig_010471 or
  144 |       rhel8stig_010472
  145 |     - (not rhel8stig_010020)
  146 |       or ansible_fips  # Can't enable if FIPS
  147 |   tags:
  148 |     - RHEL-08-010471
  149 |     - RHEL-08-010472
  150 |     - CAT3
  151 |     - CCI-000366
  152 |     - NIST800-53R4_CM-6
  153 |     - SRG-OS-000480-GPOS-00227
  154 |     - SV-230285r1017096_rule
  155 |     - SV-244527r1017333_rule
  156 |     - V-230285
  157 |     - V-244527
  158 |   block:
  159 |     - name: "LOW | RHEL-08-010472 | PATCH | RHEL 8 must have the packages required to use the hardware random number generator entropy gatherer service"
  160 |       ansible.builtin.package:
  161 |         name: rng-tools
  162 |         state: present
  163 | 
  164 |     - name: "LOW | RHEL-08-010471 | PATCH | RHEL 8 must enable the hardware random number generator entropy gatherer service."
  165 |       ansible.builtin.systemd:
  166 |         name: rngd.service
  167 |         enabled: true
  168 |       notify: Restart rngd
  169 | 
  170 | - name: "LOW | RHEL-08-010540 | AUDIT | The RHEL 8 must use a separate file system for /var."
  171 |   when:
  172 |     - rhel8stig_010540
  173 |     - ansible_mounts | selectattr('mount', 'match', '^/var$') | list | length == 0
  174 |   tags:
  175 |     - RHEL-08-010540
  176 |     - CAT3
  177 |     - CCI-000366
  178 |     - NIST800-53R4_CM-6
  179 |     - SRG-OS-000480-GPOS-00227
  180 |     - SV-230292r1017103_rule
  181 |     - V-230292
  182 |     - complexity-high
  183 |     - mounts
  184 |     - var
  185 |   vars:
  186 |     warn_control_id: "LOW | RHEL-08-010540"
  187 |   block:
  188 |     - name: "LOW | RHEL-08-010540 | AUDIT | The RHEL 8 must use a separate file system for /var."
  189 |       ansible.builtin.debug:
  190 |         msg: "Warning!! /var is not mounted on a separate partition"
  191 | 
  192 |     - name: "LOW | RHEL-08-010540 | AUDIT | The RHEL 8 must use a separate file system for /var."
  193 |       ansible.builtin.import_tasks:
  194 |         file: warning_facts.yml
  195 | 
  196 | - name: "LOW | RHEL-08-010541 | AUDIT | RHEL 8 must use a separate file system for /var/log."
  197 |   when:
  198 |     - rhel8stig_010541
  199 |     - ansible_mounts | selectattr('mount', 'match', '^/var/log$') | list | length == 0
  200 |   tags:
  201 |     - RHEL-08-010541
  202 |     - CAT3
  203 |     - CCI-000366
  204 |     - NIST800-53R4_CM-6
  205 |     - SRG-OS-000480-GPOS-00227
  206 |     - SV-230293r1017104_rule
  207 |     - V-230293
  208 |     - complexity_high
  209 |     - mounts
  210 |   vars:
  211 |     warn_control_id: "LOW | RHEL-08-010541"
  212 |   block:
  213 |     - name: "LOW | RHEL-08-010541 | AUDIT | RHEL 8 must use a separate file system for /var/log."
  214 |       ansible.builtin.debug:
  215 |         msg: "Warning!! /var/log is not mounted on a separate partition"
  216 | 
  217 |     - name: "LOW | RHEL-08-010541 | AUDIT | RHEL 8 must use a separate file system for /var/log."
  218 |       ansible.builtin.import_tasks:
  219 |         file: warning_facts.yml
  220 | 
  221 | - name: "LOW | RHEL-08-010542 | AUDIT | The RHEL 8 must use a separate file system for the system audit data path."
  222 |   when:
  223 |     - rhel8stig_010542
  224 |     - ansible_mounts | selectattr('mount', 'match', '^/var/log/audit$') | list | length == 0
  225 |   tags:
  226 |     - RHEL-08-010542
  227 |     - CAT3
  228 |     - CCI-000366
  229 |     - NIST800-53R4_CM-6
  230 |     - SRG-OS-000480-GPOS-00227
  231 |     - SV-230294r1017105_rule
  232 |     - V-230294
  233 |     - complexity_high
  234 |     - mounts
  235 |     - auditd
  236 |   vars:
  237 |     warn_control_id: "LOW | RHEL-08-010542"
  238 |   block:
  239 |     - name: "LOW | RHEL-08-010542 | AUDIT | The RHEL 8 must use a separate file system for the system audit data path."
  240 |       ansible.builtin.debug:
  241 |         msg: "Warning!! /var/log/audit is not mounted on a separate partition"
  242 | 
  243 |     - name: "LOW | RHEL-08-010542 | AUDIT | The RHEL 8 must use a separate file system for the system audit data path."
  244 |       ansible.builtin.import_tasks:
  245 |         file: warning_facts.yml
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `.`; 72 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: yes

.ansible-lint
.gitattributes
.github/workflows/add_repo_issue_to_gh_project.yml
.github/workflows/benchmark_tracking_controller.yml
.github/workflows/devel_pipeline_validation.yml
.github/workflows/export_badges_private.yml
.github/workflows/export_badges_public.yml
.github/workflows/main_pipeline_validation.yml
.github/workflows/molecule.yml
.github/workflows/repo_qa.yml
.gitignore
.pre-commit-config.yaml
.qa_baseline.json
.yamllint
CONTRIBUTING.rst
Changelog.md
LICENSE
Makefile
README.md
ansible.cfg
collections/requirements.yml
defaults/main.yml
handlers/main.yml
meta/main.yml
molecule/default/README_Molecule+Ansible216.md
molecule/default/converge.yml
molecule/default/molecule.yml
molecule/default/prepare.yml
molecule/default/verify.yml
requirements.txt
rules/tag.py
site.yml
tasks/Cat_1/RHEL-08-010xxx.yml
tasks/Cat_1/RHEL-08-020xxx.yml
tasks/Cat_1/RHEL-08-040xxx.yml
tasks/Cat_1/main.yml
tasks/Cat_2/RHEL-08-010xxx.yml
tasks/Cat_2/RHEL-08-020xxx.yml
tasks/Cat_2/RHEL-08-030xxx.yml
tasks/Cat_2/RHEL-08-040xxx.yml
tasks/Cat_2/main.yml
tasks/Cat_3/RHEL-08-010xxx.yml
tasks/Cat_3/RHEL-08-020xxx.yml
tasks/Cat_3/RHEL-08-030xxx.yml
tasks/Cat_3/RHEL-08-040xxx.yml
tasks/Cat_3/main.yml
tasks/LE_audit_setup.yml
tasks/audit_only.yml
tasks/fetch_audit_output.yml
tasks/main.yml
tasks/parse_etc_passwd.yml
tasks/post_remediation_audit.yml
tasks/pre_remediation_audit.yml
tasks/prelim.yml
tasks/warning_facts.yml
templates/01_users.j2
templates/aide.conf.j2
templates/ansible_vars_goss.yml.j2
templates/audit/99_auditd.rules.j2
templates/etc/ansible/compliance_facts.j2
templates/etc/crypto-policies/policies/modules/STIG.pmod.j2
templates/etc/systemd/system.conf.d/55-CtrlAltDel-BurstAction.j2
templates/resolv.conf.j2
test_plugins/rhel8_stig_ansible_backport.py
test_plugins/rhel8_stig_jinja_compat.py
vars/AlmaLinux.yml
vars/OracleLinux.yml
vars/RedHat.yml
vars/Rocky.yml
vars/audit.yml
vars/is_container.yml
vars/main.yml
```

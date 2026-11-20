# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-037

- Repository: `ansible-lockdown/RHEL8-STIG`
- Commit: `baa075468dfa59050141c99d99dcacd2e977248c`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `3c7be78120720dc5a5547e932991fbb5738a2c426c782e58d4aa0fc425d5da48`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–199 of 199:

```text
    1 | ---
    2 | 
    3 | - name: Check OS version and family
    4 |   when: not skip_os_check
    5 |   tags: always
    6 |   ansible.builtin.assert:
    7 |     that: (ansible_facts.distribution != 'CentOS' and ansible_facts.os_family == 'RedHat' or ansible_facts.os_family == "Rocky") and ansible_facts.distribution_major_version is version_compare('8', '==')
    8 |     fail_msg: "This role can only be run against RHEL/Rocky 8. {{ ansible_facts.distribution }} {{ ansible_facts.distribution_major_version }} is not supported."
    9 |     success_msg: "This role is running against a supported OS {{ ansible_facts.distribution }} {{ ansible_facts.distribution_major_version }}"
   10 | 
   11 | - name: Check ansible version
   12 |   tags: always
   13 |   ansible.builtin.assert:
   14 |     that: ansible_version.full is version_compare(rhel8stig_min_ansible_version, '>=')
   15 |     fail_msg: "You must use Ansible {{ rhel8stig_min_ansible_version }} or greater"
   16 |     success_msg: "This role is running a supported version of ansible {{ ansible_version.full }} >= {{ rhel8stig_min_ansible_version }}"
   17 | 
   18 | - name: Setup rules if container
   19 |   when:
   20 |     - ansible_connection == 'docker' or
   21 |       ansible_facts.virtualization_type in ["docker", "lxc", "openvz", "podman", "container"]
   22 |   tags: always
   23 |   block:
   24 |     - name: Discover and set container variable if required
   25 |       ansible.builtin.set_fact:
   26 |         system_is_container: true
   27 | 
   28 |     - name: Load variable for container
   29 |       ansible.builtin.include_vars:
   30 |         file: "{{ container_vars_file }}"
   31 | 
   32 |     - name: Output if discovered is a container
   33 |       ansible.builtin.debug:
   34 |         msg: system has been discovered as a container
   35 |       when: system_is_container
   36 | 
   37 | - name: "Check password set for connecting user"
   38 |   when:
   39 |     - rhel8stig_010380
   40 |     - ansible_env.SUDO_USER is defined
   41 |     - not system_is_ec2
   42 |   tags: always
   43 |   block:
   44 |     - name: Capture current password state of connecting user"
   45 |       ansible.builtin.shell: "grep {{ ansible_env.SUDO_USER }} /etc/shadow | awk -F: '{print $2}'"
   46 |       changed_when: false
   47 |       failed_when: false
   48 |       check_mode: false
   49 |       no_log: true
   50 |       register: discovered_user_password_set
   51 | 
   52 |     - name: "Assert that password set for {{ ansible_env.SUDO_USER }} and account not locked"  # noqa: name[template]
   53 |       ansible.builtin.assert:
   54 |         that: discovered_user_password_set.stdout | length != 0 and discovered_user_password_set.stdout != "!!"
   55 |         fail_msg: "You have {{ sudo_password_rule }} enabled but the user = {{ ansible_env.SUDO_USER }} has no password set - It can break access"
   56 |         success_msg: "You have a password set for the {{ ansible_env.SUDO_USER }}"
   57 |       vars:
   58 |         sudo_password_rule: [REDACTED_LITERAL]
   59 | 
   60 | - name: "Ensure superuser for grub does not match existing user"
   61 |   when: rhel8stig_010141 or rhel8stig_010149
   62 |   tags: always
   63 |   block:
   64 |     - name: "Ensure superuser for grub does not match existing user | capture users"
   65 |       ansible.builtin.shell: cat /etc/passwd | cut -d':' -f1
   66 |       changed_when: false
   67 |       failed_when: false
   68 |       check_mode: false
   69 |       register: discovered_user_list
   70 | 
   71 |     - name: "Ensure superuser for grub does not match existing user"
   72 |       ansible.builtin.assert:
   73 |         that: rhel8stig_boot_superuser not in discovered_user_list.stdout_lines
   74 |         fail_msg: "A unique name must be used for bootloader access user='{{ rhel8stig_boot_superuser }}' already exists refer to variable rhel8stig_boot_superuser"
   75 | 
   76 | - name: Include OS specific variables
   77 |   tags: always
   78 |   ansible.builtin.include_vars:
   79 |     file: "{{ ansible_facts.distribution }}.yml"
   80 | 
   81 | - name: Check rhel8stig_bootloader_password_hash variable has been changed
   82 |   when:
   83 |     - not system_is_ec2
   84 |     - not system_is_container
   85 |     - rhel8stig_010140 or
   86 |       rhel8stig_010150
   87 |   tags: always
   88 |   ansible.builtin.assert:
   89 |     that: rhel8stig_bootloader_password_hash != 'grub.pbkdf2.sha512.changethispassword'  # pragma: allowlist secret
   90 |     msg: "This role will not be able to run single user password commands as rhel8stig_bootloader_password_hash variable has not been set"  # pragma: allowlist secret
   91 | 
   92 | - name: Check if using resolv.conf template settings are changed
   93 |   when:
   94 |     - rhel8stig_use_resolv_template
   95 |     - rhel8stig_010680
   96 |   tags: always
   97 |   ansible.builtin.assert:
   98 |     that:
   99 |       - rhel8stig_resolv_domain != 'example.com'
  100 |       - rhel8stig_resolv_search | length > 0
  101 |     msg: "WARNING!! You are set to change your resolv.conf file this can be very disruptive if not configured correctly"
  102 | 
  103 | - name: Gather the package facts
  104 |   tags: always
  105 |   ansible.builtin.package_facts:
  106 |     manager: auto
  107 | 
  108 | - name: Include prelim tasks
  109 |   tags: always
  110 |   ansible.builtin.import_tasks:
  111 |     file: prelim.yml
  112 | 
  113 | - name: Include CAT I patches
  114 |   when: rhel8stig_cat1
  115 |   tags:
  116 |     - rhel8stig_cat1
  117 |     - high
  118 |   ansible.builtin.import_tasks:
  119 |     file: Cat_1/main.yml
  120 | 
  121 | - name: Include CAT II patches
  122 |   when: rhel8stig_cat2
  123 |   tags:
  124 |     - rhel8stig_cat2
  125 |     - medium
  126 |   ansible.builtin.import_tasks:
  127 |     file: Cat_2/main.yml
  128 | 
  129 | - name: Include CAT III patches
  130 |   when: rhel8stig_cat3
  131 |   tags:
  132 |     - rhel8stig_cat3
  133 |     - low
  134 |   ansible.builtin.import_tasks:
  135 |     file: Cat_3/main.yml
  136 | 
  137 | - name: Flush handlers
  138 |   ansible.builtin.meta: flush_handlers
  139 | 
  140 | - name: Reboot system
  141 |   when:
  142 |     - change_requires_reboot
  143 |     - not system_is_container
  144 |   block:
  145 |     - name: Reboot system if not skipped
  146 |       when: not rhel8stig_skip_reboot
  147 |       ansible.builtin.reboot:
  148 | 
  149 |     - name: Warning a reboot required but skip option set
  150 |       when: rhel8stig_skip_reboot
  151 |       ansible.builtin.debug:
  152 |         msg: "Warning!! changes have been made that require a reboot to be implemented but skip reboot was set - Can affect compliance check results"
  153 |       changed_when: true
  154 | 
  155 | - name: Run post remediation audit
  156 |   when: run_audit
  157 |   tags: always
  158 |   ansible.builtin.import_tasks:
  159 |     file: post_remediation_audit.yml
  160 | 
  161 | - name: Add ansible file showing Benchmark and levels applied
  162 |   when: create_benchmark_facts
  163 |   tags: always
  164 |   block:
  165 |     - name: Create ansible facts directory
  166 |       ansible.builtin.file:
  167 |         path: "{{ ansible_facts_path }}"
  168 |         state: directory
  169 |         owner: root
  170 |         group: root
  171 |         mode: 'u=rwx,go=rx'
  172 | 
  173 |     - name: Create ansible facts file
  174 |       ansible.builtin.template:
  175 |         src: etc/ansible/compliance_facts.j2
  176 |         dest: "{{ ansible_facts_path }}/compliance_facts.fact"
  177 |         owner: root
  178 |         group: root
  179 |         mode: 'u-x,go-wx'
  180 | 
  181 | - name: Fetch audit files
  182 |   when:
  183 |     - fetch_audit_output
  184 |     - run_audit
  185 |   tags: always
  186 |   ansible.builtin.import_tasks:
  187 |     file: fetch_audit_output.yml
  188 | 
  189 | - name: Show Audit Summary
  190 |   when: run_audit
  191 |   tags: run_audit
  192 |   ansible.builtin.debug:
  193 |     msg: "{{ audit_results.split('\n') }}"
  194 | 
  195 | - name: If Warnings found Output count and control IDs affected
  196 |   when: warn_count != 0
  197 |   tags: always
  198 |   ansible.builtin.debug:
  199 |     msg: You have {{ warn_count }} Warning(s) that require investigating that are related to the following benchmark ID(s) {{ warn_control_list }}
```

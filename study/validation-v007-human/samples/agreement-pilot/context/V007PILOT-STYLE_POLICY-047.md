# Frozen source context: V007PILOT-STYLE_POLICY-047

- Repository: `ComplianceAsCode/content`
- Commit: `30d390c4b0d1f842a87a16d953c584e213cef4d5`
- Family: Style/policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `linux_os/guide/system/permissions/restrictions/sysctl_kernel_core_pattern_empty_string/ansible/shared.yml` (reported anchor line 30)
- Object: `task` `2c32e2911868fab80547b8c4c64887f2cb0ab518a7affc64ea971486852d6643`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–52 of 52:

```text
    1 | # platform = multi_platform_all
    2 | # reboot = true
    3 | # strategy = disable
    4 | # complexity = low
    5 | # disruption = medium
    6 | 
    7 | - name: "{{{ rule_title }}} - Set fact for sysctl paths"
    8 |   ansible.builtin.set_fact:
    9 |     sysctl_paths:
   10 |       - "/etc/sysctl.d/"
   11 |       - "/run/sysctl.d/"
   12 |       - "/usr/local/lib/sysctl.d/"
   13 | 
   14 | - name: "{{{ rule_title }}} - Find all files that contain kernel.core_pattern"
   15 |   ansible.builtin.shell:
   16 |     cmd: find -L {{ sysctl_paths | join(" ") }} -type f -name '*.conf' | xargs grep -HP '^\s*kernel.core_pattern\s*=\s*.*$'
   17 |   register: find_all_values
   18 |   check_mode: false
   19 |   changed_when: false
   20 |   failed_when: false
   21 | 
   22 | - name: "{{{ rule_title }}} - Find all files that set kernel.core_pattern to correct value"
   23 |   ansible.builtin.shell:
   24 |     cmd: find -L {{ sysctl_paths | join(" ") }} -type f -name '*.conf' | xargs grep -HP '^\s*kernel.core_pattern\s*=\s*$'
   25 |   register: find_correct_value
   26 |   check_mode: false
   27 |   changed_when: false
   28 |   failed_when: false
   29 | 
   30 | - name: "{{{ rule_title }}} - Comment out any occurrences of kernel.core_pattern from config files"
   31 |   ansible.builtin.replace:
   32 |     path: '{{ item | split(":") | first }}'
   33 |     regexp: '^[\s]*kernel.core_pattern'
   34 |     replace: '#kernel.core_pattern'
   35 |   loop: '{{ find_all_values.stdout_lines }}'
   36 |   when: find_correct_value.stdout_lines | length == 0 or find_all_values.stdout_lines | length > find_correct_value.stdout_lines | length
   37 | 
   38 | - name: "{{{ rule_title }}} - Comment out any occurrences of kernel.core_pattern from /etc/sysctl.conf"
   39 |   ansible.builtin.replace:
   40 |     path: "{{ item }}"
   41 |     regexp: '^[\s]*kernel.core_pattern'
   42 |     replace: '#kernel.core_pattern'
   43 |   with_fileglob:
   44 |     - "/etc/sysctl.conf"
   45 | 
   46 | - name: "{{{ rule_title }}} - Ensure sysctl kernel.core_pattern is set to empty"
   47 |   ansible.posix.sysctl:
   48 |     name: "kernel.core_pattern"
   49 |     value: ' '  # ansible sysctl module doesn't allow empty string, a space string is allowed and has the same semantics as sysctl will ignore spaces
   50 |     sysctl_file: "/etc/sysctl.d/kernel_core_pattern.conf"
   51 |     state: present
   52 |     reload: yes
```

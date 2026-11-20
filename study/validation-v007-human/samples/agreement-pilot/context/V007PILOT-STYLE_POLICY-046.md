# Frozen source context: V007PILOT-STYLE_POLICY-046

- Repository: `ansible-lockdown/RHEL7-STIG`
- Commit: `a3d78cfc5c2cae8f8b344fbcd6664a35817dbad0`
- Family: Style/policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `tasks/fix-cat2.yml` (reported anchor line 845)
- Object: `source_location` `f8b5acdffedf21e87f1a0c9f2678789cb9e197734e11caec24027dccb9369f95`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 810–880 of 4812:

```text
  810 |             state: updated
  811 |             type: auth
  812 |             control: required
  813 |             module_path: pam_faillock.so
  814 |             module_arguments: "preauth silent audit deny={{ rhel7stig_pam_faillock.attempts }}{{ (rhel7stig_pam_faillock.fail_for_root) | ternary(' even_deny_root ',' ') }}fail_interval={{ rhel7stig_pam_faillock.interval }} unlock_time={{ rhel7stig_pam_faillock.unlock_time }}"
  815 |         with_items:
  816 |             - "system-auth"
  817 |             - "password-auth"
  818 | 
  819 |       - name: "MEDIUM | RHEL-07-010330 | PATCH | The Red Hat Enterprise Linux operating system must lock the associated account after three unsuccessful root logon attempts are made within a 15-minute period."
  820 |         community.general.pamd:
  821 |             name: "{{ item }}"
  822 |             state: before
  823 |             type: auth
  824 |             control: required
  825 |             module_path: pam_deny.so
  826 |             new_type: auth
  827 |             new_control: "[default=die]"
  828 |             new_module_path: pam_faillock.so
  829 |         with_items:
  830 |             - "system-auth"
  831 |             - "password-auth"
  832 | 
  833 |       # TODO: Remove temporary audit check to determine if the following pamd module task needs to be run since the module is not idempotent
  834 |       # - name: "MEDIUM | RHEL-07-010330 | AUDIT | Check for existing account lockout settings"
  835 |       #  ansible.builtin.shell: "grep -iE '^auth\\s+\\[default=die\\]\\s+pam_faillock.so\\s+authfail\\s+audit\\s+deny={{ rhel7stig_pam_faillock.attempts }}{{ (rhel7stig_pam_faillock.fail_for_root) | ternary(' even_deny_root ',' ') }}fail_interval={{ rhel7stig_pam_faillock.interval }}\\s+unlock_time={{ rhel7stig_pam_faillock.unlock_time }}$' /etc/pam.d/{{ item }}"
  836 |       #  check_mode: no
  837 |       #  changed_when: no
  838 |       #  failed_when: rhel_07_010330_authfail_audit.rc > 1
  839 |       #  register: rhel_07_010330_authfail_audit
  840 |       #  with_items:
  841 |       #  - "system-auth"
  842 |       #  - "password-auth"
  843 | 
  844 |       # TODO: Once the pamd module is fixed (either args_present or updated) then remove the previous grep task and update the following.
  845 |       - name: "MEDIUM | RHEL-07-010330 | PATCH | The Red Hat Enterprise Linux operating system must lock the associated account after three unsuccessful root logon attempts are made within a 15-minute period."
  846 |         community.general.pamd:
  847 |             name: "{{ item }}"
  848 |             state: updated
  849 |             type: auth
  850 |             control: "[default=die]"
  851 |             module_path: pam_faillock.so
  852 |             module_arguments: "authfail audit deny={{ rhel7stig_pam_faillock.attempts }}{{ (rhel7stig_pam_faillock.fail_for_root) | ternary(' even_deny_root ',' ') }}fail_interval={{ rhel7stig_pam_faillock.interval }} unlock_time={{ rhel7stig_pam_faillock.unlock_time }}"
  853 |         with_items:
  854 |             - "system-auth"
  855 |             - "password-auth"
  856 |       # when: item.rc == 1
  857 | 
  858 |       - name: "MEDIUM | RHEL-07-010330 | PATCH | The Red Hat Enterprise Linux operating system must lock the associated account after three unsuccessful root logon attempts are made within a 15-minute period."
  859 |         community.general.pamd:
  860 |             name: "{{ item }}"
  861 |             state: before
  862 |             type: account
  863 |             control: required
  864 |             module_path: pam_unix.so
  865 |             new_type: account
  866 |             new_control: required
  867 |             new_module_path: pam_faillock.so
  868 |         with_items:
  869 |             - "system-auth"
  870 |             - "password-auth"
  871 |   when:
  872 |       - not rhel_07_010199  # 010199 uses template that is compliant already
  873 |       - rhel_07_010320 or
  874 |         rhel_07_010330
  875 |   tags:
  876 |       - CAT2
  877 |       - RHEL-07-010320
  878 |       - CCI-000044
  879 |       - CCI-002236
  880 |       - CCI-002237
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

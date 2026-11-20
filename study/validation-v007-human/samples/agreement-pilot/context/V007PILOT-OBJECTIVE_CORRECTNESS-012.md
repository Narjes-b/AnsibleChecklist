# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-012

- Repository: `ComplianceAsCode/content`
- Commit: `30d390c4b0d1f842a87a16d953c584e213cef4d5`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `linux_os/guide/system/permissions/partitions/mount_option_tmp_noexec/ansible/slmicro5.yml` (reported anchor line 24)
- Object: `source_location` `81c4c3e61d57bcf1fc6c3d8d74d964501050013c95b750c9ea87a96eb9623205`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–28 of 28:

```text
    1 | # platform = multi_platform_slmicro
    2 | # reboot = true
    3 | # strategy = configure
    4 | # complexity = low
    5 | # disruption = low
    6 | 
    7 | - name: '{{{ rule_title }}} - Check if noexec options is configured in /usr/lib/systemd/system/tmp.mount'
    8 |   ansible.builtin.lineinfile:
    9 |     path: /usr/lib/systemd/system/tmp.mount
   10 |     regexp: ^[\s]*Options=[\s]*.*noexec.*$
   11 |     state: absent
   12 |   check_mode: true
   13 |   register: noexec_match
   14 | 
   15 | # if no match, collect current options and add noexec
   16 | - name: '{{{ rule_title }}} - Collect previously configured options'
   17 |   ansible.builtin.shell:
   18 |     cmd: sed -n 's/^[\s]*Options=[\s]*\(.*\)$/\1/p' /usr/lib/systemd/system/tmp.mount
   19 |   register: current_options
   20 |   when:
   21 |     - noexec_match is defined and noexec_match.found == 0
   22 | 
   23 | 
   24 | - name: '{{{ rule_title }}} - Add noexec option to previously configured options'
   25 |   ansible.builtin.shell:
   26 |     cmd: sed -i "s/^Options=.*/Options={{ current_options.stdout }},noexec/g" /usr/lib/systemd/system/tmp.mount
   27 |   when:
   28 |     - noexec_match.found == 0 and current_options is defined
```

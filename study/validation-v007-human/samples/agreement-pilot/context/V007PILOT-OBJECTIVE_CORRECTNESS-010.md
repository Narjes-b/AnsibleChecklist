# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-010

- Repository: `ansible-lockdown/RHEL7-STIG`
- Commit: `a3d78cfc5c2cae8f8b344fbcd6664a35817dbad0`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `tasks/fix-cat2.yml` (reported anchor line 1720)
- Object: `source_location` `842e4cc888d030cd8f25f152240ec03d5c5588e2e1d500a37449303557a8a669`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1685–1755 of 4812:

```text
 1685 |         with_items:
 1686 |             - "{{ rhel_07_all_gid_audit.results }}"
 1687 |         loop_control:
 1688 |             label: "{{ rhel7stig_passwd_label }}"
 1689 |         when: this_item.uid >= rhel7stig_int_gid
 1690 |         vars:
 1691 |             this_item: "{{ item.item }}"
 1692 |             this_result: "{{ item }}"
 1693 | 
 1694 |       - name: "MEDIUM | RHEL-07-020670 | PATCH | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories are group-owned by a group of which the home directory owner is a member."
 1695 |         ansible.builtin.shell: "{{ find_command_base }} -exec chgrp {{ this_item.gid }} {} +"
 1696 |         with_items: "{{ rhel_07_020670_audit.results }}"
 1697 |         loop_control:
 1698 |             label: "{{ rhel7stig_passwd_label }}"
 1699 |         when: item is changed  # noqa: no-handler
 1700 |         vars:
 1701 |             this_item: "{{ item.item.item }}"
 1702 |             this_result: "{{ item.item }}"
 1703 |   vars:
 1704 |       find_command_base: 'find "{{ this_item.dir }}" -mindepth 1
 1705 |               -path "{{ this_item.dir }}/.*" -not -path "{{ this_item.dir }}/.*/*" -type f -o
 1706 |               -not -group {{ this_result.stdout.split(" ") | join(" -not -group ") }}'
 1707 |   when:
 1708 |       - rhel_07_020670
 1709 |   tags:
 1710 |       - RHEL-07-020670
 1711 |       - CAT2
 1712 |       - CCI-000366
 1713 |       - SRG-OS-000480-GPOS-00227
 1714 |       - SV-204472r991589_rule
 1715 |       - V-204472
 1716 |       - users
 1717 | 
 1718 | - name: "MEDIUM | RHEL-07-020680 | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories have a mode of 0750 or less permissive."
 1719 |   block:
 1720 |       - name: "MEDIUM | RHEL-07-020680 | AUDIT | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories have a mode of 0750 or less permissive."
 1721 |         ansible.builtin.stat:
 1722 |             path: "{{ item }}"
 1723 |         with_items: "{{ rhel7stig_passwd | selectattr('uid', '>=', rhel7stig_interactive_uid_start | int ) | selectattr('uid', '!=', 65534) | map(attribute='dir') | list }}"
 1724 |         register: rhel_07_020680_audit
 1725 | 
 1726 |       - name: "MEDIUM | RHEL-07-020680 | AUDIT | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories have a mode of 0750 or less permissive."
 1727 |         ansible.builtin.shell: find -H {{ item.0 | quote }} -not -type l -perm /027
 1728 |         changed_when: rhel_07_020680_patch_audit.stdout| length > 0
 1729 |         check_mode: false
 1730 |         register: rhel_07_020680_patch_audit
 1731 |         with_together:
 1732 |             - "{{ rhel_07_020680_audit.results | map(attribute='item') | list }}"
 1733 |             - "{{ rhel_07_020680_audit.results | map(attribute='stat') | list }}"
 1734 |         loop_control:
 1735 |             label: "{{ item.0 }}"
 1736 |         when:
 1737 |             - ansible_check_mode
 1738 |             - item.1.exists
 1739 | 
 1740 |       - name: "MEDIUM | RHEL-07-020680 | PATCH | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories have a mode of 0750 or less permissive."
 1741 |         ansible.builtin.file:
 1742 |             path: "{{ item.0 }}"
 1743 |             recurse: true
 1744 |             mode: a-st,g-w,o-rwx
 1745 |         register: rhel_07_020680_patch
 1746 |         with_together:
 1747 |             - "{{ rhel_07_020680_audit.results | map(attribute='item') | list }}"
 1748 |             - "{{ rhel_07_020680_audit.results | map(attribute='stat') | list }}"
 1749 |         loop_control:
 1750 |             label: "{{ item.0 }}"
 1751 |         when:
 1752 |             - not ansible_check_mode
 1753 |             - item.1.exists
 1754 | 
 1755 |       # set default ACLs so the homedir has an effective umask of 0027
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

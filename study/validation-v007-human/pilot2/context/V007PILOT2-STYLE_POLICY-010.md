# Frozen source context: V007PILOT2-STYLE_POLICY-010

- Repository: `ansible-lockdown/RHEL7-STIG`
- Commit: `a3d78cfc5c2cae8f8b344fbcd6664a35817dbad0`
- Family: style_policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `tasks/fix-cat2.yml` (reported anchor line 1756)
- Flagged construct: task `medium | rhel-07-020680 | patch | the red hat enterprise linux operating system must be configured so that all files and directories contained in local interactive user home directories have a mode of 0750 or less permissive.`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1656–1856 of 4812:

```text
 1656 |             -not -user {{ this_item.uid }}'
 1657 |   when:
 1658 |       - rhel_07_020660
 1659 |   tags:
 1660 |       - RHEL-07-020660
 1661 |       - CAT2
 1662 |       - CCI-000366
 1663 |       - SRG-OS-000480-GPOS-00227
 1664 |       - SV-204471r991589_rule
 1665 |       - V-204471
 1666 |       - users
 1667 | 
 1668 | - name: "MEDIUM | RHEL-07-020670 | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories are group-owned by a group of which the home directory owner is a member."
 1669 |   block:
 1670 |       - name: "MEDIUM | RHEL-07-020670 | AUDIT | Get all GIDs for each user."
 1671 |         ansible.builtin.shell: id -G "{{ item.id }}"
 1672 |         changed_when: false
 1673 |         check_mode: false
 1674 |         register: rhel_07_all_gid_audit
 1675 |         with_items:
 1676 |             - "{{ rhel7stig_passwd }}"
 1677 |         loop_control:
 1678 |             label: "{{ rhel7stig_passwd_label }}"
 1679 | 
 1680 |       - name: "MEDIUM | RHEL-07-020670 | AUDIT | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories are group-owned by a group of which the home directory owner is a member."
 1681 |         ansible.builtin.shell: "{{ find_command_base }} -print -quit"
 1682 |         changed_when: rhel_07_020670_audit.stdout| length > 0
 1683 |         check_mode: false
 1684 |         register: rhel_07_020670_audit
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
 1756 |       - name: "MEDIUM | RHEL-07-020680 | PATCH | The Red Hat Enterprise Linux operating system must be configured so that all files and directories contained in local interactive user home directories have a mode of 0750 or less permissive."
 1757 |         ansible.posix.acl:
 1758 |             path: "{{ item.0 }}"
 1759 |             default: true
 1760 |             state: present
 1761 |             recursive: true
 1762 |             etype: "{{ item.1.etype }}"
 1763 |             permissions: "{{ item.1.mode }}"
 1764 |         with_nested:
 1765 |             - "{{ (ansible_check_mode | ternary(rhel_07_020680_patch_audit, rhel_07_020680_patch)).results |
 1766 |               rejectattr('skipped', 'defined') | map(attribute='item') | map('first') | list }}"
 1767 |             -
 1768 |                 - etype: group
 1769 |                   mode: rx
 1770 |                 - etype: other
 1771 |                   mode: '0'
 1772 |         when: not rhel7stig_system_is_container
 1773 |   when:
 1774 |       - rhel_07_020680
 1775 |   tags:
 1776 |       - RHEL-07-020680
 1777 |       - CAT2
 1778 |       - CCI-000366
 1779 |       - SRG-OS-000480-GPOS-00227
 1780 |       - SV-204473r991589_rule
 1781 |       - V-204473
 1782 |       - permissions
 1783 | 
 1784 | - name: "MEDIUM | RHEL-07-020690 | The Red Hat Enterprise Linux operating system must be configured so that all local initialization files for interactive users are owned by the home directory user or root."
 1785 |   block:
 1786 |       - name: "MEDIUM | RHEL-07-020690 | AUDIT | The Red Hat Enterprise Linux operating system must be configured so that all local initialization files for interactive users are owned by the home directory user or root."
 1787 |         ansible.builtin.shell: "{{ find_command_base }} -print -quit"
 1788 |         changed_when: rhel_07_020690_audit.stdout | length > 0
 1789 |         check_mode: false
 1790 |         register: rhel_07_020690_audit
 1791 |         with_items:
 1792 |             - "{{ rhel7stig_passwd }}"
 1793 |         loop_control:
 1794 |             label: "{{ rhel7stig_passwd_label }}"
 1795 |         when: rhel7stig_interactive_uid_start | int <= this_item.uid
 1796 |         vars:
 1797 |             this_item: "{{ item }}"
 1798 | 
 1799 |       - name: "MEDIUM | RHEL-07-020690 | PATCH | The Red Hat Enterprise Linux operating system must be configured so that all local initialization files for interactive users are owned by the home directory user or root."
 1800 |         ansible.builtin.shell: "{{ find_command_base }} -exec chown {{ this_item.uid }} {} +"
 1801 |         with_items: "{{ rhel_07_020690_audit.results }}"
 1802 |         loop_control:
 1803 |             label: "{{ rhel7stig_passwd_label }}"
 1804 |         when: item is changed  # noqa: no-handler
 1805 |         vars:
 1806 |             this_item: "{{ item.item }}"
 1807 |   vars:
 1808 |       find_command_base: 'find "{{ this_item.dir }}" -mindepth 1 -type f
 1809 |               -path "{{ this_item.dir }}/.*" -not -path "{{ this_item.dir }}/.*/*"
 1810 |               -not -user {{ this_item.uid }} -o -user root'
 1811 |   when:
 1812 |       - rhel_07_020690
 1813 |   tags:
 1814 |       - RHEL-07-020690
 1815 |       - CAT2
 1816 |       - CCI-000366
 1817 |       - SRG-OS-000480-GPOS-00227
 1818 |       - SV-204474r991589_rule
 1819 |       - V-204474
 1820 |       - permissions
 1821 | 
 1822 | - name: "MEDIUM | RHEL-07-020700 | The Red Hat Enterprise Linux operating system must be configured so that all local initialization files for local interactive users are be group-owned by the users primary group or root."
 1823 |   block:
 1824 |       - name: "MEDIUM | RHEL-07-020700 | AUDIT | The Red Hat Enterprise Linux operating system must be configured so that all local initialization files for local interactive users are be group-owned by the users primary group or root."
 1825 |         ansible.builtin.shell: "{{ find_command_base }} -print -quit"
 1826 |         changed_when: rhel_07_020700_audit.stdout| length > 0
 1827 |         check_mode: false
 1828 |         register: rhel_07_020700_audit
 1829 |         with_items:
 1830 |             - "{{ rhel7stig_passwd }}"
 1831 |         loop_control:
 1832 |             label: "{{ rhel7stig_passwd_label }}"
 1833 |         when: rhel7stig_interactive_uid_start | int <= this_item.uid
 1834 |         vars:
 1835 |             this_item: "{{ item }}"
 1836 | 
 1837 |       - name: "MEDIUM | RHEL-07-020700 | PATCH | The Red Hat Enterprise Linux operating system must be configured so that all local initialization files for local interactive users are be group-owned by the users primary group or root."
 1838 |         ansible.builtin.shell: "{{ find_command_base }} -exec chgrp {{ this_item.gid }} {} +"
 1839 |         with_items: "{{ rhel_07_020700_audit.results }}"
 1840 |         loop_control:
 1841 |             label: "{{ rhel7stig_passwd_label }}"
 1842 |         when: item is changed  # noqa: no-handler
 1843 |         vars:
 1844 |             this_item: "{{ item.item }}"
 1845 |   vars:
 1846 |       find_command_base: 'find "{{ this_item.dir }}" -mindepth 1 -type f
 1847 |               -path "{{ this_item.dir }}/.*" -not -path "{{ this_item.dir }}/.*/*"
 1848 |               -not -group {{ this_item.gid }} -o -group root'
 1849 |   when:
 1850 |       - rhel_07_020700
 1851 |   tags:
 1852 |       - RHEL-07-020700
 1853 |       - CAT2
 1854 |       - CCI-000366
 1855 |       - SRG-OS-000480-GPOS-00227
 1856 |       - SV-204475r991589_rule
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).

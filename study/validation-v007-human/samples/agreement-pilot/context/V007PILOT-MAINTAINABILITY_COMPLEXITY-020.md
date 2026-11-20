# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-020

- Repository: `ansible-lockdown/RHEL7-STIG`
- Commit: `a3d78cfc5c2cae8f8b344fbcd6664a35817dbad0`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `tasks/fix-cat2.yml` (reported anchor line 1)
- Object: `source_location` `7ebf254b2f4793451f3d00646288a760adb464d05b375a69a60db23adbd34117`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–36 of 4812:

```text
    1 | ---
    2 | 
    3 | - name: "MEDIUM | RHEL-07-010019 | PATCH | RHEL 7 must ensure cryptographic verification of vendor software packages."
    4 |   block:
    5 |       - name: "MEDIUM | RHEL-07-010019 | PATCH | RHEL 7 must ensure cryptographic verification of vendor software packages. | package installed"
    6 |         ansible.builtin.package:
    7 |             name: "{{ gpg_package }}"
    8 |             state: present
    9 |         when: "gpg_package not in ansible_facts.packages"
   10 | 
   11 |       - name: "MEDIUM | RHEL-07-010019 | AUDIT | RHEL 7 must ensure cryptographic verification of vendor software packages. | Confirm keys"
   12 |         ansible.builtin.shell: "gpg -q --keyid-format short --with-fingerprint {{ rpm_gpg_key }} | grep -A1 '{{ item.name }}' | grep '{{ item.fingerprint }}'"
   13 |         changed_when: false
   14 |         failed_when: rhel_07_010019_gpg_info.rc not in [ 0, 1]
   15 |         register: rhel_07_010019_gpg_info
   16 |         loop: "{{ gpg_keys }}"
   17 |         loop_control:
   18 |             label: item.name
   19 | 
   20 |       - name: "MEDIUM | RHEL-07-010019 | AUDIT | RHEL 7 must ensure cryptographic verification of vendor software packages. | warn"
   21 |         ansible.builtin.debug:
   22 |             msg:
   23 |                 - "WARNING!! Please investigate the vendor gpgkeys match expected values"
   24 |         loop: "{{ rhel_07_010019_gpg_info.results }}"
   25 |         when: item.rc != 0
   26 |   when:
   27 |       - rhel_07_010019
   28 |   tags:
   29 |       - RHEL-07-010019
   30 |       - CAT2
   31 |       - CCI-001749
   32 |       - SRG-OS-000366-GPOS-00153
   33 |       - SV-256968r982212_rule
   34 |       - V-256968
   35 | 
   36 | ### RHEL-07-010030 | RHEL-07-010040 combined as related tasks in regards to a config file no other content will be in.
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

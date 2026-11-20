# Frozen source context: V007PILOT-STYLE_POLICY-016

- Repository: `ansible-lockdown/RHEL8-STIG`
- Commit: `baa075468dfa59050141c99d99dcacd2e977248c`
- Family: Style/policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `tasks/Cat_2/RHEL-08-040xxx.yml` (reported anchor line 906)
- Object: `task` `ecae79e9ca7e6da829ed16f4736328742b7312434a770ce5f0b2291002794797`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 871–941 of 2049:

```text
  871 |         regexp: '^permissive ='
  872 |         line: 'permissive = 0'
  873 |         create: true
  874 |         mode: 'u-x,go-wx'
  875 | 
  876 | - name: |
  877 |     "MEDIUM | RHEL-08-040139 | PATCH | RHEL 8 must have the USBGuard installed."
  878 |     "MEDIUM | RHEL-08-040140 | PATCH | RHEL 8 must block unauthorized peripherals before establishing a connection."
  879 |     "MEDIUM | RHEL-08-040141 | PATCH | RHEL 8 must enable the USBGuard."
  880 |   when:
  881 |     - rhel8stig_040139 or
  882 |       rhel8stig_040140 or
  883 |       rhel8stig_040141
  884 |   tags:
  885 |     - RHEL-08-040139
  886 |     - RHEL-08-040140
  887 |     - RHEL-08-040141
  888 |     - CAT2
  889 |     - CCI-001958
  890 |     - NIST800-53R4_IA-3
  891 |     - SRG-OS-000378-GPOS-00163
  892 |     - SV-244547r1014811_rule
  893 |     - SV-230524r1155418_rule
  894 |     - SV-244548r1014815_rule
  895 |     - V-244547
  896 |     - V-230524
  897 |     - V-244548
  898 |     - usbguard
  899 |   block:
  900 |     - name: "MEDIUM | RHEL-08-040139 | PATCH | RHEL 8 must have the USBGuard installed. | Install usbguard"
  901 |       when: rhel8stig_040139
  902 |       ansible.builtin.package:
  903 |         name: usbguard
  904 |         state: present
  905 | 
  906 |     - name: "MEDIUM | RHEL-08-040140 | PATCH | RHEL 8 must block unauthorized peripherals before establishing a connection. | generate policy"
  907 |       when:
  908 |         - rhel8stig_040140
  909 |         - rhel8stig_040139
  910 |       ansible.builtin.command: usbguard generate-policy > /etc/usbguard/rules.conf
  911 |       changed_when: true
  912 | 
  913 |     - name: "MEDIUM | RHEL-08-040141 | PATCH | RHEL 8 must enable the USBGuard. | Start/Enable service"
  914 |       when:
  915 |         - rhel8stig_040141
  916 |         - rhel8stig_040139
  917 |       ansible.builtin.service:
  918 |         name: usbguard
  919 |         enabled: true
  920 |       notify: Restart usbguard
  921 | 
  922 | - name: "MEDIUM | RHEL-08-040150 | PATCH | A firewall must be able to protect against or limit the effects of Denial of Service (DoS) attacks by ensuring RHEL 8 can implement rate-limiting measures on impacted network interfaces."
  923 |   when:
  924 |     - rhel8stig_040150
  925 |     - rhel8stig_firewall_service != "not_required"
  926 |   tags:
  927 |     - RHEL-08-040150
  928 |     - CAT2
  929 |     - CCI-002385
  930 |     - NIST800-53R4_SC-5
  931 |     - SRG-OS-000420-GPOS-00186
  932 |     - SV-230525r958902_rule
  933 |     - V-230525
  934 |     - firewall
  935 |     - nftables
  936 |   ansible.builtin.lineinfile:
  937 |     path: /etc/firewalld/firewalld.conf
  938 |     regexp: '^FirewallBackend='
  939 |     line: 'FirewallBackend=nftables'
  940 | 
  941 | - name: |
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

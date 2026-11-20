# Frozen source context: V007PILOT-SECURITY-014

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: Security
- Rule: `ansibleguard/unsafe-file-write`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `automation/roles/resolv_conf/tasks/main.yml` (reported anchor line 17)
- Object: `source_location` `f56af934daba51381c58cc8797ecb8c56238c170cf737a39ca6f651cd202e285`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–34 of 34:

```text
    1 | ---
    2 | - block:
    3 |     - name: Make sure /etc/resolv.conf exists
    4 |       ansible.builtin.stat:
    5 |         path: /etc/resolv.conf
    6 |       register: resolv_conf
    7 | 
    8 |     - name: Create /etc/resolv.conf
    9 |       ansible.builtin.file:
   10 |         path: /etc/resolv.conf
   11 |         state: touch
   12 |         owner: root
   13 |         group: root
   14 |         mode: u=rw,g=r,o=r
   15 |       when: not resolv_conf.stat.exists
   16 | 
   17 |     - name: Manage DNS server entries in /etc/resolv.conf
   18 |       ansible.builtin.lineinfile:
   19 |         path: /etc/resolv.conf
   20 |         regexp: '^nameserver[ \t]+{{ resolv_conf_nameserver | regex_escape }}[ \t]*(?:#.*)?$'
   21 |         insertbefore: "^options"
   22 |         line: "nameserver {{ resolv_conf_nameserver }}"
   23 |         state: "{{ resolv_conf_entry_state }}"
   24 |         unsafe_writes: true # to prevent failures in CI
   25 |       loop: "{{ nameservers }}"
   26 |       loop_control:
   27 |         label: "{{ resolv_conf_nameserver }} ({{ resolv_conf_entry_state }})"
   28 |       vars:
   29 |         resolv_conf_nameserver: "{{ item.entry if item is mapping else item }}"
   30 |         resolv_conf_entry_state: "{{ item.state | default('present') if item is mapping else 'present' }}"
   31 |   when:
   32 |     - nameservers is defined
   33 |     - nameservers | length > 0
   34 |   tags: dns, nameservers
```

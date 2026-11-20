# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-007

- Repository: `dfroberg/cluster`
- Commit: `7bc521db65db986a2deef35ea955704bb0621dbd`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-play`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `provision/ansible/kubernetes/playbooks/kubernetes/rook-ceph-nuke.yml` (reported anchor line 2)
- Object: `source_location` `c622386b9706f949d942ddf53f83cf81b02ee13f6504337f120efa5821ed0d46`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–80 of 80:

```text
    1 | ---
    2 | - hosts:
    3 |     - master
    4 |     - worker
    5 |     - storage
    6 |   become: true
    7 |   gather_facts: true
    8 |   any_errors_fatal: true
    9 |   pre_tasks:
   10 |     - setup:
   11 |       register: setup_status
   12 |       until: setup_status is success
   13 |       delay: 10
   14 |       retries: 30
   15 |     - block:
   16 |         - stat: path=/var/run/reboot-required
   17 |           register: reboot_required
   18 |           check_mode: no
   19 |       when: allow_reboot is not defined or (allow_reboot is defined and allow_reboot == true)
   20 |   post_tasks:
   21 |     - block:
   22 |         - stat: path=/var/run/reboot-required
   23 |           register: reboot_required
   24 |           check_mode: no
   25 | 
   26 |         - name: "Restart Server"
   27 |           reboot:
   28 |             msg: "Reboot Ansible-Playbook after update"
   29 |             reboot_timeout: 3600
   30 |           register: result
   31 |           when: reboot_required.stat.exists
   32 | 
   33 |         - name: "Info if Reboot was sucessful"
   34 |           debug:
   35 |             msg: "{{ inventory_hostname }} has rebooted: {{ result.rebooted }}, it has taken: {{ result.elapsed }} seconds"
   36 |           when: reboot_required.stat.exists
   37 |       when: allow_reboot is not defined or (allow_reboot is defined and allow_reboot == true)
   38 |   tasks:
   39 |     # Ensure any remnants of rook is nuked on ALL nodes
   40 |     - name: Remove /var/lib/rook
   41 |       ansible.builtin.file:
   42 |         state: absent
   43 |         path: "/var/lib/rook"
   44 | 
   45 |     - name: Locating all files in rook backup dir
   46 |       find:
   47 |         path: "/var/ramdisk-backup"
   48 |       register: cleanup
   49 |       ignore_errors: true
   50 | 
   51 |     - name: Removing all files previously found in rook backup dir
   52 |       file:
   53 |         path: "{{ item.path }}"
   54 |         state: absent
   55 |       with_items: "{{ cleanup.files }}"
   56 |       ignore_errors: true
   57 | 
   58 |     - name: Reset disks
   59 |       block:
   60 |         - name: Zap the drives
   61 |           ansible.builtin.shell: >
   62 |             sgdisk --zap-all {{ item }} || true
   63 |           loop:
   64 |             - "{{ rook_devices }}"
   65 |         - name: Remove lvm partitions
   66 |           ansible.builtin.shell: "{{ item }}"
   67 |           loop:
   68 |             - ls /dev/mapper/ceph--* | xargs -I% -- fuser --kill %
   69 |             - ls /dev/mapper/ceph--* | xargs -I% -- dmsetup clear %
   70 |             - ls /dev/mapper/ceph--* | xargs -I% -- dmsetup remove -f %
   71 |             - ls /dev/mapper/ceph--* | xargs -I% -- rm -rf %
   72 |         - name: Wipe the block device
   73 |           ansible.builtin.command: "wipefs -af {{ item }}"
   74 |           with_items:
   75 |             - "{{ rook_devices }}"
   76 |       when:
   77 |         - rook_devices is defined
   78 |         - rook_devices is iterable
   79 |         - rook_devices | length > 0
   80 | 
```

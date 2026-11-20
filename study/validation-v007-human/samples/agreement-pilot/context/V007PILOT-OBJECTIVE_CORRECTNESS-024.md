# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-024

- Repository: `dfroberg/cluster`
- Commit: `7bc521db65db986a2deef35ea955704bb0621dbd`
- Family: Objective correctness
- Rule: `ansibleguard/invalid-task-attribute-type`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `provision/ansible/kubernetes/playbooks/kubernetes/roles/ubuntu/tasks/mounts.yml` (reported anchor line 55)
- Object: `attribute` `6a4a77b9e74ac1ac9b9d14a4dd81ba434637ed57a167d141502a49bded643ead`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–66 of 66:

```text
    1 | ---
    2 | - name: stat /dev/shm
    3 |   stat:
    4 |     path: /dev/shm
    5 |   register: dev_shm
    6 |   tags:
    7 |     - mount
    8 |     - shm
    9 | 
   10 | - name: mount /dev/shm with noexec and size 12G
   11 |   become: 'yes'
   12 |   mount:
   13 |     name: /dev/shm
   14 |     src: none
   15 |     fstype: tmpfs
   16 |     opts: rw,nosuid,nodev,noexec,size=16G
   17 |     state: present
   18 |   when: dev_shm.stat.exists
   19 |   tags:
   20 |     - mount
   21 |     - shm
   22 | 
   23 | - name: create tmp.mount
   24 |   ansible.builtin.template:
   25 |     src: etc/systemd/tmp.mount.j2
   26 |     dest: /etc/systemd/system/tmp.mount
   27 |     backup: 'yes'
   28 |     mode: 0644
   29 |     owner: root
   30 |     group: root
   31 |   tags:
   32 |     - mount
   33 |     - systemd
   34 |     - tmp
   35 | 
   36 | - name: stat tmp.mount
   37 |   stat:
   38 |     path: /etc/systemd/system/tmp.mount
   39 |   register: tmp_mount
   40 |   tags:
   41 |     - mount
   42 |     - tmp
   43 | 
   44 | - name: unmask tmp.mount
   45 |   become: 'yes'
   46 |   systemd:
   47 |     name: tmp.mount
   48 |     masked: 'no'
   49 |   when: tmp_mount.stat.exists
   50 |   tags:
   51 |     - mount
   52 |     - systemd
   53 |     - tmp
   54 | 
   55 | - name: start tmp.mount
   56 |   become: 'yes'
   57 |   systemd:
   58 |     name: tmp.mount
   59 |     daemon_reload: 'yes'
   60 |     state: started
   61 |     enabled: 'yes'
   62 |   when: tmp_mount.stat.exists
   63 |   tags:
   64 |     - mount
   65 |     - systemd
   66 |     - tmp
```

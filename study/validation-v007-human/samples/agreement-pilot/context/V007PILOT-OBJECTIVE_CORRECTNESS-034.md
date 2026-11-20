# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-034

- Repository: `grycap/im`
- Commit: `5e54aa6e02108a615abf2670abaa4aa1c56add02`
- Family: Objective correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `contextualization/AnsibleRecipes/utils/tasks/disk_format_mount.yml` (reported anchor line 66)
- Object: `task` `fc473dd1d74617b86f8e4bee585a3aad0872201b862cbe241e5a26e5002de735`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–67 of 67:

```text
    1 | # IM - Infrastructure Manager
    2 | # Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
    3 | # 
    4 | # This program is free software: you can redistribute it and/or modify
    5 | # it under the terms of the GNU General Public License as published by
    6 | # the Free Software Foundation, either version 3 of the License, or
    7 | # (at your option) any later version.
    8 | #
    9 | # This program is distributed in the hope that it will be useful,
   10 | # but WITHOUT ANY WARRANTY; without even the implied warranty of
   11 | # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   12 | # GNU General Public License for more details.
   13 | #
   14 | # You should have received a copy of the GNU General Public License
   15 | # along with this program.  If not, see <http://www.gnu.org/licenses/>.
   16 | 
   17 | - set_fact: partition={{device}}p1
   18 |   when: "'nvme' in device"
   19 | 
   20 | - set_fact: partition={{device}}1
   21 |   when: "'nvme' not in device"
   22 | 
   23 | #- shell: (echo n; echo p; echo 1; echo ; echo; echo w) | fdisk {{device}} creates={{partition}}
   24 | #  args:
   25 | #    creates: "{{partition}}"
   26 | 
   27 | - name: Install parted package
   28 |   package: name=parted
   29 |   ignore_errors: yes
   30 | 
   31 | - name: Check if partition exists
   32 |   stat:
   33 |     path: "{{partition}}"
   34 |   register: partition_stat
   35 | 
   36 | - name: Create partition
   37 |   parted: device={{device}} number=1 state=present part_type=primary label=gpt
   38 |   when: not partition_stat.stat.exists
   39 | 
   40 | - name: Format partition
   41 |   filesystem: fstype={{fstype}} dev={{partition}}
   42 |   ignore_errors: yes
   43 |   register: format
   44 | 
   45 | - when: fstype == 'swap' and not format is failed
   46 |   block:
   47 |     - name: Create swap
   48 |       command: mkswap {{partition}}
   49 | 
   50 |     - name: Add swap entry in /etc/fstab
   51 |       lineinfile:
   52 |         path: /etc/fstab
   53 |         state: present
   54 |         line: "{{partition}} none swap sw 0 0"
   55 | 
   56 |     - name: Activate swap
   57 |       command: swapon {{partition}}
   58 | 
   59 | - when: fstype != 'swap'
   60 |   block:
   61 | 
   62 |   - name: Create mount point
   63 |     file: path={{mount_path}} state=directory
   64 | 
   65 |   - name: Mount partition
   66 |     mount: name={{mount_path}} src={{partition}} state=mounted fstype={{fstype}}
   67 |     when: not format is failed
```

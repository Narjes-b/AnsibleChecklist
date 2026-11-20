# Frozen source context: V007PILOT-STRUCTURE_REUSE-016

- Repository: `CentOS-PaaS-SIG/linchpin`
- Commit: `0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `dev_setup/playbooks/roles/minishift/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `a9bf5748f4fbd8754b584372b6549fa5c8e295cc0fc633ec668f3b47c3f670f4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–41 of 41:

```text
    1 | ---
    2 | # setup minishift
    3 | 
    4 | # Determine if minishift binary exists
    5 | - name: "Is minishift binary present in {{ minishift_dest_dir }}"
    6 |   stat:
    7 |     path: "{{ minishift_dest_dir }}/minishift"
    8 |   register: minishift_bin
    9 | 
   10 | # install minishift
   11 | - include: install_minishift_bin.yml
   12 |   when: (minishift_bin.stat.exists == false or force_minishift_install|bool == true)
   13 | 
   14 | # set disk size and memory
   15 | - name: "Set minishift disk-size {{ disk_size }}"
   16 |   shell: minishift config set disk-size {{ disk_size }}
   17 | 
   18 | - name: "Set minishift disk-size {{ memory }}"
   19 |   shell: minishift config set memory {{ memory }}
   20 | 
   21 | # set base device size
   22 | - name: "Set minishift base device size to {{basedevice_size}}"
   23 |   shell: minishift config set docker-opt "storage-opt=dm.basesize={{basedevice_size}}"
   24 | 
   25 | - name: Pull down the minishift iso
   26 |   get_url:
   27 |     url: "{{ minishift_iso }}"
   28 |     dest: "{{ minishift_dest_dir }}/minishift.iso"
   29 |     timeout: 120
   30 | 
   31 | # check if the minishift profile exists
   32 | - name: "Check if the minishift profile exists"
   33 |   shell: "minishift status --profile {{ profile }} | head -1 | grep -i 'does not exist'"
   34 |   register: minishift_exist
   35 |   ignore_errors: yes
   36 | 
   37 | # initialize minishift
   38 | - include: init_minishift.yml
   39 |   when: minishift_exist.stdout != ""
   40 | 
   41 | 
```

## Frozen tracked paths in the relevant role/scope

```text
dev_setup/playbooks/roles/minishift/defaults/main.yml
dev_setup/playbooks/roles/minishift/tasks/init_minishift.yml
dev_setup/playbooks/roles/minishift/tasks/install_minishift_bin.yml
dev_setup/playbooks/roles/minishift/tasks/main.yml
dev_setup/playbooks/roles/minishift/tasks/set_minishift_path.yml
```

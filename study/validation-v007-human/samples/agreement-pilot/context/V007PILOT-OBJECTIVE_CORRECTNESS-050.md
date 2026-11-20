# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-050

- Repository: `oliversalzburg/ansible-workstation`
- Commit: `635ab67d1fdf72ea4de69556c8dd428626699df5`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `provision/ansible/roles/gpu_nvidia/tasks/main.yml` (reported anchor line 2)
- Object: `source_location` `6a8caf3650a938c4b893e00e367ae5fdc35079de4cc50078dbb85229911f1b46`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–57 of 57:

```text
    1 | ---
    2 | - name: Check APT non-free
    3 |   ansible.builtin.shell:
    4 |     cmd: |
    5 |       set -o pipefail
    6 |       apt-cache policy | grep bookworm/non-free
    7 |     executable: /bin/bash
    8 |   register: gpu_nvidia_result_check_nonfree
    9 |   changed_when: gpu_nvidia_result_check_nonfree.rc == 1
   10 |   failed_when: gpu_nvidia_result_check_nonfree.rc > 1
   11 | - name: Enable APT non-free
   12 |   become: true
   13 |   ansible.builtin.command: apt-add-repository --yes non-free
   14 |   when: gpu_nvidia_result_check_nonfree.rc == 1
   15 |   changed_when: true
   16 | 
   17 | - name: Check APT non-free-firmware
   18 |   ansible.builtin.shell:
   19 |     cmd: |
   20 |       set -o pipefail
   21 |       apt-cache policy | grep bookworm/non-free-firmware
   22 |     executable: /bin/bash
   23 |   register: gpu_nvidia_result_check_nonfreefirmware
   24 |   changed_when: gpu_nvidia_result_check_nonfreefirmware.rc == 1
   25 |   failed_when: gpu_nvidia_result_check_nonfreefirmware.rc > 1
   26 | - name: Enable APT non-free-firmware
   27 |   become: true
   28 |   ansible.builtin.command: apt-add-repository --yes non-free-firmware
   29 |   when: gpu_nvidia_result_check_nonfreefirmware.rc == 1
   30 |   changed_when: true
   31 | 
   32 | - name: Check APT contrib
   33 |   ansible.builtin.shell:
   34 |     cmd: |
   35 |       set -o pipefail
   36 |       apt-cache policy | grep bookworm/contrib
   37 |     executable: /bin/bash
   38 |   register: gpu_nvidia_result_check_contrib
   39 |   changed_when: gpu_nvidia_result_check_contrib.rc == 1
   40 |   failed_when: gpu_nvidia_result_check_contrib.rc > 1
   41 | - name: Enable APT contrib
   42 |   become: true
   43 |   ansible.builtin.command: apt-add-repository --yes contrib
   44 |   when: gpu_nvidia_result_check_contrib.rc == 1
   45 |   changed_when: true
   46 | 
   47 | - name: Install Nvidia driver
   48 |   become: true
   49 |   ansible.builtin.apt:
   50 |     install_recommends: true
   51 |     update_cache: true
   52 |     name:
   53 |       - firmware-misc-nonfree
   54 |       - linux-headers-amd64
   55 |       - nvidia-driver
   56 |       - vainfo
   57 |       - vdpauinfo
```

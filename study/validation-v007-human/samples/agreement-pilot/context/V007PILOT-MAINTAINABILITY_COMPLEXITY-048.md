# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-048

- Repository: `seapath/ansible`
- Commit: `bc10619e516866d0e86af601fd7aa8738b55e645`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/debian_grub_bootcount/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `778da35c7ba44c1eeea499568d507ebe538a28e39dfdebfb54b5838aa3cbcb75`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–178 of 178:

```text
    1 | # Copyright (C) 2025 RTE
    2 | # SPDX-License-Identifier: Apache-2.0
    3 | 
    4 | ---
    5 | # add grub-editenv to initramfs
    6 | - name: "Add initramfs-tools SEAPATH hooks"
    7 |   ansible.builtin.copy:
    8 |     src: initramfs-tools/hooks/seapath
    9 |     dest: /etc/initramfs-tools/hooks/seapath
   10 |     mode: "0755"
   11 |   notify: Rebuild initramfs if necessary
   12 |   when: not debian_grub_bootcount_revert
   13 | - name: "REVERT Add initramfs-tools SEAPATH hooks"
   14 |   ansible.builtin.file:
   15 |     path: /etc/initramfs-tools/hooks/seapath
   16 |     state: absent
   17 |   notify: Rebuild initramfs if necessary
   18 |   when: debian_grub_bootcount_revert
   19 | 
   20 | # Needed to open ESP (usually in /boot/efi/) from initramfs.
   21 | - name: "Add FAT modules into initramfs"
   22 |   ansible.builtin.blockinfile:
   23 |     path: /etc/initramfs-tools/modules
   24 |     marker: "# {mark} ANSIBLE MANAGED BLOCK GRUBCOUNT"
   25 |     block: |
   26 |       fat
   27 |       vfat
   28 |       nls_ascii
   29 |       nls_cp437
   30 |     state: present
   31 |   notify: Rebuild initramfs if necessary
   32 |   when: not debian_grub_bootcount_revert
   33 | - name: "REVERT Add FAT modules into initramfs"
   34 |   ansible.builtin.blockinfile:
   35 |     path: /etc/initramfs-tools/modules
   36 |     marker: "# {mark} ANSIBLE MANAGED BLOCK GRUBCOUNT"
   37 |     state: absent
   38 |   notify: Rebuild initramfs if necessary
   39 |   when: debian_grub_bootcount_revert
   40 | 
   41 | # The rest of the tasks needed to set up the boot count feature
   42 | - name: "Add initramfs-tools script: script file"
   43 |   ansible.builtin.copy:
   44 |     src: initramfs-tools/scripts/init-premount/bootcount_recovery
   45 |     dest: /etc/initramfs-tools/scripts/init-premount/bootcount_recovery
   46 |     mode: "0755"
   47 |   notify: Rebuild initramfs if necessary
   48 |   when: not debian_grub_bootcount_revert
   49 | - name: "REVERT Add initramfs-tools script: script file"
   50 |   ansible.builtin.file:
   51 |     path: /etc/initramfs-tools/scripts/init-premount/bootcount_recovery
   52 |     state: absent
   53 |   notify: Rebuild initramfs if necessary
   54 |   when: debian_grub_bootcount_revert
   55 | 
   56 | - name: Add seapath_boot_count_params to grub default cmdline
   57 |   ansible.builtin.lineinfile:
   58 |     insertafter: EOF
   59 |     path: /etc/default/grub
   60 |     line: "GRUB_CMDLINE_LINUX_DEFAULT=\"${GRUB_CMDLINE_LINUX_DEFAULT:+$GRUB_CMDLINE_LINUX_DEFAULT }\\$seapath_boot_count_params\""
   61 |     state: present
   62 |   notify: Update-grub
   63 |   when: not debian_grub_bootcount_revert
   64 | - name: Remove seapath_boot_count_params from GRUB_CMDLINE_LINUX_DEFAULT
   65 |   ansible.builtin.replace:
   66 |     path: /etc/default/grub
   67 |     regexp: "(\\s*\\\\\\$seapath_boot_count_params)"
   68 |     replace: ""
   69 |   when: debian_grub_bootcount_revert
   70 | 
   71 | - name: Backup 10_linux before patching
   72 |   ansible.builtin.copy:
   73 |     src: /etc/grub.d/10_linux
   74 |     dest: /etc/grub.d_backup10_linux
   75 |     mode: preserve
   76 |     remote_src: true
   77 |     force: false
   78 |   when: not debian_grub_bootcount_revert
   79 | - name: Add hooks to /etc/grub.d/10_linux
   80 |   ansible.posix.patch:
   81 |     dest: /etc/grub.d/10_linux
   82 |     src: 10_linux.patch
   83 |   notify: Update-grub
   84 |   when: not debian_grub_bootcount_revert
   85 | - name: REVERT Restore original 10_linux
   86 |   ansible.builtin.copy:
   87 |     src: /etc/grub.d_backup10_linux
   88 |     dest: /etc/grub.d/10_linux
   89 |     mode: preserve
   90 |     remote_src: true
   91 |   notify: Update-grub
   92 |   when: debian_grub_bootcount_revert
   93 | - name: Remove backup file /etc/grub.d_backup10_linux
   94 |   ansible.builtin.file:
   95 |     path: /etc/grub.d_backup10_linux
   96 |     state: absent
   97 |   when: debian_grub_bootcount_revert
   98 | 
   99 | - name: Add SEAPATH bootcount to grub
  100 |   ansible.builtin.copy:
  101 |     src: 11_seapath_boot_count
  102 |     dest: /etc/grub.d/11_seapath_boot_count
  103 |     mode: "0755"
  104 |   notify: Update-grub
  105 |   when: not debian_grub_bootcount_revert
  106 | - name: REVERT Add SEAPATH bootcount to grub
  107 |   ansible.builtin.file:
  108 |     path: /etc/grub.d/11_seapath_boot_count
  109 |     state: absent
  110 |   notify: Update-grub
  111 |   when: debian_grub_bootcount_revert
  112 | 
  113 | - name: Ensure /usr/lib/seapath_bootcount/ exists
  114 |   ansible.builtin.file:
  115 |     path: /usr/lib/seapath_bootcount/
  116 |     state: directory
  117 |     mode: "0755"
  118 |   when: not debian_grub_bootcount_revert
  119 | 
  120 | - name: Install system_check
  121 |   ansible.builtin.copy:
  122 |     src: system_check
  123 |     dest: /usr/lib/seapath_bootcount/system_check
  124 |     mode: "0755"
  125 |   when: not debian_grub_bootcount_revert
  126 | 
  127 | - name: REVERT Ensure /usr/lib/seapath_bootcount/ exists
  128 |   ansible.builtin.file:
  129 |     path: /usr/lib/seapath_bootcount/
  130 |     state: absent
  131 |   when: debian_grub_bootcount_revert
  132 | 
  133 | - name: Add system_check service
  134 |   ansible.builtin.copy:
  135 |     src: system_check.service
  136 |     dest: /etc/systemd/system/system_check.service
  137 |     mode: "0644"
  138 |   when: not debian_grub_bootcount_revert
  139 | 
  140 | - name: Enable system_check.service
  141 |   ansible.builtin.systemd:
  142 |     name: system_check
  143 |     enabled: true
  144 |     daemon-reload: true
  145 |     state: restarted
  146 |   when: not debian_grub_bootcount_revert
  147 | 
  148 | - name: Gather service facts
  149 |   ansible.builtin.service_facts:
  150 |   when: debian_grub_bootcount_revert
  151 | - name: REVERT Enable system_check.service
  152 |   ansible.builtin.systemd:
  153 |     name: system_check
  154 |     enabled: false
  155 |     daemon-reload: true
  156 |     state: stopped
  157 |   when:
  158 |     - debian_grub_bootcount_revert
  159 |     - "'system_check.service' in ansible_facts.services"
  160 | 
  161 | - name: REVERT Add system_check service
  162 |   ansible.builtin.file:
  163 |     path: /etc/systemd/system/system_check.service
  164 |     state: absent
  165 |   when: debian_grub_bootcount_revert
  166 | 
  167 | - name: Create /boot/efi/bootcountenv
  168 |   ansible.builtin.shell:
  169 |     cmd: |
  170 |       /usr/bin/grub-editenv /boot/efi/bootcountenv create
  171 |       /usr/bin/grub-editenv /boot/efi/bootcountenv set bootcount=disabled
  172 |   changed_when: true
  173 |   when: not debian_grub_bootcount_revert
  174 | - name: REVERT Create /boot/efi/bootcountenv
  175 |   ansible.builtin.file:
  176 |     path: /boot/efi/bootcountenv
  177 |     state: absent
  178 |   when: debian_grub_bootcount_revert
```

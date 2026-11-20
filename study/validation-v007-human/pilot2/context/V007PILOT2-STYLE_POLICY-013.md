# Frozen source context: V007PILOT2-STYLE_POLICY-013

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: style_policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/afm_cos_upgrade/tasks/install_local_pkg.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/afm_cos_upgrade/tasks/install_local_pkg.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–125 of 125:

```text
    1 | ---
    2 | # Local package installation method
    3 | 
    4 | - block:  ## run_once: true
    5 |     - name: upgrade | Stat local installation package
    6 |       stat:
    7 |         path: "{{ scale_install_localpkg_path }}"
    8 |         checksum_algorithm: md5
    9 |       register: scale_install_localpkg
   10 | 
   11 |     - name: upgrade | Check local installation package
   12 |       assert:
   13 |         that: scale_install_localpkg.stat.exists
   14 |         msg: >-
   15 |           Please set the variable 'scale_install_localpkg_path' to point to the
   16 |           local installation package (accessible on Ansible control machine)!
   17 | #
   18 | # Optionally, verify package checksum
   19 | #
   20 |     - name: upgrade | Stat checksum file
   21 |       stat:
   22 |         path: "{{ scale_install_localpkg_path }}.md5"
   23 |       register: scale_install_md5_file
   24 | 
   25 |     - block:  ## when: scale_install_md5_file.stat.exists
   26 |         - name: upgrade | Read checksum from file
   27 |           set_fact:
   28 |             scale_install_md5_sum: "{{ lookup('file', scale_install_localpkg_path + '.md5') }}"
   29 | 
   30 |         - name: upgrade | Compare checksums
   31 |           assert:
   32 |             that: scale_install_md5_sum.strip().split().0 == scale_install_localpkg.stat.checksum
   33 |             msg: >-
   34 |               Checksums don't match. Please check integritiy of your local
   35 |               installation package!
   36 |       when: scale_install_md5_file.stat.exists
   37 |   run_once: true
   38 |   delegate_to: localhost
   39 | 
   40 | #
   41 | # Copy installation package
   42 | #
   43 | - name: upgrade | Stat extracted packages
   44 |   stat:
   45 |     path: "{{ scale_gpfs_path_url }}"
   46 |   register: scale_install_gpfs_packagedir
   47 | 
   48 | - block:  ## when: not scale_install_gpfs_packagedir.stat.exists
   49 |     - name: upgrade | Stat temporary directory
   50 |       stat:
   51 |         path: "{{ scale_install_localpkg_tmpdir_path }}"
   52 |       register: scale_install_localpkg_tmpdir
   53 | 
   54 |     - name: upgrade | Check temporary directory
   55 |       assert:
   56 |         that:
   57 |           - scale_install_localpkg_tmpdir.stat.exists
   58 |           - scale_install_localpkg_tmpdir.stat.isdir
   59 |         msg: >-
   60 |           Please set the variable 'scale_install_localpkg_tmpdir_path' to point
   61 |           to a temporary directory on the remote system!
   62 |     - name: upgrade | Copy installation package to node
   63 |       copy:
   64 |         src: "{{ scale_install_localpkg_path }}"
   65 |         dest: "{{ scale_install_localpkg_tmpdir_path }}"
   66 |         mode: a+x
   67 |   when: not scale_install_gpfs_packagedir.stat.exists
   68 | 
   69 | #
   70 | # Extract installation package
   71 | #
   72 | - name: upgrade | Extract installation package
   73 |   vars:
   74 |     localpkg: "{{ scale_install_localpkg_tmpdir_path + '/' + scale_install_localpkg_path | basename }}"
   75 |   command: "{{ localpkg + ' --silent' }}"
   76 |   args:
   77 |     creates: "{{ scale_gpfs_path_url }}"
   78 | 
   79 | - name: upgrade | Stat extracted packages
   80 |   stat:
   81 |     path: "{{ scale_gpfs_path_url }}"
   82 |   register: scale_install_gpfs_packagedir
   83 | 
   84 | - name: upgrade | Check extracted packages
   85 |   assert:
   86 |     that:
   87 |       - scale_install_gpfs_packagedir.stat.exists
   88 |       - scale_install_gpfs_packagedir.stat.isdir
   89 |     msg: >-
   90 |       The variable 'scale_version' doesn't seem to match the contents of the
   91 |       local installation package!
   92 | #
   93 | # Delete installation package
   94 | #
   95 | - name: upgrade | Delete installation package from node
   96 |   file:
   97 |     path: "{{ scale_install_localpkg_tmpdir_path + '/' + scale_install_localpkg_path | basename }}"
   98 |     state: absent
   99 | 
  100 | #
  101 | # Find GPFS AFM COS(HPT)
  102 | #
  103 | - block:
  104 |     - name: upgrade | Find GPFS HPT (gpfs.afm.cos) packages
  105 |       find:
  106 |         paths: "{{ scale_gpfs_path_url }}"
  107 |         patterns: gpfs.afm.cos*
  108 |       register: scale_install_gpfs_hpt
  109 | 
  110 |     - name: upgrade | Check valid GPFS HPT (gpfs.afm.cos) packages
  111 |       assert:
  112 |         that: scale_install_gpfs_hpt.matched > 0
  113 |         msg: >-
  114 |           No GPFS HPT (gpfs.afm.cos) packages found:
  115 |           "{{ scale_gpfs_path_url }}/gpfs.afm.cos*"
  116 | 
  117 |     - name: upgrade | Add GPFS HPT packages to list
  118 |       vars:
  119 |         current_package: "{{ scale_gpfs_path_url }}/{{ item }}"
  120 |       set_fact:
  121 |         scale_install_all_packages: "{{ scale_install_all_packages + [ current_package ] }}"
  122 |       with_items:
  123 |         - "{{ scale_install_gpfs_hpt.files.0.path | basename }}"
  124 | 
  125 |   when: scale_install_package | bool
```

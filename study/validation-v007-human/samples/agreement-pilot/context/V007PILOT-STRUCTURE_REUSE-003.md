# Frozen source context: V007PILOT-STRUCTURE_REUSE-003

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/s3_install/tasks/install_dir_pkg.yml` (reported anchor line 1)
- Object: `source_location` `508ddd3a461d1821041364368739b01897353eb96552118f76984a261732b808`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–77 of 77:

```text
    1 | ---
    2 | # Dir package installation method
    3 | 
    4 | - block:  ## run_once: true
    5 |     - name: install | Stat directory installation package
    6 |       stat:
    7 |         path: "{{ scale_install_directory_pkg_path }}"
    8 |       register: scale_install_dirpkg
    9 | 
   10 |     - name: install | Check directory installation package
   11 |       assert:
   12 |         that: scale_install_dirpkg.stat.exists
   13 |         msg: >-
   14 |           Please set the variable 'scale_install_directory_pkg_path' to point to the
   15 |           local installation package (accessible on Ansible control machine)!
   16 |   run_once: true
   17 |   delegate_to: localhost
   18 | 
   19 | - name: install| Creates default directory
   20 |   file:
   21 |     path: "{{ scale_extracted_path }}"
   22 |     state: directory
   23 |     mode: a+x
   24 |     recurse: yes
   25 | 
   26 | - name: install | Stat extracted packages
   27 |   stat:
   28 |     path: "{{ scale_extracted_path + '/' + scale_install_directory_pkg_path | basename }}"
   29 |   register: scale_install_gpfs_packagedir
   30 | 
   31 | #
   32 | # Copy installation directory package to default
   33 | #
   34 | - block:
   35 |     - name: install | Copy installation package to node
   36 |       copy:
   37 |         src: "{{ scale_install_directory_pkg_path }}"
   38 |         dest: "{{ scale_extracted_path }}"
   39 |         mode: a+x
   40 | 
   41 | - name: install | Set installation package path
   42 |   set_fact:
   43 |     dir_path: "{{ scale_extracted_path + '/' + scale_install_directory_pkg_path | basename }}"
   44 | 
   45 | - name: install | gpfs base path
   46 |   set_fact:
   47 |     gpfs_path_url: "{{ dir_path }}"
   48 |   when: scale_install_directory_pkg_path is defined
   49 | 
   50 | #
   51 | # Find noobaa-core
   52 | #
   53 | # 
   54 | 
   55 | - block:  ## when: host is defined as a protocol node
   56 | 
   57 |   - name: install | Find noobaa-core (noobaa-core) package
   58 |     find:
   59 |      paths:  "{{ gpfs_path_url }}"
   60 |      patterns: noobaa-core*
   61 |     register: scale_install_gpfs_s3
   62 | 
   63 |   - name: install | Check valid GPFS (s3) package
   64 |     assert:
   65 |      that: scale_install_gpfs_s3.matched > 0
   66 |      msg: "No S3 (noobaa-core) package found {{ gpfs_path_url }}noobaa-core*"
   67 | 
   68 |   - name: install | Add GPFS s3 package to list
   69 |     vars:
   70 |      current_package:  "{{ item.path }}"
   71 |     set_fact:
   72 |      scale_install_all_packages: "{{ scale_install_all_packages + [ current_package ] }}"
   73 |     with_items:
   74 |     - "{{ scale_install_gpfs_s3.files }}"
   75 | 
   76 | - debug:
   77 |    msg: "{{ scale_install_all_packages }}"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/s3_install/defaults/main.yml
roles/s3_install/handlers/main.yml
roles/s3_install/meta/main.yml
roles/s3_install/tasks/apt/install.yml
roles/s3_install/tasks/install.yml
roles/s3_install/tasks/install_dir_pkg.yml
roles/s3_install/tasks/install_local_pkg.yml
roles/s3_install/tasks/install_remote_pkg.yml
roles/s3_install/tasks/install_repository.yml
roles/s3_install/tasks/main.yml
roles/s3_install/tasks/parseFile.yml
roles/s3_install/tasks/yum/install.yml
roles/s3_install/tasks/zypper/install.yml
roles/s3_install/vars/main.yml
```

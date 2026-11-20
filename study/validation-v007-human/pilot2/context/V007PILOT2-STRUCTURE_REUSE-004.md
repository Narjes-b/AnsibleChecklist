# Frozen source context: V007PILOT2-STRUCTURE_REUSE-004

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: structure_reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/perfmon_upgrade/tasks/install_dir_pkg.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/perfmon_upgrade/tasks/install_dir_pkg.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–100 of 100:

```text
    1 | ---
    2 | # Dir package installation method
    3 | 
    4 | - block:  ## run_once: true
    5 |     - name: upgrade | Stat directory installation package
    6 |       stat:
    7 |         path: "{{ scale_install_directory_pkg_path }}"
    8 |       register: scale_install_dirpkg
    9 | 
   10 |     - name: upgrade | Check directory installation package
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
   26 | - name: upgrade | Stat extracted packages
   27 |   stat:
   28 |     path: "{{ scale_extracted_path + '/' + scale_install_directory_pkg_path | basename }}"
   29 |   register: scale_install_gpfs_packagedir
   30 | 
   31 | #
   32 | # Copy installation directory package to default
   33 | #
   34 | - block:
   35 |     - name: upgrade | Copy installation package to node
   36 |       copy:
   37 |         src: "{{ scale_install_directory_pkg_path }}"
   38 |         dest: "{{ scale_extracted_path }}"
   39 |         mode: a+x
   40 | 
   41 | - name: upgrade | Extract installation package
   42 |   set_fact:
   43 |     dir_path: "{{ scale_extracted_path + '/' + scale_install_directory_pkg_path | basename }}"
   44 | 
   45 | - name: upgrade | gpfs base path
   46 |   set_fact:
   47 |     scale_gpfs_path_url: "{{ dir_path }}"
   48 |   when: scale_install_directory_pkg_path is defined
   49 | 
   50 | #
   51 | # Find Zimon collector
   52 | #
   53 | - block:  ## when: host is defined as a gui node
   54 |     #
   55 |     # Find GPFS gpfs.collector
   56 |     #
   57 |     - name: upgrade | Find gpfs.collector (gpfs.collector) package
   58 |       find:
   59 |         paths: "{{ scale_gpfs_path_url }}"
   60 |         patterns: gpfs.gss.pmcollector*.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}*
   61 |       register: scale_install_gpfs_collector
   62 | 
   63 |     - name: upgrade | Check valid GPFS (gpfs.collector) package
   64 |       assert:
   65 |         that: scale_install_gpfs_collector.matched > 0
   66 |         msg: >-
   67 |           No GPFS collector (gpfs.gss.collector) package found:
   68 |           "{{ scale_gpfs_path_url }}/gpfs.gss.pmcollector*el{{ ansible_distribution_major_version }}.{{ scale_architecture }}*"
   69 | 
   70 |     - name: upgrade | Add GPFS zimon collector packages to list
   71 |       vars:
   72 |         current_package: "{{ scale_gpfs_path_url }}/{{ item }}"
   73 |       set_fact:
   74 |         scale_install_all_packages: "{{ scale_install_all_packages + [ current_package ] }}"
   75 |       with_items:
   76 |         - "{{ scale_install_gpfs_collector.files.0.path | basename }}"
   77 | 
   78 | #
   79 | # Find GPFS gpfs.gss.pmsensors
   80 | #
   81 | - name: upgrade | Find gpfs.gss.pmsensors (gpfs.gss.pmsensors) package
   82 |   find:
   83 |     paths: "{{ scale_gpfs_path_url }}"
   84 |     patterns: gpfs.gss.pmsensors*el{{ ansible_distribution_major_version }}.{{ scale_architecture }}*
   85 |   register: scale_install_gpfs_pmsensors
   86 | 
   87 | - name: upgrade | Check valid GPFS (gpfs.gss.pmsensors) package
   88 |   assert:
   89 |     that: scale_install_gpfs_pmsensors.matched > 0
   90 |     msg: >-
   91 |       No GPFS pmsensors (gpfs.gss.pmsensors) package found:
   92 |       "{{ scale_gpfs_path_url }}/gpfs.gss.pmsensors*el{{ ansible_distribution_major_version }}.{{ scale_architecture }}*"
   93 | 
   94 | - name: upgrade | Add GPFS zimon sensors packages to list
   95 |   vars:
   96 |     current_package: "{{ scale_gpfs_path_url }}/{{ item }}"
   97 |   set_fact:
   98 |     scale_install_all_packages: "{{ scale_install_all_packages + [ current_package ] }}"
   99 |   with_items:
  100 |     - "{{ scale_install_gpfs_pmsensors.files.0.path | basename }}"
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/perfmon_upgrade`; 13 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: no

roles/perfmon_upgrade/README.md
roles/perfmon_upgrade/defaults/main.yml
roles/perfmon_upgrade/meta/main.yml
roles/perfmon_upgrade/tasks/apt/install.yml
roles/perfmon_upgrade/tasks/install.yml
roles/perfmon_upgrade/tasks/install_dir_pkg.yml
roles/perfmon_upgrade/tasks/install_local_pkg.yml
roles/perfmon_upgrade/tasks/install_remote_pkg.yml
roles/perfmon_upgrade/tasks/install_repository.yml
roles/perfmon_upgrade/tasks/main.yml
roles/perfmon_upgrade/tasks/yum/install.yml
roles/perfmon_upgrade/tasks/zypper/install.yml
roles/perfmon_upgrade/vars/main.yml
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- blocks in file: 3; blocks containing exactly one task: 1
  - block at line 34: block-level keys none; justifying keys none
```

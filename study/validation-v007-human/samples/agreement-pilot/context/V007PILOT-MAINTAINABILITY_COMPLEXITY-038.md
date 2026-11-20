# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-038

- Repository: `ARTbio/GalaxyKickStart`
- Commit: `d04bc40174594a2996a23a1c1b07155de4a694e4`
- Family: Maintainability/complexity
- Rule: `ansibleguard/deprecated-modules`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/galaxy.movedata/tasks/main.yml` (reported anchor line 22)
- Object: `task` `6991d49461a5cba833d67486cedb4e8ba7a8eefc24fcd1f70be834c50c96624e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–38 of 38:

```text
    1 | - name: Ensure galaxy_mutable_data_dir/tmp is owned by galaxy user
    2 |   file: path="{{ galaxy_mutable_data_dir }}/tmp" state=directory owner={{ galaxy_user_name }} group={{ galaxy_user_gid }} recurse=yes
    3 | 
    4 | - name: Check for persistent directory
    5 |   stat: path={{ galaxy_persistent_directory }}
    6 |   register: export_dir_exists
    7 | 
    8 | - name: Check for persistent data
    9 |   stat: path={{ galaxy_persistent_directory }}/exported_dirs.yml
   10 |   register: export_exists
   11 | 
   12 | - name: Check if galaxy config dir should be imported (no .original file)
   13 |   stat: path="{{ galaxy_config_dir }}/.original"
   14 |   register: original
   15 | 
   16 | - include: import.yml
   17 |   when: export_dir_exists.stat.exists and export_exists.stat.exists and not original.stat.exists
   18 | 
   19 | - include: export.yml
   20 |   when: export_dir_exists.stat.exists and not export_exists.stat.exists
   21 | 
   22 | - include: update_yaml_config.yml
   23 |   tags: galaxy_config_files
   24 | 
   25 | - name: Restart supervisor proftpd.
   26 |   supervisorctl: name={{ item }} state=restarted
   27 |   with_items:
   28 |     - proftpd
   29 |   tags: skip_supervisor_start_in_docker
   30 |   when: ansible_distribution_version is version('20.04', '!=')
   31 | 
   32 | # to do: test whether this task is still required
   33 | - name: Start nodejs proxy if installed
   34 |   supervisorctl: name={{ item }} state=started
   35 |   with_items:
   36 |     - "galaxy:galaxy_nodejs_proxy"
   37 |   when: supervisor_manage_ie_proxy
   38 |   ignore_errors: yes
```

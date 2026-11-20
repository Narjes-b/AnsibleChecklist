# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-005

- Repository: `mageops/ansible-infrastructure`
- Commit: `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/cs.deploy/tasks/07-relink-releases.yml` (reported anchor line 16)
- Object: `variable` `40afee3c0356fe3d2fdba411bcaaf243e73231783dca3368d753ccc91fc984e0`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–88 of 88:

```text
    1 | - name: Link previous release
    2 |   file:
    3 |     state: link
    4 |     force: yes
    5 |     dest: "{{ deploy_previous_release_dir }}"
    6 |     src: "{{ deploy_current_release_path }}"
    7 |   become: yes
    8 |   become_user: "{{ deploy_app_user }}"
    9 |   when: deploy_current_release_path is defined
   10 | 
   11 | - name: Link current release
   12 |   file:
   13 |     state: link
   14 |     force: yes
   15 |     dest: "{{ deploy_current_release_dir }}"
   16 |     src: "{{ deploy_next_release_path }}"
   17 |   become: yes
   18 |   become_user: "{{ deploy_app_user }}"
   19 | 
   20 | - name: List current release directories
   21 |   find:
   22 |     file_type: directory
   23 |     follow: no
   24 |     hidden: no
   25 |     recurse: no
   26 |     path: "{{ deploy_releases_dir }}"
   27 |   register: deploy_find_releases
   28 | 
   29 | # The fact `ansible_mount` contains only the root mount while we have tons of others.
   30 | # Cleared fact cache, tried `setup` module, I think this is a bug.
   31 | - name: Find current mounts
   32 |   become: yes
   33 |   become_user: root
   34 |   command: "findmnt --all --output=TARGET --raw --noheadings --notruncate"
   35 |   changed_when: no
   36 |   register: deploy_findmnt_cmd
   37 | 
   38 | - name: Set list directories to remove
   39 |   set_fact:
   40 |     deploy_release_to_remove: >-
   41 |       {{
   42 |         (
   43 |           deploy_find_releases.files
   44 |             | sort(attribute='ctime')
   45 |             | map(attribute='path')
   46 |             | list
   47 |         )[:-deploy_keep_current_releases]
   48 |           | reject('equalto', deploy_next_release_path)
   49 |           | list
   50 |       }}
   51 |     deploy_release_mountpoints_to_unmount: >-
   52 |       {{
   53 |         deploy_findmnt_cmd.stdout_lines
   54 |           | select('match', deploy_releases_dir | regex_escape ~ '.*')
   55 |           | list
   56 |       }}
   57 | 
   58 | # We cannot remove dirs with mounts which may sometimes break deploy
   59 | # if previous broken deploys managed to get stuff mounted; also we
   60 | # have to do `unmount` then `absent` because of some weird ansible bug
   61 | - name: Unmount any mountpoints in the release directories to be removed
   62 |   become: yes
   63 |   become_user: root
   64 |   mount:
   65 |     path: "{{ item[1] }}"
   66 |     state: "{{ item[2] }}"
   67 |   when: item[1].startswith(item[0])
   68 |   with_nested:
   69 |     - "{{ deploy_release_to_remove }}"
   70 |     - "{{ deploy_release_mountpoints_to_unmount }}"
   71 |     - ['unmounted', 'absent']
   72 |   loop_control:
   73 |     label: "{{ item[2] | capitalize }} {{ item[1] }}"
   74 | 
   75 | 
   76 | # Retry release removal as some mounts take some time to finally
   77 | # release the mountpoint directories (S3FS FTW!)
   78 | - name: Remove stale releases
   79 |   become: yes
   80 |   become_user: root
   81 |   file:
   82 |     path: "{{ item }}"
   83 |     state: absent
   84 |   loop: "{{ deploy_release_to_remove }}"
   85 |   register: deploy_remove_release_result
   86 |   retries: 5
   87 |   delay: 10
   88 |   until: deploy_remove_release_result is not failed
```

## Visible variable references

```text
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/01-register-variables.yml:14:    deploy_next_release_path: "{{ deploy_releases_dir }}/{{ deploy_release_id }}"
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/03-install-artifact.yml:61:      '{{ deploy_next_release_path }}'
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/04-link-shared-dirs.yml:4:    path: "{{ (deploy_next_release_path ~ '/' ~ item)|dirname }}"
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/04-link-shared-dirs.yml:15:    path: "{{ deploy_next_release_path }}/{{ item }}"
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/05-ensure-permissions.yml:11:    path: "{{ deploy_next_release_path }}/{{ item }}"
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/05-ensure-permissions.yml:18:    find -L {{ deploy_next_release_path }}/{{ item }}/ {{ deploy_perm_fix_find_opts }} -type d -exec chmod {{ deploy_directory_permissions }} {{ '{}' }} \; &&
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/05-ensure-permissions.yml:19:    find -L {{ deploy_next_release_path }}/{{ item }}/ {{ deploy_perm_fix_find_opts }} -type f -exec chmod {{ deploy_file_permissions }} {{ '{}' }} \;
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/07-relink-releases.yml:16:    src: "{{ deploy_next_release_path }}"
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/07-relink-releases.yml:48:          | reject('equalto', deploy_next_release_path)
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/91-emergency-rename.yml:2:  command: "mv '{{ deploy_next_release_path }}' '{{ deploy_next_release_path }}.failed'"
5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8:roles/cs.deploy/tasks/91-emergency-rename.yml:6:  when: (deploy_next_release_path | default('', true) | string | length) > 0
```

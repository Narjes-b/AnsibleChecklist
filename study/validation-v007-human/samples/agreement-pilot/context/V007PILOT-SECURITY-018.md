# Frozen source context: V007PILOT-SECURITY-018

- Repository: `Linuxfabrik/lfops`
- Commit: `9b51b59db61b87e01cc75adef892e5345a5bf4b1`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/repo_icinga/tasks/Debian.yml` (reported anchor line 4)
- Object: `source_location` `d4803e1c7389716f3515e690363a49e333a3fd9517f4146e7328e87a84eee391`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–44 of 44:

```text
    1 | - block:
    2 | 
    3 |   # https://icinga.com/docs/icinga-2/latest/doc/02-installation/01-Debian/
    4 |   - name: 'curl https://packages.icinga.com/icinga.key --output /tmp/ansible.icinga.key'
    5 |     ansible.builtin.get_url:
    6 |       url: 'https://packages.icinga.com/icinga.key'
    7 |       dest: '/tmp/ansible.icinga.key'
    8 |       mode: 0o644
    9 |     delegate_to: 'localhost'
   10 |     become: false
   11 |     changed_when: false # not an actual config change on the server
   12 |     check_mode: false # run task even if `--check` is specified
   13 | 
   14 |   - name: 'copy /tmp/ansible.icinga.key to remote host'
   15 |     ansible.builtin.copy:
   16 |       src: '/tmp/ansible.icinga.key'
   17 |       dest: '/etc/apt/keyrings/icinga.asc' # use asc for ASCII-armored keys
   18 |       owner: 'root'
   19 |       group: 'root'
   20 |       mode: 0o644
   21 | 
   22 |   - name: 'deploy the repo file (mirror: {{ repo_icinga__mirror_url | default("") }})'
   23 |     ansible.builtin.template:
   24 |       backup: true
   25 |       src: 'etc/apt/sources.list.d/packages_icinga_com_debian.list.j2'
   26 |       dest: '/etc/apt/sources.list.d/packages_icinga_com_{{ ansible_facts["distribution"] | lower }}.list'
   27 |       owner: 'root'
   28 |       group: 'root'
   29 |       mode: 0o644
   30 | 
   31 |   - name: 'Remove rpmnew / rpmsave (and Debian equivalents)'
   32 |     ansible.builtin.include_role:
   33 |       name: 'shared'
   34 |       tasks_from: 'remove-rpmnew-rpmsave.yml'
   35 |     vars:
   36 |       shared__remove_rpmnew_rpmsave_config_file: '/etc/apt/sources.list.d/packages_icinga_com_{{ ansible_facts["distribution"] | lower }}.list'
   37 | 
   38 |   - name: 'apt update # update the cache'
   39 |     ansible.builtin.apt:
   40 |       update_cache: true
   41 |     changed_when: false # refreshing the package cache is not a config change
   42 | 
   43 |   tags:
   44 |     - 'repo_icinga'
```

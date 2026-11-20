# Frozen source context: V007PILOT-SECURITY-049

- Repository: `dfroberg/cluster`
- Commit: `7bc521db65db986a2deef35ea955704bb0621dbd`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `provision/ansible/docker/roles/apps.docker/tasks/wikijs.yml` (reported anchor line 2)
- Object: `source_location` `4a7611d894afd6c8ae76b91a4119a9846011fc08e214fa1fd7da1d4571370927`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–31 of 31:

```text
    1 | ---
    2 | - name: Create wikijs directories
    3 |   ansible.builtin.file:
    4 |     path: "{{ item }}"
    5 |     state: directory
    6 |     owner: "{{ ansible_user }}"
    7 |     group: users
    8 |     mode: 0777
    9 |   loop:
   10 |     - "{{ docker_base_dir }}/wikijs"
   11 |     - "{{ wikijs_data_dir }}"
   12 |     - "{{ wikijs_data_dir }}/config"
   13 |     - "{{ wikijs_data_dir }}/data"
   14 |     - "{{ wikijs_data_dir }}/logs"
   15 | 
   16 | - block:
   17 |     - name: Create wikijs docker compose file
   18 |       ansible.builtin.template:
   19 |         src: wikijs/docker-compose.yml.j2
   20 |         dest: "{{ docker_base_dir }}/wikijs/docker-compose.yml"
   21 |         owner: "{{ ansible_user }}"
   22 |         group: users
   23 |         mode: 0775
   24 |     - name: Create wikijs systemd service file
   25 |       ansible.builtin.template:
   26 |         src: "docker-compose@.service.j2"
   27 |         dest: "/etc/systemd/system/docker-compose@wikijs.service"
   28 |         mode: 0644
   29 |       vars:
   30 |         condition_path_is_mount_point: "{{ wikijs_data_dir }}"
   31 |   notify: Restart wikijs
```

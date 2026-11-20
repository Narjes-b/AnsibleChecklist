# Frozen source context: V007PILOT2-STYLE_POLICY-007

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: style_policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `playbooks/tigerdata.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`playbooks/tigerdata.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–86 of 86:

```text
    1 | ---
    2 | # by default this playbook runs in the staging environment
    3 | # to run in production, pass '-e runtime_env=production'
    4 | # to run in qa, pass '-e runtime_env=qa'
    5 | - name: build the tigerdata site
    6 |   hosts: tigerdata_{{ runtime_env | default('staging') }}
    7 |   remote_user: pulsys
    8 |   become: true
    9 |   vars_files:
   10 |     - ../group_vars/tigerdata/vault.yml
   11 |     - ../group_vars/tigerdata/common.yml
   12 |     - ../group_vars/tigerdata/{{ runtime_env | default('staging') }}.yml
   13 |   roles:
   14 |     - role: mailcatcher
   15 |     - role: ruby_app
   16 |     - role: redis
   17 |     - role: sidekiq_worker
   18 |     - role: otel_collector
   19 |       tags: otel
   20 |     - role: beyla
   21 |       tags: otel
   22 | 
   23 |   tasks:
   24 |     - name: install nfs-common
   25 |       ansible.builtin.apt:
   26 |         name: "nfs-common"
   27 |         state: present
   28 |         update_cache: true
   29 | 
   30 |     - name:  add fqdn for idmapping
   31 |       ansible.builtin.lineinfile:
   32 |         path: /etc/idmapd.conf
   33 |         insertbefore: '# Domain = localdomain'
   34 |         line: "Domain = {{ nfs_host_server }}"
   35 |         state: present
   36 | 
   37 |     - name:  enable id_mapping
   38 |       ansible.builtin.lineinfile:
   39 |         path: /etc/default/nfs-common
   40 |         regexp: '^NEED_IDMAPD='
   41 |         line: NEED_IDMAPD=yes
   42 | 
   43 |     - name:  add fqdn for idmapping
   44 |       ansible.builtin.lineinfile:
   45 |         path: /etc/idmapd.conf
   46 |         insertbefore: '# Domain = localdomain'
   47 |         line: "Domain = {{ nfs_host_server }}"
   48 |         state: present
   49 | 
   50 |     - name: Ensure the presence of nfs mount
   51 |       ansible.posix.mount:
   52 |         src: "{{ nfs_server }}:/var/nfs/tigerdata"
   53 |         path: "/mnt/nfs/tigerdata"
   54 |         state: mounted
   55 |         fstype: nfs
   56 |         opts: rw,sync,hard
   57 |       become: true
   58 |   pre_tasks:
   59 |     - name: update cache
   60 |       ansible.builtin.apt:
   61 |         update_cache: true
   62 |         cache_valid_time: 600
   63 | 
   64 |   post_tasks:
   65 |     - name: restart nginx
   66 |       service:
   67 |         name: nginx
   68 |         state: restarted
   69 |     - name: Update stringio
   70 |       ansible.builtin.command: "gem update stringio"
   71 |       become: true
   72 |       become_user: root
   73 | 
   74 |     - name: Copy department file to the server
   75 |       ansible.builtin.copy:
   76 |         src: ../group_vars/tigerdata/PeopleSoft-Departments.csv
   77 |         dest: "/opt/{{ rails_app_directory }}/shared/departments.csv"
   78 |         owner: deploy
   79 |         group: deploy
   80 |         mode: u=rw,g=r,o=r
   81 |       tags:
   82 |         - department_config
   83 | 
   84 |     - name: send information to slack
   85 |       ansible.builtin.include_tasks:
   86 |         file: utils/slack_tasks_end_of_playbook.yml
```

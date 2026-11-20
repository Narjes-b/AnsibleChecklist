# Frozen source context: V007PILOT-STRUCTURE_REUSE-028

- Repository: `Princeton-CDH/cdh-ansible`
- Commit: `8fc536c88cbc18d048418263ecc64a9b1c339922`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/configure_crontab/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `d324b64c05c7736c03903ee67ca6b675c620ee277e9ec542075d33c079a704dd`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–55 of 55:

```text
    1 | - name: Configure cron jobs
    2 |   when: inventory_hostname == cronjob_host
    3 |   tags:
    4 |     - crontab
    5 |   block:
    6 |   - name: "Configure crontab — special times"
    7 |     cron:
    8 |       name: "{{ item.name }}"
    9 |       special_time: "{{ item.special_time }}"
   10 |       job: "{{ item.job }}"
   11 |       user: "{{ deploy_user }}"
   12 |       state: "{{ item.state | default('present') }}"
   13 |     with_items:   # only include items with special time defined
   14 |       "{{ crontab | selectattr('special_time', 'defined') | list }}"
   15 |   # non-special time cron jobs
   16 |   - name: "Configure crontab — scheduled"
   17 |     cron:
   18 |       name: "{{ item.name }}"
   19 |       minute: "{{ item.minute | default('*') }}"
   20 |       hour: "{{ item.hour | default('*')}}"
   21 |       day: "{{ item.day | default('*')}}"
   22 |       weekday: "{{ item.weekday | default('*')}}"
   23 |       month: "{{ item.month | default('*')}}"
   24 |       job: "{{ item.job }}"
   25 |       user: "{{ deploy_user }}"
   26 |       state: "{{ item.state | default('present') }}"
   27 |     with_items:   # only include items with special time NOT set
   28 |       "{{ crontab | selectattr('special_time', 'undefined') | list }}"
   29 | 
   30 |   - name: Ensure bin directory exists.
   31 |     file:
   32 |       path: "/home/{{ deploy_user }}/bin"
   33 |       state: directory
   34 |       mode: 0700
   35 |       owner: "{{ deploy_user }}"
   36 | 
   37 |   - name: Set group ownership for bin directory
   38 |     file:
   39 |       path: "/home/{{ deploy_user }}/bin"
   40 |       group: "{{ deploy_user }}"
   41 | 
   42 |   - name: Ensure cron wrapper script is present
   43 |     copy:
   44 |       src: "files/cron-wrapper"
   45 |       dest: "/home/{{ deploy_user }}/bin/cron-wrapper"
   46 |       mode: 0700
   47 |       owner: "{{ deploy_user }}"
   48 | 
   49 |   - name: Set group ownership for cron wrapper script
   50 |     file:
   51 |       path: "/home/{{ deploy_user }}/bin/cron-wrapper"
   52 |       group: "{{ deploy_user }}"
   53 | 
   54 |   rescue:
   55 |     - include_tasks: roles/create_deployment/tasks/fail.yml
```

## Frozen tracked paths in the relevant role/scope

```text
roles/configure_crontab/files/cron-wrapper
roles/configure_crontab/tasks/main.yml
```

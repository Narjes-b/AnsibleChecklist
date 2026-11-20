# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-043

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/roles/ipt/tasks/main.yml` (reported anchor line 42)
- Object: `source_location` `c86d4249f889525eb742929bb52b629ba4545f48acd68fa791b0ec18ca1c5529`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–48 of 48:

```text
    1 | - include_tasks: ../../apache_vhost/tasks/main.yml
    2 |   vars:
    3 |     context_path: '{{ ipt_context_path }}'
    4 |     hostname: '{{ ipt_hostname }}'
    5 |   tags:
    6 |     - ipt
    7 |     - apache_vhost
    8 |     - deploy
    9 |   when: not webserver_nginx
   10 | 
   11 | - name: add nginx vhost if configured
   12 |   include_role:
   13 |     name: nginx_vhost
   14 |   vars:
   15 |     appname: "ipt"
   16 |     hostname: "{{ ipt_hostname }}"
   17 |     context_path: "{{ ipt_context_path }}"
   18 |   tags:
   19 |     - nginx_vhost
   20 |     - deploy
   21 |     - ipt
   22 |   when: webserver_nginx | bool 
   23 | 
   24 | - include_tasks: ../../tomcat_deploy/tasks/main.yml
   25 |   vars:
   26 |     war_url: '{{ ipt_war_url }}'
   27 |     context_path: '{{ipt_context_path}}'
   28 |     hostname: '{{ ipt_hostname }}'
   29 |   tags:
   30 |     - ipt
   31 |     - tomcat_vhost
   32 |     - deploy
   33 | 
   34 | - name: ensure ipt data directory exists
   35 |   file: path={{item}} state=directory mode=0775
   36 |   with_items:
   37 |     - "{{data_dir}}/ipt"
   38 |   tags:
   39 |     - ipt
   40 |     - ipt_data_dir    
   41 | 
   42 | - name: set data ownership [all data is owned by tomcat]
   43 |   file: path={{data_dir}}/{{item}} owner={{tomcat_user}} group={{tomcat_user}} recurse=true
   44 |   with_items:
   45 |     - ipt 
   46 |   tags:
   47 |     - ipt
   48 |     - ipt_data_dir    
```

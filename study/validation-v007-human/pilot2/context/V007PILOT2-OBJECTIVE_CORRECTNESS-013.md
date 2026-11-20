# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-013

- Repository: `mageops/ansible-infrastructure`
- Commit: `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`
- Family: objective_correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `site.maintenance.blackfire.yml` (reported anchor line 38)
- Flagged construct: not named by the finding; the anchor line 38 lies in the task at line 38, name `Blackfire profile with empty cache`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–59 of 59:

```text
    1 | - hosts: localhost
    2 |   connection: local
    3 |   become: no
    4 |   tasks:
    5 |     - name: Get list of EC2 instances
    6 |       ec2_instance_info:
    7 |         region: "{{ aws_region }}"
    8 |         filters:
    9 |           "tag:Role": "app"
   10 |           "tag:Project": "{{ mageops_project }}"
   11 |           "tag:Environment": "{{ mageops_environment }}"
   12 |       register: _aws_ec2
   13 |     - name: Add servers to app_servers
   14 |       add_host:
   15 |         groups:  app_servers
   16 |         host: "{{ item }}"
   17 |       with_items: "{{ _aws_ec2|json_query('instances[].public_ip_address')}}"
   18 |   vars_files:
   19 |       - vars/app/env.yml
   20 |       - vars/aws/env.yml
   21 | 
   22 | - hosts: "app_servers"
   23 |   tasks:
   24 |       - name: Flush cache
   25 |         become: yes
   26 |         become_user: "{{ magento_user }}"
   27 |         command: "bin/magento cache:flush"
   28 |         args:
   29 |             chdir: "{{ magento_live_release_dir }}"
   30 |   vars_files:
   31 |       - vars/app/env.yml
   32 |       - vars/aws/env.yml
   33 | 
   34 | - hosts: localhost
   35 |   connection: local
   36 |   become: no
   37 |   tasks:
   38 |       - name: Blackfire profile with empty cache
   39 |         shell: "blackfire --json curl --samples=1 --metadata='app={{ mageops_app_name }}' --metadata='cache=no' {{ magento_base_url }}"
   40 |         register: tmp_blackfire_out_nocache
   41 |         failed_when: false
   42 |       - name: Link to profile
   43 |         debug:
   44 |           var: (tmp_blackfire_out_nocache.stdout | from_json)._links.graph_url
   45 |       - name: Blackfire profile selected pages with Magento cache
   46 |         shell: "blackfire --json curl --metadata='app={{ mageops_app_name }}' --metadata='cache=yes' {{ item }}"
   47 |         with_items: "{{ blackfire_urls + blackfire_extra_urls | default([]) }}"
   48 |         register: tmp_blackfire_out_cache
   49 |       - name: Store links to profiles
   50 |         template:
   51 |           src: templates/vars/blackfire_profiles.j2
   52 |           dest: vars/generated/blackfire_profiles.yml
   53 |           force: yes
   54 |   vars_files:
   55 |       - vars/app/env.yml
   56 |       - vars/aws/env.yml
   57 |   vars:
   58 |     blackfire_urls:
   59 |       - "{{ magento_base_url }}"
```

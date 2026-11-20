# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-019

- Repository: `cfpb/aurora`
- Commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Family: objective_correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `deploy/roles/logstash-config/tasks/main.yml` (reported anchor line 62)
- Flagged construct: task `set default admin permissions on log folders`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–69 of 69:

```text
    1 | ---
    2 | - name: Setup logstash-courier input
    3 |   template:
    4 |     src: 01-logstash-courier-input.conf
    5 |     dest: /etc/logstash/conf.d/01-logstash-courier-input.conf
    6 |   when: install_logstash
    7 |   notify:
    8 |     - restart logstash
    9 | 
   10 | - name: Setup syslog filter
   11 |   template:
   12 |     src: 10-syslog.conf
   13 |     dest: /etc/logstash/conf.d/10-syslog.conf
   14 |   notify:
   15 |     - restart logstash
   16 | 
   17 | #- name: Setup Elasticsearch filter
   18 | #  template:
   19 | #    src: 20-elasticsearch-input.conf.j2
   20 | #    dest: /etc/logstash/conf.d/20-elasticsearch-input.conf
   21 | 
   22 | - name: Setup elasticsearch output
   23 |   template:
   24 |     src: "{{ logstash_es_output_file }}"
   25 |     dest: /etc/logstash/conf.d/30-elasticsearch-output.conf
   26 |   notify:
   27 |     - restart logstash
   28 | 
   29 | - name: Add custom filters
   30 |   copy:
   31 |     dest: "/etc/logstash/conf.d/{{ item.name }}"
   32 |     content: "{{ item.content }}"
   33 |     mode: 0644
   34 |   with_items: "{{ logstash_filters }}"
   35 | 
   36 | - name: Ensure permissions are correct
   37 |   shell: "chmod 644 /etc/logstash/conf.d/*"
   38 |   notify:
   39 |     - restart logstash
   40 | 
   41 | - name: Test Logstash configuration
   42 |   shell: /opt/logstash/bin/logstash --configtest
   43 |   register: logstash_configtest
   44 | 
   45 | - name: Ensure logstash is started
   46 |   service:
   47 |     name: logstash
   48 |     state: started
   49 |     enabled: yes
   50 | 
   51 | - name: Set recursive admin permissions on log folders
   52 |   acl:
   53 |     path: "{{ item }}"
   54 |     entity: "{{ restricted_group_name }}"
   55 |     etype: group
   56 |     permissions: rX
   57 |     recursive: yes
   58 |     state: present
   59 |   with_items: "{{ logstash_log_file_locations }}"
   60 | 
   61 | - name: Set default admin permissions on log folders
   62 |   acl:
   63 |     path: "{{ item }}"
   64 |     entity: "{{ restricted_group_name }}"
   65 |     etype: group
   66 |     permissions: rX
   67 |     default: yes
   68 |     state: present
   69 |   with_items: "{{ logstash_log_file_locations }}"
```

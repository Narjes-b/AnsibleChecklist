# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-011

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: objective_correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `vagrant/provisioning/roles/snowbound-app/tasks/main.yml` (reported anchor line 24)
- Flagged construct: not named by the finding; the anchor line 24 lies in the task at line 24, name `Delete all but last 5 backups`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–121 of 121:

```text
    1 | - name: set JAVA_HOME
    2 |   become: yes
    3 |   become_user: "snowbound"
    4 |   blockinfile:
    5 |     path: "{{ root_folder }}/app/snowbound/bin/setenv.sh"
    6 |     marker: "# {mark} ANSIBLE MANAGED BLOCK - JAVA_HOME"
    7 |     block: |
    8 |       export JAVA_HOME="{{ '/usr/lib/jvm/java-1.8.0-openjdk' if snowbound_vendor_version == '4.10' else '/usr/lib/jvm/java-11-openjdk' }}"
    9 | 
   10 | - name: see if war files exist
   11 |   become: yes
   12 |   become_user: snowbound
   13 |   stat:
   14 |     path: "{{ root_folder }}/app/snowbound/webapps/VirtualViewerJavaHTML5.war"
   15 |   register: war_file
   16 | 
   17 | - name: stop snowbound
   18 |   become: yes
   19 |   systemd:
   20 |     name: snowbound
   21 |     state: stopped
   22 |   when: war_file.stat.exists
   23 | 
   24 | - name: Delete all but last 5 backups
   25 |   become: yes
   26 |   become_user: snowbound
   27 |   shell: ls -atp | grep "VirtualViewerJavaHTML5.war.*.backup" | tail -n +6 | xargs -d '\n' -r rm -rf
   28 |   args:
   29 |     chdir: "{{ root_folder }}/app/snowbound/webapps/"
   30 |   when: war_file.stat.exists
   31 | 
   32 | - name: backup war files
   33 |   become: yes
   34 |   become_user: snowbound
   35 |   shell: mv {{ root_folder }}/app/snowbound/webapps/VirtualViewerJavaHTML5.war {{ root_folder }}/app/snowbound/webapps/VirtualViewerJavaHTML5.war.{{ ansible_date_time.iso8601 }}.backup
   36 |   when: war_file.stat.exists
   37 | 
   38 | - name: download VirtualViewer war file (if using GitHub)
   39 |   include_tasks: "{{ role_path }}/../common/tasks/download.yml"
   40 |   args:
   41 |     apply:
   42 |       vars:
   43 |         item: 
   44 |           name: VirtualViewer war file
   45 |           dest: "{{ root_folder }}/tmp/snowbound/snowbound-integration-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war"
   46 |           owner: snowbound
   47 |           url: https://github.com/ArkCase/arkcase-dependencies/releases/download/{{ snowbound_arkcase_version }}/VirtualViewerJavaHTML5-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war
   48 |   when: snowbound_retrieve_strategy == "github"
   49 |   register: snowbound_war
   50 | 
   51 | - name: download VirtualViewer war file (if using sftp)
   52 |   become: yes
   53 |   become_user: snowbound
   54 |   command: sshpass -e sftp -o StrictHostKeyChecking\=no -o UserKnownHostsFile\=/dev/null {{ sftp_arkcase_user }}@{{ sftp_service_base_url }}:{{ sftp_arkcase_folder }}/snowbound-integration-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war
   55 |   args:
   56 |     chdir: "{{ root_folder }}/tmp/snowbound"
   57 |   environment:
   58 |     SSHPASS: "{{ sftp_arkcase_password }}"
   59 |   when: snowbound_retrieve_strategy == "sftp"
   60 | 
   61 | - name: copy war file to install folder (this will tell us if it actually changed)
   62 |   become: yes
   63 |   become_user: snowbound
   64 |   copy:
   65 |     remote_src: yes
   66 |     src: "{{ root_folder }}/tmp/snowbound/snowbound-integration-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war"
   67 |     dest: "{{ root_folder }}/install/snowbound/snowbound-integration-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war"
   68 |     force: yes
   69 |   register: snowbound_war
   70 | 
   71 | - name: expand the WEB-INF/web.xml file
   72 |   become: yes
   73 |   become_user: snowbound
   74 |   command: unzip -o snowbound-integration-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war WEB-INF/web.xml
   75 |   args:
   76 |     chdir: "{{ root_folder }}/install/snowbound"
   77 |   when: snowbound_war is changed
   78 | 
   79 | - name: fix the WEB-INF/web.xml file
   80 |   become: yes
   81 |   become_user: snowbound
   82 |   replace:
   83 |     path: "{{ root_folder }}/install/snowbound/WEB-INF/web.xml"
   84 |     regexp: "{{ item.regexp }}"
   85 |     replace: "{{ item.replace }}"
   86 |   loop:
   87 |     - regexp: "https://acm-snowbound:8443"
   88 |       replace: "https://{{ snowbound_host }}"
   89 |     - regexp: "https://acm-arkcase:8843"
   90 |       replace: "https://{{ arkcase_host_name }}:8843"
   91 |     - regexp: '\$\{snowbound_host_port\}'
   92 |       replace: "https://{{ snowbound_host }}"
   93 |     - regexp: '\$\{arkcase_host_port\}'
   94 |       replace: "https://{{ arkcase_host_name }}:8843"
   95 |   register: web_xml
   96 |   when: snowbound_war is changed
   97 | 
   98 | - name: update snowbound.war with updated web.xml
   99 |   become: yes
  100 |   become_user: snowbound
  101 |   command: zip -r snowbound-integration-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war WEB-INF
  102 |   args:
  103 |     chdir: "{{ root_folder }}/install/snowbound"
  104 |   when: web_xml is changed
  105 | 
  106 | - name: Update Snowbound war file
  107 |   become: yes
  108 |   become_user: snowbound
  109 |   copy:
  110 |     remote_src: yes
  111 |     src: "{{ root_folder }}/install/snowbound/snowbound-integration-{{ snowbound_vendor_version }}{{ snowbound_arkcase_version_formatted }}.war"
  112 |     dest: "{{ root_folder }}/app/snowbound/webapps/VirtualViewerJavaHTML5.war"
  113 |     force: yes
  114 |   register: snowbound_war_copied
  115 | 
  116 | - name: start Snowbound
  117 |   become: yes
  118 |   systemd:
  119 |     name: snowbound
  120 |     state: restarted
  121 |   when: snowbound_war_copied is changed or web_xml is changed
```

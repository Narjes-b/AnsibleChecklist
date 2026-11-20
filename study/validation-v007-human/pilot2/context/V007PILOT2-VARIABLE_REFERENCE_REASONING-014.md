# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-014

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `vagrant/provisioning/roles/arkcase-interactive-reports/tasks/main.yml` (reported anchor line 58)
- Flagged construct: variable `arkcase_configuration_version_formatted`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–183 of 183:

```text
    1 | - name: List the data sources that already exist
    2 |   become: true
    3 |   become_user: pentaho
    4 |   ansible.builtin.command:
    5 |     cmd: 'wget --no-check-certificate -O {{ root_folder }}/install/pentaho/datasources-list.json --user={{ arkcase_admin_user }} --password "{{ arkcase_admin_password }}" https://{{ internal_host }}:2002/pentaho/plugin/data-access/api/datasource/jdbc/connection'
    6 |   changed_when: false
    7 | 
    8 | - name: Read the list of data sources
    9 |   become: true
   10 |   become_user: pentaho
   11 |   ansible.builtin.command: cat {{ root_folder }}/install/pentaho/datasources-list.json
   12 |   register: data_source_list
   13 |   changed_when: false
   14 | 
   15 | - name: File to post to Pentaho to create the data source
   16 |   become: true
   17 |   become_user: pentaho
   18 |   template:
   19 |     src: put_connection.json
   20 |     dest: "{{ root_folder }}/install/pentaho/put_connection.json"
   21 |   when: not '"MariaDB Local"' in data_source_list.stdout
   22 | 
   23 | # the ansible uri module causes a timeout for some reason but wget works fine
   24 | - name: Create the ArkCase JDBC data source for interactive reports
   25 |   ansible.builtin.command:
   26 |     cmd: 'wget --no-check-certificate --user={{ arkcase_admin_user }} --password "{{ arkcase_admin_password }}" --post-file {{ root_folder }}/install/pentaho/put_connection.json --header="Content-Type: application/json" https://{{ internal_host }}:2002/pentaho/plugin/data-access/api/connection/add'
   27 |   register: create_datasource_rest_call
   28 |   when: not '"MariaDB Local"' in data_source_list.stdout
   29 | 
   30 | - name: Check if keep alive report exists
   31 |   ansible.builtin.command:
   32 |     cmd: 'curl -k -v -u {{ arkcase_admin_user }}:{{ arkcase_admin_password }} https://{{ external_host }}/pentaho/api/scheduler/getJobs'
   33 |   register: scheduled_jobs_out
   34 | 
   35 | - name: Copy keep alive files to /tmp
   36 |   copy:
   37 |     src: "{{ item.src }}"
   38 |     dest: "{{ item.dest }}"
   39 |   with_items:
   40 |     - { src: 'DBConnectionDS.xmi', dest: '/tmp' }
   41 |     - { src: 'DBKeepAlive.prpti.zip', dest: '/tmp' }
   42 |     - { src: 'DBKeepAliveJob.xml', dest: '/tmp' }
   43 |   when: '"KeepAliveJob" not in scheduled_jobs_out.stdout'
   44 | 
   45 | - name: Deploy keep alive interactive reports datasource
   46 |   ansible.builtin.command: "{{ root_folder }}/app/pentaho/pentaho-server/import-export.sh --import --url=https://{{ pentaho_host }}:2002/pentaho --username={{ arkcase_admin_user }} --password='{{ arkcase_admin_password }}' --resource-type=DATASOURCE --datasource-type=METADATA --metadata-domain-id='DBConnectionDS' --file-path='/tmp/DBConnectionDS.xmi' --permission=true --overwrite=true --retainOwnership=true"
   47 |   when: '"KeepAliveJob" not in scheduled_jobs_out.stdout'
   48 | 
   49 | - name: Deploy keep alive interactive report
   50 |   ansible.builtin.command: "{{ root_folder }}/app/pentaho/pentaho-server/import-export.sh --import --url=https://{{ internal_host }}:2002/pentaho --username={{ arkcase_admin_user }} --password='{{ arkcase_admin_password }}' --charset=UTF-8 --path=/public --file-path='/tmp/DBKeepAlive.prpti.zip'"
   51 |   when: '"KeepAliveJob" not in scheduled_jobs_out.stdout'
   52 | 
   53 | - name: Schedule execution of keep alive report on every 30 min to keep connection alive
   54 |   ansible.builtin.command:
   55 |     cmd: 'curl -k -v -H "Content-Type: application/xml" --data @/tmp/DBKeepAliveJob.xml -X POST -u {{ arkcase_admin_user }}:{{ arkcase_admin_password }} https://{{ external_host }}/pentaho/api/scheduler/job'
   56 |   when: '"KeepAliveJob" not in scheduled_jobs_out.stdout'
   57 | 
   58 | - name: Download configuration (if using sftp, and no extension is configured)
   59 |   become: true
   60 |   become_user: arkcase
   61 |   ansible.builtin.command: sshpass -e sftp -o StrictHostKeyChecking\=no -o UserKnownHostsFile\=/dev/null {{ sftp_arkcase_user }}@{{ sftp_service_base_url }}:{{ sftp_arkcase_folder }}/arkcase-config-{{ arkcase_configuration_classifier }}{{ arkcase_configuration_version_formatted }}.zip
   62 |   args:
   63 |     chdir: "{{ root_folder }}/install/arkcase"
   64 |   environment:
   65 |     SSHPASS: "{{ sftp_arkcase_password }}"
   66 |   when: arkcase_retrieve_strategy == "sftp" and not arkcase_extension_install|bool and pentaho_host != internal_host
   67 | 
   68 | - name: Set extension config file name (extension id)
   69 |   set_fact:
   70 |     extension_config_file_name: "arkcase-config-{{ arkcase_extension_id }}{{ arkcase_extension_version_formatted }}.zip"
   71 |   when: arkcase_extension_id is defined and pentaho_host != internal_host
   72 | 
   73 | - name: Set extension config file name (no extension id)
   74 |   set_fact:
   75 |     extension_config_file_name: "arkcase-config{{ arkcase_extension_version }}.zip"
   76 |   when: not arkcase_extension_id is defined and pentaho_host != internal_host
   77 | 
   78 | - name: Download extension configuration (if configured)
   79 |   become: true
   80 |   become_user: arkcase
   81 |   ansible.builtin.command: sshpass -e sftp -o StrictHostKeyChecking\=no -o UserKnownHostsFile\=/dev/null {{ sftp_extension_user }}@{{ sftp_service_base_url }}:{{ sftp_extension_folder }}/{{ extension_config_file_name }}
   82 |   args:
   83 |     chdir: "{{ root_folder }}/install/arkcase"
   84 |   environment:
   85 |     SSHPASS: "{{ sftp_extension_password }}"
   86 |   when: arkcase_retrieve_strategy == "sftp" and arkcase_extension_install|bool and pentaho_host != internal_host
   87 | 
   88 | - name: Download configuration (if using GitHub)
   89 |   include_tasks: "{{ role_path }}/../common/tasks/download.yml"
   90 |   loop:
   91 |     - name: ArkCase configuration
   92 |       dest: "{{ root_folder }}/install/arkcase/arkcase-config.zip"
   93 |       owner: arkcase
   94 |       url: https://github.com/ArkCase/.arkcase/archive/arkcase-{{ arkcase_version }}.zip
   95 |   when: arkcase_retrieve_strategy == "github" and pentaho_host != internal_host
   96 | 
   97 | - name: Rename extension config zip to common file name
   98 |   become: true
   99 |   become_user: arkcase
  100 |   ansible.builtin.command: mv {{ root_folder }}/install/arkcase/{{ extension_config_file_name }} {{ root_folder }}/install/arkcase/arkcase-config.zip
  101 |   when: arkcase_retrieve_strategy == "sftp" and arkcase_extension_install | bool and not extension_config_file_name  == "arkcase-config.zip" and pentaho_host != internal_host
  102 | 
  103 | - name: Format config version
  104 |   set_fact:
  105 |     arkcase_configuration_version_formatted: "{{ '-' ~ arkcase_configuration_version if arkcase_configuration_version != '' else '' }}"
  106 | 
  107 | - name: Rename core config zip to common file name
  108 |   become: true
  109 |   become_user: arkcase
  110 |   ansible.builtin.command: mv {{ root_folder }}/install/arkcase/arkcase-config-{{ arkcase_configuration_classifier }}{{ arkcase_configuration_version_formatted }}.zip {{ root_folder }}/install/arkcase/arkcase-config.zip
  111 |   when: arkcase_retrieve_strategy == "sftp" and not arkcase_extension_install|bool and pentaho_host != internal_host
  112 | 
  113 | - name: Unzip the configuration files
  114 |   become: true
  115 |   become_user: arkcase
  116 |   unarchive:
  117 |     remote_src: true
  118 |     src: "{{ root_folder }}/install/arkcase/arkcase-config.zip"
  119 |     dest: "/home/arkcase/.arkcase"
  120 |     creates: "/home/arkcase/.arkcase/acm/conf.yml"
  121 |   register: arkcase_config_unzipped
  122 |   when: pentaho_host != internal_host
  123 | 
  124 | - name: Find interactive reports datasources in configuration
  125 |   become: true
  126 |   become_user: arkcase
  127 |   find:
  128 |     paths: /home/arkcase/.arkcase/acm/reports/interactive/datasources
  129 |     patterns: '*.xmi'
  130 |     recurse: false
  131 |   register: interactive_reports_datasources
  132 | 
  133 | - name: Install interactive reports datasources
  134 |   become: true
  135 |   become_user: arkcase
  136 |   ansible.builtin.command: "{{ root_folder }}/app/pentaho/pentaho-server/import-export.sh --import --url=https://{{ pentaho_host }}:2002/pentaho --username={{ arkcase_admin_user }} --password='{{ arkcase_admin_password }}' --resource-type=DATASOURCE --datasource-type=METADATA --metadata-domain-id='{{ item.path | basename | splitext | first }}' --file-path='{{ item.path }}' --permission=true --overwrite=true --retainOwnership=true"
  137 |   with_items: "{{ interactive_reports_datasources.files }}"
  138 |   register: datasource_install
  139 |   failed_when: "'Import was successful' not in datasource_install.stdout"
  140 | 
  141 | - name: Check if foia or core variant
  142 |   become: true
  143 |   stat:
  144 |     path: /home/arkcase/.arkcase/acm/acm-config-server-repo/arkcase-foia.yaml
  145 |   register: arkcase_foia_yaml
  146 | 
  147 | - name: Set reports folder
  148 |   set_fact:
  149 |     reports_folder: "{{ 'foia' if arkcase_foia_yaml.stat.exists == true else 'arkcase' }}"
  150 | 
  151 | - name: Find interactive reports in configuration
  152 |   become: true
  153 |   become_user: arkcase
  154 |   find:
  155 |     paths: /home/arkcase/.arkcase/acm/reports/interactive/reports
  156 |     patterns: '*.zip'
  157 |     recurse: false
  158 |   register: interactive_reports
  159 | 
  160 | - name: Install interactive reports from configuration
  161 |   become: true
  162 |   become_user: arkcase
  163 |   ansible.builtin.command: "{{ root_folder }}/app/pentaho/pentaho-server/import-export.sh --import --url=https://{{ internal_host }}:2002/pentaho --username={{ arkcase_admin_user }} --password='{{ arkcase_admin_password }}' --charset=UTF-8 --path=/public/{{ reports_folder }} --file-path='{{ item.path }}' --permission=true --overwrite=true --retainOwnership=true"
  164 |   with_items: "{{ interactive_reports.files }}"
  165 |   register: interactive_install
  166 |   failed_when: "'Import was successful' not in interactive_install.stdout"
  167 | 
  168 | - name: Find static reports folder in configuration
  169 |   become: true
  170 |   become_user: arkcase
  171 |   find:
  172 |     paths: /home/arkcase/.arkcase/acm/reports/static/reports
  173 |     patterns: '*.prpt'
  174 |     recurse: true
  175 |   register: static_reports
  176 | 
  177 | - name: Install static reports from configuration
  178 |   become: true
  179 |   become_user: arkcase
  180 |   ansible.builtin.command: "{{ root_folder }}/app/pentaho/pentaho-server/import-export.sh --import --url=https://{{ internal_host }}:2002/pentaho --username={{ arkcase_admin_user }} --password='{{ arkcase_admin_password }}' --charset=UTF-8 --path=/public/{{ item.path | dirname | regex_replace('.*\\/', '') }} --file-path='{{ item.path }}' --permission=true --overwrite=true --retainOwnership=true"
  181 |   with_items: "{{ static_reports.files }}"
  182 |   register: static_install
  183 |   failed_when: "'Import was successful' not in static_install.stdout"
```

## Visible variable references

```text
Whole-word search for `arkcase_configuration_version_formatted`: 6 matches in 2 files; 2 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
vagrant/provisioning/roles/arkcase-app/tasks/main.yml:259:    arkcase_configuration_version_formatted: "{{ '-' ~ arkcase_configuration_version if arkcase_configuration_version != '' else '' }}"
vagrant/provisioning/roles/arkcase-interactive-reports/tasks/main.yml:105:    arkcase_configuration_version_formatted: "{{ '-' ~ arkcase_configuration_version if arkcase_configuration_version != '' else '' }}"

Other references:
vagrant/provisioning/roles/arkcase-app/tasks/main.yml:278:  command: sshpass -e sftp -o StrictHostKeyChecking\=no -o UserKnownHostsFile\=/dev/null {{ sftp_arkcase_user }}@{{ sftp_service_base_url }}:{{ sftp_arkcase_folder }}/arkcase-config-{{ arkcase_configuration_classifier }}{{ arkcase_configuration_version_formatted }}.zip
vagrant/provisioning/roles/arkcase-app/tasks/main.yml:288:  command: mv {{ root_folder }}/install/arkcase/arkcase-config-{{ arkcase_configuration_classifier }}{{ arkcase_configuration_version_formatted }}.zip {{ root_folder }}/install/arkcase/arkcase-config.zip
vagrant/provisioning/roles/arkcase-interactive-reports/tasks/main.yml:61:  ansible.builtin.command: sshpass -e sftp -o StrictHostKeyChecking\=no -o UserKnownHostsFile\=/dev/null {{ sftp_arkcase_user }}@{{ sftp_service_base_url }}:{{ sftp_arkcase_folder }}/arkcase-config-{{ arkcase_configuration_classifier }}{{ arkcase_configuration_version_formatted }}.zip
vagrant/provisioning/roles/arkcase-interactive-reports/tasks/main.yml:110:  ansible.builtin.command: mv {{ root_folder }}/install/arkcase/arkcase-config-{{ arkcase_configuration_classifier }}{{ arkcase_configuration_version_formatted }}.zip {{ root_folder }}/install/arkcase/arkcase-config.zip
```

# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-020

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/overriding-facts`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `vagrant/provisioning/roles/solr-custom-plugin/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `007198974248a71ca648d646ae11036b559f7c25e59b882fea969b605002de34`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–152 of 152:

```text
    1 | - name: create custom solr plugin library directory
    2 |   become: yes
    3 |   become_user: solr
    4 |   file:
    5 |     path: "{{ root_folder }}/app/solr/contrib/arkcase/lib/"
    6 |     state: directory
    7 |   when: enable_solr_snippets | default(false)
    8 | 
    9 | - name: set flag if this should configure the Signed jar
   10 |   set_fact:
   11 |     use_signed_plugin:
   12 |     when:
   13 |     - ark_solr_custom_jar_sig is defined
   14 |     - ark_solr_custom_jar_sig|length >0
   15 |     - enable_solr_snippets
   16 | 
   17 | - name: set Plugin PEM file for jar signing (with custom PEM)
   18 |   set_fact:
   19 |     plugin_pem_file: "{{ solr_plugin_pem_file }}"
   20 |     when:
   21 |       - solr_plugin_pem_file is defined
   22 |       - solr_plugin_pem_file|length > 0
   23 | 
   24 | - name: set plugin PEM file for Jar signing (use default PEM)
   25 |   set_fact:
   26 |     plugin_pem_file: "/etc/tls/private/arkcase-root.pem"
   27 |     when: solr_plugin_pem_file is undefined or (solr_plugin_pem_file|length == 0)
   28 | 
   29 | - name: create public key for signing Solr plugin jar (jar sig must be provided)
   30 |   become: yes
   31 |   command: openssl rsa -in {{ plugin_pem_file | default('/etc/tls/private/arkcase-root.pem') }} -pubout -outform DER -out {{ root_folder }}/common/solr_plugin_key.der
   32 |   when: use_signed_plugin
   33 | 
   34 | - name: Create key directory to Zookeeper
   35 |   become: yes
   36 |   command: '{{ root_folder }}/app/zookeeper/bin/zkCli.sh create "/keys"'
   37 |   when: use_signed_plugin | default(false)
   38 | 
   39 | - name: Create key/exe directory to Zookeeper
   40 |   become: yes
   41 |   command: '{{ root_folder }}/app/zookeeper/bin/zkCli.sh create "/keys/exe"'
   42 |   when: use_signed_plugin | default(false)
   43 | 
   44 | - name: Add Solr Plugin Public key to Zookeeper
   45 |   become: yes
   46 |   command: '{{ root_folder }}/app/zookeeper/bin/zkCli.sh create /keys/exe/pub_plugin_key.der {{ root_folder }}/common/solr_plugin_key.der'
   47 |   when: use_signed_plugin | default(false)
   48 | 
   49 | - name: add arkSolrCustomizations.jar when Snippets are enabled
   50 |   become: yes
   51 |   become_user: solr
   52 |   copy:
   53 |     src: arkSolrCustomizations.jar
   54 |     dest: "{{ root_folder }}/app/solr/contrib/arkcase/lib/arkSolrCustomizations.jar"
   55 |     mode: "0644"
   56 |     checksum: "{{ ark_solr_customizations_jar_checksum }}"
   57 |   when: "enable_solr_snippets | default(false)"
   58 | 
   59 | - name: add arkSolrCustomizations.jar location to solrconfig.xml
   60 |   become: yes
   61 |   become_user: solr
   62 |   ansible.builtin.lineinfile:
   63 |     path: "{{ root_folder }}/app/solr/server/solr/configsets/arkcase/conf/solrconfig.xml"
   64 |     backup: true
   65 |     line: '  <lib dir="${solr.install.dir:../../../..}/contrib/arkcase/lib" regex=".*\.jar" />'
   66 |     insertbefore: " <!-- an exact 'path' can be used instead of a 'dir' to specify a"
   67 |   when: "enable_solr_snippets | default(false)"
   68 | 
   69 | - name: read current solr service
   70 |   become: yes
   71 |   command: cat /etc/systemd/system/solr.service
   72 |   register: solr_service_file
   73 |   changed_when: false
   74 | 
   75 | - name: enable runtime libs with Solr
   76 |   become: yes
   77 |   replace:
   78 |     backup: yes
   79 |     path: /etc/systemd/system/solr.service
   80 |     regexp: "/app/solr/bin/solr start"
   81 |     replace: "/app/solr/bin/solr start -a -Denable.runtime.lib=true"
   82 |   when: "'-a -Denable.runtime.lib=true' not in solr_service_file.stdout"
   83 |   register: systemd_solr_updated
   84 | 
   85 | - name: reload daemon files if needed
   86 |   become: yes
   87 |   command: systemctl daemon-reload
   88 |   when: systemd_solr_updated is changed
   89 | 
   90 | - name: restart Solr if needed
   91 |   become: yes
   92 |   systemd:
   93 |     name: solr
   94 |     state: restarted
   95 |   when: systemd_solr_updated is changed
   96 | 
   97 | - name: wait for Solr to come back, if it was restarted
   98 |   wait_for:
   99 |     port: 8983
  100 |     delay: 15
  101 |     timeout: 300
  102 |   when: systemd_solr_updated is changed
  103 | 
  104 | - name: Add arkSolrCustomizations.jar to the .system blob (required for Solr Cloud mode)
  105 |   ansible.builtin.command:
  106 |     cmd: >
  107 |       curl -X POST -H 'Content-Type: application/octet-stream' --data-binary @roles/files/arkSolrCustomizations.jar --insecure https://{{ internal_host }}:{{ solr_port | default('8983') }}/solr/.system/blob/arkSolrCustomizations
  108 |   when: enable_solr_snippets | default(false)
  109 | 
  110 | - name: Confirm arkSolrCustomizations.jar has been added to the .system blob
  111 |   ansible.builtin.command:
  112 |     cmd: >
  113 |       curl --insecure https://{{ internal_host }}:{{ solr_port | default('8983') }}/solr/.system/blob?omitHeader=true
  114 |   when: enable_solr_snippets | default(false)
  115 | 
  116 | - name: Debug signature
  117 |   debug:
  118 |     msg: "ark_solr_custom_jar_sig == {{ ark_solr_custom_jar_sig }}"
  119 |   when: use_signed_plugin | default(false)
  120 | 
  121 | - name: Enable signed arkSolrCustomizations.jar as a runtime lib
  122 |   ansible.builtin.command:
  123 |     cmd: >
  124 |       curl --insecure https://{{ internal_host }}:{{ solr_port | default('8983') }}/solr/acmAdvancedSearch/config -H 'Content-type:application/json' -d '{   "add-runtimelib": { "name":"arkSolrCustomizations", "version":1, "sha1": {{ ark_solr_customizations_jar_checksum }}, "sig": {{ ark_solr_custom_jar_sig }} } }'
  125 |   when: use_signed_plugin | default(false)
  126 | 
  127 | - name: Enable arkSolrCustomizations.jar as a runtime lib without sig value
  128 |   ansible.builtin.command:
  129 |     cmd: >
  130 |       curl --insecure https://{{ internal_host }}:{{ solr_port | default('8983') }}/solr/acmAdvancedSearch/config -H 'Content-type:application/json' -d '{   "add-runtimelib": { "name":"arkSolrCustomizations", "version":1, "sha1": {{ ark_solr_customizations_jar_checksum }} } }'
  131 |   when: use_signed_plugin is undefined or (not use_signed_plugin)
  132 | 
  133 | - name: update schema.xml to use the custom tokenizer
  134 |   become: yes
  135 |   replace:
  136 |     backup: yes
  137 |     path: "{{ root_folder }}/app/solr/server/solr/configsets/arkcase/conf/schema.xml"
  138 |     regexp: 'class="solr.PatternTokenizerFactory"'
  139 |     replace: 'class="com.armedia.solr.tokenizers.ArkPatternTokenizerFactory"'
  140 |   when: enable_solr_snippets | default(false)
  141 | 
  142 | - name: upload configuration file
  143 |   become: yes
  144 |   become_user: solr
  145 |   shell: "{{ root_folder }}/app/solr/bin/solr zk upconfig localhost:2182 -n arkcaseConfig -d {{ root_folder }}/app/solr/server/solr/configsets/arkcase"
  146 |   when: enable_solr_cloud is defined and enable_solr_cloud
  147 | 
  148 | - name: restart Solr again
  149 |   become: yes
  150 |   systemd:
  151 |     name: solr
  152 |     state: restarted
```

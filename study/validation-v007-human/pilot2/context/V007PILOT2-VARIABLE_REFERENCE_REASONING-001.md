# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-001

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/missing-bool-filters`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `ansible/roles/common/tasks/setfacts.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`ansible/roles/common/tasks/setfacts.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–374 of 374:

```text
    1 | - name: show ansible versions
    2 |   debug: msg="You are using Ansible {{ ansible_version.full }} on {{ansible_os_family}}. The current supported version for ala-install is {{ supported_ansible_version.full }}."
    3 | 
    4 | - name: set container virtualisation types where snap can't mount squashfs
    5 |   set_fact:
    6 |     snap_unsupported_virt_types: ['lxc', 'docker', 'podman', 'container', 'systemd-nspawn', 'openvz']
    7 |   tags:
    8 |     - setfacts
    9 | 
   10 | # - name: check the ansible version
   11 | #   pause: prompt="You are not using the supported version of Ansible. The supported version is {{ supported_ansible_version.full }}. You are using {{ ansible_version.full }}. Proceed at your own risk. Press enter to continue"
   12 | #   when: supported_ansible_version.major != ansible_version.major or supported_ansible_version.minor != ansible_version.minor
   13 | #   tags:
   14 | #     - version_check
   15 | 
   16 | - name: set ubuntu-14.04 variables
   17 |   set_fact:
   18 |     libtcnative: "libtcnative-1"
   19 |     tomcat_package: "tomcat7"
   20 |     tomcat_user: "tomcat7"
   21 |     tomcat: "tomcat7"
   22 |     tomcat_conf: "/etc/default/tomcat7"
   23 |     tomcat_conf_dir: "/etc/tomcat7"
   24 |     tomcat_log_dir: "/var/log/tomcat7"
   25 |     apache: "apache2"
   26 |     nginx: "nginx"
   27 |     postfix: "postfix"
   28 |     mysql_service: "mysql"
   29 |     mysql: "mysql-server-5.5"
   30 |     cassandra_yaml: "/etc/cassandra/cassandra.yaml"
   31 |     cassandra_user: "cassandra"
   32 |     python_software_properties: "python-software-properties"
   33 |     tomcat_dir: "/var/lib/tomcat7"
   34 |     tomcat_webapps: "/var/lib/tomat7/webapps/"
   35 |     use_openjdk8: false
   36 |     use_zulu8: True
   37 |     psycopg2_package: "python-psycopg2"
   38 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "14.04"
   39 |   tags:
   40 |     - setfacts
   41 | 
   42 | - name: set ubuntu-16.04 variables
   43 |   set_fact:
   44 |     libtcnative: "libtcnative-1"
   45 |     tomcat_package: "tomcat7"
   46 |     tomcat_user: "tomcat7"
   47 |     tomcat: "tomcat7"
   48 |     tomcat_conf: "/etc/default/tomcat7"
   49 |     tomcat_conf_dir: "/etc/tomcat7"
   50 |     tomcat_log_dir: "/var/log/tomcat7"
   51 |     apache: "apache2"
   52 |     nginx: "nginx"
   53 |     postfix: "postfix"
   54 |     mysql_service: "mysql"
   55 |     mysql: "mysql-server-5.7"
   56 |     cassandra_yaml: "/etc/cassandra/cassandra.yaml"
   57 |     cassandra_user: "cassandra"
   58 |     python_software_properties: "python-software-properties"
   59 |     tomcat_dir: "/var/lib/tomcat7"
   60 |     tomcat_webapps: "/var/lib/tomcat7/webapps/"
   61 | #    use_openjdk8: true
   62 | #    use_zulu8: False
   63 |     psycopg2_package: "python3-psycopg2"
   64 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "16.04"
   65 |   tags:
   66 |     - setfacts
   67 | 
   68 | # Allows switching back to tomcat7, which is available but not fully supported for Ubuntu-18.04
   69 | - name: set ubuntu-18.04 variables - overrides
   70 |   set_fact:
   71 |     tomcat: "{{ tomcat | default('tomcat8') }}"
   72 | #    use_openjdk8: "{{ use_openjdk8 | default('True') }}"
   73 | #    use_openjdk11: "{{ use_openjdk11 | default('False') }}"
   74 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "18.04"
   75 |   tags:
   76 |   - setfacts
   77 | 
   78 | - name: set ubuntu-18.04 variables
   79 |   set_fact:
   80 |     libtcnative: "libtcnative-1"
   81 |     tomcat_package: "{{ tomcat }}"
   82 |     tomcat_user: "{{ tomcat_user | default(tomcat) }}"
   83 |     tomcat_conf: "/etc/default/{{ tomcat }}"
   84 |     tomcat_conf_dir: "/etc/{{ tomcat }}"
   85 |     tomcat_log_dir: "/var/log/{{ tomcat }}"
   86 |     apache: "apache2"
   87 |     nginx: "nginx"
   88 |     postfix: "postfix"
   89 |     mysql_service: "mysql"
   90 |     mysql: "mysql-server-5.7"
   91 |     cassandra_yaml: "/etc/cassandra/cassandra.yaml"
   92 |     cassandra_user: "cassandra"
   93 |     python_software_properties: "python3-software-properties"
   94 |     tomcat_dir: "/var/lib/{{ tomcat }}"
   95 |     tomcat_webapps: "/var/lib/{{ tomcat }}/webapps/"
   96 |     mongodb_version: "{{ mongodb_version | default(5.0) | float }}"
   97 |     pg_version: "{{ pg_version | default('9.6') }}"
   98 |     postgis_version: "{{ postgis_version | default('2.4') }}"
   99 |     postgis_version_folder: "{{ postgis_version_folder | default('2.4') }}"
  100 |     postgis_scripts_version: "{{ postgis_scripts_version | default('2.4') }}"
  101 | # openjdk-8 will be removed at some point from Ubuntu-18.04, so we will need to switch to Zulu-8 or similar at that point
  102 | # openjdk-lts on Ubuntu-18.04 is JDK-11, so will not be directly useful by our applications at this point due to lack of testing
  103 | #    use_openjdk8: true
  104 | #    use_zulu8: False
  105 |     psycopg2_package: "python3-psycopg2"
  106 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "18.04"
  107 |   tags:
  108 |     - setfacts
  109 | 
  110 | - name: set ubuntu-20.04 variables - overrides
  111 |   set_fact:
  112 |     tomcat: "{{ tomcat | default('tomcat9') }}"
  113 |     tomcat_user: "{{ tomcat_user | default('tomcat') }}"
  114 | #    use_openjdk8: "{{ use_openjdk8 | default('True') }}"
  115 | #    use_openjdk11: "{{ use_openjdk11 | default('False') }}"
  116 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "20.04"
  117 |   tags:
  118 |   - setfacts
  119 | 
  120 | - name: set ubuntu-20.04 variables
  121 |   set_fact:
  122 |     libtcnative: "libtcnative-1"
  123 |     tomcat_package: "{{ tomcat }}"
  124 |     tomcat_user: "{{ tomcat_user }}"
  125 |     tomcat_conf: "/etc/default/{{ tomcat }}"
  126 |     tomcat_conf_dir: "/etc/{{ tomcat }}"
  127 |     tomcat_log_dir: "/var/log/{{ tomcat }}"
  128 |     apache: "apache2"
  129 |     nginx: "nginx"
  130 |     postfix: "postfix"
  131 |     mysql_service: "mysql"
  132 |     mysql: "mysql-server-8.0"
  133 |     cassandra_yaml: "/etc/cassandra/cassandra.yaml"
  134 |     cassandra_user: "cassandra"
  135 |     python_software_properties: "python3-software-properties"
  136 |     tomcat_dir: "/var/lib/{{ tomcat }}"
  137 |     tomcat_webapps: "/var/lib/{{ tomcat }}/webapps/"
  138 |     mongodb_version: "{{ mongodb_version | default(5.0) | float }}"
  139 |     pg_version: "{{ pg_version | default('10') }}"
  140 |     postgis_version: "{{ postgis_version | default('2.5') }}"
  141 |     postgis_version_folder: "{{ postgis_version_folder | default('2.5') }}"
  142 |     postgis_scripts_version: "{{ postgis_scripts_version | default('2.5') }}"
  143 | # openjdk-8 will be removed at some point from Ubuntu-18.04, so we will need to switch to Zulu-8 or similar at that point
  144 | #    use_openjdk8: true
  145 | #    use_zulu8: False
  146 |     psycopg2_package: "python3-psycopg2"
  147 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "20.04"
  148 |   tags:
  149 |     - setfacts
  150 | 
  151 | - name: set ubuntu-22.04 variables - overrides
  152 |   set_fact:
  153 |     tomcat: "{{ tomcat | default('tomcat9') }}"
  154 |     tomcat_user: "{{ tomcat_user | default('tomcat') }}"
  155 | #    use_openjdk8: "{{ use_openjdk8 | default('True') }}"
  156 | #    use_openjdk11: "{{ use_openjdk11 | default('False') }}"
  157 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "22.04"
  158 |   tags:
  159 |   - setfacts
  160 | 
  161 | - name: set ubuntu-22.04 variables
  162 |   set_fact:
  163 |     libtcnative: "libtcnative-1"
  164 |     tomcat_package: "{{ tomcat }}"
  165 |     tomcat_user: "{{ tomcat_user }}"
  166 |     tomcat_conf: "/etc/default/{{ tomcat }}"
  167 |     tomcat_conf_dir: "/etc/{{ tomcat }}"
  168 |     tomcat_log_dir: "/var/log/{{ tomcat }}"
  169 |     apache: "apache2"
  170 |     nginx: "nginx"
  171 |     postfix: "postfix"
  172 |     mysql_service: "mysql"
  173 |     mysql: "mysql-server-8.0"
  174 |     cassandra_yaml: "/etc/cassandra/cassandra.yaml"
  175 |     cassandra_user: "cassandra"
  176 |     python_software_properties: "python3-software-properties"
  177 |     tomcat_dir: "/var/lib/{{ tomcat }}"
  178 |     tomcat_webapps: "/var/lib/{{ tomcat }}/webapps/"
  179 |     psycopg2_package: "python3-psycopg2"
  180 |     mongodb_version: "{{ mongodb_version | default(8.0) | float }}"
  181 |     pg_version: "{{ pg_version | default('14') }}"
  182 |     postgis_version: "{{ postgis_version | default('3') }}"
  183 |     postgis_version_folder: "{{ postgis_version_folder | default('3') }}"
  184 |     postgis_scripts_version: "{{ postgis_scripts_version | default('3.6') }}"
  185 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "22.04"
  186 |   tags:
  187 |     - setfacts
  188 | 
  189 | - name: set ubuntu-24.04 variables - overrides
  190 |   set_fact:
  191 |     tomcat: "{{ tomcat | default('tomcat10') }}"
  192 |     tomcat_user: "{{ tomcat_user | default('tomcat') }}"
  193 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "24.04"
  194 |   tags:
  195 |   - setfacts
  196 | 
  197 | - name: set ubuntu-24.04 variables
  198 |   set_fact:
  199 |     libtcnative: "libtcnative-1"
  200 |     tomcat_package: "{{ tomcat }}"
  201 |     tomcat_user: "{{ tomcat_user }}"
  202 |     tomcat_conf: "/etc/default/{{ tomcat }}"
  203 |     tomcat_conf_dir: "/etc/{{ tomcat }}"
  204 |     tomcat_log_dir: "/var/log/{{ tomcat }}"
  205 |     apache: "apache2"
  206 |     nginx: "nginx"
  207 |     postfix: "postfix"
  208 |     mysql_service: "mysql"
  209 |     mysql: "mysql-server-8.0"
  210 |     cassandra_yaml: "/etc/cassandra/cassandra.yaml"
  211 |     cassandra_user: "cassandra"
  212 |     python_software_properties: "python3-software-properties"
  213 |     tomcat_dir: "/var/lib/{{ tomcat }}"
  214 |     tomcat_webapps: "/var/lib/{{ tomcat }}/webapps/"
  215 |     psycopg2_package: "python3-psycopg2"
  216 |     mongodb_version: "{{ mongodb_version | default(8.0) | float }}"
  217 |     pg_version: "{{ pg_version | default('16') }}"
  218 |     postgis_version: "{{ postgis_version | default('3') }}"
  219 |     postgis_version_folder: "{{ postgis_version_folder | default('3') }}"
  220 |     postgis_scripts_version: "{{ postgis_scripts_version | default('3.6') }}"
  221 |   when: ansible_os_family == "Debian" and ansible_distribution_version == "24.04"
  222 |   tags:
  223 |     - setfacts
  224 | 
  225 | - name: set java defaults for openjdk21 (amd64)
  226 |   set_fact:
  227 |     java_security_opts: -Dlog4j2.formatMsgNoLookups=true
  228 |     java_home: /usr/lib/jvm/java-21-openjdk-amd64
  229 |   when: use_openjdk21 is defined and use_openjdk21 | bool == True and ansible_architecture != "aarch64"
  230 |   tags:
  231 |     - setfacts
  232 | 
  233 | - name: set java defaults for openjdk21 (arm64)
  234 |   set_fact:
  235 |     java_security_opts: -Dlog4j2.formatMsgNoLookups=true
  236 |     java_home: /usr/lib/jvm/java-21-openjdk-arm64
  237 |   when: use_openjdk21 is defined and use_openjdk21 | bool == True and ansible_architecture == "aarch64"
  238 |   tags:
  239 |     - setfacts
  240 | 
  241 | - name: set java defaults for openjdk17 (amd64)
  242 |   set_fact:
  243 |     java_security_opts: -Dlog4j2.formatMsgNoLookups=true
  244 |     java_home: /usr/lib/jvm/java-17-openjdk-amd64
  245 |   when: use_openjdk17 is defined and use_openjdk17 | bool == True and ansible_architecture != "aarch64"
  246 |   tags:
  247 |     - setfacts
  248 | 
  249 | - name: set java defaults for openjdk17 (arm64)
  250 |   set_fact:
  251 |     java_security_opts: -Dlog4j2.formatMsgNoLookups=true
  252 |     java_home: /usr/lib/jvm/java-17-openjdk-arm64
  253 |   when: use_openjdk17 is defined and use_openjdk17 | bool == True and ansible_architecture == "aarch64"
  254 |   tags:
  255 |     - setfacts
  256 | 
  257 | - name: set java defaults for openjdk11 (amd64)
  258 |   set_fact:
  259 |     java_security_opts: -Dlog4j2.formatMsgNoLookups=true
  260 |     java_home: /usr/lib/jvm/java-11-openjdk-amd64
  261 |   when: use_openjdk11 is defined and use_openjdk11 | bool == True and ansible_architecture != "aarch64"
  262 |   tags:
  263 |     - setfacts
  264 | 
  265 | - name: set java defaults for openjdk11 (arm64)
  266 |   set_fact:
  267 |     java_security_opts: -Dlog4j2.formatMsgNoLookups=true
  268 |     java_home: /usr/lib/jvm/java-11-openjdk-arm64
  269 |   when: use_openjdk11 is defined and use_openjdk11 | bool == True and ansible_architecture == "aarch64"
  270 |   tags:
  271 |     - setfacts
  272 | 
  273 | - name: set java defaults for openjdk8 (amd64)
  274 |   set_fact:
  275 |     java_security_opts: -Djava.security.properties=/etc/java-8-openjdk/security/enableLegacyTLS.security -Dlog4j2.formatMsgNoLookups=true
  276 |     java_home: /usr/lib/jvm/java-8-openjdk-amd64
  277 |   when: use_openjdk8 is defined and use_openjdk8 | bool == True and ansible_architecture != "aarch64"
  278 |   tags:
  279 |     - setfacts
  280 | 
  281 | - name: set java defaults for openjdk8 (arm64)
  282 |   set_fact:
  283 |     java_security_opts: -Djava.security.properties=/etc/java-8-openjdk/security/enableLegacyTLS.security -Dlog4j2.formatMsgNoLookups=true
  284 |     java_home: /usr/lib/jvm/java-8-openjdk-arm64
  285 |   when: use_openjdk8 is defined and use_openjdk8 | bool == True and ansible_architecture == "aarch64"
  286 |   tags:
  287 |     - setfacts
  288 | 
  289 | - name: set java defaults for zulu8
  290 |   set_fact:
  291 |     java_home: /usr/lib/jvm/zulu-8-amd64/jre
  292 |     java_security_opts:
  293 |   when: use_zulu8 is defined and use_zulu8 | bool == True
  294 |   tags:
  295 |     - setfacts
  296 | 
  297 | - name: set name index date
  298 |   set_fact:
  299 |       name_index_date: "{{ nameindex_datestamp | default('latest') }}"
  300 |   tags:
  301 |     - setfacts
  302 | 
  303 | - name: set name data date
  304 |   set_fact:
  305 |       name_data_date: "{{ namedata_datestamp | default('latest') }}"
  306 |   tags:
  307 |     - setfacts
  308 | 
  309 | - name: set name index location with date {{name_index_date}}
  310 |   set_fact:
  311 |     aws_name_indexes_repo: "{{ aws_nameindex_source_url | default('https://s3.amazonaws.com/ala-nameindexes/latest') }}"
  312 |     ala_name_indexes_repo: "{{ ala_nameindex_source_url | default('https://archives.ala.org.au/archives/nameindexes') }}/{{name_index_date}}"
  313 |     ala_name_data_repo: "{{ ala_namedata_source_url | default('https://archives.ala.org.au/archives/nameindexes') }}/{{name_data_date}}"
  314 |   tags:
  315 |     - setfacts    
  316 | 
  317 | - name: using the ALA nexus repository
  318 |   set_fact:
  319 |     maven_repo_base_url: "https://nexus.ala.org.au/repository/"
  320 |     maven_repo_url: "https://nexus.ala.org.au/repository/{{maven_release_dir|default('public')}}"
  321 |     maven_repo_ws_url: "https://nexus.ala.org.au/service/local/artifact/maven/redirect?r={{maven_release_dir | default('public')}}&g={{groupId | default('au.org.ala')}}&a={{artifactId | default('')}}&v={{version | default('')}}&e={{packaging | default('war')}}&c={{classifier | default('')}}"
  322 |   when: use_gbif_nexus is not defined or use_gbif_nexus == "false"
  323 |   tags:
  324 |     - setfacts  
  325 | 
  326 | - name: using the GBIF nexus repository
  327 |   set_fact:
  328 |     maven_repo_base_url: "http://repository.gbif.org/content/groups/"
  329 |     maven_repo_url: "http://repository.gbif.org/content/groups/{{maven_release_dir|default('ala-release')}}"
  330 |     maven_repo_ws_url: "http://repository.gbif.org/service/local/artifact/maven/redirect?r={{maven_release_dir | default('ala-release')}}&g={{groupId | default('au.org.ala')}}&a={{artifactId | default('')}}&v={{version | default('')}}&e={{packaging | default('war')}}&c={{classifier | default('')}}"
  331 |   when: use_gbif_nexus is defined and use_gbif_nexus == "true"
  332 |   tags:
  333 |     - setfacts  
  334 | 
  335 | - name: setup name index and data URLs
  336 |   set_fact:
  337 |     col_namematching_url: "{{aws_name_indexes_repo}}/col_namematching_20160226.tgz"
  338 |     merged_namematching_url: "{{aws_name_indexes_repo}}/merge_namematching.tgz"
  339 |     ala_namematching_url: "{{ala_name_indexes_repo}}/namematching-{{name_index_date}}.tgz"
  340 |   tags:
  341 |     - setfacts    
  342 | 
  343 | - name: setup name sources
  344 |   set_fact:
  345 |     ala_name_sources:
  346 |       - combined
  347 |   tags:
  348 |     - setfacts
  349 | 
  350 | - name: set whether webserver is apache or nginx
  351 |   set_fact:
  352 |     webserver_nginx: "{{ webserver_nginx | default(false) }}"
  353 |   tags:
  354 |     - setfacts
  355 | 
  356 | - name: set exec_jar as default value
  357 |   set_fact:
  358 |     exec_jar: false
  359 |   tags:
  360 |     - setfacts
  361 | 
  362 | - name: set deployment packaging
  363 |   set_fact:
  364 |     exec_jar: true
  365 |   when: packaging is defined and packaging == "jar"
  366 |   tags:
  367 |     - setfacts
  368 | 
  369 | - name: set deployment_type
  370 |   set_fact:
  371 |     deployment_type: "{{ deployment_type | default('vm') }}"
  372 |   tags:
  373 |     - setfacts
  374 |     - properties-file
```

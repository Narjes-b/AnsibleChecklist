# Frozen source context: V007PILOT2-STRUCTURE_REUSE-008

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: structure_reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `vagrant/provisioning/roles/java-corretto-11/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`vagrant/provisioning/roles/java-corretto-11/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–122 of 122:

```text
    1 | - name: Import Amazon Corretto GPG key
    2 |   become: yes
    3 |   ansible.builtin.rpm_key:
    4 |     key: https://yum.corretto.aws/corretto.key
    5 |     state: present
    6 | 
    7 | - name: Install Amazon Corretto 11 from RPM URL
    8 |   become: yes
    9 |   ansible.builtin.yum:
   10 |     name: https://corretto.aws/downloads/latest/amazon-corretto-11-x64-linux-jdk.rpm
   11 |     state: present
   12 | 
   13 | - name: See if the Java truststore exists
   14 |   become: yes
   15 |   ansible.builtin.stat:
   16 |     path: "{{ java_trust_store }}"
   17 |   register: arkcase_ts_stat
   18 |   changed_when: false
   19 | 
   20 | - name: Import server certificates to JDK truststore
   21 |   when: arkcase_ts_stat.stat.exists
   22 |   block:
   23 |     - name: Write Java key store and trust store
   24 |       block:
   25 |         - name: Add JDK 11 certs to Java trust store
   26 |           become: true
   27 |           ansible.builtin.command: keytool -importkeystore -srckeystore /usr/lib/jvm/java-11-amazon-corretto/lib/security/cacerts -srcstorepass changeit -destkeystore "{{ java_trust_store }}" -deststorepass {{ java_trust_store_pass }} -noprompt
   28 |         - name: Add Arkcase server certs to Java 11 trust store
   29 |           become: true
   30 |           ansible.builtin.command: keytool -importkeystore -srckeystore "{{ java_trust_store }}" -srcstorepass {{ java_trust_store_pass }} -destkeystore /usr/lib/jvm/java-11-amazon-corretto/lib/security/cacerts -deststorepass changeit -noprompt
   31 | 
   32 | #Activemq
   33 | 
   34 | - name: set java version
   35 |   become: yes
   36 |   become_user: activemq
   37 |   replace:
   38 |     path: "{{ root_folder }}/app/activemq/bin/linux-x86-64/wrapper.conf"
   39 |     regexp: "^wrapper.java.command=.*"
   40 |     replace: "wrapper.java.command={{ activemq_java_home | default('/usr/lib/jvm/java-11-amazon-corretto') }}/bin/java"
   41 | 
   42 | 
   43 | #Arkcase
   44 | 
   45 | - name: set Java 8 as Java Home (versions below 2023.02)
   46 |   set_fact:
   47 |     java_home_version: "/usr/lib/jvm/java-1.8.0-openjdk"
   48 |   when: arkcase_version != "" and arkcase_version is version('2023.02', '<')
   49 | 
   50 | - name: set Java 11 as Java Home (versions equal and above 2023.02)
   51 |   set_fact:
   52 |     java_home_version: "/usr/lib/jvm/java-11-amazon-corretto"
   53 |   when: arkcase_version == "" or arkcase_version is version('2023.02', '>=')
   54 | 
   55 | - include_tasks: "{{ role_path }}/../tomcat/tasks/main.yml"
   56 |   args:
   57 |     apply:
   58 |       vars:
   59 |         tc:
   60 |           service: arkcase
   61 |           user: arkcase
   62 |           tomcat_home: "{{ root_folder }}/app/arkcase"
   63 |           tls_port: 8843
   64 |           shutdown_port: 4005
   65 |           jmx_remote_port: 40506
   66 |           jmx_rmi_port: 40507
   67 |           http_port: 8080
   68 |           redirect_port: 4443
   69 |           ajp_port: 4009
   70 |           catalina_out: "{{ root_folder }}/log/arkcase/catalina.out"
   71 |           catalina_temp: "{{ root_folder }}/tmp/arkcase"
   72 |           log_folder: "{{ root_folder }}/log/arkcase"
   73 |           java_home: "{{java_home_version}}"
   74 |   register: tomcat_unarchived
   75 | 
   76 | - name: Update JAVA_HOME in config-server.service
   77 |   become: yes
   78 |   ansible.builtin.replace:
   79 |     path: /etc/systemd/system/config-server.service
   80 |     regexp: '^Environment=JAVA_HOME=.*$'
   81 |     replace: 'Environment=JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto'
   82 | 
   83 | - name: Update JAVA_HOME in activemq.service
   84 |   become: yes
   85 |   ansible.builtin.replace:
   86 |     path: /etc/systemd/system/activemq.service
   87 |     regexp: '^Environment=JAVA_HOME=.*$'
   88 |     replace: 'Environment=JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto'
   89 | 
   90 | - name: Reload systemd daemon
   91 |   become: yes
   92 |   ansible.builtin.command: systemctl daemon-reexec
   93 | 
   94 | - name: Restart config-server
   95 |   become: yes
   96 |   ansible.builtin.service:
   97 |     name: config-server
   98 |     state: restarted
   99 | 
  100 | - name: Restart activemq
  101 |   become: yes
  102 |   ansible.builtin.service:
  103 |     name: activemq
  104 |     state: restarted
  105 | 
  106 | - name: Remove Java 11 OpenJDK RPM packages
  107 |   become: yes
  108 |   package:
  109 |     name:
  110 |       - java-11-openjdk
  111 |       - java-11-openjdk-devel
  112 |       - java-11-openjdk-headless
  113 |     state: absent
  114 | 
  115 | - name: Remove residual Java 11 directories
  116 |   become: yes
  117 |   file:
  118 |     path: "{{ item }}"
  119 |     state: absent
  120 |   loop:
  121 |     - /etc/java/java-11-openjdk
  122 |     - /usr/share/doc/java-11-openjdk-11.0.24.0.8-3.el8.x86_64
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `vagrant/provisioning/roles/java-corretto-11`; 4 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: no
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

vagrant/provisioning/roles/java-corretto-11/tasks/main.yml
vagrant/provisioning/roles/java-corretto-11/tests/inventory
vagrant/provisioning/roles/java-corretto-11/tests/test.yml
vagrant/provisioning/roles/java-corretto-11/vars/main.yml
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- blocks in file: 2; blocks containing exactly one task: 1
  - block at line 20: block-level keys ['name', 'when']; justifying keys ['when']
```

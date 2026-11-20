# Frozen source context: V007PILOT-STRUCTURE_REUSE-005

- Repository: `ArkCase/arkcase-ce`
- Commit: `75895cbe09118f02addf4c00fd8e10b8ccddeaa8`
- Family: Structure/reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `vagrant/provisioning/roles/common/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `1133032db3ca56d6955a89705f07a3b984a763c6163a93d597f156efaf8e2917`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–162 of 162:

```text
    1 | - name: System details
    2 |   ansible.builtin.debug:
    3 |     msg: "{{ item }}"
    4 |   with_items:
    5 |     - "{{ ansible_distribution }}"
    6 |     - "{{ ansible_distribution_version }}"
    7 |     - "{{ ansible_distribution_major_version }}"
    8 | 
    9 | - name: Set package names if we are on RHEL 8
   10 |   ansible.builtin.set_fact:
   11 |     pkg_policycoreutils: "policycoreutils-python-utils"
   12 |     pkg_python_setuptools: "python3-setuptools"
   13 |     pkg_python_cryptography: "python3-cryptography"
   14 |   when: ansible_distribution in ["RedHat","Rocky"] and ansible_distribution_major_version == "8"
   15 | 
   16 | - name: Set package names if we are on CentOS 7
   17 |   ansible.builtin.set_fact:
   18 |     pkg_policycoreutils: "policycoreutils-python"
   19 |     pkg_python_setuptools: "python-setuptools"
   20 |     pkg_python_cryptography: "python-cryptography"
   21 |   when: ansible_distribution == "CentOS" and ansible_distribution_major_version == "7"
   22 | 
   23 | - name: Install epel (needed first)
   24 |   become: true
   25 |   command: dnf install -y epel-release
   26 |   when: ansible_distribution == "CentOS" and ansible_distribution_major_version == "7"
   27 | 
   28 | - name: Import Amazon Corretto GPG key
   29 |   become: yes
   30 |   ansible.builtin.rpm_key:
   31 |     key: https://yum.corretto.aws/corretto.key
   32 |     state: present
   33 | 
   34 | - name: Install required packages
   35 |   become: true
   36 |   command: dnf install -y "{{ item }}"
   37 |   loop:
   38 |     - java-1.8.0-openjdk
   39 |     - java-1.8.0-openjdk-devel
   40 |     - "{{ pkg_policycoreutils }}"
   41 |     - zip
   42 |     - unzip
   43 |     - git
   44 |     - net-tools
   45 |     - "@Development Tools"
   46 |     - bzip2
   47 |     - tar
   48 |     - wget
   49 |     - sshpass
   50 |     - python3
   51 |     - python3-pip
   52 |     - "{{ pkg_python_setuptools }}"
   53 |     - "{{ pkg_python_cryptography }}"
   54 |     - https://corretto.aws/downloads/latest/amazon-corretto-11-x64-linux-jdk.rpm
   55 | 
   56 | - name: See if the Java truststore exists
   57 |   become: true
   58 |   ansible.builtin.stat:
   59 |     path: "{{ java_trust_store }}"
   60 |   register: arkcase_ts_stat
   61 |   changed_when: false
   62 | 
   63 | - name: Install firewalld
   64 |   become: true
   65 |   command: dnf install -y firewalld
   66 |   when: enable_firewall is undefined or enable_firewall
   67 | 
   68 | - name: Remove python2-passlib since it breaks solr password setting
   69 |   become: true
   70 |   command: dnf remove -y python2-passlib
   71 | 
   72 | - name: Folder structure for app, data and logs
   73 |   become: true
   74 |   ansible.builtin.file:
   75 |     path: "{{ item }}"
   76 |     state: directory
   77 |   loop:
   78 |     - "{{ root_folder }}"
   79 |     - "{{ root_folder }}/app"
   80 |     - "{{ root_folder }}/data"
   81 |     - "{{ root_folder }}/log"
   82 |     - "{{ root_folder }}/install"
   83 |     - "{{ root_folder }}/common"
   84 |     - "{{ root_folder }}/tmp"
   85 | 
   86 | - name: Check whether I am inside a Docker container
   87 |   ansible.builtin.stat:
   88 |     path: /.dockerenv
   89 |   register: stat_dockerenv_result
   90 | 
   91 | - name: Set hostname
   92 |   become: true
   93 |   ansible.builtin.hostname:
   94 |     name: "{{ internal_host }}"
   95 |   # Don't try to set the hostname when running inside Docker, this is
   96 |   # not possible. Instead, use `--hostname` on the `docker run`
   97 |   # command line.
   98 |   when: not stat_dockerenv_result.stat.exists
   99 | 
  100 | - name: Add to hosts file - {{ internal_host }}
  101 |   become: true
  102 |   ansible.builtin.lineinfile:
  103 |     path: /etc/hosts
  104 |     line: "{{ item }}"
  105 |   loop:
  106 |     - "{{ arkcase_host_address | default('127.0.0.1') }} arkcase-host"
  107 |     - "{{ ansible_default_ipv4.address | default(ansible_all_ipv4_addresses[0]) }} {{ internal_host }}"
  108 |   # Don't try to modify the `/etc/hosts` file when running inside
  109 |   # Docker, this is not possible. Instead, use `--add-host` on the
  110 |   # `docker run` command line.
  111 |   when: not stat_dockerenv_result.stat.exists
  112 | 
  113 | - name: Set timezone to UTC
  114 |   become: true
  115 |   community.general.timezone:
  116 |     name: "{{ time_zone | default('UTC') }}"
  117 | 
  118 | - name: Set default locale to en_US.utf8
  119 |   become: true
  120 |   ansible.builtin.command: localectl set-locale LANG=en_US.utf8
  121 | 
  122 | - name: Run CRON job every day at 1.05 to remove files older than 7 days
  123 |   become: true
  124 |   ansible.builtin.cron:
  125 |     name: "remove_files"
  126 |     user: "root"
  127 |     hour: "1"
  128 |     minute: "5"
  129 |     job: 'find {{ root_folder }}/data/arkcase-home/fileserver -mtime +6 -type f -exec rm {} \;'
  130 |     state: present
  131 | 
  132 | - name: Get the RDS common certifcate
  133 |   become: true
  134 |   ansible.builtin.uri:
  135 |     creates: "{{ root_folder }}/common/rds-ca-2019-root.pem"
  136 |     dest: "{{ root_folder }}/common/rds-ca-2019-root.pem"
  137 |     url: https://s3.amazonaws.com/rds-downloads/rds-ca-2019-root.pem
  138 | 
  139 | - name: See if the Java truststore exists
  140 |   become: true
  141 |   ansible.builtin.stat:
  142 |     path: "{{ java_trust_store }}"
  143 |   register: arkcase_ts_stat
  144 |   changed_when: false
  145 | 
  146 | - name: Import server certificates to JDK truststore
  147 |   when: arkcase_ts_stat.stat.exists
  148 |   block:
  149 |     - name: Write Java key store and trust store
  150 |       block:
  151 |         - name: Add JDK 11 certs to Java trust store
  152 |           become: true
  153 |           ansible.builtin.command: keytool -importkeystore -srckeystore /usr/lib/jvm/java-11-amazon-corretto/lib/security/cacerts -srcstorepass changeit -destkeystore "{{ java_trust_store }}" -deststorepass {{ java_trust_store_pass }} -noprompt
  154 |         - name: Add JDK 8 certs to Java trust store
  155 |           become: true
  156 |           ansible.builtin.command: keytool -importkeystore -srckeystore /usr/lib/jvm/java-1.8.0-openjdk/jre/lib/security/cacerts -srcstorepass changeit -destkeystore "{{ java_trust_store }}" -deststorepass {{ java_trust_store_pass }} -noprompt
  157 |         - name: Add Arkcase server certs to Java 11 trust store
  158 |           become: true
  159 |           ansible.builtin.command: keytool -importkeystore -srckeystore "{{ java_trust_store }}" -srcstorepass {{ java_trust_store_pass }} -destkeystore /usr/lib/jvm/java-11-amazon-corretto/lib/security/cacerts -deststorepass changeit -noprompt
  160 |         - name: Add Arkcase server certs to Java 8 trust store
  161 |           become: true
  162 |           ansible.builtin.command: keytool -importkeystore -srckeystore "{{ java_trust_store }}" -srcstorepass {{ java_trust_store_pass }} -destkeystore /usr/lib/jvm/java-1.8.0-openjdk/jre/lib/security/cacerts -deststorepass changeit -noprompt
```

## Frozen tracked paths in the relevant role/scope

```text
vagrant/provisioning/roles/common/files/requirements.txt
vagrant/provisioning/roles/common/tasks/download.yml
vagrant/provisioning/roles/common/tasks/logrotate.yml
vagrant/provisioning/roles/common/tasks/main.yml
```

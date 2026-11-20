# Frozen source context: V007PILOT-STYLE_POLICY-039

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: Style/policy
- Rule: `ansibleguard/molecule-test-absent`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `jboss-migration-toolkit/roles/jboss-standalone/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `a62a3c908d237fc10b853e17bda1b588bce80eb819020470570fa8beb8b920da`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–97 of 97:

```text
    1 | ---
    2 | - name: Install Java 1.7 and some basic dependencies
    3 |   yum: 
    4 |     name: "{{ item }}"
    5 |     state: present
    6 |   with_items:
    7 |    - unzip
    8 |    - java-1.7.0-openjdk
    9 |    - libselinux-python
   10 |    - libsemanage-python
   11 | 
   12 | - name: Download JBoss from jboss.org
   13 |   get_url: 
   14 |     url: http://download.jboss.org/jbossas/7.1/jboss-as-7.1.1.Final/jboss-as-7.1.1.Final.zip 
   15 |     dest: /opt/jboss-as-7.1.1.Final.zip
   16 | 
   17 | - name: Extract archive
   18 |   unarchive: 
   19 |     dest: /usr/share 
   20 |     src: /opt/jboss-as-7.1.1.Final.zip 
   21 |     creates: /usr/share/jboss-as 
   22 |     copy: no 
   23 | 
   24 |   # Rename the dir to avoid encoding the version in the init script
   25 | - name: Rename install directory
   26 |   command: chdir=/usr/share /bin/mv jboss-as-7.1.1.Final jboss-as creates=/usr/share/jboss-as
   27 | 
   28 | - name: Copying standalone.xml configuration file
   29 |   template: 
   30 |     src: standalone.xml 
   31 |     dest: /usr/share/jboss-as/standalone/configuration/
   32 | #  notify: restart jboss
   33 | 
   34 | - name: Add group "jboss"
   35 |   group: 
   36 |     name: jboss
   37 | 
   38 | - name: Add user "jboss"
   39 |   user: 
   40 |     name: jboss 
   41 |     group: jboss 
   42 |     home: /usr/share/jboss-as
   43 | 
   44 | - name: Change ownership of JBoss installation
   45 |   file: 
   46 |     path: /usr/share/jboss-as/ 
   47 |     owner: jboss 
   48 |     group: jboss 
   49 |     state: directory 
   50 |     recurse: yes
   51 | 
   52 | - name: Copy the init script
   53 |   copy: 
   54 |     src: jboss-as-standalone.sh 
   55 |     dest: /etc/init.d/jboss 
   56 |     mode: 0755
   57 | 
   58 | - name: Workaround for systemd bug
   59 |   shell: service jboss start && chkconfig jboss on
   60 |   ignore_errors: yes
   61 | 
   62 | - name: Enable JBoss to be started at boot
   63 |   service: 
   64 |     name: jboss 
   65 |     enabled: yes 
   66 |     state: started
   67 | 
   68 | - name: deploy iptables rules
   69 |   template: 
   70 |     src: iptables-save 
   71 |     dest: /etc/sysconfig/iptables
   72 |   when: ansible_distribution_major_version != "7" 
   73 | #  notify: restart iptables
   74 | 
   75 | - name: Ensure that firewalld is installed
   76 |   yum: 
   77 |     name: firewalld 
   78 |     state: present
   79 |   when: ansible_distribution_major_version == "7" 
   80 | 
   81 | - name: Ensure that firewalld is started
   82 |   service: 
   83 |     name: firewalld 
   84 |     state: started
   85 |   when: ansible_distribution_major_version == "7" 
   86 | 
   87 | - name: deploy firewalld rules
   88 |   firewalld: 
   89 |     immediate: yes 
   90 |     port: "{{ item }}" 
   91 |     state: enabled 
   92 |     permanent: yes
   93 |   when: ansible_distribution_major_version == "7"
   94 |   with_items:
   95 |   - "{{ http_port }}/tcp"
   96 |   - "{{ https_port }}/tcp"
   97 | 
```

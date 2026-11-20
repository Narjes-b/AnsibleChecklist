# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-025

- Repository: `gdcc/dataverse-ansible`
- Commit: `ae29ce65dd4cddd5187c2bc00aefd319b6bb4484`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/shell-environment-export`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `tasks/dataverse-build.yml` (reported anchor line 29)
- Flagged construct: not named by the finding; the anchor line 29 lies in the task at line 29, name `build warfile without tests and default maven. tail /tmp/dataverse/mvn.out for gory details.`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–80 of 80:

```text
    1 | # datavarse/tasks/dataverse-build.yml
    2 | 
    3 | - name: build warfile
    4 |   debug:
    5 |     msg: '##### BUILD WARFILE #####'
    6 | 
    7 | - ansible.builtin.import_tasks: maven.yml
    8 | 
    9 | - name: get branch_commit
   10 |   shell: 'cd "{{ dataverse.srcdir }}" && git log --oneline | head -1 | awk "{print $1}"'
   11 |   register: bcout
   12 | 
   13 | - set_fact:
   14 |     commit='{{ bcout.stdout.split(" ")[0] }}'
   15 | 
   16 | - set_fact:
   17 |     jacoco_arg=''
   18 | 
   19 | - set_fact:
   20 |     jacoco_arg='-Djacoco.skip.instrument=false'
   21 |   when: dataverse.jacoco.enabled == true
   22 | 
   23 | - name: add branch name, branch_commit to BuildNumber.properties
   24 |   lineinfile:
   25 |     path: "{{ dataverse.srcdir }}/src/main/java/BuildNumber.properties"
   26 |     line: "build.number={{ dataverse_branch }}-{{ commit }}"
   27 |     create: yes
   28 | 
   29 | - name: build warfile without tests and default maven. tail /tmp/dataverse/mvn.out for gory details.
   30 |   shell: "export JAVA_HOME={{ java_home }} && mvn -T 2C clean package -Dmaven.test.skip=true > mvn.out"
   31 |   args:
   32 |     chdir: "{{ dataverse.srcdir }}"
   33 |   when: dataverse.unittests.enabled == false and
   34 |         maven.version == 'default'
   35 |   become: true
   36 |   become_user: '{{ dataverse.payara.user }}'
   37 | 
   38 | - name: build warfile without tests and custom maven. tail /home/dataverse/dataverse/mvn.out for gory details.
   39 |   shell: "source /etc/profile.d/maven.sh && mvn -T 2C clean package -Dmaven.test.skip=true > mvn.out"
   40 |   args:
   41 |     chdir: "{{ dataverse.srcdir }}"
   42 |   when: dataverse.unittests.enabled == false and
   43 |         maven.version != 'default'
   44 |   become: true
   45 |   become_user: '{{ dataverse.payara.user }}'
   46 | 
   47 | - name: build warfile with specified tests. tail /tmp/dataverse/mvn.out for gory details.
   48 |   shell: "mvn {{ dataverse.unittests.argument }} {{ jacoco_arg }} -T 2C clean package > mvn.out"
   49 |   args:
   50 |     chdir: "{{ dataverse.srcdir }}"
   51 |   when: dataverse.unittests.enabled == true and
   52 |         maven.version == 'default'
   53 |   become: true
   54 |   become_user: '{{ dataverse.payara.user }}'
   55 | 
   56 | - name: build warfile with specified tests using custom maven. tail /home/dataverse/dataverse/mvn.out for gory details.
   57 |   shell: "source /etc/profile.d/maven.sh && mvn {{ dataverse.unittests.argument }} {{ jacoco_arg }} -T 2C clean package > mvn.out"
   58 |   args:
   59 |     chdir: "{{ dataverse.srcdir }}"
   60 |   when: dataverse.unittests.enabled == true and
   61 |         maven.version != 'default'
   62 |   become: true
   63 |   become_user: '{{ dataverse.payara.user }}'
   64 | 
   65 | - name: copy warfile over release
   66 |   copy:
   67 |     src: '{{ dataverse.srcdir }}/target/dataverse-{{ dataverse.version }}.war'
   68 |     dest: '/tmp/dvinstall/dataverse.war'
   69 |     owner: root
   70 |     group: root
   71 |     mode: 0644
   72 |     remote_src: yes
   73 | 
   74 | - name: place redeploy script
   75 |   template:
   76 |     src: redeploy.sh.j2
   77 |     dest: '{{ dataverse.srcdir }}/redeploy.sh'
   78 |     owner: root
   79 |     group: root
   80 |     mode: 0755
```

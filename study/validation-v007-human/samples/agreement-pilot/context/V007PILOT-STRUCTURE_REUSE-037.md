# Frozen source context: V007PILOT-STRUCTURE_REUSE-037

- Repository: `gdcc/dataverse-ansible`
- Commit: `ae29ce65dd4cddd5187c2bc00aefd319b6bb4484`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `tasks/prometheus.yml` (reported anchor line 1)
- Object: `source_location` `2b51eea4621fc1ab7a7ea5fb2ca333f6340627c7c71d5b2aa53d16fbcc2834be`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–109 of 109:

```text
    1 | ---
    2 | 
    3 | - name: install prometheus
    4 |   debug:
    5 |     msg: '##### PROMETHEUS #####'
    6 | 
    7 | - ansible.builtin.import_tasks: dataverse-fqdn.yml
    8 | 
    9 | - name: systemd no likey escaped colons
   10 |   set_fact:
   11 |     siteUrl: "{{ siteUrl | regex_replace('\\\\:', ':') }}"
   12 |   tags: grafana
   13 | 
   14 | - debug:
   15 |     msg: "siteUrl is {{ siteUrl }}"
   16 | 
   17 | - name: Put SELinux in permissive mode
   18 |   selinux:
   19 |     policy: targeted
   20 |     state: permissive
   21 | 
   22 | - ansible.builtin.import_tasks: collectd.yml
   23 | 
   24 | - name: add prometheus service account
   25 |   user:
   26 |     name: '{{ prometheus.user }}'
   27 | 
   28 | # firewalld is outside the role scope
   29 | #- name: punch prometheus firewall holes
   30 | #  firewalld:
   31 | #    port: '{{ item }}'
   32 | #    permanent: yes
   33 | #    state: enabled
   34 | #  with_items:
   35 | #  - 9090/tcp
   36 | #  - 9100/tcp
   37 | 
   38 | - name: unarchive won't create directory
   39 |   file:
   40 |     path: '{{ prometheus.root }}'
   41 |     state: directory
   42 |     owner: '{{ prometheus.user }}'
   43 |     mode: '0755'
   44 | 
   45 | - name: install prometheus
   46 |   unarchive:
   47 |     src: '{{ prometheus.url }}'
   48 |     dest: '{{ prometheus.root }}'
   49 |     owner: '{{ prometheus.user }}'
   50 |     remote_src: yes
   51 |     extra_opts: [--strip-components=1]
   52 | 
   53 | - name: copy prometheus config file
   54 |   copy:
   55 |     src: prometheus.yml
   56 |     dest: '{{ prometheus.root }}/prometheus.yml'
   57 |     owner: '{{ prometheus.user }}'
   58 |     mode: 0644
   59 | 
   60 | - name: node_exporter dir must exist
   61 |   file:
   62 |     path: '{{ prometheus.root }}/node_exporter'
   63 |     state: directory
   64 |     owner: '{{ prometheus.user }}'
   65 |     mode: '0755'
   66 | 
   67 | - name: install node_exporter
   68 |   unarchive:
   69 |     src: '{{ prometheus.node_exporter }}'
   70 |     dest: '{{ prometheus.root }}/node_exporter'
   71 |     remote_src: yes
   72 |     extra_opts: [--strip-components=1]
   73 |     
   74 | - name: place prometheus systemd template
   75 |   template:
   76 |     src: prometheus.service.j2
   77 |     dest: /usr/lib/systemd/system/prometheus.service
   78 |     owner: root
   79 |     group: root
   80 |     mode: 0644
   81 | 
   82 | - name: place node_exporter systemd template
   83 |   template:
   84 |     src: node_exporter.service.j2
   85 |     dest: /usr/lib/systemd/system/node_exporter.service
   86 |     owner: root
   87 |     group: root
   88 |     mode: 0644
   89 | 
   90 | - name: reload systemd
   91 |   shell: systemctl daemon-reload
   92 | 
   93 | - name: start and enable prometheus
   94 |   systemd:
   95 |     name: prometheus
   96 |     state: started
   97 |     enabled: yes
   98 | 
   99 | - name: give prometheus a breather
  100 |   pause:
  101 |     seconds: 2
  102 | 
  103 | - name: start and enable node_exporter
  104 |   systemd:
  105 |     name: prometheus
  106 |     state: started
  107 |     enabled: yes
  108 | 
  109 | - ansible.builtin.import_tasks: grafana.yml
```

## Frozen tracked paths in the relevant role/scope

```text
.gitignore
.travis.yml
LICENSE
README.md
Vagrantfile
custom_sampledata/datasets/dataset-finch1.json
custom_sampledata/datasets/dataset-finch2.json
custom_sampledata/datasets/dataset-trees1.xml
custom_sampledata/datasets/finch_datasets.sh
custom_sampledata/dataverses/00_birds
custom_sampledata/dataverses/00_trees
custom_sampledata/dataverses/01_chestnut
custom_sampledata/dataverses/01_finches
custom_sampledata/dataverses/01_sparrows
custom_sampledata/dataverses/01_spruce
custom_sampledata/dataverses/01_wrens
custom_sampledata/files/120745.dta
custom_sampledata/files/1char
custom_sampledata/files/50by1000.dta
custom_sampledata/files/50by1000.dta.zip
custom_sampledata/files/open-source-at-harvard118.dta
custom_sampledata/files/stata13-auto-withstrls.dta
custom_sampledata/files/stata13-auto.dta
custom_sampledata/files/stata14-auto-withstrls.dta
custom_sampledata/files/upload_samplefiles.sh
custom_sampledata/users/chestnut.user
custom_sampledata/users/create-users.sh
custom_sampledata/users/finch.user
custom_sampledata/users/sparrow.user
custom_sampledata/users/spruce.user
custom_sampledata/users/wren.user
dataverse.pb
defaults/main.yml
ec2/README.md
ec2/ec2-create-instance.sh
ec2/ec2-destroy-all.sh
ec2/ec2-list-all.sh
files/00-shib.conf
files/503.html
files/DataCuration.json
files/attribute-map.xml
files/collectd_t.pp
files/collectd_t.te
files/cors.json
files/createsequence.sql
files/dataExplorer.json
files/dataverse-dashboards.yml
files/dataverse-idp-metadata.xml
files/dataverse-previewers.sh
files/grafana-dashboard.json
files/grafana.repo
files/install-mod_shib-to-shibd.sh
files/jmx.conf
files/logging.properties
files/maven.sh
files/mod_shib-to-shibd.te
files/prometheus.conf
files/prometheus.yml
files/sampleusers/1
files/sampleusers/2
files/sampleusers/3
files/sampleusers/4
files/sampleusers/5
files/sampleusers/6
files/shibboleth.centos8.repo
files/shibboleth.rocky8.repo
files/shibboleth.rocky9.repo
files/solr.conf
files/wholetale.json
handlers/main.yml
inventory
meta/main.yml
molecule/default/INSTALL.md
molecule/default/converge.yml
molecule/default/molecule.yml
molecule/default/prepare.yml
molecule/default/verify.yml
site.yml
tasks/ansible-scripts.yml
tasks/aws_cli.yml
tasks/aws_config.yml
tasks/build_guides.yml
tasks/certbot.yml
tasks/check_index_status.yml
tasks/collectd.yml
tasks/custom_metadata_blocks.yml
tasks/custom_sampledata.yml
tasks/dataverse-apache-ssl-pems.yml
tasks/dataverse-apache-ssl.yml
tasks/dataverse-apache.yml
tasks/dataverse-api-testsuite.yml
tasks/dataverse-apitoken.yml
tasks/dataverse-branch.yml
tasks/dataverse-build.yml
tasks/dataverse-counter.yml
tasks/dataverse-externaltools.yml
tasks/dataverse-fqdn.yml
tasks/dataverse-frontend.yml
tasks/dataverse-gui.yml
tasks/dataverse-handlenet.yml
tasks/dataverse-install.yml
tasks/dataverse-installer.yml
tasks/dataverse-languages.yml
tasks/dataverse-licenses.yml
tasks/dataverse-optional-settings.yml
tasks/dataverse-postinstall.yml
tasks/dataverse-prereqs.yml
tasks/dataverse-previewers.yml
tasks/dataverse-required-variables.yml
tasks/dataverse-sampledata-examples.yml
tasks/dataverse-storage.yml
tasks/docker.yml
tasks/extra-certificate-authorities.yml
tasks/fin.yml
tasks/grafana.yml
tasks/jacoco-download.yml
tasks/jacoco-generate_report.yml
tasks/jacoco-instrument.yml
tasks/localstack.yml
tasks/localstack_create.yml
[listing truncated after 120 paths]
```

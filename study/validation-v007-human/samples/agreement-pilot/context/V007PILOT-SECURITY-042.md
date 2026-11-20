# Frozen source context: V007PILOT-SECURITY-042

- Repository: `clusterinthecloud/ansible`
- Commit: `a378fceff7cd03dbd36da1fc4bd5a4ed09270c60`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/monitoring/tasks/master.yml` (reported anchor line 74)
- Object: `source_location` `2adfe8bc2fb30e3a7108e23da4bbd2b47baed7ad5a22d99cf1c572b3e75e6f3e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–196 of 196:

```text
    1 | ---
    2 | 
    3 | - name: Configure mgmt to recieve syslog on UDP and TCP
    4 |   ansible.builtin.replace:
    5 |     path: /etc/rsyslog.conf
    6 |     regexp: "{{ item.regexp }}"
    7 |     replace: "{{ item.replace }}"
    8 |   with_items:
    9 |     - regexp: '#\$ModLoad imudp'
   10 |       replace: '$ModLoad imudp'
   11 |     - regexp: '#\$UDPServerRun 514'
   12 |       replace: '$UDPServerRun 514'
   13 |     - regexp: '#\$ModLoad imtcp'
   14 |       replace: '$ModLoad imtcp'
   15 |     - regexp: '#\$InputTCPServerRun 514'
   16 |       replace: '$InputTCPServerRun 514'
   17 |   notify: Restart rsyslog
   18 | 
   19 | - name: Install influxdb package
   20 |   ansible.builtin.yum:
   21 |     name:
   22 |       - influxdb
   23 |   notify: Restart influxdb
   24 | 
   25 | - name: Enable the influxdb service
   26 |   ansible.builtin.service:
   27 |     name: influxdb
   28 |     state: started
   29 |     enabled: true
   30 | 
   31 | - name: Add Grafana repository
   32 |   ansible.builtin.yum_repository:
   33 |     name: grafana
   34 |     description: Grafana
   35 |     baseurl: https://packages.grafana.com/oss/rpm
   36 |     gpgkey: https://packages.grafana.com/gpg.key
   37 | 
   38 | - name: Install grafana package
   39 |   ansible.builtin.yum:
   40 |     name:
   41 |       - grafana
   42 |   notify: Restart grafana
   43 | 
   44 | - name: Enable the grafana service
   45 |   ansible.builtin.service:
   46 |     name: grafana-server
   47 |     state: started
   48 |     enabled: true
   49 | 
   50 | # TODO move firewalld installation into a separate role
   51 | - name: Install firewalld
   52 |   ansible.builtin.package:
   53 |     name: firewalld
   54 |     state: present
   55 | 
   56 | - name: Install python-firewall
   57 |   ansible.builtin.package:
   58 |     name: python3-firewall
   59 |     state: present
   60 | 
   61 | - name: Start service firewalld
   62 |   ansible.builtin.service:
   63 |     name: firewalld
   64 |     enabled: true
   65 |     state: started
   66 | 
   67 | - name: Open Grafana port in firewall
   68 |   ansible.posix.firewalld:
   69 |     port: 3000/tcp
   70 |     permanent: true
   71 |     state: enabled
   72 |   notify: Restart firewalld
   73 | 
   74 | - name: Check admin password
   75 |   ansible.builtin.uri:
   76 |     url: http://localhost:3000/api/admin/settings
   77 |     user: admin
   78 |     password: "{{ grafana_admin_password }}"
   79 |     force_basic_auth: true
   80 |   ignore_errors: true
   81 |   register: grafana_password
   82 | 
   83 | - name: Set admin password
   84 |   ansible.builtin.uri:
   85 |     url: http://localhost:3000/api/user/password
   86 |     user: admin
   87 |     password: admin
   88 |     force_basic_auth: true
   89 |     method: PUT
   90 |     body_format: json
   91 |     body: '{ "oldPassword": [REDACTED_LITERAL]
   92 |   ignore_errors: '{{ ansible_check_mode }}'
   93 |   when: grafana_password.status =[REDACTED_LITERAL]
   94 | 
   95 | - name: Add grafana password to secrets
   96 |   ansible.builtin.lineinfile:
   97 |     path: /usr/sbin/get_secrets
   98 |     line: echo grafana "{{ grafana_admin_password }}"
   99 | 
  100 | - name: Create influxdb telegraf datasource
  101 |   community.grafana.grafana_datasource:
  102 |     grafana_url: http://localhost:3000
  103 |     grafana_user: admin
  104 |     grafana_password: "{{ grafana_admin_password }}"
  105 |     name: influxdb_telegraf
  106 |     ds_type: influxdb
  107 |     ds_url: http://localhost:8086
  108 |     database: telegraf
  109 |   tags:
  110 |     - molecule-idempotence-notest  # https://github.com/ansible-collections/community.grafana/issues/127
  111 | 
  112 | - name: Install monitor_slurm script
  113 |   ansible.builtin.copy:
  114 |     dest: /usr/local/bin/monitor_slurm
  115 |     content: |
  116 |       #! /bin/bash
  117 |       set -euo pipefail
  118 |       IFS=$'\n\t'
  119 | 
  120 |       data=$(sinfo --noheader --Format=StateLong,Nodes)
  121 | 
  122 |       values=""
  123 | 
  124 |       for i in $data
  125 |       do
  126 |         state=$(echo $i | awk '{print $1}')
  127 |         count=$(echo $i | awk '{print $2}')
  128 |         values+=",${state}=${count}"
  129 |       done
  130 | 
  131 |       if [[ ! -z "${values}" ]]
  132 |       then
  133 |         echo "nodestatuscount ${values:1}"
  134 |       fi
  135 |     mode: a=rx,u+w
  136 | 
  137 | - name: Enable slurm monitoring in influx
  138 |   community.general.ini_file:
  139 |     path: /etc/telegraf/telegraf.conf
  140 |     section: "[inputs.exec]"
  141 |     option: "{{ item.key }}"
  142 |     value: "{{ item.value }}"
  143 |     state: present
  144 |     mode: u=rw,g=r,o=r
  145 |   loop: "{{ keys | dict2items }}"
  146 |   vars:
  147 |     keys:
  148 |       commands: '["/usr/local/bin/monitor_slurm"]'
  149 |       timeout: '"5s"'
  150 |       name_suffix: '"_slurm"'
  151 |       data_format: '"influx"'
  152 |   notify: Restart telegraf
  153 | 
  154 | - name: Create directory for grafana dashboards
  155 |   ansible.builtin.file:
  156 |     path: /etc/citc/grafana
  157 |     state: directory
  158 |     mode: u=rwx,g=rx,o=rx
  159 | 
  160 | - name: Copy in Slurm Grafana dashboard
  161 |   ansible.builtin.template:
  162 |     src: slurm_dashboard.json.j2
  163 |     dest: /etc/citc/grafana/slurm_dashboard.json
  164 |     mode: u=rw,g=r,o=r
  165 | 
  166 | - name: Download Telegraf dashboard
  167 |   ansible.builtin.get_url:
  168 |     url: https://grafana.com/api/dashboards/928/revisions/3/download
  169 |     dest: /etc/citc/grafana/928.json
  170 |     mode: u=rw,g=r,o=r
  171 |   tags:
  172 |     - molecule-idempotence-notest  # We download and then change this file in-place
  173 | 
  174 | - name: Set Influx datasource on dashboard
  175 |   ansible.builtin.replace:
  176 |     path: /etc/citc/grafana/928.json
  177 |     regexp: '\${DS_INFLUXDB_TELEGRAF}'
  178 |     replace: 'influxdb_telegraf'
  179 | 
  180 | - name: Import dashboard
  181 |   ansible.builtin.copy:
  182 |     dest: /etc/grafana/provisioning/dashboards/citc.yaml
  183 |     content: |
  184 |       apiVersion: 1
  185 | 
  186 |       providers:
  187 |       - name: 'default'
  188 |         orgId: 1
  189 |         folder: ''
  190 |         type: file
  191 |         disableDeletion: false
  192 |         updateIntervalSeconds: 10 #how often Grafana will scan for changed dashboards
  193 |         options:
  194 |           path: /etc/citc/grafana
  195 |     mode: u=rw,g=r,o=r
  196 |   notify: Restart grafana
```

# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-020

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: Objective correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/hdfs_configure/tasks/configure.yml` (reported anchor line 152)
- Object: `source_location` `d7c54fb82d893e2a4c3cfdcfdfaa8dee43aff16de632e2892b1610d7a2a29791`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–370 of 370:

```text
    1 | ---
    2 | - name: global_var | Initialize
    3 |   set_fact:
    4 |    scale_hdfs_nodes_list: []
    5 |    scale_hdfs_namenodes_list: []
    6 |    scale_hdfs_datanodes_list: []
    7 |    scale_hdfs_cluster: []
    8 |    hdfs_site_conf_dict: []
    9 |    core_site_conf_dict: []
   10 |    gpfs_site_conf_dict: []
   11 | 
   12 | - name: global_var | initializing scale_hdfs_cluster
   13 |   set_fact:
   14 |     scale_hdfs_cluster: "{{ item }}"
   15 |   delegate_to: localhost
   16 |   run_once: true
   17 | 
   18 | - name: global_var | Collect all HDFS NameNodes
   19 |   set_fact:
   20 |    scale_hdfs_namenodes_list: "{{ scale_hdfs_cluster.namenodes | unique }}"
   21 |   delegate_to: localhost
   22 |   run_once: true
   23 | 
   24 | - name: global_var | Collect all HDFS DataNodes
   25 |   set_fact:
   26 |    scale_hdfs_datanodes_list: "{{ scale_hdfs_cluster.datanodes | unique }}"
   27 |   delegate_to: localhost
   28 |   run_once: true
   29 | 
   30 | - name: global_var | Get HDFS nodes
   31 |   set_fact:
   32 |     scale_hdfs_nodes_list: "{{ scale_hdfs_namenodes_list + scale_hdfs_datanodes_list }}"
   33 | 
   34 | - name: global_var | make unique HDFS nodes
   35 |   set_fact:
   36 |     scale_hdfs_nodes_list: "{{ scale_hdfs_nodes_list | unique }}"
   37 | 
   38 | - name: global_var | Initialize
   39 |   set_fact:
   40 |     namenodes_service: ""
   41 | 
   42 | - block:
   43 |    - name: check | Collect hdfs datadir
   44 |      set_fact:
   45 |       scale_hdfs_datadir: "{{ scale_hdfs_cluster.datadir }}"
   46 |    - name: check | Collect hdfs filesystem
   47 |      set_fact:
   48 |       scale_hdfs_filesystem: "{{ scale_hdfs_cluster.filesystem }}"
   49 |    - name: check | Collect hdfs cluster name
   50 |      set_fact:
   51 |       scale_hdfs_cluster_name: "{{ scale_hdfs_cluster.name }}"
   52 |    - name: check | Collect ces hdfs group
   53 |      set_fact:
   54 |       scale_hdfs_ces_group_name: "hdfs{{ scale_hdfs_cluster.name }}"
   55 |    - name: configure | scale_server node
   56 |      set_fact:
   57 |        scale_server: "{{ scale_hdfs_cluster.namenodes[0] }}"
   58 |    - name: configure |  initialise ces
   59 |      set_fact:
   60 |        scale_free_ces: []
   61 | 
   62 | - name: check | namenode length
   63 |   set_fact:
   64 |     namenodes_length: "{{ scale_hdfs_namenodes_list|length }}"
   65 | 
   66 | - name: check | calculate namenodes services 
   67 |   set_fact:
   68 |      namenodes_service: "{{ namenodes_service }}nn{{ namenode_list }},"
   69 |   with_sequence: count={{ namenodes_length }}
   70 |   when: scale_hdfs_namenodes_list|length > 1
   71 |   loop_control:
   72 |     loop_var: namenode_list
   73 |   delegate_to: localhost
   74 |   run_once: true
   75 | 
   76 | - name:
   77 |   set_fact:
   78 |      namenodes_service: "{{ namenodes_service | regex_replace('\\,$', '') }}"
   79 |   when: scale_hdfs_namenodes_list|length > 1
   80 |   delegate_to: localhost
   81 |   run_once: true
   82 | 
   83 | - name: check | calculate namenodes services
   84 |   set_fact:
   85 |      namenodes_service: 'nn1'
   86 |   when: scale_hdfs_namenodes_list|length == 1
   87 |   delegate_to: localhost
   88 |   run_once: true
   89 | 
   90 | - name: check | Verify existing ces ip
   91 |   shell:
   92 |     cmd: "mmces address list -Y|grep -w {{ scale_hdfs_ces_group_name }}|awk -F: '{print $7}'"
   93 |   register: scale_existing_ces_ip
   94 |   delegate_to: "{{ scale_server }}"
   95 |   run_once: true
   96 | 
   97 | - name: check | Check free ces ip
   98 |   shell:
   99 |    cmd: "mmces address list -Y|awk -F: '(length($9) == 0){print $7}'"
  100 |   register: scale_free_ces
  101 |   delegate_to: "{{ scale_server }}"
  102 |   run_once: true
  103 |   when: scale_existing_ces_ip.stdout | length == 0
  104 | 
  105 | - name: check | Collect hdfs cesip
  106 |   set_fact:
  107 |     scale_hdfs_ces_ip: "{{ scale_free_ces.stdout_lines }}"
  108 |   when:
  109 |     - scale_existing_ces_ip.stdout | length == 0
  110 |     - scale_free_ces.stdout_lines | length > 0
  111 |   delegate_to: "{{ scale_server }}"
  112 |   run_once: true
  113 | 
  114 | - block:
  115 |    - name: check | fetch mountpoint
  116 |      shell: /usr/lpp/mmfs/bin/mmlsfs "{{ scale_hdfs_filesystem }}" -T -Y | grep defaultMountPoint | awk -F':' '{print $9}'
  117 |      register: hdfs_mountpoint
  118 | 
  119 |    - name: check| decode mountpoint
  120 |      command: /usr/lpp/mmfs/bin/mmclidecode "{{ hdfs_mountpoint.stdout }}"
  121 |      register: hdfs_mountpoint_decode
  122 |      when: hdfs_mountpoint.rc == 0
  123 | 
  124 |    - name: check| get mountpoint
  125 |      set_fact:
  126 |        scale_hdfs_mountpoint: "{{ hdfs_mountpoint_decode.stdout }}"
  127 |      when: hdfs_mountpoint_decode.rc == 0
  128 | 
  129 |   run_once: true
  130 |   delegate_to: "{{ scale_server }}"
  131 | 
  132 | - fail:
  133 |     msg: "Failed to fetch mountpoint. "
  134 |   when: hdfs_mountpoint.changed|bool and hdfs_mountpoint.rc != 0 and scale_hdfs_mountpoint|length == 0
  135 | 
  136 | - name: configure | ha_enable_dir
  137 |   shell: "ls {{ scale_hdfs_mountpoint }}/HA-{{ scale_hdfs_cluster.name }}"
  138 |   register: ha_enable_dir
  139 |   failed_when: false
  140 |   ignore_errors: yes
  141 |   run_once: true
  142 |   delegate_to: "{{ scale_server }}"
  143 | 
  144 | - name: configure | Check HDFS ces_group
  145 |   shell: "/usr/lpp/mmfs/bin/mmces address list|grep -w {{ scale_hdfs_ces_group_name }}"
  146 |   register: check_hdfs_ces_group
  147 |   run_once: true
  148 |   delegate_to: "{{ scale_server }}"
  149 |   failed_when: false
  150 |   ignore_errors: yes
  151 | 
  152 | - name: configure | Check Namenodes running status
  153 |   shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs hdfs-nn status | grep 'namenode pid is' | wc -l
  154 |   register: check_hdfs
  155 |   delegate_to: "{{ scale_server }}"
  156 | 
  157 | - name: configure | Check HA
  158 |   set_fact:
  159 |       ha_enabled: "{{ true if scale_hdfs_cluster.namenodes|length > 1 else false }}"
  160 |       ces_hdfs_enabled: "{{ false if check_hdfs.stdout|int != 0 else true }}"
  161 |   run_once: true
  162 |   delegate_to: "{{ scale_server }}"
  163 | 
  164 | - name: "fetch JAVA_HOME path"
  165 |   shell: echo $JAVA_HOME
  166 |   register: javahome_path
  167 |   run_once: true
  168 |   delegate_to: "{{ scale_server }}"
  169 | 
  170 | - fail:
  171 |     msg: "Failed due to namenodes are running, please stop namenodes(/usr/lpp/mmfs/hadoop/sbin/mmhdfs hdfs-nn stop) and retry deploy."
  172 |   when: ha_enabled|bool and not ces_hdfs_enabled|bool and ha_enable_dir.rc != 0
  173 |   run_once: true
  174 |   delegate_to: "{{ scale_server }}"
  175 | 
  176 | - name: Configure | Set JAVA_HOME
  177 |   command: "/usr/lpp/mmfs/hadoop/sbin/mmhdfs config set hadoop-env.sh -k JAVA_HOME={{ javahome_path.stdout }}"
  178 |   register: javahome
  179 |   run_once: true
  180 |   delegate_to: "{{ scale_server }}"
  181 | 
  182 | - block:
  183 |    - name: configure | Configuare core-site.xml
  184 |      set_fact:
  185 |          core_site_conf_dict: "{{ core_site_conf_dict | default({}) | combine ({ core_list.key : core_list.value }) }}"
  186 |      with_items:
  187 |         - { 'key': "fs.defaultFS", 'value': "hdfs://{{scale_hdfs_cluster.name}}" }
  188 |         - { 'key': "hadoop.proxyuser.livy.hosts", 'value': "*" }
  189 |         - { 'key': "hadoop.proxyuser.livy.groups", 'value': "*" }
  190 |         - { 'key': "hadoop.proxyuser.hive.hosts", 'value': "*" }
  191 |         - { 'key': "hadoop.proxyuser.hive.groups", 'value': "*" }
  192 |         - { 'key': "hadoop.proxyuser.oozie.hosts", 'value': "*" }
  193 |         - { 'key': "hadoop.proxyuser.oozie.groups", 'value': "*" }
  194 |      loop_control:
  195 |        loop_var: core_list
  196 | 
  197 |    - name: configure | Configuare hdfs-site.xml
  198 |      set_fact:
  199 |          hdfs_site_conf_dict: "{{ hdfs_site_conf_dict | default({}) | combine ({ hdfs_list.key : hdfs_list.value }) }}"
  200 |      with_items:
  201 |         - { 'key': "dfs.ha.namenodes.{{ scale_hdfs_cluster.name }}", 'value': "{{ namenodes_service }}" }
  202 |         - { 'key': "dfs.client.failover.proxy.provider.{{ scale_hdfs_cluster.name }}", 'value': 'org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider' }
  203 |         - { 'key': "dfs.nameservices", 'value': "{{ scale_hdfs_cluster.name }}" }
  204 |         - { 'key': "dfs.namenode.rpc-bind-host", 'value': "0.0.0.0" }
  205 |         - { 'key': "dfs.namenode.servicerpc-bind-host", 'value': "0.0.0.0" }
  206 |         - { 'key': "dfs.namenode.lifeline.rpc-bind-host", 'value': "0.0.0.0" }
  207 |         - { 'key': "dfs.namenode.http-bind-host", 'value': "0.0.0.0" }
  208 |      loop_control:
  209 |        loop_var: hdfs_list
  210 | 
  211 |    - name: configure | include append_dict.yml
  212 |      include_tasks: append_dict.yml
  213 |      vars:
  214 |         map_var: "{{ namenodes_item }}" 
  215 |      loop: "{{ namenodes_service.split(',')|zip(scale_hdfs_namenodes_list)|list }}"
  216 |      loop_control:
  217 |         loop_var: namenodes_item
  218 | 
  219 |    - name: configure | Configuare hdfs-site.xml for HA
  220 |      set_fact:
  221 |         hdfs_site_conf_dict: "{{ hdfs_site_conf_dict | default({}) | combine ({ hdfs_site_ha_conf.key : hdfs_site_ha_conf.value }) }}"
  222 |      with_items:
  223 |        - { 'key': "dfs.namenode.shared.edits.dir", 'value': "file:///{{ scale_hdfs_mountpoint }}/HA-{{ scale_hdfs_cluster.name }}" }
  224 |      when: ha_enabled|bool
  225 |      loop_control:
  226 |         loop_var: hdfs_site_ha_conf
  227 | 
  228 |    - name: configure | Configuare gpfs-site.xml
  229 |      set_fact:
  230 |          gpfs_site_conf_dict: "{{ gpfs_site_conf_dict | default({}) | combine ({ hdfs_site_list.key : hdfs_site_list.value }) }}"
  231 |      with_items:
  232 |        - { 'key': "gpfs.mnt.dir", 'value': "{{ scale_hdfs_mountpoint }}" }
  233 |        - { 'key': "gpfs.data.dir", 'value': "{{ scale_hdfs_datadir }}" }
  234 |      loop_control:
  235 |         loop_var: hdfs_site_list
  236 |   run_once: true
  237 |   delegate_to: localhost
  238 | 
  239 | - block:
  240 |    - name: configure | Set configuration for core-site.xml
  241 |      shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs config set core-site.xml -k "{{ core_site_conf.key }}"="{{ core_site_conf.value }}"
  242 |      loop:  "{{ core_site_conf_dict | dict2items }}"
  243 |      loop_control:
  244 |         loop_var: core_site_conf
  245 | 
  246 |    - name: configure | Set configuration for gpfs-site.xml
  247 |      shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs config set gpfs-site.xml -k "{{ gpfs_site_conf.key }}"="{{ gpfs_site_conf.value }}"
  248 |      loop:  "{{ gpfs_site_conf_dict | dict2items }}"
  249 |      loop_control:
  250 |         loop_var: gpfs_site_conf
  251 | 
  252 |    - name: configure | Set configuration for hdfs-site.xml
  253 |      shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs config set hdfs-site.xml -k "{{ hdfs_site_conf.key }}"="{{ hdfs_site_conf.value }}"
  254 |      loop:  "{{ hdfs_site_conf_dict | dict2items }}"
  255 |      loop_control:
  256 |         loop_var: hdfs_site_conf
  257 | 
  258 |    - name: configure | Remove localhost
  259 |      shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs worker remove localhost
  260 |      register: worker_remove
  261 | 
  262 |    - name: configure | Add Datanodes
  263 |      command: /usr/lpp/mmfs/hadoop/sbin/mmhdfs worker add "{{ add_dn_item }}"
  264 |      loop: "{{ scale_hdfs_cluster.datanodes }}"
  265 |      loop_control:
  266 |         loop_var: add_dn_item
  267 | 
  268 |    - name: configure | Set hadoop ident for scaleadmd
  269 |      lineinfile: 
  270 |        dest: /var/mmfs/hadoop/etc/hadoop/hadoop-env.sh  
  271 |        state: present 
  272 |        regexp: '# export HADOOP_IDENT_STRING=.'
  273 |        line: 'export HADOOP_IDENT_STRING=root'
  274 |      when: 
  275 |        - scale_scaleadmd is defined  
  276 |        - scale_scaleadmd == true   
  277 |    
  278 |    - name: configure | Remove hadoop workers
  279 |      lineinfile: 
  280 |        dest: /var/mmfs/hadoop/etc/hadoop/workers 
  281 |        state: absent 
  282 |        regexp: '(^\n)'
  283 | 
  284 |    - name: configure | Upload config
  285 |      command: /usr/lpp/mmfs/hadoop/sbin/mmhdfs config upload
  286 |      register: config_upload
  287 | 
  288 |    - name: configure | InitializeSharedEdits for Namenodes HA
  289 |      command: /usr/lpp/mmfs/hadoop/bin/hdfs namenode -initializeSharedEdits -force
  290 |      register: initializedSharedEdits
  291 |      when: ha_enabled|bool and ces_hdfs_enabled|bool and ha_enable_dir.rc != 0
  292 | 
  293 |    - name: configure | suspend CES nodes
  294 |      command: "/usr/lpp/mmfs/bin/mmces node suspend --stop -N {{ scale_hdfs_cluster.namenodes|join(',') }}"
  295 |      register: suspend_ces
  296 |      when:
  297 |        - check_hdfs_ces_group.rc == 0
  298 | 
  299 |    - name:  configure | current CES-GROUP cleanup
  300 |      command: "/usr/lpp/mmfs/bin/mmchnode --noces-group {{ scale_hdfs_ces_group_name }} -N {{ scale_hdfs_cluster.namenodes|join(',') }}"
  301 |      register: clean_ces
  302 |      when:
  303 |        - check_hdfs_ces_group.rc == 0
  304 | 
  305 |    - name: configure | Enable CES
  306 |      command: "/usr/lpp/mmfs/bin/mmchnode --ces-group {{ scale_hdfs_ces_group_name }} -N {{ scale_hdfs_cluster.namenodes|join(',') }}"
  307 |      register: enable_ces
  308 | 
  309 |    - name: configure | start CES nodes
  310 |      command: "/usr/lpp/mmfs/bin/mmces node resume --start -N {{ scale_hdfs_cluster.namenodes|join(',') }}"
  311 |      register: start_ces
  312 |      when:
  313 |        - check_hdfs_ces_group.rc == 0
  314 | 
  315 |    - name: configure | Configure CES IP
  316 |      command: "/usr/lpp/mmfs/bin/mmces address change --ces-group {{ scale_hdfs_ces_group_name }} --ces-ip {{ scale_hdfs_ces_ip[0] }}"
  317 |      register: add_cesip
  318 |      when:
  319 |        - scale_hdfs_ces_ip is defined
  320 |        - scale_hdfs_ces_ip|length > 0
  321 |        - check_hdfs_ces_group.rc != 0
  322 |   run_once: true
  323 |   delegate_to: "{{ scale_server }}"
  324 | 
  325 | - fail:
  326 |     msg: "mmces address add failed. "
  327 |   when: add_cesip.changed|bool and add_cesip.rc > 0 and not ces_hdfs_enabled|bool
  328 |   run_once: true
  329 |   delegate_to: "{{ scale_server }}"
  330 | 
  331 | - fail:
  332 |     msg: "Failed to upload config hdfs"
  333 |   when: config_upload.rc > 0
  334 |   run_once: true
  335 |   delegate_to: "{{ scale_server }}"
  336 | 
  337 | - block:
  338 |     - name: Enable HDFS
  339 |       command: /usr/lpp/mmfs/bin/mmces service enable HDFS
  340 | 
  341 |     - name: Start Namenodes
  342 |       shell: /usr/lpp/mmfs/bin/mmces service start HDFS -N "{{ nn_items }}"
  343 |       with_items: "{{ scale_hdfs_namenodes_list }}"
  344 |       loop_control:
  345 |         loop_var: nn_items
  346 | 
  347 |     - name: Check Namenodes running status
  348 |       shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs hdfs-nn status | grep 'namenode pid is' | wc -l
  349 |       register: nn_status
  350 | 
  351 |     - name: Start Datanodes
  352 |       shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs hdfs-dn restart
  353 | 
  354 |     - name: Check Datanodes running status
  355 |       shell: /usr/lpp/mmfs/hadoop/sbin/mmhdfs hdfs-dn status | grep 'datanode pid is' | wc -l
  356 |       register: dn_status
  357 |   run_once: true
  358 |   delegate_to: "{{ scale_server }}"
  359 | 
  360 | - fail:
  361 |     msg: "Fail to start all NameNode. "
  362 |   when: nn_status.stdout|int != scale_hdfs_namenodes_list|length
  363 |   run_once: true
  364 |   delegate_to: "{{ scale_server }}"
  365 | 
  366 | - fail:
  367 |     msg: "Fail to start all DataNode. "
  368 |   when: dn_status.stdout|int != scale_hdfs_datanodes_list|length
  369 |   run_once: true
  370 |   delegate_to: "{{ scale_server }}"
```

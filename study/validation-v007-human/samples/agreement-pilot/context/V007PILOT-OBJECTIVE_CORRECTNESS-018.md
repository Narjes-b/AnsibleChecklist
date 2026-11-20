# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-018

- Repository: `Sunbird-Obsrv/sunbird-data-pipeline`
- Commit: `eb1e1a1c3533c549693dda32cd92c667754aaea9`
- Family: Objective correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/roles/data-products-deploy/tasks/main.yml` (reported anchor line 201)
- Object: `source_location` `737bbfc8d6bc0c3f9cf1f1b85398a1bc3f87d74f3db0c1f744a7da7c1057893b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–441 of 441:

```text
    1 | ## Data products deployment ##
    2 | - name: Ensure azure blob storage container exists
    3 |   command: az storage container create --name {{ bucket }}
    4 |   when: dp_object_store_type == "azure"
    5 |   tags:
    6 |     - always
    7 | 
    8 | - name: Copy Core Data Products
    9 |   copy: src={{ analytics_batch_module_artifact }} dest={{ analytics.home }}/models-{{ model_version }}
   10 |   tags:
   11 |     - dataproducts
   12 | 
   13 | - name: Copy Core Data Products to azure blob
   14 |   command: az storage blob upload --overwrite -c {{ bucket }} --name models-{{ model_version }}/{{ analytics_batch_module_artifact }} -f {{ analytics.home }}/models-{{ model_version }}/{{ analytics_batch_module_artifact }}
   15 |   async: 3600
   16 |   poll: 10
   17 |   tags:
   18 |     - dataproducts-spark-cluster 
   19 | 
   20 | - name: Unarchive Ed Data Products
   21 |   become: yes
   22 |   unarchive: src={{ playbook_dir}}/{{ analytics_ed_dataporducts_artifact }} dest={{ analytics.home }}/models-{{ model_version }} copy=yes group={{ analytics_group }} owner={{ analytics_user }}
   23 |   tags:
   24 |     - ed-dataproducts
   25 | 
   26 | - name: Copy Ed Data Products to azure blob
   27 |   command: az storage blob upload --overwrite -c {{ bucket }} --name models-{{ model_version }}/data-products-1.0.jar -f {{ analytics.home }}/models-{{ model_version }}/data-products-1.0/data-products-1.0.jar
   28 |   async: 3600
   29 |   poll: 10
   30 |   tags:
   31 |     - ed-dataproducts-spark-cluster      
   32 | 
   33 | - name: Copy Framework Library
   34 |   copy: src={{ analytics_core_artifact }} dest={{ analytics.home }}/models-{{ model_version }}
   35 |   tags:
   36 |     - framework
   37 | 
   38 | - name: Copy Framework Library to azure blob
   39 |   command: az storage blob upload --overwrite --debug -c {{ bucket }} --name models-{{ model_version }}/{{ analytics_core_artifact }} -f {{ analytics.home }}/models-{{ model_version }}/{{ analytics_core_artifact }}
   40 |   async: 3600
   41 |   poll: 10
   42 |   tags:
   43 |     - framework-spark-cluster
   44 | 
   45 | - name: Copy Scruid Library
   46 |   copy: src={{ scruid_artifact }} dest={{ analytics.home }}/models-{{ model_version }}
   47 |   tags:
   48 |     - framework  
   49 | 
   50 | - name: Copy Scruid Library to azure blob
   51 |   command: az storage blob upload --overwrite -c {{ bucket }} --name models-{{ model_version }}/{{ scruid_artifact }} -f {{ analytics.home }}/models-{{ model_version }}/{{ scruid_artifact }}
   52 |   async: 3600
   53 |   poll: 10
   54 |   tags:
   55 |     - framework-spark-cluster  
   56 | 
   57 | - name: Copy Job Manager
   58 |   copy: src={{ analytics_job_manager_artifact }} dest={{ analytics.home }}/models-{{ model_version }}
   59 |   tags:
   60 |     - dataproducts
   61 | 
   62 | - name: Copy configuration file
   63 |   template: src=common.conf.j2 dest={{ analytics.home }}/models-{{ model_version }}/{{ env }}.conf mode=755 owner={{ analytics_user }} group={{ analytics_group }}
   64 |   tags:
   65 |     - dataproducts
   66 |     - ed-dataproducts
   67 |     - framework
   68 |   when: dockdataproducts is undefined
   69 | 
   70 | - name: Copy configuration file
   71 |   template: src=common.conf.j2 dest={{ analytics.home }}/models-{{ model_version }}/dock-{{ env }}.conf mode=755 owner={{ analytics_user }} group={{ analytics_group }}
   72 |   tags:
   73 |     - dataproducts
   74 |     - ed-dataproducts
   75 |     - framework
   76 |   when: dockdataproducts is defined
   77 | 
   78 | - name: Copy configuration file as application.conf for cluster
   79 |   template: src=common.conf.j2 dest={{ analytics.home }}/models-{{ model_version }}/application.conf mode=755 owner={{ analytics_user }} group={{ analytics_group }}
   80 |   tags:
   81 |     - framework-spark-cluster
   82 | 
   83 | - name: Update spark temp dir value for cluster
   84 |   lineinfile:
   85 |     path: '{{ analytics.home }}/models-{{ model_version }}/application.conf'
   86 |     regexp: '^spark_output_temp_dir="/mount/data/analytics/tmp/"'
   87 |     line: 'spark_output_temp_dir="/var/log/sparkapp/tmp/"'
   88 |   tags:
   89 |     - framework-spark-cluster
   90 | 
   91 | - name: Update logger kafka config for cluster
   92 |   lineinfile:
   93 |     path: '{{ analytics.home }}/models-{{ model_version }}/application.conf'
   94 |     regexp: '^log.appender.kafka.enable="false"'
   95 |     line: 'log.appender.kafka.enable="true"'
   96 |   tags:
   97 |     - framework-spark-cluster       
   98 | 
   99 | - name: Copy configuration file to azure blob
  100 |   command: az storage blob upload --overwrite -c {{ bucket }} -f {{ analytics.home }}/models-{{ model_version }}/application.conf --name models-{{ model_version }}/application.conf
  101 |   async: 3600
  102 |   poll: 10
  103 |   tags:
  104 |     - framework-spark-cluster    
  105 | 
  106 | - name: Copy log4j2 xml file
  107 |   template: src=log4j2.xml.j2 dest={{ analytics.home }}/models-{{ model_version }}/log4j2.xml mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  108 |   tags: [ dataproducts, framework, ed-dataproducts ]
  109 | 
  110 | - name: Copy Scripts
  111 |   template: src={{ item }}.j2 dest={{ analytics.home }}/scripts/{{ item }}.sh mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  112 |   with_items: "{{ analytics.scripts }}"
  113 |   tags: [ dataproducts, framework, ed-dataproducts ]
  114 |   when: dockdataproducts is undefined
  115 | 
  116 | - name: Copy python sanity check script file
  117 |   template: src=exhaust_sanity_check.py.j2 dest={{ analytics.home }}/scripts/exhaust_sanity_check.py
  118 |   tags: [ dataproducts, framework, ed-dataproducts ]
  119 |   when: dockdataproducts is undefined
  120 | 
  121 | - name: Copy Dock Scripts
  122 |   template: src={{ item }}.j2 dest={{ analytics.home }}/scripts/{{ item }}.sh mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  123 |   with_items: "{{ analytics.dockScripts }}"
  124 |   tags: [ dataproducts, framework, ed-dataproducts ]
  125 |   when: dockdataproducts is defined
  126 | 
  127 | - name: Update model config
  128 |   template: src=model-config.j2 dest={{ analytics.home }}/scripts/model-config.sh mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  129 |   tags:
  130 |     - dataproducts
  131 |     - update-config
  132 |     - ed-dataproducts
  133 |   when: dockdataproducts is undefined
  134 | 
  135 | - name: Update model dock config
  136 |   template: src=model-dock-config.j2 dest={{ analytics.home }}/scripts/model-dock-config.sh mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  137 |   tags:
  138 |     - dataproducts
  139 |     - update-config
  140 |     - ed-dataproducts
  141 |   when: dockdataproducts is defined
  142 | 
  143 | - name: Copy submit-all-jobs ruby file
  144 |   template: src=submit-all-jobs.rb.j2 dest={{ analytics.home }}/scripts/submit-all-jobs.rb mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  145 |   tags:
  146 |     - dataproducts
  147 |     - update-config
  148 |     - ed-dataproducts
  149 | 
  150 | - name: Copy model-config.json file
  151 |   template: src=model-config.json.j2 dest={{ analytics.home }}/scripts/model-config.json mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  152 |   tags:
  153 |     - dataproducts
  154 |     - update-config
  155 |     - ed-dataproducts
  156 | 
  157 | - name: Clean cron jobs
  158 |   command: crontab -r
  159 |   ignore_errors: yes
  160 |   tags:
  161 |     - default-jobs
  162 |     - spark-jobs
  163 |     - spark1-jobs
  164 |     - clean-cronjobs
  165 | 
  166 | - name: Create daily cron jobs for wfs
  167 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh wfs"
  168 |   with_dict: "{{ run_wfs_job }}"
  169 |   tags:
  170 |     - spark1-jobs
  171 | 
  172 | - name: Create daily cron jobs for monitor job
  173 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh monitor-job-summ"
  174 |   with_dict: "{{ run_monitor_job }}"
  175 |   tags:
  176 |     - spark1-jobs
  177 | 
  178 | - name: Create daily cron jobs using submit-all-jobs
  179 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job='/bin/bash -lc "ruby {{ analytics.home }}/scripts/submit-all-jobs.rb"'
  180 |   with_dict: "{{ submit_jobs }}"
  181 |   tags:
  182 |     - default-jobs
  183 |     - spark-jobs
  184 |     - cronjobs
  185 | 
  186 | - name: Create start-jobmanager cron jobs
  187 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/start-jobmanager.sh"
  188 |   with_dict: "{{ start_jobmanager }}"
  189 |   tags:
  190 |     - default-jobs
  191 |     - spark-jobs
  192 |     - cronjobs
  193 | 
  194 | - name: Create course-batch-status-updater cron job
  195 |   cron: name="{{env}}-course-batch-status-updater" minute=*/{{ course_batch_status_updater_job_schedule }} job="{{ analytics.home }}/scripts/run-job.sh course-batch-status-updater"
  196 |   tags:
  197 |     - cronjobs
  198 |     - default-jobs
  199 |     - spark1-jobs
  200 | 
  201 | - name: Create admin-user-reports cron job
  202 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh admin-user-reports"
  203 |   with_dict: "{{ run_admin_user_reports_job }}"
  204 |   tags:
  205 |     - cronjobs 
  206 |     - default-jobs
  207 |     - spark-jobs
  208 | - name: Create admin-geo-reports cron job
  209 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh admin-geo-reports"
  210 |   with_dict: "{{ run_admin_geo_reports_job }}"
  211 |   tags:
  212 |     - cronjobs
  213 |     - default-jobs
  214 |     - spark-jobs 
  215 | 
  216 | - name: Create assessment-aggregator reports cron job
  217 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="/bin/bash {{ analytics.home }}/adhoc-scripts/run_exporter.sh > /home/analytics/output.log"
  218 |   with_dict: "{{ run_assessment_aggregator_report_job }}"
  219 |   tags:
  220 |     - cronjobs
  221 |     - default-jobs
  222 |     - spark-jobs  
  223 | 
  224 | - name: Create etb metrics cron job
  225 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }} weekday={{ item.value.weekday }}  job="{{ analytics.home }}/scripts/run-job.sh etb-metrics"
  226 |   with_dict: "{{ run_etb_metrics_weekly_job }}"
  227 |   tags:
  228 |     - cronjobs
  229 |     - default-jobs
  230 |     - spark-jobs
  231 | 
  232 | - name: Create progress-exhaust cron job
  233 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh progress-exhaust"
  234 |   with_dict: "{{ run_progress_exhaust }}"
  235 |   tags:
  236 |     - cronjobs
  237 |     - default-jobs
  238 |     - spark1-jobs
  239 | 
  240 | - name: Create response-exhaust cron job
  241 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh response-exhaust"
  242 |   with_dict: "{{ run_response_exhaust }}"
  243 |   tags:
  244 |     - cronjobs
  245 |     - default-jobs
  246 |     - spark-jobs
  247 | 
  248 | - name: Create cassandra-migration cron job
  249 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh cassandra-migration"
  250 |   with_dict: "{{ run_cassandra_migration }}"
  251 |   tags:
  252 |     - cronjobs
  253 |     - default-jobs
  254 |     - spark-jobs
  255 |     
  256 | 
  257 | - name: Create userinfo-exhaust cron job
  258 |   cron: name="{{ env }}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }} job="{{ analytics.home }}/scripts/run-job.sh userinfo-exhaust"
  259 |   with_dict: "{{ run_userinfo_exhaust }}"
  260 |   tags:
  261 |     - cronjobs
  262 |     - default-jobs
  263 |     - spark-jobs
  264 | 
  265 | - name: Create collection-summary cron job
  266 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh collection-summary-report"
  267 |   with_dict: "{{ run_collection_summary }}"
  268 |   tags:
  269 |     - cronjobs
  270 |     - default-jobs
  271 |     - spark-jobs
  272 | 
  273 | - name: Copy collection-summary ingestion spec
  274 |   copy: src="collection-summary-ingestion-spec.json" dest={{ analytics.home }}/scripts/ mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  275 |   tags:
  276 |     - ed-dataproducts
  277 | 
  278 | - name: Create sourcing-summary cron job
  279 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-dock-job.sh sourcing-summary-report"
  280 |   with_dict: "{{ run_sourcing_summary }}"
  281 |   tags:
  282 |     - cronjobs
  283 |     - default-jobs
  284 |     - spark-jobs
  285 | 
  286 | - name: Create uci-private-exhaust cron job
  287 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh uci-private-exhaust"
  288 |   with_dict: "{{ run_uci_private_exhaust_job }}"
  289 |   tags:
  290 |     - cronjobs
  291 |     - default-jobs
  292 |     - spark-jobs
  293 | 
  294 | - name: Create uci-response-exhaust cron job
  295 |   cron: name="{{env}}-{{ item.key }}" minute={{ item.value.minute }} hour={{ item.value.hour }}  job="{{ analytics.home }}/scripts/run-job.sh uci-response-exhaust"
  296 |   with_dict: "{{ run_uci_response_exhaust_job }}"
  297 |   tags:
  298 |     - cronjobs
  299 |     - default-jobs
  300 |     - spark-jobs 
  301 | 
  302 | - name: Copy sourcing-summary ingestion spec
  303 |   copy: src="sourcing-ingestion-spec.json" dest={{ analytics.home }}/scripts/ mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  304 |   tags:
  305 |     - ed-dataproducts
  306 | 
  307 | - name: Update start jobmanager
  308 |   template: src=start-jobmanager.j2 dest={{ analytics.home }}/scripts/start-jobmanager.sh mode=755 owner={{ analytics_user }} group={{ analytics_group }}
  309 |   tags:
  310 |     - update-jobmanager-config
  311 |     - dataproducts
  312 | 
  313 | # Cluster job sumbit tasks
  314 | - name: Copy cluster-config.json file
  315 |   template: src=cluster-config.json.j2 dest={{ analytics_cluster.home }}/cluster-config.json
  316 |   delegate_to: localhost
  317 |   tags:
  318 |     - replay-job
  319 |     - run-job
  320 |     - config-update
  321 | 
  322 | - name: Copy submit-script.sh file
  323 |   template: src=submit-script.j2 dest={{ analytics_cluster.home }}/submit-script.sh mode=755
  324 |   delegate_to: localhost
  325 |   tags:
  326 |     - replay-job
  327 |     - run-job
  328 |     - config-update
  329 | 
  330 | - name: Copy model-config.sh file
  331 |   template: src=model-config.j2 dest={{ analytics_cluster.home }}/model-config.sh
  332 |   delegate_to: localhost  
  333 |   tags:
  334 |     - replay-job
  335 |     - run-job
  336 |     - config-update
  337 | 
  338 | - name: Replay Job
  339 |   shell: "nohup {{ analytics_cluster.home }}/submit-script.sh --job {{ job_id }} --mode {{ mode }} --partitions {{ partitions }} --parallelisation {{ parallelisation }} --startDate {{ start_date }} --endDate {{ end_date }} --sparkMaster {{ sparkMaster }} --selectedPartitions {{ selected_partitions }} &"
  340 |   async: "{{ (pause_min * 60) }}"
  341 |   poll: 0
  342 |   tags:
  343 |     - replay-job 
  344 | 
  345 | - name: Run Job
  346 |   shell: "nohup {{ analytics_cluster.home }}/submit-script.sh --job {{ job_id }} --mode {{ mode }} --partitions {{ partitions }} --parallelisation {{ parallelisation }} --sparkMaster {{ sparkMaster }} --selectedPartitions {{ selected_partitions }} --batch_id {{ batch_id }} &"
  347 |   async: "{{ (pause_min * 60) }}"
  348 |   poll: 0
  349 |   tags:
  350 |     - run-job
  351 | 
  352 | - name: Submit jobs
  353 |   shell: "nohup {{ analytics_cluster.home }}/submit-script.sh --job {{ item }} --mode default --sparkMaster yarn &"
  354 |   with_items: "{{ jobs.split(',')|list }}"
  355 |   tags:
  356 |     - job-submit
  357 | 
  358 | # Cluster exhaust parallel jobs sumbit tasks
  359 | 
  360 | - name: Install required python packages
  361 |   pip:
  362 |     name:
  363 |       - psycopg2-binary
  364 |       - pandas
  365 |       - IPython
  366 |   tags:
  367 |     - parallel-jobs-submit  
  368 | 
  369 | - name: Copy python script file
  370 |   template: src=update-job-requests.py.j2 dest={{ analytics_cluster.home }}/update-job-requests.py
  371 |   delegate_to: localhost  
  372 |   tags:
  373 |     - parallel-jobs-submit
  374 | 
  375 | - name: Execute python script to populate batch numbers
  376 |   shell: |
  377 |     if echo "{{jobs}}" | grep 'druid'
  378 |     then
  379 |      python {{ analytics_cluster.home }}/update-job-requests.py {{ jobs }} {{ batch_size }} druid {{env}}_report_config
  380 |     elif echo "{{jobs}}" | grep 'exhaust'
  381 |      then
  382 |      python {{ analytics_cluster.home }}/update-job-requests.py {{ jobs }} {{ batch_size }} exhaust {{env}}_job_request
  383 |     fi
  384 |   tags:
  385 |     - parallel-jobs-submit
  386 |   register: jobsCountStr
  387 | 
  388 | 
  389 | - debug:
  390 |     var: jobsCountStr
  391 |   tags:
  392 |     - parallel-jobs-submit  
  393 | 
  394 | - name: Get stdout with parallelisation value from python script to tmp file
  395 |   shell: echo "{{ jobsCountStr.stdout }}" > /tmp/test.txt
  396 |   tags:
  397 |     - parallel-jobs-submit
  398 | 
  399 | - name: Extract parallelisation value from tmp file
  400 |   shell: "cat /tmp/test.txt | tr '\n' ' ' | awk -F': ' '{print $NF}'"
  401 |   register: jobsCountOut
  402 |   tags:
  403 |     - parallel-jobs-submit
  404 | 
  405 | - debug:
  406 |     var: jobsCountOut
  407 |   tags:
  408 |     - parallel-jobs-submit
  409 | 
  410 | # set jobs count variable from python script output
  411 | - set_fact:
  412 |     jobs_count: "{{ jobsCountOut.stdout }}"
  413 |   tags:
  414 |     - parallel-jobs-submit  
  415 | 
  416 | - name: Submit parallel exhaust jobs
  417 |   shell: "nohup {{ analytics_cluster.home }}/submit-script.sh --job {{ jobs }} --mode parallel-jobs --parallelisation {{ jobs_count }} &"
  418 |   poll: 30
  419 |   tags:
  420 |     - parallel-jobs-submit 
  421 |   register: submitOutput
  422 | 
  423 | - debug:
  424 |     var: submitOutput 
  425 |   tags:
  426 |     - parallel-jobs-submit      
  427 | 
  428 | # Execute Exhaust job sanity check script tasks
  429 | 
  430 | - name: Install required python packages
  431 |   pip:
  432 |     name:
  433 |       - requests
  434 |   tags:
  435 |     - run-sanity    
  436 | 
  437 | - name: Run sanity check python script
  438 |   shell: python {{ analytics.home }}/scripts/exhaust_sanity_check.py
  439 |   tags:
  440 |     - run-sanity
  441 |   register: SanityCheckStatus
```

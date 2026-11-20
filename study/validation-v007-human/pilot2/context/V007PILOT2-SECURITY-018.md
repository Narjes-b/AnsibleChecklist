# Frozen source context: V007PILOT2-SECURITY-018

- Repository: `ansible/instruqt`
- Commit: `e23435acd50f1f645c88958c8dee4fe2929014b6`
- Family: security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `images/ansible/setup-scripts/getting-started-mesh/getting-started-mesh-setup.yml` (reported anchor line 311)
- Flagged construct: task `high-availability setup refresh exec node health until unavailable`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–421 of 421:

```text
    1 | ---
    2 | # code: language=ansible
    3 | # getting-started-mesh
    4 | ##
    5 | # https://play.instruqt.com/redhat/tracks/getting-started-mesh/
    6 | #
    7 | # Tags:
    8 | # setup-env - Setup controller env for lab
    9 | # <challenge-slug>-check - check challenge
   10 | # <challenge-slug>-solve - solve challenge
   11 | # <challenge-slug>-setup - setup challenge
   12 | ##
   13 | - name: Instruqt config getting-started-mesh
   14 |   hosts: all
   15 |   gather_facts: false
   16 |   become: true
   17 |   tasks:
   18 |   # For some reason, the authorized_key file disappears after instruqt setup sequence on rhel user
   19 |   - name: Add instruqt_lab ssh key to authorized keys on nodes
   20 |     ansible.posix.authorized_key:
   21 |       user: "{{ ansible_user }}"
   22 |       state: present
   23 |       key: "{{ lookup('file', '/home/' + ansible_user + '/.ssh/instruqt_lab.pub') }}"
   24 |       comment: "Instruqt lab key"
   25 |     tags:
   26 |       - setup-overview
   27 | 
   28 | - name: Instruqt challenge tasks getting-started-mesh
   29 |   hosts: automationcontroller
   30 |   gather_facts: false
   31 |   become: true
   32 | 
   33 |   vars:
   34 |     controller_login: &controller_login
   35 |       controller_username: "{{ controller_username }}"
   36 |       controller_password: "{{ controller_password }}"
   37 |       controller_host: "{{ controller_hostname }}"
   38 |       validate_certs: "{{ controller_validate_certs }}"
   39 | 
   40 |   pre_tasks:
   41 |     - name: Include variable file
   42 |       ansible.builtin.include_vars:
   43 |         file: "{{ playbook_dir }}/track_vars.yml"
   44 |       tags:
   45 |         - always
   46 | 
   47 |   tasks:
   48 |     - name: Solve mesh-instance-groups
   49 |       awx.awx.instance_group:
   50 |         state: present
   51 |         name: "{{ item.lab_instance_group_name }}"
   52 |         instances: "{{ item.lab_instance_group_hosts }}"
   53 |         <<: *controller_login
   54 |       loop: "{{ lab_instance_groups }}"
   55 |       tags:
   56 |         - mesh-instance-groups-solve
   57 | 
   58 |     - name: Check mesh-instance-groups
   59 |       ansible.builtin.command: "awx -k --conf.username {{ controller_username }}
   60 |                                 --conf.password {{ controller_password }}
   61 |                                 --conf.host https://{{ controller_hostname }}
   62 |                                 instance_group get '{{ lab_instance_group_name }}'"
   63 |       register: _instance_groups_check
   64 |       changed_when: _instance_groups_check.rc != 0
   65 |       tags:
   66 |         - mesh-instance-groups-check
   67 |         - mesh-instance-groups-instances-check
   68 | 
   69 |     - name: Assert instance is in the correct instance group
   70 |       ansible.builtin.assert:
   71 |         that: lab_instance_group_instance_name in _instance_groups_check.stdout
   72 |       tags:
   73 |         - mesh-instance-groups-instances-check
   74 | 
   75 |     # Solve / check multi-site
   76 |     - name: Solve multi-site instance groups and inventories
   77 |       awx.awx.inventory:
   78 |         name: "{{ item.name }}"
   79 |         description: "{{ item.description }}"
   80 |         organization: "{{ lab_organization }}"
   81 |         state: present
   82 |         instance_groups: "{{ item.inv_instance_groups }}"
   83 |         <<: *controller_login
   84 |       loop: "{{ lab_inventories }}"
   85 |       tags:
   86 |         - multi-site-solve
   87 |         - multi-site-solve-inv-ig
   88 | 
   89 |     - name: Solve multi-site run job templates Raleigh inventory
   90 |       awx.awx.job_launch:
   91 |         name: "{{ item.jt_name }}"
   92 |         organization: "{{ lab_organization }}"
   93 |         inventory: "{{ lab_us_inventory_name }}"
   94 |         wait: true
   95 |         <<: *controller_login
   96 |       retries: 60
   97 |       delay: 1
   98 |       loop: "{{ lab_job_templates }}"
   99 |       tags:
  100 |         - multi-site-solve-jt
  101 |         - multi-site-solve
  102 | 
  103 |     - name: Solve multi-site run job templates JHB inventory
  104 |       awx.awx.job_launch:
  105 |         name: "{{ item.jt_name }}"
  106 |         organization: "{{ lab_organization }}"
  107 |         inventory: "{{ lab_jhb_inventory_name }}"
  108 |         wait: true
  109 |         <<: *controller_login
  110 |       retries: 60
  111 |       delay: 1
  112 |       loop: "{{ lab_job_templates }}"
  113 |       tags:
  114 |         - multi-site-solve-jt
  115 |         - multi-site-solve
  116 | 
  117 |     - name: Check multi-site inventory instance group assignment
  118 |       awx.awx.inventory:
  119 |         name: "{{ lab_inv_name }}"
  120 |         organization: "{{ lab_organization }}"
  121 |         state: present
  122 |         instance_groups: "{{ lab_inv_igs }}"
  123 |         <<: *controller_login
  124 |       check_mode: true
  125 |       register: _multi_site_check_inv
  126 |       failed_when: (_multi_site_check_inv["changed"] | bool) or (_multi_site_check_inv["failed"] | bool)
  127 |       tags:
  128 |         - multi-site-check-inv-ig
  129 |         - multi-site-check
  130 | 
  131 |     - name: List job template run list
  132 |       awx.awx.job_list:
  133 |         status: successful
  134 |         query: {"name": "{{ lab_jt_name }}",
  135 |                 "inventory__name": "{{ lab_inv_name }}"}
  136 |         <<: *controller_login
  137 |       register: _multi_site_check_inv
  138 |       failed_when: _multi_site_check_inv.count == 0
  139 |       tags:
  140 |         - multi-site-check-inv-jt
  141 |         - multi-site-check
  142 | 
  143 |     # Setup / solve / check high-availability
  144 |     - name: High-availability set instance id fact - {{ lab_exec_node_hostname }}  # noqa yaml[line-length]
  145 |       ansible.builtin.set_fact:
  146 |         _exec1: "{{ _exec1 | default({}) | combine({'name': item.hostname, 'id': item.id}) }}"
  147 |       loop: "{{ query('awx.awx.controller_api', 'instances',
  148 |                 username=controller_username,
  149 |                 password=[REDACTED_LITERAL]
  150 |                 verify_ssl=controller_validate_certs,
  151 |                 query_params={'hostname': lab_dbn_check_instance_name}) | list }}"
  152 |       tags:
  153 |         - high-availability-setup
  154 |         - high-availability-check-instance
  155 |         - high-availability-solve
  156 |         - playground-setup
  157 | 
  158 |     - name: High-availability solve mesh dublin hop templates
  159 |       awx.awx.job_launch:
  160 |         name: "{{ item.jt_name }}"
  161 |         organization: "{{ lab_organization }}"
  162 |         wait: true
  163 |         <<: *controller_login
  164 |       retries: 60
  165 |       delay: 1
  166 |       when: '"Setup Dublin hop node" in item.jt_name'
  167 |       loop: "{{ lab_dbn_check_job_templates }}"
  168 |       tags:
  169 |         - high-availability-solve
  170 | 
  171 |     - name: High-availability reload receptor service
  172 |       ansible.builtin.command: >
  173 |         /usr/bin/receptorctl --socket /var/run/awx-receptor/receptor.sock reload
  174 |       register: _receptor_reload
  175 |       changed_when: _receptor_reload.rc != 0
  176 |       tags:
  177 |         - high-availability-solve
  178 |         - high-availability-setup
  179 |         - playground-setup
  180 | 
  181 |     - name: High-availability solve receptor ping {{ lab_hop_node_hostname }}
  182 |       ansible.builtin.command: >
  183 |         /usr/bin/receptorctl --socket /var/run/awx-receptor/receptor.sock ping {{ lab_hop_node_hostname }}
  184 |       register: _lab_hop_node_hostname_ping
  185 |       until: _lab_hop_node_hostname_ping.rc == 0
  186 |       changed_when: false
  187 |       retries: 10
  188 |       delay: 3
  189 |       tags:
  190 |         - high-availability-solve
  191 | 
  192 |     - name: High-availability solve receptor ping {{ lab_exec_node_hostname }}
  193 |       ansible.builtin.command: >
  194 |         /usr/bin/receptorctl --socket /var/run/awx-receptor/receptor.sock ping {{ lab_exec_node_hostname }}
  195 |       register: _lab_exec_node_hostname_ping
  196 |       until: _lab_exec_node_hostname_ping.rc == 0
  197 |       changed_when: false
  198 |       retries: 10
  199 |       delay: 3
  200 |       tags:
  201 |         - high-availability-solve
  202 | 
  203 |     - name: High-availability solve perform health check
  204 |       ansible.builtin.uri:
  205 |         url: "https://localhost/api/v2/instances/{{ _exec1.id }}/health_check/"
  206 |         method: POST
  207 |         user: "{{ controller_username }}"
  208 |         password: "{{ controller_password }}"
  209 |         validate_certs: false
  210 |         force_basic_auth: true
  211 |       tags:
  212 |         - high-availability-solve
  213 | 
  214 |     - name: High-availability solve refresh node health until ready
  215 |       ansible.builtin.uri:
  216 |         url: "https://localhost/api/v2/instances/{{ _exec1.id }}/"
  217 |         method: GET
  218 |         user: "{{ controller_username }}"
  219 |         password: "{{ controller_password }}"
  220 |         validate_certs: false
  221 |         force_basic_auth: true
  222 |       register: __health_check
  223 |       until: __health_check.json.node_state == "ready"
  224 |       retries: 20
  225 |       delay: 3
  226 |       tags:
  227 |         - high-availability-solve
  228 | 
  229 |     - name: High-availability solve mesh route info jt
  230 |       awx.awx.job_launch:
  231 |         name: "{{ item.jt_name }}"
  232 |         organization: "{{ lab_organization }}"
  233 |         wait: true
  234 |         <<: *controller_login
  235 |       retries: 60
  236 |       delay: 1
  237 |       when: '"Mesh route info" in item.jt_name'
  238 |       loop: "{{ lab_dbn_check_job_templates }}"
  239 |       tags:
  240 |         - high-availability-solve
  241 | 
  242 |     - name: High-availability solve mesh Debug info
  243 |       awx.awx.job_launch:
  244 |         name: "{{ item.jt_name }}"
  245 |         organization: "{{ lab_organization }}"
  246 |         inventory: "{{ lab_jhb_inventory_name }}"
  247 |         wait: true
  248 |         <<: *controller_login
  249 |       retries: 60
  250 |       delay: 1
  251 |       when: '"Debug info" in item.jt_name'
  252 |       loop: "{{ lab_dbn_check_job_templates }}"
  253 |       tags:
  254 |         - high-availability-solve
  255 | 
  256 |     - name: Stop receptor service on {{ lab_hop_node_hostname }}
  257 |       ansible.builtin.service:
  258 |         name: receptor
  259 |         state: stopped
  260 |       delegate_to: "{{ lab_hop_node_hostname }}"
  261 |       tags:
  262 |         - high-availability-setup
  263 |         - playground-setup
  264 | 
  265 |     - name: High-availability remove stanza from receptor.conf - {{ lab_exec_node_hostname }}
  266 |       ansible.builtin.template:
  267 |         src: "{{ playbook_dir }}/receptor.conf.j2"
  268 |         dest: "/etc/receptor/receptor.conf"
  269 |         mode: 0644
  270 |         validate: "/bin/receptorctl --socket /var/run/awx-receptor/receptor.sock --tls-client tls_client --config %s reload"
  271 |         backup: true
  272 |       register: _receptor_conf
  273 |       tags:
  274 |         - high-availability-setup
  275 |         - playground-setup
  276 | 
  277 |     - name: Restart receptor service
  278 |       ansible.builtin.service:
  279 |         name: receptor
  280 |         state: restarted
  281 |       tags:
  282 |         - high-availability-setup
  283 |         - playground-setup
  284 | 
  285 |     - name: High-availability setup receptor ping until failed - {{ lab_hop_node_hostname }}
  286 |       ansible.builtin.command: >
  287 |         /usr/bin/receptorctl --socket /var/run/awx-receptor/receptor.sock ping {{ lab_hop_node_hostname }}
  288 |       register: _lab_hop_node_hostname_ping
  289 |       until: _lab_hop_node_hostname_ping.rc != 0
  290 |       failed_when: _lab_hop_node_hostname_ping.rc == 0
  291 |       changed_when: false
  292 |       retries: 60
  293 |       delay: 1
  294 |       tags:
  295 |         - high-availability-setup
  296 |         - playground-setup
  297 | 
  298 |     - name: High-availability perform health check
  299 |       ansible.builtin.uri:
  300 |         url: "https://localhost/api/v2/instances/{{ _exec1.id }}/health_check/"
  301 |         method: POST
  302 |         user: "{{ controller_username }}"
  303 |         password: "{{ controller_password }}"
  304 |         validate_certs: false
  305 |         force_basic_auth: true
  306 |       tags:
  307 |         - high-availability-setup
  308 |         - playground-setup
  309 | 
  310 |     - name: High-availability setup refresh exec node health until unavailable
  311 |       ansible.builtin.uri:
  312 |         url: "https://localhost/api/v2/instances/{{ _exec1.id }}/"
  313 |         method: GET
  314 |         user: "{{ controller_username }}"
  315 |         password: "{{ controller_password }}"
  316 |         validate_certs: false
  317 |         force_basic_auth: true
  318 |       register: __health_check
  319 |       until: __health_check.json.node_state == "unavailable"
  320 |       retries: 60
  321 |       delay: 1
  322 |       tags:
  323 |         - high-availability-setup
  324 |         - playground-setup
  325 | 
  326 |     - name: High-availability clear job history
  327 |       ansible.builtin.uri:
  328 |         url: "https://localhost/api/v2/system_job_templates/1/launch/"
  329 |         method: POST
  330 |         body_format: json
  331 |         body:
  332 |           extra_vars:
  333 |             days: 0
  334 |         user: "{{ controller_username }}"
  335 |         password: "{{ controller_password }}"
  336 |         validate_certs: false
  337 |         force_basic_auth: true
  338 |       register: _job_history
  339 |       failed_when: false
  340 |       tags:
  341 |         - high-availability-setup
  342 |         - playground-setup
  343 | 
  344 |     - name: High-availability create dublin inventory
  345 |       awx.awx.inventory:
  346 |         name: "{{ item.name }}"
  347 |         description: "{{ item.description }}"
  348 |         organization: "{{ lab_organization }}"
  349 |         state: present
  350 |         <<: *controller_login
  351 |       loop: "{{ lab_dbn_inventories }}"
  352 |       tags:
  353 |         - high-availability-setup
  354 |         - playground-setup
  355 | 
  356 |     - name: High-availability create dublin hosts
  357 |       awx.awx.host:
  358 |         name: "{{ item.lab_host_name }}"
  359 |         inventory: "{{ item.lab_host_inventory }}"
  360 |         state: present
  361 |         variables: "{{ item.lab_host_vars }}"
  362 |         <<: *controller_login
  363 |       loop: "{{ lab_dbn_hosts }}"
  364 |       tags:
  365 |         - high-availability-setup
  366 |         - playground-setup
  367 | 
  368 |     - name: High-availability setup create job templates
  369 |       awx.awx.job_template:
  370 |         name: "{{ item.jt_name }}"
  371 |         state: present
  372 |         become_enabled: "{{ item.jt_become }}"
  373 |         project: "{{ lab_project_name }}"
  374 |         credential: "{{ lab_credential_name }}"
  375 |         inventory: "{{ item.jt_inventory }}"
  376 |         playbook: "{{ item.jt_playbook }}"
  377 |         survey_enabled: "{{ item.survey_enabled }}"
  378 |         survey_spec: "{{ item.survey_spec | default(omit) }}"
  379 |         ask_inventory_on_launch: "{{ item.jt_prompt_inventory }}"
  380 |         extra_vars: "{{ item.jt_extra_vars | default(omit) }}"
  381 |         <<: *controller_login
  382 |       loop: "{{ lab_dbn_job_templates }}"
  383 |       tags:
  384 |         - high-availability-setup
  385 |         - playground-setup
  386 | 
  387 |     - name: High-availability list job template run list
  388 |       awx.awx.job_list:
  389 |         status: successful
  390 |         query: {"name": "{{ lab_jt_name }}",
  391 |                 "inventory__name": "{{ lab_inv_name }}"}
  392 |         <<: *controller_login
  393 |       register: _high_availability_check_jt
  394 |       failed_when: _high_availability_check_jt.count == 0
  395 |       tags:
  396 |         - high-availability-check-jt
  397 | 
  398 |     - name: High-availability check exec node status until ready
  399 |       ansible.builtin.uri:
  400 |         url: "https://localhost/api/v2/instances/{{ _exec1.id }}/"
  401 |         method: GET
  402 |         user: "{{ controller_username }}"
  403 |         password: "{{ controller_password }}"
  404 |         validate_certs: false
  405 |         force_basic_auth: true
  406 |       until: __health_check.json.node_state == "ready"
  407 |       retries: 30
  408 |       delay: 1
  409 |       register: __health_check
  410 |       tags:
  411 |         - high-availability-check-instance
  412 | 
  413 |     # Setup / solve / check playground
  414 |     - name: Setup playground remove instance groups
  415 |       awx.awx.instance_group:
  416 |         state: absent
  417 |         name: "{{ item.lab_instance_group_name }}"
  418 |         <<: *controller_login
  419 |       loop: "{{ lab_instance_groups }}"
  420 |       tags:
  421 |         - playground-setup
```

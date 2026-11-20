# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-014

- Repository: `ansible/instruqt`
- Commit: `e23435acd50f1f645c88958c8dee4fe2929014b6`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `images/ansible/setup-scripts/getting-started-edge-lab/getting-started-edge-lab-setup.yml` (reported anchor line 1)
- Object: `source_location` `f41db1e69167b55ee436e9575f4b99b0ba693c7ee35bb989366dde4353f0d3dc`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–208 of 208:

```text
    1 | ---
    2 | # https://play.instruqt.com/redhat/tracks/getting-started-edge-lab/
    3 | #
    4 | # Tags:
    5 | # controller-config - Setup controller env for lab
    6 | # auth-token - create controller auth-token
    7 | # <challenge-slug>-check - check challenge
    8 | # <challenge-slug>-solve - solve challenge
    9 | # <challenge-slug>-setup - setup challenge
   10 | ##
   11 | - name: Instruqt config getting-started-mesh
   12 |   hosts: all
   13 |   gather_facts: false
   14 |   become: true
   15 |   tasks:
   16 |     # For some reason, the authorized_key file disappears after instruqt setup sequence on rhel user
   17 |     - name: Add instruqt_lab ssh key to authorized keys on nodes
   18 |       ansible.posix.authorized_key:
   19 |         user: "{{ ansible_user }}"
   20 |         state: present
   21 |         key: "{{ lookup('file', '/home/' + ansible_user + '/.ssh/instruqt_lab.pub') }}"
   22 |         comment: "Instruqt lab key"
   23 |       tags:
   24 |         - env-overview-setup
   25 | 
   26 | - name: Instruqt config getting started with edge lab
   27 |   hosts: automationcontroller
   28 |   gather_facts: false
   29 |   become: true
   30 |   tags:
   31 |     - getting-started-edge-lab
   32 | 
   33 |   vars:
   34 |     controller_login: &controller_login
   35 |       controller_username: "{{ controller_username }}"
   36 |       controller_password: "{{ controller_password }}"
   37 |       controller_host: "{{ controller_hostname }}"
   38 |       validate_certs: "{{ controller_validate_certs }}"
   39 | 
   40 |   tasks:
   41 |   ## Setup, check and solve challenges
   42 |     # Need inventory to create job template
   43 |     - name: Setup - create inventories - {{ lab_inv_name }}
   44 |       awx.awx.inventory:
   45 |         name: "{{ item.name }}"
   46 |         organization: "{{ item.organization }}"
   47 |         description: "{{ item.description | default(omit) }}"
   48 |         instance_groups: "{{ item.instance_groups | default(omit) }}"
   49 |         kind: "{{ item.kind | default(omit) }}"
   50 |         host_filter: "{{ item.host_filter | default(omit) }}"
   51 |         state: "{{ item.state | default('present') }}"
   52 |         variables: "{{ item.variables | default(omit) }}"
   53 |         <<: *controller_login
   54 |       when: (controller_inventories is defined) and (item["name"] == lab_inv_name)
   55 |       loop: "{{ controller_inventories }}"
   56 |       tags:
   57 |         - edge-workflow-setup-inv
   58 |         - edge-workflow-setup
   59 | 
   60 |     - name: Setup - create job templates - {{ lab_jt_name }}
   61 |       awx.awx.job_template:
   62 |         name: "{{ item.name }}"
   63 |         state: "{{ item.state }}"
   64 |         become_enabled: "{{ item.become_enabled }}"
   65 |         project: "{{ item.project }}"
   66 |         credentials: "{{ item.credentials }}"
   67 |         inventory: "{{ item.inventory }}"
   68 |         playbook: "{{ item.playbook }}"
   69 |         survey_spec: "{{ item.survey_spec | default(omit) }}"
   70 |         ask_inventory_on_launch: "{{ item.ask_inventory_on_launch | default(false) }}"
   71 |         ask_limit_on_launch: "{{ item.ask_limit_on_launch | default(omit) }}"
   72 |         extra_vars: "{{ item.extra_vars | default(omit) }}"
   73 |         limit: "{{ lab_jt_limit | default(omit) }}"
   74 |         execution_environment: "{{ item.execution_environment }}"
   75 |         <<: *controller_login
   76 |       loop: "{{ controller_templates }}"
   77 |       register: __create_templates_job_async
   78 |       when: (controller_templates is defined) and (item["name"] == lab_jt_name)
   79 |       changed_when: not __create_templates_job_async.changed
   80 |       async: 1000
   81 |       poll: 0
   82 |       tags:
   83 |         - install-edge-app-setup
   84 |         - install-monitor-app-setup
   85 |         - config-firewall-setup
   86 |         - edge-workflow-setup
   87 | 
   88 |     - name: "Async | Setup - create job templates"
   89 |       ansible.builtin.async_status:
   90 |         jid: "{{ __create_templates_job_async_result_item.ansible_job_id }}"
   91 |       retries: 60
   92 |       delay: 1
   93 |       loop: "{{ __create_templates_job_async.results }}"
   94 |       loop_control:
   95 |         loop_var: __create_templates_job_async_result_item
   96 |       until: __create_templates_job_async_result.finished
   97 |       register: __create_templates_job_async_result
   98 |       when: __create_templates_job_async_result_item.ansible_job_id is defined
   99 |       tags:
  100 |         - install-edge-app-setup
  101 |         - install-monitor-app-setup
  102 |         - config-firewall-setup
  103 |         - edge-workflow-setup
  104 | 
  105 |     - name: Check - assert {{ lab_jt_name }} template ran successfully
  106 |       awx.awx.job_list:
  107 |         status: successful
  108 |         query: {"name": "{{ lab_jt_name }}",
  109 |                 "inventory__name": "{{ lab_inv_name }}"}
  110 |         <<: *controller_login
  111 |       register: __jt_list
  112 |       failed_when: (__jt_list.count == 0) or (__jt_list is undefined)
  113 |       tags:
  114 |         - install-edge-app-check
  115 |         - install-monitor-app-check
  116 |         - config-firewall-check
  117 | 
  118 |     - name: Check - assert workflow template ran - {{ lab_workflow_name }}
  119 |       block:
  120 |         - name: Query controller api for workflow job
  121 |           ansible.builtin.set_fact: # noqa jinja[spacing]
  122 |             __workflow_job: "{{ query('awx.awx.controller_api', 'workflow_jobs',
  123 |                               username=controller_username,
  124 |                               password=[REDACTED_LITERAL]
  125 |                               verify_ssl=controller_validate_certs,
  126 |                               query_params={ 'name': lab_workflow_name, 'status': lab_workflow_status | default('successful') }) }}"
  127 |           register: __workflow_job_result
  128 | 
  129 |         - name: Assert __workflow_job length
  130 |           ansible.builtin.assert:
  131 |             that: __workflow_job | length > 0
  132 |             fail_msg: "No successful jobs for {{ lab_workflow_name }}"
  133 |       when: (lab_workflow_name is defined) and (lab_workflow_name == lab_jt_workflow_name)
  134 |       tags:
  135 |         - edge-workflow-check-jt
  136 | 
  137 |     # Need retries to give mesh time to initialize for solve scripts
  138 |     - name: Solve - run job template {{ lab_jt_name }}
  139 |       awx.awx.job_launch:
  140 |         name: "{{ lab_jt_name }}"
  141 |         organization: "{{ lab_organization }}"
  142 |         inventory: "{{ lab_inv_name }}"
  143 |         wait: true
  144 |         <<: *controller_login
  145 |       register: __run_templates_job
  146 |       until: __run_templates_job is success
  147 |       retries: 60
  148 |       delay: 0
  149 |       loop: "{{ controller_templates }}"
  150 |       when: (controller_templates is defined) and (item["name"] == lab_jt_name)
  151 |       tags:
  152 |         - install-edge-app-solve
  153 |         - install-monitor-app-solve
  154 |         - config-firewall-solve
  155 | 
  156 |     - name: Solve and check - lab workflow job template - {{ lab_workflow_name }}
  157 |       awx.awx.workflow_job_template:
  158 |         name: "{{ item.name }}"
  159 |         inventory: "{{ item.inventory | default(omit) }}"
  160 |         extra_vars: "{{ item.extra_vars | default(omit) }}"
  161 |         ask_variables_on_launch: "{{ item.ask_variables_on_launch | default(false) }}"
  162 |         organization: "{{ item.organization | default(omit) }}"
  163 |         state: "{{ lab_workflow_state | default('present') }}"
  164 |         <<: *controller_login
  165 |       check_mode: "{{ check_mode | default(false) }}"
  166 |       register: __workflow_template
  167 |       loop: "{{ controller_workflows }}"
  168 |       when: (controller_workflows is defined) and (lab_workflow_name == item.name)
  169 |       tags:
  170 |         - edge-workflow-solve
  171 |         - edge-workflow-check-jt-exists
  172 |         - edge-playground-setup
  173 | 
  174 |     - name: Solve - lab workflow template nodes - "{{ lab_workflow_name }}"
  175 |       awx.awx.workflow_job_template_node:
  176 |         identifier: "{{ item.identifier }}"
  177 |         organization: "{{ item.organization }}"
  178 |         inventory: "{{ item.inventory }}"
  179 |         unified_job_template: "{{ item.unified_job_template }}"
  180 |         success_nodes: "{{ item.success_nodes | default(omit) }}"
  181 |         workflow_job_template: "{{ item.workflow_job_template }}"
  182 |         controller_username: "{{ controller_username }}"
  183 |         controller_password: "{{ controller_password }}"
  184 |         controller_host: "{{ controller_hostname }}"
  185 |         validate_certs: "{{ controller_validate_certs }}"
  186 |       loop: "{{ controller_workflow_nodes }}"
  187 |       when: (controller_workflow_nodes is defined) and (lab_workflow_name == item.workflow_job_template)
  188 |       tags:
  189 |         - edge-workflow-solve
  190 | 
  191 |     - name: Assert if __workflow_template changed
  192 |       ansible.builtin.assert:
  193 |         that: not __workflow_template.changed | bool
  194 |         fail_msg: "Workflow template not created - {{ lab_workflow_name }}"
  195 |       tags:
  196 |         - edge-workflow-check-jt-exists
  197 | 
  198 |     - name: Solve - Launch workflow job template - {{ lab_workflow_name }}
  199 |       awx.awx.workflow_launch:
  200 |         workflow_template: "{{ item.name }}"
  201 |         organization: "{{ lab_organization }}"
  202 |         wait: true
  203 |         <<: *controller_login
  204 |       loop: "{{ controller_workflows }}"
  205 |       when:
  206 |         - (controller_workflows is defined) and (lab_workflow_name == item["name"])
  207 |       tags:
  208 |         - edge-workflow-solve
```

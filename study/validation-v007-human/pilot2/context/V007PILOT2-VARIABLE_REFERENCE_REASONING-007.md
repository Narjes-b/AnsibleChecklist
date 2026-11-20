# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-007

- Repository: `ansible/instruqt`
- Commit: `e23435acd50f1f645c88958c8dee4fe2929014b6`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `images/ansible/setup-scripts/lightspeed-101/lightspeed-101-lab_setup.yml` (reported anchor line 281)
- Flagged construct: variable `__output`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 181–381 of 812:

```text
  181 | 
  182 |         # #  Temp
  183 |         - name: Remove current repo dir
  184 |           ansible.builtin.file:
  185 |             state: absent
  186 |             path: "~{{ student_username }}/acme_corp"
  187 |           become_user: "{{ student_username }}"
  188 | 
  189 |         # # temp
  190 |         - name: Clone repository to {{ student_username }} # noqa latest[git]
  191 |           environment:
  192 |             GIT_SSL_NO_VERIFY: true
  193 |           ansible.builtin.git:
  194 |             repo: "{{ gitea_app_url }}/{{ student_username }}/{{ gitea_repo_name }}"
  195 |             dest: "~{{ student_username }}/acme_corp"
  196 |           become_user: "{{ student_username }}"
  197 | 
  198 |         # temp or rh1 branch
  199 |         - name: Temp - checkout devel
  200 |           ansible.builtin.command:
  201 |             # TODO fix to correct branch
  202 |             cmd: git checkout devel
  203 |             chdir: "~{{ student_username }}/{{ gitea_repo_name }}"
  204 |           become_user: "{{ student_username }}"
  205 |         # temp
  206 |         - name: Copy VS Code workspace settings to repo
  207 |           ansible.builtin.copy:
  208 |             src: "/opt/setup-scripts/{{ track_slug }}/files/.vscode"
  209 |             dest: "~{{ student_username }}/{{ gitea_repo_name }}/"
  210 |             remote_src: true
  211 |             owner: "{{ student_username }}"
  212 |             group: "{{ student_username }}"
  213 |             directory_mode: "755"
  214 |             mode: "644"
  215 |         # # temp
  216 |         - name: Fix directory permissions - {{ gitea_repo_name }}
  217 |           ansible.builtin.file:
  218 |             path: "~{{ student_username }}/{{ gitea_repo_name }}/.vscode"
  219 |             state: directory
  220 |             owner: "{{ student_username }}"
  221 |             group: "{{ student_username }}"
  222 |             mode: "755"
  223 | 
  224 |     # - name: Setup initial playbook files for challenges
  225 |     #   ansible.builtin.copy:
  226 |     #     src: "{{ playbook_dir }}/files/initial_playbooks/{{ item }}"
  227 |     #     dest: "~{{ student_username }}/{{ gitea_repo_name }}/{{ item }}"
  228 |     #     owner: "{{ student_username }}"
  229 |     #     group: "{{ student_username }}"
  230 |     #     remote_src: true
  231 |     #     mode: "644"
  232 |     #   register: __initial_playbook
  233 |     #   retries: 20
  234 |     #   delay: 1
  235 |     #   until: not __initial_playbook.failed
  236 |     #   loop: "{{ lookup('ansible.builtin.vars', content_list)['playbooks'] }}"
  237 |     #   tags:
  238 |     #     - setup-monitoring-playbook
  239 |     #     # - setup-keywords-playbook
  240 |     #     - setup-external-content-playbook
  241 |     #     - setup-generate-tasks-playbook
  242 |     #     - setup-workflow-playbook
  243 |   
  244 |     - name: Solve Overwrite demo Playbooks with solution playbooks - {{ gitea_repo_name }}
  245 |       ansible.builtin.copy:
  246 |         src: "{{ item.source_playbook }}"
  247 |         dest: "{{ item.dest_playbook }}"
  248 |         owner: "{{ student_username }}"
  249 |         group: "{{ student_username }}"
  250 |         remote_src: "{{ item.remote_src | default(omit) }}"
  251 |         mode: "644"
  252 |       loop: "{{ lookup('ansible.builtin.vars', content_list)['playbooks'] }}"
  253 |       tags:
  254 |         - setup-workflow-playbooks
  255 |         - solve-workflow-playbooks
  256 |         - solve-database-playbooks
  257 |         - solve-monitoring-playbooks
  258 |         - solve-apache-playbooks
  259 |         - solve-aws-playbooks
  260 |         - solve-azure-playbooks
  261 |         - setup-playground-playbooks
  262 | 
  263 |     - name: Setup and Solve - Git add Playbooks to repo
  264 |       ansible.builtin.command:
  265 |         cmd: "git add {{ item.dest_playbook }}"
  266 |         chdir: "~{{ student_username }}/{{ gitea_repo_name }}"
  267 |       become_user: "{{ student_username }}"
  268 |       register: __add_output
  269 |       changed_when: __add_output.rc == 0
  270 |       loop: "{{ lookup('ansible.builtin.vars', content_list)['playbooks']  }}"
  271 |       tags:
  272 |         - setup-playground-playbooks
  273 |         - setup-workflow-playbooks
  274 |         - solve-monitoring-playbooks
  275 |         - solve-apache-playbooks
  276 |         - solve-database-playbooks
  277 |         - solve-aws-playbooks
  278 |         - solve-azure-playbooks
  279 |         - solve-workflow-playbooks
  280 | 
  281 |     - name: Setup - Push challenge setup commit to repo
  282 |       ansible.builtin.command:
  283 |         cmd: "{{ item }}"
  284 |         chdir: "~{{ student_username }}/{{ gitea_repo_name }}"
  285 |       become_user: "{{ student_username }}"
  286 |       register: __output
  287 |       failed_when: false # TODO loop with matching changed_when and failed_when text.
  288 |       loop:
  289 |         - "git commit -m'Challenge setup commit.'"
  290 |         - "git push -u origin devel --force" # Temp
  291 |         # - "git push -u origin main --force"
  292 |       tags:
  293 |         - setup-playground-playbooks
  294 |         - setup-workflow-playbooks
  295 |         - solve-workflow-playbooks
  296 |         - solve-database-playbooks
  297 |         - solve-monitoring-playbooks
  298 |         - solve-apache-playbooks
  299 |         - solve-aws-playbooks
  300 |         - solve-azure-playbooks
  301 | 
  302 |     - name: Sync Project - {{ lab.project.name }}
  303 |       awx.awx.project_update:
  304 |         name: "{{ lab.project.name }}"
  305 |         wait: true
  306 |         timeout: 60
  307 |         <<: *controller_login
  308 |       tags:
  309 |         setup-env
  310 | 
  311 |     - name: Update controller credentials - {{ content_list }}
  312 |       awx.awx.credential:[REDACTED VALUE BLOCK]
  313 |         [REDACTED ENCRYPTED VALUE]
      [... 6 further identical redacted lines, through 319]
  320 |       # no_log: true
  321 |       delegate_to: localhost
  322 |       loop: "{{ controller_credentials[content_list] }}"
  323 |       when: 
  324 |         - controller_credentials is defined
  325 |         - content_list is defined
  326 |       retries: 10
  327 |       delay: 1
  328 |       tags:
  329 |         # Have to add playground-credentials because of content_list var
  330 |         - setup-playground-credentials
  331 |         - setup-aws-credentials
  332 |         - setup-azure-credentials
  333 | 
  334 |     - name: Setup - create job templates - {{ content_list }}
  335 |       awx.awx.job_template:
  336 |         name: "{{ item.name }}"
  337 |         state: "{{ item.state }}"
  338 |         become_enabled: "{{ item.become_enabled | default(omit)}}"
  339 |         project: "{{ item.project }}"
  340 |         credentials: "{{ item.credentials }}"
  341 |         organization: "{{ item.organization }}"
  342 |         inventory: "{{ item.inventory }}"
  343 |         playbook: "{{ item.playbook }}"
  344 |         survey_spec: "{{ item.survey_spec | default(omit) }}"
  345 |         ask_inventory_on_launch: "{{ item.ask_inventory_on_launch | default(false) }}"
  346 |         ask_limit_on_launch: "{{ item.ask_limit_on_launch | default(omit) }}"
  347 |         extra_vars: "{{ item.extra_vars | default(omit) }}"
  348 |         limit: "{{ item.limit | default(omit) }}"
  349 |         execution_environment: "{{ item.execution_environment }}"
  350 |         job_tags: "{{ item.job_tags | default(omit) }}"
  351 |         <<: *controller_login
  352 |       delegate_to: localhost
  353 |       register: __create_job_templates
  354 |       until: not __create_job_templates.failed
  355 |       retries: 20
  356 |       delay: 1
  357 |       loop: "{{ controller_templates[content_list] }}"
  358 |       when: 
  359 |         - controller_templates[content_list] is defined
  360 |       tags:
  361 |         - setup-monitoring-jt
  362 |         - setup-apache-jt
  363 |         - setup-database-jt
  364 |         - setup-workflow-jt
  365 |         - setup-aws-jt
  366 |         - setup-azure-jt
  367 |         - setup-playground-jt
  368 | 
  369 |     - name: Setup AWS resources
  370 |       delegate_to: localhost
  371 |       tags:
  372 |         - setup-aws-resources
  373 |       block:
  374 |         - name: Create keypair called lightspeed-keypair from instruqt_lab.pub key
  375 |           amazon.aws.ec2_key:
  376 |             name: lightspeed-keypair
  377 |             key_material: "{{ lookup('ansible.builtin.file', '~/.ssh/instruqt_lab.pub') }}"
  378 |             tags:
  379 |               function: lightspeed-demo
  380 | 
  381 |         - name: Create VPC named vpc-lightspeed
```

## Visible variable references

```text
Whole-word search for `__output`: 7 matches in 4 files; 4 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
images/ansible/devops-controller-setup.yml:560:          register: __output
images/ansible/setup-scripts/lightspeed-101/lightspeed-101-lab_setup.yml:286:      register: __output
images/ansible/setup-scripts/lightspeed-101/setup/lightspeed-101-lab_setup.yml:155:      register: __output
tracks/devops-controller/assets/files/gitea/configure_gitea.yml:19:      register: __output

Other references:
images/ansible/devops-controller-setup.yml:561:          changed_when: __output.rc == 0
tracks/devops-controller/assets/files/gitea/configure_gitea.yml:20:      failed_when: __output.rc not in [ 0, 1 ]
tracks/devops-controller/assets/files/gitea/configure_gitea.yml:21:      changed_when: '"user already exists" not in __output.stdout'
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).

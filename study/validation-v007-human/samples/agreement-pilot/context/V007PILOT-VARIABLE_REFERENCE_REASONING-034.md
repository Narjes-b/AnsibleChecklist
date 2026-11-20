# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-034

- Repository: `ansible/instruqt`
- Commit: `e23435acd50f1f645c88958c8dee4fe2929014b6`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `images/ansible/setup-scripts/lightspeed-101/setup/lightspeed-101-lab_setup.yml` (reported anchor line 215)
- Object: `variable` `0a8909cb22292c5edfe144fcc6e8726ff649fdcf297c1c0d495a624d7fbcc10c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 180–250 of 550:

```text
  180 |         - solve-keywords-playbook
  181 |         - solve-external-content-playbook
  182 |         - solve-generate-tasks-playbook
  183 | 
  184 |     - name: Setup - create job templates - {{ content_list }}
  185 |       awx.awx.job_template:
  186 |         name: "{{ item.name }}"
  187 |         state: "{{ item.state }}"
  188 |         become_enabled: "{{ item.become_enabled | default(omit)}}"
  189 |         project: "{{ item.project }}"
  190 |         credentials: "{{ item.credentials }}"
  191 |         organization: "{{ item.organization }}"
  192 |         inventory: "{{ item.inventory }}"
  193 |         playbook: "{{ item.playbook }}"
  194 |         survey_spec: "{{ item.survey_spec | default(omit) }}"
  195 |         ask_inventory_on_launch: "{{ item.ask_inventory_on_launch | default(false) }}"
  196 |         ask_limit_on_launch: "{{ item.ask_limit_on_launch | default(omit) }}"
  197 |         extra_vars: "{{ item.extra_vars | default(omit) }}"
  198 |         limit: "{{ item.limit | default(omit) }}"
  199 |         execution_environment: "{{ item.execution_environment }}"
  200 |         job_tags: "{{ item.job_tags | default(omit) }}"
  201 |         <<: *controller_login
  202 |       register: __create_job_templates
  203 |       until: not __create_job_templates.failed
  204 |       retries: 20
  205 |       delay: 1
  206 |       loop: "{{ controller_templates[content_list] }}"
  207 |       when: 
  208 |         - controller_templates[content_list] is defined
  209 |       tags:
  210 |         - setup-workflow-jt
  211 |         - setup-keywords-jt
  212 |         - setup-external-content-jt
  213 |         - setup-generate-tasks-jt
  214 | 
  215 |     - name: Solve configure-tools VS Code settings
  216 |       ansible.builtin.copy:
  217 |         src: "{{ playbook_dir }}/files/settings_workspace_solve.json"
  218 |         dest: "~{{ student_username }}/{{ gitea_repo_name }}/.vscode/settings.json"
  219 |         owner: "{{ student_username }}"
  220 |         group: "{{ student_username }}"
  221 |         remote_src: true
  222 |         mode: "0644"
  223 |       register: __settings_file
  224 |       tags:
  225 |         - solve-configure-tools
  226 | 
  227 |     - name: Check configure-tools present VS Code settings
  228 |       tags:
  229 |         - check-configure-tools
  230 |       block:
  231 |         - name: Check Lightspeed config present
  232 |           ansible.builtin.lineinfile:
  233 |             path: "~{{ student_username }}/{{ gitea_repo_name }}/.vscode/settings.json"
  234 |             # path: "~{{ student_username }}/.config/Code/User/settings.json"
  235 |             state: absent
  236 |             backrefs: true
  237 |             regex: "{{ item.regex }}"
  238 |             owner: "{{ student_username }}"
  239 |             group: "{{ student_username }}"
  240 |             mode: "0644"
  241 |           check_mode: "{{ check_mode | default(true) }}"
  242 |           register: __vscode_lightspeed
  243 |           loop: "{{ configure_tools['vscode_settings']['present'] }}"
  244 | 
  245 |         - name: Assert __vscode_lightspeed lines found
  246 |           ansible.builtin.assert:
  247 |             that: 
  248 |               - item.found > 0
  249 |             fail_msg: The VS Code .vscode/settings.json missing Lightspeed entries.
  250 |             success_msg: VS Code Lightspeed config entries present.
```

## Visible variable references

```text
e23435acd50f1f645c88958c8dee4fe2929014b6:images/ansible/setup-scripts/lightspeed-101/lightspeed-101-lab_setup.yml:525:      register: __settings_file
e23435acd50f1f645c88958c8dee4fe2929014b6:images/ansible/setup-scripts/lightspeed-101/setup/lightspeed-101-lab_setup.yml:223:      register: __settings_file
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

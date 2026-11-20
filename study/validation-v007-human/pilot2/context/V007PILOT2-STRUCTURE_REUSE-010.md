# Frozen source context: V007PILOT2-STRUCTURE_REUSE-010

- Repository: `Kubeinit/kubeinit`
- Commit: `da6fec314d5594b6bd97ef2e4e71f9098a85e63c`
- Family: structure_reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `kubeinit/roles/kubeinit_services/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`kubeinit/roles/kubeinit_services/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–84 of 84:

```text
    1 | ---
    2 | # Copyright kubeinit contributors
    3 | # All Rights Reserved.
    4 | #
    5 | # Licensed under the Apache License, Version 2.0 (the "License"); you may
    6 | # not use this file except in compliance with the License. You may obtain
    7 | # a copy of the License at
    8 | #
    9 | #     http://www.apache.org/licenses/LICENSE-2.0
   10 | #
   11 | # Unless required by applicable law or agreed to in writing, software
   12 | # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
   13 | # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
   14 | # License for the specific language governing permissions and limitations
   15 | # under the License.
   16 | 
   17 | - name: Prepare the environment and stop the deployment if required
   18 |   block:
   19 |     - name: Prepare environment if not prepared
   20 |       ansible.builtin.include_role:
   21 |         name: kubeinit.kubeinit.kubeinit_prepare
   22 |         public: true
   23 |       vars:
   24 |         environment_prepared: "{{ 'kubeinit_facts' in groups }}"
   25 |       when: not environment_prepared
   26 | 
   27 |     - name: Stop the deployment if required
   28 |       block:
   29 |         - name: "Stop before 'task-create-services' when requested"
   30 |           ansible.builtin.add_host:
   31 |             name: "kubeinit-facts"
   32 |             playbook_terminated: true
   33 |         - name: End play
   34 |           ansible.builtin.meta: end_play
   35 |       when: kubeinit_stop_before_task is defined and kubeinit_stop_before_task == 'task-create-services'
   36 |   tags: omit_from_grapher
   37 | 
   38 | - name: Setup the services pod
   39 |   ansible.builtin.include_tasks: 00_create_service_pod.yml
   40 |   loop: "{{ groups['all_service_nodes'] }}"
   41 |   loop_control:
   42 |     loop_var: kubeinit_deployment_node_name
   43 |   vars:
   44 |     kubeinit_deployment_bridge_name: "{{ hostvars[kubeinit_deployment_node_name].guest_name }}-bridge"
   45 |     kubeinit_deployment_pod_name: "{{ hostvars[kubeinit_deployment_node_name].guest_name }}-pod"
   46 |     kubeinit_deployment_delegate: "{{ hostvars[kubeinit_deployment_node_name].target }}"
   47 | 
   48 | - name: Prepare the credentials we are going to use in the cluster
   49 |   ansible.builtin.include_tasks: prepare_credentials.yml
   50 |   vars:
   51 |     kubeinit_deployment_node_name: "{{ kubeinit_provision_service_node }}"
   52 |     kubeinit_deployment_pod_name: "{{ hostvars[kubeinit_provision_service_node].guest_name }}-pod"
   53 |     kubeinit_deployment_delegate: "{{ hostvars[kubeinit_provision_service_node].target }}"
   54 | 
   55 | - name: Start services containers
   56 |   ansible.builtin.include_tasks: start_services_containers.yml
   57 |   loop: "{{ groups['all_service_nodes'] }}"
   58 |   loop_control:
   59 |     loop_var: kubeinit_deployment_node_name
   60 |   vars:
   61 |     kubeinit_deployment_pod_name: "{{ hostvars[kubeinit_deployment_node_name].guest_name }}-pod"
   62 |     kubeinit_deployment_delegate: "{{ hostvars[kubeinit_deployment_node_name].target }}"
   63 | 
   64 | - name: Gather hosts facts and stop the deployment if required
   65 |   block:
   66 |     - name: Add task-create-services to tasks_completed
   67 |       ansible.builtin.add_host:
   68 |         name: "kubeinit-facts"
   69 |         tasks_completed: "{{ kubeinit_facts_hostvars.tasks_completed | union(['task-create-services']) }}"
   70 | 
   71 |     - name: Update kubeinit_facts_hostvars
   72 |       ansible.builtin.set_fact:
   73 |         kubeinit_facts_hostvars: "{{ hostvars['kubeinit-facts'] }}"
   74 | 
   75 |     - name: Stop the deployment if required
   76 |       block:
   77 |         - name: Stop after 'task-create-services' when requested
   78 |           ansible.builtin.add_host:
   79 |             name: "kubeinit-facts"
   80 |             playbook_terminated: true
   81 |         - name: End play
   82 |           ansible.builtin.meta: end_play
   83 |       when: kubeinit_stop_after_task is defined and kubeinit_stop_after_task in kubeinit_facts_hostvars.tasks_completed
   84 |   tags: omit_from_grapher
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `kubeinit/roles/kubeinit_services`; 16 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: yes

kubeinit/roles/kubeinit_services/README.md
kubeinit/roles/kubeinit_services/defaults/main.yml
kubeinit/roles/kubeinit_services/files/.gitkeep
kubeinit/roles/kubeinit_services/handlers/main.yml
kubeinit/roles/kubeinit_services/meta/main.yml
kubeinit/roles/kubeinit_services/molecule/default/converge.yml
kubeinit/roles/kubeinit_services/molecule/default/molecule.yml
kubeinit/roles/kubeinit_services/molecule/default/verify.yml
kubeinit/roles/kubeinit_services/tasks/00_create_service_pod.yml
kubeinit/roles/kubeinit_services/tasks/create_managed_service.yml
kubeinit/roles/kubeinit_services/tasks/create_provision_container.yml
kubeinit/roles/kubeinit_services/tasks/main.yml
kubeinit/roles/kubeinit_services/tasks/prepare_credentials.yml
kubeinit/roles/kubeinit_services/tasks/prepare_services.yml
kubeinit/roles/kubeinit_services/tasks/start_services_containers.yml
kubeinit/roles/kubeinit_services/vars/main.yml
```

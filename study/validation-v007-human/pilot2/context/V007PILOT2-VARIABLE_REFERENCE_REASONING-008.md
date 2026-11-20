# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-008

- Repository: `ansible/galaxy-operator`
- Commit: `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `roles/galaxy-worker/tasks/main.yml` (reported anchor line 17)
- Flagged construct: variable `_image`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–82 of 82:

```text
    1 | ---
    2 | - name: Apply NetworkPolicy for Hub worker operand pod
    3 |   include_tasks: networkpolicy.yml
    4 | 
    5 | - k8s_status:
    6 |     api_version: "{{ api_version }}"
    7 |     kind: "{{ kind }}"
    8 |     name: "{{ ansible_operator_meta.name }}"
    9 |     namespace: "{{ ansible_operator_meta.namespace }}"
   10 |     conditions:
   11 |       - type: "{{ deployment_type|capitalize }}-Worker-Ready"
   12 |         message: "Starting {{ deployment_type|capitalize }}-worker tasks"
   13 |         reason: StartingTasksExecution
   14 |         status: "False"
   15 |         lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
   16 | 
   17 | - name: Set default galaxy-worker image
   18 |   set_fact:
   19 |     _default_image: "{{ _image }}:{{ _image_version }}"
   20 | 
   21 | - name: Set user provided galaxy-worker image
   22 |   set_fact:
   23 |     _custom_image: "{{ image }}:{{ image_version }}"
   24 |   when:
   25 |     - image is defined and image != ''
   26 |     - image_version is defined and image_version != ''
   27 | 
   28 | - name: Set galaxy-worker image URL
   29 |   set_fact:
   30 |     _image: "{{ _custom_image | default(lookup('env', 'RELATED_IMAGE_GALAXY')) | default(_default_image, true) }}"
   31 | 
   32 | - name: Set node affinity
   33 |   set_fact:
   34 |     _node_affinity: "{{ raw_spec['affinity']['node_affinity'] | default({}) }}"
   35 |   when: affinity is defined and affinity.node_affinity is defined
   36 | 
   37 | - name: Set deployment-specific affinity
   38 |   set_fact:
   39 |     worker_affinity: "{{ raw_spec['worker']['affinity'] | default({}) }}"
   40 |   when: raw_spec['worker']['affinity'] is defined and raw_spec['worker']['affinity'] | length > 0
   41 | 
   42 | - k8s_status:
   43 |     api_version: "{{ api_version }}"
   44 |     kind: "{{ kind }}"
   45 |     name: "{{ ansible_operator_meta.name }}"
   46 |     namespace: "{{ ansible_operator_meta.namespace }}"
   47 |     conditions:
   48 |       - type: "{{ deployment_type|capitalize }}-Worker-Ready"
   49 |         message: "Creating {{ deployment_type|capitalize }}-worker Deployment resource"
   50 |         reason: CreatingDeployment
   51 |         status: "False"
   52 |         lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
   53 | 
   54 | - name: Wait for {{ ansible_operator_meta.name }}-server secret to be created
   55 |   k8s:
   56 |     definition:
   57 |       apiVersion: v1
   58 |       kind: Secret
   59 |       metadata:
   60 |         name: "{{ ansible_operator_meta.name }}-server"
   61 |         namespace: "{{ ansible_operator_meta.namespace }}"
   62 |     wait: yes
   63 |     wait_timeout: 300
   64 | 
   65 | - name: galaxy-worker deployment
   66 |   k8s:
   67 |     state: "{{ deployment_state }}"
   68 |     definition: "{{ lookup('template', 'templates/' + item + '.deployment.yaml.j2') | from_yaml }}"
   69 |   with_items:
   70 |     - galaxy-worker
   71 | 
   72 | - k8s_status:
   73 |     api_version: "{{ api_version }}"
   74 |     kind: "{{ kind }}"
   75 |     name: "{{ ansible_operator_meta.name }}"
   76 |     namespace: "{{ ansible_operator_meta.namespace }}"
   77 |     conditions:
   78 |       - type: "{{ deployment_type|capitalize }}-Worker-Ready"
   79 |         message: "All {{ deployment_type|capitalize }}-worker tasks ran successfully"
   80 |         reason: WorkerTasksFinished
   81 |         status: "True"
   82 |         lastTransitionTime: "{{ lookup('pipe', 'date --iso-8601=seconds') }}"
```

## Visible variable references

```text
Whole-word search for `_image`: 20 matches in 8 files; 4 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
playbooks/galaxy.yaml:46:    _image: quay.io/ansible/galaxy-ng
roles/common/tasks/set_images.yml:15:    _image: "{{ _custom_image | default(lookup('env', 'RELATED_IMAGE_GALAXY')) | default(_default_image, true) }}"
roles/galaxy-content/tasks/main.yml:37:    _image: "{{ _custom_image | default(lookup('env', 'RELATED_IMAGE_GALAXY')) | default(_default_image, true) }}"
roles/galaxy-worker/tasks/main.yml:30:    _image: "{{ _custom_image | default(lookup('env', 'RELATED_IMAGE_GALAXY')) | default(_default_image, true) }}"

Other references:
roles/common/tasks/set_images.yml:4:    _default_image: "{{ _image }}:{{ _image_version }}"
roles/common/templates/labels/version.yaml.j2:1:app.kubernetes.io/version: '{{ _image.split(':')[-1] | truncate(63, True, '', 0) }}'
roles/galaxy-api/templates/galaxy-api.deployment.yaml.j2:161:          image: "{{ _image }}"
roles/galaxy-api/templates/galaxy-api.deployment.yaml.j2:294:          image: {{ _image }}
roles/galaxy-api/templates/galaxy-api.deployment.yaml.j2:336:          image: "{{ _image }}"
roles/galaxy-api/templates/galaxy-api.deployment.yaml.j2:402:          image: "{{ _image }}"
roles/galaxy-api/templates/galaxy-api.deployment.yaml.j2:422:          image: {{ _image }}
roles/galaxy-content/tasks/main.yml:26:    _default_image: "{{ _image }}:{{ _image_version }}"
roles/galaxy-content/templates/galaxy-content.deployment.yaml.j2:136:          image: "{{ _image }}"
roles/galaxy-content/templates/galaxy-content.deployment.yaml.j2:166:          image: "{{ _image }}"
roles/galaxy-content/templates/galaxy-content.deployment.yaml.j2:187:          image: "{{ _image }}"
roles/galaxy-worker/tasks/main.yml:19:    _default_image: "{{ _image }}:{{ _image_version }}"
roles/galaxy-worker/templates/galaxy-worker.deployment.yaml.j2:130:          image: "{{ _image }}"
roles/galaxy-worker/templates/galaxy-worker.deployment.yaml.j2:212:          image: "{{ _image }}"
roles/galaxy-worker/templates/galaxy-worker.deployment.yaml.j2:243:          image: "{{ _image }}"
roles/galaxy-worker/templates/galaxy-worker.deployment.yaml.j2:278:          image: "{{ _image }}"
```

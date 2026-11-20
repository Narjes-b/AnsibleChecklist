# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-021

- Repository: `ansible/zuul-config`
- Commit: `82f3415452ef899524f4257b3cdae20b13692c87`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/redundant-default-value`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/run_awx_tests/tasks/main.yml` (reported anchor line 35)
- Object: `variable` `1c0037c95d7e18336b6d2adabc333bfc6881586640c10d2bed4362ba7b401597`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–69 of 69:

```text
    1 | ---
    2 | - set_fact:
    3 |     image_tag: "awx-pr-{{ zuul.change }}"
    4 |   when: image_tag is not defined
    5 | 
    6 | - set_fact:
    7 |     source_dir: "{{ ansible_user_dir }}/{{ zuul.project.src_dir }}"
    8 |   when: source_dir is not defined
    9 | 
   10 | - set_fact:
   11 |     job_source_dir: "{{ zuul.executor.src_root }}/{{ zuul.project.canonical_name }}"
   12 |   when: job_source_dir is not defined
   13 | 
   14 | - set_fact:
   15 |     target_branch: "{{ zuul.branch }}"
   16 |   when: target_branch is not defined
   17 | 
   18 | - name: Pre-pull images
   19 |   shell: |
   20 |     docker pull quay.io/awx/awx_devel:{{ target_branch }}
   21 |   ignore_errors: yes
   22 | 
   23 | - name: Determine where Dockerfile is
   24 |   stat:
   25 |     path: "{{ source_dir }}/tools/ansible/roles/dockerfile/templates/Dockerfile.j2"
   26 |   register: new_dockerfile_location
   27 | 
   28 | - name: Use new dockerfile role
   29 |   when: new_dockerfile_location.stat.exists
   30 |   block:
   31 |     - include_role:
   32 |         name: "{{ job_source_dir }}/tools/ansible/roles/dockerfile"
   33 |       vars:
   34 |         dockerfile_dest: "{{ source_dir }}"
   35 |         build_dev: yes
   36 | 
   37 | # Delete this in near future.
   38 | - name: Use old dockerfile role
   39 |   when: not new_dockerfile_location.stat.exists
   40 |   block:
   41 |     - include_role:
   42 |         name: "{{ job_source_dir }}/installer/roles/dockerfile"
   43 |       vars:
   44 |         dockerfile_dest: "{{ source_dir }}"
   45 |         build_dev: yes
   46 | 
   47 | - set_fact:
   48 |     command_to_run: |
   49 |       docker build \
   50 |         -t {{ image_tag }} \
   51 |         --build-arg BUILDKIT_INLINE_CACHE=1 \
   52 |         --cache-from {{ image_tag }} \
   53 |         --cache-from quay.io/awx/awx_devel:{{ target_branch }} .
   54 | 
   55 | - name: Build image
   56 |   shell: "{{ command_to_run }}"
   57 |   args:
   58 |     chdir: "{{ source_dir }}"
   59 |   environment:
   60 |     DOCKER_BUILDKIT: '1'
   61 | 
   62 | - set_fact:
   63 |     command_to_run: |
   64 |       docker run -u$(id -u) --rm \
   65 |         -v {{ source_dir }}:/awx_devel/:Z --workdir=/awx_devel \
   66 |         {{ image_tag }} {{ command | quote }}
   67 | 
   68 | - name: Run {{ command }}
   69 |   shell: "{{ command_to_run }}"
```

## Visible variable references

```text
82f3415452ef899524f4257b3cdae20b13692c87:roles/run_awx_tests/defaults/main.yml:2:build_dev: true
82f3415452ef899524f4257b3cdae20b13692c87:roles/run_awx_tests/tasks/main.yml:35:        build_dev: yes
82f3415452ef899524f4257b3cdae20b13692c87:roles/run_awx_tests/tasks/main.yml:45:        build_dev: yes
```

# Frozen source context: V007PILOT-STRUCTURE_REUSE-015

- Repository: `NationalGenomicsInfrastructure/miarka-provision`
- Commit: `52daa7027450753c62cb0f38a2b5ef546cae7ede`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/ngi_pipeline/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `7fa66a3402f68ad8fc6521c943d148c1d6f3beac8e2a1845cb20468555c0df48`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–76 of 76:

```text
    1 | ---
    2 | 
    3 | - name: "Get list of conda environments"
    4 |   shell: "conda env list"
    5 |   register: py_venv_exists
    6 | 
    7 | - name: Setup virtual env with python{{ python3_version }} and install dependencies
    8 |   shell: "conda create -n {{ NGI_venv_name }} pip python={{ python3_version }}"
    9 |   when: not NGI_venv_name in py_venv_exists.stdout|split
   10 | 
   11 | - name: Fetch ngi_pipeline from github
   12 |   git:
   13 |     repo: "{{ ngi_pipeline_repo }}"
   14 |     dest: "{{ ngi_pipeline_dest }}"
   15 |     version: "{{ ngi_pipeline_version }}"
   16 |     force: yes
   17 | 
   18 | - name: Install ngi_pipeline requirements
   19 |   pip:
   20 |     requirements: "{{ ngi_pipeline_dest }}/requirements.txt"
   21 |     executable: "{{ ngi_pipeline_venv }}/bin/pip"
   22 | 
   23 | - name: Install ngi_pipeline
   24 |   pip:
   25 |     name: "file:{{ ngi_pipeline_dest }}"
   26 |     executable: "{{ ngi_pipeline_venv }}/bin/pip"
   27 | 
   28 | - name: Store ngi_pipeline version in deployment
   29 |   lineinfile:
   30 |     dest: "{{ deployed_tool_versions }}"
   31 |     line: "NGI Pipeline: {{ ngi_pipeline_version }}"
   32 | 
   33 | - name: Create ngi_resources/piper folder
   34 |   file:
   35 |     name: "{{ ngi_resources }}/piper"
   36 |     state: directory
   37 | 
   38 | - name: Deploy GATK license key
   39 |   copy:
   40 |     src: files/{{ gatk_key }}
   41 |     dest: "{{ ngi_resources }}/piper/{{ gatk_key }}"
   42 |   ignore_errors: true
   43 | 
   44 | - name: Deploy fastqc conf for miarka
   45 |   template:
   46 |     src: fastq_screen.miarka.conf.j2
   47 |     dest: "{{ ngi_pipeline_conf }}/fastq_screen.miarka.conf"
   48 | 
   49 | - name: Create ngi_pipeline wildwest directory
   50 |   file:
   51 |     path: "{{ proj_root }}"
   52 |     state: directory
   53 |   when: deployment_environment in ["staging", "devel"]
   54 | 
   55 | - name: Deploy miarka ngi_pipeline config for {{ site }}
   56 |   template:
   57 |     src: miarka_ngi_config.yaml.j2
   58 |     dest: "{{ ngi_pipeline_conf }}/{{ ngi_pipeline_config }}"
   59 | 
   60 | - name: Deploy script for creating site specific ngi_pipeline deliverables
   61 |   template:
   62 |     src: create_ngi_pipeline_deliverables.sh.j2
   63 |     dest: "{{ ngi_resources }}/create_ngi_pipeline_deliverables_{{ site }}.sh"
   64 | 
   65 | - name: add static folders to be created
   66 |   set_fact:
   67 |     static_folders: "{{ static_folders + [ngi_log_path, ngi_pipeline_db_path, ngi_softlinks] }}"
   68 | 
   69 | - name: add {{ site }}-specific folders to be created
   70 |   set_fact:
   71 |     static_folders: "{{ static_folders + [[proj_root, uppmax_project, 'genotype_data', 'incoming'] | join('/'), [proj_root, uppmax_project, 'genotype_data', 'archive'] | join('/')] }}"
   72 |   when: site == 'sthlm'
   73 | 
   74 | - name: add static commands to be run
   75 |   set_fact:
   76 |     static_commands: "{{ static_commands + ['. ' ~ ngi_resources ~ '/create_ngi_pipeline_deliverables_' ~ site ~ '.sh'] }}"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/ngi_pipeline/defaults/main.yml
roles/ngi_pipeline/meta/main.yml
roles/ngi_pipeline/tasks/main.yml
roles/ngi_pipeline/templates/create_ngi_pipeline_deliverables.sh.j2
roles/ngi_pipeline/templates/fastq_screen.miarka.conf.j2
roles/ngi_pipeline/templates/miarka_ngi_config.yaml.j2
```

# Frozen source context: V007PILOT-STRUCTURE_REUSE-019

- Repository: `axivo/k3s-cluster`
- Commit: `f0e3a56f57f0e13f9f8624af2bb370c7eb92063f`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/victoria-logs/tasks/validation.yaml` (reported anchor line 1)
- Object: `source_location` `d68c98d2893f20bba5b328f30414c2c28b4ccdce65242b800232a08807005b40`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–135 of 135:

```text
    1 | ---
    2 | - name: Role Facts
    3 |   ansible.builtin.include_role:
    4 |     name: '{{ role }}'
    5 |     tasks_from: facts
    6 |   loop:
    7 |     - external-dns
    8 |     - k3s
    9 |     - victoria-metrics
   10 |     - victoria-logs
   11 |   loop_control:
   12 |     loop_var: role
   13 | 
   14 | - name: Role Validation
   15 |   when: (ansible_run_tags in [(), ('all',)]) or ('victoria-logs' in ansible_run_tags)
   16 |   run_once: true
   17 |   block:
   18 |     - name: Validate project url
   19 |       ansible.builtin.uri:
   20 |         url: '{{ victorialogs_project.url }}/{{ victorialogs_project.tag }}'
   21 |         timeout: 5
   22 |       register: victorialogs_result
   23 |       delay: 1
   24 |       retries: 3
   25 |       until: victorialogs_result is not failed
   26 | 
   27 |     - name: Chart Validation
   28 |       block:
   29 |         - name: Update repository
   30 |           kubernetes.core.helm_repository:
   31 |             name: '{{ victorialogs_vars.kubernetes.helm.repository.org }}'
   32 |             repo_url: '{{ victorialogs_map.helm.repository.url }}'
   33 |             force_update: true
   34 | 
   35 |         - name: Validate cluster kubeconfig path
   36 |           ansible.builtin.stat:
   37 |             path: '{{ k3s_project.cluster.kubeconfig }}'
   38 |           register: victorialogs_kubeconfig
   39 |           changed_when: false
   40 | 
   41 |         - name: Get deployed chart release info
   42 |           kubernetes.core.helm_info:
   43 |             kubeconfig: '{{ k3s_project.cluster.kubeconfig }}'
   44 |             name: '{{ victorialogs_vars.kubernetes.helm.chart.alias }}'
   45 |             namespace: '{{ victorialogs_vars.kubernetes.namespace }}'
   46 |           register: victorialogs_release
   47 |           when: victorialogs_kubeconfig.stat.exists
   48 |           changed_when: false
   49 | 
   50 |         - name: Set comparison fact
   51 |           ansible.builtin.set_fact:
   52 |             victorialogs_comparison:
   53 |               chart: '{{ victorialogs_map.helm.chart.version }}'
   54 |               release: "{{ victorialogs_release.status.chart | default('0') | regex_search('[0-9.]+') }}"
   55 | 
   56 |         - name: Set chart postinstall fact
   57 |           ansible.builtin.set_fact:
   58 |             victorialogs_postinstall: false
   59 | 
   60 |         - name: Validate chart values
   61 |           ansible.builtin.debug:
   62 |             msg: "{{ lookup('ansible.builtin.template', 'values.j2') }}"
   63 | 
   64 |         - name: Set chart values fact
   65 |           ansible.builtin.set_fact:
   66 |             victorialogs_chart_values: "{{ lookup('ansible.builtin.template', 'values.j2') | trim | from_yaml }}"
   67 |           when:
   68 |             - victorialogs_comparison.release is version('0', '>')
   69 |             - victorialogs_comparison.release != victorialogs_comparison.chart
   70 | 
   71 |         - name: Update chart postinstall fact
   72 |           ansible.builtin.set_fact:
   73 |             victorialogs_postinstall: true
   74 | 
   75 |         - name: Validate postinstall chart values
   76 |           ansible.builtin.debug:
   77 |             msg: "{{ lookup('ansible.builtin.template', 'values.j2') }}"
   78 | 
   79 |         - name: Chart Deployment Validation
   80 |           when:
   81 |             - victorialogs_comparison.release is version('0', '>')
   82 |             - victorialogs_comparison.release != victorialogs_comparison.chart
   83 |           block:
   84 |             - name: Update chart values fact
   85 |               ansible.builtin.set_fact:
   86 |                 victorialogs_chart_values: >
   87 |                   {{ victorialogs_chart_values | combine(lookup('ansible.builtin.template', 'values.j2') | trim | from_yaml, recursive=true) }}
   88 | 
   89 |             - name: Simulate chart deployment
   90 |               ansible.builtin.command:
   91 |                 cmd: >-
   92 |                   helm diff upgrade
   93 |                     {{ victorialogs_vars.kubernetes.helm.chart.alias }}
   94 |                     {{ victorialogs_map.helm.chart.reference }}
   95 |                     --kubeconfig {{ k3s_project.cluster.kubeconfig }}
   96 |                     --namespace {{ victorialogs_vars.kubernetes.namespace }}
   97 |                     --version {{ victorialogs_vars.kubernetes.helm.chart.version }}
   98 |                     --context 3 --values -
   99 |                 stdin: '{{ victorialogs_chart_values | to_yaml }}'
  100 |               register: victorialogs_result
  101 |               delay: 1
  102 |               retries: 3
  103 |               until: victorialogs_result is not failed
  104 |               changed_when: false
  105 | 
  106 |             - name: Chart deployment simulation result
  107 |               ansible.builtin.debug:
  108 |                 msg: "{{ victorialogs_result.stdout if victorialogs_result.stdout | length > 0 else 'No chart deployment errors found.' }}"
  109 | 
  110 |             - name: Compare chart values
  111 |               ansible.builtin.command:
  112 |                 cmd: bash -c "{{
  113 |                   ' '.join(['diff', '-u', '<(curl', '-s ' +
  114 |                     '/'.join([victorialogs_map.helm.platform.raw,
  115 |                       victorialogs_vars.kubernetes.helm.repository.org,
  116 |                       victorialogs_vars.kubernetes.helm.repository.name, 'refs', 'tags',
  117 |                       '-'.join([victorialogs_vars.kubernetes.helm.chart.name, victorialogs_comparison.release]), 'charts',
  118 |                       victorialogs_vars.kubernetes.helm.chart.name, 'values.yaml']) + ')',
  119 |                   '<(curl', '-s ' +
  120 |                     '/'.join([victorialogs_map.helm.platform.raw,
  121 |                       victorialogs_vars.kubernetes.helm.repository.org,
  122 |                       victorialogs_vars.kubernetes.helm.repository.name, 'refs', 'tags',
  123 |                       '-'.join([victorialogs_vars.kubernetes.helm.chart.name, victorialogs_comparison.chart]), 'charts',
  124 |                       victorialogs_vars.kubernetes.helm.chart.name, 'values.yaml']) + ')'])
  125 |                   }}"
  126 |               register: victorialogs_result
  127 |               delay: 1
  128 |               retries: 3
  129 |               until: victorialogs_result is not failed
  130 |               changed_when: false
  131 |               failed_when: victorialogs_result.rc > 1
  132 | 
  133 |             - name: Chart values comparison result
  134 |               ansible.builtin.debug:
  135 |                 msg: "{{ victorialogs_result.stdout if victorialogs_result.stdout | length > 0 else 'No chart comparison changes found.' }}"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/victoria-logs/Chart.yaml
roles/victoria-logs/README.md
roles/victoria-logs/README.md.gotmpl
roles/victoria-logs/defaults/main.yaml
roles/victoria-logs/tasks/facts.yaml
roles/victoria-logs/tasks/main.yaml
roles/victoria-logs/tasks/postinstall.yaml
roles/victoria-logs/tasks/reset.yaml
roles/victoria-logs/tasks/upgrade.yaml
roles/victoria-logs/tasks/validation.yaml
roles/victoria-logs/templates/values.j2
```

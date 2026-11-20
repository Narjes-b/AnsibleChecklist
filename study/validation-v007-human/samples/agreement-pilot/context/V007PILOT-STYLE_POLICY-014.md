# Frozen source context: V007PILOT-STYLE_POLICY-014

- Repository: `ansible/awx-operator`
- Commit: `45363a1a0d312d16f740c626407a7521bbe3a31c`
- Family: Style/policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/installer/tasks/install.yml` (reported anchor line 24)
- Object: `task` `f846b94d7ce66a67b738faf3636825fc2b1d21bf63db67c9bbfbf9ab31d6f4e3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–141 of 141:

```text
    1 | ---
    2 | - name: Delete old deployment for before installing during upgrade
    3 |   k8s:
    4 |     kind: Deployment
    5 |     api_version: apps/v1
    6 |     namespace: "{{ ansible_operator_meta.namespace }}"
    7 |     name: "{{ ansible_operator_meta.name }}"
    8 |     state: absent
    9 | 
   10 | - name: Patching labels to AWX kind
   11 |   k8s:
   12 |     state: present
   13 |     definition:
   14 |       apiVersion: '{{ api_version }}'
   15 |       kind: '{{ kind }}'
   16 |       name: '{{ ansible_operator_meta.name }}'
   17 |       namespace: '{{ ansible_operator_meta.namespace }}'
   18 |       metadata:
   19 |         name: '{{ ansible_operator_meta.name }}'
   20 |         namespace: '{{ ansible_operator_meta.namespace }}'
   21 |         labels: '{{ lookup("template", "../common/templates/labels/common.yaml.j2") | from_yaml }}'
   22 |   when: set_self_labels | bool
   23 | 
   24 | - name: Build `additional_labels_items` labels from `additional_labels`
   25 |   block:
   26 |   - name: Look up details for this deployment
   27 |     k8s_info:
   28 |       api_version: "{{ api_version }}"
   29 |       kind: "{{ kind }}"
   30 |       name: "{{ ansible_operator_meta.name }}"
   31 |       namespace: "{{ ansible_operator_meta.namespace }}"
   32 |     register: this_awx
   33 | 
   34 |   - name: Select resource labels which are in `additional_labels`
   35 |     set_fact:
   36 |       additional_labels_items: >-
   37 |         {{ this_awx['resources'][0]['metadata']['labels']
   38 |            | dict2items | selectattr('key', 'in', additional_labels)
   39 |            | list
   40 |         }}
   41 |     when: this_awx['resources'][0]['metadata']['labels']
   42 |   when: additional_labels | length
   43 | 
   44 | - name: Include secret key configuration tasks
   45 |   include_tasks: secret_key_configuration.yml
   46 | 
   47 | - name: Apply Redirect Page Configmap
   48 |   k8s:
   49 |     apply: true
   50 |     definition: "{{ lookup('template', 'configmaps/redirect-page.configmap.html.j2') }}"
   51 |   when: public_base_url is defined
   52 | 
   53 | - name: Set gateway hostname for NO_PROXY exclusion
   54 |   ansible.builtin.set_fact:
   55 |     _gateway_hostname: >-
   56 |       {{ extra_settings | default([]) | selectattr('setting', 'equalto', 'RESOURCE_SERVER')
   57 |          | map(attribute='value') | map(attribute='URL') | select | list | first | default('')
   58 |          | urlsplit('hostname') }}
   59 | 
   60 | - name: Apply proxy environment ConfigMap
   61 |   k8s:
   62 |     apply: true
   63 |     definition: "{{ lookup('template', 'configmaps/proxy-env.configmap.yaml.j2') }}"
   64 |     state: "{{ 'present' if (http_proxy or https_proxy or no_proxy) else 'absent' }}"
   65 | 
   66 | - name: Load LDAP CAcert certificate (Deprecated)
   67 |   include_tasks: load_ldap_cacert_secret.yml
   68 |   when:
   69 |   - ldap_cacert_secret != ''
   70 | 
   71 | - name: Load ldap bind password (Deprecated)
   72 |   include_tasks: load_ldap_password_secret.yml
   73 |   when:
   74 |   - ldap_password_secret != ''
   75 | 
   76 | - name: Load bundle certificate authority certificate
   77 |   include_tasks: load_bundle_cacert_secret.yml
   78 |   when:
   79 |   - bundle_cacert_secret != ''
   80 | 
   81 | - name: Include admin password configuration tasks
   82 |   include_tasks: admin_password_configuration.yml
   83 | 
   84 | - name: Include broadcast websocket configuration tasks
   85 |   include_tasks: broadcast_websocket_configuration.yml
   86 | 
   87 | - name: Include set_images tasks
   88 |   include_tasks: set_images.yml
   89 | 
   90 | - name: Include Database tasks
   91 |   include_tasks: database.yml
   92 | 
   93 | - name: Apply NetworkPolicies for AWX operand pods
   94 |   include_tasks: networkpolicy.yml
   95 | 
   96 | - name: Load Route TLS certificate
   97 |   include_tasks: load_route_tls_secret.yml
   98 |   when:
   99 |   - ingress_type | lower == 'route'
  100 |   - route_tls_secret != ''
  101 | 
  102 | - name: Wait for {{ deployment_type }}restore to complete
  103 |   kubernetes.core.k8s_info:
  104 |     api_version: "{{ api_version }}"
  105 |     kind: "{{ deployment_type }}restore"
  106 |     namespace: "{{ ansible_operator_meta.namespace }}"
  107 |   register: restore_status_check
  108 |   until:
  109 |   # yamllint disable-line rule:line-length
  110 |   - (restore_status_check.resources | length == 0) or (restore_status_check.resources | selectattr('spec.deployment_name', 'equalto', ansible_operator_meta.name) | map(attribute='status') | selectattr('restoreComplete', 'defined') | map(attribute='restoreComplete') | list | length > 0)
  111 |   delay: 10
  112 |   retries: 8640
  113 |   ignore_errors: yes
  114 |   changed_when: false
  115 | 
  116 | - name: Include resources configuration tasks
  117 |   include_tasks: resources_configuration.yml
  118 | 
  119 | - name: Migrate database to the latest schema
  120 |   include_tasks: migrate_schema.yml
  121 |   when: awx_web_pod_name != ''
  122 | 
  123 | - name: Initialize Django
  124 |   include_tasks: initialize_django.yml
  125 |   when: awx_web_pod_name != ''
  126 | 
  127 | - name: Enable optional metrics-utility
  128 |   include_tasks: enable_metrics_utility.yml
  129 | 
  130 |   when: _metrics_utility_enabled | default(false) | bool
  131 | 
  132 | - name: Enable optional metrics-utility for Redhat Console
  133 |   include_tasks: enable_metrics_utility_console.yml
  134 |   when: _metrics_utility_console_enabled | default(false) | bool
  135 | 
  136 | - name: Update status variables
  137 |   include_tasks: update_status.yml
  138 |   when: update_status | bool
  139 | 
  140 | - name: Cleanup & Set garbage collection refs
  141 |   include_tasks: cleanup.yml
```

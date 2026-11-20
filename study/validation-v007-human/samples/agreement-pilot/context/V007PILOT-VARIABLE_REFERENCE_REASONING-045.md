# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-045

- Repository: `azimuth-cloud/ansible-collection-azimuth-ops`
- Commit: `396972118edcecb213e69497f9f2c70e7abd0611`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unnecessary-set-fact`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/certmanager/tasks/main.yml` (reported anchor line 106)
- Object: `variable` `e912ebf12b327c9f0aea8e34364f6f0449758b0871cbdbdb29bf7b098d2d2bf2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–124 of 124:

```text
    1 | ---
    2 | - name: Create cert-manager release namespace
    3 |   ansible.builtin.command: kubectl create namespace {{ certmanager_release_namespace }}
    4 |   register: certmanager_create_namespace
    5 |   changed_when: certmanager_create_namespace.rc == 0
    6 |   failed_when: >-
    7 |     certmanager_create_namespace.rc != 0 and
    8 |     'AlreadyExists' not in certmanager_create_namespace.stderr
    9 | 
   10 | - name: Install trust bundle
   11 |   ansible.builtin.command: kubectl apply -f -
   12 |   args:
   13 |     stdin: "{{ certmanager_trust_bundle_configmap_definition | to_nice_yaml }}"
   14 |   vars:
   15 |     certmanager_trust_bundle_configmap_definition:
   16 |       apiVersion: v1
   17 |       kind: ConfigMap
   18 |       metadata:
   19 |         name: "{{ certmanager_trust_bundle_configmap_name }}"
   20 |         namespace: "{{ certmanager_release_namespace }}"
   21 |       data:
   22 |         ca-certificates.crt: "{{ certmanager_trust_bundle }}"
   23 |   when: certmanager_trust_bundle
   24 |   register: kubectl_install_trust_bundle
   25 |   changed_when: kubectl_install_trust_bundle.stdout_lines | select('match', '(?!.*unchanged$)') | length > 0
   26 | 
   27 | - name: Install cert-manager on target Kubernetes cluster
   28 |   kubernetes.core.helm:
   29 |     chart_ref: "{{ certmanager_chart_name }}"
   30 |     chart_repo_url: "{{ certmanager_chart_repo }}"
   31 |     chart_version: "{{ certmanager_chart_version }}"
   32 |     release_namespace: "{{ certmanager_release_namespace }}"
   33 |     release_name: "{{ certmanager_release_name }}"
   34 |     release_values: "{{ certmanager_release_values }}"
   35 |     atomic: true
   36 |     create_namespace: true
   37 |     wait: true
   38 |     wait_timeout: "{{ certmanager_wait_timeout }}"
   39 | 
   40 | - name: Configure certmanager grafana dashboard
   41 |   when: certmanager_monitoring_enabled
   42 |   block:
   43 |     - name: Install Grafana dashboard for cert-manager metrics
   44 |       ansible.builtin.command: kubectl apply -f -
   45 |       args:
   46 |         stdin: "{{ certmanager_dashboard_definition | to_nice_yaml }}"
   47 |       vars:
   48 |         certmanager_dashboard_definition:
   49 |           apiVersion: v1
   50 |           kind: ConfigMap
   51 |           metadata:
   52 |             name: cert-manager-grafana-dashboard
   53 |             namespace: "{{ certmanager_release_namespace }}"
   54 |             labels:
   55 |               grafana_dashboard: "1"
   56 |           data:
   57 |             certmanager_dashboard.json: |-
   58 |               {{ lookup("file", "grafana_dashboard.json") | from_json | to_nice_json }}
   59 |       register: kubectl_install_certmanager_dashboard
   60 |       changed_when: kubectl_install_certmanager_dashboard.stdout_lines | select('match', '(?!.*unchanged$)') | length > 0
   61 | 
   62 |     - name: Configure custom alerting rules for cert-manager
   63 |       ansible.builtin.command: kubectl apply -f -
   64 |       args:
   65 |         stdin: "{{ lookup('template', 'prometheusrule.yaml.j2') }}"
   66 |       register: kubectl_install_certmanager_alert_rules
   67 |       changed_when: kubectl_install_certmanager_alert_rules.stdout_lines | select('match', '(?!.*unchanged$)') | length > 0
   68 | 
   69 | - name: Configure EAB credentials
   70 |   when: >-
   71 |     certmanager_acmehttp01issuer_enabled and
   72 |     certmanager_acmehttp01issuer_eab_required and
   73 |     not certmanager_acmehttp01issuer_eab_kid
   74 |   block:
   75 |     - name: Check if EAB secret exists
   76 |       ansible.builtin.command: >-
   77 |         kubectl get secret {{ certmanager_acmehttp01issuer_eab_secret_name }}
   78 |           --namespace {{ certmanager_release_name }}
   79 |           --output json
   80 |       register: certmanager_acmehttp01issuer_eab_secret_cmd
   81 |       changed_when: false
   82 |       failed_when: >-
   83 |         certmanager_acmehttp01issuer_eab_secret_cmd.rc != 0 and
   84 |         "NotFound" not in certmanager_acmehttp01issuer_eab_secret_cmd.stderr
   85 | 
   86 |     - name: Set EAB credential facts from secret
   87 |       ansible.builtin.set_fact:
   88 |         certmanager_acmehttp01issuer_eab_kid: >-
   89 |           {{ (certmanager_acmehttp01issuer_eab_secret_cmd.stdout | from_json).data.kid | b64decode }}
   90 |         certmanager_acmehttp01issuer_eab_key: >-
   91 |           {{ (certmanager_acmehttp01issuer_eab_secret_cmd.stdout | from_json).data.key | b64decode }}
   92 |       when: certmanager_acmehttp01issuer_eab_secret_cmd.rc =[REDACTED_LITERAL]
   93 | 
   94 |     - name: Generate EAB credentials and set facts based on response
   95 |       when: certmanager_acmehttp01issuer_eab_secret_cmd.rc != 0
   96 |       block:
   97 |         - name: Generate EAB credentials
   98 |           ansible.builtin.uri:
   99 |             url: "{{ certmanager_acmehttp01issuer_eab_generate_url }}"
  100 |             method: POST
  101 |           register: certmanager_acmehttp01issuer_eab_credentials
  102 | 
  103 |         - name: Set EAB credential facts from response
  104 |           ansible.builtin.set_fact:
  105 |             certmanager_acmehttp01issuer_eab_kid: "{{ certmanager_acmehttp01issuer_eab_credentials.json.eab_kid }}"
  106 |             certmanager_acmehttp01issuer_eab_key: "{{ certmanager_acmehttp01issuer_eab_credentials.json.eab_hmac_key }}"
  107 | 
  108 | - name: Configure ACME HTTP01 cluster issuer and set ingress annotation fact
  109 |   when: certmanager_acmehttp01issuer_enabled
  110 |   block:
  111 |     - name: Install ACME HTTP01 cluster issuer
  112 |       ansible.builtin.command: kubectl apply -f -
  113 |       args:
  114 |         stdin: "{{ item | to_nice_yaml }}"
  115 |       register: kubectl_install_http01_cluster_issuer
  116 |       changed_when: kubectl_install_http01_cluster_issuer.stdout_lines | select('match', '(?!.*unchanged$)') | length > 0
  117 |       loop: "{{ certmanager_acmehttp01issuer_manifests }}"
  118 |       loop_control:
  119 |         label: "{{ item.kind }}"
  120 | 
  121 |     - name: Set auto-TLS facts
  122 |       ansible.builtin.set_fact:
  123 |         certmanager_ingress_annotations:
  124 |           cert-manager.io/cluster-issuer: "{{ certmanager_acmehttp01issuer_name }}"
```

## Visible variable references

```text
396972118edcecb213e69497f9f2c70e7abd0611:roles/certmanager/defaults/main.yml:88:certmanager_acmehttp01issuer_eab_key:
396972118edcecb213e69497f9f2c70e7abd0611:roles/certmanager/defaults/main.yml:106:    key: "{{ certmanager_acmehttp01issuer_eab_key }}"
396972118edcecb213e69497f9f2c70e7abd0611:roles/certmanager/tasks/main.yml:90:        certmanager_acmehttp01issuer_eab_key: >-
396972118edcecb213e69497f9f2c70e7abd0611:roles/certmanager/tasks/main.yml:106:            certmanager_acmehttp01issuer_eab_key: "{{ certmanager_acmehttp01issuer_eab_credentials.json.eab_hmac_key }}"
```

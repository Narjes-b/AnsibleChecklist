# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-003

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/redundant-default-value`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `roles/eco_gotests/tasks/ptp.yml` (reported anchor line 51)
- Flagged construct: variable `eco_gotests_generic_env`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–56 of 56:

```text
    1 | ---
    2 | - name: "PTP prerequisites checks"
    3 |   when: eco_gotests_ptp_check_prerequisites | bool
    4 |   block:
    5 |     - name: "Check PTP prerequisites - PtpOperatorConfig"
    6 |       kubernetes.core.k8s_info:
    7 |         api_version: ptp.openshift.io/v1
    8 |         kind: PtpOperatorConfig
    9 |         name: default
   10 |         namespace: openshift-ptp
   11 |       register: _eco_gotests_ptp_operator_config
   12 |       failed_when: false
   13 | 
   14 |     - name: "Validate PTP prerequisites - enableEventPublisher"
   15 |       ansible.builtin.assert:
   16 |         that:
   17 |           - _eco_gotests_ptp_operator_config.resources is defined
   18 |           - _eco_gotests_ptp_operator_config.resources | length > 0
   19 |           - _eco_gotests_ptp_operator_config.resources[0].spec.ptpEventConfig is defined
   20 |           - _eco_gotests_ptp_operator_config.resources[0].spec.ptpEventConfig.enableEventPublisher | default(false) == true
   21 |         fail_msg: "PTP prerequisite check failed: spec.ptpEventConfig.enableEventPublisher must be true"
   22 |         success_msg: "PTP prerequisite check passed: [REDACTED_LITERAL]
   23 | 
   24 |     - name: "Validate PTP prerequisites - apiVersion"
   25 |       ansible.builtin.assert:
   26 |         that:
   27 |           - _eco_gotests_ptp_operator_config.resources is defined
   28 |           - _eco_gotests_ptp_operator_config.resources | length > 0
   29 |           - _eco_gotests_ptp_operator_config.resources[0].spec.ptpEventConfig is defined
   30 |           - _eco_gotests_ptp_operator_config.resources[0].spec.ptpEventConfig.apiVersion | default("") == "2.0"
   31 |         fail_msg: "PTP prerequisite check failed: spec.ptpEventConfig.apiVersion must be '2.0'"
   32 |         success_msg: "PTP prerequisite check passed: [REDACTED_LITERAL]
   33 | 
   34 | - name: "Show relevant PTP variables for verification"
   35 |   ansible.builtin.debug:
   36 |     msg:
   37 |       eco_gotests_image: "{{ eco_gotests_image }}"
   38 |       eco_gotests_kubconfig_dir: "{{ eco_gotests_kubconfig_dir }}"
   39 |       eco_gotests_log_dir: "{{ eco_gotests_log_dir }}"
   40 |       eco_gotests_eco_test_features_ptp: "{{ eco_gotests_eco_test_features_ptp }}"
   41 |       eco_gotests_registry_auth_file: "{{ eco_gotests_registry_auth_file }}"
   42 |       eco_gotests_run_labels_ptp: "{{ eco_gotests_run_labels_ptp | default([]) }}"
   43 |       eco_gotests_skip_labels_ptp: "{{ eco_gotests_skip_labels_ptp | default([]) }}"
   44 |       eco_gotests_ptp_run_timeout_sec: "{{ eco_gotests_ptp_run_timeout_sec }}"
   45 | 
   46 | - name: "Map PTP variables to generic runner"
   47 |   ansible.builtin.set_fact:
   48 |     eco_gotests_generic_features: "{{ eco_gotests_eco_test_features_ptp }}"
   49 |     eco_gotests_generic_run_labels: "{{ eco_gotests_run_labels_ptp }}"
   50 |     eco_gotests_generic_skip_labels: "{{ eco_gotests_skip_labels_ptp }}"
   51 |     eco_gotests_generic_env: {}
   52 |     eco_gotests_generic_timeout: "{{ eco_gotests_ptp_run_timeout_sec }}s"
   53 |     eco_gotests_generic_run_label_operator: '&&'
   54 | 
   55 | - name: "Run PTP tests via generic runner"
   56 |   ansible.builtin.include_tasks: generic.yml
```

## Visible variable references

```text
Whole-word search for `eco_gotests_generic_env`: 4 matches in 4 files; 3 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
roles/eco_gotests/defaults/main.yml:40:eco_gotests_generic_env: {}
roles/eco_gotests/tasks/ptp.yml:51:    eco_gotests_generic_env: {}
roles/eco_gotests/tasks/sriov.yml:7:    eco_gotests_generic_env:

Other references:
roles/eco_gotests/tasks/generic.yml:45:    env: "{{ _eco_gotests_generic_base_env | combine(eco_gotests_generic_env) }}"
```

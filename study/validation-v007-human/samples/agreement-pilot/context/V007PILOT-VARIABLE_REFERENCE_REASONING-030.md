# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-030

- Repository: `ansible/awx-operator`
- Commit: `45363a1a0d312d16f740c626407a7521bbe3a31c`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/role-variable-precedence-collision`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/installer/vars/main.yml` (reported anchor line 7)
- Object: `variable` `bb520baec77631ae9964698b5a2ed3fd1ba9d98ff1bca9e6c78c501fca7425eb`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–26 of 26:

```text
    1 | ---
    2 | postgres_initdb_args: '--auth-host=scram-sha-256'
    3 | postgres_host_auth_method: 'scram-sha-256'
    4 | # LDAP is deprecated
    5 | ldap_cacert_ca_crt: ''
    6 | bundle_ca_crt: ''
    7 | projects_existing_claim: ''
    8 | supported_pg_version: 15
    9 | _previous_upgraded_pg_version: 0
   10 | old_postgres_pod: []
   11 | _postgres_data_path: '/var/lib/pgsql/data/userdata'
   12 | # metrics-utility (github.com/ansible/metrics-utility)
   13 | _metrics_utility_enabled: "{{ metrics_utility_enabled | default(false) }}"
   14 | _metrics_utility_configmap: "{{ metrics_utility_configmap | default(deployment_type + '-metrics-utility-configmap') }}"
   15 | _metrics_utility_console_enabled: "{{ metrics_utility_console_enabled | default(false) }}"
   16 | _metrics_utility_image: "{{ metrics_utility_image | default(_image) }}"
   17 | _metrics_utility_image_version: "{{ metrics_utility_image_version | default(_image_version) }}"
   18 | _metrics_utility_image_pull_policy: "{{ metrics_utility_image_pull_policy | default('IfNotPresent') }}"
   19 | _metrics_utility_ship_target: "{{ metrics_utility_ship_target | default('directory') }}"
   20 | _metrics_utility_pvc_claim: "{{ metrics_utility_pvc_claim | default(deployment_type + '-metrics-utility') }}"
   21 | _metrics_utility_pvc_claim_size: "{{ metrics_utility_pvc_claim_size | default('5Gi') }}"
   22 | _metrics_utility_cronjob_gather_schedule: "{{ metrics_utility_cronjob_gather_schedule | default('@hourly') }}"
   23 | _metrics_utility_cronjob_report_schedule: "{{ metrics_utility_cronjob_report_schedule | default('@monthly') }}"
   24 | 
   25 | # version check
   26 | gating_version: ''
```

## Visible variable references

```text
45363a1a0d312d16f740c626407a7521bbe3a31c:config/crd/bases/awx.ansible.com_awxs.yaml:1914:              projects_existing_claim:
45363a1a0d312d16f740c626407a7521bbe3a31c:config/manifests/bases/awx-operator.clusterserviceversion.yaml:786:        path: projects_existing_claim
45363a1a0d312d16f740c626407a7521bbe3a31c:roles/installer/defaults/main.yml:434:projects_existing_claim: ''
45363a1a0d312d16f740c626407a7521bbe3a31c:roles/installer/templates/deployments/task.yaml.j2:632:{% if projects_existing_claim %}
45363a1a0d312d16f740c626407a7521bbe3a31c:roles/installer/templates/deployments/task.yaml.j2:633:            claimName: {{ projects_existing_claim }}
45363a1a0d312d16f740c626407a7521bbe3a31c:roles/installer/templates/deployments/web.yaml.j2:499:{% if projects_existing_claim %}
45363a1a0d312d16f740c626407a7521bbe3a31c:roles/installer/templates/deployments/web.yaml.j2:500:            claimName: {{ projects_existing_claim }}
45363a1a0d312d16f740c626407a7521bbe3a31c:roles/installer/templates/storage/persistent.yaml.j2:1:{% if projects_persistence|bool and projects_existing_claim == '' %}
45363a1a0d312d16f740c626407a7521bbe3a31c:roles/installer/vars/main.yml:7:projects_existing_claim: ''
```

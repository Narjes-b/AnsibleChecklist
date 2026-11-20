# AnsibleGuard v0.0.7.1 full reproducible run

Run identity: `v0071-rerun-2026-10-22`.  The canonical command uses exactly 4 concurrent repository jobs.

## Reproducibility identity

See `run-manifest.json`, `environment/`, `inputs/`, and `checksums/outputs.sha256`.

## Execution health

Targeted repositories: 207. Complete: 171; partial: 35; failed: 1. Provider and repository state are in `tables/repository-execution-status.csv`.

## Main result totals

Raw findings: 389924.  Canonical occurrences: 373923.  Internal and external-provider totals remain separate in `tables/findings-by-provider.csv`.

## Results and caveats

Rule, repository, provider, severity, confidence, uncertainty, runtime, and failure tables are in `tables/`; all chart source data is in `charts/data/`. Incomplete scans are explicit missing observations, never zero findings.

### Incomplete scans

| Repository | Status | Provider state | Error |
|---|---|---|---|
| ansible-collections/ibm_zos_core | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| ansible-lockdown/RHEL7-STIG | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| ansible/instruqt | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| azimuth-cloud/ansible-collection-azimuth-ops | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| bitsy-ai/ansible-collection-printnanny | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| braucktoon/home-services-ansible-automation | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| CentOS-PaaS-SIG/linchpin | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| ceph/ceph-ansible | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| ceph/ceph-cm-ansible | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| cfpb/aurora | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| cisco-en-programmability/dnacenter-ansible | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| clincha-org/clincha | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| dimagi/commcare-cloud | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| encapsulate-xyz/cosmos-ansible | failed | ansibleguard=missing;ansible-lint=missing;gitleaks=missing | RuntimeError: AnsibleGuard timed out after 1800 seconds for encapsulate-xyz/cosmos-ansible; see /home/aymmzn/Documents/AnsibleChecklist/study/runs/v0071-rerun-2026-10-22/logs/encapsulate-xyz__cosmos-ansible__a49d30281d2d.log |
| ergho/homelab-ops | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| JenswBE/setup | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| jlu5/ansible-dn42 | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| Kubeinit/kubeinit | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| openshift/openshift-ansible | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| progmaticltd/homebox | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| pulibrary/princeton_ansible | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| redhat-openstack/infrared | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| RedHatGov/redhatgov.workshops | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| rtdevx/homelab | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| sdwilsh/ansible-playbooks | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| SkynetLabs/ansible-playbooks | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| snowdrop/k8s-infra | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| snyssen/infra-snyssen.be | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| splunk/splunk-ansible | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| stuttgart-things/ansible | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| trilioData/triliovault-cfg-scripts | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| usegalaxy-au/infrastructure | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| usegalaxy-eu/infrastructure-playbook | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| usegalaxy-eu/vgcn | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| vexxhost/atmosphere | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |
| wonderbird/ansible-all-my-things | partial | ansibleguard=completed;ansible-lint=partial;gitleaks=completed |  |

## What these results do not prove

This execution alone does **not** establish precision, recall, F1, human agreement, correctness of candidate thresholds, or generalization beyond the selected frozen population. No threshold-validation conclusion is made here.

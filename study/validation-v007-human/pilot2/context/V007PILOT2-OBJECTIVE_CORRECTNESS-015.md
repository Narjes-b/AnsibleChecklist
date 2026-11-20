# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-015

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: objective_correctness
- Rule: `ansibleguard/invalid-task-attribute-type`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `ansible/playbook/kubernetes/k8s_remove.yml` (reported anchor line 23)
- Flagged construct: attribute `vars`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–39 of 39:

```text
    1 | ---
    2 | - name: "Uninstall kubernetes modules"
    3 |   hosts: "{{ override_host | default('masters') }}"
    4 |   gather_facts: "{{ gathering_host_info | default('true') | bool == true }}"
    5 | 
    6 |   # Define default values for variables that are common between roles
    7 |   vars:
    8 |     client_tool: kubectl
    9 | 
   10 |   tasks:
   11 |     - name: "Execute k8s_dashboard uninstall role"
   12 |       import_role:
   13 |         name: 'k8s_dashboard'
   14 |       vars:
   15 |         - remove: true
   16 | 
   17 |     - name: "Execute Ingress Controller uninstall role"
   18 |       import_role:
   19 |         name: 'ingress'
   20 |       vars:
   21 |         - remove: true
   22 | 
   23 |     - name: "Execute k8s_cluster uninstall role"
   24 |       import_role:
   25 |         name: 'k8s_cluster'
   26 |       vars:
   27 |         - remove: true
   28 | 
   29 |     - name: "Execute docker uninstall role"
   30 |       import_role:
   31 |         name: 'docker'
   32 |       vars:
   33 |         state: 'absent'
   34 | 
   35 |     - name: "Execute containerd uninstall role"
   36 |       import_role:
   37 |         name: 'containerd'
   38 |       vars:
   39 |         state: 'absent'
```

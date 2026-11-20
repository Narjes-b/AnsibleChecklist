# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-014

- Repository: `ansible/zuul-config`
- Commit: `82f3415452ef899524f4257b3cdae20b13692c87`
- Family: maintainability_complexity
- Rule: `ansibleguard/complex-playbook`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `playbooks/openshift/pre.yaml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`playbooks/openshift/pre.yaml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–34 of 34:

```text
    1 | ---
    2 | - hosts: localhost
    3 |   tasks:
    4 |     - block:
    5 |         - import_role: name=emit-job-header
    6 |         # We need those tasks to use log-inventory, see: https://review.openstack.org/577674
    7 |         - name: Define zuul_info_dir fact
    8 |           set_fact:
    9 |             zuul_info_dir: "{{ zuul.executor.log_root }}/zuul-info"
   10 | 
   11 |         - name: Ensure Zuul Ansible directory exists
   12 |           delegate_to: localhost
   13 |           run_once: true
   14 |           file:
   15 |             path: "{{ zuul_info_dir }}"
   16 |             state: directory
   17 | 
   18 |         - name: Define inventory_file fact
   19 |           set_fact:
   20 |             inventory_file: "/tmp/{{ zuul.build }}/ansible/inventory.yaml"
   21 | 
   22 |         - import_role: name=log-inventory
   23 |       vars:
   24 |         zuul_log_url: "https://gateway-cloud-softwarefactory.apps.ocp.cloud.ci.centos.org/logs"
   25 | 
   26 |     - name: Set oc_command fact
   27 |       set_fact:
   28 |         oc_command: >
   29 |           oc --context "{{ zuul.resources['project'].context }}"
   30 |              --namespace "{{ zuul.resources['project'].namespace }}"
   31 | 
   32 |     - include_tasks: prepare-namespace.yaml
   33 |     - include_tasks: build-project.yaml
   34 |     - include_tasks: deploy-project.yaml
```

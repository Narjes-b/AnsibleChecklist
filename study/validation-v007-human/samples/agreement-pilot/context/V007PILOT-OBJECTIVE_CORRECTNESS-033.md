# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-033

- Repository: `CentOS-PaaS-SIG/linchpin`
- Commit: `0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f`
- Family: Objective correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `dev_setup/playbooks/roles/pipeline/tasks/set_oc_client.yml` (reported anchor line 3)
- Object: `source_location` `832b364631ec74e8e1910436ccd03dd227f61601f99f95c4f401289b0f651503`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–18 of 18:

```text
    1 | ---
    2 | # set the oc client for the minishift cluster
    3 | - name: "Determine the oc client is for profile {{ profile}}"
    4 |   shell: "minishift oc-env --profile {{ profile }} | head -1"
    5 |   register: oc_client_path
    6 | 
    7 | - name: Update the path with the oc client
    8 |   shell: "{{ oc_client_path.stdout }}"
    9 | 
   10 | - name: "Set path for oc client in {{ ansible_env.HOME }}/.bashrc"
   11 |   lineinfile:
   12 |     path: "{{ ansible_env.HOME }}/.bashrc"
   13 |     line: '{{ oc_client_path.stdout }}'
   14 |     create: yes
   15 | 
   16 | - name: "Source {{ ansible_env.HOME }}/.bashrc"
   17 |   shell: source {{ ansible_env.HOME }}/.bashrc
   18 | 
```

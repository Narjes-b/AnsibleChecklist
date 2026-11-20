# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-016

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: objective_correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `ansible/roles/bie-hub/tasks/docker-tasks.yml` (reported anchor line 2)
- Flagged construct: not named by the finding; the anchor line 2 lies in the task at line 2, name `ensure target db directories exist`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–15 of 15:

```text
    1 | ---
    2 | - name: ensure target db directories exist
    3 |   file: path={{item}} state=directory
    4 |   with_items:
    5 |     - "{{ bie_hub_docker_dir }}"
    6 |   run_once: true
    7 |   tags:
    8 |     - docker
    9 |     - docker-service
   10 | 
   11 | - name: Deploy bie_hub stack
   12 |   import_tasks: ../../docker-common/tasks/stack-create.yml
   13 |   vars:
   14 |     stack: la_bie_hub
   15 |     docker_compose_data_dir: "{{ bie_hub_docker_dir }}"
```

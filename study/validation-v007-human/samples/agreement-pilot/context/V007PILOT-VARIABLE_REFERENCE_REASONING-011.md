# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-011

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/overriding-facts`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `playbooks/primary_sr_switchover_cp_to_cc.yml` (reported anchor line 1)
- Object: `source_location` `78188af614693715e5661ed1e9eaa4a46dcd41f8453fe3c3a3e57ceac12c1820`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–36 of 546:

```text
    1 | ---
    2 | - import_playbook: validations/primary_sr_switchover_validations.yml
    3 |   tags:
    4 |     - validate
    5 |     - always
    6 | 
    7 | # Schema Registry Automation Workflow
    8 | #
    9 | # Default behavior (no tags):
   10 | #   - Runs only Schema Exporter setup on CP SR
   11 | #
   12 | # Run specific phases:
   13 | #   ansible-playbook primary_sr_switchover_cp_to_cc.yml --tags "schema_exporter"
   14 | #   ansible-playbook primary_sr_switchover_cp_to_cc.yml --tags "forward_to_cc"
   15 | #   ansible-playbook primary_sr_switchover_cp_to_cc.yml --tags "schema_importer"
   16 | #
   17 | # Run switchover to CC and enable reverse sync:
   18 | #   ansible-playbook primary_sr_switchover_cp_to_cc.yml --tags "switchover_to_cc"
   19 | #
   20 | # Available tags:
   21 | #   - validate: Pre-flight validation
   22 | #   - schema_exporter: Setup schema exporter
   23 | #   - forward_to_cc: Perform SR switchover
   24 | #   - schema_importer: Setup schema importer (reverse sync)
   25 | #   - switchover_to_cc: Run switchover and reverse sync in addition to exporter
   26 | 
   27 | - name: Schema Registry Automation Workflow Prerequisites
   28 |   hosts: schema_registry
   29 |   gather_facts: true
   30 |   vars:
   31 |     # Status tracking
   32 |     workflow_status: "started"
   33 |     failed_step: ""
   34 | 
   35 |   tasks:
   36 |     - import_role:
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

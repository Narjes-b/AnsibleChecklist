# Frozen source context: V007PILOT-STYLE_POLICY-029

- Repository: `dryvist/ansible-proxmox-apps`
- Commit: `b179574eb875a6b7be09df83d001f623a68a2681`
- Family: Style/policy
- Rule: `ansibleguard/molecule-test-absent`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/technitium_dns/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `f535758b0ddf5c05186b9c47faef6282f73795b873e66960b17480bfd02cd24b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–21 of 21:

```text
    1 | ---
    2 | # Technitium DNS Configuration Tasks
    3 | # Configures internal DNS zone with A records for all infrastructure hosts
    4 | 
    5 | - name: Validate required variables and authenticate to this node's API
    6 |   ansible.builtin.include_tasks: main/validate_and_auth.yml
    7 | 
    8 | - name: Build A-record data from inventory and resolve group topology
    9 |   ansible.builtin.include_tasks: main/build_records.yml
   10 | 
   11 | - name: Configure upstream forwarders and create the DNS zones
   12 |   ansible.builtin.include_tasks: main/forwarders_and_zones.yml
   13 | 
   14 | - name: Create/prune infrastructure A records and service CNAME aliases
   15 |   ansible.builtin.include_tasks: main/infra_a_records.yml
   16 | 
   17 | - name: Probe the ingress VIP and write the Traefik/Proxmox apex records
   18 |   ansible.builtin.include_tasks: main/ingress_and_apex.yml
   19 | 
   20 | - name: Verify the zone is active and configure the health-checked apex
   21 |   ansible.builtin.include_tasks: main/health_check.yml
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-019

- Repository: `dell/dellemc-openmanage-ansible-modules`
- Commit: `1f35059202d432465b8bd54e980d069a88583edc`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-play`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/ome/template/ome_template_network_vlan.yml` (reported anchor line 2)
- Object: `source_location` `113a28439e8e80dc13bdcf1637e2cb12c5e2c0e979e321858b55443aedb82369`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–64 of 64:

```text
    1 | ---
    2 | - name: Dell OpenManage Ansible template tag and untag.
    3 |   hosts: ome
    4 |   gather_facts: false
    5 | 
    6 |   tasks:
    7 |     - name: Tag or untag vlans in template
    8 |       dellemc.openmanage.ome_template_network_vlan:
    9 |         hostname: "{{ hostname }}"
   10 |         username: "{{ username }}"
   11 |         password: "{{ password }}"
   12 |         ca_path: "/path/to/ca_cert.pem"
   13 |         template_id: 78
   14 |         nic_identifier: NIC Slot 4
   15 |         untagged_networks:
   16 |           - port: 1
   17 |             untagged_network_id: 12765
   18 |           - port: 2
   19 |             untagged_network_name: vlan2
   20 |         tagged_networks:
   21 |           - port: 1
   22 |             tagged_network_ids:
   23 |               - 12767
   24 |               - 12768
   25 |           - port: 4
   26 |             tagged_network_ids:
   27 |               - 12767
   28 |               - 12768
   29 |             tagged_network_names:
   30 |               - vlan3
   31 |           - port: 2
   32 |             tagged_network_names:
   33 |               - vlan4
   34 |               - vlan1
   35 |       tags:
   36 |         - tag_untag_vlan
   37 |       delegate_to: localhost
   38 | 
   39 |     - name: Clear the tagged and untagged vLANs
   40 |       dellemc.openmanage.ome_template_network_vlan:
   41 |         hostname: "{{ hostname }}"
   42 |         username: "{{ username }}"
   43 |         password: "{{ password }}"
   44 |         ca_path: "/path/to/ca_cert.pem"
   45 |         template_id: 78
   46 |         nic_identifier: NIC Slot 4
   47 |         untagged_networks:
   48 |           # For removing the untagged vLANs for the port 1 and 2
   49 |           - port: 1
   50 |             untagged_network_id: 0
   51 |           - port: 2
   52 |             untagged_network_name: 0
   53 |         tagged_networks:
   54 |           # For removing the tagged vLANs for port 1 and 4
   55 |           - port: 1
   56 |             tagged_network_ids: []
   57 |           - port: 4
   58 |             tagged_network_ids: []
   59 |             tagged_network_names: []
   60 |           - port: 2
   61 |             tagged_network_names: []
   62 |       tags:
   63 |         - clear_tagged_untagged
   64 |       delegate_to: localhost
```

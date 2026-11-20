# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-031

- Repository: `osism/testbed`
- Commit: `ef457f4318fd7f7dce061cafe13159bcbb87f74e`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `netbox/resources/300-testbed-node-5.yml` (reported anchor line 1)
- Object: `source_location` `8e58ca75570eeb884df63e16177c61822620744513be6cc11881a80767f64c55`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–134 of 134:

```text
    1 | ---
    2 | - device_interface:
    3 |     device: testbed-node-5
    4 |     name: Loopback0
    5 |     type: virtual
    6 |     enabled: true
    7 |     tags:
    8 |       - managed-by-osism
    9 | 
   10 | - cable:
   11 |     type: mmf-om4
   12 |     termination_a_type: dcim.interface
   13 |     termination_a:
   14 |       device: testbed-switch-0
   15 |       name: Ethernet40
   16 |     termination_b_type: dcim.interface
   17 |     termination_b:
   18 |       device: testbed-node-5
   19 |       name: Ethernet3
   20 | 
   21 | - cable:
   22 |     type: mmf-om4
   23 |     termination_a_type: dcim.interface
   24 |     termination_a:
   25 |       device: testbed-switch-1
   26 |       name: Ethernet40
   27 |     termination_b_type: dcim.interface
   28 |     termination_b:
   29 |       device: testbed-node-5
   30 |       name: Ethernet4
   31 | 
   32 | - cable:
   33 |     type: cat6a
   34 |     termination_a_type: dcim.interface
   35 |     termination_a:
   36 |       device: testbed-switch-oob
   37 |       name: Ethernet15
   38 |     termination_b_type: dcim.interface
   39 |     termination_b:
   40 |       device: testbed-node-5
   41 |       name: Ethernet0
   42 | 
   43 | - ip_address:
   44 |     tenant: Testbed
   45 |     address: 172.29.0.15/24
   46 |     assigned_object:
   47 |       name: Ethernet0
   48 |       device: testbed-node-5
   49 | 
   50 | - ip_address:
   51 |     tenant: Testbed
   52 |     address: 192.168.16.15/32
   53 |     assigned_object:
   54 |       name: Loopback0
   55 |       device: testbed-node-5
   56 | 
   57 | - mac_address:
   58 |     mac_address: "18:C0:86:63:A9:D2"
   59 |     assigned_object:
   60 |       device: testbed-node-5
   61 |       name: Ethernet0
   62 | 
   63 | - mac_address:
   64 |     mac_address: "18:C0:86:B7:4F:E8"
   65 |     assigned_object:
   66 |       device: testbed-node-5
   67 |       name: Ethernet1
   68 | 
   69 | - mac_address:
   70 |     mac_address: "18:C0:86:2E:D6:54"
   71 |     assigned_object:
   72 |       device: testbed-node-5
   73 |       name: Ethernet2
   74 | 
   75 | - mac_address:
   76 |     mac_address: "18:C0:86:98:1C:7B"
   77 |     assigned_object:
   78 |       device: testbed-node-5
   79 |       name: Ethernet3
   80 | 
   81 | - mac_address:
   82 |     mac_address: "18:C0:86:F5:83:AE"
   83 |     assigned_object:
   84 |       device: testbed-node-5
   85 |       name: Ethernet4
   86 | 
   87 | - ip_address:
   88 |     tenant: Testbed
   89 |     address: "fda6:f659:8c2b::192:168:16:15/128"
   90 |     assigned_object:
   91 |       name: Loopback0
   92 |       device: testbed-node-5
   93 | 
   94 | - device:
   95 |     name: testbed-node-5
   96 |     oob_ip: 172.29.0.15/24
   97 |     primary_ip4: 192.168.16.15/32
   98 |     primary_ip6: "fda6:f659:8c2b::192:168:16:15/128"
   99 | 
  100 | - device_interface:
  101 |     device: testbed-node-5
  102 |     name: Ethernet0
  103 |     mode: access
  104 |     untagged_vlan:
  105 |       name: OOB Testbed
  106 |     tags:
  107 |       - managed-by-osism
  108 |     primary_mac_address: "18:C0:86:63:A9:D2"
  109 | 
  110 | - device_interface:
  111 |     device: testbed-node-5
  112 |     name: Ethernet1
  113 |     primary_mac_address: "18:C0:86:B7:4F:E8"
  114 | 
  115 | - device_interface:
  116 |     device: testbed-node-5
  117 |     name: Ethernet2
  118 |     primary_mac_address: "18:C0:86:2E:D6:54"
  119 | 
  120 | - device_interface:
  121 |     device: testbed-node-5
  122 |     name: Ethernet3
  123 |     primary_mac_address: "18:C0:86:98:1C:7B"
  124 |     label: leaf1
  125 |     tags:
  126 |       - managed-by-osism
  127 | 
  128 | - device_interface:
  129 |     device: testbed-node-5
  130 |     name: Ethernet4
  131 |     primary_mac_address: "18:C0:86:F5:83:AE"
  132 |     label: leaf2
  133 |     tags:
  134 |       - managed-by-osism
```

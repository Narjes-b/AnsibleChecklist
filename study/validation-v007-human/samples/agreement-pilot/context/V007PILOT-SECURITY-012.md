# Frozen source context: V007PILOT-SECURITY-012

- Repository: `dell/dellemc-openmanage-ansible-modules`
- Commit: `1f35059202d432465b8bd54e980d069a88583edc`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `playbooks/idrac/idrac_network_attributes_info.yml` (reported anchor line 73)
- Object: `task` `56e7b84f9299b40e77cdefcea72a4dd3567c20d4fd3cb0c7fc489429ba52259b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–94 of 94:

```text
    1 | ---
    2 | - name: Query Network Attribute Registry for a Specific NIC
    3 |   hosts: idrac
    4 |   gather_facts: false
    5 | 
    6 |   tasks:
    7 |     - name: Step 1 - Discover all NICs
    8 |       dellemc.openmanage.idrac_network_info:
    9 |         idrac_ip: "{{ idrac_ip }}"
   10 |         idrac_user: "{{ idrac_user }}"
   11 |         idrac_password: "{{ idrac_password }}"
   12 |         validate_certs: false
   13 |       register: nic_result
   14 |       tags:
   15 |         - two_step_workflow
   16 |       delegate_to: localhost
   17 | 
   18 |     - name: Step 2 - Query attributes for first NIC
   19 |       dellemc.openmanage.idrac_network_attributes_info:
   20 |         idrac_ip: "{{ idrac_ip }}"
   21 |         idrac_user: "{{ idrac_user }}"
   22 |         idrac_password: "{{ idrac_password }}"
   23 |         validate_certs: false
   24 |         network_device_function_id: "{{ nic_result.network_device_functions[0].id }}"
   25 |       register: attr_result
   26 |       tags:
   27 |         - two_step_workflow
   28 |       delegate_to: localhost
   29 | 
   30 |     - name: Display attribute summary
   31 |       ansible.builtin.debug:
   32 |         msg: "Found {{ attr_result.attribute_count }} attributes for {{ attr_result.network_device_function_id }}"
   33 |       tags:
   34 |         - two_step_workflow
   35 |       delegate_to: localhost
   36 | 
   37 |     - name: Query attributes for a specific NIC by ID
   38 |       dellemc.openmanage.idrac_network_attributes_info:
   39 |         idrac_ip: "{{ idrac_ip }}"
   40 |         idrac_user: "{{ idrac_user }}"
   41 |         idrac_password: "{{ idrac_password }}"
   42 |         validate_certs: false
   43 |         network_device_function_id: "{{ network_device_function_id | default('NIC.Embedded.1-1-1') }}"
   44 |       tags:
   45 |         - query_specific
   46 |       delegate_to: localhost
   47 | 
   48 |     - name: Filter attributes by glob pattern
   49 |       dellemc.openmanage.idrac_network_attributes_info:
   50 |         idrac_ip: "{{ idrac_ip }}"
   51 |         idrac_user: "{{ idrac_user }}"
   52 |         idrac_password: "{{ idrac_password }}"
   53 |         validate_certs: false
   54 |         network_device_function_id: "{{ network_device_function_id | default('NIC.Embedded.1-1-1') }}"
   55 |         attribute_name: "VLan*"
   56 |       tags:
   57 |         - filter_name
   58 |       delegate_to: localhost
   59 | 
   60 |     - name: Query OEM attributes only
   61 |       dellemc.openmanage.idrac_network_attributes_info:
   62 |         idrac_ip: "{{ idrac_ip }}"
   63 |         idrac_user: "{{ idrac_user }}"
   64 |         idrac_password: "{{ idrac_password }}"
   65 |         validate_certs: false
   66 |         network_device_function_id: "{{ network_device_function_id | default('NIC.Embedded.1-1-1') }}"
   67 |         attribute_source: "oem"
   68 |       tags:
   69 |         - filter_oem
   70 |       delegate_to: localhost
   71 | 
   72 |     - name: Query standard Redfish attributes only
   73 |       dellemc.openmanage.idrac_network_attributes_info:
   74 |         idrac_ip: "{{ idrac_ip }}"
   75 |         idrac_user: "{{ idrac_user }}"
   76 |         idrac_password: "{{ idrac_password }}"
   77 |         validate_certs: false
   78 |         network_device_function_id: "{{ network_device_function_id | default('NIC.Embedded.1-1-1') }}"
   79 |         attribute_source: "standard"
   80 |       tags:
   81 |         - filter_standard
   82 |       delegate_to: localhost
   83 | 
   84 |     - name: Force refresh attribute registry (bypass cache)
   85 |       dellemc.openmanage.idrac_network_attributes_info:
   86 |         idrac_ip: "{{ idrac_ip }}"
   87 |         idrac_user: "{{ idrac_user }}"
   88 |         idrac_password: "{{ idrac_password }}"
   89 |         validate_certs: false
   90 |         network_device_function_id: "{{ network_device_function_id | default('NIC.Embedded.1-1-1') }}"
   91 |         force_refresh: true
   92 |       tags:
   93 |         - force_refresh
   94 |       delegate_to: localhost
```

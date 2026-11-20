# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-002

- Repository: `dell/dellemc-openmanage-ansible-modules`
- Commit: `1f35059202d432465b8bd54e980d069a88583edc`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/overriding-facts`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/idrac_reset/tasks/lcstatus_check.yml` (reported anchor line 1)
- Object: `source_location` `3a2de6ef2303788a956ad81754d8008e717d6ddf324e7096bbcc6626b796e70d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–52 of 52:

```text
    1 | - name: Setting idrac_lc_status to default
    2 |   ansible.builtin.set_fact:
    3 |     idrac_lc_status:
    4 |       LCStatus: ""
    5 |     result_lc:
    6 |       LCStatus: ""
    7 | 
    8 | - name: Add a delay
    9 |   ansible.builtin.pause:
   10 |     seconds: "{{ idrac_reset_delay }}"
   11 | 
   12 | - name: Get lifecycle controller status from iDRAC
   13 |   ansible.builtin.uri:
   14 |     url: "https://{{ hostname }}:{{ https_port }}/\
   15 |       redfish/v1/Managers/iDRAC.Embedded.1/\
   16 |       Oem/Dell/DellLCService/Actions/\
   17 |       DellLCService.GetRemoteServicesAPIStatus"
   18 |     user: "{{ username | default(lookup('env', 'IDRAC_USERNAME')) }}"
   19 |     password: "{{ password |
   20 |                 default(lookup('env', 'IDRAC_PASSWORD')) }}"
   21 |     validate_certs: "{{ validate_certs }}"
   22 |     ca_path: "{{ ca_path | default(omit) }}"
   23 |     headers: "{{ idrac_reset_uri_headers }}"
   24 |     body_format: "{{ idrac_reset_uri_body_format }}"
   25 |     return_content: "{{ idrac_reset_uri_return_content }}"
   26 |     force_basic_auth: "{{ idrac_reset_force_basic_auth }}"
   27 |     timeout: "{{ https_timeout }}"
   28 |     method: "POST"
   29 |     body: "{}"
   30 |     status_code: 200
   31 |   delegate_to: "{{ idrac_reset_task_delegate }}"
   32 |   register: result_lc
   33 |   until:
   34 |     - result_lc is defined
   35 |     - result_lc.json is defined
   36 |     - result_lc.json.LCStatus is defined
   37 |     - result_lc.json.LCStatus == 'Ready'
   38 |   retries: '{{ idrac_reset_retries }}'
   39 |   delay: "{{ idrac_reset_delay }}"
   40 | 
   41 | - name: Parse lifecycle controller status response
   42 |   ansible.builtin.set_fact:
   43 |     idrac_lc_status:
   44 |       LCStatus: "{{ result_lc.json.LCStatus }}"
   45 |       RTStatus: "{{ result_lc.json.RTStatus }}"
   46 |       ServerStatus: "{{ result_lc.json.ServerStatus }}"
   47 |       Status: "{{ result_lc.json.Status }}"
   48 | 
   49 | - name: Log the LC status
   50 |   ansible.builtin.debug:
   51 |     msg: "LC Status is Ready"
   52 |   when: idrac_lc_status.LCStatus == "Ready"
```

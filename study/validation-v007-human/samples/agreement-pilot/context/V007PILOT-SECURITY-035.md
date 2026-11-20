# Frozen source context: V007PILOT-SECURITY-035

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/vendors/kvm/tasks/disk.yml` (reported anchor line 39)
- Object: `task` `99fa3459ad5bc7b8b475c9146523a261e7ecfbe482cfc9549b591a8e9425c0b6`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–73 of 73:

```text
    1 | ---
    2 | #
    3 | # Virtual Redfish BMC
    4 | # https://docs.openstack.org/sushy-tools/latest/user/dynamic-emulator.html#uefi-boot
    5 | #
    6 | # Mount Live ISO, Boot into Live ISO (KVM only)
    7 | - name: Identify System Manager
    8 |   ansible.builtin.include_tasks: get-sm.yml
    9 | 
   10 | - name: KVM Force Power Off System {{ target_host }}
   11 |   ansible.builtin.uri:
   12 |     url: "{{ system_uuid_url }}/Actions/ComputerSystem.Reset"
   13 |     user: "{{ bmc_user }}"
   14 |     password: "{{ bmc_password }}"
   15 |     method: POST
   16 |     body_format: json
   17 |     body: { "ResetType": "ForceOff" }
   18 |     status_code: [200, 204]
   19 |     force_basic_auth: false
   20 |     validate_certs: "{{ bmc_validate_certs }}"
   21 |     return_content: true
   22 |   register: redfish_poweroff
   23 |   failed_when: false
   24 | 
   25 | - name: KVM Eject Virtual Media (if any) {{ target_host }}
   26 |   ansible.builtin.uri:
   27 |     url: "{{ system_manager_url }}/VirtualMedia/Cd/Actions/VirtualMedia.EjectMedia"
   28 |     user: "{{ bmc_user }}"
   29 |     password: "{{ bmc_password }}"
   30 |     method: POST
   31 |     body_format: json
   32 |     body: {}
   33 |     status_code: [200, 204]
   34 |     validate_certs: "{{ bmc_validate_certs }}"
   35 |     return_content: true
   36 |   register: redfish_reply
   37 |   failed_when: false
   38 | 
   39 | - name: KVM Set Next Boot from HDD {{ target_host }}
   40 |   ansible.builtin.uri:
   41 |     url: "{{ system_uuid_url }}"
   42 |     user: "{{ bmc_user }}"
   43 |     password: "{{ bmc_password }}"
   44 |     method: PATCH
   45 |     body_format: json
   46 |     body:
   47 |       {
   48 |         "Boot":
   49 |           {
   50 |             "BootSourceOverrideTarget": "Hdd",
   51 |             "BootSourceOverrideMode": "UEFI",
   52 |             "BootSourceOverrideEnabled": "Continuous",
   53 |           },
   54 |       }
   55 |     status_code: [200, 204]
   56 |     force_basic_auth: false
   57 |     validate_certs: "{{ bmc_validate_certs }}"
   58 |     return_content: true
   59 |   register: redfish_reply
   60 | 
   61 | - name: KVM Force Power On System {{ target_host }}
   62 |   ansible.builtin.uri:
   63 |     url: "{{ system_uuid_url }}/Actions/ComputerSystem.Reset"
   64 |     user: "{{ bmc_user }}"
   65 |     password: "{{ bmc_password }}"
   66 |     method: POST
   67 |     body_format: json
   68 |     body: { "ResetType": "ForceOn" }
   69 |     status_code: [200, 204]
   70 |     force_basic_auth: false
   71 |     validate_certs: "{{ bmc_validate_certs }}"
   72 |     return_content: true
   73 |   register: redfish_poweron
```

# Frozen source context: V007PILOT-STRUCTURE_REUSE-006

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: Structure/reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/vendors/pxe/defaults/main.yml` (reported anchor line 1)
- Object: `source_location` `896bb71411ad86fd9a3b7d8a199843106b28e2ef9ab59ad0e7fb241b58824ca4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–6 of 6:

```text
    1 | ---
    2 | boot_iso_url: "{{ discovery_iso_server }}/{{ discovery_iso_name }}"
    3 | bmc_address: "{{ hostvars[target_host]['bmc_address'] }}"
    4 | bmc_user: "{{ hostvars[target_host]['bmc_user'] }}"
    5 | bmc_password: "{{ hostvars[target_host]['bmc_password'] }}"
    6 | bmc_port: "{{ hostvars[target_host]['bmc_port'] | default(623) }}"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/vendors/dell/README.md
roles/vendors/dell/defaults/main.yml
roles/vendors/dell/tasks/disk.yml
roles/vendors/dell/tasks/disk_redfish.yml
roles/vendors/dell/tasks/eject.yml
roles/vendors/dell/tasks/exists.yml
roles/vendors/dell/tasks/iso.yml
roles/vendors/dell/tasks/iso_idrac.yml
roles/vendors/dell/tasks/iso_redfish.yml
roles/vendors/hpe/README.md
roles/vendors/hpe/defaults/main.yml
roles/vendors/hpe/tasks/disk.yml
roles/vendors/hpe/tasks/eject.yml
roles/vendors/hpe/tasks/exists.yml
roles/vendors/hpe/tasks/iso.yml
roles/vendors/kvm/README.md
roles/vendors/kvm/defaults/main.yml
roles/vendors/kvm/tasks/disk.yml
roles/vendors/kvm/tasks/eject.yml
roles/vendors/kvm/tasks/exists.yml
roles/vendors/kvm/tasks/get-sm.yml
roles/vendors/kvm/tasks/iso.yml
roles/vendors/lenovo/README.md
roles/vendors/lenovo/defaults/main.yml
roles/vendors/lenovo/tasks/disk.yml
roles/vendors/lenovo/tasks/eject.yml
roles/vendors/lenovo/tasks/exists.yml
roles/vendors/lenovo/tasks/iso.yml
roles/vendors/pxe/README.md
roles/vendors/pxe/defaults/main.yml
roles/vendors/pxe/tasks/disk.yml
roles/vendors/pxe/tasks/exists.yml
roles/vendors/pxe/tasks/iso.yml
roles/vendors/supermicro/README.md
roles/vendors/supermicro/defaults/main.yml
roles/vendors/supermicro/tasks/disk.yml
roles/vendors/supermicro/tasks/eject.yml
roles/vendors/supermicro/tasks/exists.yml
roles/vendors/supermicro/tasks/iso.yml
roles/vendors/supermicro/tasks/mount.yml
roles/vendors/zt/README.md
roles/vendors/zt/defaults/main.yml
roles/vendors/zt/tasks/disk.yml
roles/vendors/zt/tasks/eject.yml
roles/vendors/zt/tasks/exists.yml
roles/vendors/zt/tasks/get_resource_id.yml
roles/vendors/zt/tasks/iso.yml
roles/vendors/zt/tasks/power_off.yml
roles/vendors/zt/tasks/set_resource_id.yml
```

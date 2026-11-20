# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-042

- Repository: `CentOS-PaaS-SIG/linchpin`
- Commit: `0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unused-registered-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `linchpin/provision/roles/libvirt/tasks/main.yml` (reported anchor line 11)
- Object: `variable` `2d24e7ad2503e38a33c45f4c05a3c827e0e1bf394b6f03a24af0e9ca79a280e7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–15 of 15:

```text
    1 | ---
    2 | - name: "Gather facts"
    3 |   setup:
    4 |     filter: ansible_*
    5 | 
    6 | - name: "declaring output vars"
    7 |   set_fact:
    8 |     topology_outputs_libvirt_nodes: []
    9 |     current_provider: "libvirt"
   10 | 
   11 | - name: "Initiating libvirt resource group"
   12 |   include: provision_resource_group.yml res_grp={{ item }}
   13 |   with_items:
   14 |     - "{{ resources }}"
   15 |   register: resource_grps_output
```

## Visible variable references

```text
0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f:linchpin/provision/roles/libvirt/tasks/main.yml:15:  register: resource_grps_output
0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f:linchpin/provision/roles/openstack/tasks/main.yml:19:  register: resource_grps_output
0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f:linchpin/provision/roles/ovirt/tasks/main.yml:13:  register: resource_grps_output
0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f:linchpin/provision/roles/rackspace/tasks/main.yml:16:  register: resource_grps_output
0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f:linchpin/provision/roles/vmware/tasks/main.yml:11:  register: resource_grps_output
```

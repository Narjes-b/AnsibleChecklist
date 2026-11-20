# Frozen source context: V007PILOT-STRUCTURE_REUSE-047

- Repository: `JenswBE/setup`
- Commit: `18c39275cc08ae3f7bea8b7ee0624876b8fa72fe`
- Family: Structure/reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `server/roles/jenswbe.vm_host/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `82012ebe693794a6943051cc7b85290e702224c032d65f2c4a241c3d2fb9ae99`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–16 of 16:

```text
    1 | - name: Assert distribution is supported
    2 |   ansible.builtin.assert:
    3 |     that: ansible_facts['distribution'] in ['Debian']
    4 |     fail_msg: "{{ ansible_facts['distribution'] }} is not a supported distro for this role. Supported distros: Debian"
    5 | 
    6 | - name: VM host
    7 |   become: true
    8 |   block:
    9 |     - name: "Include tasks for {{ subtask }}"
   10 |       ansible.builtin.include_tasks: "{{ subtask | lower }}.yml"
   11 |       loop_control:
   12 |         loop_var: subtask
   13 |       loop:
   14 |         - Libvirt
   15 |         - Cockpit
   16 |         - Caddy
```

## Frozen tracked paths in the relevant role/scope

```text
server/roles/jenswbe.vm_host/defaults/main.yml
server/roles/jenswbe.vm_host/files/clone-vm.sh
server/roles/jenswbe.vm_host/files/start-vm-after-nfs.sh
server/roles/jenswbe.vm_host/handlers/main.yml
server/roles/jenswbe.vm_host/meta/argument_specs.yml
server/roles/jenswbe.vm_host/tasks/caddy.yml
server/roles/jenswbe.vm_host/tasks/cockpit.yml
server/roles/jenswbe.vm_host/tasks/libvirt.yml
server/roles/jenswbe.vm_host/tasks/libvirt_setup_network.yml
server/roles/jenswbe.vm_host/tasks/libvirt_setup_storage_pool.yml
server/roles/jenswbe.vm_host/tasks/main.yml
server/roles/jenswbe.vm_host/templates/caddy/Caddyfile
server/roles/jenswbe.vm_host/templates/caddy/caddy-config.volume
server/roles/jenswbe.vm_host/templates/caddy/caddy-data.volume
server/roles/jenswbe.vm_host/templates/caddy/caddy.Containerfile
server/roles/jenswbe.vm_host/templates/caddy/caddy.build
server/roles/jenswbe.vm_host/templates/caddy/caddy.container
server/roles/jenswbe.vm_host/templates/networks/100_nointernet.xml
server/roles/jenswbe.vm_host/templates/networks/200_nat.xml
server/roles/jenswbe.vm_host/templates/start-vm-after-nfs@.service
```

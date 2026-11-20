# Frozen source context: V007PILOT2-SECURITY-021

- Repository: `dell/dellemc-openmanage-ansible-modules`
- Commit: `1f35059202d432465b8bd54e980d069a88583edc`
- Family: security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `roles/idrac_os_deployment/tasks/idrac/attach_iso_to_virtual_media.yml` (reported anchor line 25)
- Flagged construct: task `attach the iso to virtual media slot 1`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–45 of 45:

```text
    1 | ---
    2 | - name: Attach the iso image to idrac virtual media
    3 |   delegate_to: "{{ idrac_os_deployment_delegate }}"
    4 |   block:
    5 |     - name: Create virtual media mount facts
    6 |       when: source.is_custom_iso is undefined or source.is_custom_iso is false
    7 |       ansible.builtin.set_fact:
    8 |         idrac_os_deployment_vm_protocol: "{{ destination.protocol }}"
    9 |         idrac_os_deployment_vm_hostname: "{{ destination.hostname }}"
   10 |         idrac_os_deployment_vm_iso_path: "{{ destination.iso_path }}"
   11 |         idrac_os_deployment_vm_iso_name: "{{ idrac_os_deployment_custom_iso_filename }}"
   12 |         idrac_os_deployment_vm_username: "{{ destination.username | default(omit) }}"
   13 |         idrac_os_deployment_vm_password: "{{ destination.password | default(omit) }}"
   14 |       no_log: "{{ set_no_log }}"
   15 | 
   16 |     - name: Create virtual media mount url
   17 |       when: >
   18 |         idrac_os_deployment_vm_protocol is defined and
   19 |         idrac_os_deployment_vm_protocol | length > 0
   20 |       ansible.builtin.set_fact:
   21 |         idrac_os_deployment_vm_url:
   22 |           "{{ idrac_os_deployment_vm_proto_map[idrac_os_deployment_vm_protocol]
   23 |           | format(idrac_os_deployment_vm_hostname, idrac_os_deployment_vm_iso_path, idrac_os_deployment_vm_iso_name) }}"
   24 | 
   25 |     - name: Attach the iso to Virtual Media slot 1
   26 |       register: idrac_os_deployment_vm_insert
   27 |       dellemc.openmanage.idrac_virtual_media:
   28 |         idrac_ip: "{{ hostname }}"
   29 |         idrac_user: "{{ username }}"
   30 |         idrac_password: "{{ password }}"
   31 |         idrac_port: "{{ https_port }}"
   32 |         validate_certs: "{{ validate_certs }}"
   33 |         ca_path: "{{ ca_path | default(omit) }}"
   34 |         timeout: "{{ https_timeout }}"
   35 |         force: true
   36 |         virtual_media:
   37 |           - insert: true
   38 |             image: "{{ idrac_os_deployment_vm_url }}"
   39 |             username: "{{ idrac_os_deployment_vm_username | default(omit) }}"
   40 |             password: "{{ idrac_os_deployment_vm_password | default(omit) }}"
   41 | 
   42 |     - name: Set virtual media attached to success
   43 |       when: idrac_os_deployment_vm_insert is succeeded
   44 |       ansible.builtin.set_fact:
   45 |         idrac_os_deployment_virtual_media_attached: true
```

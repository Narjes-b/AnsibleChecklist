# Frozen source context: V007PILOT-SECURITY-010

- Repository: `Checkmk/ansible-collection-checkmk.general`
- Commit: `50be8bde935f94e4702f40c9a549f86ffe773db1`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `playbooks/usecases/remote-registration.yml` (reported anchor line 15)
- Object: `source_location` `e59607d99c306cff849bc81fdd1c981a4590242449c213d1287d1ab430ed8be1`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–49 of 49:

```text
    1 | ---
    2 | # This playbook uses the inventory from the 'playbooks/hosts' file and expects
    3 | # an existing site with the below configuration and hosts of the group
    4 | # 'linux'.
    5 | 
    6 | - name: "Register hosts against a remote site. Both for updates and TLS."
    7 |   hosts: linux
    8 |   strategy: linear
    9 |   vars:
   10 |     # Basic server and authentication information.
   11 |     # You have to provide the distributed setup yourself.
   12 |     checkmk_agent_version: "2.3.0p14"
   13 |     checkmk_agent_edition: "cre"
   14 |     checkmk_agent_user: "cmkadmin"
   15 |     checkmk_agent_pass: "password"
   16 |     # Here comes the part, where we get into remote registration
   17 |     checkmk_agent_server_protocol: http
   18 |     # The following should be set to the central site.
   19 |     # This where you configure the host objects.
   20 |     # Currently the agent package is also pulled from here.
   21 |     checkmk_agent_server: 192.168.56.1
   22 |     checkmk_agent_site: "ansible"
   23 |     # The following should be pointed to the respective remote site.
   24 |     # This is where the registration will happen.
   25 |     checkmk_agent_registration_server: "{{ checkmk_agent_server }}"
   26 |     checkmk_agent_registration_site: ansible_remote_1
   27 |     # The folder might differ from your remote site name,
   28 |     # as it is the technical path. Check your configuration for this information.
   29 |     checkmk_agent_folder: "/remote_1"
   30 |     # These options need to be enabled for all registrations to work.
   31 |     # You can however disable the one you do not want to perform.
   32 |     # But the host needs to be added and changes activated in any case.
   33 |     checkmk_agent_auto_activate: true
   34 |     checkmk_agent_update: true
   35 |     checkmk_agent_tls: true
   36 |     checkmk_agent_add_host: true
   37 |     # These are some generic agent options you might want to configure.
   38 |     checkmk_agent_discover: true
   39 |     checkmk_agent_discover_max_parallel_tasks: 0
   40 |     checkmk_agent_force_install: true
   41 |     checkmk_agent_delegate_api_calls: localhost
   42 |     checkmk_agent_delegate_download: "{{ inventory_hostname }}"
   43 |     checkmk_agent_host_name: "{{ inventory_hostname }}"
   44 |     checkmk_agent_host_folder: "{{ checkmk_var_site }}"
   45 |     checkmk_agent_host_ip: "{{ ansible_host }}"
   46 |     checkmk_agent_host_attributes:
   47 |       ipaddress: "{{ checkmk_agent_host_ip | default(omit) }}"
   48 |   roles:
   49 |     - agent
```

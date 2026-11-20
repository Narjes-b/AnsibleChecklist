# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-020

- Repository: `dell/dellemc-openmanage-ansible-modules`
- Commit: `1f35059202d432465b8bd54e980d069a88583edc`
- Family: maintainability_complexity
- Rule: `ansibleguard/large-playbook`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `playbooks/ome/ome_active_directory.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`playbooks/ome/ome_active_directory.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–75 of 75:

```text
    1 | ---
    2 | - name: Dell OpenManage Ansible Active Directory service configuration.
    3 |   hosts: ome
    4 |   gather_facts: false
    5 | 
    6 |   tasks:
    7 |     - name: Add AD service using DNS lookup along with the test connection
    8 |       dellemc.openmanage.ome_active_directory:
    9 |         hostname: "{{ hostname }}"
   10 |         username: "{{ username }}"
   11 |         password: "{{ password }}"
   12 |         ca_path: "/path/to/ca_cert.pem"
   13 |         name: my_ad1
   14 |         domain_server:
   15 |           - domainname.com
   16 |         group_domain: domainname.com
   17 |         test_connection: true
   18 |         domain_username: user@domainname
   19 |         domain_password: [REDACTED_LITERAL]
   20 |       delegate_to: localhost
   21 | 
   22 |     - name: Add AD service using IP address of the domain controller with
   23 |             certificate validation
   24 |       dellemc.openmanage.ome_active_directory:
   25 |         hostname: "{{ hostname }}"
   26 |         username: "{{ username }}"
   27 |         password: "{{ password }}"
   28 |         ca_path: "/path/to/ca_cert.pem"
   29 |         name: my_ad2
   30 |         domain_controller_lookup: MANUAL
   31 |         domain_server:
   32 |           - 192.68.20.181
   33 |         group_domain: domainname.com
   34 |         validate_certificate: true
   35 |         certificate_file: "/path/to/certificate/file.cer"
   36 |       delegate_to: localhost
   37 | 
   38 |     - name: Modify domain controller IP address, network_timeout and
   39 |             group_domain
   40 |       dellemc.openmanage.ome_active_directory:
   41 |         hostname: "{{ hostname }}"
   42 |         username: "{{ username }}"
   43 |         password: "{{ password }}"
   44 |         ca_path: "/path/to/ca_cert.pem"
   45 |         name: my_ad2
   46 |         domain_controller_lookup: MANUAL
   47 |         domain_server:
   48 |           - 192.68.20.189
   49 |         group_domain: newdomain.in
   50 |         network_timeout: 150
   51 |       delegate_to: localhost
   52 | 
   53 |     - name: Delete Active Directory service
   54 |       dellemc.openmanage.ome_active_directory:
   55 |         hostname: "{{ hostname }}"
   56 |         username: "{{ username }}"
   57 |         password: "{{ password }}"
   58 |         ca_path: "/path/to/ca_cert.pem"
   59 |         name: my_ad2
   60 |         state: absent
   61 |       delegate_to: localhost
   62 | 
   63 |     - name: Test connection to existing AD service with certificate validation
   64 |       dellemc.openmanage.ome_active_directory:
   65 |         hostname: "{{ hostname }}"
   66 |         username: "{{ username }}"
   67 |         password: "{{ password }}"
   68 |         ca_path: "/path/to/ca_cert.pem"
   69 |         name: my_ad2
   70 |         test_connection: true
   71 |         domain_username: user@domainname
   72 |         domain_password: [REDACTED_LITERAL]
   73 |         validate_certificate: true
   74 |         certificate_file: "/path/to/certificate/file.cer"
   75 |       delegate_to: localhost
```

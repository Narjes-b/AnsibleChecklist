# Frozen source context: V007PILOT-SECURITY-038

- Repository: `osism/ansible-collection-services`
- Commit: `131734f2c007d0009a7fc218849f4ede66c7c899`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/nexus/tasks/declare-script.yml` (reported anchor line 22)
- Object: `task` `d5f93cc0ed47c2d3912e907fc382f666c9802911dcb13453af91307a27b6c871`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–44 of 44:

```text
    1 | ---
    2 | - name: Set nexus url
    3 |   ansible.builtin.set_fact:
    4 |     declare_script_nexus_url: "https://{{ nexus_host }}/service/rest/v1"
    5 |   when: nexus_traefik|bool
    6 | 
    7 | - name: Set nexus url
    8 |   ansible.builtin.set_fact:
    9 |     declare_script_nexus_url: "http://{{ nexus_host }}:{{ nexus_port }}/service/rest/v1"
   10 |   when: not nexus_traefik|bool
   11 | 
   12 | - name: Wait for nexus
   13 |   ansible.builtin.uri:
   14 |     url: "{{ declare_script_nexus_url }}/status"
   15 |     validate_certs: false
   16 |   register: result
   17 |   until: result.status == 200
   18 |   retries: 60
   19 |   delay: 5
   20 | 
   21 | - name: Deleting script {{ item }}
   22 |   ansible.builtin.uri:
   23 |     url: "{{ declare_script_nexus_url }}/script/{{ item }}"
   24 |     user: "{{ nexus_admin_username }}"
   25 |     password: "{{ current_nexus_admin_password }}"
   26 |     method: DELETE
   27 |     status_code: 204,404
   28 |     force_basic_auth: true
   29 |     validate_certs: false
   30 | 
   31 | - name: Declaring script {{ item }}
   32 |   ansible.builtin.uri:
   33 |     url: "{{ declare_script_nexus_url }}/script"
   34 |     user: "{{ nexus_admin_username }}"
   35 |     password: "{{ current_nexus_admin_password }}"
   36 |     method: POST
   37 |     status_code: 204
   38 |     force_basic_auth: true
   39 |     validate_certs: false
   40 |     body_format: json
   41 |     body:
   42 |       name: "{{ item }}"
   43 |       type: 'groovy'
   44 |       content: "{{ lookup('file', item + '.groovy') }}"
```

# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-002

- Repository: `redhat-cop/aap_configuration_extended`
- Commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/overriding-facts`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `roles/filetree_create/tasks/gateway_settings.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/filetree_create/tasks/gateway_settings.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–31 of 31:

```text
    1 | ---
    2 | - name: "Get changed Gateway Settings from the API"
    3 |   block:
    4 |     - name: "Query gateway settings/changed"
    5 |       ansible.builtin.set_fact:
    6 |         all_settings: "{{ query('ansible.platform.gateway_api', 'api/gateway/v1/settings/changed/',
    7 |                                 host=aap_hostname, oauth_token=[REDACTED_LITERAL]
    8 |                                 return_all=true, max_objects=query_gateway_api_max_objects)
    9 |                            }}"
   10 |         settings_export_from_changed: true
   11 |   rescue:
   12 |     - name: "Fallback to gateway settings/all when changed endpoint is unavailable"
   13 |       ansible.builtin.set_fact:
   14 |         all_settings: "{{ query('ansible.platform.gateway_api', 'api/gateway/v1/settings/all/',
   15 |                                 host=aap_hostname, oauth_token=[REDACTED_LITERAL]
   16 |                                 return_all=true, max_objects=query_gateway_api_max_objects)
   17 |                            }}"
   18 |         settings_export_from_changed: false
   19 | 
   20 | - name: "Create the output directory for gateway_settings in {{ output_path }}"
   21 |   ansible.builtin.file:
   22 |     path: "{{ output_path }}"
   23 |     state: directory
   24 |     mode: '0755'
   25 | 
   26 | - name: "Add current settings to the gateway_settings.yaml output file in {{ output_path }}"
   27 |   ansible.builtin.template:
   28 |     src: "templates/gateway_settings.j2"
   29 |     dest: "{{ output_path }}/gateway_settings.yaml"
   30 |     mode: '0644'
   31 | ...
```

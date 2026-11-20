# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-030

- Repository: `cisco-en-programmability/dnacenter-ansible`
- Commit: `33276c6275a666371b085bea241441cf4f6a29d2`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-play`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/swim_import_local.yml` (reported anchor line 2)
- Object: `source_location` `faba8faadfe8b9b4b763f6289b23c8e48f6c56bf1fe6e1b62c53592305fceb82`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–24 of 24:

```text
    1 | ---
    2 | - name: Swim import local
    3 |   hosts: dnac_servers
    4 |   vars_files:
    5 |     - vars/credentials.yml
    6 |   gather_facts: false
    7 |   connection: local
    8 |   tasks:
    9 |     - name: Import Local
   10 |       cisco.dnac.swim_import_local:
   11 |         dnac_host: "{{ dnac_host }}"
   12 |         dnac_username: "{{ dnac_username }}"
   13 |         dnac_password: "{{ dnac_password }}"
   14 |         dnac_verify: "{{ dnac_verify }}"
   15 |         dnac_port: "{{ dnac_port }}"
   16 |         dnac_version: "{{ dnac_version }}"
   17 |         dnac_debug: "{{ dnac_debug }}"
   18 |         # headers: "{{my_headers | from_json}}"
   19 |         isThirdParty: false
   20 |         thirdPartyVendor: "string"
   21 |         thirdPartyImageFamily: "string"
   22 |         thirdPartyApplicationType: "string"
   23 |         filePath: "./tests/test-1592357065255.csv"
   24 |       register: result
```

# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-001

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: maintainability_complexity
- Rule: `ansibleguard/complex-expression`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `ansible/ansible_collections/snowdrop/godaddy/roles/domain/tasks/create.yml` (reported anchor line 13)
- Flagged construct: not named by the finding; the anchor line 13 lies in the task at line 13, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–117 of 117:

```text
    1 | ---
    2 | # Requires:
    3 | #  . api_key: [REDACTED_LITERAL]
    4 | #  . api_secret: [REDACTED_LITERAL]
    5 | #  . domain_name: Domain to be purchased
    6 | - name: Print TLD
    7 |   ansible.builtin.debug:
    8 |     msg: 
    9 |       - "{{ domain_name | replace(\"snowdropansibletest.\",'') }}"
   10 |       - "{{ domain_name | replace('snowdropansibletest.','') }}"
   11 |       - "{{ (domain_name | split('.') )[0] }}"
   12 |       - "{{ (domain_name | split('.') )[0] ~ '.' }}"
   13 |       - "{{ domain_name | replace((domain_name | split('.') )[0] ~ '.','') }}"
   14 |       - "{{ domain_name | replace(\"{{ (domain_name | split('.') )[0] }}\",'') }}"
   15 | 
   16 | - name: Set default facts
   17 |   ansible.builtin.set_fact:
   18 |     api_url: "{{ ote_api_url }}/{{ domains_folder }}"
   19 |     authorization: [REDACTED_LITERAL]
   20 |     tld: "{{ domain_name | replace((domain_name | split('.') )[0] ~ '.','') }}"
   21 | 
   22 | - name: Print TLD
   23 |   ansible.builtin.debug:
   24 |     var: tld
   25 | 
   26 | - name: Set URL
   27 |   ansible.builtin.set_fact:
   28 |     api_url: "{{ pro_api_url }}/{{ domains_folder }}"
   29 |   when: environment is defined and environment == 'production'
   30 | 
   31 | # - name: Get TLDs
   32 | #   ansible.builtin.uri:
   33 | #     headers:
   34 | #       accept: application/json
   35 | #       authorization: "{{ authorization }}"
   36 | #     method: GET
   37 | #     return_content: true
   38 | #     url: "{{ api_url }}/tlds"
   39 | #   register: godaddy_tlds
   40 | 
   41 | # - name: Print TLDs
   42 | #   ansible.builtin.debug:
   43 | #     var: godaddy_tlds
   44 | 
   45 | - name: Set URL
   46 |   ansible.builtin.set_fact:
   47 |     agreements_url: "{{ api_url }}/{{ agreements_folder }}?tlds={{ tld }}&privacy=false&forTransfer=false"
   48 | 
   49 | - name: Print Agreements URL
   50 |   ansible.builtin.debug:
   51 |     var: agreements_url
   52 |     verbosity: 2
   53 | 
   54 | - name: Get agreements
   55 |   ansible.builtin.uri:
   56 |     headers:
   57 |       accept: application/json
   58 |       authorization: "{{ authorization }}"
   59 |     method: GET
   60 |     return_content: true
   61 |     url: "{{ agreements_url }}"
   62 |   register: godaddy_agreements
   63 | 
   64 | - name: Print Agreements INFO
   65 |   ansible.builtin.debug:
   66 |     var: godaddy_agreements
   67 |     verbosity: 2
   68 | 
   69 | # - name: Print Agreement Keys
   70 | #   ansible.builtin.debug:
   71 | #     msg: "agreement: {{ agreement.agreementKey }}"
   72 | #     verbosity: 2
   73 | #   loop: "{{ godaddy_agreements.json }}"
   74 | #   loop_control: 
   75 | #     loop_var: agreement
   76 | 
   77 | - name: "Template purchase body"
   78 |   ansible.builtin.set_fact:
   79 |     purchase_body: "{{ lookup('template', './purchase_body.json.j2') }}"
   80 |   when: override_purchase_body is undefined or override_purchase_body | length == 0
   81 | 
   82 | - name: "Apply override purchase body"
   83 |   ansible.builtin.set_fact:
   84 |     purchase_body: "{{ override_purchase_body }}"
   85 |   when: override_purchase_body is defined and override_purchase_body | length > 0
   86 | 
   87 | - name: Print Purchase body
   88 |   ansible.builtin.debug:
   89 |     var: purchase_body
   90 |     # verbosity: 2
   91 | 
   92 | - name: Print Purchase body
   93 |   ansible.builtin.debug:
   94 |     msg: 
   95 |       # - "{{ purchase_body }}"
   96 |       - "{{ purchase_body | string }}"
   97 |       # - "{{ purchase_body | to_json | tojson }}"
   98 |     # verbosity: 2
   99 | 
  100 | - name: Call Purchase and register domain API
  101 |   ansible.builtin.uri:
  102 |     body: "{{ purchase_body | to_json }}"
  103 |     headers:
  104 |       accept: application/json
  105 |       authorization: "{{ authorization }}"
  106 |       Content-Type: application/json
  107 |     method: POST
  108 |     return_content: true
  109 |     url: "{{ api_url }}/{{ purchase_folder }}"
  110 |   register: godaddy_domain_info
  111 | 
  112 | - name: Print result
  113 |   ansible.builtin.debug:
  114 |     var: godaddy_domain_info
  115 |     verbosity: 2
  116 | 
  117 | ...
```

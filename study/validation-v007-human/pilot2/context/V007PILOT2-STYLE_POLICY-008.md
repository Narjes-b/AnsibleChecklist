# Frozen source context: V007PILOT2-STYLE_POLICY-008

- Repository: `bluebanquise/bluebanquise`
- Commit: `fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0`
- Family: style_policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `collections/infrastructure/roles/pxe_stack/tasks/diskful/RHCOS.yml` (reported anchor line 13)
- Flagged construct: task `template <|> generate equipment_profiles {{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{item}.ipxe`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–102 of 102:

```text
    1 | ---
    2 | ##### RHCOS os familly
    3 | 
    4 | - name: "copy <|> Copy osdeploy files {{ pxe_stack_htdocs_path }}/pxe/osdeploy/"
    5 |   ansible.builtin.copy:
    6 |     src: osdeploy/rhcos_{{ item.major }}.ipxe
    7 |     dest: "{{ pxe_stack_htdocs_path }}/pxe/osdeploy/rhcos_{{ item.major }}.ipxe"
    8 |     mode: 0644
    9 |     owner: "{{ pxe_stack_apache_user }}"
   10 |     group: "{{ pxe_stack_apache_group }}"
   11 |   loop: "{{ pxe_stack_supported_os.rhcos }}"
   12 | 
   13 | - name: "template <|> Generate equipment_profiles {{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{item}.ipxe"
   14 |   ansible.builtin.template:
   15 |     src: "RHCOS/equipment_profile_rhcos.ipxe.j2"
   16 |     dest: "{{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{{ item | trim }}.ipxe"
   17 |     mode: 0644
   18 |     owner: "{{ pxe_stack_apache_user }}"
   19 |     group: "{{ pxe_stack_apache_group }}"
   20 |   vars:
   21 |     equipment: "{{ pxe_stack_equipment_profiles[item] | default({}, true) }}"
   22 |   loop: "{{ pxe_stack_equipment_profiles | default({}, true) | flatten(levels=1) }}"
   23 |   when:
   24 |     - (pxe_stack_equipment_profiles[item]['hw']['hw_equipment_type'] | default(pxe_stack_hw_equipment_type, true)) == "server"
   25 |     - (pxe_stack_equipment_profiles[item]['os']['os_operating_system']['distribution'] | default(pxe_stack_os_operating_system.distribution, true) | lower) in ['rhcos']
   26 |   tags:
   27 |     - template
   28 | 
   29 | # Generate empty ignition files, for tenants
   30 | 
   31 | # - name: file <|> Create rhcos_tenants directory
   32 | #   ansible.builtin.file:
   33 | #     path: "{{ item }}"
   34 | #     state: directory
   35 | #     mode: 0755
   36 | #     owner: "{{ pxe_stack_apache_user }}"
   37 | #     group: "{{ pxe_stack_apache_group }}"
   38 | #   loop:
   39 | #     - "{{ pxe_stack_htdocs_path }}/pxe/rhcos_tenants"
   40 | 
   41 | # - name: "template <|> Generate tenants ipxe files"
   42 | #   ansible.builtin.template:
   43 | #     src: "RHCOS/tenant.ipxe.j2"
   44 | #     dest: "{{ pxe_stack_htdocs_path }}/pxe/rhcos_tenants/{{ item | trim }}.ipxe"
   45 | #     mode: 0644
   46 | #     owner: "{{ pxe_stack_apache_user }}"
   47 | #     group: "{{ pxe_stack_apache_group }}"
   48 | #   vars:
   49 | #     tenant: "{{ item }}"
   50 | #   loop: "{{ groups | select('match','^rhcos_tenant_'+'[a-zA-Z0-9]+') | list }}"
   51 | #   tags:
   52 | #     - template
   53 | 
   54 | - name: stat <|> Check for ignition file
   55 |   ansible.builtin.stat:
   56 |     path: "{{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{{ item | trim }}.ign"
   57 |   register: pxe_stack_file_checks
   58 |   loop: "{{ groups | select('match','^tenant_'+'[a-zA-Z0-9]+') | list }}"
   59 |   # when:
   60 |   #   - pxe_stack_rhcos_enable_tenants
   61 |   tags:
   62 |     - file
   63 | 
   64 | - name: file <|> Create missing ignition files
   65 |   ansible.builtin.file:
   66 |     path: "{{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{{ item.item | trim }}.ign"
   67 |     state: touch
   68 |     mode: 0644
   69 |   loop: "{{ pxe_stack_file_checks.results }}"
   70 |   when: not item.stat.exists
   71 |   tags:
   72 |     - file
   73 | 
   74 | - name: template <|> Generate /etc/bluebanquise/bootset/tenants.yml
   75 |   ansible.builtin.template:
   76 |     src: "tenants.yml.j2"
   77 |     dest: /etc/bluebanquise/bootset/tenants.yml
   78 |     mode: 0644
   79 |   tags:
   80 |     - template
   81 | 
   82 | # - name: stat <|> Check for ignition file
   83 | #   ansible.builtin.stat:
   84 | #     path: "{{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{{ item | trim }}.ign"
   85 | #   register: file_checks
   86 | #   loop: "{{ pxe_stack_equipment_profiles | default({}, true) | flatten(levels=1) }}"
   87 | #   when:
   88 | #     - pxe_stack_equipment_profiles
   89 | #     - (pxe_stack_equipment_profiles[item]['hw']['hw_equipment_type'] | default(pxe_stack_hw_equipment_type)) == "server"
   90 | #     - (pxe_stack_equipment_profiles[item]['os']['os_operating_system']['distribution'] | default(pxe_stack_os_operating_system.distribution) | lower) in ['rhcos']
   91 | #     - (pxe_stack_equipment_profiles[item]['os']['os_operating_system']['distribution_major_version'] | default(pxe_stack_os_operating_system.distribution_major_version) | int) in [4]
   92 | #   tags:
   93 | #     - file
   94 | 
   95 | # - name: file <|> Create missing ignition files
   96 | #   ansible.builtin.file:
   97 | #     path: "{{ item.item }}"
   98 | #   state: touch
   99 | #   loop: "{{ file_checks.results }}"
  100 | #   when: not item.stat.exists
  101 | #   tags:
  102 | #     - file
```

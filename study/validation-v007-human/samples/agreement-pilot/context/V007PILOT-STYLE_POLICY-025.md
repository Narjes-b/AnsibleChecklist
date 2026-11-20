# Frozen source context: V007PILOT-STYLE_POLICY-025

- Repository: `bluebanquise/bluebanquise`
- Commit: `fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0`
- Family: Style/policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `collections/infrastructure/roles/pxe_stack/tasks/diskful/RedHat.yml` (reported anchor line 25)
- Object: `task` `56d2d5e35a465fe88b8b6707bc56c0cf6062f3c36d03d20ffd0f3924daee0c61`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–55 of 55:

```text
    1 | ---
    2 | ##### RedHat os familly
    3 | 
    4 | - name: "copy <|> Copy osdeploy files {{ pxe_stack_htdocs_path }}/pxe/osdeploy/"
    5 |   ansible.builtin.copy:
    6 |     src: osdeploy/redhat_{{ item.major }}.ipxe
    7 |     dest: "{{ pxe_stack_htdocs_path }}/pxe/osdeploy/redhat_{{ item.major }}.ipxe"
    8 |     mode: 0644
    9 |     owner: "{{ pxe_stack_apache_user }}"
   10 |     group: "{{ pxe_stack_apache_group }}"
   11 |   loop: "{{ pxe_stack_supported_os.redhat }}"
   12 | 
   13 | - name: file <|> Generate links for all supported OS
   14 |   ansible.builtin.file:
   15 |     src: redhat_{{ item.0.major }}.ipxe
   16 |     dest: "{{ pxe_stack_htdocs_path }}/pxe/osdeploy/{{ item.1 }}_{{ item.0.major }}.ipxe"
   17 |     mode: 0644
   18 |     owner: "{{ pxe_stack_apache_user }}"
   19 |     group: "{{ pxe_stack_apache_group }}"
   20 |     state: link
   21 |     force: true
   22 |   loop: "{{ pxe_stack_supported_os.redhat | subelements('distributions') }}"
   23 |   when: item.1 != 'redhat'
   24 | 
   25 | - name: "template <|> Generate kickstarts {{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{item}.kickstart.cfg"
   26 |   ansible.builtin.template:
   27 |     src: "RedHat/kickstart.cfg.j2"
   28 |     dest: "{{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{{ item | trim }}.kickstart.cfg"
   29 |     mode: 0644
   30 |     owner: "{{ pxe_stack_apache_user }}"
   31 |     group: "{{ pxe_stack_apache_group }}"
   32 |   vars:
   33 |     equipment: "{{ pxe_stack_equipment_profiles[item] | default({}, true) }}"
   34 |   loop: "{{ pxe_stack_equipment_profiles | default({}, true) | flatten(levels=1) }}"
   35 |   when:
   36 |     - (pxe_stack_equipment_profiles[item]['hw']['hw_equipment_type'] | default(pxe_stack_hw_equipment_type, true)) == "server"
   37 |     - (pxe_stack_equipment_profiles[item]['os']['os_operating_system']['distribution'] | default(pxe_stack_os_operating_system.distribution, true) | lower) in ['redhat', 'rhel', 'centos', 'centosstream', 'rockylinux', 'cloudlinux', 'oraclelinux', 'almalinux']
   38 |   tags:
   39 |     - template
   40 | 
   41 | - name: "template <|> Generate equipment_profiles {{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{item}.ipxe"
   42 |   ansible.builtin.template:
   43 |     src: "RedHat/equipment_profile_ks.ipxe.j2"
   44 |     dest: "{{ pxe_stack_htdocs_path }}/pxe/equipment_profiles/{{ item | trim }}.ipxe"
   45 |     mode: 0644
   46 |     owner: "{{ pxe_stack_apache_user }}"
   47 |     group: "{{ pxe_stack_apache_group }}"
   48 |   vars:
   49 |     equipment: "{{ pxe_stack_equipment_profiles[item] | default({}, true) }}"
   50 |   loop: "{{ pxe_stack_equipment_profiles | default({}, true) | flatten(levels=1) }}"
   51 |   when:
   52 |     - (pxe_stack_equipment_profiles[item]['hw']['hw_equipment_type'] | default(pxe_stack_hw_equipment_type, true)) == "server"
   53 |     - (pxe_stack_equipment_profiles[item]['os']['os_operating_system']['distribution'] | default(pxe_stack_os_operating_system.distribution, true) | lower) in ['redhat', 'rhel', 'centos', 'centosstream', 'rockylinux', 'cloudlinux', 'oraclelinux', 'almalinux']
   54 |   tags:
   55 |     - template
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-003

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: Maintainability/complexity
- Rule: `ansibleguard/deprecated-modules`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `plugins/tripleo-overcloud/tasks/upgrade/10/main.yml` (reported anchor line 174)
- Object: `task` `33c27ed1d6af01bea03e971f53d691a828b089d51cf1e1b69458cc8d9a25c2b7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–180 of 180:

```text
    1 | ---
    2 | - name: Setting temp_dir
    3 |   file:
    4 |       path: "{{ temp_dir }}"
    5 |       state: directory
    6 | 
    7 | - name: SSL Config
    8 |   include_tasks: "ssl.yml"
    9 |   tags:
   10 |       - upgrade
   11 |       - upgrade_ssl
   12 | 
   13 | - block:
   14 |     - debug: msg="Starting floating IP dataplane ping check before Ceilometer migration"
   15 |     - include: ../../update/common/startping.yaml
   16 |   when: install.dataplaneping|default(False)
   17 |   vars:
   18 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
   19 | 
   20 | - name: Pre-Upgrade Ceilometer migration
   21 |   include_tasks: "ceilometer_migration.yml"
   22 |   tags:
   23 |       - upgrade
   24 |       - upgrade_ceilometer
   25 |   vars:
   26 |       ceilometer_migration_script: "~/ceilometer_migration.sh"
   27 | 
   28 | - block:
   29 |     - debug: msg="Ending floating IP dataplane ping check after Ceilometer migration"
   30 |     - include: ../../update/common/endping.yaml
   31 |   when: install.dataplaneping|default(False)
   32 | 
   33 | - block:
   34 |     - debug: msg="Starting floating IP dataplane ping check before Overcloud Upgrade Init"
   35 |     - include: ../../update/common/startping.yaml
   36 |   when: install.dataplaneping|default(False)
   37 |   vars:
   38 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
   39 | 
   40 | - name: Overcloud Upgrade Init
   41 |   include_tasks: "upgrade_init.yml"
   42 |   tags:
   43 |       - upgrade
   44 |       - upgrade_init
   45 |   vars:
   46 |       upgrade_init_script: "~/upgrade_init.sh"
   47 | 
   48 | - block:
   49 |     - debug: msg="Ending floating IP dataplane ping check after Overcloud Upgrade Init"
   50 |     - include: ../../update/common/endping.yaml
   51 |   when: install.dataplaneping|default(False)
   52 | 
   53 | - name: Object Storage Upgrade
   54 |   shell: |
   55 |       source {{ undercloud_rc }}
   56 |       upgrade-non-controller.sh --upgrade {{ item }} &>> swift-upgrade.log
   57 |   tags:
   58 |     - upgrade
   59 |     - upgrade_object_storage
   60 |   with_items: "{{ groups.swift|default([])|difference(groups.unused|default([]))|default([]) }}"
   61 | 
   62 | - name: Check if there are any stopped pacemaker resources
   63 |   become: true
   64 |   command: pcs status
   65 |   register: pcs_status
   66 |   delegate_to: "{{ groups.controller | first }}"
   67 | 
   68 | - name: Cleanup resources if any stopped resource
   69 |   become: true
   70 |   command: pcs resource cleanup --force
   71 |   when: pcs_status.stdout.find("Stopped") > -1
   72 |   register: pcs_stopped
   73 |   delegate_to: "{{ groups.controller | first }}"
   74 | 
   75 | - block:
   76 |     - debug: msg="Starting floating IP dataplane ping check before Controller And Block Storage Upgrade"
   77 |     - include: ../../update/common/startping.yaml
   78 |   when: install.dataplaneping|default(False)
   79 |   vars:
   80 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
   81 | 
   82 | - name: Controller And Block Storage Upgrade
   83 |   include_tasks: "controller_upgrade.yml"
   84 |   tags:
   85 |       - upgrade
   86 |       - upgrade_controller
   87 |   vars:
   88 |       controller_upgrade_script: "~/controller_upgrade.sh"
   89 | 
   90 | - block:
   91 |     - debug: msg="Ending floating IP dataplane ping check after Controller And Block Storage Upgrade"
   92 |     - include: ../../update/common/endping.yaml
   93 |   when: install.dataplaneping|default(False)
   94 | 
   95 | - block:
   96 |     - debug: msg="Starting floating IP dataplane ping check before Ceph Upgrade"
   97 |     - include: ../../update/common/startping.yaml
   98 |   when: install.dataplaneping|default(False)
   99 |   vars:
  100 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  101 | 
  102 | - name: Ceph Upgrade
  103 |   shell: |
  104 |       source {{ undercloud_rc }}
  105 |       upgrade-non-controller.sh --upgrade {{ item }} &>> ceph-upgrade.log
  106 |   tags:
  107 |     - upgrade
  108 |     - upgrade_ceph
  109 |   with_items: "{{ groups.ceph|default([])|difference(groups.unused|default([]))|default([]) }}"
  110 | 
  111 | - block:
  112 |     - debug: msg="Ending floating IP dataplane ping check after Ceph Upgrade"
  113 |     - include: ../../update/common/endping.yaml
  114 |   when: install.dataplaneping|default(False)
  115 | 
  116 | - block:
  117 |     - debug: msg="Starting floating IP dataplane ping check before Compute Upgrade"
  118 |     - include: ../../update/common/startping.yaml
  119 |   when: install.dataplaneping|default(False)
  120 |   vars:
  121 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  122 | 
  123 | - name: Compute Upgrade
  124 |   shell: |
  125 |       source {{ undercloud_rc }}
  126 |       upgrade-non-controller.sh --upgrade {{ item }} &>> compute-upgrade.log
  127 |   tags:
  128 |     - upgrade
  129 |     - upgrade_compute
  130 |   with_items: "{{ groups.compute|default([])|difference(groups.unused|default([]))|default([]) }}"
  131 | 
  132 | - block:
  133 |     - debug: msg="Ending floating IP dataplane ping check after Compute Upgrade"
  134 |     - include: ../../update/common/endping.yaml
  135 |   when: install.dataplaneping|default(False)
  136 | 
  137 | - block:
  138 |     - debug: msg="Starting floating IP dataplane ping check before Convergence"
  139 |     - include: ../../update/common/startping.yaml
  140 |   when: install.dataplaneping|default(False)
  141 |   vars:
  142 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  143 | 
  144 | - name: Convergence
  145 |   include_tasks: "convergence.yml"
  146 |   tags:
  147 |       - upgrade
  148 |       - upgrade_convergence
  149 |   vars:
  150 |       convergence_script: "~/convergence.sh"
  151 | 
  152 | - block:
  153 |     - debug: msg="Ending floating IP dataplane ping check after Convergence"
  154 |     - include: ../../update/common/endping.yaml
  155 |   when: install.dataplaneping|default(False)
  156 | 
  157 | - block:
  158 |     - debug: msg="Starting floating IP dataplane ping check before Post-Upgrade Aodh migration"
  159 |     - include: ../../update/common/startping.yaml
  160 |   when: install.dataplaneping|default(False)
  161 |   vars:
  162 |       overcloudrc_file: "{{ ansible_user_dir }}/{{ install.overcloud.stack }}rc"
  163 | 
  164 | - name: Overcloud Post-Upgrade Aodh migration
  165 |   include_tasks: "aodh_migration.yml"
  166 |   tags:
  167 |       - upgrade
  168 |       - upgrade_aodh
  169 |   vars:
  170 |       aodh_migration_script: "~/aodh_migration.sh"
  171 | 
  172 | - block:
  173 |     - debug: msg="Ending floating IP dataplane ping check after Post-Upgrade Aodh migration"
  174 |     - include: ../../update/common/endping.yaml
  175 |   when: install.dataplaneping|default(False)
  176 | 
  177 | - name: Deleting temp folder
  178 |   file:
  179 |       path: "{{ temp_dir }}"
  180 |       state: absent
```

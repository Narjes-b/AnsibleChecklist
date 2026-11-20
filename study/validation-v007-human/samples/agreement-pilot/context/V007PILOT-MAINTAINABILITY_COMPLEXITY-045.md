# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-045

- Repository: `bluebanquise/bluebanquise`
- Commit: `fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0`
- Family: Maintainability/complexity
- Rule: `ansibleguard/undocumented-complex-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `collections/infrastructure/roles/rsyslog/tasks/main.yml` (reported anchor line 31)
- Object: `source_location` `24f1207084106c717b8b815073fcdf82ef89531a411ba36fe73eb4500acf2168`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–90 of 90:

```text
    1 | ---
    2 | - name: include_vars <|> Gather OS specific variables
    3 |   # This task gathers variables defined in OS specific files.
    4 |   #
    5 |   # Search vars in:
    6 |   #  - <distribution>_<major>.yml    # eg. CentOS_8.yml
    7 |   #  - <os_family>_<major>.yml       # eg. RedHat_8.yml
    8 |   #  - <distribution>.yml            # eg. CentOS.yml
    9 |   #  - <os_family>.yml               # eg. RedHat.yml
   10 |   #
   11 |   # If no OS specific file is found, the role will default to vars/main.yml
   12 |   #
   13 |   ansible.builtin.include_vars: "{{ item }}"
   14 |   with_first_found:
   15 |     - files:
   16 |         - "vars/{{ ansible_facts.distribution | replace(' ','_') }}_{{ ansible_facts.distribution_major_version }}.yml"
   17 |         - "vars/{{ ansible_facts.os_family }}_{{ ansible_facts.distribution_major_version }}.yml"
   18 |         - "vars/{{ ansible_facts.distribution | replace(' ','_') }}.yml"
   19 |         - "vars/{{ ansible_facts.os_family }}.yml"
   20 |       skip: true
   21 |   tags:
   22 |     - always
   23 | 
   24 | - name: "package <|> Install {{ rsyslog_packages_to_install }} packages"
   25 |   ansible.builtin.package:
   26 |     name: "{{ rsyslog_packages_to_install }}"
   27 |     state: present
   28 |   tags:
   29 |     - package
   30 | 
   31 | - name: "template <|> Generate {{ rsyslog_conf_path }}"
   32 |   ansible.builtin.template:
   33 |     src: rsyslog.conf.j2
   34 |     dest: "{{ rsyslog_custom_conf_path | default(rsyslog_conf_path) }}"
   35 |     owner: root
   36 |     group: root
   37 |     mode: 0644
   38 |   notify: service <|> Restart rsyslog service
   39 |   when: "'rsyslog.conf' not in (rsyslog_configuration_files | default([]) | selectattr('name','defined') | map(attribute='name') | list)"
   40 |   tags:
   41 |     - template
   42 | 
   43 | - name: "template <|> Generate custom rsyslog files"
   44 |   ansible.builtin.template:
   45 |     src: rsyslog.d_custom.conf.j2
   46 |     dest: "{{ item.path | default('/etc/rsyslog.d') }}/{{ item.name }}"
   47 |     owner: root
   48 |     group: root
   49 |     mode: 0644
   50 |   loop: "{{ rsyslog_configuration_files }}"
   51 |   loop_control:
   52 |     label: "Install configuration file {{ item.name }}"
   53 |   notify: service <|> Restart rsyslog service
   54 |   when: rsyslog_configuration_files is defined and rsyslog_configuration_files is iterable
   55 |   tags:
   56 |     - template
   57 | 
   58 | - name: include_tasks <|> Configure log Server
   59 |   ansible.builtin.include_tasks: "server.yml"
   60 |   when: rsyslog_profile == "server"
   61 | 
   62 | - name: include_tasks <|> Configure log Client
   63 |   ansible.builtin.include_tasks: "client.yml"
   64 |   when: rsyslog_profile == "client"
   65 | 
   66 | - name: seport <|> Allow syslog port into SELinux
   67 |   community.general.seport:
   68 |     ports: "{{ rsyslog_port }}"
   69 |     proto: "{{ item }}"
   70 |     setype: syslogd_port_t
   71 |     state: present
   72 |   when:
   73 |     - ansible_facts.os_family == "RedHat"
   74 |     - ansible_facts.selinux.status == "enabled"
   75 |   loop:
   76 |     - tcp
   77 |     - udp
   78 |   notify: service <|> Restart rsyslog service
   79 | 
   80 | - name: meta <|> Run handler tasks to restart rsyslog services
   81 |   ansible.builtin.meta: flush_handlers
   82 | 
   83 | - name: "service <|> Manage {{ rsyslog_services_to_start | join(' ') }} state"
   84 |   ansible.builtin.service:
   85 |     name: "{{ item }}"
   86 |     enabled: "{{ (rsyslog_enable_services | default(bb_enable_services) | default(true) | bool) | ternary(true, false) }}"
   87 |     state: "{{ (rsyslog_start_services | default(bb_start_services) | default(true) | bool) | ternary('started', omit) }}"
   88 |   loop: "{{ rsyslog_services_to_start }}"
   89 |   tags:
   90 |     - service
```

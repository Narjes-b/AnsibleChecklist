# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-024

- Repository: `JenswBE/setup`
- Commit: `18c39275cc08ae3f7bea8b7ee0624876b8fa72fe`
- Family: Maintainability/complexity
- Rule: `ansibleguard/unused-handler`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `server/docker_host.yml` (reported anchor line 121)
- Object: `source_location` `004104f9738c17f5d38e780dc652abd1741a1f0bc14277cdbbbbe3f76c27d95f`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–124 of 124:

```text
    1 | - name: Init
    2 |   hosts: docker_host
    3 |   vars:
    4 |     playbook_supported_distros:
    5 |       - Debian
    6 | 
    7 |   pre_tasks:
    8 |     - name: Include init tasks
    9 |       ansible.builtin.include_tasks: "tasks/init.yml"
   10 |       tags: ["always"]
   11 | 
   12 |   roles:
   13 |     - role: jenswbe.basics
   14 |       tags: ["basics"]
   15 | 
   16 |     - role: jenswbe.automatic_updates
   17 |       tags: ["automatic_updates"]
   18 | 
   19 | - name: Setup Homelab
   20 |   hosts: docker_host:&homelab
   21 |   gather_facts: false
   22 |   roles:
   23 |     - role: jenswbe.network_config
   24 |       tags: ["network_config"]
   25 | 
   26 |     - role: jenswbe.powersavings
   27 |       tags: ["powersavings"]
   28 | 
   29 | - name: Setup VPS
   30 |   hosts: docker_host:&vps
   31 |   gather_facts: false
   32 |   roles:
   33 |     - role: jenswbe.wireguard # Docker requires Wireguard for GELF logging transport
   34 |       tags: ["wireguard"]
   35 | 
   36 | - name: Setup other roles and tasks
   37 |   hosts: docker_host
   38 |   gather_facts: false
   39 |   roles:
   40 |     - role: geerlingguy.security
   41 |       become: true
   42 |       tags: ["gsecurity"]
   43 | 
   44 |     - role: geerlingguy.docker
   45 |       become: true
   46 |       tags: ["gdocker"]
   47 |       vars:
   48 |         docker_daemon_options:
   49 |           default-address-pools:
   50 |             - base: "172.16.0.0/12"
   51 |               size: 24 # Default is /16
   52 |           icc: false
   53 | 
   54 |     - role: jenswbe.docker_host
   55 |       tags: ["docker", "docker_host"]
   56 | 
   57 |     - role: jenswbe.observability
   58 |       tags: ["observability", "logging", "monitoring"]
   59 |       vars:
   60 |         jwob_with_docker: true
   61 | 
   62 |     - role: jenswbe.crowdsec
   63 |       tags: ["crowdsec"]
   64 | 
   65 |     - role: jenswbe.firewall
   66 |       tags: ["firewall"]
   67 | 
   68 |   tasks:
   69 |     - name: Copy systemd system unit templates
   70 |       when: '("templates/hosts/" + inventory_hostname + "/etc/systemd/system") is exists'
   71 |       ansible.builtin.include_role:
   72 |         name: jenswbe.copy_dir
   73 |       vars:
   74 |         jwcd_source_templates_dir: "templates/hosts/{{ inventory_hostname }}/etc/systemd/system"
   75 |         jwcd_destination_dir: "/etc/systemd/system"
   76 |         jwcd_privileged: true
   77 |         jwcd_destination_mode_files: "644"
   78 |         jwcd_destination_mode_dirs: "755"
   79 |       tags: ["systemd"]
   80 | 
   81 |     - name: Force systemd reload
   82 |       become: true
   83 |       ansible.builtin.systemd_service:
   84 |         daemon_reload: true
   85 |       tags: ["systemd"]
   86 | 
   87 |     - name: Docker login to GHCR
   88 |       become: true
   89 |       community.docker.docker_login:
   90 |         registry_url: ghcr.io
   91 |         username: USERNAME
   92 |         password: "{{ docker_ghcr_personal_access_token }}"
   93 |       tags: ["docker"]
   94 | 
   95 |     - name: Include host specific tasks
   96 |       ansible.builtin.include_tasks: "tasks/hosts/{{ inventory_hostname }}.yml"
   97 |       tags: ["always"]
   98 | 
   99 |     - name: "Copy templates home/_user_/deploy"
  100 |       ansible.builtin.include_role:
  101 |         name: jenswbe.copy_dir
  102 |       vars:
  103 |         jwcd_source_templates_dir: "templates/hosts/{{ inventory_hostname }}/home/_user_/deploy"
  104 |         jwcd_destination_dir: "{{ ansible_facts['user_dir'] }}/deploy"
  105 |         jwcd_destination_delete_extra: true
  106 |       tags: ["docker"]
  107 | 
  108 |     - name: Restart changed Docker services
  109 |       when: "item in jwcd_copy_diff"
  110 |       become: true
  111 |       community.docker.docker_compose_v2:
  112 |         project_src: "{{ ansible_facts['user_dir'] }}/deploy"
  113 |         services: ["{{ item }}"]
  114 |         state: restarted
  115 |       retries: 3
  116 |       delay: 10
  117 |       tags: ["docker"]
  118 |       loop: "{{ docker_restart_changed_services }}"
  119 | 
  120 |   handlers:
  121 |     - name: Update resolvconf
  122 |       become: true
  123 |       changed_when: true
  124 |       ansible.builtin.command: /usr/sbin/resolvconf -u
```

# Frozen source context: V007PILOT-STRUCTURE_REUSE-041

- Repository: `osism/ansible-collection-services`
- Commit: `131734f2c007d0009a7fc218849f4ede66c7c899`
- Family: Structure/reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/manager/tasks/service.yml` (reported anchor line 1)
- Object: `source_location` `29e4adb7a6e60051742b8ba5ec1136fb34217cf2f521508db68c0312d7944ee7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–104 of 104:

```text
    1 | ---
    2 | - name: Copy manager systemd unit file
    3 |   become: true
    4 |   ansible.builtin.template:
    5 |     src: manager.service.j2
    6 |     dest: "/etc/systemd/system/manager.service"
    7 |     mode: 0644
    8 |     owner: root
    9 |     group: root
   10 |   register: manager_systemd_unit_file
   11 | 
   12 | - name: Create traefik external network
   13 |   community.docker.docker_network:
   14 |     name: "{{ traefik_external_network_name }}"
   15 |     ipam_config:
   16 |       - subnet: "{{ traefik_external_network_cidr }}"
   17 |   when: ara_server_traefik|bool
   18 | 
   19 | - name: Set mariadb healthcheck for mariadb < 11.0.0
   20 |   ansible.builtin.set_fact:
   21 |     ara_server_mariadb_healthcheck: "mysqladmin status -h localhost -u $$MYSQL_USER -p$$MYSQL_PASSWORD || exit 1"
   22 |   when:
   23 |     - "ara_server_mariadb_tag is version('11.0.0', '<')"
   24 | 
   25 | - name: Set mariadb healthcheck for mariadb >= 11.0.0
   26 |   ansible.builtin.set_fact:
   27 |     ara_server_mariadb_healthcheck: "healthcheck.sh --connect --innodb_initialized --mariadbupgrade"
   28 |   when:
   29 |     - "ara_server_mariadb_tag is version('11.0.0', '>=')"
   30 | 
   31 | - name: Copy docker-compose.yml file
   32 |   ansible.builtin.template:
   33 |     src: docker-compose.yml.j2
   34 |     dest: "{{ manager_docker_compose_directory }}/docker-compose.yml"
   35 |     owner: "{{ operator_user }}"
   36 |     group: "{{ operator_group }}"
   37 |     mode: 0640
   38 |   notify:
   39 |     - Restart manager service
   40 | 
   41 | - name: Pull container images
   42 |   community.docker.docker_compose_v2_pull:
   43 |     project_src: "{{ manager_docker_compose_directory }}"
   44 |   when: manager_pre_pull | bool
   45 |   retries: 3
   46 |   delay: 30
   47 |   notify: Restart manager service
   48 | 
   49 | - name: "Stop and disable old service {{ manager_old_service_name }}"
   50 |   become: true
   51 |   ansible.builtin.systemd_service:
   52 |     name: "{{ manager_old_service_name }}"
   53 |     state: stopped
   54 |     enabled: false
   55 | 
   56 | - name: Do a manual start of the manager service
   57 |   ansible.builtin.command: "/usr/bin/docker compose --project-directory {{ manager_docker_compose_directory }} up -d --remove-orphans"
   58 |   changed_when: true
   59 |   notify: Wait for an healthy manager service
   60 |   when: manager_service_manual_start | bool
   61 | 
   62 | - name: Ensure that the manager service is up and running
   63 |   block:
   64 |     - name: Manage manager service
   65 |       become: true
   66 |       ansible.builtin.systemd_service:
   67 |         name: "{{ manager_service_name }}"
   68 |         state: started
   69 |         enabled: true
   70 |         daemon_reload: "{{ manager_systemd_unit_file.changed }}"
   71 |       register: manager_service
   72 |       notify: Wait for manager service to start
   73 | 
   74 |   rescue:
   75 |     # Compose is not always reliable when starting services. Therefore,
   76 |     # in case of an error at startup, another stop and start of the
   77 |     # service is tried here.
   78 |     - name: Stop manager service
   79 |       become: true
   80 |       ansible.builtin.systemd_service:
   81 |         name: "{{ manager_service_name }}"
   82 |         state: stopped
   83 | 
   84 |     - name: Do a manual start of the manager service
   85 |       ansible.builtin.command: "/usr/bin/docker compose --project-directory {{ manager_docker_compose_directory }} up -d --remove-orphans"
   86 |       changed_when: true
   87 |       notify: Wait for manager service to start
   88 | 
   89 |     # This does not change anything on the service side, but the unit is
   90 |     # then in the expected state.
   91 |     - name: Start manager service again
   92 |       become: true
   93 |       ansible.builtin.systemd_service:
   94 |         name: "{{ manager_service_name }}"
   95 |         state: started
   96 |       register: manager_service
   97 | 
   98 | - name: Register that manager service was started
   99 |   ansible.builtin.set_fact:
  100 |     _manager_service_restart: false
  101 |   when: manager_service.changed  # noqa no-handler
  102 | 
  103 | - name: Flush handlers
  104 |   ansible.builtin.meta: flush_handlers
```

## Frozen tracked paths in the relevant role/scope

```text
roles/manager/README.md
roles/manager/defaults/main.yml
roles/manager/handlers/main.yml
roles/manager/meta/main.yml
roles/manager/tasks/config-ansible.yml
roles/manager/tasks/config-ara.yml
roles/manager/tasks/config-celery.yml
roles/manager/tasks/config-frontend.yml
roles/manager/tasks/config-netbox.yml
roles/manager/tasks/config-scripts.yml
roles/manager/tasks/config-vault.yml
roles/manager/tasks/config-wrapper.yml
roles/manager/tasks/config.yml
roles/manager/tasks/initialize-vault.yml
roles/manager/tasks/initialize.yml
roles/manager/tasks/install-Debian-family.yml
roles/manager/tasks/install-RedHat-family.yml
roles/manager/tasks/main.yml
roles/manager/tasks/service.yml
roles/manager/tasks/verify-versions.yml
roles/manager/templates/check-service-manager-versions.sh.j2
roles/manager/templates/config-netbox-secret.j2
roles/manager/templates/config-ssh-key.j2
roles/manager/templates/config-vault-key.j2
roles/manager/templates/config.j2
roles/manager/templates/docker-compose.yml.j2
roles/manager/templates/env/all.env.j2
roles/manager/templates/env/ansible.env.j2
roles/manager/templates/env/ara-server.env.j2
roles/manager/templates/env/ara.env.j2
roles/manager/templates/env/client.env.j2
roles/manager/templates/env/conductor.env.j2
roles/manager/templates/env/frontend.env.j2
roles/manager/templates/env/inventory-reconciler.env.j2
roles/manager/templates/env/listener.env.j2
roles/manager/templates/env/mariadb.env.j2
roles/manager/templates/env/netbox.env.j2
roles/manager/templates/env/openstack.env.j2
roles/manager/templates/env/postgres.env.j2
roles/manager/templates/env/vault.env.j2
roles/manager/templates/manager.service.j2
roles/manager/templates/scripts/osism-include.j2
roles/manager/templates/vault.hcl.j2
roles/manager/templates/wrapper/cilium.j2
roles/manager/templates/wrapper/flux.j2
roles/manager/templates/wrapper/hubble.j2
roles/manager/templates/wrapper/osism-ansible.j2
roles/manager/templates/wrapper/osism-ceph.j2
roles/manager/templates/wrapper/osism-custom.j2
roles/manager/templates/wrapper/osism-generic.j2
roles/manager/templates/wrapper/osism-infrastructure.j2
roles/manager/templates/wrapper/osism-kolla.j2
roles/manager/templates/wrapper/osism-manager.j2
roles/manager/templates/wrapper/osism-monitoring.j2
roles/manager/templates/wrapper/osism-openstack.j2
roles/manager/templates/wrapper/osism-run-without-secrets.j2
roles/manager/templates/wrapper/osism-run.j2
roles/manager/templates/wrapper/osism-state.j2
roles/manager/templates/wrapper/osism-update-docker.j2
roles/manager/templates/wrapper/osism-validate.j2
roles/manager/templates/wrapper/osism.j2
roles/manager/vars/Debian-family.yml
roles/manager/vars/RedHat-family.yml
roles/manager/vars/scripts.yml
roles/manager/vars/wrapper.yml
```

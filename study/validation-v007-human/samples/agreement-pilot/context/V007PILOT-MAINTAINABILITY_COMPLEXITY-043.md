# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-043

- Repository: `trailofbits/algo`
- Commit: `20e22a8715c198b38c01c1ca62d0953b93587a74`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/cloud-gce/tasks/main.yml` (reported anchor line 16)
- Object: `task` `879dac8ca9748e94376e7a3b648c202ca13ced647777af5b84d98553be8e5001`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–81 of 81:

```text
    1 | ---
    2 | - name: Include prompts
    3 |   import_tasks: prompts.yml
    4 | 
    5 | - name: Network configured
    6 |   gcp_compute_network:
    7 |     auth_kind: serviceaccount
    8 |     service_account_file: "{{ credentials_file_path }}"
    9 |     project: "{{ project_id }}"
   10 |     name: algovpn
   11 |     auto_create_subnetworks: true
   12 |     routing_config:
   13 |       routing_mode: REGIONAL
   14 |   register: gcp_compute_network
   15 | 
   16 | - name: Firewall configured
   17 |   gcp_compute_firewall:
   18 |     auth_kind: serviceaccount
   19 |     service_account_file: "{{ credentials_file_path }}"
   20 |     project: "{{ project_id }}"
   21 |     name: algovpn
   22 |     network: "{{ gcp_compute_network }}"
   23 |     direction: INGRESS
   24 |     allowed:
   25 |       - ip_protocol: udp
   26 |         ports:
   27 |           - "500"
   28 |           - "4500"
   29 |           - "{{ wireguard_port | string }}"
   30 |       - ip_protocol: tcp
   31 |         ports:
   32 |           - "{{ ssh_port }}"
   33 |       - ip_protocol: icmp
   34 | 
   35 | - when: cloud_providers.gce.external_static_ip
   36 |   block:
   37 |     - name: External IP allocated
   38 |       gcp_compute_address:
   39 |         auth_kind: serviceaccount
   40 |         service_account_file: "{{ credentials_file_path }}"
   41 |         project: "{{ project_id }}"
   42 |         name: "{{ algo_server_name }}"
   43 |         region: "{{ algo_region }}"
   44 |       register: gcp_compute_address
   45 | 
   46 |     - name: Set External IP as a fact
   47 |       set_fact:
   48 |         external_ip: "{{ gcp_compute_address.address }}"
   49 | 
   50 | - name: Instance created
   51 |   gcp_compute_instance:
   52 |     auth_kind: serviceaccount
   53 |     service_account_file: "{{ credentials_file_path }}"
   54 |     project: "{{ project_id }}"
   55 |     name: "{{ algo_server_name }}"
   56 |     zone: "{{ algo_zone }}"
   57 |     machine_type: "{{ cloud_providers.gce.size }}"
   58 |     disks:
   59 |       - auto_delete: true
   60 |         boot: true
   61 |         initialize_params:
   62 |           source_image: projects/ubuntu-os-cloud/global/images/family/{{ cloud_providers.gce.image }}
   63 |     metadata:
   64 |       ssh-keys: algo:{{ ssh_public_key_lookup }}
   65 |       user-data: "{{ lookup('template', 'files/cloud-init/base.yml') }}"
   66 |     network_interfaces:
   67 |       - network: "{{ gcp_compute_network }}"
   68 |         access_configs:
   69 |           - name: "{{ algo_server_name }}"
   70 |             nat_ip: "{{ gcp_compute_address | default(None) }}"
   71 |             type: ONE_TO_ONE_NAT
   72 |     tags:
   73 |       items:
   74 |         - environment-algo
   75 |   register: gcp_compute_instance
   76 | 
   77 | - set_fact:
   78 |     cloud_instance_ip: "{{ gcp_compute_instance.networkInterfaces[0].accessConfigs[0].natIP }}"
   79 |     ansible_ssh_user: algo
   80 |     ansible_ssh_port: "{{ ssh_port }}"
   81 |     cloudinit: true
```

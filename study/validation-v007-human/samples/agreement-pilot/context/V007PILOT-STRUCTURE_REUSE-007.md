# Frozen source context: V007PILOT-STRUCTURE_REUSE-007

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `plugins/virsh/provision_vms_bgp.yml` (reported anchor line 1)
- Object: `source_location` `9e69df01aee155191cc6e307079d961aa82abba68fe5fcd0e5e4eb09499d7afb`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–85 of 85:

```text
    1 | ---
    2 | - name: Provision VMs
    3 |   hosts: "{{ (_run_condition | bool) | ternary('hypervisor', 'none') }}"
    4 |   gather_facts: yes
    5 |   any_errors_fatal: true
    6 |   vars:
    7 |     base_image_path: /var/lib/libvirt/images
    8 |     url: "{{ provision.image.url }}"
    9 |   tasks:
   10 |     - name: load nodes topology configuration
   11 |       include_tasks: tasks/load_topology.yml
   12 |       with_dict: "{{ provision.topology.nodes }}"
   13 |       loop_control:
   14 |           loop_var: node
   15 | 
   16 |     - name: provision image for each node
   17 |       include_tasks: tasks/download_images.yml
   18 |       with_dict: "{{ topology_nodes }}"
   19 |       loop_control:
   20 |           loop_var: node
   21 |       when: node.value.node_indexes|length > 0
   22 |       tags: images
   23 | 
   24 |     - name: Load bgp networks
   25 |       include_vars: "{{ playbook_dir }}/defaults/topology/network/bgp_networks.yml"
   26 | 
   27 |     - name: Create tmp bgp-ifcfg-files directory
   28 |       tempfile:
   29 |         state: directory
   30 |         prefix: bgp-ifcfg-files-
   31 |       register: tmp_bgp_ifcfg_dir
   32 | 
   33 |     - name: initialize dictionary for results
   34 |       set_fact:
   35 |         vms_jobs: {}
   36 | 
   37 |     - name: create disks for each bgp vm
   38 |       vars:
   39 |         tmp_ifcfg_dir: tmp_bgp_ifcfg_dir.path
   40 |       include_tasks: tasks/vms_1_create_disk_bgp.yml
   41 |       with_dict: "{{ topology_nodes }}"
   42 |       loop_control:
   43 |         loop_var: node
   44 |       when: node.value.node_indexes|length > 0
   45 | 
   46 |     - name: wait for bgp vms base images
   47 |       include_tasks: tasks/vms_wait_for_disks_bgp.yml
   48 |       with_dict: "{{ topology_nodes }}"
   49 |       loop_control:
   50 |         loop_var: node
   51 |       when: node.value.node_indexes|length > 0
   52 | 
   53 |     - name: initialize dictionary for results
   54 |       set_fact:
   55 |         vms_jobs: {}
   56 | 
   57 |     - name: customize disks
   58 |       vars:
   59 |         tmp_ifcfg_dir: tmp_bgp_ifcfg_dir.path
   60 |       include_tasks: tasks/vms_2_customize_disks_bgp.yml
   61 |       with_dict: "{{ topology_nodes }}"
   62 |       loop_control:
   63 |         loop_var: node
   64 |       when: node.value.node_indexes|length > 0
   65 | 
   66 |     - name: wait for bgp vms base images
   67 |       include_tasks: tasks/vms_wait_for_disks_bgp.yml
   68 |       with_dict: "{{ topology_nodes }}"
   69 |       loop_control:
   70 |         loop_var: node
   71 |       when: node.value.node_indexes|length > 0
   72 | 
   73 |     - name: start up bgm vms
   74 |       include_tasks: tasks/vms_3_start_up_bgp_vms.yml
   75 |       with_dict: "{{ topology_nodes }}"
   76 |       loop_control:
   77 |         loop_var: node
   78 |       when: node.value.node_indexes|length > 0
   79 | 
   80 |     - name: get VMs hardware adresses
   81 |       include_tasks: tasks/vms_4_hwaddr_bgp.yml
   82 |       with_dict: "{{ topology_nodes }}"
   83 |       loop_control:
   84 |         loop_var: node
   85 |       when: node.value.node_indexes|length > 0
```

## Frozen tracked paths in the relevant role/scope

```text
.ansible-lint
.gitignore
.gitreview
.pre-commit-config.yaml
.yamllint
LICENSE
Makefile
README.rst
docs/Makefile
docs/examples/3_nets.yml
docs/examples/ansible.cfg
docs/examples/main.yml
docs/examples/plugin.spec
docs/examples/v1_syntax.sh
docs/examples/v2_syntax.sh
docs/requirements.txt
docs/source/_static/.placeholder
docs/source/advance_features.rst
docs/source/baremetal.rst
docs/source/beaker.rst
docs/source/bootstrap.rst
docs/source/cdn_cookbook.rst
docs/source/changes.rst
docs/source/cloud-config.rst
docs/source/collect-logs.rst
docs/source/composable_roles.rst
docs/source/conf.py
docs/source/configuration.rst
docs/source/contacts.rst
docs/source/contribute.rst
docs/source/control_placement.rst
docs/source/controller_replacement.rst
docs/source/current_temporary_hacks.rst
docs/source/foreman.rst
docs/source/gabbi_tester.rst
docs/source/hybrid_deployment.rst
docs/source/hypervisor.rst
docs/source/index.rst
docs/source/interactive_ssh.rst
docs/source/list_builds.rst
docs/source/openstack_provisioner.rst
docs/source/ospdui_tester.rst
docs/source/ovb.rst
docs/source/plugins.rst
docs/source/plugins_guide.rst
docs/source/pytest_runner.rst
docs/source/rdo.rst
docs/source/release_notes.rst
docs/source/setup.rst
docs/source/splitstack.rst
docs/source/standalone_deployment.rst
docs/source/tempest.rst
docs/source/topology.rst
docs/source/tripleo-overcloud.rst
docs/source/tripleo-undercloud.rst
docs/source/troubleshoot.rst
docs/source/virsh.rst
docs/source/workspace.rst
etc/bash_completion.d/infrared
infrared.cfg.example
infrared/__init__.py
infrared/__main__.py
infrared/api.py
infrared/bash_completers.py
infrared/common/README.md
infrared/common/callback_plugins/README.rst
infrared/common/callback_plugins/junit_report.py
infrared/common/filter_plugins/README.rst
infrared/common/filter_plugins/absolute_path.py
infrared/common/filter_plugins/container_mirror.py
infrared/common/filter_plugins/from_csv.py
infrared/common/filter_plugins/from_xml.py
infrared/common/filter_plugins/openstack_release.py
infrared/common/library/fetch_bz.py
infrared/common/library/junitxml.py
infrared/common/library/rhos_release.py
infrared/common/library/virt_util.py
infrared/common/roles/README.rst
infrared/common/roles/cdn_registery/defaults/main.yml
infrared/common/roles/cdn_registery/tasks/main.yml
infrared/common/roles/cdn_registery/tasks/register_cdn.yml
infrared/common/roles/collect-ansible-facts/defaults/main.yml
infrared/common/roles/collect-ansible-facts/tasks/main.yml
infrared/common/roles/create_venv/defaults/main.yml
infrared/common/roles/create_venv/tasks/main.yml
infrared/common/roles/dstat/tasks/main.yml
infrared/common/roles/dstat/templates/dstat.service.j2
infrared/common/roles/freeipa-setup/README.md
infrared/common/roles/freeipa-setup/defaults/main.yml
infrared/common/roles/freeipa-setup/meta/main.yml
infrared/common/roles/freeipa-setup/tasks/ipa_prep.yml
infrared/common/roles/freeipa-setup/tasks/main.yml
infrared/common/roles/freeipa-setup/templates/deploy_freeipa.sh.j2
infrared/common/roles/freeipa-setup/templates/ipa_prep.sh.j2
infrared/common/roles/from-script/defaults/main.yml
infrared/common/roles/from-script/tasks/main.yml
infrared/common/roles/from-source/defaults/main.yml
infrared/common/roles/from-source/tasks/dlrn.yml
infrared/common/roles/from-source/tasks/main.yml
infrared/common/roles/from-source/templates/patched_rpms.j2
infrared/common/roles/inventory-update/README.rst
infrared/common/roles/inventory-update/defaults/main.yml
infrared/common/roles/inventory-update/tasks/main.yml
infrared/common/roles/inventory-update/templates/inventory.j2
infrared/common/roles/network/forward-port/defaults/main.yml
infrared/common/roles/network/forward-port/tasks/main.yml
infrared/common/roles/rdo-release/defaults/main.yml
infrared/common/roles/rdo-release/tasks/main.yml
infrared/common/roles/rdo-release/tasks/public-repos.yml
infrared/common/roles/rdo-release/tasks/rdo-release.yml
infrared/common/roles/resurrect_host/tasks/main.yaml
infrared/common/roles/rhos-release/defaults/main.yml
infrared/common/roles/rhos-release/files/select-mirror.sh
infrared/common/roles/rhos-release/files/use-mirror.sh
infrared/common/roles/rhos-release/tasks/main.yml
infrared/common/roles/shade/README.rst
infrared/common/roles/shade/defaults/main.yml
infrared/common/roles/shade/tasks/main.yml
infrared/common/roles/tls-ca/tasks/deploy.yml
infrared/common/roles/tls-ca/tasks/main.yml
[listing truncated after 120 paths]
```

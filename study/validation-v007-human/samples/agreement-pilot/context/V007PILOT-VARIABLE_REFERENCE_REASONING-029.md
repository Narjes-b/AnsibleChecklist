# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-029

- Repository: `axivo/k3s-cluster`
- Commit: `f0e3a56f57f0e13f9f8624af2bb370c7eb92063f`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/overriding-facts`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/k3s/tasks/upgrade.yaml` (reported anchor line 1)
- Object: `source_location` `e4fe362f0490f33aab08f7b8056571499a3995a35e4936087c88de736e5adb99`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–103 of 103:

```text
    1 | ---
    2 | - name: Role Facts
    3 |   ansible.builtin.import_tasks:
    4 |     file: facts.yaml
    5 | 
    6 | - name: Cluster Validation
    7 |   when: inventory_hostname == k3s_map.server.default_host
    8 |   run_once: true
    9 |   block:
   10 |     - name: Get binary statistics
   11 |       ansible.builtin.stat:
   12 |         path: '{{ k3s_node.binary }}'
   13 |       changed_when: not k3s_binary.stat.exists
   14 |       register: k3s_binary
   15 | 
   16 |     - name: Validate deployed cluster
   17 |       ansible.builtin.assert:
   18 |         that: k3s_binary.stat.exists
   19 |         fail_msg: 'ERROR: K3s cluster not deployed.'
   20 |         quiet: true
   21 | 
   22 |     - name: Get deployed cluster version
   23 |       kubernetes.core.k8s_cluster_info:
   24 |         kubeconfig: '{{ k3s_project.cluster.kubeconfig }}'
   25 |       register: k3s_cluster
   26 |       no_log: true
   27 | 
   28 | - name: Role Upgrade
   29 |   block:
   30 |     - name: Install k3s binary
   31 |       ansible.builtin.get_url:
   32 |         url: '{{ k3s_project.release.k3s.file }}'
   33 |         checksum: sha256:{{ k3s_project.release.k3s.checksum }}
   34 |         dest: '{{ k3s_node.binary }}'
   35 |         owner: root
   36 |         group: root
   37 |         mode: '755'
   38 |       register: k3s_result
   39 |       delay: 1
   40 |       retries: 3
   41 |       until: k3s_result is not failed
   42 |       when: k3s_cluster.version.server.kubernetes.gitVersion != k3s_vars.release.k3s.version
   43 | 
   44 |     - name: Get configuration file statistics
   45 |       ansible.builtin.stat:
   46 |         checksum: sha256
   47 |         path: '{{ k3s_project.cluster.config }}'
   48 |       register: k3s_config
   49 | 
   50 |     - name: Set role postinstall fact
   51 |       ansible.builtin.set_fact:
   52 |         k3s_postinstall: false
   53 | 
   54 |     - name: Update configuration file
   55 |       ansible.builtin.template:
   56 |         src: config.j2
   57 |         dest: '{{ k3s_project.cluster.config }}'
   58 |         owner: root
   59 |         group: root
   60 |         mode: '600'
   61 | 
   62 |     - name: Update service file
   63 |       ansible.builtin.template:
   64 |         src: service.j2
   65 |         dest: /etc/systemd/system/{{ k3s_node.service.name }}.service
   66 |         owner: root
   67 |         group: root
   68 |         mode: '644'
   69 | 
   70 |     - name: Role Configuration
   71 |       ansible.builtin.import_tasks:
   72 |         file: configuration.yaml
   73 | 
   74 |     - name: Set role postinstall fact
   75 |       ansible.builtin.set_fact:
   76 |         k3s_postinstall: true
   77 | 
   78 |     - name: Update configuration file
   79 |       ansible.builtin.template:
   80 |         src: config.j2
   81 |         dest: '{{ k3s_project.cluster.config }}'
   82 |         owner: root
   83 |         group: root
   84 |         mode: '600'
   85 | 
   86 |     - name: Get revised configuration file statistics
   87 |       ansible.builtin.stat:
   88 |         checksum: sha256
   89 |         path: '{{ k3s_project.cluster.config }}'
   90 |       register: k3s_config_revised
   91 | 
   92 |     - name: Schedule reboot
   93 |       ansible.builtin.file:
   94 |         path: /var/run/reboot-required
   95 |         access_time: preserve
   96 |         modification_time: preserve
   97 |         state: touch
   98 |         owner: root
   99 |         group: root
  100 |         mode: '644'
  101 |       when: >
  102 |         (k3s_config.stat.checksum != k3s_config_revised.stat.checksum) or
  103 |         (k3s_cluster.version.server.kubernetes.gitVersion != k3s_vars.release.k3s.version)
```

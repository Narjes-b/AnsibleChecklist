# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-009

- Repository: `kubernetes-sigs/kubespray`
- Commit: `9ee6f9b27981b251d77302fd6cf631f330e0ec39`
- Family: objective_correctness
- Rule: `ansibleguard/loop-legacy-syntax`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/kubernetes-apps/registry/tasks/main.yml` (reported anchor line 73)
- Flagged construct: not named by the finding; the anchor line 73 lies in the task at line 73, name `Registry | Create PVC manifests`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–98 of 98:

```text
    1 | ---
    2 | - name: Registry | check registry_service_type value
    3 |   fail:
    4 |     msg: "registry_service_type can only be 'ClusterIP', 'LoadBalancer' or 'NodePort'"
    5 |   when: registry_service_type not in ['ClusterIP', 'LoadBalancer', 'NodePort']
    6 | 
    7 | - name: Registry | Stop if registry_service_cluster_ip is defined when registry_service_type is not 'ClusterIP'
    8 |   fail:
    9 |     msg: "registry_service_cluster_ip support only compatible with ClusterIP."
   10 |   when:
   11 |     - registry_service_cluster_ip is defined and registry_service_cluster_ip | length > 0
   12 |     - registry_service_type != "ClusterIP"
   13 | 
   14 | - name: Registry | Stop if registry_service_loadbalancer_ip is defined when registry_service_type is not 'LoadBalancer'
   15 |   fail:
   16 |     msg: "registry_service_loadbalancer_ip support only compatible with LoadBalancer."
   17 |   when:
   18 |     - registry_service_loadbalancer_ip is defined and registry_service_loadbalancer_ip | length > 0
   19 |     - registry_service_type != "LoadBalancer"
   20 | 
   21 | - name: Registry | Stop if registry_service_nodeport is defined when registry_service_type is not 'NodePort'
   22 |   fail:
   23 |     msg: "registry_service_nodeport support only compatible with NodePort."
   24 |   when:
   25 |     - registry_service_nodeport is defined and registry_service_nodeport | length > 0
   26 |     - registry_service_type != "NodePort"
   27 | 
   28 | - name: Registry | Create addon dir
   29 |   file:
   30 |     path: "{{ kube_config_dir }}/addons/registry"
   31 |     state: directory
   32 |     owner: root
   33 |     group: root
   34 |     mode: "0755"
   35 | 
   36 | - name: Registry | Templates list
   37 |   set_fact:
   38 |     registry_templates:
   39 |       - { name: registry-ns, file: registry-ns.yml, type: ns }
   40 |       - { name: registry-sa, file: registry-sa.yml, type: sa }
   41 |       - { name: registry-svc, file: registry-svc.yml, type: svc }
   42 |       - { name: registry-secrets, file: registry-secrets.yml, type: secrets }
   43 |       - { name: registry-cm, file: registry-cm.yml, type: cm }
   44 |       - { name: registry-rs, file: registry-rs.yml, type: rs }
   45 | 
   46 | - name: Registry | Append ingress templates to Registry Templates list when ALB ingress enabled
   47 |   set_fact:
   48 |     registry_templates: "{{ registry_templates + [item] }}"
   49 |   with_items:
   50 |     - [{ name: registry-ing, file: registry-ing.yml, type: ing }]
   51 |   when: ingress_alb_enabled
   52 | 
   53 | - name: Registry | Create manifests
   54 |   template:
   55 |     src: "{{ item.file }}.j2"
   56 |     dest: "{{ kube_config_dir }}/addons/registry/{{ item.file }}"
   57 |     mode: "0644"
   58 |   with_items: "{{ registry_templates }}"
   59 |   register: registry_manifests
   60 |   when: inventory_hostname == groups['kube_control_plane'][0]
   61 | 
   62 | - name: Registry | Apply manifests
   63 |   kube:
   64 |     name: "{{ item.item.name }}"
   65 |     namespace: "{{ registry_namespace }}"
   66 |     kubectl: "{{ bin_dir }}/kubectl"
   67 |     resource: "{{ item.item.type }}"
   68 |     filename: "{{ kube_config_dir }}/addons/registry/{{ item.item.file }}"
   69 |     state: "latest"
   70 |   with_items: "{{ registry_manifests.results }}"
   71 |   when: inventory_hostname == groups['kube_control_plane'][0]
   72 | 
   73 | - name: Registry | Create PVC manifests
   74 |   template:
   75 |     src: "{{ item.file }}.j2"
   76 |     dest: "{{ kube_config_dir }}/addons/registry/{{ item.file }}"
   77 |     mode: "0644"
   78 |   with_items:
   79 |     - { name: registry-pvc, file: registry-pvc.yml, type: pvc }
   80 |   register: registry_manifests
   81 |   when:
   82 |     - registry_storage_class != none and registry_storage_class
   83 |     - registry_disk_size != none and registry_disk_size
   84 |     - inventory_hostname == groups['kube_control_plane'][0]
   85 | 
   86 | - name: Registry | Apply PVC manifests
   87 |   kube:
   88 |     name: "{{ item.item.name }}"
   89 |     namespace: "{{ registry_namespace }}"
   90 |     kubectl: "{{ bin_dir }}/kubectl"
   91 |     resource: "{{ item.item.type }}"
   92 |     filename: "{{ kube_config_dir }}/addons/registry/{{ item.item.file }}"
   93 |     state: "latest"
   94 |   with_items: "{{ registry_manifests.results }}"
   95 |   when:
   96 |     - registry_storage_class != none and registry_storage_class
   97 |     - registry_disk_size != none and registry_disk_size
   98 |     - inventory_hostname == groups['kube_control_plane'][0]
```

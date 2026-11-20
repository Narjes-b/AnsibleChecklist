# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-005

- Repository: `easzlab/kubeasz`
- Commit: `fcb46a47a7fcd3bbc97498ea4aefdd564e16b383`
- Family: Objective correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/clean/tasks/clean_node.yml` (reported anchor line 11)
- Object: `source_location` `fe2f8238af656083b3af1102274e9f382bb0b5508d67eb669653b5fdc40ea3f2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–123 of 123:

```text
    1 | # to clean 'kube_node' nodes
    2 | - block:
    3 |   - name: stop and disable kube_node service
    4 |     service: name={{ item }} state=stopped enabled=no
    5 |     with_items:
    6 |     - kube-lb
    7 |     - kubelet
    8 |     - kube-proxy
    9 |     ignore_errors: true
   10 | 
   11 |   - name: umount kubelet filesystems
   12 |     shell: "mount | grep '/var/lib/kubelet'| awk '{print $3}'|xargs umount || exit 0"
   13 |     ignore_errors: true
   14 | 
   15 |   - name: remove files and dirs of 'kube_node' nodes
   16 |     file: name={{ item }} state=absent
   17 |     with_items:
   18 |     - "/var/lib/kubelet/"
   19 |     - "/var/lib/kube-proxy/"
   20 |     - "/etc/systemd/system/kube-lb.service"
   21 |     - "/etc/systemd/system/kubelet.service"
   22 |     - "/etc/systemd/system/kube-proxy.service"
   23 |     - "/etc/kube-lb/"
   24 |     - "/etc/kubernetes/"
   25 |     - "/opt/kubeasz_prepare_tasks"
   26 |     - "/root/.kube/config"
   27 |     ignore_errors: true
   28 | 
   29 | # to clean container runtime and networking
   30 |   - block:
   31 |       - name: to check if container 'kubeasz' is running
   32 |         shell: 'docker ps|grep kubeasz || echo "NOT FOUND"'
   33 |         register: install_info
   34 | 
   35 |       - block:
   36 |         - name: stop and disable docker service
   37 |           service:
   38 |             name: docker
   39 |             state: stopped
   40 |             enabled: no
   41 |           ignore_errors: true
   42 |   
   43 |         # as k8s-network-plugins use host-network, '/var/run/docker/netns/default' must be umounted
   44 |         - name: umount docker filesystem-1
   45 |           mount: path=/var/run/docker/netns/default state=unmounted
   46 |   
   47 |         - name: umount docker filesystem-2
   48 |           mount: path=/var/lib/docker/overlay state=unmounted
   49 |   
   50 |         - name: umount docker filesystem-3
   51 |           shell: "echo /var/lib/docker/overlay2/*/merged|xargs umount || exit 0"
   52 |           ignore_errors: true
   53 | 
   54 |         - name: umount docker filesystem-4
   55 |           shell: "echo /var/lib/docker/containers/*/mounts/shm|xargs umount || exit 0"
   56 |           ignore_errors: true
   57 | 
   58 |         - name: umount docker filesystem-5
   59 |           shell: "echo /var/run/docker/netns/*|xargs umount || exit 0"
   60 |           ignore_errors: true
   61 | 
   62 |         - name: remove files and dirs
   63 |           file: name={{ item }} state=absent
   64 |           with_items:
   65 |           - "/var/lib/docker/"
   66 |           - "/var/lib/dockershim/"
   67 |           - "/var/run/docker/"
   68 |           - "/etc/docker/"
   69 |           - "/etc/systemd/system/docker.service"
   70 |           - "/etc/systemd/system/docker.service.requires/"
   71 |           - "/etc/systemd/system/docker.service.d/"
   72 |           - "/etc/bash_completion.d/docker"
   73 |           - "/usr/bin/docker"
   74 |         when: "'kubeasz' not in install_info.stdout"
   75 |     ignore_errors: true
   76 |     when: CONTAINER_RUNTIME == 'docker'
   77 | 
   78 |   - block:
   79 |       - name: stop and disable {{ CONTAINERD_SERVICE_NAME }}
   80 |         service:
   81 |           name: containerd
   82 |           state: stopped
   83 |           enabled: no
   84 |         ignore_errors: true
   85 | 
   86 |       - name: umount containerd filesystems
   87 |         shell: "mount | grep 'containerd/io.containerd'| awk '{print $3}'|xargs umount || exit 0"
   88 |         ignore_errors: true
   89 | 
   90 |       - name: remove files and dirs
   91 |         file: name={{ item }} state=absent
   92 |         with_items:
   93 |         - "{{ CONTAINERD_CONFIG_DIR }}"
   94 |         - "/etc/crictl.yaml"
   95 |         - "/etc/systemd/system/{{ CONTAINERD_SERVICE_NAME }}"
   96 |         - "/opt/containerd/"
   97 |         - "{{ CONTAINERD_ROOT_DIR }}"
   98 |         - "{{ CONTAINERD_STATE_DIR }}"
   99 |     ignore_errors: true
  100 |     when: CONTAINER_RUNTIME == 'containerd'
  101 | 
  102 |   - name: remove files and dirs2
  103 |     file: name={{ item }} state=absent
  104 |     with_items:
  105 |     - "/etc/cni/"
  106 |     - "/run/flannel/"
  107 |     - "/etc/calico/"
  108 |     - "/var/lib/calico/"
  109 |     - "/var/log/calico/"
  110 |     - "/etc/cilium/"
  111 |     - "/sys/fs/bpf/tc/"
  112 |     - "/var/lib/cni/"
  113 |     - "/var/lib/kube-router/"
  114 |     - "/var/run/openvswitch/"
  115 |     - "/var/run/ovn/"
  116 |     - "/etc/origin/openvswitch/"
  117 |     - "/etc/origin/ovn/"
  118 |     - "/var/log/openvswitch/"
  119 |     - "/var/log/ovn/"
  120 |     - "/var/log/kube-ovn/"
  121 |     ignore_errors: true
  122 | 
  123 |   when: "inventory_hostname in groups['kube_master'] or inventory_hostname in groups['kube_node']"
```

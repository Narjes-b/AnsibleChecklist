# Frozen source context: V007PILOT-STRUCTURE_REUSE-035

- Repository: `kubernetes-sigs/kubespray`
- Commit: `9ee6f9b27981b251d77302fd6cf631f330e0ec39`
- Family: Structure/reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/network_plugin/calico/tasks/repos.yml` (reported anchor line 1)
- Object: `source_location` `f4f74425114a2623824410ebaaa758f11a473df14c979a0f32bb6b679ba2b02b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–21 of 21:

```text
    1 | ---
    2 | - name: Calico | Add wireguard yum repo
    3 |   when:
    4 |     - calico_wireguard_enabled
    5 |   block:
    6 | 
    7 |     - name: Calico | Add wireguard yum repo
    8 |       yum_repository:
    9 |         name: copr:copr.fedorainfracloud.org:jdoss:wireguard
   10 |         file: _copr:copr.fedorainfracloud.org:jdoss:wireguard
   11 |         description: Copr repo for wireguard owned by jdoss
   12 |         baseurl: "{{ calico_wireguard_repo }}"
   13 |         gpgcheck: true
   14 |         gpgkey: https://download.copr.fedorainfracloud.org/results/jdoss/wireguard/pubkey.gpg
   15 |         skip_if_unavailable: true
   16 |         enabled: true
   17 |         repo_gpgcheck: false
   18 |       when:
   19 |         - ansible_facts['os_family'] in ['RedHat']
   20 |         - ansible_facts['distribution'] not in ['Fedora']
   21 |         - ansible_facts['distribution_major_version'] | int < 9
```

## Frozen tracked paths in the relevant role/scope

```text
roles/network_plugin/calico/files/openssl.conf
roles/network_plugin/calico/handlers/main.yml
roles/network_plugin/calico/meta/main.yml
roles/network_plugin/calico/rr/defaults/main.yml
roles/network_plugin/calico/rr/tasks/main.yml
roles/network_plugin/calico/rr/tasks/pre.yml
roles/network_plugin/calico/rr/tasks/update-node.yml
roles/network_plugin/calico/tasks/calico_apiserver_certs.yml
roles/network_plugin/calico/tasks/check.yml
roles/network_plugin/calico/tasks/install.yml
roles/network_plugin/calico/tasks/main.yml
roles/network_plugin/calico/tasks/peer_with_calico_rr.yml
roles/network_plugin/calico/tasks/peer_with_router.yml
roles/network_plugin/calico/tasks/pre.yml
roles/network_plugin/calico/tasks/repos.yml
roles/network_plugin/calico/tasks/reset.yml
roles/network_plugin/calico/tasks/typha_certs.yml
roles/network_plugin/calico/templates/calico-apiserver-ns.yml.j2
roles/network_plugin/calico/templates/calico-apiserver.yml.j2
roles/network_plugin/calico/templates/calico-config.yml.j2
roles/network_plugin/calico/templates/calico-cr.yml.j2
roles/network_plugin/calico/templates/calico-crb.yml.j2
roles/network_plugin/calico/templates/calico-ipamconfig.yml.j2
roles/network_plugin/calico/templates/calico-node-sa.yml.j2
roles/network_plugin/calico/templates/calico-node.yml.j2
roles/network_plugin/calico/templates/calico-typha.yml.j2
roles/network_plugin/calico/templates/calicoctl.etcd.sh.j2
roles/network_plugin/calico/templates/calicoctl.kdd.sh.j2
roles/network_plugin/calico/templates/kubernetes-services-endpoint.yml.j2
roles/network_plugin/calico/templates/make-ssl-calico.sh.j2
roles/network_plugin/calico/vars/amazon.yml
roles/network_plugin/calico/vars/centos-9.yml
roles/network_plugin/calico/vars/debian.yml
roles/network_plugin/calico/vars/fedora.yml
roles/network_plugin/calico/vars/opensuse.yml
roles/network_plugin/calico/vars/redhat-9.yml
roles/network_plugin/calico/vars/redhat.yml
roles/network_plugin/calico/vars/rocky-9.yml
roles/network_plugin/calico_defaults/defaults/main.yml
roles/network_plugin/cilium/defaults/main.yml
roles/network_plugin/cilium/tasks/apply.yml
roles/network_plugin/cilium/tasks/check.yml
roles/network_plugin/cilium/tasks/install.yml
roles/network_plugin/cilium/tasks/main.yml
roles/network_plugin/cilium/tasks/reset.yml
roles/network_plugin/cilium/tasks/reset_iface.yml
roles/network_plugin/cilium/templates/cilium/cilium-bgp-advertisement.yml.j2
roles/network_plugin/cilium/templates/cilium/cilium-bgp-cluster-config.yml.j2
roles/network_plugin/cilium/templates/cilium/cilium-bgp-node-config-override.yml.j2
roles/network_plugin/cilium/templates/cilium/cilium-bgp-peer-config.yml.j2
roles/network_plugin/cilium/templates/cilium/cilium-bgp-peering-policy.yml.j2
roles/network_plugin/cilium/templates/cilium/cilium-loadbalancer-ip-pool.yml.j2
roles/network_plugin/cilium/templates/values.yaml.j2
roles/network_plugin/cni/defaults/main.yml
roles/network_plugin/cni/tasks/main.yml
roles/network_plugin/custom_cni/defaults/main.yml
roles/network_plugin/custom_cni/meta/main.yml
roles/network_plugin/custom_cni/tasks/main.yml
roles/network_plugin/flannel/defaults/main.yml
roles/network_plugin/flannel/meta/main.yml
roles/network_plugin/flannel/tasks/main.yml
roles/network_plugin/flannel/tasks/reset.yml
roles/network_plugin/flannel/templates/cni-flannel-rbac.yml.j2
roles/network_plugin/flannel/templates/cni-flannel.yml.j2
roles/network_plugin/kube-ovn/defaults/main.yml
roles/network_plugin/kube-ovn/tasks/main.yml
roles/network_plugin/kube-ovn/templates/cni-kube-ovn-crd.yml.j2
roles/network_plugin/kube-ovn/templates/cni-kube-ovn.yml.j2
roles/network_plugin/kube-ovn/templates/cni-ovn.yml.j2
roles/network_plugin/kube-router/defaults/main.yml
roles/network_plugin/kube-router/handlers/main.yml
roles/network_plugin/kube-router/meta/main.yml
roles/network_plugin/kube-router/tasks/annotate.yml
roles/network_plugin/kube-router/tasks/main.yml
roles/network_plugin/kube-router/tasks/reset.yml
roles/network_plugin/kube-router/templates/cni-conf.json.j2
roles/network_plugin/kube-router/templates/kube-router.yml.j2
roles/network_plugin/kube-router/templates/kubeconfig.yml.j2
roles/network_plugin/macvlan/defaults/main.yml
roles/network_plugin/macvlan/files/ifdown-local
roles/network_plugin/macvlan/files/ifdown-macvlan
roles/network_plugin/macvlan/files/ifup-local
roles/network_plugin/macvlan/files/ifup-macvlan
roles/network_plugin/macvlan/handlers/main.yml
roles/network_plugin/macvlan/meta/main.yml
roles/network_plugin/macvlan/tasks/main.yml
roles/network_plugin/macvlan/templates/10-macvlan.conf.j2
roles/network_plugin/macvlan/templates/99-loopback.conf.j2
roles/network_plugin/macvlan/templates/centos-network-macvlan.cfg.j2
roles/network_plugin/macvlan/templates/centos-postdown-macvlan.cfg.j2
roles/network_plugin/macvlan/templates/centos-postup-macvlan.cfg.j2
roles/network_plugin/macvlan/templates/centos-routes-macvlan.cfg.j2
roles/network_plugin/macvlan/templates/coreos-device-macvlan.cfg.j2
roles/network_plugin/macvlan/templates/coreos-interface-macvlan.cfg.j2
roles/network_plugin/macvlan/templates/coreos-network-macvlan.cfg.j2
roles/network_plugin/macvlan/templates/coreos-service-nat_ouside.j2
roles/network_plugin/macvlan/templates/debian-network-macvlan.cfg.j2
roles/network_plugin/multus/defaults/main.yml
roles/network_plugin/multus/files/multus-clusterrole.yml
roles/network_plugin/multus/files/multus-clusterrolebinding.yml
roles/network_plugin/multus/files/multus-crd.yml
roles/network_plugin/multus/files/multus-serviceaccount.yml
roles/network_plugin/multus/meta/main.yml
roles/network_plugin/multus/tasks/main.yml
roles/network_plugin/multus/templates/multus-daemonset.yml.j2
roles/network_plugin/ovn4nfv/tasks/main.yml
roles/network_plugin/tasks/main.yml
```

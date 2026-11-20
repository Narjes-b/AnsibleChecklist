# Frozen source context: V007PILOT-STYLE_POLICY-045

- Repository: `kubernetes-sigs/kubespray`
- Commit: `9ee6f9b27981b251d77302fd6cf631f330e0ec39`
- Family: Style/policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/network_plugin/cilium/tasks/check.yml` (reported anchor line 57)
- Object: `task` `9d932887d1c3d1e44aed768a6d47fa692161c011b5cb6eb5e8d4e41b5283f074`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–85 of 85:

```text
    1 | ---
    2 | - name: Cilium | Check Cilium encryption `cilium_ipsec_key` for ipsec
    3 |   assert:
    4 |     that:
    5 |       - "cilium_ipsec_key is defined"
    6 |     msg: "cilium_ipsec_key should be defined to enable encryption using ipsec"
    7 |   when:
    8 |     - cilium_encryption_enabled
    9 |     - cilium_encryption_type == "ipsec"
   10 |     - cilium_tunnel_mode in ['vxlan']
   11 | 
   12 | # TODO: Clean this task up when we drop backward compatibility support for `cilium_ipsec_enabled`
   13 | - name: Stop if `cilium_ipsec_enabled` is defined and `cilium_encryption_type` is not `ipsec`
   14 |   assert:
   15 |     that: cilium_encryption_type == 'ipsec'
   16 |     msg: >
   17 |       It is not possible to use `cilium_ipsec_enabled` when `cilium_encryption_type` is set to {{ cilium_encryption_type }}.
   18 |   when:
   19 |     - cilium_ipsec_enabled is defined
   20 |     - cilium_ipsec_enabled
   21 |     - kube_network_plugin == 'cilium' or cilium_deploy_additionally
   22 | 
   23 | - name: Stop if kernel version is too low for Cilium Wireguard encryption
   24 |   assert:
   25 |     that: ansible_facts['kernel'].split('-')[0] is version('5.6.0', '>=')
   26 |   when:
   27 |     - kube_network_plugin == 'cilium' or cilium_deploy_additionally
   28 |     - cilium_encryption_enabled
   29 |     - cilium_encryption_type == "wireguard"
   30 |     - not ignore_assert_errors
   31 | 
   32 | - name: Stop if bad Cilium identity allocation mode
   33 |   assert:
   34 |     that: cilium_identity_allocation_mode in ['crd', 'kvstore']
   35 |     msg: "cilium_identity_allocation_mode must be either 'crd' or 'kvstore'"
   36 | 
   37 | - name: Stop if bad Cilium Cluster ID
   38 |   assert:
   39 |     that:
   40 |       - cilium_cluster_id <= 255
   41 |       - cilium_cluster_id >= 0
   42 |     msg: "'cilium_cluster_id' must be between 1 and 255"
   43 |   when: cilium_cluster_id is defined
   44 | 
   45 | - name: Stop if bad encryption type
   46 |   assert:
   47 |     that: cilium_encryption_type in ['ipsec', 'wireguard']
   48 |     msg: "cilium_encryption_type must be either 'ipsec' or 'wireguard'"
   49 |   when: cilium_encryption_enabled
   50 | 
   51 | - name: Stop if cilium_version is < {{ cilium_min_version_required }}
   52 |   assert:
   53 |     that: cilium_version is version(cilium_min_version_required, '>=')
   54 |     msg: "cilium_version is too low. Minimum version {{ cilium_min_version_required }}"
   55 | 
   56 | # TODO: Clean this task up when we drop backward compatibility support for `cilium_ipsec_enabled`
   57 | - name: Set `cilium_encryption_type` to "ipsec" and  if `cilium_ipsec_enabled` is true
   58 |   set_fact:
   59 |     cilium_encryption_type: ipsec
   60 |     cilium_encryption_enabled: true
   61 |   when:
   62 |     - cilium_ipsec_enabled is defined
   63 |     - cilium_ipsec_enabled
   64 | 
   65 | - name: Stop if cilium_hubble_event_buffer_capacity is not a power of 2 minus 1 and is not between 1 and 65535
   66 |   assert:
   67 |     that: "cilium_hubble_event_buffer_capacity in [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535]"
   68 |     msg: "Error: cilium_hubble_event_buffer_capacity:{{ cilium_hubble_event_buffer_capacity }} is not a power of 2 minus 1 and it should be between 1 and 65535."
   69 |   when: cilium_hubble_event_buffer_capacity is defined
   70 | 
   71 | # Cilium < 1.20 only supports Gateway API v1.4.1; v1.5+ standard channel drops
   72 | # TLSRoute v1alpha2 (served=false) which makes cilium-operator CrashLoopBackOff.
   73 | # Fix is in Cilium 1.20+ (cilium/cilium#45251) and will not be backported.
   74 | - name: Stop if cilium_gateway_api_enabled is incompatible with the Gateway API CRD bundle
   75 |   assert:
   76 |     that:
   77 |       - gateway_api_version is version('1.5.0', '<') or gateway_api_channel != 'standard'
   78 |     msg: |
   79 |       Cilium < 1.20 only supports Gateway API v1.4.1, see
   80 |       https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/.
   81 |       Pin gateway_api_version: '1.4.1', or set gateway_api_channel: 'experimental'.
   82 |   when:
   83 |     - cilium_gateway_api_enabled
   84 |     - gateway_api_enabled
   85 |     - cilium_version is version('1.20.0', '<')
```

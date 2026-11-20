# Frozen source context: V007PILOT-STYLE_POLICY-005

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: Style/policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `automation/roles/cloud_resources/tasks/hetzner.yml` (reported anchor line 103)
- Object: `task` `36085f3d051b6a69992a2c143810d65ff08011171565a151fd193bd4de9d15f5`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 68–138 of 733:

```text
   68 |         label: "{{ item.name }}"
   69 |       when:
   70 |         - (ssh_key_name | length < 1 or ssh_key_name == (tmp_ssh_key_name | default('')))
   71 |         - (ssh_public_keys is not defined or ssh_public_keys | length < 1)
   72 |   when: state == 'present'
   73 | 
   74 | # Create (if state is present)
   75 | - block:
   76 |     - name: "Hetzner Cloud: Gather information about network zones"
   77 |       ansible.builtin.uri:
   78 |         url: "https://api.hetzner.cloud/v1/locations"
   79 |         method: GET
   80 |         headers:
   81 |           Authorization: [REDACTED_LITERAL]
   82 |         return_content: true
   83 |       register: hetzner_locations_response
   84 |       failed_when: hetzner_locations_response.status != 200
   85 | 
   86 |     - name: "Hetzner Cloud: Extract network zone for server_location"
   87 |       ansible.builtin.set_fact:
   88 |         target_network_zone: "{{ item.network_zone }}"
   89 |       loop: "{{ hetzner_locations_response.json.locations }}"
   90 |       loop_control:
   91 |         label: "network_zone: {{ item.network_zone }}"
   92 |       when: item.name == server_location
   93 | 
   94 |     - name: "Hetzner Cloud: Gather information about networks"
   95 |       hetzner.hcloud.network_info:
   96 |         api_token: "{{ lookup('ansible.builtin.env', 'HCLOUD_API_TOKEN') }}"
   97 |       register: network_info
   98 |       until: network_info is success
   99 |       delay: 5
  100 |       retries: 3
  101 | 
  102 |     # if server_network is specified
  103 |     - name: "Hetzner Cloud: Check if network '{{ server_network | default('') }}' exists for given location"
  104 |       ansible.builtin.fail:
  105 |         msg: "No network with name '{{ server_network }}' in location '{{ target_network_zone }}'"
  106 |       when:
  107 |         - server_network | length > 0
  108 |         - not (network_info.hcloud_network_info
  109 |           | selectattr("name", "equalto", server_network)
  110 |           | selectattr("subnetworks", "defined")
  111 |           | map(attribute='subnetworks')
  112 |           | flatten
  113 |           | selectattr("network_zone", "equalto", target_network_zone)
  114 |           | list | length > 0)
  115 | 
  116 |     - name: "Hetzner Cloud: Extract ip_range for network '{{ server_network | default('') }}'"
  117 |       ansible.builtin.set_fact:
  118 |         server_network_ip_range: "{{ item.ip_range }}"
  119 |       loop: "{{ network_info.hcloud_network_info }}"
  120 |       when:
  121 |         - server_network | length > 0
  122 |         - item.name == server_network
  123 |       loop_control:
  124 |         label: "{{ item.ip_range }}"
  125 | 
  126 |     # if server_network is not specified, create a network and subnet
  127 |     - block:
  128 |         - name: "Hetzner Cloud: Create a postgres cluster network"
  129 |           hetzner.hcloud.network:
  130 |             api_token: "{{ lookup('ansible.builtin.env', 'HCLOUD_API_TOKEN') }}"
  131 |             name: "{{ hcloud_network_name | default('postgres-cluster-network-' + target_network_zone) }}"
  132 |             ip_range: "{{ hcloud_network_ip_range | default('10.0.0.0/16') }}"
  133 |             state: present
  134 | 
  135 |         - name: "Hetzner Cloud: Create a subnetwork in postgres cluster network"
  136 |           hetzner.hcloud.subnetwork:
  137 |             api_token: "{{ lookup('ansible.builtin.env', 'HCLOUD_API_TOKEN') }}"
  138 |             network: "{{ hcloud_network_name | default('postgres-cluster-network-' + target_network_zone) }}"
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

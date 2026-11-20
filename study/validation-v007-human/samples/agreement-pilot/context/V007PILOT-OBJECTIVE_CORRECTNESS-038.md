# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-038

- Repository: `dryvist/ansible-proxmox-apps`
- Commit: `b179574eb875a6b7be09df83d001f623a68a2681`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `playbooks/validate-pipeline/netflow.yml` (reported anchor line 32)
- Object: `source_location` `c18eafcce85f42261946af4d60316709db832cbde83bb73c53b06acf299275ba`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–142 of 142:

```text
    1 | ---
    2 | - name: Validate NetFlow Port
    3 |   hosts: cribl_stream_group[0]
    4 |   become: true
    5 |   gather_facts: true
    6 |   tags:
    7 |     - netflow
    8 |     - validation
    9 | 
   10 |   vars:
   11 |     constants: "{{ hostvars['localhost']['tofu_data']['constants'] }}"
   12 |     # Splunk mgmt REST API — the one shared splunk_mgmt_base_url
   13 |     # (inventory/group_vars/all.yml), never reconstructed here.
   14 |     splunk_user: admin
   15 |     # SPLUNK_PASSWORD must be set via Doppler
   16 |     splunk_password: "{{ lookup('env', 'SPLUNK_PASSWORD') }}"
   17 | 
   18 |   tasks:
   19 |     - name: Skip E2E data injection in check mode
   20 |       ansible.builtin.meta: end_play
   21 |       when: ansible_check_mode
   22 | 
   23 |     - name: Verify SPLUNK_PASSWORD is set
   24 |       ansible.builtin.assert:
   25 |         that:
   26 |           - splunk_password | length > 0
   27 |         fail_msg: >-
   28 |           SPLUNK_PASSWORD environment variable must be set.
   29 |           Run with doppler run --
   30 |         quiet: true
   31 | 
   32 |     - name: Check netflow UDP port is listening
   33 |       ansible.builtin.shell:
   34 |         cmd: |
   35 |           set -o pipefail
   36 |           ss -ulnp | grep ':{{ constants.netflow_ports.unifi }}'
   37 |         executable: /bin/bash
   38 |       register: netflow_port_check
   39 |       failed_when: netflow_port_check.rc != 0
   40 |       changed_when: false
   41 | 
   42 |     - name: Generate unique sentinel port for NetFlow test correlation
   43 |       ansible.builtin.set_fact:
   44 |         netflow_sentinel_port: "{{ 40000 + (ansible_date_time.epoch | int % 25000) }}"
   45 | 
   46 |     - name: Send minimal NetFlow v5 test packet
   47 |       ansible.builtin.shell:
   48 |         cmd: |
   49 |           python3 -c "
   50 |           import socket, struct, time
   51 | 
   52 |           # NetFlow v5 header: version=5, count=1, uptime=0
   53 |           # epoch, nanosec, flow_seq=1, engine=0, sampling=0
   54 |           epoch = int(time.time())
   55 |           header = struct.pack('!HHIIIIBBH',
   56 |               5,       # version
   57 |               1,       # count (1 flow record)
   58 |               0,       # sys_uptime_ms
   59 |               epoch,   # unix_secs
   60 |               0,       # unix_nsecs
   61 |               1,       # flow_sequence
   62 |               0,       # engine_type + engine_id (packed as one byte each below)
   63 |               0,       # engine_id
   64 |               0        # sampling_interval
   65 |           )
   66 | 
   67 |           # NetFlow v5 flow record (48 bytes): minimal valid record
   68 |           # Uses sentinel src_port for test correlation in Splunk
   69 |           record = struct.pack('!IIIHHIIIIHHBBBBHHBBH',
   70 |               0x0A000001,  # src_addr 10.0.0.1
   71 |               0x0A000002,  # dst_addr 10.0.0.2
   72 |               0,           # next_hop
   73 |               0,           # snmp_input
   74 |               0,           # snmp_output
   75 |               1,           # packets
   76 |               64,          # octets
   77 |               0,           # first_switched
   78 |               0,           # last_switched
   79 |               {{ netflow_sentinel_port }},  # src_port (sentinel)
   80 |               80,          # dst_port
   81 |               0,           # pad1
   82 |               6,           # tcp_flags
   83 |               6,           # protocol (TCP)
   84 |               0,           # tos
   85 |               0,           # src_as
   86 |               0,           # dst_as
   87 |               0,           # src_mask
   88 |               0,           # dst_mask
   89 |               0            # pad2
   90 |           )
   91 | 
   92 |           sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   93 |           sock.sendto(header + record, ('127.0.0.1', {{ constants.netflow_ports.unifi }}))
   94 |           sock.close()
   95 |           print('NetFlow v5 test packet sent with sentinel src_port={{ netflow_sentinel_port }}')
   96 |           "
   97 |         executable: /bin/bash
   98 |       changed_when: false
   99 | 
  100 |     - name: Wait for NetFlow event to propagate through pipeline
  101 |       ansible.builtin.pause:
  102 |         seconds: 10
  103 |         prompt: >-
  104 |           Waiting for NetFlow test event to propagate through Cribl Stream to Splunk...
  105 | 
  106 |     # Pipeline latency assertion: poll up to 120 seconds (retries: 12, delay: 10)
  107 |     # The loop fails the play if the event does not appear within 120 seconds.
  108 |     - name: Query Splunk for NetFlow event in netflow index (pipeline latency assertion, 120s timeout)
  109 |       ansible.builtin.uri:
  110 |         url: "{{ splunk_mgmt_base_url }}/services/search/jobs"
  111 |         method: POST
  112 |         user: "{{ splunk_user }}"
  113 |         password: "{{ splunk_password }}"
  114 |         force_basic_auth: true
  115 |         validate_certs: false
  116 |         body_format: form-urlencoded
  117 |         body:
  118 |           # Cribl's netflow input emits camelCase srcPort (preserved by
  119 |           # Splunk's JSON auto-extraction) — src_port never matches.
  120 |           search: 'search index=netflow earliest=-5m srcPort={{ netflow_sentinel_port }} | head 1'
  121 |           output_mode: json
  122 |           exec_mode: oneshot
  123 |       register: splunk_netflow_result
  124 |       retries: 12
  125 |       delay: 10
  126 |       until: >-
  127 |         splunk_netflow_result.status == 200 and
  128 |         (splunk_netflow_result.json.results | default([]) | length > 0)
  129 |       failed_when: >-
  130 |         splunk_netflow_result.status != 200 or
  131 |         (splunk_netflow_result.json.results | default([]) | length == 0)
  132 | 
  133 |     - name: Display NetFlow validation result
  134 |       ansible.builtin.debug:
  135 |         msg: |
  136 |           === NETFLOW VALIDATION PASSED =[REDACTED_LITERAL]
  137 |           NetFlow port {{ constants.netflow_ports.unifi }} UDP is listening
  138 |           {{ netflow_port_check.stdout }}
  139 |           NetFlow v5 test packet sent and event found in Splunk
  140 |           Splunk host: {{ splunk_mgmt_base_url }}
  141 |           Search results (index=netflow): {{ splunk_netflow_result.json.results | length }} event(s) found
  142 |           Full path verified: NetFlow source -> Cribl Stream LXC -> Splunk HEC -> Splunk Index (netflow)
```

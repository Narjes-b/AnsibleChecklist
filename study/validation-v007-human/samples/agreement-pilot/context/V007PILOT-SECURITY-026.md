# Frozen source context: V007PILOT-SECURITY-026

- Repository: `CentOS-PaaS-SIG/linchpin`
- Commit: `0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `linchpin/provision/roles/aws/tasks/teardown_aws_ec2_vpc_nat_gateway.yml` (reported anchor line 4)
- Object: `task` `29f929922d6a71e2455046d82bd6d5d1577dd662ff22de9124bd0af7fd79d927`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–47 of 47:

```text
    1 | - name: "Get AWS VPC NAT Gateway ID"
    2 |   block:
    3 |   - name: "set ec2_vpc_nat_gateway facts"
    4 |     ec2_vpc_nat_gateway_facts:
    5 |       aws_access_key: "{{ auth_var['aws_access_key_id'] | default(omit) }}"
    6 |       aws_secret_key: "{{  auth_var['aws_secret_access_key'] | default(omit) }}"
    7 |       region: "{{ res_def['region'] }}"
    8 |       security_token: "{{ res_def['security_token'] | default(omit) }}"
    9 |       ec2_url: "{{ res_def['ec2_url'] | default(omit) }}"
   10 |       profile: "{{ res_def['profile'] | default(omit) }}"
   11 |       debug_botocore_endpoint_logs: "{{ debug_mode | default(omit) }}"
   12 |       validate_certs: false
   13 |       filters:
   14 |         "tag:Name": "{{ res_def['name'] }}"
   15 |     register: ngws_facts
   16 | 
   17 |   - name: "set nat_gateway ids"
   18 |     set_fact:
   19 |       nat_gateway_ids: "{{ ngws_facts.netgateways|map(attribute='id')|list }}"
   20 |     when: ngws_facts.netgateways is defined and ngws_facts | length > 0
   21 | 
   22 | 
   23 | - name: "Teardown AWS VPC NAT Gateways"
   24 |   ec2_vpc_nat_gateway:
   25 |     state: absent
   26 |     aws_access_key: "{{ auth_var['aws_access_key_id'] | default(omit) }}"
   27 |     aws_secret_key: "{{  auth_var['aws_secret_access_key'] | default(omit) }}"
   28 |     region: "{{ res_def['region'] }}"
   29 |     security_token: "{{ res_def['security_token'] | default(omit) }}"
   30 |     ec2_url: "{{ res_def['ec2_url'] | default(omit) }}"
   31 |     profile: "{{ res_def['profile'] | default(omit) }}"
   32 |     debug_botocore_endpoint_logs: "{{ debug_mode | default(omit) }}"
   33 |     validate_certs: false
   34 |     client_token: "{{ res_def['client_token'] | default(omit) }}"
   35 |     wait_timeout: "{{ res_def['wait_timeout'] | default(omit) }}"
   36 |     wait: "{{ res_def['wait'] | default(omit) }}"
   37 |     eip_address: "{{ res_def['eip_address'] | default(omit) }}"
   38 |     nat_gateway_id: "{{ nat_gateway_id }}"
   39 |     release_eip: "{{ res_def['release_eip'] | default(true) }}"
   40 |   register: res_def_output
   41 |   when: nat_gateway_id is defined
   42 | 
   43 | - name: "Append outputitem to topology_outputs"
   44 |   set_fact:
   45 |     topology_outputs_aws_net: "{{ topology_outputs_aws_net +
   46 |                                   [res_def_output] }}"
   47 |   when: res_def_output['changed']
```

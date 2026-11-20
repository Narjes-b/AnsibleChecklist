# Frozen source context: V007PILOT2-STRUCTURE_REUSE-005

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: structure_reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/_aws_delete_all.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/_aws_delete_all.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–157 of 157:

```text
    1 | ---
    2 | #===============================================================================
    3 | #  Gather facts from AWS to use for deletion
    4 | #===============================================================================
    5 | - amazon.aws.ec2_vpc_net_info:
    6 |     region: "{{ region }}"
    7 |     filters:
    8 |       "tag:Name": "{{ openshift_cluster_name }}-{{ workshop_prefix }}-vpc"
    9 |   register: ec2_vpc
   10 | 
   11 | - name: debug vpc object
   12 |   debug:
   13 |     msg: "{{ ec2_vpc }}"
   14 | 
   15 | - amazon.aws.ec2_vpc_subnet_info:
   16 |     region: "{{ region }}"
   17 |     filters:
   18 |       vpc-id: "{{ ec2_vpc.vpcs.0.id }}"
   19 |   register: ec2_subnet
   20 | 
   21 | - name: debug subnets object
   22 |   debug:
   23 |     msg: "{{ ec2_subnet }}"
   24 | 
   25 | - name: Get rhel instance info
   26 |   community.aws.ec2_instance_info:
   27 |     region: "{{ region }}"
   28 |     filters:
   29 |       "tag:ServiceName": "{{ openshift_cluster_name }}-{{ workshop_prefix}}"
   30 |       instance-state-name: [ "starting", "running" ]
   31 |   register: ec2_rhel
   32 | 
   33 | - name: debug rhel instance hosts
   34 |   debug:
   35 |     msg: "{{ ec2_rhel }}"
   36 | 
   37 | #===============================================================================
   38 | #  De-Provisioning
   39 | #===============================================================================
   40 | 
   41 | - name: set RHEL AMI to use
   42 |   set_fact:
   43 |     rhel_ami: "{{ regions[region][rhel_ver].ami }}"
   44 |   when: not beta|bool
   45 | 
   46 | - name: set RHEL AMI to use (beta)
   47 |   set_fact:
   48 |     rhel_ami: "{{ regions[region][rhel_ver].beta.ami }}"
   49 |   when: beta|bool
   50 | 
   51 | - name: RHEL AMI
   52 |   debug:
   53 |     msg: "Using AWS {{ region }} {{ rhel_ver }} AMI: {{ rhel_ami }}"
   54 | 
   55 | - name: Delete DNS records for RHEL
   56 |   route53:
   57 |     zone: "{{ openshift_cluster_base_domain }}"
   58 |     type: "CNAME"
   59 |     ttl: "300"
   60 |     record: "{{ i.tags.Route53 }}"
   61 |     value: "{{ i.public_dns_name }}"
   62 |     state: "{{ aws_state }}"
   63 |   loop: "{{ ec2_rhel.instances }}"
   64 |   loop_control:
   65 |     loop_var: i
   66 | 
   67 | - name: Delete RHEL instances
   68 |   ec2:
   69 |     assign_public_ip: yes
   70 |     image: "{{ rhel_ami }}"
   71 |     region: "{{ region }}"
   72 |     vpc_subnet_id: "{{ ec2_subnet.subnets.0.subnet_id }}"
   73 |     wait: true
   74 |     state: "{{ aws_state }}"
   75 |     instance_ids: "{{ ec2.instance_id }}"
   76 |   loop: "{{ ec2_rhel.instances }}"
   77 |   loop_control:
   78 |     loop_var: ec2
   79 |   register: ec2_rhel
   80 | 
   81 | - debug:
   82 |     var: ec2_rhel
   83 | 
   84 | - name: Delete RHEL security group
   85 |   ec2_group:
   86 |     name: "{{ openshift_cluster_name }}-{{ workshop_prefix }}-sg"
   87 |     description: "SG for RHEL hosts"
   88 |     region: "{{ region }}"
   89 |     vpc_id: "{{ ec2_vpc.vpcs.0.id }}"
   90 |     state: "{{ aws_state }}"
   91 |   register: result
   92 | 
   93 | - debug:
   94 |     var: result
   95 | 
   96 | - name: Delete VPC internet gateway
   97 |   ec2_vpc_igw:
   98 |     region: "{{ region }}"
   99 |     vpc_id: "{{ ec2_vpc.vpcs.0.id }}"
  100 |     state: "{{ aws_state }}"
  101 |     tags:
  102 |       Name: "{{ openshift_cluster_name }}-{{ workshop_prefix }}-igw"
  103 |       username: "{{ local_user }}"
  104 |       workshop: "{{ workshop_name }}"
  105 |       workshop_prefix: "{{ workshop_prefix }}"
  106 |   register: ec2_igw
  107 | 
  108 | - debug:
  109 |     var: result
  110 | 
  111 | - name: Delete VPC route table
  112 |   ec2_vpc_route_table:
  113 |     region: "{{ region }}"
  114 |     vpc_id: "{{ ec2_vpc.vpcs.0.id }}"
  115 |     subnets: "{{ ec2_subnet.subnets }}"
  116 |     lookup: tag
  117 |     tags:
  118 |       Name: "{{ openshift_cluster_name }}-{{ workshop_prefix }}-route"
  119 |     state: "{{ aws_state }}"
  120 |   register: ec2_route
  121 | 
  122 | - debug:
  123 |     var: ec2_route
  124 | 
  125 | - name: Delete public subnet
  126 |   ec2_vpc_subnet:
  127 |     cidr: "10.0.2.0/24"
  128 |     region: "{{ region }}"
  129 |     vpc_id: "{{ ec2_vpc.vpcs.0.id }}"
  130 |     tags:
  131 |       Name: "{{ openshift_cluster_name }}-{{ workshop_prefix }}-subnet"
  132 |       username: "{{ local_user }}"
  133 |       workshop: "{{ workshop_name }}"
  134 |       workshop_prefix: "{{ workshop_prefix }}"
  135 |     wait: yes
  136 |     state: "{{ aws_state }}"
  137 |   register: ec2_subnet
  138 |   ignore_errors: yes
  139 | 
  140 | - debug:
  141 |     var: ec2_subnet
  142 | 
  143 | - name: Delete VPC
  144 |   ec2_vpc_net:
  145 |     name: "{{ openshift_cluster_name }}-{{ workshop_prefix }}-vpc"
  146 |     region: "{{ region }}"
  147 |     cidr_block: "10.0.0.0/16"
  148 |     state: "{{ aws_state }}"
  149 |   register: temp_ec2_vpc
  150 | 
  151 | - name: Delete EC2 keypair
  152 |   ec2_key:
  153 |     name: "{{ openshift_cluster_name }}-{{ workshop_prefix }}-key"
  154 |     region: "{{ region }}"
  155 |     state: "{{ aws_state }}"
  156 |   register: ec2_key
  157 | ...
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `openshift4_aws/roles/deploy_ansible_automation_workshop`; 20 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

openshift4_aws/roles/deploy_ansible_automation_workshop/README.md
openshift4_aws/roles/deploy_ansible_automation_workshop/defaults/main.yml
openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/_aws_create_base_infra.yml
openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/_aws_create_instance.yml
openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/_aws_delete_all.yml
openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/cg.yml
openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/main.yml
openshift4_aws/roles/deploy_ansible_automation_workshop/tasks/usertoken.yml
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/codeready-workspaces-rolebinding.yml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/ec2.ini.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/edge-rolebinding.yml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/edge-serviceaccount.yml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/expose-registry.yml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/hosts.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/sshkey-user.yaml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/sshkey.yaml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/tower-cg-pod-manager.yml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/tower-cg-rolebinding.yml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/templates/tower-rolebinding.yml.j2
openshift4_aws/roles/deploy_ansible_automation_workshop/vars/main.yml
```

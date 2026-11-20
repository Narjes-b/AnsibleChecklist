# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-021

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: Objective correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `rhel_edge_aws/roles/aws.remove/tasks/main.yml` (reported anchor line 253)
- Object: `task` `5f1c816102d42a671a43103fc3f534fe486f5531f0bf8a184598ed490a1d57c0`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–349 of 349:

```text
    1 | ---
    2 | # tasks file for roles/aws.remove
    3 | 
    4 | - name: RHEL AMI
    5 |   debug:
    6 |     msg: "Using AWS {{ region }} {{ rhel_ver }} AMI: {{ regions[region][rhel_ver].ami }}"
    7 | 
    8 | - name: Windows AMI
    9 |   debug:
   10 |     msg: "Using AWS {{ region }} {{ win_ver }} AMI: {{ regions[region][win_ver].ami }}"
   11 | 
   12 | - debug:
   13 |     var: tower_instance_type
   14 | 
   15 | - debug:
   16 |     var: rhel_instance_type
   17 | 
   18 | - debug:
   19 |     var: win_instance_type
   20 | 
   21 | #===============================================================================
   22 | #  Search and record IDs
   23 | #===============================================================================
   24 | - name: Initialize an empty list for our strings
   25 |   set_fact:
   26 |     route_id: ""
   27 |     subnet_id: ""
   28 |     vpc_id: ""
   29 |     admin_rhel_instance_ids: []
   30 |     tower_rhel_instance_ids: []
   31 |     rhel_instance_ids: []
   32 |     rhel_group_id: ""
   33 |     win_instance_ids: []
   34 |     win_group_id: ""
   35 | 
   36 | - name: lookup running RHEL admin instances
   37 |   ec2_instance_info:
   38 |     region: "{{ region }}"
   39 |     filters:
   40 |       tag:rhel_admin: "{{ workshop_abbrev }}-{{ workshop_prefix }}"
   41 |   register: ec2_rhel_admin
   42 | 
   43 | - name: lookup running RHEL instances
   44 |   ec2_instance_info:
   45 |     region: "{{ region }}"
   46 |     filters:
   47 |       tag:rhel: "{{ workshop_abbrev }}-{{ workshop_prefix }}"
   48 |   register: ec2_rhel
   49 | 
   50 | - name: lookup running RHEL Tower instances
   51 |   ec2_instance_info:
   52 |     region: "{{ region }}"
   53 |     filters:
   54 |       tag:tower_rhel: "{{ workshop_abbrev }}-{{ workshop_prefix }}"
   55 |   register: ec2_tower_rhel
   56 | 
   57 | - debug:
   58 |     var: ec2_rhel
   59 | 
   60 | - debug:
   61 |     var: ec2_tower_rhel
   62 | 
   63 | - name: Append RHEL admin instances to list
   64 |   set_fact:
   65 |     admin_rhel_instance_ids: "{{ admin_rhel_instance_ids }} + [ '{{ item.instance_id }}' ]"
   66 |   with_items: "{{ ec2_rhel_admin.instances }}"
   67 | 
   68 | - name: Append RHEL instances to list
   69 |   set_fact:
   70 |     rhel_instance_ids: "{{ rhel_instance_ids }} + [ '{{ item.instance_id }}' ]"
   71 |   with_items: "{{ ec2_rhel.instances }}"
   72 | 
   73 | - name: Append RHEL Tower instances to list
   74 |   set_fact:
   75 |     tower_rhel_instance_ids: "{{ tower_rhel_instance_ids }} + [ '{{ item.instance_id }}' ]"
   76 |   with_items: "{{ ec2_tower_rhel.instances }}"
   77 | 
   78 | - name: lookup running Windows instances
   79 |   ec2_instance_info:
   80 |     region: "{{ region }}"
   81 |     filters:
   82 |       tag:win: "{{ workshop_abbrev }}-{{ workshop_prefix }}"
   83 |   register: ec2_win
   84 | 
   85 | - name: Append Windows instances to list`
   86 |   set_fact:
   87 |     win_instance_ids: "{{ win_instance_ids }} + [ '{{ item.instance_id }}' ]"
   88 |   with_items: "{{ ec2_win.instances }}"
   89 | 
   90 | - name: lookup running windows security groups
   91 |   ec2_group_info:
   92 |     region: "{{ region }}"
   93 |     filters:
   94 |       tag:win: "{{ workshop_abbrev }}-{{ workshop_prefix }}"
   95 |   register: ec2_win_grp
   96 | 
   97 | - name: Record Windows security group ID
   98 |   set_fact:
   99 |     win_group_id: "{{ ec2_win_grp.security_groups[0].group_id }}"
  100 |   when: ec2_win_grp.security_groups|length > 0
  101 | 
  102 | - name: lookup running rhel security groups
  103 |   ec2_group_info:
  104 |     region: "{{ region }}"
  105 |     filters:
  106 |       tag:rhel: "{{ workshop_abbrev }}-{{ workshop_prefix }}"
  107 |   register: ec2_rhel_grp
  108 | 
  109 | - name: Record RHEL security group ID
  110 |   set_fact:
  111 |     rhel_group_id: "{{ ec2_rhel_grp.security_groups[0].group_id }}"
  112 |   when: ec2_rhel_grp.security_groups|length > 0
  113 | 
  114 | - name: lookup running subnets
  115 |   ec2_vpc_subnet_info:
  116 |     region: "{{ region }}"
  117 |     filters:
  118 |       tag:workshop: "{{ workshop_name }}"
  119 |       tag:workshop_prefix: "{{ workshop_prefix }}"
  120 |   register: ec2_subnet
  121 | 
  122 | - name: Record subnet ID
  123 |   set_fact:
  124 |     subnet_id: "{{ ec2_subnet.subnets[0].subnet_id }}"
  125 |   when: ec2_subnet.subnets|length > 0
  126 | 
  127 | - name: lookup running vpc route tables
  128 |   ec2_vpc_route_table_info:
  129 |     region: "{{ region }}"
  130 |     filters:
  131 |       tag:workshop: "{{ workshop_name }}"
  132 |       tag:workshop_prefix: "{{ workshop_prefix }}"
  133 |   register: ec2_route
  134 | 
  135 | - name: Record route table ID 
  136 |   set_fact:
  137 |     route_id: "{{ ec2_route.route_tables[0].id }}"
  138 |   when: ec2_route.route_tables|length > 0
  139 | 
  140 | - name: lookup running vpcs
  141 |   ec2_vpc_net_info:
  142 |     region: "{{ region }}"
  143 |     filters:
  144 |       tag:workshop: "{{ workshop_name }}"
  145 |       tag:workshop_prefix: "{{ workshop_prefix }}"
  146 |   register: ec2_vpc
  147 | 
  148 | - name: Record VPC ID
  149 |   set_fact:
  150 |     vpc_id: "{{ ec2_vpc.vpcs[0].id }}"
  151 |   when: ec2_vpc.vpcs|length > 0
  152 | 
  153 | - name: Lookup existing Windows DNS records
  154 |   route53:
  155 |     state: get
  156 |     zone: "{{ domain_name }}"
  157 |     record: "{{ workshop_prefix }}.win2016.{{ dns_idx }}.{{ domain_name }}"
  158 |     type: CNAME
  159 |   register: win_rec
  160 |   loop: "{{ win_instance_ids }}"
  161 |   loop_control:
  162 |     index_var: dns_idx
  163 |   ignore_errors: true
  164 | 
  165 | - name: Lookup existing RHEL admin DNS records
  166 |   route53:
  167 |     state: get
  168 |     zone: "{{ domain_name }}"
  169 |     record: "{{ workshop_prefix }}.admin.{{ domain_name }}"
  170 |     type: CNAME
  171 |   register: admin_rhel_rec
  172 |   loop: "{{ admin_rhel_instance_ids }}"
  173 |   loop_control:
  174 |     index_var: dns_idx
  175 |   ignore_errors: true
  176 | 
  177 | - name: Lookup existing RHEL DNS records
  178 |   route53:
  179 |     state: get
  180 |     zone: "{{ domain_name }}"
  181 |     record: "{{ workshop_prefix }}.node.{{ dns_idx }}.{{ domain_name }}"
  182 |     type: CNAME
  183 |   register: rhel_rec
  184 |   loop: "{{ rhel_instance_ids }}"
  185 |   loop_control:
  186 |     index_var: dns_idx
  187 |   ignore_errors: true
  188 | 
  189 | - name: Lookup existing RHEL Tower DNS records
  190 |   route53:
  191 |     state: get
  192 |     zone: "{{ domain_name }}"
  193 |     record: "{{ workshop_prefix }}.tower.{{ dns_idx }}.{{ domain_name }}"
  194 |     type: CNAME
  195 |   register: tower_rhel_rec
  196 |   loop: "{{ tower_rhel_instance_ids }}"
  197 |   loop_control:
  198 |     index_var: dns_idx
  199 |   ignore_errors: true
  200 | 
  201 | 
  202 | #===============================================================================
  203 | #  Deprovisioning
  204 | #===============================================================================
  205 | 
  206 | - name: Remove existing Windows DNS records
  207 |   route53:
  208 |     state: absent
  209 |     zone: "{{ domain_name }}"
  210 |     record: "{{ item.set.record }}"
  211 |     ttl: "{{ item.set.ttl }}"
  212 |     type: "{{ item.set.type }}"
  213 |     value: "{{ item.set.value }}"
  214 |   when: item.set.record is defined
  215 |   with_items: "{{ win_rec.results }}"
  216 | 
  217 | - name: Remove Windows instances
  218 |   ec2:
  219 |     key_name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-key"
  220 |     group: "{{ workshop_abbrev }}-{{ workshop_prefix }}-win-sg"
  221 |     region: "{{ region }}"
  222 |     instance_type: "{{ win_instance_type }}"
  223 |     image: "{{ regions[region][win_ver].ami }}"
  224 |     vpc_subnet_id: "{{ subnet_id }}"
  225 |     wait: true
  226 |     instance_ids: "{{ win_instance_ids }}"
  227 |     state: absent
  228 |   when: win_instance_ids|length > 0
  229 | 
  230 | - name: Remove existing RHEL admin DNS records
  231 |   route53:
  232 |     state: absent
  233 |     zone: "{{ domain_name }}"
  234 |     record: "{{ item.set.record }}"
  235 |     ttl: "{{ item.set.ttl }}"
  236 |     type: "{{ item.set.type }}"
  237 |     value: "{{ item.set.value }}"
  238 |   when: item.set.record is defined
  239 |   with_items: "{{ admin_rhel_rec.results }}"
  240 | 
  241 | - name: Remove existing RHEL DNS records
  242 |   route53:
  243 |     state: absent
  244 |     zone: "{{ domain_name }}"
  245 |     record: "{{ item.set.record }}"
  246 |     ttl: "{{ item.set.ttl }}"
  247 |     type: "{{ item.set.type }}"
  248 |     value: "{{ item.set.value }}"
  249 |   when: item.set.record is defined
  250 |   with_items: "{{ rhel_rec.results }}"
  251 | 
  252 | - name: Remove existing RHEL Tower DNS records
  253 |   route53:
  254 |     state: absent
  255 |     zone: "{{ domain_name }}"
  256 |     record: "{{ item.set.record }}"
  257 |     ttl: "{{ item.set.ttl }}"
  258 |     type: "{{ item.set.type }}"
  259 |     value: "{{ item.set.value }}"
  260 |   when: item.set.record is defined
  261 |   with_items: "{{ tower_rhel_rec.results }}"
  262 | 
  263 | - name: Remove RHEL Tower instances
  264 |   ec2:
  265 |     key_name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-key"
  266 |     group: "{{ workshop_abbrev }}-{{ workshop_prefix }}-rhel-sg"
  267 |     region: "{{ region }}"
  268 |     instance_type: "{{ tower_instance_type }}"
  269 |     image: "{{ regions[region][rhel_ver].ami }}"
  270 |     vpc_subnet_id: "{{ subnet_id }}"
  271 |     wait: true
  272 |     instance_ids: "{{ tower_rhel_instance_ids }}"
  273 |     state: absent
  274 |   when: tower_rhel_instance_ids|length > 0
  275 |     #  when: false
  276 | 
  277 | - name: Remove RHEL admin instances
  278 |   ec2:
  279 |     key_name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-key"
  280 |     group: "{{ workshop_abbrev }}-{{ workshop_prefix }}-rhel-sg"
  281 |     region: "{{ region }}"
  282 |     instance_type: "{{ rhel_instance_type }}"
  283 |     image: "{{ regions[region][rhel_ver].ami }}"
  284 |     vpc_subnet_id: "{{ subnet_id }}"
  285 |     wait: true
  286 |     instance_ids: "{{ admin_rhel_instance_ids }}"
  287 |     state: absent
  288 |   when: admin_rhel_instance_ids|length > 0
  289 | 
  290 | - name: Remove RHEL instances
  291 |   ec2:
  292 |     key_name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-key"
  293 |     group: "{{ workshop_abbrev }}-{{ workshop_prefix }}-rhel-sg"
  294 |     region: "{{ region }}"
  295 |     instance_type: "{{ rhel_instance_type }}"
  296 |     image: "{{ regions[region][rhel_ver].ami }}"
  297 |     vpc_subnet_id: "{{ subnet_id }}"
  298 |     wait: true
  299 |     instance_ids: "{{ rhel_instance_ids }}"
  300 |     state: absent
  301 |   when: rhel_instance_ids|length > 0
  302 | 
  303 | - name: Delete VPC route table
  304 |   ec2_vpc_route_table:
  305 |     region: "{{ region }}"
  306 |     vpc_id: "{{ vpc_id }}"
  307 |     lookup: id
  308 |     route_table_id: "{{ route_id }}"
  309 |     state: absent
  310 | 
  311 | - name: Delete public subnet
  312 |   ec2_vpc_subnet:
  313 |     region: "{{ region }}"
  314 |     cidr: "10.0.2.0/24"
  315 |     vpc_id: "{{ vpc_id }}"
  316 |     state: absent
  317 | 
  318 | - name: Delete Windows security group
  319 |   ec2_group:
  320 |     name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-win-sg"
  321 |     region: "{{ region }}"
  322 |     state: absent
  323 | 
  324 | - name: Delete RHEL security group
  325 |   ec2_group:
  326 |     name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-rhel-sg"
  327 |     region: "{{ region }}"
  328 |     state: absent
  329 | 
  330 | - name: Delete VPC internet gateway
  331 |   ec2_vpc_igw:
  332 |     region: "{{ region }}"
  333 |     vpc_id: "{{ vpc_id }}"
  334 |     state: absent
  335 | 
  336 | - name: Delete VPC
  337 |   ec2_vpc_net:
  338 |     name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-vpc"
  339 |     region: "{{ region }}"
  340 |     cidr_block: "10.0.0.0/16"
  341 |     state: absent
  342 | 
  343 | - name: Delete key
  344 |   ec2_key:
  345 |     name: "{{ workshop_abbrev }}-{{ workshop_prefix }}-key"
  346 |     region: "{{ region }}"
  347 |     state: absent
  348 | 
  349 | ...
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-015

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: Maintainability/complexity
- Rule: `ansibleguard/deprecated-modules`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `jboss-aws-setup/roles/aws-teardown/tasks/04_dns.yml` (reported anchor line 29)
- Object: `task` `ece748e11c22e06e636cc1b51e7261ef4bd1a84f181a2b08cac33f9d8d73e589`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–34 of 34:

```text
    1 | ---
    2 | - name: List all hosted zones
    3 |   route53_facts:
    4 |     query: hosted_zone
    5 |   register: hosted_zones
    6 | 
    7 | - name: Delete master and bastion routes
    8 |   include: delete-route.yml zone={{ intranet }} record="{{item}}.{{ intranet }}" private_zone="true"
    9 |   with_items:
   10 |     - "bastion"
   11 |     - "master"
   12 | 
   13 | - name: Delete node routes
   14 |   include: delete-route.yml zone={{ intranet }} record="node{{item}}.{{ intranet }}" private_zone="true"
   15 |   with_sequence: start=1 end={{ec2_node_count|int}}
   16 | 
   17 | - name: Delete private DNS zone for openshift
   18 |   route53_zone:
   19 |      zone: "{{ intranet }}"
   20 |      state: "absent"
   21 |      vpc_region: "{{ aws_region }}"
   22 |      comment: "Internal zone for Openshift"
   23 |   ignore_errors: yes
   24 | 
   25 | - name: Delete Public Route
   26 |   include: delete-route.yml zone={{ domain }} record={{ domain }} private_zone="false"
   27 | 
   28 | - name: Delete Public Wildcard Route
   29 |   include: delete-route.yml zone={{ domain }} record="{{ wildcard }}" private_zone="false"
   30 | 
   31 | # - name: Delete private zone for openshift
   32 | #   route53_zone:
   33 | #      zone: "{{ intranet }}"
   34 | #      state: "absent"
```

# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-011

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: Maintainability/complexity
- Rule: `ansibleguard/undocumented-complex-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `automation/roles/cloud_resources/tasks/aws.yml` (reported anchor line 473)
- Object: `source_location` `38d1f02d233d03b4f765004b7e44e3bc1f461c3f9ac958c16d0e069f29789c12`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 438–508 of 726:

```text
  438 |           ping_port: "{{ patroni_restapi_port | default('8008') }}"
  439 |           ping_path: "/{{ item }}"
  440 |           interval: 5
  441 |           timeout: 2
  442 |           unhealthy_threshold: 2
  443 |           healthy_threshold: 3
  444 |         idle_timeout: 600
  445 |         scheme: "{{ 'internet-facing' if database_public_access | bool else 'internal' }}"
  446 |         state: present
  447 |       loop:
  448 |         - "primary"
  449 |         - "replica"
  450 |         - "sync"
  451 |       loop_control:
  452 |         label: "{{ patroni_cluster_name }}-{{ item }}"
  453 |       register: aws_elb_classic_lb
  454 |       until: aws_elb_classic_lb is success
  455 |       retries: 3
  456 |       delay: 10
  457 |       when: server_result.results | default([]) | length > 0 and
  458 |         cloud_load_balancer | bool and aws_load_balancer_type | lower == 'clb' and
  459 |         (item == 'primary' or
  460 |         (item == 'replica' and server_count | int > 1) or
  461 |         (item in ['sync', 'async'] and server_count | int > 1 and synchronous_mode | bool))
  462 | 
  463 |     # Network Load Balancer (NLB)
  464 |     - name: Build NLB targets
  465 |       ansible.builtin.set_fact:
  466 |         nlb_targets: "{{ (nlb_targets | default([])) + [{'Id': item, 'Port': target_port | int}] }}"
  467 |       loop: "{{ instance_ids | default([]) }}"
  468 |       vars:
  469 |         instance_ids: "{{ (server_result | default({'results': []})) | json_query('results[].instances[].instance_id') }}"
  470 |         target_port: "{{ pgbouncer_listen_port | default('6432') if pgbouncer_install | bool else postgresql_port | default('5432') }}"
  471 |       when: cloud_load_balancer | bool and aws_load_balancer_type | lower == 'nlb'
  472 | 
  473 |     - name: "AWS: Create or modify NLB Target Group"
  474 |       community.aws.elb_target_group:
  475 |         access_key: "{{ lookup('ansible.builtin.env', 'AWS_ACCESS_KEY_ID') }}"
  476 |         secret_key: "{{ lookup('ansible.builtin.env', 'AWS_SECRET_ACCESS_KEY') }}"
  477 |         name: "{{ patroni_cluster_name }}-tg-{{ item }}"
  478 |         region: "{{ server_location }}"
  479 |         vpc_id: "{{ vpc_id }}"
  480 |         protocol: "TCP"
  481 |         port: "{{ target_port }}"
  482 |         preserve_client_ip_enabled: true
  483 |         health_check_protocol: "{{ patroni_restapi_protocol | default('http') }}"
  484 |         health_check_port: "{{ patroni_restapi_port | default('8008') }}"
  485 |         health_check_path: "/{{ item }}"
  486 |         health_check_interval: 5
  487 |         health_check_timeout: 2
  488 |         unhealthy_threshold_count: 2
  489 |         healthy_threshold_count: 3
  490 |         successful_response_codes: "200"
  491 |         target_type: instance
  492 |         targets: "{{ nlb_targets | default([]) }}"
  493 |         modify_targets: true
  494 |         wait: false
  495 |         state: present
  496 |       loop:
  497 |         - "primary"
  498 |         - "replica"
  499 |         - "sync"
  500 |       loop_control:
  501 |         label: "{{ patroni_cluster_name }}-tg-{{ item }}"
  502 |       vars:
  503 |         target_port: "{{ pgbouncer_listen_port | default('6432') if pgbouncer_install | bool else postgresql_port | default('5432') }}"
  504 |       when: cloud_load_balancer | bool and aws_load_balancer_type | lower == 'nlb' and
  505 |         (item == 'primary' or
  506 |         (item == 'replica' and server_count | int > 1) or
  507 |         (item in ['sync', 'async'] and server_count | int > 1 and synchronous_mode | bool))
  508 | 
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.

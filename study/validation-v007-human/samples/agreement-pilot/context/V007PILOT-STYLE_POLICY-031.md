# Frozen source context: V007PILOT-STYLE_POLICY-031

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-task`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `src/commcare_cloud/ansible/ping.yml` (reported anchor line 4)
- Object: `source_location` `e770382f67cd3b6bdfc565ef920cb19ed8cfb2d8e0a5537b2d2839d8ce5800e3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–132 of 132:

```text
    1 | - hosts:
    2 |   - all
    3 |   tasks:
    4 |   - action: ping
    5 |   - wait_for:
    6 |       host: "{{ item }}"
    7 |       port: 22
    8 |       timeout: 5
    9 |     with_items: "{{ groups['all'] }}"
   10 |   - debug: msg=ok
   11 | 
   12 | - hosts:
   13 |   - proxy
   14 |   tasks:
   15 |   - command: service nginx status
   16 |     name: Check nginx status
   17 |     args:
   18 |       warn: False
   19 | 
   20 | - hosts:
   21 |   - webworkers
   22 |   tasks:
   23 |   - command: supervisorctl status
   24 |     become: True
   25 |     name: Check supervisor processes status
   26 |     args:
   27 |       warn: False
   28 | 
   29 | - hosts:
   30 |   - postgresql
   31 |   - pg_standby
   32 |   tasks:
   33 |   - command: service pgbouncer status
   34 |     name: Check pgbouncer status
   35 |     args:
   36 |       warn: False
   37 |   - command: service postgresql status
   38 |     name: Check postgresql status
   39 |     args:
   40 |       warn: False
   41 | 
   42 | - hosts:
   43 |   - couchdb2
   44 |   tasks:
   45 |   - command: service couchdb2 status
   46 |     name: Check couchdb status
   47 |     args:
   48 |       warn: False
   49 | 
   50 | - hosts:
   51 |   - redis
   52 |   tasks:
   53 |   - command: service redis-server status
   54 |     name: Check redis status
   55 |     become: True
   56 |     args:
   57 |       warn: False
   58 | 
   59 | - hosts:
   60 |   - zookeeper
   61 |   tasks:
   62 |   - command: service zookeeper-server status
   63 |     name: Check zookeeper status
   64 |     become: True
   65 |     args:
   66 |       warn: False
   67 | 
   68 | - hosts:
   69 |   - kafka
   70 |   tasks:
   71 |   - command: service kafka-server status
   72 |     name: Check kafka status
   73 |     args:
   74 |       warn: False
   75 | 
   76 | - hosts:
   77 |   - all
   78 |   - mailrelay
   79 |   tasks:
   80 |   - command: service postfix status
   81 |     name: Check postfix status
   82 |     become: True
   83 |     args:
   84 |       warn: False
   85 | 
   86 | - hosts:
   87 |   - pillowtop
   88 |   - celery
   89 |   tasks:
   90 |   - command: supervisorctl status
   91 |     become: True
   92 |     name: Check supervisor processes status
   93 |     args:
   94 |       warn: False
   95 | 
   96 | - hosts:
   97 |   - formplayer
   98 |   tasks:
   99 |   - command: supervisorctl status
  100 |     become: True
  101 |     name: Check supervisor processes status
  102 |     args:
  103 |       warn: False
  104 | 
  105 | - hosts:
  106 |   - elasticsearch
  107 |   tasks:
  108 |   - command: service elasticsearch status
  109 |     name: Check elasticsearch status
  110 |     args:
  111 |       warn: False
  112 | 
  113 | - hosts:
  114 |   - elasticsearch
  115 |   tasks:
  116 |   - uri: url="http://{{ inventory_hostname }}:9200/_cluster/health" return_content=yes
  117 |     name: Get ES status
  118 |     register: es_status
  119 |     when: inventory_hostname == groups.elasticsearch.0
  120 |   - assert:
  121 |       that: "es_status.json.status == 'green'"
  122 |       msg: "ES health is {{ es_status.json.status }}"
  123 |     name: Check ES status
  124 |     when: inventory_hostname == groups.elasticsearch.0
  125 | 
  126 | - hosts:
  127 |   - shared_dir_host
  128 |   tasks:
  129 |   - command: service nfs-kernel-server status
  130 |     name: Check NFS status
  131 |     args:
  132 |       warn: False
```

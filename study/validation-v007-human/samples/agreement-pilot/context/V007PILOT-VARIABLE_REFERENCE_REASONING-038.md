# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-038

- Repository: `dfroberg/cluster`
- Commit: `7bc521db65db986a2deef35ea955704bb0621dbd`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/role-variable-precedence-collision`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `provision/ansible_new/kubernetes/roles/k3s.kubernetes/vars/main/etcd-snapshots.yml` (reported anchor line 3)
- Object: `variable` `25dadd67807807a498821c87eee21e9965d6c98f0450962339d16207d830368f`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–9 of 9:

```text
    1 | ---
    2 | # -- enable exporting etcd backups to s3
    3 | k3s_etcd_s3: "true"
    4 | # -- snapshot bucket name
    5 | k3s_etcd_s3_bucket: k3s
    6 | # -- snapshot schedule
    7 | k3s_etcd_snapshot_schedule_cron: "0 */6 * * *"
    8 | # -- snapshot retention
    9 | k3s_etcd_snapshot_retention: 28
```

## Visible variable references

```text
7bc521db65db986a2deef35ea955704bb0621dbd:provision/ansible_new/kubernetes/roles/k3s.kubernetes/defaults/main.yml:2:k3s_etcd_s3: false
7bc521db65db986a2deef35ea955704bb0621dbd:provision/ansible_new/kubernetes/roles/k3s.kubernetes/templates/k3s/10-etcd-snapshots.yaml.j2:2:etcd-s3: {{ k3s_etcd_s3 | bool | lower }}
7bc521db65db986a2deef35ea955704bb0621dbd:provision/ansible_new/kubernetes/roles/k3s.kubernetes/templates/k3s/10-etcd-snapshots.yaml.j2:3:{% if k3s_etcd_s3 %}
7bc521db65db986a2deef35ea955704bb0621dbd:provision/ansible_new/kubernetes/roles/k3s.kubernetes/templates/k3s/10-etcd-snapshots.yaml.j2:7:etcd-s3-bucket: "{{ k3s_etcd_s3_bucket }}"
7bc521db65db986a2deef35ea955704bb0621dbd:provision/ansible_new/kubernetes/roles/k3s.kubernetes/vars/main/etcd-snapshots.yml:3:k3s_etcd_s3: "true"
7bc521db65db986a2deef35ea955704bb0621dbd:provision/ansible_new/kubernetes/roles/k3s.kubernetes/vars/main/etcd-snapshots.yml:5:k3s_etcd_s3_bucket: k3s
```

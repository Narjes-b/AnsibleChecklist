# Frozen source context: V007PILOT-STRUCTURE_REUSE-022

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/roles/cassandra3/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `6f32c02c8c8cdca284002c632a5a01cffebd4da41ace16b90e776956a54a0904`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–12 of 12:

```text
    1 | ---
    2 | - include_tasks: ../../common/tasks/setfacts.yml
    3 |   tags:
    4 |     - cassandra
    5 | 
    6 | - name: Include docker tasks
    7 |   include_tasks: docker-tasks.yml
    8 |   when: deployment_type == 'swarm'
    9 | 
   10 | - name: Include VM tasks
   11 |   import_tasks: vm-tasks.yml
   12 |   when: deployment_type == 'vm'
```

## Frozen tracked paths in the relevant role/scope

```text
ansible/roles/cassandra3/defaults/main.yml
ansible/roles/cassandra3/files/conf/90-nproc.conf
ansible/roles/cassandra3/files/conf/limits.conf
ansible/roles/cassandra3/files/yum/datastax.repo
ansible/roles/cassandra3/handlers/main.yml
ansible/roles/cassandra3/tasks/docker-tasks.yml
ansible/roles/cassandra3/tasks/main.yml
ansible/roles/cassandra3/tasks/vm-tasks.yml
ansible/roles/cassandra3/templates/cassandra-bitnami-env.sh
ansible/roles/cassandra3/templates/cassandra-bitnami.yaml
ansible/roles/cassandra3/templates/cassandra-env.sh
ansible/roles/cassandra3/templates/cassandra.yaml
ansible/roles/cassandra3/templates/docker-compose.yml.j2
ansible/roles/cassandra3/vars/main.yml
```

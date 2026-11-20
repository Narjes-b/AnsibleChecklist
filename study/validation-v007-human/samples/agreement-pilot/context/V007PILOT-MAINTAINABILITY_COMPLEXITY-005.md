# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-005

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: Maintainability/complexity
- Rule: `ansibleguard/high-coupling`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `ansible/profiles.yml` (reported anchor line 1)
- Object: `source_location` `7c8f61dc9f9adf6751675100807d85f9018e35d07d0cf8039183e5ae237a4322`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–11 of 11:

```text
    1 | - hosts: all
    2 |   roles:
    3 |     - common
    4 |     - { role: java, when: is_primary | bool }
    5 |     - {role: mongodb-org, dbPath: "{{ profiles_dbPath }}"}
    6 |     - { role: webserver, when: is_primary | bool }
    7 |     - { role: nameindex, when: is_primary | bool }
    8 |     - { role: ansible-elasticsearch, es_templates: false, es_instance_name: 'profiles-elasticsearch', es_data_dirs: ['/data/elasticsearch'], tags: ['elasticsearch'], when: install_elasticsearch | bool }
    9 | #    cannot put is_primary condition on this role as it is used to create various mongo roles
   10 |     - profile-service
   11 |     - { role: profile-hub, when: is_primary | bool }
```

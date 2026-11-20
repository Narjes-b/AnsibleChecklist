# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-001

- Repository: `redhat-cop/infra.aap_configuration`
- Commit: `f84d6a61e4b18aa135d707fe539371587bc92931`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-expression`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/hub_publish/tasks/evaluate_tarball_item.yml` (reported anchor line 6)
- Object: `source_location` `27f21164d0ced4db32eb2d2a8d84a318ea4e0972c028537e508ec4ce6324e478`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–20 of 20:

```text
    1 | ---
    2 | - name: evaluate_tarball_item | Set tarball metadata from filename
    3 |   ansible.builtin.set_fact:
    4 |     __hub_publish_namespace: "{{ (__hub_collection_tarball | basename).split('-')[0] }}"
    5 |     __hub_publish_name: "{{ (__hub_collection_tarball | basename).split('-')[1] }}"
    6 |     __hub_publish_version: "{{ (__hub_collection_tarball | basename).split('-')[2:] | join('-') | splitext | first | splitext | first }}"
    7 |     __hub_publish_overwrite: "{{ hub_overwrite_existing | bool }}"
    8 |     __hub_publish_should_skip: false
    9 | 
   10 | - name: evaluate_tarball_item | Existence check for pre-built collection tarball
   11 |   ansible.builtin.include_tasks: check_collection_version.yml
   12 |   when: hub_skip_existing_collections | bool
   13 | 
   14 | - name: evaluate_tarball_item | Register pending pre-built collection tarball
   15 |   ansible.builtin.set_fact:
   16 |     __hub_publish_pending_tarballs: "{{ __hub_publish_pending_tarballs + [__hub_collection_tarball] }}"
   17 |     __hub_publish_overwrite_lookup: "{{ __hub_publish_overwrite_lookup | combine({(__hub_publish_namespace + '.' + __hub_publish_name + ':' + __hub_publish_version): __hub_publish_overwrite}) }}"
   18 |   when: not (__hub_publish_should_skip | default(false) | bool)
   19 | 
   20 | ...
```

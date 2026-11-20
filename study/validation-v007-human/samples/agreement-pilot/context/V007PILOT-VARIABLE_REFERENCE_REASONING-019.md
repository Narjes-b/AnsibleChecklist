# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-019

- Repository: `folio-org/folio-ansible`
- Commit: `dde7c5f2011b34eb79b03ef38f334b34449e67af`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/missing-bool-filters`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/okapi-kubernetes/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `a75c7c623b98c6d99d74f0540989aece7d1f50453ac959bc9bfbf0d92159362d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–33 of 33:

```text
    1 | ---
    2 | - name: create hazelcast service account
    3 |   k8s:
    4 |     state: present
    5 |     definition: "{{ lookup('template', 'rbac.yml.j2') }}"
    6 |   when: create_rbac == "true"
    7 | 
    8 | - name: create okapi pod service account
    9 |   k8s:
   10 |     state: present
   11 |     definition: "{{ lookup('template', 'okapi-sa.yml.j2') }}"
   12 |   when: sa_name != "default"
   13 | 
   14 | - name: create okapi service
   15 |   k8s:
   16 |     state: present
   17 |     definition: "{{ lookup('template', 'okapi-service.yml.j2') }}"
   18 | 
   19 | - name: create hazelcast configmap
   20 |   k8s:
   21 |     state: present
   22 |     definition: "{{ lookup('template', 'hazelcast-configmap.yml.j2') }}"
   23 | 
   24 | - name: create okapi deployment
   25 |   k8s:
   26 |     state: present
   27 |     definition: "{{ lookup('template', 'okapi-deployment.yml.j2') }}"
   28 | 
   29 | - name: create okapi ingress
   30 |   k8s:
   31 |     state: present
   32 |     definition: "{{ lookup('template', 'okapi-ingress.yml.j2') }}"
   33 |   when: create_ingress
```

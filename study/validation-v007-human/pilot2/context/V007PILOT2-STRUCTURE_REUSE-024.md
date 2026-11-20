# Frozen source context: V007PILOT2-STRUCTURE_REUSE-024

- Repository: `Sunbird-Obsrv/sunbird-data-pipeline`
- Commit: `eb1e1a1c3533c549693dda32cd92c667754aaea9`
- Family: structure_reuse
- Rule: `ansibleguard/unexpected-task-location`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `ansible/roles/data-products-fetch-logs/tasks/defaults/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`ansible/roles/data-products-fetch-logs/tasks/defaults/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–2 of 2:

```text
    1 | analytics:
    2 |    home: /mount/data/analytics
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `ansible/roles/data-products-fetch-logs`; 3 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: no
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

ansible/roles/data-products-fetch-logs/defaults/main.yml
ansible/roles/data-products-fetch-logs/tasks/defaults/main.yml
ansible/roles/data-products-fetch-logs/tasks/main.yml
```

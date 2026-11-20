# Frozen source context: V007PILOT2-STRUCTURE_REUSE-019

- Repository: `CentOS-PaaS-SIG/linchpin`
- Commit: `0703f6bcb683afa7f543e9f3e8f4153bc3c9b36f`
- Family: structure_reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `linchpin/provision/roles/dependencies/tasks/beaker_deps.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`linchpin/provision/roles/dependencies/tasks/beaker_deps.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–3 of 3:

```text
    1 | - name: Install pypi dependencies of beaker
    2 |   pip:
    3 |     name: ['beaker-client>=27.0', 'bottle']
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `linchpin/provision/roles/dependencies`; 1 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: no
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

linchpin/provision/roles/dependencies/tasks/beaker_deps.yml
```

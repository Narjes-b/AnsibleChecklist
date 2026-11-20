# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-014

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: objective_correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `automation/roles/ntp/meta/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`automation/roles/ntp/meta/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–3 of 3:

```text
    1 | ---
    2 | dependencies:
    3 |   - role: vitabaks.autobase.common
```

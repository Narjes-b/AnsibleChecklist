# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-020

- Repository: `chrisshaiman/lamware`
- Commit: `09f919635087b38354bce34c9bc48e7c6517b463`
- Family: objective_correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `ansible/roles/cape-guests/handlers/main.yml` (reported anchor line 4)
- Flagged construct: not named by the finding; the anchor line 4 lies in the task at line 4, name `Restart Cape services`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–13 of 13:

```text
    1 | ---
    2 | # roles/cape-guests/handlers/main.yml
    3 | 
    4 | - name: Restart Cape services
    5 |   ansible.builtin.systemd:
    6 |     name: "{{ item }}"
    7 |     state: restarted
    8 |     daemon_reload: true
    9 |   loop:
   10 |     - cape
   11 |     - cape-web
   12 |     - cape-processor
   13 |   failed_when: false
```

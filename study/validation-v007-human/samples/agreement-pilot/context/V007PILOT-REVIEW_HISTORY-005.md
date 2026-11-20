# Frozen Git review context: V007PILOT-REVIEW_HISTORY-005

- Repository: `ric03uec/clawrium`
- Target commit: `77274d5ca3d71b5a057df332482dd678446d9544`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
daily-docs-sweep 2026-08-02 (#964)

* docs: add --home-channel flag to Discord channel docs (#642)

PR #961 unblocked --home-channel for Discord channels but the
documentation was never updated. Add the flag to the Hermes setup
example, flags table, and channels.json example in docs/ and mirror
to website/.

Refs #642

* docs(#642): drop stale "slack only" marker on home_channel schema comment

The channels.json schema docstring in core/channels.py still described
home_channel as Slack-only after #961 lifted the CLI guard for Discord.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---------

Co-authored-by: Clawrium Agent <clawrium-agent@nousresearch.com>
Co-authored-by: Claude Opus 4.5 <noreply@anthropic.com>
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

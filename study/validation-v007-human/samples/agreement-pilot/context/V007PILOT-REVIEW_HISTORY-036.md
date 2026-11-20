# Frozen Git review context: V007PILOT-REVIEW_HISTORY-036

- Repository: `ConnectBox/connectbox-pi`
- Target commit: `e69eabdecfa2e39b2751acdb928bfafb2f8f28f6`
- Actual first parent: `7309078d0c3b67ee43eb4dfba4b82d39e69d9a14` (available; diff not required by this message-only rule)
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/missing-bug-reference`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
fix(usb-mounter): add -A flag to all umount calls

umount -A unmounts all mounts of the same device in one call, which
clears stacked bind mounts reliably without needing multiple loop
iterations. Applied to the pre-mount cleanup loop and both paths in
handle_remove (by device node and by mount point fallback).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

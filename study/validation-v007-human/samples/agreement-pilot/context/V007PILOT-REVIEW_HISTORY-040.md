# Frozen Git review context: V007PILOT-REVIEW_HISTORY-040

- Repository: `ansible/vscode-ansible`
- Target commit: `a63dab35a4c1c530142bc1f29fb7c03bacb46578`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/missing-bug-reference`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
fix: point MCP Learn More links to docs.ansible.com (AAP-73918) (#3139)

## Summary
- Fix broken MCP "Learn More" links on the VS Code marketplace details
page
- Replace relative `mcp/README.md` and `mcp/api.md` paths with published
docs.ansible.com URLs
- Matches how other links in `docs/README.md` already point to the docs
site (e.g. Contact)

## Context
Fixes [AAP-73918](https://redhat.atlassian.net/browse/AAP-73918).
Relative markdown links were resolving to non-existent GitHub URLs
(`.../mcp/README.md`) on the marketplace.

## Test plan
- [ ] Open `docs/README.md` and confirm both MCP links resolve to
docs.ansible.com
- [ ] Verify https://docs.ansible.com/projects/vscode-ansible/mcp/ loads
- [ ] Verify https://docs.ansible.com/projects/vscode-ansible/mcp/api/
loads

<!-- This is an auto-generated comment: release notes by coderabbit.ai
-->

- Updated the MCP “Learn More” links in `docs/README.md` to use
published `docs.ansible.com` URLs.
- Fixed broken links on the VS Code Marketplace details page by
replacing relative paths with absolute documentation links.
- Addresses AAP-73918.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.

# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-014

- Repository: `ansible/vscode-ansible`
- Target commit: `a63dab35a4c1c530142bc1f29fb7c03bacb46578`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

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


The rule is evaluated only on the exact target commit message above.

# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-011

- Repository: `ansible-collections/community.vmware`
- Target commit: `f8fde60167ae8f6d252d46691913f7a451e2d723`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
vmware_vcenter_settings: Deprecate defaults (#2566)

SUMMARY
When using vmware_vcenter_settings to set a single advanced_settings value, it also overwrites all other vCenter settings to defaults which is not intuitive or expected. So all the defaults will be remove in community.vmware 8.0.0 where possible.
ISSUE TYPE

Feature Pull Request

COMPONENT NAME
vmware_vcenter_settings
ADDITIONAL INFORMATION
#2559
```

## Changed paths (not required for message-only evidence)


The rule is evaluated only on the exact target commit message above.

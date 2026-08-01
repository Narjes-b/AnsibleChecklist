"""Versioned decisions for concepts detected by more than one provider."""

OVERLAP_POLICY_VERSION = 1

OVERLAP_POLICY = {
    "duplicate-mapping-key": {
        "relationship": "substantial",
        "canonical_provider": "ansible-lint",
        "disposition": "internal-shadow",
        "reason": (
            "ansible-lint/yaml[key-duplicates] is the developer-facing "
            "authority; the internal detector remains visible for comparison."
        ),
    },
    "module-deprecation": {
        "relationship": "substantial",
        "canonical_provider": "ansible-lint",
        "disposition": "compare-and-augment",
        "reason": (
            "ansible-lint is canonical for its known set while AnsibleGuard "
            "adds installed metadata and replacement evidence."
        ),
    },
    "shell-module-migration": {
        "relationship": "substantial",
        "canonical_provider": "ansibleguard",
        "disposition": "merge-evidence",
        "reason": (
            "Both results remain visible; AnsibleGuard owns actionable "
            "command-to-module migration evidence."
        ),
    },
    "credential-log-exposure": {
        "relationship": "partial",
        "canonical_provider": "ansibleguard",
        "disposition": "merge-evidence",
        "reason": (
            "ansible-lint covers password loops; AnsibleGuard covers broader "
            "structured sensitive arguments and effective no_log handling."
        ),
    },
    "unhandled-failure-suppression": {
        "relationship": "partial",
        "canonical_provider": "ansibleguard",
        "disposition": "merge-evidence",
        "reason": (
            "ansible-lint covers broad ignore_errors while AnsibleGuard also "
            "checks failed_when:false and whether registered results are used."
        ),
    },
}


def overlap_policy(concept_id):
    return OVERLAP_POLICY.get(concept_id, {})

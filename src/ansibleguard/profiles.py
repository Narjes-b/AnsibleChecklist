"""Explicit, versioned rule populations for technical and research scans."""

from __future__ import annotations

import hashlib
import json

from .report.findings import RULE_CATALOG


TECHNICAL_FULL = "technical-full"
SNAPSHOT_SOURCE = "snapshot-source"
RESEARCH_CORE = "research-core"
EXTENDED_ANSIBLE = "extended-ansible"
REVIEW_RANGE = "review-range"
PROFILE_NAMES = (
    TECHNICAL_FULL,
    SNAPSHOT_SOURCE,
    RESEARCH_CORE,
    EXTENDED_ANSIBLE,
    REVIEW_RANGE,
)

REVIEW_RULES = frozenset(
    {
        "missing-release-note",
        "missing-bug-reference",
        "invalid-depends-on-reference",
        "commit-message-format",
        "removed-copyright-notice",
        "missing-test-update",
        "untested-override-change",
    }
)
EXTERNAL_RULES = frozenset({"hardcoded-credentials", "ansible-lint-issue"})

# Conservative v1 allowlist.  The unresolved-variable construct is
# intentionally quarantined in extended-ansible until OpenStack cross-file
# variable resolution and manual precision validation are complete.
RESEARCH_CORE_RULES = frozenset(
    {
        "complex-expression",
        "incomplete-task",
        "long-statement",
        "unstructured-module",
        "empty-abstraction",
        "excessive-nesting",
        "missing-abstraction",
        "broken-role-dependency",
    }
)

ALL_RULES = frozenset(RULE_CATALOG)
SNAPSHOT_RULES = ALL_RULES - REVIEW_RULES - EXTERNAL_RULES
EXTENDED_RULES = SNAPSHOT_RULES - RESEARCH_CORE_RULES

PROFILE_DEFINITIONS = {
    TECHNICAL_FULL: {
        "description": "All internal, external-tool, and Git review findings.",
        "rules": ALL_RULES,
        "source_analysis": True,
        "review_analysis": True,
        "external_tools": True,
        "requires_manifest": False,
        "research_eligible": False,
    },
    SNAPSHOT_SOURCE: {
        "description": (
            "All internal source findings at one frozen repository state; "
            "review-range and aggregate external-tool rules are excluded."
        ),
        "rules": SNAPSHOT_RULES,
        "source_analysis": True,
        "review_analysis": False,
        "external_tools": False,
        "requires_manifest": True,
        "research_eligible": False,
    },
    RESEARCH_CORE: {
        "description": (
            "Conservative paper-derived source allowlist for primary empirical "
            "analysis."
        ),
        "rules": RESEARCH_CORE_RULES,
        "source_analysis": True,
        "review_analysis": False,
        "external_tools": False,
        "requires_manifest": True,
        "research_eligible": False,
        "status": "provisional-pending-manual-calibration",
    },
    EXTENDED_ANSIBLE: {
        "description": (
            "Ansible-specific internal source rules outside the conservative "
            "research core, reported as a disjoint secondary stratum."
        ),
        "rules": EXTENDED_RULES,
        "source_analysis": True,
        "review_analysis": False,
        "external_tools": False,
        "requires_manifest": True,
        "research_eligible": False,
    },
    REVIEW_RANGE: {
        "description": "Git/base-to-head review-process findings only.",
        "rules": REVIEW_RULES,
        "source_analysis": False,
        "review_analysis": True,
        "external_tools": False,
        "requires_manifest": False,
        "research_eligible": False,
    },
}


def profile_definition(name: str) -> dict:
    try:
        return PROFILE_DEFINITIONS[name]
    except KeyError as exc:
        raise ValueError(
            f"unknown profile {name!r}; choose one of {', '.join(PROFILE_NAMES)}"
        ) from exc


def filter_profile_findings(findings, profile: str):
    allowed = profile_definition(profile)["rules"]
    return [finding for finding in findings if finding.get("rule_id") in allowed]


def rule_family(rule_id: str) -> str:
    if rule_id in REVIEW_RULES:
        return "review-range"
    if rule_id in EXTERNAL_RULES:
        return "external-tool"
    if rule_id in RESEARCH_CORE_RULES:
        return "research-core"
    if rule_id in EXTENDED_RULES:
        return "extended-ansible"
    raise ValueError(f"rule is not assigned to a profile family: {rule_id}")


def profile_metadata(name: str) -> dict:
    definition = profile_definition(name)
    rule_ids = sorted(definition["rules"])
    rules_sha256 = hashlib.sha256(
        json.dumps(rule_ids, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "name": name,
        "description": definition["description"],
        "rule_count": len(rule_ids),
        "rule_ids": rule_ids,
        "rules_sha256": rules_sha256,
        "source_analysis": definition["source_analysis"],
        "review_analysis": definition["review_analysis"],
        "external_tools": definition["external_tools"],
        "requires_manifest": definition["requires_manifest"],
        "research_eligible": definition["research_eligible"],
        "status": definition.get("status", "operational"),
    }


def validate_profile_definitions() -> None:
    assigned = REVIEW_RULES | EXTERNAL_RULES | RESEARCH_CORE_RULES | EXTENDED_RULES
    if assigned != ALL_RULES:
        missing = sorted(ALL_RULES - assigned)
        extra = sorted(assigned - ALL_RULES)
        raise RuntimeError(f"invalid profile mapping; missing={missing}; extra={extra}")
    if RESEARCH_CORE_RULES & EXTENDED_RULES:
        raise RuntimeError("research-core and extended-ansible must be disjoint")


validate_profile_definitions()

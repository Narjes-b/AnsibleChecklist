"""Compare canonical base/head occurrences for pull-request ratcheting."""

from __future__ import annotations


def _shared_fingerprint(left, right):
    return bool(
        set(left.get("evidence_fingerprints", ()))
        & set(right.get("evidence_fingerprints", ()))
    )


def _same_semantics(left, right):
    return (
        left.get("concept_id") == right.get("concept_id")
        and left.get("scan_mode", "source") == right.get("scan_mode", "source")
        and left.get("semantic_key") == right.get("semantic_key")
    )


def _same_detector_shape(left, right):
    return (
        left.get("concept_id") != "hardcoded-secret"
        and right.get("concept_id") != "hardcoded-secret"
        and left.get("concept_id") == right.get("concept_id")
        and left.get("scan_mode", "source") == right.get("scan_mode", "source")
        and left.get("file") == right.get("file")
        and set(left.get("native_rules", ())) == set(right.get("native_rules", ()))
    )


def compare_occurrences(base_occurrences, head_occurrences):
    """Classify exact, moved, introduced, fixed, and uncertain occurrences."""
    base_remaining = {item["occurrence_id"]: item for item in base_occurrences}
    head_remaining = {item["occurrence_id"]: item for item in head_occurrences}
    unchanged = []
    for occurrence_id in sorted(set(base_remaining) & set(head_remaining)):
        unchanged.append(
            {
                "base": base_remaining.pop(occurrence_id),
                "head": head_remaining.pop(occurrence_id),
                "match": "exact",
            }
        )

    moved = []
    for head_id, head in list(head_remaining.items()):
        fingerprint_candidates = [
            (base_id, base)
            for base_id, base in base_remaining.items()
            if _shared_fingerprint(base, head)
        ]
        candidates = fingerprint_candidates
        match = "native-fingerprint"
        if not candidates:
            candidates = [
                (base_id, base)
                for base_id, base in base_remaining.items()
                if _same_semantics(base, head)
            ]
            match = "semantic"
        if len(candidates) != 1:
            continue
        base_id, base = candidates[0]
        moved.append(
            {
                "base": base_remaining.pop(base_id),
                "head": head_remaining.pop(head_id),
                "match": match,
            }
        )

    uncertain = []
    for head_id, head in list(head_remaining.items()):
        candidates = [
            (base_id, base)
            for base_id, base in base_remaining.items()
            if _same_detector_shape(base, head)
        ]
        if len(candidates) != 1:
            continue
        base_id, _ = candidates[0]
        uncertain.append(
            {
                "base": base_remaining.pop(base_id),
                "head": head_remaining.pop(head_id),
                "match": "uncertain-detector-shape",
            }
        )

    ordering = lambda item: (
        item.get("file", ""),
        item.get("line", 1),
        item.get("concept_id", ""),
    )
    return {
        "schema_version": 1,
        "introduced": sorted(head_remaining.values(), key=ordering),
        "unchanged": unchanged,
        "fixed": sorted(base_remaining.values(), key=ordering),
        "moved": moved,
        "uncertain": uncertain,
    }


def evaluate_policy(comparison, mode="observe"):
    if mode not in {"observe", "ratchet"}:
        raise ValueError("policy mode must be 'observe' or 'ratchet'")
    introduced = comparison.get("introduced", [])
    blocking = [
        item
        for item in introduced
        if item.get("concept_id") == "hardcoded-secret"
        or (mode == "ratchet" and item.get("severity") == "error")
    ]
    return {
        "mode": mode,
        "conclusion": "failure" if blocking else "success",
        "blocking_occurrence_ids": [
            item["occurrence_id"] for item in blocking
        ],
        "counts": {
            key: len(comparison.get(key, []))
            for key in ("introduced", "unchanged", "fixed", "moved", "uncertain")
        },
    }

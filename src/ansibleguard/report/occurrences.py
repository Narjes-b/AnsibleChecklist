"""Group lossless detector findings into developer-facing physical occurrences."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .overlap import overlap_policy


_SEVERITY_RANK = {"note": 0, "warning": 1, "error": 2}


def _normalized_path(value: str, repo_root=None) -> str:
    path = Path(value)
    if repo_root is not None:
        try:
            path = path.resolve().relative_to(Path(repo_root).resolve())
        except ValueError:
            path = Path(path.name)
    return path.as_posix().lstrip("./")


def _identity_message(value: str, repo_root=None) -> str:
    message = str(value or "")
    if repo_root is not None:
        root = Path(repo_root).resolve()
        for spelling in {str(root), root.as_posix()}:
            message = message.replace(spelling, "<repo>")
    return re.sub(r"\d+", "#", message.lower())


def build_occurrences(findings, repo_root=None):
    """Return canonical occurrences while retaining every contributing result."""
    grouped = {}
    for finding in findings:
        file = _normalized_path(finding.get("file", ""), repo_root)
        line = int(finding.get("line") or 1)
        concept_id = finding.get("concept_id") or finding.get("rule_id")
        scan_mode = finding.get("scan_mode", "source")
        key = (concept_id, file, line, scan_mode)
        grouped.setdefault(key, []).append(finding)

    occurrences = []
    for (concept_id, file, line, scan_mode), contributors in grouped.items():
        contributors = sorted(
            contributors,
            key=lambda item: (
                item.get("provider", "ansibleguard"),
                item.get("native_rule_id", item.get("rule_id", "")),
                item.get("message", ""),
                item.get("finding_id", ""),
            ),
        )
        policy = overlap_policy(concept_id)
        canonical_provider = policy.get("canonical_provider")
        primary = next(
            (
                item
                for item in contributors
                if item.get("provider") == canonical_provider
            ),
            contributors[0],
        )
        severity = max(
            (item.get("severity", "warning") for item in contributors),
            key=lambda value: _SEVERITY_RANK.get(value, 1),
        )
        evidence_fingerprints = sorted(
            {
                item["native_fingerprint"]
                for item in contributors
                if item.get("native_fingerprint")
            }
        )
        native_rules = sorted(
            {
                f"{item.get('provider', 'ansibleguard')}/"
                f"{item.get('native_rule_id', item.get('rule_id', 'unknown'))}"
                for item in contributors
            }
        )
        normalized_message = _identity_message(primary.get("message", ""), repo_root)
        semantic_source = "|".join(
            (
                concept_id,
                file,
                scan_mode,
                normalized_message,
                ",".join(native_rules),
                ",".join(evidence_fingerprints),
            )
        )
        semantic_key = hashlib.sha256(semantic_source.encode("utf-8")).hexdigest()
        occurrence_source = (
            f"{concept_id}|{file}|{line}|{scan_mode}|{semantic_key}"
        )
        occurrence_id = hashlib.sha256(occurrence_source.encode("utf-8")).hexdigest()
        occurrences.append(
            {
                "occurrence_id": occurrence_id,
                "concept_id": concept_id,
                "file": file,
                "line": line,
                "scan_mode": scan_mode,
                "severity": severity,
                "message": primary.get("message", ""),
                "canonical_provider": primary.get("provider", "ansibleguard"),
                "overlap": policy,
                "detector_count": len(contributors),
                "native_rules": native_rules,
                "evidence_fingerprints": evidence_fingerprints,
                "semantic_key": semantic_key,
                "detectors": [
                    {
                        key: item[key]
                        for key in (
                            "finding_id",
                            "provider",
                            "rule_id",
                            "native_rule_id",
                            "native_severity",
                            "native_fingerprint",
                            "scan_mode",
                            "message",
                        )
                        if key in item
                    }
                    for item in contributors
                ],
            }
        )
    return sorted(
        occurrences,
        key=lambda item: (
            item["file"],
            item["line"],
            item["concept_id"],
            item["occurrence_id"],
        ),
    )


def occurrence_findings(occurrences):
    """Adapt canonical occurrences to the normalized finding/SARIF contract."""
    return [
        {
            "file": occurrence["file"],
            "line": occurrence["line"],
            "rule_id": occurrence["concept_id"],
            "severity": occurrence["severity"],
            "message": occurrence["message"],
            "provider": "ansibleguard-canonical",
            "native_rule_id": occurrence["concept_id"],
            "concept_id": occurrence["concept_id"],
            "finding_id": occurrence["occurrence_id"],
            "detectors": occurrence["detectors"],
        }
        for occurrence in occurrences
    ]

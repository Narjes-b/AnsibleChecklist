"""Group lossless detector findings into developer-facing physical occurrences."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .findings import (
    finding_actionability,
    finding_catalog_metadata,
    finding_category,
    finding_maturity,
    finding_policy,
    finding_taxonomy,
)
from .overlap import overlap_policy
from .llm_explain import ASSESSMENT_FIELDS


_SEVERITY_RANK = {"note": 0, "warning": 1, "error": 2}


def _normalized_path(value: str, repo_root=None) -> str:
    path = Path(value)
    if not path.is_absolute():
        return path.as_posix().removeprefix("./")
    if repo_root is not None:
        try:
            path = path.resolve().relative_to(Path(repo_root).resolve())
        except ValueError:
            path = Path(path.name)
    return path.as_posix().removeprefix("./")


def _semantic_subject(finding) -> str:
    """Return a conservative subject key for same-location deduplication."""
    subject = None
    for key in ("semantic_subject", "variable", "attribute", "module"):
        if finding.get(key):
            subject = f"{key}:{finding[key]}"
            break
    if subject is None:
        message = str(finding.get("message") or "")
        for label, pattern in (
            ("variable", r"\bVariable ['\"]([^'\"]+)['\"]"),
            ("attribute", r"\battribute ['\"]([^'\"]+)['\"]"),
            ("task", r"\bTask ['\"]([^'\"]+)['\"]"),
        ):
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                subject = f"{label}:{match.group(1).strip().lower()}"
                break
    task_context = finding.get("task_fingerprint")
    if not task_context and finding.get("task_name"):
        task_context = str(finding["task_name"]).strip().lower()
    if task_context:
        task_part = f"task:{task_context}"
        return f"{subject}|{task_part}" if subject else task_part
    return subject or "location"


def build_occurrences(findings, repo_root=None):
    """Return canonical occurrences while retaining every contributing result."""
    grouped = {}
    for finding in findings:
        file = _normalized_path(finding.get("file", ""), repo_root)
        line = int(finding.get("line") or 1)
        concept_id = finding.get("concept_id") or finding.get("rule_id")
        scan_mode = finding.get("scan_mode", "source")
        # GitLeaks directory scans and internal source analysis describe the
        # same checkout population. Keep history/range findings distinct, but
        # permit source-vs-directory provider evidence to merge.
        dedup_scan_mode = "source" if scan_mode in {"source", "dir"} else scan_mode
        semantic_subject = _semantic_subject(finding)
        key = (concept_id, file, line, dedup_scan_mode, semantic_subject)
        grouped.setdefault(key, []).append(finding)

    occurrences = []
    for (
        concept_id, file, line, dedup_scan_mode, semantic_subject
    ), contributors in grouped.items():
        contributors = sorted(
            contributors,
            key=lambda item: (
                item.get("provider", "ansibleguard"),
                item.get("native_rule_id", item.get("rule_id", "")),
                item.get("message", ""),
                item.get("finding_id", ""),
            ),
        )
        # The same finding may reach aggregation through multiple detector
        # paths. Preserve distinct provider/rule evidence, but remove exact
        # repeated copies before calculating detector_count or writing SARIF.
        unique_contributors = {}
        for item in contributors:
            identity = (
                item.get("finding_id", ""),
                item.get("provider", "ansibleguard"),
                item.get("native_rule_id", item.get("rule_id", "")),
                item.get("file", ""),
                int(item.get("line") or 1),
                item.get("message", ""),
            )
            unique_contributors.setdefault(identity, item)
        contributors = list(unique_contributors.values())
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
        reported_scan_mode = primary.get("scan_mode", dedup_scan_mode)
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
        # Semantic identity deliberately excludes provider wording, native rule
        # IDs and native fingerprints. Those describe evidence for a defect,
        # not the defect itself, and may change between provider releases.
        semantic_source = "|".join(
            (
                concept_id,
                file,
                dedup_scan_mode,
                semantic_subject,
            )
        )
        semantic_key = hashlib.sha256(semantic_source.encode("utf-8")).hexdigest()
        task_fingerprints = {
            str(item["task_fingerprint"])
            for item in contributors
            if item.get("task_fingerprint")
        }
        task_fingerprint = (
            next(iter(task_fingerprints))
            if len(task_fingerprints) == 1 else ""
        )
        content_semantic_source = "|".join(
            (
                concept_id,
                dedup_scan_mode,
                semantic_subject,
                task_fingerprint,
            )
        )
        content_semantic_key = hashlib.sha256(
            content_semantic_source.encode("utf-8")
        ).hexdigest()
        occurrence_source = (
            f"{concept_id}|{file}|{line}|{dedup_scan_mode}|{semantic_key}"
        )
        occurrence_id = hashlib.sha256(occurrence_source.encode("utf-8")).hexdigest()
        provider_evidence_source = "|".join(
            sorted(
                "|".join(
                    (
                        str(item.get("provider", "ansibleguard")),
                        str(item.get("native_rule_id", item.get("rule_id", ""))),
                        str(item.get("native_fingerprint", "")),
                        str(item.get("message", "")),
                    )
                )
                for item in contributors
            )
        )
        provider_evidence_fingerprint = hashlib.sha256(
            provider_evidence_source.encode("utf-8")
        ).hexdigest()
        occurrence = {
                "occurrence_id": occurrence_id,
                "concept_id": concept_id,
                "file": file,
                "line": line,
                "scan_mode": reported_scan_mode,
                "severity": severity,
                "message": primary.get("message", ""),
                "canonical_provider": primary.get("provider", "ansibleguard"),
                "overlap": policy,
                "detector_count": len(contributors),
                "native_rules": native_rules,
                "evidence_fingerprints": evidence_fingerprints,
                "semantic_key": semantic_key,
                "content_semantic_key": content_semantic_key,
                "provider_evidence_fingerprint": provider_evidence_fingerprint,
                "semantic_subject": semantic_subject,
                **(
                    {"task_fingerprint": task_fingerprint}
                    if task_fingerprint else {}
                ),
                "analysis_population": primary.get(
                    "analysis_population", "classification_suspect"
                ),
                "analysis_populations": sorted({
                    item.get("analysis_population", "classification_suspect")
                    for item in contributors
                }),
                "source_population": primary.get("source_population", "unknown"),
                "classification_confidence": primary.get(
                    "classification_confidence", "low"
                ),
                "semantic_status": primary.get("semantic_status", "CONFIRMED"),
                "resolution_status": primary.get(
                    "resolution_status", "DETECTOR_RESULT"
                ),
                "resolution_scope": primary.get(
                    "resolution_scope", "rule-static"
                ),
                "resolution_evidence": primary.get("resolution_evidence", {}),
                **(
                    {
                        "variable_classification": primary[
                            "variable_classification"
                        ]
                    }
                    if primary.get("variable_classification")
                    else {}
                ),
                **(
                    {"legacy_concept_id": primary["legacy_concept_id"]}
                    if primary.get("legacy_concept_id")
                    else {}
                ),
                "uncertainty_sources": sorted({
                    source
                    for item in contributors
                    for source in item.get("uncertainty_sources", [])
                }),
                "confidence_factors": primary.get("confidence_factors", {}),
                "known_limitations": primary.get("known_limitations", []),
                "rule_uncertainty_sources": primary.get(
                    "rule_uncertainty_sources", []
                ),
                "sensitive_class": primary.get("sensitive_class"),
                "evidence_level": primary.get("evidence_level"),
                "secret_population": primary.get("secret_population"),
                "secret_context": primary.get("secret_context"),
                "secret_context_factors": primary.get(
                    "secret_context_factors", {}
                ),
                "native_policies": sorted({
                    item["native_policy"]
                    for item in contributors
                    if item.get("native_policy")
                }),
                "policy_adjusted": any(
                    item.get("policy_adjusted") is True for item in contributors
                ),
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
                            "native_policy",
                            "policy_adjusted",
                            "scan_mode",
                            "message",
                        )
                        if key in item
                    }
                    for item in contributors
                ],
            }
        occurrence["finding_category"] = finding_category(occurrence)
        occurrence["policy"] = finding_policy(occurrence)
        occurrence["taxonomy"] = finding_taxonomy(occurrence)
        occurrence["actionability"] = finding_actionability(occurrence)
        occurrence["rule_maturity"] = finding_maturity(occurrence)
        metadata = finding_catalog_metadata(occurrence)
        occurrence["confidence"] = primary.get(
            "confidence", metadata.get("confidence", "medium")
        )
        if occurrence["policy_adjusted"]:
            occurrence["confidence"] = "low"
        if occurrence["semantic_status"] == "UNCERTAIN":
            occurrence["confidence"] = "low"
            occurrence["policy"] = "optional"
            occurrence["taxonomy"] = "OPTIONAL_PRACTICE"
            occurrence["actionability"] = (
                "informational"
                if occurrence["concept_id"] == "unresolved-runtime-input"
                else "advisory"
            )
        occurrence["remediation"] = metadata.get(
            "remediation",
            primary.get("remediation", "Review the finding in project context."),
        )
        occurrences.append(occurrence)
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
    findings = []
    for occurrence in occurrences:
        finding = {
            "file": occurrence["file"],
            "line": occurrence["line"],
            "rule_id": occurrence["concept_id"],
            "severity": occurrence["severity"],
            "message": occurrence["message"],
            "provider": "ansibleguard-canonical",
            "native_rule_id": occurrence["concept_id"],
            "concept_id": occurrence["concept_id"],
            "finding_id": occurrence["occurrence_id"],
            "semantic_key": occurrence.get("semantic_key"),
            "evidence_fingerprints": occurrence.get("evidence_fingerprints", []),
            "detectors": occurrence["detectors"],
        }
        for key in (
            "finding_category", "policy", "confidence", "remediation",
            "native_policies", "policy_adjusted", "analysis_population",
            "analysis_populations", "source_population",
            "classification_confidence",
            "taxonomy", "actionability", "rule_maturity",
            "semantic_subject",
            "task_fingerprint",
            "content_semantic_key",
            "provider_evidence_fingerprint",
            "semantic_status", "uncertainty_sources", "confidence_factors",
            "resolution_status", "resolution_scope", "resolution_evidence",
            "variable_classification", "legacy_concept_id",
            "known_limitations", "rule_uncertainty_sources",
            "sensitive_class", "evidence_level",
            "secret_population", "secret_context", "secret_context_factors",
            "llm_status", "llm_error", "llm_model", "llm_explanation",
            "llm_why_in_this_context", "llm_suggested_fix",
            "llm_fixed_code_snippet", "llm_confidence", "llm_limitations",
            "llm_duration_seconds", "llm_disclaimer",
            *ASSESSMENT_FIELDS,
        ):
            if key in occurrence:
                finding[key] = occurrence[key]
        findings.append(finding)
    return findings

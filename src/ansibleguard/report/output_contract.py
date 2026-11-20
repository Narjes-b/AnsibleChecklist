"""Write the versioned, organized output contract and compatibility aliases."""

from __future__ import annotations

from collections import Counter
import csv
from importlib.resources import files
import json
from pathlib import Path

from .csv_writer import write_findings_to_csv
from .findings import finding_category
from .occurrences import build_occurrences, occurrence_findings
from .llm_explain import STRUCTURED_FIELDS, ASSESSMENT_FIELDS, DEFAULT_HOST, DEFAULT_MODEL, assessment_text, enrich_occurrences_with_explanations
from .sarif_writer import write_sarif
from .text_writer import write_findings_to_txt


SCHEMA_VERSION = 3
CONTRACT_URI = "ansibleguard://schemas/output-v3.json"
SCHEMA_ARTIFACT = "schemas/output-v3.json"
SCHEMA_RESOURCE = "schemas/output-v3.json"
SUPPORTED_SCHEMA_VERSIONS = frozenset({SCHEMA_VERSION})
SUPPORTED_KINDS = frozenset({
    "contract-manifest", "run-metadata", "file-selection", "raw-findings",
    "suppressed-external-findings", "canonical-occurrences", "diagnostics",
    "review-metrics", "file-metrics", "file-report", "run-report",
    "legacy-layout", "diff-report", "pr-comparison",
    "introduced-occurrences", "fixed-occurrences", "playbook-summary",
})
ITEM_REQUIRED_FIELDS = {
    "raw-findings": frozenset(
        {"finding_id", "rule_id", "provider", "file", "line", "severity", "message"}
    ),
    "suppressed-external-findings": frozenset(
        {"finding_id", "rule_id", "provider", "file", "line", "severity", "message"}
    ),
    "canonical-occurrences": frozenset(
        {
            "occurrence_id", "concept_id", "file", "line", "scan_mode",
            "severity", "message", "semantic_key", "content_semantic_key",
            "semantic_subject", "provider_evidence_fingerprint", "detectors",
        }
    ),
    "diagnostics": frozenset({"file", "stage", "status", "message"}),
}
ITEM_STRING_FIELDS = {
    "raw-findings": frozenset(
        {"finding_id", "rule_id", "provider", "file", "severity", "message"}
    ),
    "suppressed-external-findings": frozenset(
        {"finding_id", "rule_id", "provider", "file", "severity", "message"}
    ),
    "canonical-occurrences": frozenset({
        "occurrence_id", "concept_id", "file", "scan_mode", "severity",
        "message", "semantic_key", "content_semantic_key", "semantic_subject",
        "provider_evidence_fingerprint", "task_fingerprint",
    }),
    "diagnostics": frozenset({"file", "stage", "status", "message"}),
}
SUMMARY_FIELDS = (
    "file",
    "file_class",
    "ansible_artifact_kind",
    "parse_status",
    "document_type",
    "structural_status",
    "gitleaks_status",
    "ansible_lint_status",
    "errors",
    "warnings",
    "notes",
    "total",
    "raw_findings",
    "canonical_occurrences",
    "ansibleguard_findings",
    "ansible_lint_findings",
    "gitleaks_findings",
    "new_pr_findings",
    "new_pr_actionable_findings",
    "new_pr_optional_findings",
    "new_pr_findings_by_category",
    "pr_comparison_status",
)
OCCURRENCE_FIELDS = (
    "schema_version",
    "occurrence_id",
    "concept_id",
    "file",
    "line",
    "scan_mode",
    "severity",
    "confidence",
    "analysis_population",
    "source_population",
    "classification_confidence",
    "taxonomy",
    "actionability",
    "rule_maturity",
    "finding_category",
    "policy",
    "message",
    "remediation",
    "canonical_provider",
    "detector_count",
    "native_rules",
    "evidence_fingerprints",
    "semantic_key",
    "semantic_subject",
    "task_fingerprint",
    "content_semantic_key",
    "provider_evidence_fingerprint",
    "llm_status",
    *ASSESSMENT_FIELDS,
    "llm_explanation",
    "llm_why_in_this_context",
    "llm_suggested_fix",
    "llm_fixed_code_snippet",
    "llm_confidence",
    "llm_limitations",
    "llm_disclaimer",
)


def _relative_path(value, repo_root):
    path = Path(value)
    if not path.is_absolute():
        return path.as_posix().removeprefix("./") or "."
    try:
        return path.resolve().relative_to(Path(repo_root).resolve()).as_posix()
    except ValueError:
        return path.as_posix().removeprefix("./") or "."


def _envelope(kind, items, **extra):
    return {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": kind,
        "items": items,
        **extra,
    }


def load_contract_schema():
    """Load the canonical packaged schema independently of the current cwd."""
    resource = files("ansibleguard.report").joinpath(SCHEMA_RESOURCE)
    return json.loads(resource.read_text(encoding="utf-8"))


def write_contract_schema(output_root):
    """Copy the packaged schema beside an output contract and return its path."""
    target = Path(output_root) / SCHEMA_ARTIFACT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(load_contract_schema(), indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def validate_contract_payload(payload, *, expected_kind=None):
    """Validate a v0.0.5 JSON envelope before treating it as canonical data."""
    if not isinstance(payload, dict):
        raise ValueError("output contract payload must be an object")
    version = payload.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(f"unsupported output schema version: {version!r}")
    if payload.get("contract") != CONTRACT_URI:
        raise ValueError("output contract URI does not match the supported schema")
    if payload.get("kind") not in SUPPORTED_KINDS:
        raise ValueError(f"unsupported output kind: {payload.get('kind')!r}")
    if expected_kind is not None and payload.get("kind") != expected_kind:
        raise ValueError(
            f"expected output kind {expected_kind!r}, got {payload.get('kind')!r}"
        )
    kind = payload.get("kind")
    required = ITEM_REQUIRED_FIELDS.get(kind)
    if required is not None:
        items = payload.get("items")
        if not isinstance(items, list):
            raise ValueError(f"output kind {kind!r} requires an items array")
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"{kind} item {index} must be an object")
            missing = sorted(required - item.keys())
            if missing:
                raise ValueError(
                    f"{kind} item {index} is missing required fields: "
                    + ", ".join(missing)
                )
            for field in ITEM_STRING_FIELDS[kind]:
                if field in item and not isinstance(item[field], str):
                    raise ValueError(
                        f"{kind} item {index} field {field!r} must be a string"
                    )
            if "line" in item and (
                not isinstance(item["line"], int)
                or isinstance(item["line"], bool)
                or item["line"] < 1
            ):
                raise ValueError(
                    f"{kind} item {index} field 'line' must be a positive integer"
                )
            if item.get("severity") not in {None, "error", "warning", "note"}:
                raise ValueError(
                    f"{kind} item {index} has an invalid severity"
                )
            if kind == "canonical-occurrences":
                detectors = item["detectors"]
                if not isinstance(detectors, list):
                    raise ValueError(
                        f"{kind} item {index} field 'detectors' must be an array"
                    )
                if any(
                    not isinstance(detector, dict)
                    or not isinstance(detector.get("provider"), str)
                    or not detector["provider"]
                    for detector in detectors
                ):
                    raise ValueError(
                        f"{kind} item {index} has invalid provider evidence"
                    )
    return payload


def _write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_run_summary(path, report, run_metadata):
    """Write a compact trust/completeness panel before finding details."""
    tools = report.get("tools", {})
    scope = run_metadata.get("analysis_scope", {}).get("internal", {})
    versions = run_metadata.get("reproducibility", {})
    counts = report.get("counts", {})
    lines = [
        "# AnsibleGuard scan trust summary",
        "",
        f"- Run status: **{report.get('status', 'unknown')}**",
        f"- Profile: `{report.get('profile', 'unknown')}`",
        f"- Selected files: {scope.get('selected_files', 0)}",
        f"- Processed source files: {scope.get('processed_files', 0)}",
        f"- Structurally analyzed files: {scope.get('structurally_analyzed_files', 0)}",
        f"- Raw findings: {counts.get('raw_findings', 0)}",
        f"- Canonical occurrences: {counts.get('canonical_occurrences', 0)}",
        f"- Suppressed external findings: {counts.get('suppressed_external_findings', 0)}",
        f"- ansible-lint: **{tools.get('ansible_lint', 'not-requested')}** "
        f"(version `{versions.get('ansible_lint_version') or 'unknown'}`)",
        f"- GitLeaks: **{tools.get('gitleaks', 'not-requested')}** "
        f"(version `{versions.get('gitleaks_version') or 'unknown'}`)",
        f"- AnsibleGuard: `{versions.get('ansibleguard_version') or 'unknown'}` "
        f"at `{versions.get('ansibleguard_git_sha') or 'unknown'}`",
        f"- Target commit: `{versions.get('target_git_sha') or 'not-a-git-checkout'}`",
        "",
        "A completed policy result and complete execution are separate facts. "
        "Inspect diagnostics and provider status before treating zero findings as clean.",
        "",
    ]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_summary(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _status_value(rows, field, default):
    values = [row.get(field) for row in rows if row.get(field)]
    if not values:
        return default
    priorities = {
        "read-error": 5,
        "invalid": 4,
        "parsed": 3,
        "unsupported": 2,
        "not-applicable": 1,
        "analyzed": 3,
        "skipped": 2,
        "partial": 4,
        "failed": 5,
    }
    return max(values, key=lambda value: priorities.get(value, 0))


def _selection_categories(selection_metadata):
    manifest = selection_metadata.get("manifest") if selection_metadata else None
    if not manifest:
        return {}
    try:
        with Path(manifest).open(newline="", encoding="utf-8") as stream:
            return {
                row["path"].replace("\\", "/"): {
                    "file_class": row.get("file_class") or "unclassified",
                    "ansible_artifact_kind": (
                        row.get("ansible_artifact_kind")
                        or row.get("document_type")
                        or "unclassified"
                    ),
                }
                for row in csv.DictReader(stream)
            }
    except OSError:
        return {}


def build_summary_rows(
    summary_rows, findings, occurrences, repo_root, file_categories=None
):
    """Build one enriched row per file from raw and canonical evidence."""
    source_rows = {}
    for row in summary_rows:
        source_rows.setdefault(row["file"].replace("\\", "/"), []).append(row)

    raw_by_file = {}
    for finding in findings:
        file = _relative_path(finding.get("file", "."), repo_root)
        raw_by_file.setdefault(file, []).append(finding)
    occurrences_by_file = {}
    for occurrence in occurrences:
        occurrences_by_file.setdefault(occurrence["file"], []).append(occurrence)

    files = sorted(set(source_rows) | set(raw_by_file) | set(occurrences_by_file))
    enriched = []
    file_categories = file_categories or {}
    for file in files:
        rows = source_rows.get(file, [])
        raw = raw_by_file.get(file, [])
        canonical = occurrences_by_file.get(file, [])
        severity = Counter(item.get("severity", "warning") for item in raw)
        providers = Counter(item.get("provider", "ansibleguard") for item in raw)
        category = file_categories.get(file, {})
        file_class = category.get("file_class") or (
            "non-yaml" if any(row.get("document_type") == "non-yaml" for row in rows)
            else "unclassified"
        )
        artifact_kind = category.get("ansible_artifact_kind") or _status_value(
            rows, "document_type", "unclassified"
        )
        enriched.append(
            {
                "file": file,
                "file_class": file_class,
                "ansible_artifact_kind": artifact_kind,
                "parse_status": _status_value(rows, "parse_status", "not-applicable"),
                "document_type": _status_value(
                    rows, "document_type", "not-applicable"
                ),
                "structural_status": _status_value(
                    rows, "structural_status", "not-applicable"
                ),
                "gitleaks_status": _status_value(
                    rows, "gitleaks_status", "not-applicable"
                ),
                "ansible_lint_status": _status_value(
                    rows, "ansible_lint_status", "not-applicable"
                ),
                "errors": severity["error"],
                "warnings": severity["warning"],
                "notes": severity["note"],
                "total": len(raw),
                "raw_findings": len(raw),
                "canonical_occurrences": len(canonical),
                "ansibleguard_findings": providers["ansibleguard"],
                "ansible_lint_findings": providers["ansible-lint"],
                "gitleaks_findings": providers["gitleaks"],
                "new_pr_findings": "",
                "new_pr_actionable_findings": "",
                "new_pr_optional_findings": "",
                "new_pr_findings_by_category": "",
                "pr_comparison_status": "not-compared",
            }
        )
    return sorted(
        enriched,
        key=lambda row: (-row["errors"], -row["warnings"], -row["total"], row["file"]),
    )


def write_occurrences_csv(occurrences, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OCCURRENCE_FIELDS)
        writer.writeheader()
        for occurrence in occurrences:
            row = {
                field: occurrence.get(field, "")
                for field in OCCURRENCE_FIELDS
            }
            row["schema_version"] = SCHEMA_VERSION
            row["native_rules"] = json.dumps(occurrence.get("native_rules", []))
            row["evidence_fingerprints"] = json.dumps(
                occurrence.get("evidence_fingerprints", [])
            )
            for field in STRUCTURED_FIELDS:
                if field in occurrence:
                    row[field] = json.dumps(occurrence[field], ensure_ascii=False)
            writer.writerow(row)


def write_occurrences_text(occurrences, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        stream.write(
            f"### CANONICAL OCCURRENCES (SCHEMA {SCHEMA_VERSION}) ###\n\n"
        )
        if not occurrences:
            stream.write("No canonical occurrences detected.\n")
            return
        for occurrence in occurrences:
            rules = ", ".join(occurrence.get("native_rules", []))
            stream.write(
                f"- [{occurrence['severity']}] {occurrence['concept_id']} at "
                f"{occurrence['file']}:{occurrence['line']}: "
                f"{occurrence['message']} "
                f"(canonical={occurrence['canonical_provider']}; "
                f"detectors={occurrence['detector_count']}; rules={rules}; "
                f"confidence={occurrence.get('confidence', 'medium')})\n"
            )
            if occurrence.get("remediation"):
                stream.write(f"  Fix: {occurrence['remediation']}\n")
            assessment = assessment_text(occurrence)
            if assessment:
                stream.write(f"  {assessment}\n")
            elif occurrence.get("llm_status") == "ok" and occurrence.get("llm_suggested_fix"):
                stream.write(
                    f"  AI suggestion (unverified): {occurrence['llm_suggested_fix']}\n"
                )
                if occurrence.get("llm_disclaimer"):
                    stream.write(f"    ({occurrence['llm_disclaimer']})\n")


def _finding_category(occurrence):
    return finding_category(occurrence)


def _nested_counts(occurrences, file_metadata, file_key):
    nested = {}
    for occurrence in occurrences:
        file_value = file_metadata.get(occurrence.get("file"), {}).get(
            file_key, "unclassified"
        )
        category = _finding_category(occurrence)
        nested.setdefault(file_value, Counter())[category] += 1
    return {
        key: dict(sorted(value.items())) for key, value in sorted(nested.items())
    }


def _counts(findings, occurrences, summary_rows):
    file_metadata = {
        row["file"]: {
            "file_class": row.get("file_class", "unclassified"),
            "ansible_artifact_kind": row.get(
                "ansible_artifact_kind", "unclassified"
            ),
        }
        for row in summary_rows
    }
    return {
        "files": len(summary_rows),
        "files_by_class": dict(
            sorted(Counter(row.get("file_class", "unclassified") for row in summary_rows).items())
        ),
        "files_by_artifact_kind": dict(
            sorted(Counter(row.get("ansible_artifact_kind", "unclassified") for row in summary_rows).items())
        ),
        "raw_findings": len(findings),
        "canonical_occurrences": len(occurrences),
        "raw_by_severity": dict(
            sorted(Counter(item["severity"] for item in findings).items())
        ),
        "canonical_by_severity": dict(
            sorted(Counter(item["severity"] for item in occurrences).items())
        ),
        "raw_by_provider": dict(
            sorted(
                Counter(
                    item.get("provider", "ansibleguard") for item in findings
                ).items()
            )
        ),
        "canonical_by_concept": dict(
            sorted(Counter(item["concept_id"] for item in occurrences).items())
        ),
        "canonical_by_finding_category": dict(
            sorted(Counter(_finding_category(item) for item in occurrences).items())
        ),
        "canonical_by_file_class": dict(
            sorted(
                Counter(
                    file_metadata.get(item.get("file"), {}).get(
                        "file_class", "unclassified"
                    )
                    for item in occurrences
                ).items()
            )
        ),
        "canonical_by_artifact_kind": dict(
            sorted(
                Counter(
                    file_metadata.get(item.get("file"), {}).get(
                        "ansible_artifact_kind", "unclassified"
                    )
                    for item in occurrences
                ).items()
            )
        ),
        "canonical_by_file_class_and_finding_category": _nested_counts(
            occurrences, file_metadata, "file_class"
        ),
        "canonical_by_artifact_kind_and_finding_category": _nested_counts(
            occurrences, file_metadata, "ansible_artifact_kind"
        ),
    }


def _run_status(diagnostics, summary_rows):
    analysis_errors = [
        item for item in diagnostics if item.get("status") == "analysis-error"
    ]
    if analysis_errors:
        source_states = {
            row.get("structural_status")
            for row in summary_rows
            if row.get("structural_status") not in {None, "not-applicable"}
        }
        return (
            "failed"
            if not source_states or source_states <= {"failed"}
            else "partial"
        )
    if any(
        item.get("status") in {
            "provider-error", "provider-schema-error", "provider-environment-error",
            "timeout",
        }
        for item in diagnostics
    ):
        return "partial"
    if any(
        item.get("status") in {"invalid", "invalid-encoding", "read-error"}
        for item in diagnostics
    ):
        return "partial"
    return "completed-with-diagnostics" if diagnostics else "completed"


def _write_per_file_v3(output_root, rows, findings, occurrences, diagnostics, repo_root):
    """Write one predictable JSON-only bundle for every source file."""
    files_root = Path(output_root) / "files"
    for row in rows:
        file = row["file"]
        if file in {"", "."}:
            continue
        bundle = files_root / file
        raw = [
            item for item in findings
            if _relative_path(item.get("file", "."), repo_root) == file
        ]
        canonical = [item for item in occurrences if item.get("file") == file]
        canonical_categories = dict(
            sorted(Counter(_finding_category(item) for item in canonical).items())
        )
        file_diagnostics = [item for item in diagnostics if item.get("file") == file]
        _write_json(bundle / "findings.json", _envelope("raw-findings", raw, file=file))
        _write_json(bundle / "occurrences.json", _envelope("canonical-occurrences", canonical, file=file))
        _write_json(bundle / "diagnostics.json", _envelope("diagnostics", file_diagnostics, file=file))
        _write_json(
            bundle / "metrics.json",
            {
                "schema_version": SCHEMA_VERSION,
                "contract": CONTRACT_URI,
                "kind": "file-metrics",
                "file": file,
                "file_class": row["file_class"],
                "ansible_artifact_kind": row["ansible_artifact_kind"],
                "counts": {
                    "raw_findings": len(raw),
                    "canonical_occurrences": len(canonical),
                    "errors": row["errors"],
                    "warnings": row["warnings"],
                    "notes": row["notes"],
                    "canonical_by_finding_category": canonical_categories,
                },
            },
        )
        _write_json(
            bundle / "report.json",
            {
                "schema_version": SCHEMA_VERSION,
                "contract": CONTRACT_URI,
                "kind": "file-report",
                "file": file,
                "file_class": row["file_class"],
                "ansible_artifact_kind": row["ansible_artifact_kind"],
                "status": row["structural_status"],
                "parse_status": row["parse_status"],
                "document_type": row["document_type"],
                "counts": {
                    **{key: row[key] for key in ("errors", "warnings", "notes", "raw_findings", "canonical_occurrences")},
                    "canonical_by_finding_category": canonical_categories,
                },
                "artifacts": {
                    "findings": "findings.json",
                    "occurrences": "occurrences.json",
                    "diagnostics": "diagnostics.json",
                    "metrics": "metrics.json",
                },
            },
        )


def write_rollups_v3(
    findings,
    summary_rows,
    diagnostics,
    project_metrics,
    output_root,
    repo_root,
    selection_metadata,
    run_metadata,
    suppressed_external_findings=None,
    explain=False,
    explain_model=None,
    explain_host=None,
    explain_max_items=None,
    explain_timeout=120.0,
    explain_budget=600.0,
    explain_checkpoint_dir=None,
    explain_style="free",
):
    """Write v3 organized output plus one-release root compatibility files."""
    output_root = Path(output_root)
    suppressed_external_findings = list(suppressed_external_findings or [])
    summary_dir = output_root / "summary"
    raw_dir = output_root / "raw"
    canonical_dir = output_root / "canonical"
    metadata_dir = output_root / "metadata"
    legacy_dir = output_root / "legacy"
    for directory in (
        summary_dir,
        raw_dir,
        canonical_dir,
        metadata_dir,
        legacy_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    write_contract_schema(output_root)

    occurrences = build_occurrences(findings, repo_root=repo_root)
    if explain:
        # Opt-in only (ansibleguard <target> --explain): enriches occurrences
        # in place with llm_* fields, which write_occurrences_csv/_text,
        # write_sarif (via occurrence_findings) and OCCURRENCE_FIELDS already
        # carry through to every output format below. Never raises -- a
        # missing/slow model degrades to no enrichment, not a failed scan.
        enrich_occurrences_with_explanations(
            occurrences,
            repo_root,
            model=explain_model or DEFAULT_MODEL,
            host=explain_host or DEFAULT_HOST,
            max_items=explain_max_items,
            timeout=explain_timeout,
            budget=explain_budget,
            checkpoint_dir=explain_checkpoint_dir,
            explanation_style=explain_style,
        )
    enriched_summary = build_summary_rows(
        summary_rows,
        findings,
        occurrences,
        repo_root,
        _selection_categories(selection_metadata),
    )
    _write_per_file_v3(
        output_root, enriched_summary, findings, occurrences, diagnostics, repo_root
    )

    # Compatibility files at the output root.
    _write_summary(output_root / "summary.csv", enriched_summary)
    _write_json(output_root / "findings.json", findings)
    _write_json(output_root / "findings.raw.json", findings)
    _write_json(output_root / "occurrences.json", occurrences)
    write_findings_to_csv(findings, output_root / "findings.csv")
    write_findings_to_txt(findings, output_root / "findings.txt")
    _write_json(output_root / "review_metrics.json", project_metrics)
    _write_json(output_root / "diagnostics.json", diagnostics)
    _write_json(
        output_root / "gitleaks-suppressed.json",
        suppressed_external_findings,
    )

    selection_envelope = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "file-selection",
        **selection_metadata,
    }
    run_envelope = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "run-metadata",
        **run_metadata,
    }
    _write_json(output_root / "file_selection.json", selection_envelope)
    _write_json(output_root / "run_metadata.json", run_envelope)
    _write_json(
        output_root / "contract.json",
        {
            "schema_version": SCHEMA_VERSION,
            "contract": CONTRACT_URI,
            "kind": "contract-manifest",
            "supported_schema_versions": sorted(SUPPORTED_SCHEMA_VERSIONS),
            "schema_artifact": SCHEMA_ARTIFACT,
            "canonical_artifacts": {
                "raw_findings": "raw/findings.json",
                "canonical_occurrences": "canonical/occurrences.json",
                "run_metadata": "metadata/run.json",
            },
        },
    )

    root_sarif = output_root / "findings.sarif"
    write_sarif(occurrence_findings(occurrences), root_sarif, repo_root=repo_root)

    # Authoritative organized v3 contract.
    _write_summary(summary_dir / "summary.csv", enriched_summary)
    _write_json(
        summary_dir / "diagnostics.json",
        _envelope("diagnostics", diagnostics),
    )
    _write_json(
        raw_dir / "findings.json",
        _envelope("raw-findings", findings),
    )
    _write_json(
        raw_dir / "suppressed-external-findings.json",
        _envelope(
            "suppressed-external-findings",
            suppressed_external_findings,
            policy={
                "name": "built-in-known-noise",
                "evidence_retained": True,
                "secrets_redacted": True,
            },
        ),
    )
    write_findings_to_csv(
        findings, raw_dir / "findings.csv", include_schema_version=True
    )
    write_findings_to_txt(
        findings,
        raw_dir / "findings.txt",
        title=f"Raw provider findings (schema {SCHEMA_VERSION})",
    )
    _write_json(
        canonical_dir / "occurrences.json",
        _envelope("canonical-occurrences", occurrences),
    )
    write_occurrences_csv(occurrences, canonical_dir / "occurrences.csv")
    write_occurrences_text(occurrences, canonical_dir / "occurrences.txt")
    write_sarif(
        occurrence_findings(occurrences),
        canonical_dir / "findings.sarif",
        repo_root=repo_root,
    )
    _write_json(metadata_dir / "run.json", run_envelope)
    _write_json(metadata_dir / "file-selection.json", selection_envelope)
    _write_json(
        metadata_dir / "review-metrics.json",
        {
            "schema_version": SCHEMA_VERSION,
            "contract": CONTRACT_URI,
            "kind": "review-metrics",
            "metrics": project_metrics,
        },
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "run-report",
        "status": run_metadata.get("analysis_health", {}).get("status")
        or _run_status(diagnostics, enriched_summary),
        "profile": run_metadata["profile"]["name"],
        "target": run_metadata["target"],
        "tools": run_metadata["tools"],
        "counts": _counts(findings, occurrences, enriched_summary),
        "analysis_scope": run_metadata.get("analysis_scope", {}),
        "analysis_health": run_metadata.get("analysis_health", {}),
        "timings": run_metadata.get("timings", {}),
        "performance": run_metadata.get("performance", {}),
        "reproducibility": run_metadata.get("reproducibility", {}),
        "pr_comparison": {
            "status": "not-compared",
            "introduced": None,
            "policy_conclusion": None,
        },
        "artifacts": {
            "contract": "contract.json",
            "summary": "summary/summary.csv",
            "trust_summary": "summary/run-summary.md",
            "diagnostics": "summary/diagnostics.json",
            "raw_json": "raw/findings.json",
            "raw_csv": "raw/findings.csv",
            "raw_text": "raw/findings.txt",
            "suppressed_external": "raw/suppressed-external-findings.json",
            "canonical_json": "canonical/occurrences.json",
            "canonical_csv": "canonical/occurrences.csv",
            "canonical_text": "canonical/occurrences.txt",
            "sarif": "canonical/findings.sarif",
            "run_metadata": "metadata/run.json",
            "file_selection": "metadata/file-selection.json",
            "review_metrics": "metadata/review-metrics.json",
            "per_file": "files/<repository-relative-path>/",
        },
        "compatibility": {
            "status": "deprecated-after-one-release",
            "root_aliases_preserved": True,
            "per_file_reports": "mirrored directories at the output root",
        },
    }
    report["counts"]["suppressed_external_findings"] = len(
        suppressed_external_findings
    )
    _write_json(summary_dir / "report.json", report)
    _write_run_summary(summary_dir / "run-summary.md", report, run_metadata)
    _write_json(
        legacy_dir / "layout.json",
        {
            "schema_version": SCHEMA_VERSION,
            "contract": CONTRACT_URI,
            "kind": "legacy-layout",
            "deprecation": "Root aliases are preserved for one release.",
            "per_file_reports": "Mirrored directories remain at the output root.",
            "root_aliases": [
                "summary.csv",
                "findings.json",
                "findings.raw.json",
                "occurrences.json",
                "findings.csv",
                "findings.txt",
                "findings.sarif",
                "review_metrics.json",
                "diagnostics.json",
                "gitleaks-suppressed.json",
                "file_selection.json",
                "run_metadata.json",
            ],
        },
    )
    return {
        "summary": output_root / "summary.csv",
        "findings": output_root / "findings.json",
        "sarif": root_sarif,
        "report": summary_dir / "report.json",
        "occurrences": occurrences,
    }


def write_rollups_v2(*args, **kwargs):
    """Deprecated compatibility alias for integrations importing the v2 name."""
    return write_rollups_v3(*args, **kwargs)

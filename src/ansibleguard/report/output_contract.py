"""Write the versioned, organized output contract and compatibility aliases."""

from __future__ import annotations

from collections import Counter
import csv
import json
from pathlib import Path

from .csv_writer import write_findings_to_csv
from .occurrences import build_occurrences, occurrence_findings
from .sarif_writer import write_sarif
from .text_writer import write_findings_to_txt


SCHEMA_VERSION = 2
CONTRACT_URI = "ansibleguard://schemas/output-v2.json"
SUMMARY_FIELDS = (
    "file",
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
    "message",
    "canonical_provider",
    "detector_count",
    "native_rules",
    "evidence_fingerprints",
    "semantic_key",
)


def _relative_path(value, repo_root):
    path = Path(value)
    try:
        return path.resolve().relative_to(Path(repo_root).resolve()).as_posix()
    except ValueError:
        return path.as_posix().lstrip("./") or "."


def _envelope(kind, items, **extra):
    return {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": kind,
        "items": items,
        **extra,
    }


def _write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


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
    }
    return max(values, key=lambda value: priorities.get(value, 0))


def build_summary_rows(summary_rows, findings, occurrences, repo_root):
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
    for file in files:
        rows = source_rows.get(file, [])
        raw = raw_by_file.get(file, [])
        canonical = occurrences_by_file.get(file, [])
        severity = Counter(item.get("severity", "warning") for item in raw)
        providers = Counter(item.get("provider", "ansibleguard") for item in raw)
        enriched.append(
            {
                "file": file,
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
                f"detectors={occurrence['detector_count']}; rules={rules})\n"
            )


def _counts(findings, occurrences, summary_rows):
    return {
        "files": len(summary_rows),
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
    }


def write_rollups_v2(
    findings,
    summary_rows,
    diagnostics,
    project_metrics,
    output_root,
    repo_root,
    selection_metadata,
    run_metadata,
):
    """Write v2 organized output plus one-release root compatibility files."""
    output_root = Path(output_root)
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

    occurrences = build_occurrences(findings, repo_root=repo_root)
    enriched_summary = build_summary_rows(
        summary_rows, findings, occurrences, repo_root
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

    selection_v2 = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "file-selection",
        **selection_metadata,
    }
    run_v2 = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "run-metadata",
        **run_metadata,
    }
    _write_json(output_root / "file_selection.json", selection_v2)
    _write_json(output_root / "run_metadata.json", run_v2)

    root_sarif = output_root / "findings.sarif"
    write_sarif(occurrence_findings(occurrences), root_sarif, repo_root=repo_root)

    # Organized v2 contract.
    _write_summary(summary_dir / "summary.csv", enriched_summary)
    _write_json(
        summary_dir / "diagnostics.json",
        _envelope("diagnostics", diagnostics),
    )
    _write_json(
        raw_dir / "findings.json",
        _envelope("raw-findings", findings),
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
    _write_json(metadata_dir / "run.json", run_v2)
    _write_json(metadata_dir / "file-selection.json", selection_v2)
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
        "status": (
            "completed-with-diagnostics" if diagnostics else "completed"
        ),
        "profile": run_metadata["profile"]["name"],
        "target": run_metadata["target"],
        "tools": run_metadata["tools"],
        "counts": _counts(findings, occurrences, enriched_summary),
        "pr_comparison": {
            "status": "not-compared",
            "introduced": None,
            "policy_conclusion": None,
        },
        "artifacts": {
            "summary": "summary/summary.csv",
            "diagnostics": "summary/diagnostics.json",
            "raw_json": "raw/findings.json",
            "raw_csv": "raw/findings.csv",
            "raw_text": "raw/findings.txt",
            "canonical_json": "canonical/occurrences.json",
            "canonical_csv": "canonical/occurrences.csv",
            "canonical_text": "canonical/occurrences.txt",
            "sarif": "canonical/findings.sarif",
            "run_metadata": "metadata/run.json",
            "file_selection": "metadata/file-selection.json",
            "review_metrics": "metadata/review-metrics.json",
        },
        "compatibility": {
            "status": "deprecated-after-one-release",
            "root_aliases_preserved": True,
            "per_file_reports": "mirrored directories at the output root",
        },
    }
    _write_json(summary_dir / "report.json", report)
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

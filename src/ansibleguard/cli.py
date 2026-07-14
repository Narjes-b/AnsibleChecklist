from pathlib import Path
from dataclasses import dataclass
import os

# Default output folder name is excluded too — otherwise a second run
# against the same target directory could, in principle, later start
# picking up its own previous output as input if that ever changed shape.
# Costs nothing to guard against now.
EXCLUDE_DIRS = {
    "molecule",
    ".github",
    ".git",
    ".ansible",
    ".venv",
    "venv",
    "ansibleguard-output",
}


def collect_yaml_files(target: Path) -> list[Path]:
    """Find every .yml/.yaml file under target, recursively, skipping
    directories that contain real YAML but aren't Ansible production
    content (Molecule test scenarios, CI config, etc.)."""
    target = Path(target)
    if target.is_file():
        return [target]

    files = []
    for pattern in ("*.yml", "*.yaml"):
        files.extend(target.rglob(pattern))

    return sorted(f for f in files if not any(part in EXCLUDE_DIRS for part in f.parts))


def output_dir_for(scan_root: Path, yaml_file: Path, output_root: Path) -> Path:
    """
    Build a collision-safe output directory for one analyzed file.

    Using just the file's stem (e.g. "main") breaks the moment a real
    project has more than one identically-named file in different
    directories -- roles/apache/tasks/main.yml and roles/nginx/tasks/main.yml
    both stem to "main" and would silently overwrite each other's results.
    Confirmed this collision is real, not theoretical, against a synthetic
    two-role fixture before writing this function.

    Instead, mirror the file's path *relative to the scan root* underneath
    the output directory (extension dropped), so directory structure is
    preserved and collisions are structurally impossible rather than
    merely unlikely.
    """
    scan_root = Path(scan_root)
    yaml_file = Path(yaml_file)
    try:
        rel = yaml_file.resolve().relative_to(scan_root.resolve())
    except ValueError:
        # yaml_file isn't actually under scan_root (e.g. an absolute path
        # passed as a single file target with no directory context) --
        # fall back to just its own name rather than crashing.
        rel = Path(yaml_file.name)
    return Path(output_root) / rel.with_suffix("")


def _relative_or_self(path: Path, root: Path) -> str:
    """Best-effort relative path for the summary CSV -- falls back to the
    original path string if it isn't actually under root (e.g. a
    single-file target passed with no shared directory)."""
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _finding_path(finding) -> str:
    return str(
        finding.get("File")
        or finding.get("file")
        or finding.get("Path")
        or finding.get("path")
        or ""
    )


def _findings_for_file(findings, yaml_file, scan_root):
    expected = _relative_or_self(yaml_file, scan_root).replace(os.sep, "/")
    if Path(scan_root).is_file():
        return list(findings)
    matched = []
    for finding in findings:
        actual = _finding_path(finding).replace("\\", "/").lstrip("./")
        if actual == expected or actual.endswith("/" + expected):
            matched.append(finding)
    return matched


def _lint_findings_for_file(findings, yaml_file, scan_root):
    from .external.ansible_lint import lint_issue_path

    expected = _relative_or_self(yaml_file, scan_root).replace(os.sep, "/")
    matched = []
    for finding in findings:
        actual = lint_issue_path(finding).replace("\\", "/").lstrip("./")
        if actual == expected or actual.endswith("/" + expected):
            matched.append(finding)
    return matched


def analyze_path(target: Path, output_root: Path, gitleaks_path=None):
    """
    Run the existing per-file analysis + report-writing pipeline
    (smellsDetector.py's execute_for_single_file + the ansible-lint/gitleaks
    text writers) against every YAML file found under target, writing
    results under output_root instead of config.py's hardcoded RESULTS_DIR.

    In addition to everything already written per-file (unchanged), also
    accumulates a flat findings list across every file and writes three
    project-wide rollups once at the end: summary.csv (one row per file,
    for "which files are worst" at a glance), findings.json (the flat
    findings shape, our own readable format), and findings.sarif (the
    industry-standard shape GitHub Code Scanning natively renders as
    inline PR annotations).

    Returns a run-summary dictionary with discovery, structural-analysis,
    finding, parsing, and tool-failure counts.
    """
    from .smells import (
        execute_for_single_file,
        format_ansible_lint_results,
    )
    from .report.text_writer import (
        write_AnsibleLint_results_to_txt,
        write_GitLeaks_results_to_txt,
    )
    from .report.findings import build_findings_list
    from .report.sarif_writer import write_sarif

    from .report.findings import RULE_CATALOG
    from .document import inspect_document
    from .detectors.paper_candidates import detect_paper_candidates
    from .detectors.review_checklist import detect_review_checklist_smells
    from .detectors.partial_checklist import detect_partial_checklist_smells
    from .detectors.review_metadata import detect_project_review_smells
    from .external.gitleaks import scan_with_gitleaks
    from .external.ansible_lint import scan_with_ansible_lint
    from .external.install_gitleaks import GITLEAKS_PATH

    target = Path(target)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    yaml_files = collect_yaml_files(target)
    print(f"Found {len(yaml_files)} YAML file(s) to analyze.")

    scan_root = target if target.is_dir() else target.parent
    gitleaks_result = scan_with_gitleaks(target, gitleaks_path or GITLEAKS_PATH)
    lint_result = scan_with_ansible_lint(target)
    structurally_analyzed = 0
    all_findings = []
    summary_rows = []
    diagnostics = []
    consumed_gitleaks_ids = set()

    for yaml_file in yaml_files:
        out_dir = output_dir_for(scan_root, yaml_file, output_root)
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔍 Processing file: {yaml_file}")

        document_info = inspect_document(yaml_file)
        file_gitleaks = _findings_for_file(
            gitleaks_result.findings, yaml_file, scan_root
        )
        consumed_gitleaks_ids.update(id(finding) for finding in file_gitleaks)
        file_lint = _lint_findings_for_file(lint_result.findings, yaml_file, scan_root)

        findings, lint_results, result, metrics = execute_for_single_file(
            yaml_file,
            None,
            None,
            out_dir,
            gitleaks_findings=file_gitleaks,
            lint_results=file_lint,
            run_external=False,
        )
        structurally_analyzed_file = metrics is not None

        # Source and role-layout checks are safe for empty/metadata documents
        # that the playbook parser correctly refuses to treat as task lists.
        # Keep the structural status as "skipped", but retain these findings
        # in the project-wide JSON/SARIF rollups.
        report_metrics = metrics
        report_result = result
        if not structurally_analyzed_file:
            source_metrics = detect_paper_candidates(yaml_file)
            source_metrics.update(detect_review_checklist_smells(yaml_file))
            source_metrics.update(detect_partial_checklist_smells(yaml_file))
            if any(
                value
                for key, value in source_metrics.items()
                if not key.endswith("_details")
            ):
                report_metrics = source_metrics
                report_result = {
                    "playbook": {
                        "metrics": {"WarningUnusedIncludeVars": []},
                        "plays": [],
                    }
                }

        formatted = format_ansible_lint_results(lint_results)
        write_AnsibleLint_results_to_txt(
            formatted, out_dir / "ansiblelint.txt", yaml_file
        )
        write_GitLeaks_results_to_txt(findings, out_dir / "gitleaks.txt")

        file_findings = build_findings_list(
            report_metrics, report_result, findings, lint_results, yaml_file
        )
        all_findings.extend(file_findings)

        summary_rows.append(
            {
                "file": _relative_or_self(yaml_file, scan_root),
                "parse_status": document_info.parse_status,
                "document_type": document_info.document_type,
                "structural_status": (
                    "analyzed" if structurally_analyzed_file else "skipped"
                ),
                "gitleaks_status": gitleaks_result.status,
                "ansible_lint_status": lint_result.status,
                "errors": sum(1 for f in file_findings if f["severity"] == "error"),
                "warnings": sum(1 for f in file_findings if f["severity"] == "warning"),
                "notes": sum(1 for f in file_findings if f["severity"] == "note"),
                "total": len(file_findings),
            }
        )
        if structurally_analyzed_file:
            structurally_analyzed += 1
        if document_info.diagnostics:
            diagnostics.append(
                {
                    "file": _relative_or_self(yaml_file, scan_root),
                    "stage": "yaml-parse",
                    "status": document_info.parse_status,
                    "message": "; ".join(document_info.diagnostics),
                }
            )

    project_metrics = detect_project_review_smells(scan_root)
    if project_metrics:
        project_result = {
            "playbook": {"metrics": {"WarningUnusedIncludeVars": []}, "plays": []}
        }
        project_findings = build_findings_list(
            project_metrics, project_result, [], [], scan_root
        )
        if project_findings:
            all_findings.extend(project_findings)
            summary_rows.append(
                {
                    "file": ".",
                    "parse_status": "not-applicable",
                    "document_type": "review-metadata",
                    "structural_status": "not-applicable",
                    "gitleaks_status": gitleaks_result.status,
                    "ansible_lint_status": lint_result.status,
                    "errors": sum(f["severity"] == "error" for f in project_findings),
                    "warnings": sum(
                        f["severity"] == "warning" for f in project_findings
                    ),
                    "notes": sum(f["severity"] == "note" for f in project_findings),
                    "total": len(project_findings),
                }
            )

    # Repository-wide gitleaks also covers non-YAML files. Preserve those
    # findings in JSON/SARIF instead of silently dropping them merely because
    # they never enter the structural Ansible loop above.
    for finding in gitleaks_result.findings:
        if id(finding) in consumed_gitleaks_ids:
            continue
        finding_file = _finding_path(finding) or "."
        finding_path = Path(finding_file)
        if not finding_path.is_absolute():
            finding_path = Path(scan_root) / finding_path
        external_findings = build_findings_list(None, None, [finding], [], finding_path)
        all_findings.extend(external_findings)
        summary_rows.append(
            {
                "file": _relative_or_self(finding_path, scan_root),
                "parse_status": "not-applicable",
                "document_type": "non-yaml",
                "structural_status": "not-applicable",
                "gitleaks_status": gitleaks_result.status,
                "ansible_lint_status": lint_result.status,
                "errors": len(external_findings),
                "warnings": 0,
                "notes": 0,
                "total": len(external_findings),
            }
        )

    if gitleaks_result.status != "completed":
        diagnostics.append(
            {
                "file": ".",
                "stage": "gitleaks",
                "status": gitleaks_result.status,
                "message": gitleaks_result.message,
            }
        )
    if lint_result.status != "completed":
        diagnostics.append(
            {
                "file": ".",
                "stage": "ansible-lint",
                "status": lint_result.status,
                "message": lint_result.message,
            }
        )

    _write_rollups(all_findings, summary_rows, diagnostics, output_root, scan_root)

    print(
        f"[✔] {len(yaml_files)} file(s) discovered; "
        f"{structurally_analyzed} structurally analyzed; "
        f"gitleaks={gitleaks_result.status}; ansible-lint={lint_result.status}. "
        f"Results under {output_root}"
    )
    print(f"[✔] {len(all_findings)} total finding(s) across all files.")
    return {
        "discovered": len(yaml_files),
        "structurally_analyzed": structurally_analyzed,
        "findings": all_findings,
        "tool_errors": int(gitleaks_result.status != "completed")
        + int(lint_result.status != "completed"),
        "parse_failures": sum(
            row["parse_status"] in {"invalid", "read-error"} for row in summary_rows
        ),
    }


def _write_rollups(all_findings, summary_rows, diagnostics, output_root, scan_root):
    import csv
    import json as _json
    from .report.sarif_writer import write_sarif

    # summary.csv -- one row per file, ranked worst-first, for "which files
    # actually need attention" at a glance instead of opening N CSVs by hand.
    summary_rows_sorted = sorted(
        summary_rows, key=lambda r: (-r["errors"], -r["warnings"], -r["total"])
    )
    summary_csv_path = output_root / "summary.csv"
    with open(summary_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
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
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows_sorted)

    # findings.json -- the flat shape itself, in our own readable format.
    findings_json_path = output_root / "findings.json"
    with open(findings_json_path, "w", encoding="utf-8") as f:
        _json.dump(all_findings, f, indent=2)

    with open(output_root / "diagnostics.json", "w", encoding="utf-8") as f:
        _json.dump(diagnostics, f, indent=2)

    # findings.sarif -- GitHub Code Scanning-native shape.
    sarif_path = output_root / "findings.sarif"
    write_sarif(all_findings, sarif_path, repo_root=scan_root)

    print(
        f"[✔] Rollups written: {summary_csv_path}, {findings_json_path}, {sarif_path}"
    )


def main(argv=None):
    import argparse
    import sys

    argv = list(argv) if argv is not None else sys.argv[1:]
    if argv == ["install-tools"]:
        from .external.install_gitleaks import ensure_gitleaks_installed

        ensure_gitleaks_installed()
        return

    parser = argparse.ArgumentParser(
        prog="ansibleguard",
        description="Analyze Ansible playbooks/roles for IaC code smells.",
    )
    parser.add_argument(
        "target",
        type=Path,
        help="A playbook file OR a project directory (searched recursively)",
    )
    parser.add_argument(
        "--gitleaks-path",
        type=Path,
        help="Path to the gitleaks binary (default: ~/.ansibleguard/gitleaks-bin/gitleaks)",
    )
    parser.add_argument(
        "--fail-on",
        choices=("never", "error", "warning", "tool-error", "parse-error"),
        default="error",
        help="Exit non-zero for the selected condition (default: error)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./ansibleguard-output"),
        help="Where to write reports (default: ./ansibleguard-output)",
    )
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"Error: target path does not exist: {args.target}", file=sys.stderr)
        sys.exit(1)

    run = analyze_path(args.target, args.output, args.gitleaks_path)
    severities = {finding["severity"] for finding in run.get("findings", [])}
    should_fail = {
        "never": False,
        "error": "error" in severities,
        "warning": bool(severities & {"error", "warning"}),
        "tool-error": run.get("tool_errors", 0) > 0,
        "parse-error": run.get("parse_failures", 0) > 0,
    }[args.fail_on]
    if should_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()

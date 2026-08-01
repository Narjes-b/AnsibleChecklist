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


def collect_yaml_files(target: Path, file_manifest: Path | None = None) -> list[Path]:
    """Find every .yml/.yaml file under target, recursively, skipping
    directories that contain real YAML but aren't Ansible production
    content (Molecule test scenarios, CI config, etc.)."""
    target = Path(target)
    if file_manifest is not None:
        from .file_manifest import included_files_from_manifest

        return included_files_from_manifest(target, file_manifest)
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


def analyze_path(
    target: Path,
    output_root: Path,
    gitleaks_path=None,
    file_manifest: Path | None = None,
    profile: str = "technical-full",
):
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
        write_findings_to_txt,
        write_GitLeaks_results_to_txt,
    )
    from .report.findings import build_findings_list
    from .report.sarif_writer import write_sarif

    from .report.findings import RULE_CATALOG
    from .detector_config import filter_findings
    from .document import inspect_document
    from .detectors.paper_candidates import detect_paper_candidates
    from .detectors.review_checklist import detect_review_checklist_smells
    from .detectors.partial_checklist import detect_partial_checklist_smells
    from .detectors.missing_checklist import detect_missing_checklist_smells
    from .detectors.review_metadata import detect_project_review_smells
    from .detectors.file_kinds import (
        detect_file_kind_smells,
        detect_role_variable_precedence_collisions,
    )
    from .external.gitleaks import (
        scan_git_range_with_gitleaks,
        scan_with_gitleaks,
    )
    from .external.ansible_lint import scan_with_ansible_lint
    from .external.install_gitleaks import GITLEAKS_PATH
    from .external.gitleaks import ToolResult
    from .profiles import (
        filter_profile_findings,
        profile_definition,
        profile_metadata,
        provider_enabled,
    )
    from .file_manifest import FileManifestError

    target = Path(target)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    definition = profile_definition(profile)
    if definition["requires_manifest"] and file_manifest is None:
        raise FileManifestError(
            f"profile {profile} requires --file-manifest so the scanned and "
            "counted source populations are identical"
        )
    selected_yaml_files = collect_yaml_files(target, file_manifest)
    yaml_files = selected_yaml_files if definition["source_analysis"] else []
    if file_manifest is None:
        print(f"Found {len(selected_yaml_files)} YAML file(s) for profile {profile}.")
    else:
        print(
            f"Selected {len(selected_yaml_files)} YAML file(s) from classification "
            f"manifest {file_manifest} for profile {profile}."
        )

    scan_root = target if target.is_dir() else target.parent
    if provider_enabled(profile, "gitleaks"):
        binary_path = gitleaks_path or GITLEAKS_PATH
        tree_result = scan_with_gitleaks(target, binary_path)
        base_sha = os.environ.get("ANSIBLEGUARD_BASE_SHA")
        head_sha = os.environ.get("ANSIBLEGUARD_HEAD_SHA")
        if target.is_dir() and base_sha and head_sha:
            history_result = scan_git_range_with_gitleaks(
                target, binary_path, base_sha, head_sha
            )
            statuses = {tree_result.status, history_result.status}
            gitleaks_result = ToolResult(
                "tool-error" if "tool-error" in statuses else "completed",
                findings=tree_result.findings + history_result.findings,
                message="; ".join(
                    message
                    for message in (tree_result.message, history_result.message)
                    if message
                ),
                metadata={
                    "provider": "gitleaks",
                    "tree": tree_result.metadata,
                    "git_range": history_result.metadata,
                },
            )
        else:
            gitleaks_result = tree_result
    else:
        message = f"GitLeaks is not requested by profile {profile}."
        gitleaks_result = ToolResult("not-requested", message=message)
    if provider_enabled(profile, "ansible-lint"):
        lint_result = scan_with_ansible_lint(target)
    else:
        message = f"ansible-lint is not requested by profile {profile}."
        lint_result = ToolResult("not-requested", message=message)
    structurally_analyzed = 0
    all_findings = []
    summary_rows = []
    diagnostics = []
    consumed_gitleaks_ids = set()
    consumed_lint_ids = set()

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
        consumed_lint_ids.update(id(finding) for finding in file_lint)

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
            source_metrics.update(detect_missing_checklist_smells(yaml_file))
            source_metrics.update(detect_file_kind_smells(yaml_file))
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
        file_findings = filter_findings(file_findings, yaml_file)
        file_findings = filter_profile_findings(file_findings, profile)
        write_findings_to_txt(
            file_findings,
            out_dir / "Play_Level_Analysis.txt",
            mode="a",
            title="All file findings",
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

    project_metrics = (
        detect_project_review_smells(scan_root) if definition["review_analysis"] else {}
    )
    if project_metrics:
        project_result = {
            "playbook": {"metrics": {"WarningUnusedIncludeVars": []}, "plays": []}
        }
        project_findings = build_findings_list(
            project_metrics, project_result, [], [], scan_root
        )
        project_findings = filter_findings(project_findings, scan_root)
        project_findings = filter_profile_findings(project_findings, profile)
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

    repository_source_metrics = (
        detect_role_variable_precedence_collisions(scan_root)
        if definition["source_analysis"] and target.is_dir()
        else {}
    )
    if repository_source_metrics:
        project_result = {
            "playbook": {"metrics": {"WarningUnusedIncludeVars": []}, "plays": []}
        }
        source_project_findings = build_findings_list(
            repository_source_metrics, project_result, [], [], scan_root
        )
        source_project_findings = filter_findings(
            source_project_findings, scan_root
        )
        source_project_findings = filter_profile_findings(
            source_project_findings, profile
        )
        all_findings.extend(source_project_findings)

    # Repository-wide gitleaks also covers non-YAML files. Preserve those
    # findings in JSON/SARIF instead of silently dropping them merely because
    # they never enter the structural Ansible loop above.
    selected_yaml = {
        _relative_or_self(path, scan_root).replace(os.sep, "/") for path in yaml_files
    }
    for finding in gitleaks_result.findings:
        if id(finding) in consumed_gitleaks_ids:
            continue
        finding_file = _finding_path(finding) or "."
        finding_path = Path(finding_file)
        if not finding_path.is_absolute():
            finding_path = Path(scan_root) / finding_path
        finding_relative = _relative_or_self(finding_path, scan_root).replace(os.sep, "/")
        if (
            file_manifest is not None
            and finding_path.suffix.lower() in {".yml", ".yaml"}
            and finding_relative not in selected_yaml
        ):
            continue
        external_findings = build_findings_list(None, None, [finding], [], finding_path)
        external_findings = filter_findings(external_findings, scan_root)
        external_findings = filter_profile_findings(external_findings, profile)
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

    # Lint-only profiles deliberately skip internal structural analysis. Keep
    # every native ansible-lint result by normalizing any result not consumed
    # in the per-file loop above.
    for finding in lint_result.findings:
        if id(finding) in consumed_lint_ids:
            continue
        from .external.ansible_lint import lint_issue_path

        finding_file = lint_issue_path(finding) or "."
        finding_path = Path(finding_file)
        if not finding_path.is_absolute():
            finding_path = Path(scan_root) / finding_path
        external_findings = build_findings_list(None, None, [], [finding], finding_path)
        external_findings = filter_findings(external_findings, scan_root)
        external_findings = filter_profile_findings(external_findings, profile)
        all_findings.extend(external_findings)
        if external_findings:
            summary_rows.append(
                {
                    "file": _relative_or_self(finding_path, scan_root),
                    "parse_status": "not-applicable",
                    "document_type": "ansible-lint",
                    "structural_status": "not-applicable",
                    "gitleaks_status": gitleaks_result.status,
                    "ansible_lint_status": lint_result.status,
                    "errors": sum(
                        item["severity"] == "error" for item in external_findings
                    ),
                    "warnings": sum(
                        item["severity"] == "warning" for item in external_findings
                    ),
                    "notes": sum(
                        item["severity"] == "note" for item in external_findings
                    ),
                    "total": len(external_findings),
                }
            )

    failed_statuses = {"tool-error"}
    if gitleaks_result.status in failed_statuses:
        diagnostics.append(
            {
                "file": ".",
                "stage": "gitleaks",
                "status": gitleaks_result.status,
                "message": gitleaks_result.message,
            }
        )
    if lint_result.status in failed_statuses:
        diagnostics.append(
            {
                "file": ".",
                "stage": "ansible-lint",
                "status": lint_result.status,
                "message": lint_result.message,
            }
        )

    selection_metadata = {"mode": "recursive-discovery"}
    if file_manifest is not None:
        from .file_manifest import file_manifest_metadata

        selection_metadata = file_manifest_metadata(file_manifest)
    run_metadata = {
        "profile": profile_metadata(profile),
        "target": str(target.resolve()),
        "file_selection": selection_metadata,
        "tools": {
            "gitleaks": gitleaks_result.status,
            "ansible_lint": lint_result.status,
        },
        "tool_details": {
            "gitleaks": gitleaks_result.metadata,
            "ansible_lint": lint_result.metadata,
        },
    }
    _write_rollups(
        all_findings,
        summary_rows,
        diagnostics,
        project_metrics,
        output_root,
        scan_root,
        selection_metadata,
        run_metadata,
    )

    print(
        f"[✔] {len(selected_yaml_files)} file(s) selected; "
        f"{len(yaml_files)} source file(s) processed; "
        f"{structurally_analyzed} structurally analyzed; "
        f"gitleaks={gitleaks_result.status}; ansible-lint={lint_result.status}. "
        f"Results under {output_root}"
    )
    print(f"[✔] {len(all_findings)} total finding(s) across all files.")
    return {
        "discovered": len(selected_yaml_files),
        "processed": len(yaml_files),
        "structurally_analyzed": structurally_analyzed,
        "findings": all_findings,
        "tool_errors": int(gitleaks_result.status in failed_statuses)
        + int(lint_result.status in failed_statuses),
        "profile": profile,
        "parse_failures": sum(
            row["parse_status"] in {"invalid", "read-error"} for row in summary_rows
        ),
    }


def _write_rollups(
    all_findings,
    summary_rows,
    diagnostics,
    project_metrics,
    output_root,
    scan_root,
    selection_metadata,
    run_metadata,
):
    from .report.output_contract import write_rollups_v2

    paths = write_rollups_v2(
        all_findings,
        summary_rows,
        diagnostics,
        project_metrics,
        output_root,
        scan_root,
        selection_metadata,
        run_metadata,
    )
    print(
        f"[✔] Rollups written: {paths['summary']}, {paths['findings']}, "
        f"{paths['sarif']}, {paths['report']}"
    )


def main(argv=None):
    import argparse
    import sys
    from .file_manifest import FileManifestError

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
    parser.add_argument(
        "--file-manifest",
        type=Path,
        help=(
            "CSV classification manifest; analyze only rows with included=true "
            "after validating complete repository coverage"
        ),
    )
    from .profiles import PROFILE_NAMES

    parser.add_argument(
        "--profile",
        choices=PROFILE_NAMES,
        default="technical-full",
        help="Rule/execution profile (default: technical-full)",
    )
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"Error: target path does not exist: {args.target}", file=sys.stderr)
        sys.exit(1)

    try:
        run = analyze_path(
            args.target,
            args.output,
            args.gitleaks_path,
            args.file_manifest,
            args.profile,
        )
    except FileManifestError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
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

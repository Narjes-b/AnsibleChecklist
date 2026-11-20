from collections import Counter
from pathlib import Path
import os
import re
import sys
import time

from .redaction import redact_sensitive_text

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
    # Normalize once so external providers and report path matching share the
    # same repository root. Relative directory targets previously caused a
    # GitLeaks path such as ``repo/file`` to be joined to ``repo`` twice.
    target = Path(target).resolve()
    if file_manifest is not None:
        from .file_manifest import included_files_from_manifest

        return included_files_from_manifest(target, file_manifest)
    if target.is_file():
        return [target]

    files = []
    for pattern in ("*.yml", "*.yaml"):
        files.extend(target.rglob(pattern))

    candidates = sorted(
        f for f in files if not any(part in EXCLUDE_DIRS for part in f.parts)
    )
    # Do not analyze the same physical YAML twice through a repository-local
    # symlink (for example test/integration/default.yml -> ../../site.yml).
    # Prefer the real file when both the target and an alias were discovered.
    unique = {}
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(target)
        except (OSError, ValueError):
            # Never follow broken or checkout-escaping aliases discovered
            # inside a directory scan. Explicit single-file targets were
            # already resolved above and remain an intentional caller choice.
            continue
        existing = unique.get(resolved)
        if existing is None or (existing.is_symlink() and not candidate.is_symlink()):
            unique[resolved] = candidate
    return sorted(unique.values())


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
        actual = _finding_path(finding).replace("\\", "/").removeprefix("./")
        if actual == expected or actual.endswith("/" + expected):
            matched.append(finding)
    return matched


def _lint_findings_for_file(findings, yaml_file, scan_root):
    from .external.ansible_lint import lint_issue_path

    expected = _relative_or_self(yaml_file, scan_root).replace(os.sep, "/")
    matched = []
    for finding in findings:
        actual = lint_issue_path(finding).replace("\\", "/").removeprefix("./")
        if actual == expected or actual.endswith("/" + expected):
            matched.append(finding)
    return matched


def _lint_location_path(finding_file, scan_root):
    """Return a real source path, or the repository root for load failures."""
    path = Path(finding_file)
    if not path.is_absolute():
        path = Path(scan_root) / path
    return path if path.exists() else Path(scan_root)


def _annotate_finding_populations(findings, repository_context, scan_root):
    """Attach explicit, denominator-safe populations to every occurrence."""
    contexts = {}
    if repository_context is not None:
        contexts = {
            item.relative_path: item
            for item in repository_context.file_contexts.values()
        }
    population_map = {
        "production_ansible": "production_valid",
        "test_ansible": "test_or_example",
        "example_ansible": "test_or_example",
        "historical_ansible": "project_or_external",
        "fixture_or_generated": "project_or_external",
        "project_yaml": "project_or_external",
        "unknown": "classification_suspect",
    }
    secret_map = {
        "production_ansible": "production_ansible_secret",
        "test_ansible": "test_secret",
        "example_ansible": "example_secret",
        "historical_ansible": "project_external_secret",
        "fixture_or_generated": "fixture_secret",
        "project_yaml": "project_external_secret",
        "unknown": "project_external_secret",
    }
    for finding in findings:
        relative = str(finding.get("file") or ".").replace("\\", "/").removeprefix("./")
        context = contexts.get(relative)
        classification = context.classification if context else "project_yaml"
        confidence = context.classification_confidence if context else "low"
        if context and context.parse_status in {"invalid", "invalid-encoding", "read-error"}:
            inferred = "analysis_failed"
        else:
            inferred = population_map.get(classification, "classification_suspect")
        finding.setdefault("analysis_population", inferred)
        finding["source_population"] = classification
        finding["classification_confidence"] = confidence
        if finding.get("provider") == "gitleaks":
            finding["secret_population"] = secret_map.get(
                classification, "project_external_secret"
            )
            candidate = str(
                finding.get("Secret")
                or finding.get("secret")
                or finding.get("Match")
                or finding.get("match")
                or ""
            )
            placeholder = bool(candidate) and bool(re.match(
                r"(?i)^(?:placeholder|changeme|change[_-]?me|your[_-]|"
                r"example[_-]|dummy|fake|test|<[^>]+>|x{3,})",
                candidate.strip("'\" "),
            ))
            contextual_dummy = classification in {
                "test_ansible", "example_ansible", "fixture_or_generated"
            }
            likely_real = bool(candidate) and (
                classification == "production_ansible"
                and confidence == "high"
                and not placeholder
            )
            finding["secret_context"] = (
                "likely_dummy_secret"
                if placeholder or contextual_dummy
                else "likely_real_secret"
                if likely_real
                else "uncertain_secret"
            )
            finding["secret_context_factors"] = {
                "positive": [
                    "provider_secret_pattern",
                    *(
                        ["literal_candidate", "production_ansible", "high_classification_confidence"]
                        if likely_real else []
                    ),
                ],
                "negative": [
                    factor
                    for factor, present in (
                        ("placeholder_value", placeholder),
                        ("test_example_or_fixture", contextual_dummy),
                    )
                    if present
                ],
            }
            # A key-shaped YAML line gives provider evidence the same semantic
            # subject used by plaintext-sensitive-variable findings. This is
            # intentionally conservative: no key means no cross-provider merge.
            source_path = scan_root / relative
            try:
                line_number = max(1, int(finding.get("line") or 1))
                source_line = source_path.read_text(encoding="utf-8").splitlines()[
                    line_number - 1
                ]
            except (OSError, UnicodeError, IndexError, ValueError):
                source_line = ""
            key_match = re.match(r"^\s*([A-Za-z_][\w.-]*)\s*:", source_line)
            if key_match:
                finding.setdefault(
                    "semantic_subject", f"variable:{key_match.group(1).lower()}"
                )
    return findings


def _positive_explain_seconds(value):
    import argparse
    import math
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be positive finite seconds") from None
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be positive finite seconds")
    return number


def _add_explain_runtime_arguments(parser):
    parser.add_argument("--explain-style", choices=("free", "verified-facts"), default="free",
                        help="Free model prose or source-bound verified claims selected by the model")
    parser.add_argument("--explain-timeout", type=_positive_explain_seconds, default=120.0,
                        help="Maximum seconds per local explanation (default: 120)")
    parser.add_argument("--explain-budget", type=_positive_explain_seconds, default=600.0,
                        help="Overall local explanation budget in seconds (default: 600)")
    parser.add_argument("--explain-checkpoint-dir", type=Path,
                        help="Private per-attempt records; resume successes only for matching source/model/prompt identities")


def analyze_path(
    target: Path,
    output_root: Path,
    gitleaks_path=None,
    file_manifest: Path | None = None,
    profile: str = "technical-full",
    source_snapshot=None,
    fail_on_detector_error=False,
    provider_concurrent=True,
    ansible_lint_scope="v005-selected",
    explain=False,
    explain_model="qwen2.5-coder:7b",
    explain_host="http://127.0.0.1:11434",
    explain_max_items=None,
    explain_timeout=120.0,
    explain_budget=600.0,
    explain_checkpoint_dir=None,
    explain_style="free",
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
    if source_snapshot is None:
        from .sources.local import LocalSource

        with LocalSource(target).materialize() as snapshot:
            return analyze_path(
                snapshot.root,
                output_root,
                gitleaks_path,
                file_manifest,
                profile,
                source_snapshot=snapshot,
                fail_on_detector_error=fail_on_detector_error,
                provider_concurrent=provider_concurrent,
                ansible_lint_scope=ansible_lint_scope,
            )

    scan_started = time.perf_counter()
    cpu_started = time.process_time()

    from .smells import (
        FileAnalysisError,
        execute_for_single_file,
        format_ansible_lint_results,
    )
    from .report.text_writer import (
        write_AnsibleLint_results_to_txt,
        write_findings_to_txt,
        write_GitLeaks_results_to_txt,
    )
    from .report.findings import build_findings_list
    from .detector_config import filter_findings, find_config
    from .document import inspect_document
    from .detectors.paper_candidates import detect_paper_candidates
    from .detectors.review_checklist import detect_review_checklist_smells
    from .detectors.partial_checklist import detect_partial_checklist_smells
    from .detectors.missing_checklist import detect_missing_checklist_smells
    from .detectors.galaxy_meta import detect_galaxy_meta_incomplete
    from .detectors.variable_naming import detect_variable_naming_convention
    from .detectors.review_metadata import detect_project_review_smells
    from .detectors.file_kinds import (
        detect_file_kind_smells,
        detect_role_variable_precedence_collisions,
    )
    from .profiles import (
        filter_profile_findings,
        profile_metadata,
    )
    from .runtime import (
        FileStageResult,
        RunResult,
        build_repository_context_stage,
        build_symbol_index_stage,
        classify_fault,
        diagnostic,
        prepare_scan_context,
        reproducibility_metadata,
        run_external_providers,
    )

    def document_diagnostic(document_info, yaml_file):
        item = diagnostic(
            _relative_or_self(yaml_file, scan_root),
            "yaml-parse",
            document_info.parse_status,
            "; ".join(document_info.diagnostics),
        )
        if document_info.fault_category:
            item["category"] = document_info.fault_category
            item["failure_nature"] = (
                document_info.failure_nature or "UNKNOWN"
            )
        return item

    # Keep provider paths and report paths anchored to the same absolute root.
    # This also prevents relative GitLeaks paths from being prefixed twice.
    discovery_started = time.perf_counter()
    context = prepare_scan_context(
        target, output_root, profile, file_manifest, collect_yaml_files,
        ansible_lint_scope=ansible_lint_scope,
    )
    discovery_seconds = time.perf_counter() - discovery_started
    target = context.target
    output_root = context.output_root
    definition = context.definition
    selected_yaml_files = list(context.selected_files)
    yaml_files = list(context.source_files)

    def fail_memory_stage(stage, exc):
        failure = {
            "file": ".",
            "stage": stage,
            "status": "analysis-error",
            "category": "MEMORY_ERROR",
            "failure_nature": "ENVIRONMENT",
            "message": redact_sensitive_text(exc),
        }
        metadata = {
            "source": source_snapshot.provenance(),
            "profile": profile_metadata(profile),
            "target": str(context.target),
            "tools": {
                "gitleaks": "not-requested",
                "ansible_lint": "not-requested",
            },
            "analysis_health": {
                "status": "failed",
                "complete": False,
                "selected_files": len(selected_yaml_files),
                "processed_files": 0,
                "parsed_files": 0,
                "parse_failed_files": 0,
                "diagnostic_count": 1,
                "fault_count": 1,
                "faults_by_category": {"MEMORY_ERROR": 1},
                "faults_by_nature": {"ENVIRONMENT": 1},
            },
            "timings": {
                "pre_reporting_total_seconds": time.perf_counter() - scan_started,
                "cpu_seconds": time.process_time() - cpu_started,
            },
            "performance": {},
        }
        _write_emergency_failure_state(
            context.output_root, metadata, [failure], failure
        )
        return RunResult(
            discovered=len(selected_yaml_files),
            processed=0,
            structurally_analyzed=0,
            findings=[],
            tool_errors=0,
            profile=profile,
            parse_failures=0,
            analysis_failures=1,
            file_states={"failed": len(yaml_files)},
            status="failed",
        ).as_dict()
    if file_manifest is None:
        print(f"Found {len(selected_yaml_files)} YAML file(s) for profile {profile}.")
    else:
        print(
            f"Selected {len(selected_yaml_files)} YAML file(s) from classification "
            f"manifest {file_manifest} for profile {profile}."
        )

    scan_root = context.scan_root
    parse_started = time.perf_counter()
    try:
        repository_context = build_repository_context_stage(context)
    except MemoryError as exc:
        return fail_memory_stage("repository-context", exc)
    parse_seconds = time.perf_counter() - parse_started
    symbol_started = time.perf_counter()
    try:
        symbol_index = build_symbol_index_stage(context, repository_context)
    except MemoryError as exc:
        return fail_memory_stage("symbol-index", exc)
    symbol_index_seconds = time.perf_counter() - symbol_started
    if repository_context is not None:
        repository_context = repository_context.with_symbol_graph(symbol_index)
    providers_started = time.perf_counter()
    try:
        providers = run_external_providers(
            context, gitleaks_path, repository_context,
            concurrent=provider_concurrent,
        )
    except MemoryError as exc:
        return fail_memory_stage("providers", exc)
    providers_seconds = time.perf_counter() - providers_started
    gitleaks_result = providers.gitleaks
    lint_result = providers.ansible_lint
    structurally_analyzed = 0
    all_findings = []
    summary_rows = []
    diagnostics = []
    cache_errors = (
        repository_context.performance.get("cache_errors", 0)
        if repository_context is not None else 0
    )
    if cache_errors:
        diagnostics.append(
            diagnostic(
                ".",
                "parse-cache",
                "analysis-error",
                f"{cache_errors} parse-cache operation(s) failed; source was reparsed",
            )
        )
    for provider_diagnostic in lint_result.metadata.get("provider_diagnostics", []):
        diagnostics.append(
            {
                "file": ".",
                "stage": "ansible-lint",
                "status": (
                    "provider-schema-error"
                    if provider_diagnostic.get("category") == "PROVIDER_SCHEMA_ERROR"
                    else "provider-error"
                ),
                "category": provider_diagnostic.get("category", "PROVIDER_ERROR"),
                "failure_nature": (
                    "BUG"
                    if provider_diagnostic.get("category") == "PROVIDER_SCHEMA_ERROR"
                    else "ENVIRONMENT"
                ),
                "message": provider_diagnostic.get("message", "Provider diagnostic"),
                "evidence": provider_diagnostic,
            }
        )
    for root_result in lint_result.metadata.get("root_results", []):
        if root_result.get("status") in {"completed", "not-requested"}:
            continue
        if root_result.get("metadata", {}).get("provider_diagnostics"):
            # The adapter already emitted the correlated primary cause for
            # this invocation; do not add a second generic root failure.
            continue
        diagnostics.append(
            {
                "file": ".",
                "stage": "ansible-lint",
                "status": "provider-error",
                "category": "PROVIDER_ERROR",
                "failure_nature": "ENVIRONMENT",
                "provider_root": root_result.get("root", "."),
                "message": root_result.get("message")
                or f"ansible-lint root finished as {root_result.get('status')}",
                "evidence": root_result,
            }
        )
    provider_health_results = {
        "ansible-lint": lint_result,
        "gitleaks": gitleaks_result,
    }
    for provider_name, provider_result in provider_health_results.items():
        if provider_result.status in {"completed", "not-requested"}:
            continue
        already_explained = any(
            item.get("stage") == provider_name for item in diagnostics
        )
        if already_explained:
            continue
        category = (
            "TIMEOUT" if provider_result.status == "timeout"
            else "PROVIDER_ERROR"
        )
        diagnostics.append({
            "file": ".",
            "stage": provider_name,
            "status": (
                "timeout" if provider_result.status == "timeout"
                else provider_result.status
                if provider_result.status == "tool-error"
                else "provider-error"
            ),
            "category": category,
            "failure_nature": (
                "TIMEOUT" if category == "TIMEOUT" else "ENVIRONMENT"
            ),
            "message": provider_result.message
            or f"{provider_name} finished as {provider_result.status}",
            "evidence": {
                "provider_status": provider_result.status,
                "returncode": provider_result.metadata.get("returncode"),
            },
        })
    consumed_gitleaks_ids = set()
    consumed_lint_ids = set()
    analysis_failures = 0
    file_stage_results = []
    detector_timing_totals = Counter()
    detector_skip_totals = Counter()

    internal_started = time.perf_counter()
    for yaml_file in yaml_files:
        out_dir = output_dir_for(scan_root, yaml_file, output_root)
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"Processing file: {yaml_file}")

        document_info = (
            repository_context.document_for(yaml_file)
            if repository_context is not None
            else inspect_document(yaml_file)
        )
        file_gitleaks = _findings_for_file(
            gitleaks_result.findings, yaml_file, scan_root
        )
        consumed_gitleaks_ids.update(id(finding) for finding in file_gitleaks)
        file_lint = _lint_findings_for_file(lint_result.findings, yaml_file, scan_root)
        consumed_lint_ids.update(id(finding) for finding in file_lint)

        try:
            findings, lint_results, result, metrics = execute_for_single_file(
                yaml_file,
                None,
                None,
                out_dir,
                gitleaks_findings=file_gitleaks,
                lint_results=file_lint,
                run_external=False,
                symbol_index=symbol_index,
                raise_on_error=True,
                enabled_rules=definition["rules"],
                parsed_document=document_info,
                repository_context=repository_context,
                fail_on_detector_error=fail_on_detector_error,
            )
        except FileAnalysisError as exc:
            analysis_failures += 1
            status = "partial" if exc.partial else "failed"
            try:
                file_findings = build_findings_list(
                    None, None, file_gitleaks, file_lint, yaml_file
                )
                file_findings = filter_profile_findings(
                    filter_findings(file_findings, yaml_file), profile
                )
            except Exception as fallback_exc:
                file_findings = []
                diagnostics.append(
                    diagnostic(
                        _relative_or_self(yaml_file, scan_root),
                        "external-finding-normalization",
                        "analysis-error",
                        fallback_exc,
                    )
                )
            all_findings.extend(file_findings)
            diagnostics.append(
                diagnostic(
                    _relative_or_self(yaml_file, scan_root),
                    exc.stage,
                    "analysis-error",
                    exc.cause,
                )
            )
            summary_rows.append(
                {
                    "file": _relative_or_self(yaml_file, scan_root),
                    "parse_status": document_info.parse_status,
                    "document_type": document_info.document_type,
                    "structural_status": status,
                    "gitleaks_status": gitleaks_result.status,
                    "ansible_lint_status": lint_result.status,
                    "errors": sum(f["severity"] == "error" for f in file_findings),
                    "warnings": sum(f["severity"] == "warning" for f in file_findings),
                    "notes": sum(f["severity"] == "note" for f in file_findings),
                    "total": len(file_findings),
                }
            )
            file_stage_results.append(
                FileStageResult(
                    yaml_file,
                    status,
                    document_info.parse_status,
                    document_info.document_type,
                    findings=file_findings,
                    diagnostics=[diagnostics[-1]],
                    structurally_analyzed=False,
                )
            )
            if document_info.diagnostics:
                diagnostics.append(document_diagnostic(document_info, yaml_file))
            continue
        structurally_analyzed_file = metrics is not None
        detector_diagnostics = (
            list(metrics.get("_detector_diagnostics", []))
            if isinstance(metrics, dict) else []
        )
        if isinstance(metrics, dict):
            detector_timing_totals.update(metrics.get("_detector_timings", {}))
            detector_skip_totals.update(metrics.get("_detectors_skipped", ()))
        if detector_diagnostics:
            analysis_failures += len(detector_diagnostics)
            for item in detector_diagnostics:
                diagnostics.append(
                    {
                        **item,
                        "file": _relative_or_self(yaml_file, scan_root),
                        "status": "analysis-error",
                        "failure_nature": item.get("failure_nature", "BUG"),
                    }
                )
        structural_status = (
            "partial" if detector_diagnostics
            else "analyzed" if structurally_analyzed_file
            else "skipped"
        )

        # Source and role-layout checks are safe for empty/metadata documents
        # that the playbook parser correctly refuses to treat as task lists.
        # Keep the structural status as "skipped", but retain these findings
        # in the project-wide JSON/SARIF rollups.
        report_metrics = metrics
        report_result = result
        if not structurally_analyzed_file:
            try:
                source_metrics = detect_paper_candidates(
                    yaml_file,
                    symbol_index=symbol_index,
                    parsed_document=document_info,
                    repository_context=repository_context,
                )
                source_metrics.update(
                    detect_review_checklist_smells(
                        yaml_file, symbol_index=symbol_index
                    )
                )
                source_metrics.update(
                    detect_partial_checklist_smells(
                        yaml_file, symbol_index=symbol_index
                    )
                )
                source_metrics.update(
                    detect_missing_checklist_smells(
                        yaml_file,
                        symbol_index=symbol_index,
                        repository_context=repository_context,
                        parsed_document=document_info,
                    )
                )
                source_metrics.update(
                    detect_file_kind_smells(
                        yaml_file, parsed_document=document_info
                    )
                )
                # Metadata and variable documents intentionally bypass the
                # task/play parser, so their dedicated rules belong here.
                galaxy_count, galaxy_details = detect_galaxy_meta_incomplete(
                    yaml_file, parsed_document=document_info
                )
                source_metrics.update({
                    "galaxy_meta_incomplete": galaxy_count,
                    "galaxy_meta_incomplete_details": galaxy_details,
                })
                naming_count, naming_details = detect_variable_naming_convention(
                    yaml_file, parsed_document=document_info
                )
                source_metrics.update({
                    "variable_naming_convention": naming_count,
                    "variable_naming_convention_details": naming_details,
                })
            except Exception as exc:
                analysis_failures += 1
                structural_status = "failed"
                diagnostics.append(
                    diagnostic(
                        _relative_or_self(yaml_file, scan_root),
                        "safe-source-detectors",
                        "analysis-error",
                        exc,
                    )
                )
                source_metrics = {}
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

        try:
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
        except Exception as exc:
            analysis_failures += 1
            structural_status = "partial" if metrics is not None else "failed"
            diagnostics.append(
                diagnostic(
                    _relative_or_self(yaml_file, scan_root),
                    "finding-normalization-and-reporting",
                    "analysis-error",
                    exc,
                )
            )
            # Keep independently collected external evidence even when an
            # internal normalization or per-file writer fails.
            try:
                file_findings = build_findings_list(
                    None, None, file_gitleaks, file_lint, yaml_file
                )
                file_findings = filter_profile_findings(
                    filter_findings(file_findings, yaml_file), profile
                )
            except Exception as fallback_exc:
                file_findings = []
                diagnostics.append(
                    diagnostic(
                        _relative_or_self(yaml_file, scan_root),
                        "external-finding-normalization",
                        "analysis-error",
                        fallback_exc,
                    )
                )
        all_findings.extend(file_findings)

        summary_rows.append(
            {
                "file": _relative_or_self(yaml_file, scan_root),
                "parse_status": document_info.parse_status,
                "document_type": document_info.document_type,
                "structural_status": structural_status,
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
            diagnostics.append(document_diagnostic(document_info, yaml_file))
        file_stage_results.append(
            FileStageResult(
                yaml_file,
                structural_status,
                document_info.parse_status,
                document_info.document_type,
                findings=file_findings,
                diagnostics=detector_diagnostics,
                structurally_analyzed=structurally_analyzed_file,
            )
        )

    try:
        project_metrics = (
            detect_project_review_smells(scan_root)
            if definition["review_analysis"]
            else {}
        )
    except Exception as exc:
        analysis_failures += 1
        diagnostics.append(
            diagnostic(".", "review-range-detectors", "analysis-error", exc)
        )
        project_metrics = {}
    review_range_note = project_metrics.pop("review_range_unavailable", None)
    if review_range_note:
        diagnostics.append(
            diagnostic(".", "review-range-detectors", "not-evaluated", review_range_note)
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

    try:
        repository_source_metrics = (
            detect_role_variable_precedence_collisions(
                scan_root, symbol_index=symbol_index,
                repository_context=repository_context,
            )
            if definition["source_analysis"] and target.is_dir()
            else {}
        )
    except Exception as exc:
        analysis_failures += 1
        diagnostics.append(
            diagnostic(".", "repository-source-detectors", "analysis-error", exc)
        )
        repository_source_metrics = {}
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
        finding_path = _lint_location_path(finding_file, scan_root)
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

    failed_statuses = {"tool-error", "timeout"}

    selection_metadata = {"mode": "recursive-discovery"}
    if file_manifest is not None:
        from .file_manifest import file_manifest_metadata

        selection_metadata = file_manifest_metadata(file_manifest)
    # The public result contract must not depend on whether the repository was
    # acquired under /home/... or a random temporary directory.  Normalize
    # only after filtering and aggregation so detector behavior is unchanged.
    from .report.findings import deduplicate_findings, normalize_finding_paths

    all_findings = normalize_finding_paths(all_findings, scan_root)
    # Overlapping provider roots and repeated detector walks can produce the
    # exact same observation more than once. A repeated finding_id is not
    # independent evidence and must not inflate raw totals.
    all_findings = deduplicate_findings(all_findings)
    all_findings = _annotate_finding_populations(
        all_findings, repository_context, scan_root
    )

    internal_detectors_seconds = time.perf_counter() - internal_started
    try:
        import resource

        peak_value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak_memory_mb = (
            peak_value / (1024 * 1024)
            if sys.platform == "darwin" else peak_value / 1024
        )
    except (ImportError, ValueError):
        peak_memory_mb = None
    for item in diagnostics:
        category, nature = classify_fault(
            item.get("status"), item.get("stage"), None
        )
        if category:
            item.setdefault("category", category)
            item.setdefault("failure_nature", nature)
    fault_diagnostics = [item for item in diagnostics if item.get("category")]
    failed_file_count = sum(
        item.status == "failed" for item in file_stage_results
    )
    if yaml_files and failed_file_count == len(yaml_files):
        analysis_status = "failed"
    elif fault_diagnostics or any(
        result.status not in {"completed", "not-requested"}
        for result in (lint_result, gitleaks_result)
    ):
        analysis_status = "partial"
    elif diagnostics:
        analysis_status = "completed_with_diagnostics"
    else:
        analysis_status = "completed"
    pre_reporting_seconds = time.perf_counter() - scan_started
    cpu_seconds = time.process_time() - cpu_started
    indexed_tasks = (
        repository_context.performance.get("tasks_indexed", 0)
        if repository_context is not None else 0
    )
    symbol_queries = symbol_index.query_count if symbol_index is not None else 0
    run_metadata = {
        "source": source_snapshot.provenance(),
        "profile": profile_metadata(profile),
        "target": str(target.resolve()),
        "file_selection": selection_metadata,
        "tools": {
            "gitleaks": gitleaks_result.status,
            "ansible_lint": lint_result.status,
        },
        "analysis_scope": {
            "internal": {
                "scope": "manifest-selected-files" if file_manifest else "discovered-yaml",
                "selected_files": len(selected_yaml_files),
                "processed_files": len(yaml_files),
                "structurally_analyzed_files": structurally_analyzed,
            },
            "ansible_lint": {
                "scope": context.ansible_lint_scope,
                "target": str(target),
                "population_files": lint_result.metadata.get(
                    "provider_population_files"
                ),
                "population_sha256": lint_result.metadata.get(
                    "provider_population_sha256"
                ),
            },
            "gitleaks": {
                "scope": "requested-target-and-optional-git-range",
                "target": str(target),
            },
        },
        "tool_details": {
            "gitleaks": gitleaks_result.metadata,
            "ansible_lint": lint_result.metadata,
        },
        "symbol_index": (
            symbol_index.metadata()
            if symbol_index is not None
            else {"status": "not-requested"}
        ),
        "repository_context": (
            {
                "status": "completed",
                "selected_population": list(repository_context.selected_population),
                "performance": dict(repository_context.performance),
                "project_model": {
                    "types": list(repository_context.project_model.types),
                    "ansible_roots": list(repository_context.project_model.ansible_roots),
                    "configs": dict(repository_context.project_model.configs),
                    "requirements": list(repository_context.project_model.requirements),
                    "molecule": repository_context.project_model.molecule,
                    "inventory_sources": list(repository_context.project_model.inventory_sources),
                    "configs_by_root": {
                        root: dict(configs)
                        for root, configs in repository_context.project_model.configs_by_root.items()
                    },
                    "dependencies": {
                        "declared_roles": list(
                            repository_context.project_model.dependencies.declared_roles
                        ),
                        "declared_collections": list(
                            repository_context.project_model.dependencies.declared_collections
                        ),
                        "local_collections": list(
                            repository_context.project_model.dependencies.local_collections
                        ),
                        "execution_environment_dependencies": list(
                            repository_context.project_model.dependencies.execution_environment_dependencies
                        ),
                        "source_files": list(
                            repository_context.project_model.dependencies.source_files
                        ),
                    },
                    "dependencies_by_root": {
                        root: {
                            "declared_roles": list(model.declared_roles),
                            "declared_collections": list(
                                model.declared_collections
                            ),
                            "local_collections": list(model.local_collections),
                            "execution_environment_dependencies": list(
                                model.execution_environment_dependencies
                            ),
                            "source_files": list(model.source_files),
                        }
                        for root, model in (
                            repository_context.project_model
                            .dependencies_by_root.items()
                        )
                    },
                },
                "unresolved_includes": sum(
                    edge.resolution not in {"STATIC_RESOLVED"}
                    for edge in repository_context.include_relationships
                ),
            }
            if repository_context is not None
            else {"status": "not-requested"}
        ),
        "file_states": dict(
            sorted(Counter(item.status for item in file_stage_results).items())
        ),
        "timings": {
            "discovery_seconds": discovery_seconds,
            "parse_seconds": parse_seconds,
            "symbol_index_seconds": symbol_index_seconds,
            "internal_detectors_seconds": internal_detectors_seconds,
            "ansible_lint_seconds": lint_result.metadata.get("duration_seconds", 0.0),
            "gitleaks_seconds": gitleaks_result.metadata.get("duration_seconds", 0.0),
            "providers_seconds": providers_seconds,
            "pre_reporting_total_seconds": pre_reporting_seconds,
            "cpu_seconds": cpu_seconds,
            "detectors_seconds": dict(sorted(detector_timing_totals.items())),
        },
        "performance": {
            **(
                dict(repository_context.performance)
                if repository_context is not None else {}
            ),
            "symbol_definitions": (
                len(symbol_index.definitions) if symbol_index is not None else 0
            ),
            "symbol_queries": symbol_queries,
            "cache_hits": (
                repository_context.performance.get("cache_hits", 0)
                if repository_context is not None else 0
            ),
            "cache_misses": (
                repository_context.performance.get("cache_misses", 0)
                if repository_context is not None else 0
            ),
            "peak_memory_mb": peak_memory_mb,
            "yaml_files_per_second": (
                len(yaml_files) / pre_reporting_seconds
                if pre_reporting_seconds > 0 else 0.0
            ),
            "tasks_per_second": (
                indexed_tasks / pre_reporting_seconds
                if pre_reporting_seconds > 0 else 0.0
            ),
            "symbol_queries_per_second": (
                symbol_queries / pre_reporting_seconds
                if pre_reporting_seconds > 0 else 0.0
            ),
            "detectors_skipped": dict(sorted(detector_skip_totals.items())),
        },
    }
    parse_failure_states = {"invalid", "invalid-encoding", "read-error"}
    include_resolution_counts = (
        dict(sorted(Counter(
            str(edge.resolution) for edge in repository_context.include_relationships
        ).items()))
        if repository_context is not None else {}
    )
    run_metadata["analysis_health"] = {
        "status": analysis_status,
        "overall_status": analysis_status,
        "selected_files": len(selected_yaml_files),
        "processed_files": len(yaml_files),
        "parsed_files": sum(
            item.parse_status == "parsed" for item in file_stage_results
        ),
        "parse_failed_files": sum(
            item.parse_status in parse_failure_states for item in file_stage_results
        ),
        "internal_detectors": {
            "completed_files": sum(
                item.status in {"analyzed", "skipped"}
                for item in file_stage_results
            ),
            "partial_files": sum(
                item.status == "partial" for item in file_stage_results
            ),
            "failed_files": sum(
                item.status == "failed" for item in file_stage_results
            ),
        },
        "internal_status": (
            "failed" if failed_file_count == len(yaml_files) and yaml_files
            else "partial" if any(
                item.status in {"partial", "failed"}
                for item in file_stage_results
            )
            else "completed"
        ),
        "provider_status": (
            "completed" if all(
                result.status in {"completed", "not-requested"}
                for result in (lint_result, gitleaks_result)
            ) else "partial"
        ),
        "providers": {
            "ansible_lint": lint_result.status,
            "gitleaks": gitleaks_result.status,
        },
        "include_resolutions": include_resolution_counts,
        "unresolved_dynamic_includes": include_resolution_counts.get("DYNAMIC", 0),
        "unresolved_dynamic_roles": include_resolution_counts.get(
            "DYNAMIC_ROLE", 0
        ),
        "diagnostic_count": len(diagnostics),
        "fault_count": len(fault_diagnostics),
        "faults_by_category": dict(sorted(Counter(
            item["category"] for item in fault_diagnostics
        ).items())),
        "faults_by_nature": dict(sorted(Counter(
            item.get("failure_nature", "UNKNOWN")
            for item in fault_diagnostics
        ).items())),
        "complete": not fault_diagnostics
        and lint_result.status in {"completed", "not-requested"}
        and gitleaks_result.status in {"completed", "not-requested"},
    }
    run_metadata["reproducibility"] = reproducibility_metadata(
        context,
        providers,
        find_config(target),
    )
    reporting_failed = False
    try:
        _write_rollups(
            all_findings,
            summary_rows,
            diagnostics,
            project_metrics,
            output_root,
            scan_root,
            selection_metadata,
            run_metadata,
            gitleaks_result.suppressed_findings,
            explain=explain,
            explain_model=explain_model,
            explain_host=explain_host,
            explain_max_items=explain_max_items,
            explain_timeout=explain_timeout,
            explain_budget=explain_budget,
            explain_checkpoint_dir=explain_checkpoint_dir,
            explain_style=explain_style,
        )
    except Exception as exc:
        reporting_failed = True
        analysis_failures += 1
        analysis_status = "failed"
        failure = diagnostic(
            ".", "output-serialization", "analysis-error", exc
        )
        diagnostics.append(failure)
        health = run_metadata["analysis_health"]
        health.update({
            "status": "failed",
            "complete": False,
            "diagnostic_count": len(diagnostics),
            "fault_count": health.get("fault_count", 0) + 1,
        })
        health["faults_by_category"] = dict(sorted(Counter(
            [
                *(
                    category
                    for category, count in health.get(
                        "faults_by_category", {}
                    ).items()
                    for _ in range(count)
                ),
                failure["category"],
            ]
        ).items()))
        health["faults_by_nature"] = dict(sorted(Counter(
            [
                *(
                    nature
                    for nature, count in health.get(
                        "faults_by_nature", {}
                    ).items()
                    for _ in range(count)
                ),
                failure["failure_nature"],
            ]
        ).items()))
        _write_emergency_failure_state(
            output_root, run_metadata, diagnostics, failure
        )

    print(
        f"[ok] {len(selected_yaml_files)} file(s) selected; "
        f"{len(yaml_files)} source file(s) processed; "
        f"{structurally_analyzed} structurally analyzed; "
        f"gitleaks={gitleaks_result.status}; ansible-lint={lint_result.status}. "
        f"Results under {output_root}"
    )
    if reporting_failed:
        print(
            "[error] Report serialization failed; analysis-failure.json records "
            "a non-clean terminal state."
        )
    else:
        print(f"[ok] {len(all_findings)} total finding(s) across all files.")
    lint_root_errors = sum(
        item.get("status") == "tool-error"
        for item in lint_result.metadata.get("root_results", [])
    )
    return RunResult(
        discovered=len(selected_yaml_files),
        processed=len(yaml_files),
        structurally_analyzed=structurally_analyzed,
        findings=all_findings,
        tool_errors=int(gitleaks_result.status in failed_statuses)
        + max(int(lint_result.status in failed_statuses), lint_root_errors),
        profile=profile,
        parse_failures=sum(
            row["parse_status"] in parse_failure_states for row in summary_rows
        ),
        analysis_failures=analysis_failures,
        file_states=dict(
            sorted(Counter(item.status for item in file_stage_results).items())
        ),
        status=analysis_status,
    ).as_dict()


def _write_rollups(
    all_findings,
    summary_rows,
    diagnostics,
    project_metrics,
    output_root,
    scan_root,
    selection_metadata,
    run_metadata,
    suppressed_external_findings=None,
    explain=False,
    explain_model="qwen2.5-coder:7b",
    explain_host="http://127.0.0.1:11434",
    explain_max_items=None,
    explain_timeout=120.0,
    explain_budget=600.0,
    explain_checkpoint_dir=None,
    explain_style="free",
):
    from .report.output_contract import write_rollups_v3

    paths = write_rollups_v3(
        all_findings,
        summary_rows,
        diagnostics,
        project_metrics,
        output_root,
        scan_root,
        selection_metadata,
        run_metadata,
        suppressed_external_findings,
        explain=explain,
        explain_model=explain_model,
        explain_host=explain_host,
        explain_max_items=explain_max_items,
        explain_timeout=explain_timeout,
        explain_budget=explain_budget,
        explain_checkpoint_dir=explain_checkpoint_dir,
        explain_style=explain_style,
    )
    print(
        f"[ok] Rollups written: {paths['summary']}, {paths['findings']}, "
        f"{paths['sarif']}, {paths['report']}"
    )


def _write_emergency_failure_state(output_root, run_metadata, diagnostics, failure):
    """Persist a minimal failed state when normal report serialization breaks."""
    import json

    from .report.output_contract import CONTRACT_URI, SCHEMA_VERSION

    root = Path(output_root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "run-metadata",
        **run_metadata,
    }
    emergency = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "diagnostics",
        "status": "failed",
        "items": diagnostics,
        "terminal_failure": failure,
    }
    try:
        root.mkdir(parents=True, exist_ok=True)
        (root / "metadata").mkdir(parents=True, exist_ok=True)
        (root / "run_metadata.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
        (root / "metadata/run.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
        (root / "analysis-failure.json").write_text(
            json.dumps(emergency, indent=2), encoding="utf-8"
        )
    except Exception as emergency_error:
        raise RuntimeError(
            "report serialization failed and its failed state could not be persisted"
        ) from emergency_error


def main(argv=None):
    import argparse
    import sys
    from .file_manifest import FileManifestError
    from .detector_config import DetectorConfigError
    from .sources.errors import SourceError

    # Progress output uses emoji (checkmarks, magnifying glass). On Windows,
    # stdout/stderr default to the console's legacy codepage (cp1252), which
    # cannot encode them -- print() then raises UnicodeEncodeError and aborts
    # the whole scan. reconfigure() is a no-op on streams that already
    # support UTF-8 (e.g. redirected to a file, or already UTF-8 consoles).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="backslashreplace")
            except (ValueError, OSError):
                pass

    argv = list(argv) if argv is not None else sys.argv[1:]
    if argv == ["install-tools"]:
        from .external.install_gitleaks import ensure_gitleaks_installed

        ensure_gitleaks_installed()
        return
    if argv and argv[0] == "diff":
        return _diff_main(argv[1:])
    if argv and argv[0] == "github":
        return _github_main(argv[1:])
    if argv and argv[0] == "github-diff":
        return _github_diff_main(argv[1:])
    if argv and argv[0] == "github-pr":
        return _github_pr_main(argv[1:])
    if argv and argv[0] == "gitlab":
        return _gitlab_main(argv[1:])
    if argv and argv[0] == "cache":
        return _cache_main(argv[1:])

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
        choices=(
            "never",
            "error",
            "warning",
            "tool-error",
            "parse-error",
            "analysis-error",
        ),
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
    parser.add_argument(
        "--fail-on-detector-error",
        action="store_true",
        help="Abort a file on the first detector exception (debug/strict mode).",
    )
    parser.add_argument(
        "--ansible-lint-scope",
        choices=("v004-target", "v005-selected"),
        default="v005-selected",
        help=(
            "Use explicit v0.0.5 provider populations or reproduce v0.0.4 "
            "whole-target ansible-lint discovery for paired research."
        ),
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help=(
            "Opt-in: call a local Ollama model once per actionable canonical "
            "occurrence for an AI-generated explanation/suggested fix, surfaced "
            "in findings.sarif/.csv/.txt and canonical/occurrences.*. Requires "
            "Ollama running locally; off by default. A full scan can have "
            "hundreds of occurrences -- combine with --explain-max-items to "
            "bound the number of model calls. Unverified second opinion, not "
            "a verdict -- see ansibleguard.report.llm_explain's module docstring."
        ),
    )
    parser.add_argument(
        "--explain-model", default="qwen2.5-coder:7b",
        help="Ollama model tag to use with --explain (default: qwen2.5-coder:7b)",
    )
    parser.add_argument(
        "--explain-host", default="http://127.0.0.1:11434",
        help="Local Ollama loopback URL for --explain; remote hosts, proxies and redirects are disabled",
    )
    parser.add_argument(
        "--explain-max-items", type=int, default=None,
        help="Cap how many canonical occurrences --explain calls the model for",
    )
    _add_explain_runtime_arguments(parser)
    args = parser.parse_args(argv)

    try:
        from .sources.local import LocalSource
        from .sources.capabilities import validate_profile_capabilities

        with LocalSource(args.target).materialize() as snapshot:
            validate_profile_capabilities(snapshot, args.profile)
            run = analyze_path(
                snapshot.root,
                args.output,
                args.gitleaks_path,
                args.file_manifest,
                args.profile,
                source_snapshot=snapshot,
                fail_on_detector_error=args.fail_on_detector_error,
                ansible_lint_scope=args.ansible_lint_scope,
                explain=args.explain,
                explain_model=args.explain_model,
                explain_host=args.explain_host,
                explain_max_items=args.explain_max_items,
                explain_timeout=args.explain_timeout,
                explain_budget=args.explain_budget,
                explain_checkpoint_dir=args.explain_checkpoint_dir,
                explain_style=args.explain_style,
            )
    except (FileManifestError, DetectorConfigError, SourceError) as exc:
        print(f"Error: {redact_sensitive_text(exc)}", file=sys.stderr)
        sys.exit(2)
    if _should_fail(run, args.fail_on):
        sys.exit(1)


def _should_fail(run, fail_on):
    severities = {finding["severity"] for finding in run.get("findings", [])}
    return {
        "never": False,
        "error": "error" in severities,
        "warning": bool(severities & {"error", "warning"}),
        "tool-error": run.get("tool_errors", 0) > 0,
        "parse-error": run.get("parse_failures", 0) > 0,
        "analysis-error": run.get("analysis_failures", 0) > 0,
    }[fail_on]


def _github_main(argv=None):
    """Materialize an immutable GitHub snapshot, then use the normal analyzer."""
    import argparse
    import sys

    from .detector_config import DetectorConfigError
    from .file_manifest import FileManifestError
    from .profiles import PROFILE_NAMES, profile_definition
    from .sources.errors import SourceError
    from .sources.github.provider import GitHubSource

    parser = argparse.ArgumentParser(
        prog="ansibleguard github",
        description="Analyze an immutable GitHub repository snapshot.",
    )
    parser.add_argument("repository", help="owner/repo or a GitHub repository URL")
    revision = parser.add_mutually_exclusive_group()
    revision.add_argument("--ref", help="Branch or tag to resolve to a commit SHA")
    revision.add_argument("--commit", help="Exact or abbreviated commit to resolve")
    parser.add_argument("--github-host", help="GitHub Enterprise hostname")
    parser.add_argument(
        "--acquisition",
        choices=("auto", "archive", "git"),
        default="auto",
        help="Snapshot acquisition mode (default: profile-aware auto)",
    )
    parser.add_argument("--include-submodules", action="store_true")
    parser.add_argument("--include-lfs", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--cache-backend", choices=("filesystem", "redis"), default="filesystem")
    parser.add_argument("--gitleaks-path", type=Path)
    parser.add_argument(
        "--fail-on",
        choices=(
            "never",
            "error",
            "warning",
            "tool-error",
            "parse-error",
            "analysis-error",
        ),
        default="error",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("ansibleguard-output"))
    parser.add_argument("--file-manifest", type=Path)
    parser.add_argument("--profile", choices=PROFILE_NAMES, default="technical-full")
    args = parser.parse_args(argv)

    definition = profile_definition(args.profile)
    history_required = bool(definition["review_analysis"])
    try:
        from .sources.cache.factory import create_cache_backend

        source = GitHubSource(
            args.repository,
            ref=args.ref,
            commit=args.commit,
            host=args.github_host,
            acquisition=args.acquisition,
            history_required=history_required,
            include_submodules=args.include_submodules,
            include_lfs=args.include_lfs,
            cache=(
                None
                if args.no_cache
                else create_cache_backend(
                    backend=args.cache_backend, cache_dir=args.cache_dir
                )
            ),
        )
        with source.materialize() as snapshot:
            from .sources.capabilities import validate_profile_capabilities

            validate_profile_capabilities(snapshot, args.profile)
            run = analyze_path(
                snapshot.root,
                args.output,
                args.gitleaks_path,
                args.file_manifest,
                args.profile,
                source_snapshot=snapshot,
            )
    except (SourceError, FileManifestError, DetectorConfigError) as exc:
        print(f"Error: {redact_sensitive_text(exc)}", file=sys.stderr)
        raise SystemExit(2)
    if _should_fail(run, args.fail_on):
        raise SystemExit(1)


def _add_remote_comparison_arguments(parser):
    from .profiles import PROFILE_NAMES

    parser.add_argument("-o", "--output", type=Path, default=Path("ansibleguard-output"))
    parser.add_argument("--profile", choices=PROFILE_NAMES, default="pr")
    parser.add_argument("--policy", choices=("observe", "ratchet", "strict"), default="ratchet")
    parser.add_argument("--summary", choices=("changed", "all"), default="changed")
    parser.add_argument("--gitleaks-path", type=Path)
    parser.add_argument("--github-host", help="GitHub Enterprise hostname")
    parser.add_argument("--include-submodules", action="store_true")
    parser.add_argument("--include-lfs", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--cache-backend", choices=("filesystem", "redis"), default="filesystem")
    parser.add_argument("--base-file-manifest", type=Path)
    parser.add_argument("--head-file-manifest", type=Path)


def _compare_github_snapshots(
    *,
    base_source,
    head_source,
    output,
    profile,
    policy,
    summary,
    gitleaks_path,
    base_file_manifest=None,
    head_file_manifest=None,
):
    from .sources.github.workflows import compare_github_snapshots

    return compare_github_snapshots(
        base_source=base_source,
        head_source=head_source,
        output=output,
        profile=profile,
        policy=policy,
        summary=summary,
        gitleaks_path=gitleaks_path,
        base_file_manifest=base_file_manifest,
        head_file_manifest=head_file_manifest,
        analyzer=analyze_path,
    )


def _github_diff_main(argv=None):
    """Compare two immutable GitHub refs using the existing diff engine."""
    import argparse
    import sys

    from .diff_workflow import DiffWorkflowError
    from .sources.errors import SourceError
    from .sources.github.client import GitHubClient
    from .sources.github.provider import GitHubSource
    from .sources.github.urls import parse_github_target

    parser = argparse.ArgumentParser(
        prog="ansibleguard github-diff",
        description="Compare two GitHub refs after resolving exact commit SHAs.",
    )
    parser.add_argument("repository", help="owner/repo or GitHub repository URL")
    parser.add_argument("--base", required=True, help="Base branch, tag, or commit")
    parser.add_argument("--head", required=True, help="Head branch, tag, or commit")
    _add_remote_comparison_arguments(parser)
    args = parser.parse_args(argv)

    try:
        target = parse_github_target(args.repository, host=args.github_host)
        if target.ref or target.commit or target.pull_request:
            raise SourceError("github-diff repository target must not include a revision")
        client = GitHubClient(host=target.host)
        from .sources.cache.factory import create_cache_backend

        cache = None if args.no_cache else create_cache_backend(
            backend=args.cache_backend, cache_dir=args.cache_dir
        )
        common = {
            "acquisition": "git",
            "include_submodules": args.include_submodules,
            "include_lfs": args.include_lfs,
            "client": client,
            "cache": cache,
        }
        payload = _compare_github_snapshots(
            base_source=GitHubSource(target, ref=args.base, **common),
            head_source=GitHubSource(target, ref=args.head, **common),
            output=args.output,
            profile=args.profile,
            policy=args.policy,
            summary=args.summary,
            gitleaks_path=args.gitleaks_path,
            base_file_manifest=args.base_file_manifest,
            head_file_manifest=args.head_file_manifest,
        )
    except (SourceError, DiffWorkflowError, OSError, ValueError) as exc:
        print(
            f"Error: GitHub diff analysis failed: {redact_sensitive_text(exc)}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print((args.output / "diff" / "summary.md").read_text(encoding="utf-8"))
    if payload["policy"]["conclusion"] == "failure":
        raise SystemExit(1)


def _github_pr_main(argv=None):
    """Resolve a GitHub PR (including forks) and reuse remote comparison."""
    import argparse
    import sys

    from .diff_workflow import DiffWorkflowError
    from .sources.errors import SourceError
    from .sources.github.client import GitHubClient
    from .sources.github.comments import GitHubCommentPublisher
    from .sources.github.pr import resolve_pull_request
    from .sources.github.provider import GitHubSource
    from .sources.github.urls import parse_github_target

    parser = argparse.ArgumentParser(
        prog="ansibleguard github-pr",
        description="Analyze a GitHub pull request base/head comparison.",
    )
    parser.add_argument("repository", help="owner/repo or GitHub repository/PR URL")
    parser.add_argument("number", nargs="?", type=int, help="Pull request number")
    parser.add_argument(
        "--comment",
        action="store_true",
        help="Publish the generated summary as a GitHub PR comment",
    )
    _add_remote_comparison_arguments(parser)
    args = parser.parse_args(argv)

    try:
        target = parse_github_target(args.repository, host=args.github_host)
        number = args.number or target.pull_request
        if number is None:
            raise SourceError("github-pr requires a pull request number")
        if target.ref or target.commit:
            raise SourceError("github-pr repository target must not include a revision")
        client = GitHubClient(host=target.host)
        from .sources.cache.factory import create_cache_backend

        cache = None if args.no_cache else create_cache_backend(
            backend=args.cache_backend, cache_dir=args.cache_dir
        )
        pull = resolve_pull_request(client, target.full_name, number)
        common = {
            "host": target.host,
            "acquisition": "git",
            "include_submodules": args.include_submodules,
            "include_lfs": args.include_lfs,
            "client": client,
            "cache": cache,
        }
        payload = _compare_github_snapshots(
            base_source=GitHubSource(
                pull.base_repository, commit=pull.base_sha, **common
            ),
            head_source=GitHubSource(
                pull.head_repository, commit=pull.head_sha, **common
            ),
            output=args.output,
            profile=args.profile,
            policy=args.policy,
            summary=args.summary,
            gitleaks_path=args.gitleaks_path,
            base_file_manifest=args.base_file_manifest,
            head_file_manifest=args.head_file_manifest,
        )
        summary_text = (args.output / "diff" / "summary.md").read_text(
            encoding="utf-8"
        )
        if args.comment:
            GitHubCommentPublisher(client, target.full_name).publish(
                number, summary_text
            )
    except (SourceError, DiffWorkflowError, OSError, ValueError) as exc:
        print(
            f"Error: GitHub PR analysis failed: {redact_sensitive_text(exc)}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print(summary_text)
    if payload["policy"]["conclusion"] == "failure":
        raise SystemExit(1)


def _gitlab_main(argv=None):
    """Materialize an immutable GitLab project, then use the normal analyzer."""
    import argparse
    import sys

    from .detector_config import DetectorConfigError
    from .file_manifest import FileManifestError
    from .profiles import PROFILE_NAMES, profile_definition
    from .sources.cache.factory import create_cache_backend
    from .sources.errors import SourceError
    from .sources.gitlab.provider import GitLabSource

    parser = argparse.ArgumentParser(
        prog="ansibleguard gitlab",
        description="Analyze an immutable GitLab project snapshot.",
    )
    parser.add_argument("repository", help="group/project or a GitLab project URL")
    revision = parser.add_mutually_exclusive_group()
    revision.add_argument("--ref", help="Branch or tag to resolve")
    revision.add_argument("--commit", help="Exact or abbreviated commit to resolve")
    parser.add_argument("--gitlab-host", help="Self-managed GitLab hostname")
    parser.add_argument("--acquisition", choices=("auto", "archive", "git"), default="auto")
    parser.add_argument("--include-submodules", action="store_true")
    parser.add_argument("--include-lfs", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--cache-backend", choices=("filesystem", "redis"), default="filesystem")
    parser.add_argument("--gitleaks-path", type=Path)
    parser.add_argument(
        "--fail-on",
        choices=("never", "error", "warning", "tool-error", "parse-error", "analysis-error"),
        default="error",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("ansibleguard-output"))
    parser.add_argument("--file-manifest", type=Path)
    parser.add_argument("--profile", choices=PROFILE_NAMES, default="technical-full")
    args = parser.parse_args(argv)

    try:
        source = GitLabSource(
            args.repository,
            ref=args.ref,
            commit=args.commit,
            host=args.gitlab_host,
            acquisition=args.acquisition,
            history_required=bool(profile_definition(args.profile)["review_analysis"]),
            include_submodules=args.include_submodules,
            include_lfs=args.include_lfs,
            cache=(
                None
                if args.no_cache
                else create_cache_backend(
                    backend=args.cache_backend, cache_dir=args.cache_dir
                )
            ),
        )
        with source.materialize() as snapshot:
            from .sources.capabilities import validate_profile_capabilities

            validate_profile_capabilities(snapshot, args.profile)
            run = analyze_path(
                snapshot.root,
                args.output,
                args.gitleaks_path,
                args.file_manifest,
                args.profile,
                source_snapshot=snapshot,
            )
    except (SourceError, FileManifestError, DetectorConfigError) as exc:
        print(f"Error: {redact_sensitive_text(exc)}", file=sys.stderr)
        raise SystemExit(2)
    if _should_fail(run, args.fail_on):
        raise SystemExit(1)


def _cache_main(argv=None):
    import argparse
    import json

    from .sources.cache.factory import create_cache_backend
    from .sources.errors import SourceError

    parser = argparse.ArgumentParser(
        prog="ansibleguard cache", description="Inspect or clean the source cache."
    )
    parser.add_argument("action", choices=("info", "clean"))
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--cache-backend", choices=("filesystem", "redis"), default="filesystem")
    parser.add_argument("--older-than", type=int, metavar="DAYS")
    parser.add_argument("--include-pinned", action="store_true")
    args = parser.parse_args(argv)
    try:
        cache = create_cache_backend(
            backend=args.cache_backend, cache_dir=args.cache_dir
        )
        blobs = getattr(cache, "blobs", cache)
        result = (
            blobs.info()
            if args.action == "info"
            else blobs.clean(
                older_than_days=args.older_than,
                include_pinned=args.include_pinned,
            )
        )
    except SourceError as exc:
        parser.error(redact_sensitive_text(exc))
    print(json.dumps(result, indent=2))


def _resolve_commit(repo, revision):
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=repo, capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _diff_main(argv=None):
    """Compare existing scan outputs or scan a Git base and working tree."""
    import argparse
    import json
    import subprocess
    import sys
    import tempfile

    from .detectors.review_metadata import REVIEW_RANGE_OVERRIDE
    from .diff_workflow import (
        DiffWorkflowError,
        analyze_snapshot_jobs,
        compare_outputs,
        git_changed_lines,
        incremental_analysis_scope,
        mark_incremental_output_partial,
    )

    parser = argparse.ArgumentParser(
        prog="ansibleguard diff",
        description="Report findings introduced and fixed by a branch or staged commit.",
    )
    parser.add_argument("target", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--base", default="origin/main", help="Git base revision")
    parser.add_argument("--head", help="Optional Git head revision; default: working tree")
    parser.add_argument("--staged", action="store_true", help="Compare HEAD with the staged index")
    parser.add_argument("--base-results", type=Path, help="Existing base scan output")
    parser.add_argument("--head-results", type=Path, help="Existing head scan output")
    parser.add_argument("-o", "--output", type=Path, default=Path("ansibleguard-output"))
    from .profiles import PROFILE_NAMES

    parser.add_argument("--profile", choices=PROFILE_NAMES, default="pr")
    parser.add_argument("--policy", choices=("observe", "ratchet", "strict"), default="ratchet")
    parser.add_argument("--summary", choices=("changed", "all"), default="changed")
    parser.add_argument("--gitleaks-path", type=Path)
    parser.add_argument(
        "--incremental-plan",
        action="store_true",
        help=(
            "Print the correctness-safe changed-file acceleration plan and "
            "exit; repository-semantic/provider rules remain deferred."
        ),
    )
    parser.add_argument(
        "--run-incremental-file-local",
        action="store_true",
        help=(
            "Run the safe internal file-local subset for changed working-tree "
            "YAML files; writes explicitly partial output and never compares it."
        ),
    )
    parser.add_argument(
        "--parallel-base-head",
        action="store_true",
        help=(
            "Analyze independent immutable base/head worktrees concurrently "
            "when --head is supplied; output remains deterministic."
        ),
    )
    parser.add_argument(
        "--allow-incompatible-snapshots",
        action="store_true",
        help="Compare incompatible base/head provenance (unsafe; recorded in output).",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help=(
            "Opt-in: call a local Ollama model once per introduced, actionable "
            "occurrence for an AI-generated explanation/suggested fix, surfaced "
            "in the SARIF, CSV, and PR annotation/summary outputs. Requires "
            "Ollama running locally; off by default, and a model/network "
            "failure degrades to no enrichment rather than failing the scan. "
            "This is an unverified second opinion, not a verdict -- see "
            "ansibleguard.report.llm_explain's module docstring."
        ),
    )
    parser.add_argument(
        "--explain-model", default="qwen2.5-coder:7b",
        help="Ollama model tag to use with --explain (default: qwen2.5-coder:7b)",
    )
    parser.add_argument(
        "--explain-host", default="http://127.0.0.1:11434",
        help="Local Ollama loopback URL for --explain; remote hosts, proxies and redirects are disabled",
    )
    parser.add_argument(
        "--explain-max-items", type=int, default=None,
        help="Cap how many introduced occurrences --explain calls the model for",
    )
    _add_explain_runtime_arguments(parser)
    args = parser.parse_args(argv)

    target = args.target.resolve()
    repo = target if target.is_dir() else target.parent
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=repo,
            text=True, capture_output=True, check=True,
        ).stdout.strip()
        repo = Path(top).resolve()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(
            "Error: diff target is not inside a Git repository: "
            f"{redact_sensitive_text(exc)}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if bool(args.base_results) != bool(args.head_results):
        parser.error("--base-results and --head-results must be supplied together")
    if args.staged and args.head:
        parser.error("--staged cannot be combined with --head")
    if args.run_incremental_file_local and (
        args.head or args.staged or args.base_results
    ):
        parser.error(
            "--run-incremental-file-local supports only the current working tree "
            "against --base; use --incremental-plan for other comparison modes"
        )

    if args.incremental_plan or args.run_incremental_file_local:
        from .profiles import profile_definition

        changed = git_changed_lines(
            repo,
            "HEAD" if args.staged else args.base,
            None if args.staged else args.head,
            staged=args.staged,
        )
        plan = incremental_analysis_scope(
            changed,
            profile_definition(args.profile)["rules"],
        )
        plan.update(
            {
                "profile": args.profile,
                "base": "HEAD" if args.staged else args.base,
                "head": args.head or ("staged" if args.staged else "working-tree"),
            }
        )
        if args.run_incremental_file_local:
            import hashlib

            incremental_root = args.output / "incremental-file-local"
            scanned = []
            skipped = []
            for relative in plan["changed_files"]:
                candidate = (repo / relative).resolve()
                try:
                    candidate.relative_to(repo)
                except ValueError:
                    skipped.append({"file": relative, "reason": "outside-repository"})
                    continue
                if not candidate.is_file() or candidate.suffix.lower() not in {".yml", ".yaml"}:
                    skipped.append({"file": relative, "reason": "missing-or-not-yaml"})
                    continue
                identifier = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:16]
                analyze_path(
                    candidate,
                    incremental_root / identifier,
                    args.gitleaks_path,
                    profile="incremental-file-local",
                )
                mark_incremental_output_partial(
                    incremental_root / identifier, changed_file=relative
                )
                scanned.append(relative)
            plan.update(
                {
                    "execution": "completed-partial-file-local",
                    "execution_profile": "incremental-file-local",
                    "analysis_health": {"complete": False, "scope": "changed-files-only"},
                    "scanned_files": scanned,
                    "skipped_files": skipped,
                }
            )
            incremental_root.mkdir(parents=True, exist_ok=True)
            (incremental_root / "incremental-plan.json").write_text(
                json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8"
            )
        print(json.dumps(plan, indent=2, sort_keys=True))
        return

    args.output.mkdir(parents=True, exist_ok=True)

    def finish_comparison(changed, head_source_root):
        changed, diff_text = changed
        return compare_outputs(
            base_output, head_output, args.output, repo,
            policy_mode=args.policy, changed_lines=changed, summary_mode=args.summary,
            diff_text=diff_text,
            allow_incompatible_snapshots=args.allow_incompatible_snapshots,
            explain=args.explain,
            explain_model=args.explain_model,
            explain_host=args.explain_host,
            explain_max_items=args.explain_max_items,
            explain_timeout=args.explain_timeout,
            explain_budget=args.explain_budget,
            explain_checkpoint_dir=args.explain_checkpoint_dir,
            explain_style=args.explain_style,
            head_source_root=head_source_root,
        )

    try:
        if args.base_results:
            base_output, head_output = args.base_results, args.head_results
            changed = (
                git_changed_lines(repo, "HEAD", staged=True, return_diff_text=True)
                if args.staged
                else git_changed_lines(repo, args.base, args.head, return_diff_text=True)
            )
            # Results alone do not establish that the current checkout is
            # the source they analyzed. Keep the comparison, omit source-based
            # context and record insufficiency instead of reading another tree.
            payload = finish_comparison(changed, None)
        else:
            base_output = args.output / "base"
            head_output = args.output / "head"
            relative_target = target.relative_to(repo)
            base_sha = None if args.staged else _resolve_commit(repo, args.base)
            head_sha = _resolve_commit(repo, args.head) if args.head else None

            def analyze_side(scan_target, output, gitleaks_path, review_range):
                # Review rules see the PR range on the head side and an empty
                # range on the base side, so history findings are never
                # reported as "fixed" merely because the base is older.
                token = REVIEW_RANGE_OVERRIDE.set(review_range)
                try:
                    analyze_path(scan_target, output, gitleaks_path, profile=args.profile)
                finally:
                    REVIEW_RANGE_OVERRIDE.reset(token)

            with tempfile.TemporaryDirectory(prefix="ansibleguard-diff-") as temporary:
                temporary = Path(temporary)
                base_tree = temporary / "base"
                subprocess.run(
                    ["git", "worktree", "add", "--detach", str(base_tree), "HEAD" if args.staged else args.base],
                    cwd=repo, check=True, capture_output=True, text=True,
                )
                try:
                    if args.staged:
                        analyze_path(base_tree / relative_target, base_output, args.gitleaks_path, profile=args.profile)
                        staged_tree = temporary / "staged"
                        staged_tree.mkdir()
                        prefix = str(staged_tree) + "/"
                        subprocess.run(
                            ["git", "checkout-index", "--all", f"--prefix={prefix}"],
                            cwd=repo, check=True, capture_output=True, text=True,
                        )
                        analyze_path(staged_tree / relative_target, head_output, args.gitleaks_path, profile=args.profile)
                        changed = git_changed_lines(repo, "HEAD", staged=True, return_diff_text=True)
                        payload = finish_comparison(changed, staged_tree)
                    elif args.head:
                        head_tree = temporary / "head"
                        subprocess.run(
                            ["git", "worktree", "add", "--detach", str(head_tree), args.head],
                            cwd=repo, check=True, capture_output=True, text=True,
                        )
                        try:
                            analyze_snapshot_jobs(
                                {
                                    "base": (
                                        base_tree / relative_target,
                                        base_output,
                                        args.gitleaks_path,
                                    ),
                                    "head": (
                                        head_tree / relative_target,
                                        head_output,
                                        args.gitleaks_path,
                                    ),
                                },
                                lambda scan_target, output, gitleaks_path: analyze_side(
                                    scan_target,
                                    output,
                                    gitleaks_path,
                                    (base_sha, head_sha)
                                    if output == head_output
                                    else (base_sha, base_sha),
                                ),
                                parallel=args.parallel_base_head,
                            )
                            changed = git_changed_lines(repo, args.base, args.head, return_diff_text=True)
                            payload = finish_comparison(changed, head_tree)
                        finally:
                            subprocess.run(["git", "worktree", "remove", "--force", str(head_tree)], cwd=repo, capture_output=True)
                    else:
                        analyze_side(base_tree / relative_target, base_output, args.gitleaks_path, (base_sha, base_sha))
                        analyze_side(target, head_output, args.gitleaks_path, (base_sha, _resolve_commit(repo, "HEAD")))
                        changed = git_changed_lines(repo, args.base, return_diff_text=True)
                        payload = finish_comparison(changed, repo)
                finally:
                    subprocess.run(["git", "worktree", "remove", "--force", str(base_tree)], cwd=repo, capture_output=True)
    except (DiffWorkflowError, OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(
            f"Error: diff analysis failed: {redact_sensitive_text(exc)}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print((args.output / "diff" / "summary.md").read_text(encoding="utf-8"))
    if payload["policy"]["conclusion"] == "failure":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

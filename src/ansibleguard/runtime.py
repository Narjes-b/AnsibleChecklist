"""Typed scan orchestration stages shared by the CLI and tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
import platform
import shutil
import sys
from pathlib import Path
import subprocess
import time

from .external.gitleaks import ToolResult
from .redaction import redact_sensitive_text


def _run_text(command, *, cwd=None, timeout=10):
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return (completed.stdout or completed.stderr or "").strip() or None


def _git_sha(path):
    root = Path(path)
    if root.is_file():
        root = root.parent
    return _run_text(["git", "-C", str(root), "rev-parse", "HEAD"], timeout=5)


def _package_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def _installed_collections():
    """Read installed collection manifests without invoking ansible-galaxy."""
    configured = (
        os.environ.get("ANSIBLE_COLLECTIONS_PATH")
        or os.environ.get("ANSIBLE_COLLECTIONS_PATHS")
    )
    collection_roots = (
        configured.split(os.pathsep)
        if configured
        else [
            str(Path.home() / ".ansible" / "collections"),
            str(Path(sys.prefix) / "share" / "ansible" / "collections"),
            "/usr/share/ansible/collections",
        ]
    )
    roots = []
    items = {}
    for configured_root in collection_roots:
        root = Path(configured_root).expanduser() / "ansible_collections"
        if not root.is_dir():
            continue
        roots.append(str(root.resolve()))
        for manifest in root.glob("*/*/MANIFEST.json"):
            try:
                payload = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            info = payload.get("collection_info", {})
            namespace = info.get("namespace") or manifest.parents[1].name
            name = info.get("name") or manifest.parent.name
            items[f"{namespace}.{name}"] = info.get("version")
    return {
        "status": "completed" if roots else "none-found",
        "install_roots": sorted(roots),
        "items": dict(sorted(items.items())),
    }


@lru_cache(maxsize=1)
def _environment_metadata():
    from .task_traversal import STRUCTURAL_METRICS_VERSION
    try:
        from ansible.release import __version__ as ansible_core_version
    except (ImportError, AttributeError):
        ansible_core_version = None

    from .report.findings import RULE_CATALOG

    catalog_payload = {
        rule_id: {
            key: metadata.get(key)
            for key in (
                "level", "category", "description", "confidence", "remediation",
                "status", "taxonomy", "actionability", "policy",
            )
        }
        for rule_id, metadata in sorted(RULE_CATALOG.items())
    }
    catalog_sha256 = hashlib.sha256(
        json.dumps(catalog_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    package_root = Path(__file__).resolve().parents[2]
    environment_files = {
        name: hashlib.sha256((package_root / name).read_bytes()).hexdigest()
        for name in ("requirements.txt", "Dockerfile.research", "collections.lock.yml")
        if (package_root / name).is_file()
    }
    image_digest = os.environ.get("ANSIBLEGUARD_RESEARCH_IMAGE_DIGEST") or None
    ansible_doc = Path(sys.executable).with_name("ansible-doc")
    ansible_doc_executable = (
        str(ansible_doc) if ansible_doc.is_file() else shutil.which("ansible-doc")
    )
    return {
        # Editable distribution metadata can lag the checked-out source.
        "ansibleguard_version": __import__("ansibleguard").__version__,
        "structural_metrics_version": STRUCTURAL_METRICS_VERSION,
        "ansibleguard_git_sha": (
            _git_sha(package_root)
            or os.environ.get("ANSIBLEGUARD_BUILD_GIT_SHA")
        ),
        "execution_environment": "research-container" if image_digest else "local",
        "research_image_digest": image_digest,
        "environment_files": environment_files,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "ansible_core_version": ansible_core_version,
        "ansible_lint_version": _package_version("ansible-lint"),
        "ansible_doc_disabled": os.environ.get(
            "ANSIBLEGUARD_DISABLE_ANSIBLE_DOC", ""
        ).lower() in {"1", "true", "yes"},
        "ansible_doc_executable": ansible_doc_executable,
        "ansible_doc_version": (
            _run_text([ansible_doc_executable, "--version"], timeout=5)
            if ansible_doc_executable else None
        ),
        "ansible_collections_paths": (
            os.environ.get("ANSIBLE_COLLECTIONS_PATH")
            or os.environ.get("ANSIBLE_COLLECTIONS_PATHS")
        ),
        "rule_catalog_sha256": catalog_sha256,
        "rule_count": len(RULE_CATALOG),
        "collections": _installed_collections(),
    }


def reproducibility_metadata(context, providers, config_path=None):
    """Return immutable-enough environment and target evidence for a scan."""
    metadata = dict(_environment_metadata())
    gitleaks_details = providers.gitleaks.metadata
    executable = gitleaks_details.get("executable")
    if executable is None and isinstance(gitleaks_details.get("tree"), dict):
        executable = gitleaks_details["tree"].get("executable")
    metadata["gitleaks_version"] = (
        _run_text([str(executable), "version"], timeout=5) if executable else None
    )
    metadata["target_git_sha"] = _git_sha(context.scan_root)
    metadata["base_sha"] = os.environ.get("ANSIBLEGUARD_BASE_SHA")
    metadata["head_sha"] = os.environ.get("ANSIBLEGUARD_HEAD_SHA")
    metadata["config"] = {
        "path": str(config_path) if config_path else None,
        "sha256": (
            hashlib.sha256(Path(config_path).read_bytes()).hexdigest()
            if config_path
            else None
        ),
    }
    return metadata


@dataclass(frozen=True)
class ScanContext:
    target: Path
    output_root: Path
    scan_root: Path
    profile: str
    definition: dict
    selected_files: tuple[Path, ...]
    source_files: tuple[Path, ...]
    ansible_lint_scope: str = "v005-selected"


@dataclass(frozen=True)
class ProviderResults:
    gitleaks: ToolResult
    ansible_lint: ToolResult


@dataclass
class FileStageResult:
    path: Path
    status: str
    parse_status: str
    document_type: str
    findings: list = field(default_factory=list)
    diagnostics: list = field(default_factory=list)
    structurally_analyzed: bool = False


@dataclass(frozen=True)
class RunResult:
    discovered: int
    processed: int
    structurally_analyzed: int
    findings: list
    tool_errors: int
    profile: str
    parse_failures: int
    analysis_failures: int
    file_states: dict
    status: str = "completed"

    def as_dict(self):
        return {
            "discovered": self.discovered,
            "processed": self.processed,
            "structurally_analyzed": self.structurally_analyzed,
            "findings": self.findings,
            "tool_errors": self.tool_errors,
            "profile": self.profile,
            "parse_failures": self.parse_failures,
            "analysis_failures": self.analysis_failures,
            "file_states": self.file_states,
            "status": self.status,
        }


def prepare_scan_context(
    target,
    output_root,
    profile,
    file_manifest,
    collector,
    ansible_lint_scope="v005-selected",
):
    from .file_manifest import FileManifestError
    from .profiles import profile_definition

    target = Path(target).resolve()
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    definition = profile_definition(profile)
    if ansible_lint_scope not in {"v004-target", "v005-selected"}:
        raise ValueError(
            f"unsupported ansible-lint scope: {ansible_lint_scope}"
        )
    if definition["requires_manifest"] and file_manifest is None:
        raise FileManifestError(
            f"profile {profile} requires --file-manifest so the scanned and "
            "counted source populations are identical"
        )
    selected = tuple(collector(target, file_manifest))
    source = selected if definition["source_analysis"] else ()
    return ScanContext(
        target=target,
        output_root=output_root,
        scan_root=target if target.is_dir() else target.parent,
        profile=profile,
        definition=definition,
        selected_files=selected,
        source_files=tuple(source),
        ansible_lint_scope=ansible_lint_scope,
    )


def _rebase_lint_findings(findings, provider_root, scan_root):
    """Rebase provider-root-relative locations to repository-relative paths."""
    from .external.ansible_lint import lint_issue_line, lint_issue_path

    prefix = _relative_path(provider_root, scan_root)
    rebased = []
    for raw in findings:
        issue = dict(raw)
        location = issue.get("location")
        if isinstance(location, dict):
            issue["location"] = dict(location)
        original = Path(lint_issue_path(issue))
        relative = original.as_posix().removeprefix("./")
        if prefix not in {"", "."} and not original.is_absolute():
            relative = (Path(prefix) / relative).as_posix()
        if "path" in issue:
            issue["path"] = relative
        elif isinstance(issue.get("location"), dict):
            issue["location"]["path"] = relative
        native_rule = str(
            issue.get("check_name") or issue.get("rule_id")
            or issue.get("ruleId") or "ansible-lint-issue"
        )
        message = issue.get("message") or issue.get("description") or ""
        identity = f"{native_rule}|{relative}|{lint_issue_line(issue)}|{message}"
        issue["fingerprint"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        issue["provider_root"] = prefix or "."
        rebased.append(issue)
    return rebased


def _relative_path(path, root):
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _ansible_lint_populations(context, roots):
    """Assign every selected source to exactly one deepest provider root."""
    roots = [Path(root).resolve() for root in roots]
    populations = {root: [] for root in roots}
    for source in sorted({Path(path).resolve() for path in context.selected_files}):
        owners = []
        for root in roots:
            try:
                source.relative_to(root)
            except ValueError:
                continue
            owners.append(root)
        if not owners:
            fallback = context.scan_root.resolve()
            populations.setdefault(fallback, []).append(source)
            continue
        owner = max(owners, key=lambda item: len(item.parts))
        populations[owner].append(source)
    return [
        (root, tuple(files))
        for root, files in populations.items()
        if files
    ]


def _provider_population_metadata(root, files, scan_root):
    paths = [
        _relative_path(path, scan_root)
        for path in sorted(files)
    ]
    encoded = json.dumps(paths, separators=(",", ":"))
    return {
        "provider_root": _relative_path(root, scan_root),
        "provider_population_files": len(paths),
        "provider_population_sha256": hashlib.sha256(
            encoded.encode("utf-8")
        ).hexdigest(),
    }


def _scan_ansible_lint_projects(context, repository_context, scanner):
    if context.ansible_lint_scope == "v004-target":
        result = scanner(context.target)
        selected_metadata = _provider_population_metadata(
            context.scan_root, context.selected_files, context.scan_root
        )
        provider_identity = json.dumps(
            {"scope": "v004-target", "target": "."},
            sort_keys=True, separators=(",", ":"),
        )
        result.metadata.update({
            "provider_population": "v004-target",
            "provider_scope": "v004-target",
            "explicit_population": False,
            "provider_root": ".",
            "provider_population_files": None,
            "provider_population_sha256": hashlib.sha256(
                provider_identity.encode("utf-8")
            ).hexdigest(),
            "ansibleguard_selected_files": selected_metadata[
                "provider_population_files"
            ],
            "ansibleguard_selected_sha256": selected_metadata[
                "provider_population_sha256"
            ],
            "provider_population_note": (
                "Whole-target discovery retained only for paired v0.0.4 "
                "provider comparisons. Provider-discovered file count is "
                "unknown; selected-file fields describe only the parallel "
                "AnsibleGuard cohort."
            ),
        })
        if repository_context is not None:
            _annotate_lint_environment(
                result.findings, repository_context.project_model, "."
            )
        return result
    roots = [context.target]
    if repository_context is not None and context.target.is_dir():
        roots = [
            repository_context.root / relative
            for relative in repository_context.project_model.ansible_roots
        ]
    if context.target.is_file():
        populations = [(context.target, (context.target,))]
    else:
        populations = _ansible_lint_populations(context, roots)
    results = []
    for root, population_files in populations:
        result = scanner(
            root,
            files=None if root.is_file() else population_files,
        )
        population_metadata = _provider_population_metadata(
            root, population_files, context.scan_root
        )
        result.metadata.update(population_metadata)
        result.metadata["provider_scope"] = "v005-selected"
        if repository_context is not None:
            _annotate_lint_environment(
                result.findings,
                repository_context.project_model,
                _relative_path(root, context.scan_root),
            )
        results.append((root, population_files, result))
    if (
        len(results) == 1
        and results[0][0].resolve() == context.scan_root.resolve()
    ):
        root, _population_files, result = results[0]
        result.metadata.setdefault("provider_root", ".")
        result.metadata.setdefault("provider_population", "detected_ansible_root")
        return result

    findings = []
    suppressed = []
    root_details = []
    provider_diagnostics = []
    for root, population_files, result in results:
        findings.extend(_rebase_lint_findings(result.findings, root, context.scan_root))
        suppressed.extend(result.suppressed_findings)
        for item in result.metadata.get("provider_diagnostics", []):
            provider_diagnostics.append(
                {**item, "provider_root": _relative_path(root, context.scan_root)}
            )
        root_details.append(
            {
                "root": _relative_path(root, context.scan_root),
                "status": result.status,
                "message": result.message,
                "metadata": result.metadata,
                "finding_count": len(result.findings),
                **_provider_population_metadata(
                    root, population_files, context.scan_root
                ),
            }
        )
    statuses = [result.status for _root, _files, result in results]
    if statuses and all(status == "completed" for status in statuses):
        status = "completed"
    elif statuses and all(status == "tool-error" for status in statuses):
        status = "tool-error"
    else:
        status = "partial"
    return ToolResult(
        status,
        findings=findings,
        message="; ".join(
            f"{item['root']}: {item['message']}"
            for item in root_details if item["message"]
        ),
        metadata={
            "provider": "ansible-lint",
            "provider_scope": "v005-selected",
            "provider_population": "detected_ansible_roots",
            "provider_roots": [item["root"] for item in root_details],
            "provider_population_files": sum(
                item["provider_population_files"] for item in root_details
            ),
            "provider_population_sha256": hashlib.sha256(
                json.dumps(
                    [
                        (item["root"], item["provider_population_sha256"])
                        for item in root_details
                    ],
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
            "root_results": root_details,
            "provider_diagnostics": provider_diagnostics,
            "provider_diagnostic_count": len(provider_diagnostics),
        },
        suppressed_findings=suppressed,
    )


def _annotate_lint_environment(findings, project_model, provider_root=None):
    """Attach dependency evidence to environment-sensitive syntax results."""
    dependencies = project_model.dependencies_by_root.get(
        provider_root, project_model.dependencies
    ) if provider_root is not None else project_model.dependencies
    installed = set(
        _environment_metadata().get("collections", {}).get("items", {})
    )
    declared = set(dependencies.declared_collections)
    missing = sorted(declared - installed)
    available = sorted(declared & installed)
    evidence = {
        "declared_roles": list(dependencies.declared_roles),
        "declared_collections": sorted(declared),
        "installed_declared_collections": available,
        "declared_but_not_installed_collections": missing,
        "local_collections": list(dependencies.local_collections),
        "execution_environment_dependencies": list(
            dependencies.execution_environment_dependencies
        ),
        "dependency_source_files": list(dependencies.source_files),
        "provider_root": provider_root,
    }
    for finding in findings:
        native_rule = str(
            finding.get("check_name")
            or finding.get("rule_id")
            or finding.get("ruleId")
            or ""
        )
        if not native_rule.startswith("syntax-check["):
            continue
        finding["analysis_population"] = (
            "environment_dependent_provider_finding"
        )
        finding["environment_dependent"] = True
        finding["environment_evidence"] = evidence
        if missing:
            interpretation = "declared_dependency_not_installed"
        elif dependencies.local_collections:
            interpretation = "local_collection_or_provider_resolution"
        else:
            interpretation = "undeclared_dependency_or_custom_module"
        finding["environment_interpretation"] = interpretation


def run_external_providers(
    context: ScanContext, gitleaks_path=None, repository_context=None,
    concurrent=True,
):
    from .external.ansible_lint import scan_with_ansible_lint
    from .external.gitleaks import scan_git_range_with_gitleaks, scan_with_gitleaks
    from .external.install_gitleaks import GITLEAKS_PATH
    from .profiles import provider_enabled

    def run_gitleaks_branch():
        started = time.perf_counter()
        try:
            if provider_enabled(context.profile, "gitleaks"):
                binary = gitleaks_path or GITLEAKS_PATH
                tree = scan_with_gitleaks(context.target, binary)
                base = os.environ.get("ANSIBLEGUARD_BASE_SHA")
                head = os.environ.get("ANSIBLEGUARD_HEAD_SHA")
                if context.target.is_dir() and base and head:
                    history = scan_git_range_with_gitleaks(
                        context.target, binary, base, head
                    )
                    statuses = {tree.status, history.status}
                    combined_status = (
                        "completed" if statuses == {"completed"}
                        else "timeout" if statuses == {"timeout"}
                        else "tool-error" if statuses == {"tool-error"}
                        else "partial"
                    )
                    result = ToolResult(
                        combined_status,
                        findings=tree.findings + history.findings,
                        message="; ".join(
                            value for value in (tree.message, history.message) if value
                        ),
                        metadata={
                            "provider": "gitleaks",
                            "tree": tree.metadata,
                            "git_range": history.metadata,
                        },
                        suppressed_findings=(
                            tree.suppressed_findings + history.suppressed_findings
                        ),
                    )
                else:
                    result = tree
            else:
                result = ToolResult(
                    "not-requested",
                    message=f"GitLeaks is not requested by profile {context.profile}.",
                )
        except Exception as exc:
            result = ToolResult(
                "tool-error", message=f"gitleaks adapter failure: {exc}",
                metadata={
                    "provider": "gitleaks",
                    "provider_diagnostics": [{
                        "category": "PROVIDER_ERROR",
                        "message": f"gitleaks adapter failure: {type(exc).__name__}",
                    }],
                },
            )
        result.metadata.setdefault(
            "duration_seconds", time.perf_counter() - started
        )
        return result

    def run_lint_branch():
        started = time.perf_counter()
        try:
            if provider_enabled(context.profile, "ansible-lint"):
                result = _scan_ansible_lint_projects(
                    context, repository_context, scan_with_ansible_lint
                )
            else:
                result = ToolResult(
                    "not-requested",
                    message=f"ansible-lint is not requested by profile {context.profile}.",
                )
        except Exception as exc:
            result = ToolResult(
                "tool-error", message=f"ansible-lint adapter failure: {exc}",
                metadata={
                    "provider": "ansible-lint",
                    "provider_diagnostics": [{
                        "category": "PROVIDER_SCHEMA_ERROR",
                        "message": (
                            "ansible-lint adapter failure: "
                            f"{type(exc).__name__}"
                        ),
                    }],
                },
            )
        result.metadata.setdefault(
            "duration_seconds", time.perf_counter() - started
        )
        return result

    both_enabled = all(
        provider_enabled(context.profile, name)
        for name in ("gitleaks", "ansible-lint")
    )
    if concurrent and both_enabled:
        with ThreadPoolExecutor(max_workers=2) as executor:
            gitleaks_future = executor.submit(run_gitleaks_branch)
            lint_future = executor.submit(run_lint_branch)
            gitleaks = gitleaks_future.result()
            lint = lint_future.result()
        mode = "concurrent"
    else:
        gitleaks = run_gitleaks_branch()
        lint = run_lint_branch()
        mode = "sequential"
    gitleaks.metadata.setdefault("provider_execution_mode", mode)
    lint.metadata.setdefault("provider_execution_mode", mode)
    return ProviderResults(gitleaks=gitleaks, ansible_lint=lint)


def build_repository_context_stage(context: ScanContext):
    """Parse and index the selected YAML population once."""
    from .analysis_context import build_repository_analysis_context

    if (
        not context.definition["source_analysis"]
        and "ansible-lint" not in context.definition.get("providers", ())
    ):
        return None
    repository_context = build_repository_analysis_context(
        context.scan_root,
        context.selected_files,
        cache_dir=context.output_root / ".cache" / "parsed",
    )
    metadata_rules = {
        "deprecated-modules", "deprecated-module-option",
        "credential-log-exposure",
    }
    if metadata_rules & set(context.definition.get("rules", ())):
        from .module_metadata import build_module_metadata_index

        metadata, telemetry = build_module_metadata_index(
            task.action
            for tasks in repository_context.tasks_by_file.values()
            for task in tasks
            if task.action
        )
        repository_context = repository_context.with_module_metadata(
            metadata, telemetry
        )
    return repository_context


def build_symbol_index_stage(context: ScanContext, repository_context=None):
    """Validate all effective configs, then build one provenance index."""
    from .detector_config import (
        load_detector_config,
        validate_detector_configs,
    )
    from .symbol_index import build_repository_symbol_index

    validate_detector_configs([context.target, *context.selected_files])
    if not context.definition["source_analysis"]:
        return None
    known_variables_by_file = {
        path: tuple(load_detector_config(path)["rules"].get("known_variables", []))
        for path in context.selected_files
    }
    custom_module_facts_by_file = {
        path: load_detector_config(path)["rules"].get("custom_module_facts", {})
        for path in context.selected_files
    }
    return build_repository_symbol_index(
        context.target,
        files=context.selected_files,
        known_variables_by_file=known_variables_by_file,
        custom_module_facts_by_file=custom_module_facts_by_file,
        parsed_documents=(
            repository_context.parsed_documents
            if repository_context is not None
            else None
        ),
        inventory_sources=(
            repository_context.project_model.inventory_sources
            if repository_context is not None else None
        ),
    )


def classify_fault(status, stage, error=None):
    """Map operational failures to the stable v0.0.5 fault taxonomy."""
    normalized = str(status or "").lower()
    stage = str(stage or "").lower()
    if normalized == "timeout" or isinstance(error, TimeoutError):
        return "TIMEOUT", "TIMEOUT"
    if isinstance(error, MemoryError):
        return "MEMORY_ERROR", "ENVIRONMENT"
    if isinstance(error, PermissionError):
        return "FILESYSTEM_PERMISSION_ERROR", "ENVIRONMENT"
    if normalized in {"invalid", "invalid-encoding", "read-error"}:
        return "PARSER_ERROR", "DETERMINISTIC_INPUT"
    if normalized == "provider-schema-error":
        return "PROVIDER_SCHEMA_ERROR", "BUG"
    if normalized == "provider-environment-error":
        return "PROVIDER_ENVIRONMENT_ERROR", "ENVIRONMENT"
    if normalized in {"provider-error", "tool-error"}:
        return "PROVIDER_ERROR", "ENVIRONMENT"
    if normalized != "analysis-error":
        return None, None
    if any(token in stage for token in ("write", "serialization", "reporting")):
        return "OUTPUT_SERIALIZATION_ERROR", "BUG"
    if "cache" in stage:
        return "CACHE_ERROR", "BUG"
    if "static-resolution" in stage:
        return "STATIC_RESOLUTION_ERROR", "DETERMINISTIC_INPUT"
    return "INTERNAL_DETECTOR_EXCEPTION", "BUG"


def diagnostic(file, stage, status, message):
    category, nature = classify_fault(status, stage, message)
    item = {
        "file": str(file),
        "stage": stage,
        "status": status,
        "message": redact_sensitive_text(message),
    }
    if category:
        item["category"] = category
        item["failure_nature"] = nature
    return item

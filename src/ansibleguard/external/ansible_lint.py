import subprocess
import json
import re
import os
from pathlib import Path
import shutil
import sys
import tempfile
import hashlib
from importlib.metadata import PackageNotFoundError, version

from .gitleaks import ToolResult
from ansibleguard.redaction import redact_sensitive_text


def _read_bounded(path, limit):
    with Path(path).open("rb") as stream:
        return stream.read(limit + 1)


# ansible-lint applies a project config's ``write_list`` even without ``--fix``
# and the command line cannot disable it, so the scanned tree is protected by a
# snapshot taken before the subprocess and restored after it.
_GUARDED_SUFFIXES = (".yml", ".yaml")
_LINT_ARTIFACT_DIRS = (".ansible", "__pycache__")


def _snapshot_workspace(root, backup_dir):
    """Copy every YAML file below ``root`` so a provider rewrite can be undone."""
    root = Path(root)
    snapshot = {}
    existing_dirs = set()
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name != ".git"]
        current_path = Path(current)
        existing_dirs.update(current_path / name for name in dirs)
        in_artifact_dir = any(part in _LINT_ARTIFACT_DIRS for part in current_path.relative_to(root).parts)
        if in_artifact_dir:
            # Pre-existing artifact content (often gitignored) is remembered so
            # only files created during this run are removed afterwards.
            existing_dirs.update(current_path / name for name in files)
        for name in files:
            path = current_path / name
            guarded = path.suffix.lower() in _GUARDED_SUFFIXES or name == ".ansible-lint"
            if path.is_symlink() or not guarded:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            copy = Path(backup_dir) / str(len(snapshot))
            shutil.copy2(path, copy)
            snapshot[path] = (stat.st_size, stat.st_mtime_ns, copy)
    return snapshot, existing_dirs


def _restore_workspace(root, snapshot, existing_dirs):
    """Undo provider writes; return a JSON-ready record of what was changed."""
    root = Path(root)
    restored, removed = [], []
    for path, (size, mtime_ns, copy) in snapshot.items():
        try:
            stat = path.stat()
            unchanged = stat.st_size == size and stat.st_mtime_ns == mtime_ns
        except OSError:
            unchanged = False
        if not unchanged:
            shutil.copy2(copy, path)
            restored.append(path.relative_to(root).as_posix())
    for current, dirs, files in os.walk(root, topdown=True):
        dirs[:] = [name for name in dirs if name != ".git"]
        current_path = Path(current)
        in_artifact_dir = any(part in _LINT_ARTIFACT_DIRS for part in current_path.relative_to(root).parts)
        for name in list(dirs):
            candidate = current_path / name
            if candidate in existing_dirs:
                continue
            if name in _LINT_ARTIFACT_DIRS or in_artifact_dir:
                shutil.rmtree(candidate, ignore_errors=True)
                dirs.remove(name)
                removed.append(candidate.relative_to(root).as_posix() + "/")
        for name in files:
            candidate = current_path / name
            if candidate in existing_dirs or candidate in snapshot:
                continue
            if in_artifact_dir or (".tmp." in name and candidate.suffix.lower() in _GUARDED_SUFFIXES):
                candidate.unlink(missing_ok=True)
                removed.append(candidate.relative_to(root).as_posix())
    return {
        "guarded_files": len(snapshot),
        "restored_files": sorted(restored),
        "removed_artifacts": sorted(removed),
    }


def _ansible_lint_executable():
    """Find ansible-lint beside the running Python before consulting PATH.

    Console scripts installed in a virtual environment are siblings of its
    Python executable, but callers may invoke ``.venv/bin/pytest`` without
    adding ``.venv/bin`` to PATH.
    """
    sibling = Path(sys.executable).with_name("ansible-lint")
    if sibling.is_file():
        return str(sibling)
    return shutil.which("ansible-lint") or "ansible-lint"


def lint_issue_path(issue):
    location = issue.get("location")
    location = location if isinstance(location, dict) else {}
    value = issue.get("path") or location.get("path") or ""
    return value if isinstance(value, str) else ""


def lint_issue_line(issue):
    location = issue.get("location")
    location = location if isinstance(location, dict) else {}
    positions = location.get("positions")
    positions = positions if isinstance(positions, dict) else {}
    begin_position = positions.get("begin")
    begin_position = begin_position if isinstance(begin_position, dict) else {}
    lines = location.get("lines")
    lines = lines if isinstance(lines, dict) else {}
    value = (
        issue.get("line") or location.get("line")
        or begin_position.get("line") or lines.get("begin") or 1
    )
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1


def _lint_item_schema_error(item):
    """Return a reason when provider-owned nested fields are malformed."""
    location = item.get("location")
    if location is not None and not isinstance(location, dict):
        return "location must be an object"
    location = location or {}
    for owner, key in ((item, "path"), (location, "path")):
        if (
            key in owner
            and owner[key] is not None
            and not isinstance(owner[key], str)
        ):
            return f"{key} must be a string"
    for key in ("positions", "lines"):
        if (
            key in location
            and location[key] is not None
            and not isinstance(location[key], dict)
        ):
            return f"location.{key} must be an object"
    positions = location.get("positions") or {}
    if (
        "begin" in positions
        and positions["begin"] is not None
        and not isinstance(positions["begin"], dict)
    ):
        return "location.positions.begin must be an object"
    line_values = [item.get("line"), location.get("line")]
    begin = positions.get("begin") or {}
    lines = location.get("lines") or {}
    line_values.extend((begin.get("line"), lines.get("begin")))
    for value in line_values:
        if value is None:
            continue
        try:
            if int(value) < 1:
                return "line number must be a positive integer"
        except (TypeError, ValueError):
            return "line number must be an integer"
    return None


# ansible-lint renders Python sets in some messages ("{'ccp', 'global'}"); set
# order changes between processes, which would change message-based
# fingerprints and occurrence IDs from run to run.
_SET_LITERAL_RE = re.compile(r"\{('[^'{}]*'(?:,\s*'[^'{}]*')+)\}")


def _stable_set_literals(text):
    return _SET_LITERAL_RE.sub(
        lambda match: "{" + ", ".join(sorted(part.strip() for part in match.group(1).split(","))) + "}",
        text,
    )


def _normalize_lint_issues(issues, working_directory):
    """Remove checkout-location noise from paths, messages, and fingerprints."""
    root = Path(working_directory).resolve()
    root_spellings = {str(root), root.as_posix()}
    for issue in issues:
        raw_path = Path(lint_issue_path(issue))
        if raw_path.is_absolute():
            try:
                relative_path = raw_path.resolve().relative_to(root).as_posix()
            except ValueError:
                relative_path = raw_path.as_posix()
        else:
            relative_path = raw_path.as_posix().removeprefix("./")

        if "path" in issue:
            issue["path"] = relative_path
        elif isinstance(issue.get("location"), dict):
            issue["location"]["path"] = relative_path

        for message_key in ("message", "description"):
            if not isinstance(issue.get(message_key), str):
                continue
            for spelling in root_spellings:
                issue[message_key] = issue[message_key].replace(
                    spelling, "<repo>"
                )

        rule_id = (
            issue.get("check_name")
            or issue.get("rule_id")
            or issue.get("ruleId")
            or "ansible-lint-issue"
        )
        for message_key in ("message", "description"):
            if isinstance(issue.get(message_key), str):
                issue[message_key] = _stable_set_literals(issue[message_key])
        message = issue.get("message") or issue.get("description") or ""
        identity = f"{rule_id}|{relative_path}|{lint_issue_line(issue)}|{message}"
        issue["fingerprint"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return issues


def _validate_lint_payload(payload):
    """Return schema-valid findings and provider diagnostics.

    Provider adapter/schema failures are evidence about analysis health, never
    repository code smells.  Mixed payloads remain useful but make the provider
    result partial.
    """
    if not isinstance(payload, list):
        raise TypeError(
            f"ansible-lint JSON root must be a list, got {type(payload).__name__}"
        )
    findings = []
    diagnostics = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            diagnostics.append(
                {
                    "category": "PROVIDER_SCHEMA_ERROR",
                    "index": index,
                    "value_type": type(item).__name__,
                    "item_preview": redact_sensitive_text(repr(item)[:240]),
                    "message": (
                        "ansible-lint result item must be an object; "
                        f"index={index}, type={type(item).__name__}"
                    ),
                }
            )
            continue
        schema_error = _lint_item_schema_error(item)
        if schema_error:
            diagnostics.append({
                "category": "PROVIDER_SCHEMA_ERROR",
                "index": index,
                "value_type": "object",
                "item_preview": redact_sensitive_text(repr(item)[:240]),
                "message": (
                    "malformed ansible-lint result at item "
                    f"{index}: {schema_error}"
                ),
            })
            continue
        native_rule = str(
            item.get("check_name") or item.get("rule_id") or item.get("ruleId") or ""
        )
        if native_rule == "internal-error" or native_rule.startswith("internal-error["):
            diagnostics.append(
                {
                    "category": "PROVIDER_ERROR",
                    "native_rule_id": native_rule,
                    "message": redact_sensitive_text(
                        item.get("message")
                        or item.get("description")
                        or "ansible-lint internal error"
                    ),
                    "location": item.get("location") or item.get("path"),
                }
            )
            continue
        item = dict(item)
        if native_rule.startswith("syntax-check["):
            item["analysis_population"] = "environment_dependent_provider_finding"
            item["environment_dependent"] = True
        findings.append(item)
    return findings, diagnostics


# ansible-lint 26.x reports task-level matches at the line *after* the task's
# last line (the start of the next YAML node), including matches that carry a
# column. ``yaml[...]`` and load/syntax problems are reported at their exact
# line. Without realignment, findings land on the following task.
_EXACT_LINE_RULE_PREFIXES = ("yaml", "load-failure", "syntax-check", "internal-error", "parser-error", "schema")


def _ansible_lint_major(version_text):
    try:
        return int(str(version_text).split(".", 1)[0])
    except (TypeError, ValueError):
        return None


def _align_task_lines(issues, working_directory):
    """Move task-level ansible-lint lines back onto the task they describe."""
    from ansibleguard.detectors.shell_instead_of_module import _collect_all_tasks
    from ansibleguard.detectors.source_lines import load_with_lines, source_line

    root = Path(working_directory).resolve()
    starts_by_file = {}
    aligned = 0
    for issue in issues:
        rule_id = str(issue.get("check_name") or issue.get("rule_id") or "")
        if rule_id.startswith(_EXACT_LINE_RULE_PREFIXES):
            continue
        relative = lint_issue_path(issue)
        source = Path(relative)
        source = (source if source.is_absolute() else root / source).resolve()
        if source not in starts_by_file:
            document = load_with_lines(source) if source.is_file() else None
            tasks = _collect_all_tasks(document) if document else []
            starts_by_file[source] = sorted({source_line(task) for task in tasks})
        reported = lint_issue_line(issue)
        earlier = [start for start in starts_by_file[source] if start < reported]
        if not earlier:
            continue
        corrected = earlier[-1]
        issue["provider_reported_line"] = reported
        issue["line"] = corrected
        location = issue.get("location")
        if isinstance(location, dict):
            if isinstance(location.get("lines"), dict):
                location["lines"]["begin"] = corrected
            positions = location.get("positions")
            if isinstance(positions, dict) and isinstance(positions.get("begin"), dict):
                positions["begin"]["line"] = corrected
        aligned += 1
    return aligned


def _normalize_validated_payload(payload, working_directory, metadata):
    findings, provider_diagnostics = _validate_lint_payload(payload)
    for item in provider_diagnostics:
        item.setdefault("provider_root", str(Path(working_directory).resolve()))
        item.setdefault("returncode", metadata.get("returncode"))
        item.setdefault("json_root_type", type(payload).__name__)
    normalized = _normalize_lint_issues(findings, working_directory)
    major = _ansible_lint_major(metadata.get("version"))
    if major is not None and major >= 26:
        metadata["task_line_alignment"] = {
            "rule": "task-level matches moved from next-node line to task start",
            "aligned_findings": _align_task_lines(normalized, working_directory),
        }
    normalized, read_only_suppressions = _filter_read_only_command_noise(
        normalized, working_directory
    )
    filtered = _apply_project_suppressions(
        normalized, metadata.get("config_path") or working_directory
    )
    metadata["provider_diagnostics"] = provider_diagnostics
    metadata["provider_diagnostic_count"] = len(provider_diagnostics)
    metadata["suppressed_read_only_command_findings"] = len(
        read_only_suppressions
    )
    return filtered, read_only_suppressions, provider_diagnostics


def scan_with_ansible_lint(
    target_path, output_format="json", timeout=None, files=None
):
    """Run ansible-lint and distinguish a clean scan from a tool failure."""
    target_path = Path(target_path).resolve()
    working_directory = target_path if target_path.is_dir() else target_path.parent
    # With ansible-lint 26.x, passing an explicit ``.`` treats the directory
    # itself as a lintable and can skip recursively discovered playbooks. Run
    # targetless from the project root for repository scans; retain an explicit
    # basename when the caller requested one file.
    lint_targets = []
    if files is not None:
        for source in files:
            source = Path(source).resolve()
            try:
                lint_targets.append(source.relative_to(working_directory).as_posix())
            except ValueError as exc:
                raise ValueError(
                    f"ansible-lint population file is outside provider root: {source}"
                ) from exc
    elif target_path.is_file():
        lint_targets.append(target_path.name)
    executable = _ansible_lint_executable()
    config_path = _find_ansible_lint_project_config(working_directory)
    try:
        package_version = version("ansible-lint")
    except PackageNotFoundError:
        package_version = None
    metadata = {
        "provider": "ansible-lint",
        "version": package_version,
        "executable": executable,
        "cwd": str(working_directory),
        "target": lint_targets or "<project-discovery>",
        "explicit_population": files is not None,
        "format": output_format,
        "dependency_mode": "offline-no-auto-install",
        "config": str(config_path) if config_path else "defaults",
        "config_path": str(config_path) if config_path else None,
        "config_sha256": (
            hashlib.sha256(config_path.read_bytes()).hexdigest()
            if config_path
            else None
        ),
    }
    timeout = float(
        timeout
        if timeout is not None
        else os.environ.get("ANSIBLEGUARD_ANSIBLE_LINT_TIMEOUT", "600")
    )
    metadata["timeout_seconds"] = timeout
    max_output_bytes = int(os.environ.get("ANSIBLEGUARD_PROVIDER_MAX_OUTPUT_BYTES", str(64 * 1024 * 1024)))
    metadata["max_output_bytes"] = max_output_bytes
    try:
        cmd = [executable, "--offline"]
        if config_path is not None:
            cmd += ["-c", str(config_path)]
        # Improvement C: Skip fqcn rules if repo targets Ansible < 2.9
        if not _fqcn_applicable(working_directory):
            for fqcn_rule in _FQCN_RULES:
                cmd += ["--skip-list", fqcn_rule]
        if output_format == "json":
            cmd += ["-f", "json"]
        # Keep operands after provider options so unusual relative paths cannot
        # be mistaken for command-line switches by the provider parser.
        cmd.extend(lint_targets)
        env = os.environ.copy()
        # Repository plugins are imported during linting; keep their bytecode
        # out of the scanned tree.
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        with tempfile.TemporaryDirectory(
            prefix="ansibleguard-ansible-lint-"
        ) as provider_tmp:
            env["ANSIBLE_LOCAL_TEMP"] = str(
                Path(provider_tmp) / "ansible-local"
            )
            stdout_path = Path(provider_tmp) / "stdout"
            stderr_path = Path(provider_tmp) / "stderr"
            backup_dir = Path(provider_tmp) / "workspace-snapshot"
            backup_dir.mkdir()
            snapshot, existing_dirs = _snapshot_workspace(working_directory, backup_dir)
            try:
                with stdout_path.open("wb") as stdout_stream, stderr_path.open("wb") as stderr_stream:
                    result = subprocess.run(
                        cmd,
                        stdout=stdout_stream,
                        stderr=stderr_stream,
                        env=env,
                        cwd=working_directory,
                        timeout=timeout,
                    )
            finally:
                metadata["workspace_guard"] = _restore_workspace(
                    working_directory, snapshot, existing_dirs
                )
            # Test doubles may return captured strings directly. Real provider
            # runs write to files, so Python never buffers unbounded output.
            direct_stdout = getattr(result, "stdout", None)
            direct_stderr = getattr(result, "stderr", None)
            stdout_bytes = (
                direct_stdout.encode() if isinstance(direct_stdout, str)
                else direct_stdout if isinstance(direct_stdout, bytes)
                else _read_bounded(stdout_path, max_output_bytes)
            )
            stderr_bytes = (
                direct_stderr.encode() if isinstance(direct_stderr, str)
                else direct_stderr if isinstance(direct_stderr, bytes)
                else _read_bounded(stderr_path, max_output_bytes)
            )
            output_bytes = (
                len(stdout_bytes) + len(stderr_bytes)
                if direct_stdout is not None or direct_stderr is not None
                else stdout_path.stat().st_size + stderr_path.stat().st_size
            )
            result.stdout = stdout_bytes.decode("utf-8", errors="replace")
            result.stderr = stderr_bytes.decode("utf-8", errors="replace")
        metadata["isolated_temporary_directory"] = True
    except subprocess.TimeoutExpired as exc:
        return ToolResult(
            "timeout",
            message=f"ansible-lint exceeded {timeout:g} seconds",
            metadata={
                **metadata,
                "failure_category": "TIMEOUT",
                "failure_nature": "TIMEOUT",
            },
        )
    except (FileNotFoundError, OSError) as exc:
        return ToolResult("tool-error", message=str(exc), metadata=metadata)

    if output_bytes > max_output_bytes:
        return ToolResult(
            "tool-error",
            message=f"ansible-lint output exceeded {max_output_bytes} bytes",
            metadata={
                **metadata,
                "failure_category": "OUTPUT_LIMIT",
                "failure_nature": "RESOURCE_LIMIT",
                "output_bytes": output_bytes,
            },
        )

    if result.returncode not in (0, 2):
        # ansible-lint can return a non-standard status while still emitting
        # valid JSON findings (for example when a project dependency or one
        # fixture fails). Preserve those findings as partial evidence instead
        # of treating the whole provider as unavailable.
        try:
            metadata["returncode"] = result.returncode
            partial_findings = json.loads(result.stdout or "[]")
            filtered, read_only_suppressions, _provider_diagnostics = (
                _normalize_validated_payload(
                    partial_findings, working_directory, metadata
                )
            )
            return ToolResult(
                "partial",
                filtered,
                message=(result.stderr or "").strip(),
                metadata=metadata,
                suppressed_findings=read_only_suppressions,
            )
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as exc:
            primary_message = (
                result.stderr or result.stdout or "Unknown ansible-lint failure"
            ).strip()
            return ToolResult(
                "tool-error",
                message=primary_message,
                metadata={
                    **metadata,
                    "returncode": result.returncode,
                    "provider_diagnostics": [{
                        # A non-zero provider execution with stderr is an
                        # environment/tool failure. Invalid JSON is secondary
                        # evidence, not a second AnsibleGuard adapter bug.
                        "category": "PROVIDER_ERROR",
                        "returncode": result.returncode,
                        "provider_root": str(working_directory),
                        "json_root_type": "decode-failed",
                        "exception_type": type(exc).__name__,
                        "exception_message": redact_sensitive_text(str(exc)),
                        "message": (
                            "ansible-lint execution failed before producing "
                            f"valid JSON (return code {result.returncode}): "
                            f"{redact_sensitive_text(primary_message)[:500]}"
                        ),
                    }],
                },
            )
    if output_format != "json":
        return ToolResult(
            "completed",
            [result.stdout.strip()] if result.stdout.strip() else [],
            metadata=metadata,
        )
    try:
        findings = json.loads(result.stdout or "[]")
        filtered, read_only_suppressions, provider_diagnostics = (
            _normalize_validated_payload(findings, working_directory, metadata)
        )
        return ToolResult(
            "partial" if provider_diagnostics else "completed",
            filtered,
            metadata=metadata,
            suppressed_findings=read_only_suppressions,
        )
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError) as exc:
        return ToolResult(
            "tool-error",
            message=f"Invalid ansible-lint JSON/schema: {exc}",
            metadata={
                **metadata,
                "provider_diagnostics": [{
                    "category": "PROVIDER_SCHEMA_ERROR",
                    "provider_root": str(working_directory),
                    "returncode": result.returncode,
                    "json_root_type": (
                        type(findings).__name__
                        if "findings" in locals() else "decode-failed"
                    ),
                    "exception_type": type(exc).__name__,
                    "exception_message": redact_sensitive_text(str(exc)),
                    "message": (
                        "ansible-lint adapter rejected provider output: "
                        f"{type(exc).__name__}: {redact_sensitive_text(str(exc))}"
                    ),
                }],
            },
        )

_ANSIBLE_LINT_CONFIG_NAMES = (
    ".ansible-lint",
    ".ansible-lint.yml",
    ".ansible-lint.yaml",
    ".config/ansible-lint.yml",
    ".config/ansible-lint.yaml",
)


def _find_ansible_lint_project_config(working_directory):
    """Find the nearest effective config without escaping a Git checkout."""
    start = Path(working_directory).resolve()
    for directory in (start, *start.parents):
        for name in _ANSIBLE_LINT_CONFIG_NAMES:
            candidate = directory / name
            if candidate.is_file():
                return candidate
        if (directory / ".git").exists():
            break
    return None


def _read_ansible_lint_project_config(working_directory):
    """Read skip_list and warn_list from the project's .ansible-lint config."""
    root = Path(working_directory)
    candidates = (
        (root,) if root.is_file()
        else tuple(root / name for name in _ANSIBLE_LINT_CONFIG_NAMES)
    )
    for candidate in candidates:
        if candidate.is_file():
            try:
                import yaml as _yaml
                loaded = _yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
                if isinstance(loaded, dict):
                    return {
                        "skip_list": list(loaded.get("skip_list") or []),
                        "warn_list": list(loaded.get("warn_list") or []),
                    }
            except Exception:
                pass
    return {}


def _filter_read_only_command_noise(findings, working_directory):
    """Suppress command-instead-of-module when the task only inspects state."""
    from ansibleguard.detectors.shell_instead_of_module import (
        _collect_all_tasks,
        _get_command_string,
        _is_read_only_query,
    )
    from ansibleguard.detectors.source_lines import load_with_lines, source_line

    root = Path(working_directory).resolve()
    task_cache = {}
    kept = []
    suppressed = []
    for issue in findings:
        rule_id = str(
            issue.get("check_name")
            or issue.get("rule_id")
            or issue.get("ruleId")
            or ""
        )
        if not rule_id.startswith("command-instead-of-module"):
            kept.append(issue)
            continue
        source = Path(lint_issue_path(issue))
        source = source if source.is_absolute() else root / source
        source = source.resolve()
        if source not in task_cache:
            document = load_with_lines(source)
            task_cache[source] = _collect_all_tasks(document) if document else []
        line = lint_issue_line(issue)
        read_only = any(
            source_line(task) == line
            and _is_read_only_query(_get_command_string(task))
            for task in task_cache[source]
        )
        if not read_only:
            kept.append(issue)
            continue
        suppressed.append(
            {
                "provider": "ansible-lint",
                "native_rule_id": rule_id,
                "file": lint_issue_path(issue),
                "line": line,
                "native_fingerprint": issue.get("fingerprint", ""),
                "reason": "read-only-command-has-no-state-module-migration",
            }
        )
    return kept, suppressed


_FQCN_RULES = frozenset({
    "fqcn[action-core]",
    "fqcn[action]",
    "fqcn[builtins]",
})


def _fqcn_applicable(working_directory):
    """Return False if the project targets Ansible < 2.9 (FQCN not available)."""
    import yaml as _yaml
    for meta_candidate in (
        Path(working_directory) / "meta" / "main.yml",
        Path(working_directory) / "meta" / "main.yaml",
    ):
        if not meta_candidate.is_file():
            continue
        try:
            data = _yaml.safe_load(meta_candidate.read_text(encoding="utf-8")) or {}
            min_ver = str(
                data.get("galaxy_info", {}).get("min_ansible_version", "2.9")
            ).strip()
            major_minor = min_ver.split(".")[:2]
            major = int(major_minor[0]) if major_minor else 2
            minor = int(major_minor[1]) if len(major_minor) > 1 else 9
            if (major, minor) < (2, 9):
                return False
        except Exception:
            pass
    return True


def _apply_project_suppressions(findings, working_directory):
    """Filter skip_list issues (D4) and mark warn_list issues uncertain (D5)."""
    config = _read_ansible_lint_project_config(working_directory)
    skip_list = set(config.get("skip_list", []))
    warn_list = set(config.get("warn_list", []))
    if not skip_list and not warn_list:
        return findings
    result = []
    for issue in findings:
        rule_id = (
            issue.get("check_name")
            or issue.get("rule_id")
            or issue.get("ruleId")
            or ""
        )
        # D4: skip_list suppresses the finding entirely
        in_skip = rule_id in skip_list or any(
            rule_id.startswith(s.rstrip("[")) for s in skip_list
        )
        if in_skip:
            continue
        # D5: warn_list marks as uncertain (developer acknowledged but not enforced)
        in_warn = rule_id in warn_list or any(
            rule_id.startswith(w.rstrip("[")) for w in warn_list
        )
        if in_warn:
            issue = dict(issue)
            issue["warn_list_suppressed"] = True
        result.append(issue)
    return result


def run_ansible_lint(target_path, output_format="json"):
    """
    Run ansible-lint on a given file or directory and return parsed results.

    Args:
        target_path (str): Path to a playbook file or Ansible role directory.
        output_format (str): 'json' or 'plain'

    Returns:
        list or str: Parsed lint results or raw output.
    """
    result = scan_with_ansible_lint(target_path, output_format)
    if result.status != "completed":
        print(f"Exception while running ansible-lint: {result.message}")
        return []
    return result.findings

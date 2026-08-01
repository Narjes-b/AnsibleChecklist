import subprocess
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import hashlib
from importlib.metadata import PackageNotFoundError, version

from .gitleaks import ToolResult


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
    location = issue.get("location") or {}
    return str(issue.get("path") or location.get("path") or "")


def lint_issue_line(issue):
    location = issue.get("location") or {}
    positions = location.get("positions") or {}
    begin_position = positions.get("begin") or {}
    lines = location.get("lines") or {}
    return int(
        issue.get("line")
        or location.get("line")
        or begin_position.get("line")
        or lines.get("begin")
        or 1
    )


def scan_with_ansible_lint(target_path, output_format="json"):
    """Run ansible-lint and distinguish a clean scan from a tool failure."""
    target_path = Path(target_path).resolve()
    working_directory = target_path if target_path.is_dir() else target_path.parent
    lint_target = "." if target_path.is_dir() else target_path.name
    executable = _ansible_lint_executable()
    config_path = next(
        (
            working_directory / name
            for name in (
                ".ansible-lint",
                ".ansible-lint.yml",
                ".ansible-lint.yaml",
                ".config/ansible-lint.yml",
                ".config/ansible-lint.yaml",
            )
            if (working_directory / name).is_file()
        ),
        None,
    )
    try:
        package_version = version("ansible-lint")
    except PackageNotFoundError:
        package_version = None
    metadata = {
        "provider": "ansible-lint",
        "version": package_version,
        "executable": executable,
        "cwd": str(working_directory),
        "target": lint_target,
        "format": output_format,
        "dependency_mode": "offline-no-auto-install",
        "config": str(config_path) if config_path else "defaults",
        "config_sha256": (
            hashlib.sha256(config_path.read_bytes()).hexdigest()
            if config_path
            else None
        ),
    }
    try:
        cmd = [executable, lint_target, "--offline"]
        if output_format == "json":
            cmd += ["-f", "json"]
        env = os.environ.copy()
        env.setdefault(
            "ANSIBLE_LOCAL_TEMP",
            str(Path(tempfile.gettempdir()) / "ansibleguard-ansible-tmp"),
        )
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=working_directory,
        )
    except (FileNotFoundError, OSError) as exc:
        return ToolResult("tool-error", message=str(exc), metadata=metadata)

    if result.returncode not in (0, 2):
        return ToolResult(
            "tool-error",
            message=(result.stderr or result.stdout or "Unknown ansible-lint failure").strip(),
            metadata=metadata,
        )
    if output_format != "json":
        return ToolResult(
            "completed",
            [result.stdout.strip()] if result.stdout.strip() else [],
            metadata=metadata,
        )
    try:
        return ToolResult(
            "completed", json.loads(result.stdout or "[]"), metadata=metadata
        )
    except json.JSONDecodeError as exc:
        return ToolResult(
            "tool-error",
            message=f"Invalid ansible-lint JSON: {exc}",
            metadata=metadata,
        )

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

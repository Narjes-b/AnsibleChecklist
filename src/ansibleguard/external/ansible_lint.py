import subprocess
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

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
    try:
        cmd = [_ansible_lint_executable(), str(target_path)]
        if output_format == "json":
            cmd += ["-f", "json"]
        env = os.environ.copy()
        env.setdefault(
            "ANSIBLE_LOCAL_TEMP",
            str(Path(tempfile.gettempdir()) / "ansibleguard-ansible-tmp"),
        )
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    except (FileNotFoundError, OSError) as exc:
        return ToolResult("tool-error", message=str(exc))

    if result.returncode not in (0, 2):
        return ToolResult(
            "tool-error",
            message=(result.stderr or result.stdout or "Unknown ansible-lint failure").strip(),
        )
    if output_format != "json":
        return ToolResult("completed", [result.stdout.strip()] if result.stdout.strip() else [])
    try:
        return ToolResult("completed", json.loads(result.stdout or "[]"))
    except json.JSONDecodeError as exc:
        return ToolResult("tool-error", message=f"Invalid ansible-lint JSON: {exc}")

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

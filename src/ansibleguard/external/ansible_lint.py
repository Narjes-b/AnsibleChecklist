import subprocess
import json
from pathlib import Path

from .gitleaks import ToolResult


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
        cmd = ["ansible-lint", str(target_path)]
        if output_format == "json":
            cmd += ["-f", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
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

##Snyk typically targets:

##Vulnerable dependencies (npm, pip, etc.)
##Insecure configurations in IaC (Terraform, Kubernetes)
##Vulnerabilities in containers (Docker images)

##With Ansible, the focus shifts to:

##Hardcoded secrets
##Insecure file permissions
##Unvalidated input in shell/command tasks
##Outdated packages
##Misuse of become/sudo
##Insecure or missing error handling

##So our target is more custom linting and static analysis, not dependency-based scanning.

## we adopt gotleaks that does the same job as Snyk but for Ansible playbooks detecting hardcoded credentials.


import json
import hashlib
import re
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    status: str
    findings: list = field(default_factory=list)
    message: str = ""
    metadata: dict = field(default_factory=dict)


def scan_with_gitleaks(target_path, gitleaks_path):
    target_path = Path(target_path)
    config_root = target_path if target_path.is_dir() else target_path.parent
    target_config = config_root / ".gitleaks.toml"
    metadata = {
        "provider": "gitleaks",
        "scan_mode": "dir",
        "executable": str(gitleaks_path),
        "config": str(target_config) if target_config.is_file() else "built-in-default",
        "config_sha256": (
            hashlib.sha256(target_config.read_bytes()).hexdigest()
            if target_config.is_file()
            else None
        ),
    }
    with tempfile.NamedTemporaryFile(
        mode="r", suffix=".json", delete=False
    ) as temp_json:
        report_path = Path(temp_json.name)

    try:
        try:
            command = [
                str(gitleaks_path),
                "dir",
                str(target_path),
                "--report-format",
                "json",
                "--report-path",
                str(report_path),
                "--redact=100",
                "--log-level",
                "error",
            ]
            if target_config.is_file():
                command.extend(["--config", str(target_config)])
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            message = (
                f"Gitleaks binary not found at '{gitleaks_path}'. "
                "Run `ansibleguard install-tools` or pass --gitleaks-path."
            )
            print(f"[✗] {message}")
            return ToolResult("tool-error", message=message, metadata=metadata)

        if result.returncode in [0, 1]:
            if report_path.exists() and report_path.stat().st_size > 0:
                with open(report_path, "r") as f:
                    findings = json.load(f)
                    for finding in findings:
                        finding["_scan_mode"] = "dir"
                    print(f"[✓] Gitleaks found {len(findings)} findings.")
                    return ToolResult("completed", findings, metadata=metadata)
            else:
                print("[✓] Gitleaks found no issues.")
                return ToolResult("completed", metadata=metadata)
        else:
            print("[✗] Gitleaks failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            message = (result.stderr or result.stdout or "Unknown gitleaks failure").strip()
            return ToolResult("tool-error", message=message, metadata=metadata)
    finally:
        if report_path.exists():
            report_path.unlink()


def scan_git_range_with_gitleaks(
    target_path, gitleaks_path, base_sha: str, head_sha: str
):
    """Scan commits introduced by a trusted, validated base/head SHA range."""
    target_path = Path(target_path)
    config_root = target_path if target_path.is_dir() else target_path.parent
    target_config = config_root / ".gitleaks.toml"
    metadata = {
        "provider": "gitleaks",
        "scan_mode": "git-range",
        "base_sha": base_sha,
        "head_sha": head_sha,
        "executable": str(gitleaks_path),
        "config": str(target_config) if target_config.is_file() else "built-in-default",
        "config_sha256": (
            hashlib.sha256(target_config.read_bytes()).hexdigest()
            if target_config.is_file()
            else None
        ),
    }
    sha_pattern = re.compile(r"^[0-9a-fA-F]{40,64}$")
    if not sha_pattern.fullmatch(base_sha or "") or not sha_pattern.fullmatch(
        head_sha or ""
    ):
        return ToolResult(
            "tool-error",
            message="GitLeaks history scan requires full hexadecimal base/head SHAs.",
            metadata=metadata,
        )

    with tempfile.NamedTemporaryFile(
        mode="r", suffix=".json", delete=False
    ) as temp_json:
        report_path = Path(temp_json.name)

    try:
        command = [
            str(gitleaks_path),
            "git",
            str(target_path),
            "--log-opts",
            f"{base_sha}..{head_sha}",
            "--report-format",
            "json",
            "--report-path",
            str(report_path),
            "--redact=100",
            "--log-level",
            "error",
        ]
        if target_config.is_file():
            command.extend(["--config", str(target_config)])
        try:
            result = subprocess.run(command, capture_output=True, text=True)
        except FileNotFoundError:
            return ToolResult(
                "tool-error",
                message=(
                    f"Gitleaks binary not found at '{gitleaks_path}'. "
                    "Run `ansibleguard install-tools` or pass --gitleaks-path."
                ),
                metadata=metadata,
            )

        if result.returncode in (0, 1):
            findings = []
            if report_path.exists() and report_path.stat().st_size:
                findings = json.loads(report_path.read_text(encoding="utf-8"))
                for finding in findings:
                    finding["_scan_mode"] = "git-range"
            return ToolResult("completed", findings=findings, metadata=metadata)
        return ToolResult(
            "tool-error",
            message=(result.stderr or result.stdout or "Unknown gitleaks failure").strip(),
            metadata=metadata,
        )
    finally:
        if report_path.exists():
            report_path.unlink()


def scan_with_gitleaks_file_output(playbook_path, gitleaks_path):
    """Backward-compatible list-returning wrapper for existing callers."""
    return scan_with_gitleaks(playbook_path, gitleaks_path).findings


# if __name__ == "__main__":

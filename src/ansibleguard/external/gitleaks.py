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


import subprocess
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ToolResult:
    status: str
    findings: list = field(default_factory=list)
    message: str = ""


def scan_with_gitleaks(target_path, gitleaks_path):
    target_path = Path(target_path)
    config_root = target_path if target_path.is_dir() else target_path.parent
    target_config = config_root / ".gitleaks.toml"
    with tempfile.NamedTemporaryFile(
        mode="r", suffix=".json", delete=False
    ) as temp_json:
        report_path = Path(temp_json.name)

    try:
        try:
            command = [
                str(gitleaks_path),
                "detect",
                "--source",
                str(target_path),
                "--no-git",
                "--report-format",
                "json",
                "--report-path",
                str(report_path),
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
            return ToolResult("tool-error", message=message)

        if result.returncode in [0, 1]:
            if report_path.exists() and report_path.stat().st_size > 0:
                with open(report_path, "r") as f:
                    findings = json.load(f)
                    print(f"[✓] Gitleaks found {len(findings)} findings.")
                    return ToolResult("completed", findings)
            else:
                print("[✓] Gitleaks found no issues.")
                return ToolResult("completed")
        else:
            print("[✗] Gitleaks failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            message = (result.stderr or result.stdout or "Unknown gitleaks failure").strip()
            return ToolResult("tool-error", message=message)
    finally:
        if report_path.exists():
            report_path.unlink()


def scan_with_gitleaks_file_output(playbook_path, gitleaks_path):
    """Backward-compatible list-returning wrapper for existing callers."""
    return scan_with_gitleaks(playbook_path, gitleaks_path).findings


# if __name__ == "__main__":

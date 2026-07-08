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


def scan_with_gitleaks_file_output(playbook_path, gitleaks_path):
    with tempfile.NamedTemporaryFile(
        mode="r", suffix=".json", delete=False
    ) as temp_json:
        report_path = Path(temp_json.name)

    try:
        try:
            result = subprocess.run(
                [
                    str(gitleaks_path),
                    "detect",
                    "--source",
                    playbook_path,
                    "--no-git",
                    "--report-format",
                    "json",
                    "--report-path",
                    str(report_path),
                    "--log-level",
                    "silent",
                ],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            print(
                f"[✗] Gitleaks binary not found at '{gitleaks_path}'. "
                f"Run the installer (ansibleguard.external.install_gitleaks) or check GITLEAKS_PATH in config.py."
            )
            return []

        if result.returncode in [0, 1]:
            if report_path.exists() and report_path.stat().st_size > 0:
                with open(report_path, "r") as f:
                    findings = json.load(f)
                    print(f"[✓] Gitleaks found {len(findings)} findings.")
                    return findings
            else:
                print("[✓] Gitleaks found no issues.")
                return []
        else:
            print("[✗] Gitleaks failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return []
    finally:
        if report_path.exists():
            report_path.unlink()


# if __name__ == "__main__":

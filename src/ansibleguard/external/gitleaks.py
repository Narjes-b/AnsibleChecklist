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
import os
from pathlib import Path
from dataclasses import dataclass, field
from functools import lru_cache

from ansibleguard.redaction import redact_diagnostic, redact_sensitive_text


@dataclass
class ToolResult:
    status: str
    findings: list = field(default_factory=list)
    message: str = ""
    metadata: dict = field(default_factory=dict)
    suppressed_findings: list = field(default_factory=list)

    def __post_init__(self):
        self.message = redact_sensitive_text(self.message)
        self.metadata = redact_diagnostic(self.metadata)


GITLEAKS_NOISE_FILES = {".secrets.baseline", ".gitleaksignore"}
PUBLIC_KEY_CONTEXTS = {"minisign_key", "public_key", "public-key", "stamp ="}
DOCUMENTATION_PLACEHOLDERS = {"your_token", "your_api_token", "your_api_key"}
# v0.0.4: GitLeaks rules that produce 0% precision on Ansible repos and are suppressed
# by default. kubernetes-secret-yaml fires on legitimate Kubernetes manifests stored
# alongside Ansible roles; it is not an Ansible quality signal.
_DISABLED_GITLEAKS_RULES = {"kubernetes-secret-yaml"}
CHECKSUM_VALUE_RE = re.compile(
    r"^\s*[\"'][^\"']+[\"']\s*:\s*[\"'][0-9a-f]{32,128}[\"']\s*,?\s*$",
    re.IGNORECASE,
)
# v0.0.4: generic-api-key false-positive filters.
# Pure hex strings of standard cryptographic lengths are checksums, git SHAs,
# GPG fingerprints, or certificate thumbprints — not API keys.
_HEX_ONLY_RE = re.compile(r"^[0-9a-f]+$", re.IGNORECASE)
_CRYPTO_HEX_LENGTHS = {32, 40, 56, 64, 96, 128}  # MD5, SHA-1, SHA-224/256/384/512
# Version 4 UUID pattern (git commit-ish, trace IDs, etc.)
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
_INTEGRITY_CONTEXT_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:checksum|sha(?:1|224|256|384|512)?|digest|fingerprint|content[_-]?hash)(?![A-Za-z0-9])",
    re.IGNORECASE,
)
_IDENTIFIER_CONTEXT_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:uuid|trace[_-]?id|request[_-]?id|correlation[_-]?id)(?![A-Za-z0-9])",
    re.IGNORECASE,
)
GITLEAKS_SUPPRESSION_POLICY_VERSION = 1


def _suppression_evidence(finding, reason):
    """Return redacted, reviewable evidence for one built-in suppression."""
    return {
        "provider": "gitleaks",
        "native_rule_id": str(
            finding.get("RuleID") or finding.get("ruleID") or "unknown"
        ),
        "file": str(finding.get("File") or finding.get("file") or ""),
        "line": int(
            finding.get("StartLine") or finding.get("startLine") or 1
        ),
        "scan_mode": str(finding.get("_scan_mode") or "dir"),
        "native_fingerprint": str(
            finding.get("Fingerprint") or finding.get("fingerprint") or ""
        ),
        "reason": reason,
        "policy_version": GITLEAKS_SUPPRESSION_POLICY_VERSION,
    }


def _read_source_lines(path):
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return []


def _source_context(scan_root, finding, *, lines=None):
    relative = str(finding.get("File") or finding.get("file") or "")
    line_number = int(finding.get("StartLine") or finding.get("startLine") or 1)
    path = Path(relative)
    if not path.is_absolute():
        path = Path(scan_root) / path
    if lines is None:
        lines = _read_source_lines(path)
    index = max(0, line_number - 1)
    line = lines[index] if index < len(lines) else ""
    nearby = "\n".join(lines[max(0, index - 20) : index + 1])
    return line, nearby


def _filter_known_noise(findings, scan_root):
    """Suppress deterministic non-secret artifacts while retaining evidence."""
    # Process one file at a time, retaining at most one decoded file per call.
    # A frozen large JSON file can yield tens of thousands of native findings;
    # rereading/decoding its entire contents per finding caused terabytes of
    # projected repeated reads. Restore native order in both output lists.
    @lru_cache(maxsize=1)
    def source_lines(relative):
        path = relative if relative.is_absolute() else Path(scan_root) / relative
        return _read_source_lines(path)

    kept = []
    suppressed = []
    indexed = sorted(enumerate(findings), key=lambda item: str(item[1].get("File") or item[1].get("file") or ""))
    for index, finding in indexed:
        relative = Path(str(finding.get("File") or finding.get("file") or ""))
        reason = None
        if relative.name.lower() in GITLEAKS_NOISE_FILES:
            reason = "known-secret-baseline-or-ignore-file"
        rule = str(finding.get("RuleID") or finding.get("ruleID") or "").lower()
        if reason is None and rule in _DISABLED_GITLEAKS_RULES:
            reason = "disabled-rule-not-ansible-signal"
        line, nearby = _source_context(scan_root, finding, lines=source_lines(relative))
        lowered = line.lower()
        if reason is None and any(
            placeholder in lowered for placeholder in DOCUMENTATION_PLACEHOLDERS
        ):
            reason = "documentation-placeholder"
        if reason is None and rule == "generic-api-key" and any(
            marker in lowered for marker in PUBLIC_KEY_CONTEXTS
        ):
            reason = "public-key-or-verification-material"
        if (
            reason is None
            and
            rule == "generic-api-key"
            and '"checksums"' in nearby.lower()
            and CHECKSUM_VALUE_RE.fullmatch(line)
        ):
            reason = "checksum-value"
        if (
            reason is None
            and
            rule == "generic-api-key"
            and line.lstrip().startswith("#")
            and any(
                marker in nearby.lower()
                for marker in (
                    "for example",
                    "example for",
                    "old plain text string",
                )
            )
        ):
            reason = "commented-documentation-example"
        if (
            reason is None
            and
            rule == "generic-api-key"
            and line.lstrip().startswith(";")
            and "default" in nearby.lower()
        ):
            # A leading semicolon is an inactive INI setting. Public default
            # examples (for example Grafana's template secret_key) are not
            # live credentials and should not become repository errors.
            reason = "inactive-default-ini-setting"
        if reason is None and rule == "generic-api-key":
            # v0.0.4: suppress pure hex strings of cryptographic digest lengths —
            # these are SHA-1/SHA-256 checksums, git SHAs, GPG fingerprints, or
            # certificate thumbprints, not API keys (42.6% precision root cause).
            secret_value = str(
                finding.get("Secret") or finding.get("secret") or ""
            ).strip()
            clean = secret_value.strip("'\"\t ")
            integrity_context = bool(_INTEGRITY_CONTEXT_RE.search(line))
            identifier_context = bool(_IDENTIFIER_CONTEXT_RE.search(line))
            if (
                _HEX_ONLY_RE.fullmatch(clean)
                and len(clean) in _CRYPTO_HEX_LENGTHS
                and integrity_context
            ):
                reason = "cryptographic-digest-not-api-key"
            elif _UUID_RE.fullmatch(clean) and identifier_context:
                reason = "uuid-not-api-key"
            elif integrity_context:
                reason = "integrity-identifier-not-api-key"
        # A PEM marker in a comment is documentation or an inactive example,
        # not embedded key material.  Restrict this suppression to GitLeaks'
        # private-key rule and comment syntax so actual PEM blocks remain.
        if (
            reason is None
            and rule in {"private-key", "private-key-pem"}
            and line.lstrip().startswith("#")
        ):
            reason = "commented-private-key-marker"
        if reason is not None:
            suppressed.append((index, _suppression_evidence(finding, reason)))
            continue
        kept.append((index, finding))
    return [finding for _, finding in sorted(kept)], [evidence for _, evidence in sorted(suppressed)]


def _normalize_findings(findings, scan_root, scan_mode):
    """Make GitLeaks evidence stable across equivalent checkout locations."""
    root = Path(scan_root).resolve()
    for finding in findings:
        raw_file = Path(str(finding.get("File") or finding.get("file") or ""))
        if raw_file.is_absolute():
            try:
                normalized_file = raw_file.resolve().relative_to(root).as_posix()
            except ValueError:
                normalized_file = raw_file.as_posix()
        else:
            normalized_file = raw_file.as_posix().removeprefix("./")

        if normalized_file:
            finding["File"] = normalized_file
        finding["_scan_mode"] = scan_mode

        fingerprint_key = (
            "Fingerprint" if "Fingerprint" in finding else "fingerprint"
        )
        if finding.get(fingerprint_key) and normalized_file:
            rule_id = finding.get("RuleID") or finding.get("ruleID") or "unknown"
            line = finding.get("StartLine") or finding.get("startLine") or 1
            finding[fingerprint_key] = f"{normalized_file}:{rule_id}:{line}"
    return findings


def scan_with_gitleaks(target_path, gitleaks_path, timeout=None):
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
    timeout = float(
        timeout
        if timeout is not None
        else os.environ.get("ANSIBLEGUARD_GITLEAKS_TIMEOUT", "600")
    )
    metadata["timeout_seconds"] = timeout
    max_output_bytes = int(os.environ.get("ANSIBLEGUARD_PROVIDER_MAX_OUTPUT_BYTES", str(64 * 1024 * 1024)))
    metadata["max_output_bytes"] = max_output_bytes
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
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                "timeout",
                message=f"Gitleaks exceeded {timeout:g} seconds",
                metadata={
                    **metadata,
                    "failure_category": "TIMEOUT",
                    "failure_nature": "TIMEOUT",
                },
            )
        except FileNotFoundError:
            message = (
                f"Gitleaks binary not found at '{gitleaks_path}'. "
                "Run `ansibleguard install-tools` or pass --gitleaks-path."
            )
            print(f"[error] {message}")
            return ToolResult("tool-error", message=message, metadata=metadata)

        if result.returncode in [0, 1]:
            if report_path.exists() and report_path.stat().st_size > 0:
                report_bytes = report_path.stat().st_size
                if report_bytes > max_output_bytes:
                    return ToolResult(
                        "tool-error",
                        message=f"Gitleaks report exceeded {max_output_bytes} bytes",
                        metadata={
                            **metadata,
                            "failure_category": "OUTPUT_LIMIT",
                            "failure_nature": "RESOURCE_LIMIT",
                            "output_bytes": report_bytes,
                        },
                    )
                with open(report_path, "r") as f:
                    findings = json.load(f)
                    _normalize_findings(findings, config_root, "dir")
                    findings, suppressed = _filter_known_noise(
                        findings, config_root
                    )
                    metadata["suppressed_known_noise"] = len(suppressed)
                    print(f"[ok] Gitleaks found {len(findings)} findings.")
                    return ToolResult(
                        "completed",
                        findings,
                        metadata=metadata,
                        suppressed_findings=suppressed,
                    )
            else:
                print("[ok] Gitleaks found no issues.")
                return ToolResult("completed", metadata=metadata)
        else:
            print("[error] Gitleaks failed; redacted diagnostics were retained.")
            message = (result.stderr or result.stdout or "Unknown gitleaks failure").strip()
            return ToolResult("tool-error", message=message, metadata=metadata)
    finally:
        if report_path.exists():
            report_path.unlink()


def scan_git_range_with_gitleaks(
    target_path, gitleaks_path, base_sha: str, head_sha: str, timeout=None
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
    timeout = float(
        timeout
        if timeout is not None
        else os.environ.get("ANSIBLEGUARD_GITLEAKS_TIMEOUT", "600")
    )
    metadata["timeout_seconds"] = timeout
    max_output_bytes = int(os.environ.get("ANSIBLEGUARD_PROVIDER_MAX_OUTPUT_BYTES", str(64 * 1024 * 1024)))
    metadata["max_output_bytes"] = max_output_bytes
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
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                "timeout",
                message=f"Gitleaks history scan exceeded {timeout:g} seconds",
                metadata={
                    **metadata,
                    "failure_category": "TIMEOUT",
                    "failure_nature": "TIMEOUT",
                },
            )
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
                report_bytes = report_path.stat().st_size
                if report_bytes > max_output_bytes:
                    return ToolResult(
                        "tool-error",
                        message=f"Gitleaks report exceeded {max_output_bytes} bytes",
                        metadata={
                            **metadata,
                            "failure_category": "OUTPUT_LIMIT",
                            "failure_nature": "RESOURCE_LIMIT",
                            "output_bytes": report_bytes,
                        },
                    )
                findings = json.loads(report_path.read_text(encoding="utf-8"))
                _normalize_findings(findings, config_root, "git-range")
                findings, suppressed = _filter_known_noise(findings, config_root)
                metadata["suppressed_known_noise"] = len(suppressed)
            else:
                suppressed = []
            return ToolResult(
                "completed",
                findings=findings,
                metadata=metadata,
                suppressed_findings=suppressed,
            )
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

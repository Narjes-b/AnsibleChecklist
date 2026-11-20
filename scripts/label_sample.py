#!/usr/bin/env python3
"""
Deterministic validation triage labeler.
Reads study/validation-v4/sample.csv, inspects each file, applies the
PILOT_PROTOCOL.md decision rules, and writes auto_label + auto_reason.

Rules applied:
  - Deterministic FP/TP rules (SOPS, PowerShell, read-only commands, etc.)
  - File-context heuristics for each concept
  - Falls back to 'uncertain' when context is insufficient
"""
from __future__ import annotations
import argparse
import csv, re, sys
from collections import defaultdict
from pathlib import Path

REPOS = Path("study/repositories")
SAMPLE = Path("study/validation-v6/sample.csv")

# ---------------------------------------------------------------------------
# Shared regex
# ---------------------------------------------------------------------------
SOPS_VALUE_RE = re.compile(r"^ENC\[AES256_GCM,")
VAULT_HDR_RE  = re.compile(r"\$ANSIBLE_VAULT;")
NO_LOG_BOOL_RE = re.compile(r"no_log\s*:\s*(true|yes|True|Yes)\b")
NO_LOG_STR_RE  = re.compile(r'no_log\s*:\s*"?\{\{')
NO_LOG_FALSE_RE = re.compile(r"no_log\s*:\s*(false|no|False|No)\b")
NOQA_CHANGED_RE = re.compile(r"#\s*noqa:?\s*no-changed-when", re.IGNORECASE)

SENSITIVE_PARAMS = re.compile(
    r"\b(password|passwd|secret|token|api_key|apikey|access_key|secret_key"
    r"|private_key|ibmcloud_api_key|client_secret|oauth_token|Authorization"
    r"|login_password|auth_token|aws_secret|admin_password|bearer)\b",
    re.IGNORECASE,
)

PLACEHOLDER_VALUES_RE = re.compile(
    r'^(PLACEHOLDER|CHANGEME|CHANGE.ME|changeme|change_me|to.be.changed'
    r'|your[-_].*|replace[-_]me|insert[-_]here|fill[-_]in'
    r'|not[-_]a[-_]secure[-_]key|some[-_]password|top[-_]?secret'
    r'|myClientPassword|myClientId|testpassword|password123'
    r'|example[-_].*|fake[-_].*|dummy[-_].*'
    r'|""|\'\')$',
    re.IGNORECASE,
)

READONLY_CMD_RE = re.compile(
    r"\b(repolist|is.active|is.enabled|is.failed|systemctl status"
    r"|dnf list|yum list|apt list|dpkg -l|rpm -qa|rpm -q\b"
    r"|kubectl get|kubectl describe|oc get|oc describe"
    r"|docker ps|docker inspect|docker images"
    r"|virsh list|virsh dominfo"
    r"|aws .*describe|aws .*list|aws .*get"
    r"|openstack .* list|openstack .* show"
    r"|show version|show running|show interface"
    r"|git status|git log|git diff"
    r"|cat |head |tail |ls |find |stat |df |du |free |ps |top |uptime"
    r")\b",
    re.IGNORECASE,
)

SHA256_NAME_RE = re.compile(r"\b(sha256|sha512|md5|checksum|fingerprint|hash|gpg_key_id)\b", re.IGNORECASE)
REAL_SECRET_CHARS_RE = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}$")

POWERSHELL_MARKERS_RE = re.compile(
    r"executable\s*:\s*powershell|\.ps1\b|\$env:|New-Item|Invoke-WebRequest"
    r"|cmdlet|\[Net\.|ProgressPreference|SilentlyContinue",
    re.IGNORECASE,
)
CSH_SET_RE = re.compile(r"\bset\s+(\w+)\s*=")
CSH_EXEC_RE = re.compile(r"executable\s*:\s*/bin/(c|tc)sh")

CREATES_POSITIONAL_RE = re.compile(r"\bcreates=\S+")
HANDLER_PATH_RE = re.compile(r"/handlers/")

GPG_FINGERPRINT_RE = re.compile(r"\b[0-9A-F]{40}\b")

SLACK_TOKEN_RE = re.compile(r"\bT[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{20,}")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH |PRIVATE KEY|ENCRYPTED PRIVATE)")
AWS_KEY_RE     = re.compile(r"\b(AKIA|ASIA|AROA|AIDA|ANPA|AIDJ)[A-Z0-9]{16}\b")

SOPS_FILE_RE   = re.compile(r"\.sops\.(ya?ml)$", re.IGNORECASE)


def read_context(project: str, path: str, line: str, window: int = 25) -> tuple[Path | None, str, list[tuple[int, str]]]:
    owner, _, repo = project.partition("/")
    fp = REPOS / owner / repo / path
    if not fp.is_file():
        return None, "", []
    try:
        text = fp.read_text(errors="replace")
        lines = text.splitlines()
        ln = max(0, int(line) - 1) if line and line.strip() else 0
        start = max(0, ln - 3)
        end = min(len(lines), ln + window)
        ctx = [(i + 1, lines[i]) for i in range(start, end)]
        return fp, text, ctx
    except Exception:
        return None, "", []


def ctx_text(ctx: list[tuple[int, str]]) -> str:
    return "\n".join(l for _, l in ctx)


# ---------------------------------------------------------------------------
# Per-concept labelers
# ---------------------------------------------------------------------------

def label_credential_log_exposure(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)

    # FP: no_log: true already set (explicit boolean)
    if NO_LOG_BOOL_RE.search(window):
        return "false-positive", "no_log: true explicitly set; task already protected"

    # Uncertain: no_log: "{{ variable }}" — configurable logging in reusable roles
    if NO_LOG_STR_RE.search(window):
        return "uncertain", "no_log set as a Jinja variable; protection depends on deployment configuration"

    # FP: assert module checking credential state, not exposing it
    if re.search(r"ansible\.builtin\.assert|assert:", window) and not SENSITIVE_PARAMS.search(
        "\n".join(l for _, l in ctx if ":" in l and not l.strip().startswith("-"))
    ):
        return "false-positive", "assert module: checking credential state, not passing credential value"

    # FP: set_fact on non-credential variable (no sensitive param in task body)
    task_body = "\n".join(l for _, l in ctx[3:])  # skip context before flagged line
    if re.search(r"set_fact:", window) and not SENSITIVE_PARAMS.search(task_body):
        return "false-positive", "set_fact on non-sensitive variable; no credential parameter in task body"

    # FP: debug module displaying status messages (not credentials)
    if re.search(r"ansible\.builtin\.debug|debug:", window):
        if not SENSITIVE_PARAMS.search(task_body):
            return "false-positive", "debug module displaying non-sensitive status message; no credential value in output"

    # TP: sensitive parameter present and no no_log protection
    if SENSITIVE_PARAMS.search(window):
        # Confirm there's no no_log anywhere in nearby context
        if not NO_LOG_BOOL_RE.search(full_text[:2000]) or not NO_LOG_BOOL_RE.search(window):
            return "true-positive", "task passes a sensitive parameter value without no_log: true"

    return "uncertain", "insufficient context to determine if sensitive value is exposed"


def label_hardcoded_secret(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)
    ln = int(row["line"]) - 1 if row["line"].strip() else 0
    _, flagged_line = ctx[3] if len(ctx) > 3 else (ln, "")

    # FP: SOPS-encrypted value
    if SOPS_FILE_RE.search(row["path"]) or "sops:" in full_text:
        return "false-positive", "SOPS-encrypted file; value is ENC[AES256_GCM,...] ciphertext, not plaintext"
    if SOPS_VALUE_RE.search(flagged_line):
        return "false-positive", "value matches SOPS ciphertext pattern ENC[AES256_GCM,...]; not a plaintext secret"

    # FP: SHA-256 / checksum / GPG fingerprint by variable name
    var_name = flagged_line.split(":")[0].strip() if ":" in flagged_line else ""
    if SHA256_NAME_RE.search(var_name):
        return "false-positive", f"variable name '{var_name}' indicates integrity checksum or fingerprint, not an authentication credential"

    # FP: variable explicitly named as checksum in comment
    if re.search(r"(checksum|sha256|fingerprint|hash|gpg)", window, re.IGNORECASE) and ":" in flagged_line:
        val = flagged_line.split(":", 1)[1].strip().strip('"\'')
        if re.match(r"^[0-9a-f]{40,64}$", val.lower()):
            return "false-positive", "hex value matches SHA-1/SHA-256 hash format; context confirms integrity checksum not a credential"

    # FP: infrastructure-playbooks / example files
    if re.search(r"infrastructure.playbooks|examples?/|molecule/|tests?/", row["path"], re.IGNORECASE):
        return "false-positive", f"example/test path '{row['path']}'; credentials are demonstration values, not production secrets"

    # TP: actual private key material
    if PRIVATE_KEY_RE.search(window):
        return "true-positive", "private key material (-----BEGIN ... PRIVATE KEY-----) in plaintext; genuine credential"

    # TP: Slack token format
    if SLACK_TOKEN_RE.search(flagged_line):
        return "true-positive", "Slack API token format (T.../B.../xxx) confirmed in plaintext"

    # TP: AWS access key
    if AWS_KEY_RE.search(flagged_line):
        return "true-positive", "AWS access key format (AKIA/ASIA prefix) detected in plaintext"

    # FP: obvious placeholder value
    val_match = re.search(r":\s*[\"']?(.{3,60}?)[\"']?\s*$", flagged_line)
    val = val_match.group(1).strip().strip('"\'') if val_match else ""
    if val and PLACEHOLDER_VALUES_RE.match(val):
        return "false-positive", f"value '{val[:40]}' is an obvious placeholder; not a real credential"

    # Classify by message type
    msg = row.get("message", "")
    if "Private Key" in msg:
        return "true-positive", "private key pattern detected; genuine cryptographic secret"
    if "Generic API Key" in msg:
        # 40-hex: could be OAuth or SHA-1; lean TP unless it looks like a hash
        if re.match(r"^[0-9a-f]{40}$", val.lower()):
            # Ambiguous: GitHub token = 40 hex, SHA-1 = 40 hex
            # If var name contains 'secret' or 'token' → TP; otherwise uncertain
            if re.search(r"(secret|token|password|key)", var_name, re.IGNORECASE):
                return "true-positive", f"40-hex value in variable named '{var_name}'; matches OAuth/API secret format"
            return "uncertain", "40-hex value could be SHA-1 hash or OAuth token; variable name does not confirm credential purpose"
        if len(val) >= 16 and REAL_SECRET_CHARS_RE.match(val):
            return "true-positive", f"high-entropy secret value ({len(val)} chars) in variable '{var_name}'"
        return "uncertain", f"Generic API Key pattern; value '{val[:30]}' context insufficient to confirm credential vs. identifier"

    return "uncertain", "hardcoded secret pattern; insufficient context for definitive label"


def label_plaintext_sensitive_variable(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)
    ln = int(row["line"]) - 1 if row["line"].strip() else 0
    _, flagged_line = ctx[3] if len(ctx) > 3 else (ln, "")

    # FP: SOPS-encrypted file
    if SOPS_FILE_RE.search(row["path"]) or ("sops:" in full_text and "ENC[AES256_GCM" in full_text):
        return "false-positive", "SOPS-encrypted file; values are AES-256 ciphertext despite sensitive variable names"
    if SOPS_VALUE_RE.search(flagged_line):
        return "false-positive", "value is SOPS ciphertext (ENC[AES256_GCM,...]); variable is protected, not plaintext"

    # FP: Ansible Vault encrypted
    if VAULT_HDR_RE.search(full_text[:200]):
        return "false-positive", "Ansible Vault encrypted file ($ANSIBLE_VAULT header); content is ciphertext"
    if re.search(r"!vault\s*\|", flagged_line):
        return "false-positive", "value uses !vault | Ansible Vault inline encryption"

    # Extract the value
    val_match = re.search(r":\s*[\"']?(.{1,120}?)[\"']?\s*$", flagged_line)
    val = val_match.group(1).strip().strip('"\'') if val_match else ""

    # FP: empty string
    if val in ("", "''", '""', "~", "null"):
        return "false-positive", "variable has empty/null value; no credential present; standard role defaults pattern"

    # FP: placeholder value
    if val and PLACEHOLDER_VALUES_RE.match(val):
        return "false-positive", f"value '{val[:50]}' is an explicit placeholder in role defaults; not a real credential"

    # FP: development environment
    if re.search(r"/(development|dev|test|staging|local|docker|vagrant|molecule)/", row["path"], re.IGNORECASE):
        if len(val) < 20 or not REAL_SECRET_CHARS_RE.match(val):
            return "false-positive", f"development/test environment path; value '{val[:30]}' appears to be a non-production placeholder"

    # FP: uses Jinja variable / lookup (not a literal string)
    if re.search(r"\{\{.*\}\}", flagged_line):
        return "false-positive", "value is a Jinja template expression, not a plaintext literal"

    # TP: high-entropy literal value (≥16 chars, not a template)
    if len(val) >= 12 and REAL_SECRET_CHARS_RE.match(val) and not re.search(r"[\{\}]", val):
        return "true-positive", f"sensitive variable '{flagged_line.split(':')[0].strip()}' assigned high-entropy literal value ({len(val)} chars); not a Vault/SOPS/Jinja value"

    # TP: long string that doesn't look like a placeholder
    if len(val) >= 8 and not PLACEHOLDER_VALUES_RE.match(val) and not re.search(r"[\{\}]", val):
        return "true-positive", f"sensitive variable assigned plaintext literal '{val[:40]}'; should use Vault or a lookup"

    return "uncertain", "sensitive variable name; cannot determine if value is a real credential without runtime context"


def label_missing_validate_certs(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)

    # TP: explicit validate_certs: false
    if re.search(r"validate_certs\s*:\s*(false|no|'false'|\"false\")", window, re.IGNORECASE):
        return "true-positive", "validate_certs: false explicitly set; TLS certificate validation disabled"

    # Uncertain: no validate_certs line (depends on module default)
    module_match = re.search(r"^\s+(\S+\.)?(\w+):", window, re.MULTILINE)
    module = module_match.group(2) if module_match else "unknown"
    return "uncertain", f"no validate_certs line; default depends on module '{module}' version; cannot confirm TP or FP statically"


def label_non_idempotent_command(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)

    # FP: noqa suppression
    if NOQA_CHANGED_RE.search(window):
        return "false-positive", "explicit # noqa no-changed-when suppression; developer acknowledged and accepted this exception"

    # FP: creates= positional syntax
    if CREATES_POSITIONAL_RE.search(window):
        return "false-positive", "creates= positional argument provides idempotency guard in legacy Ansible syntax"

    # FP: read-only command
    if READONLY_CMD_RE.search(window):
        return "false-positive", "command appears read-only (query/status/list); does not modify system state; always-changed reporting is acceptable"

    # Uncertain: handler context
    if HANDLER_PATH_RE.search(row["path"]):
        return "uncertain", "task is in a handlers file; handlers run only when notified — handler semantics change idempotency expectations"

    # Out of scope: raw bootstrap
    if re.search(r"raw\s*:", window) and re.search(r"(python|pip|apt-get install python|bootstrap)", window, re.IGNORECASE):
        return "out-of-scope", "raw: bootstrap task installing Python before Ansible modules available; no practical idempotency mechanism"

    # FP: changed_when: false already present
    if re.search(r"changed_when\s*:\s*(false|no|False|\"false\")", window):
        return "false-positive", "changed_when: false already present; task is marked as non-changing"

    # TP: mutating commands without any guard
    mutating_verbs = re.compile(
        r"\b(cp|mv|rm|mkdir|chmod|chown|install|deploy|start|stop|restart"
        r"|enable|disable|create|delete|drop|update|upgrade|configure|set|add|append"
        r"|push|pull|clone|checkout|apply|patch|build|compile|make|pip install"
        r"|apt.get install|yum install|dnf install|npm install|gem install"
        r"|systemctl (start|stop|restart|enable|disable)"
        r"|docker run|kubectl apply|helm install|helm upgrade"
        r"|aws .*(create|delete|update|put|post)"
        r")\b",
        re.IGNORECASE,
    )
    if mutating_verbs.search(window):
        return "true-positive", "mutating shell/command task without creates/removes/changed_when idempotency guard; will always report changed"

    return "true-positive", "shell/command task with no idempotency guard; may always report changed on re-run"


def label_invalid_task_attribute_type(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    msg = row.get("message", "")
    window = ctx_text(ctx)

    # no_log: "{{ var }}" — string template, not boolean
    if "no_log" in msg and "str" in msg:
        if NO_LOG_STR_RE.search(window):
            return "true-positive", "no_log: '{{ variable }}' is a string template, not a boolean; Ansible type handling is version-sensitive"
        return "true-positive", "no_log attribute given string value instead of boolean; type mismatch"

    # run_once: integer
    if "run_once" in msg and "int" in msg:
        return "true-positive", "run_once: N (integer) instead of run_once: true (boolean); integer coercion is fragile across Ansible versions"

    # vars: list instead of mapping
    if "vars" in msg and ("list" in msg or "seq" in msg):
        return "true-positive", "vars: given a list instead of a mapping; YAML structural type error"

    # environment: "{{ dict_var }}" — cannot verify type statically
    if "environment" in msg and "mapping" in msg:
        if re.search(r"environment\s*:\s*['\"]?\{\{", window):
            return "uncertain", "environment: '{{ variable }}'; if the variable is a dict this is valid; cannot determine type statically"
        return "true-positive", "environment: given non-mapping value; structural type error"

    # Generic: trust the message, which is deterministic
    return "true-positive", f"task attribute type mismatch: {msg[:100]}"


def label_unscoped_shell_variable(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)

    # FP: PowerShell script
    if POWERSHELL_MARKERS_RE.search(window):
        return "false-positive", "PowerShell script; $var/$env:VAR are PowerShell variable syntax, not unscoped bash variables"

    # FP: csh/tcsh with set var=value
    if CSH_EXEC_RE.search(window):
        # Extract variable names from the message
        var_match = re.search(r"Shell variable\(s\) ([\w, ]+) are not", row.get("message", ""))
        vars_flagged = [v.strip() for v in var_match.group(1).split(",")] if var_match else []
        if vars_flagged:
            for var in vars_flagged:
                if CSH_SET_RE.search(window) and re.search(rf"\b{re.escape(var)}\b", window):
                    return "false-positive", f"csh script; 'set {var}=...' defines ${var} before use; detector doesn't recognize csh assignment syntax"
        return "false-positive", "csh/tcsh script; shell-specific variable definition syntax not recognized by detector"

    # FP: variable defined within same script block by assignment
    var_match = re.search(r"Shell variable\(s\) ([\w, ]+) are not", row.get("message", ""))
    vars_flagged = [v.strip() for v in var_match.group(1).split(",")] if var_match else []
    if vars_flagged:
        for var in vars_flagged:
            # Check if var is assigned in the same window
            if re.search(rf"\b{re.escape(var)}\s*=", window):
                return "false-positive", f"variable ${var} is assigned within the same shell task body; not an unscoped variable"

    # Uncertain: variable used inside container execution
    if re.search(r"docker run|kubectl exec|sh -c|sh -lc", window):
        return "uncertain", "shell variable used inside container execution; variable scope extends to container environment, not just Ansible environment: mapping"

    # Uncertain: multi-line script where variable may be defined below context window
    if re.search(r"(sqlplus|psql|mysql|isql)", window, re.IGNORECASE):
        return "uncertain", "multi-line database script; variables may be defined in heredoc or script body beyond context window"

    return "true-positive", "shell variable not declared in task environment: mapping; would require environment injection for portability"


def label_unhandled_failure_suppression(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)

    # FP: explicit noqa suppression (developer acknowledged the exception)
    if re.search(r"#\s*noqa:?\s*ignore-errors", window, re.IGNORECASE):
        return "false-positive", "explicit # noqa ignore-errors suppression; developer acknowledged the exception"

    # FP: ignore_errors with explanatory comment
    if re.search(r"#.*ignore.*error|#.*intentional|#.*by design|#.*expected", window, re.IGNORECASE):
        return "false-positive", "ignore_errors with explanatory comment; intentional error suppression, not oversight"

    # failed_when: false IS the unhandled-suppression pattern — TP unless probe
    if re.search(r"failed_when\s*:\s*(false|no|False)\b", window):
        # Uncertain: has register — possible probe pattern (result checked downstream)
        if re.search(r"register\s*:\s*\w+", window):
            return "uncertain", "failed_when: false with register; possible probe pattern — result may be checked downstream"
        return "true-positive", "failed_when: false suppresses all task failures without recovery handling"

    # Uncertain: ignore_errors with register (probe pattern)
    if re.search(r"register\s*:\s*\w+", window) and re.search(r"ignore_errors\s*:\s*(yes|true|True)", window):
        return "uncertain", "ignore_errors with register; may be a probe pattern (result checked downstream) or genuine suppression"

    # TP: ignore_errors without register or comment
    if re.search(r"ignore_errors\s*:\s*(yes|true|True)", window):
        return "true-positive", "ignore_errors: true without register or explanatory comment; task failures silently suppressed"

    return "uncertain", "failure suppression context unclear"


def label_shell_module_migration(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)
    msg = row.get("message", "")

    # FP: explicit noqa suppression for this rule
    if re.search(r"#\s*noqa:?\s*command-instead-of-module", window, re.IGNORECASE):
        return "false-positive", "explicit # noqa command-instead-of-module suppression; developer acknowledged the exception"

    # FP: hostname read (not set)
    if re.search(r"hostname", msg, re.IGNORECASE):
        if re.search(r"register\s*:", window):
            return "false-positive", "hostname command used to read current hostname into a variable; reading hostname is not replaceable by the hostname module"
        return "true-positive", "hostname command used to set hostname; should use ansible.builtin.hostname module"

    # FP: timeout wrapper
    if re.search(r"\btimeout\b", msg, re.IGNORECASE):
        return "false-positive", "timeout command wraps another command for time-limiting; no direct Ansible module equivalent"

    return "true-positive", f"shell command with an Ansible module equivalent: {msg[:80]}"


def label_missing_tags(row: dict) -> tuple[str, str]:
    # Exploratory stratum — label all items, note it's a policy rule
    return "true-positive", "task has no tags; policy rule — whether this is a genuine issue depends on project tagging convention"


def label_ansible_lint_issue(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    msg = row.get("message", "")

    # load-failure: not a real finding
    if re.search(r"load.failure|Failed to load|No such file", msg, re.IGNORECASE):
        return "false-positive", "load-failure[yaml]: file parse error, not a quality finding; reviewer has nothing to assess"

    # yaml formatting rules — low stakes but technically valid
    if re.search(r"yaml\[indentation\]|yaml\[trailing|yaml\[new-line\]|yaml\[empty", msg, re.IGNORECASE):
        return "true-positive", "YAML formatting rule violation; technically valid finding; low stakes"

    # fqcn rules
    if re.search(r"fqcn\[", msg, re.IGNORECASE):
        return "true-positive", "non-fully-qualified collection name; valid for Ansible >= 2.9; modernisation recommendation"

    # name casing
    if re.search(r"name\[casing\]", msg, re.IGNORECASE):
        return "true-positive", "task name casing violation per ansible-lint convention"

    # no-changed-when — same as non-idempotent-command FPs
    if re.search(r"no.changed.when", msg, re.IGNORECASE):
        window = ctx_text(ctx)
        if READONLY_CMD_RE.search(window):
            return "false-positive", "no-changed-when on a read-only command; read-only commands do not modify state"
        return "true-positive", "no-changed-when: command task lacks changed_when; will always report changed"

    # risky-file-permissions
    if re.search(r"risky.file.permissions", msg, re.IGNORECASE):
        return "true-positive", "file operation without explicit mode: setting; could create world-readable files by default"

    # Default: TP for lint rules that fire on actual code issues
    return "true-positive", f"ansible-lint rule violation: {msg[:80]}"


def label_large_task(row: dict) -> tuple[str, str]:
    return "true-positive", "task body exceeds line threshold; maintainability issue — should be split or refactored"


def label_undocumented_complex_task(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)
    # FP: task is already commented
    if re.search(r"^\s*#", window, re.MULTILINE):
        return "uncertain", "task context includes comments; whether complexity is sufficiently documented requires judgment"
    return "true-positive", "complex task without explanatory comment; maintainability issue"


def label_complex_expression(row: dict) -> tuple[str, str]:
    return "true-positive", "Jinja expression exceeds complexity threshold; readability issue — should be split into intermediate set_fact steps"


def label_long_yaml_line(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    ln = int(row["line"]) - 1 if row["line"].strip() else 0
    lines_list = [l for _, l in ctx]
    flagged = lines_list[3] if len(lines_list) > 3 else ""

    # FP: URL (unavoidable length)
    if re.search(r"https?://\S{60,}", flagged):
        return "false-positive", "line length due to a long URL; unavoidable — cannot be shortened without breaking the URL"

    # FP: base64 / cert / key data
    if re.search(r"[A-Za-z0-9+/]{60,}={0,2}", flagged):
        return "false-positive", "line length due to base64-encoded data (cert, key, or binary); unavoidable"

    # FP: lone Jinja expression
    if re.search(r"^\s*\{\{.*\}\}\s*$", flagged):
        return "false-positive", "line consists of a single Jinja expression; line break would break the expression"

    return "true-positive", "line exceeds length threshold with no unavoidable reason; should be reformatted using YAML multi-line syntax"


def label_unguarded_variable(row: dict) -> tuple[str, str]:
    # Descriptive stratum — all findings are "true" in the sense that the variable IS unguarded
    return "true-positive", "variable has no visible default in the repository (descriptive finding); note: this stratum is excluded from precision headline — runtime-injected variables are indistinguishable from bugs statically"


def label_overriding_facts(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)

    # After detector fix: only unconditional reassignments should fire
    # FP: when: clause present (residual detector bug if fix not rescanned)
    when_count = window.count("when:")
    if when_count >= 2:
        return "false-positive", "multiple when: clauses present; reassignment is conditional (standard multi-OS pattern); detector fix may not be in effect for this snapshot"
    if when_count == 1:
        return "uncertain", "one when: clause in context; may or may not guard the conflicting assignment"

    return "true-positive", "set_fact variable reassigned unconditionally with different values; accidental override"


def label_variable_use_before_definition(row: dict) -> tuple[str, str]:
    return "true-positive", "variable referenced before any visible assignment in the play; potential runtime error if variable is not injected externally"


def label_duplicate_task_names(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)
    # FP: no task names in file (misclassified YAML)
    name_count = len(re.findall(r"^\s*-\s*name\s*:", full_text, re.MULTILINE))
    if name_count == 0:
        return "false-positive", "file contains no '- name:' keys; not an Ansible tasks file — misclassified by corpus filter"
    # Find duplicated name from message
    msg = row.get("message", "")
    count_match = re.search(r"count=(\d+)", msg)
    if count_match and int(count_match.group(1)) >= 1:
        return "true-positive", f"file contains duplicate task names (count={count_match.group(1)}); ambiguous Ansible changed tracking"
    return "true-positive", "multiple tasks share the same name in this file; maintainability issue"


def label_unnamed_task(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    ln = int(row["line"]) - 1 if row["line"].strip() else 0
    lines_list = [l for _, l in ctx]
    flagged = lines_list[3] if len(lines_list) > 3 else ""

    # Uncertain: bare meta directive
    if re.search(r"meta\s*:", flagged):
        return "uncertain", "bare meta: directive (e.g. meta: end_play); meta directives conventionally have no names in Ansible"

    # Uncertain: bare include/import without clear task body
    if re.search(r"^\s*-\s*(include|import):", flagged):
        return "uncertain", "bare include/import directive; debatable whether these require names"

    return "true-positive", "task block has no name: key; all production tasks should have descriptive names for readability"


def label_incomplete_task(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    ln = int(row["line"]) - 1 if row["line"].strip() else 0
    lines_list = [l for _, l in ctx]
    flagged = lines_list[3] if len(lines_list) > 3 else ""

    # FP: marker in a YAML comment line (not active configuration)
    if re.search(r"^\s*#.*\b(TODO|FIXME|HACK|XXX)\b", flagged):
        return "false-positive", "TODO/FIXME marker appears in a YAML comment line; inactive YAML — not active configuration debt"

    # Uncertain: marker in vendored Galaxy role
    if re.search(r"/(galaxy|roles/[^/]+\.[^/]+)/", row["path"]):
        return "uncertain", "TODO/FIXME marker in a vendored Galaxy role; technical debt belongs to upstream project, not the consuming repo"

    return "true-positive", "active TODO/FIXME/HACK/XXX marker in production Ansible file; unresolved technical debt"


def label_unnecessary_set_fact(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)

    # FP: variable actually referenced in same file
    var_match = re.search(r"set_fact\s*:\s*\n?\s*(\w+)\s*:", window)
    if not var_match:
        var_match = re.search(r"set_fact\s*:\s*{[^}]*?(\w+)\s*:", window)
    if var_match:
        var_name = var_match.group(1)
        # Count references after the set_fact
        rest = full_text[full_text.find(window.split("\n")[3]) + len(window.split("\n")[3]):]
        if rest.count(var_name) > 0:
            return "false-positive", f"variable '{var_name}' is referenced later in the same file; set_fact is used"

    # Uncertain: file has include/import calls — variable may be consumed downstream
    if re.search(r"include_tasks|import_tasks|include_role|import_role", full_text):
        return "uncertain", "file contains include/import calls; set_fact variable may be consumed in an included file — cannot confirm TP without cross-file analysis"

    return "true-positive", "set_fact variable has no visible reference in this file and no includes to downstream consumers"


def label_redirected_module(row: dict) -> tuple[str, str]:
    return "true-positive", "deprecated module name redirected to collection equivalent; use FQCN for clarity and forward compatibility"


def label_unpinned_ansible_dependency(row: dict) -> tuple[str, str]:
    return "true-positive", "Ansible collection or role dependency without pinned version; unpinned dependencies may break on upstream changes"


def label_missing_abstraction(row: dict) -> tuple[str, str]:
    return "true-positive", "repeated code block that should be extracted into a reusable role or task file"


def label_large_playbook(row: dict) -> tuple[str, str]:
    return "true-positive", "playbook exceeds size threshold; should be split into smaller, focused playbooks or roles"


def label_high_coupling(row: dict) -> tuple[str, str]:
    return "true-positive", "role or task has high coupling to specific external dependencies or facts; reduces reusability"


def label_module_deprecation(row: dict) -> tuple[str, str]:
    return "true-positive", "deprecated module in use; should be migrated to its replacement before the module is removed"


def label_duplicated_code(row: dict) -> tuple[str, str]:
    return "true-positive", "duplicate code block detected across files; extract into shared role or task include"


def label_large_play(row: dict) -> tuple[str, str]:
    return "true-positive", "play has excessive number of tasks; should be split into focused roles"


def label_unnecessary_abstraction(row: dict) -> tuple[str, str]:
    return "true-positive", "abstraction adds complexity without reuse value; inline the logic directly"


def label_unused_registered_variable(row: dict) -> tuple[str, str]:
    return "true-positive", "register: result variable is never referenced; remove the register to avoid confusion"


def label_unstructured_module(row: dict) -> tuple[str, str]:
    return "true-positive", "module tasks not organized into a role structure; should be moved into a proper role layout"


def label_insufficient_modularization(row: dict) -> tuple[str, str]:
    return "true-positive", "playbook or role has insufficient modularization; logic should be extracted into reusable components"


def label_incohesive_play(row: dict) -> tuple[str, str]:
    return "true-positive", "play handles tasks from unrelated concerns; should be split into separate plays by responsibility"


def label_incohesive_playbook(row: dict) -> tuple[str, str]:
    return "true-positive", "playbook mixes concerns from multiple domains; should be split into focused playbooks"


def label_long_task_name(row: dict) -> tuple[str, str]:
    return "true-positive", "task name exceeds recommended length; overly verbose names reduce readability"


def label_unnamed_play(row: dict) -> tuple[str, str]:
    return "true-positive", "play has no name: key; all plays should have descriptive names"


def label_role_variable_precedence_collision(row: dict) -> tuple[str, str]:
    return "true-positive", "role variable redefined at a lower-precedence level; may cause unexpected overrides depending on invocation context"


def label_broken_role_dependency(row: dict) -> tuple[str, str]:
    return "true-positive", "role dependency references a role or version that does not exist or cannot be resolved"


def label_duplicate_mapping_key(row: dict) -> tuple[str, str]:
    return "true-positive", "YAML mapping contains duplicate keys; second definition silently overwrites the first; structural YAML error"


def label_insecure_permissions(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)
    msg = row.get("message", "")

    # Search task body (from flagged line) first to avoid picking up mode from a preceding task
    task_body = "\n".join(l for _, l in ctx[3:])
    mode_match = re.search(r"mode\s*:\s*['\"]?([0-9]{3,5})['\"]?", task_body) \
                 or re.search(r"mode\s*:\s*['\"]?([0-9]{3,5})['\"]?", window)
    if not mode_match:
        # No numeric mode visible in window — trust the message
        if re.search(r"World-writable|setuid|setgid|readable", msg, re.IGNORECASE):
            return "true-positive", f"insecure permissions: {msg[:80]}"
        return "uncertain", "mode value not visible in context window; cannot verify permission bits"

    mode_str = mode_match.group(1)
    try:
        mode_oct = int(mode_str, 8)
    except ValueError:
        return "uncertain", f"could not parse mode value '{mode_str}' as octal"

    # Setgid bit (02000) or setuid bit (04000)
    if mode_oct & 0o6000:
        bit = "setuid" if mode_oct & 0o4000 else "setgid"
        return "true-positive", f"mode: {mode_str} sets {bit} bit; grants unexpected privilege escalation"

    # World-writable (others write = 0o002)
    if mode_oct & 0o002:
        return "true-positive", f"mode: {mode_str} grants world-write access; any user can modify this file"

    # World-readable (others read = 0o004)
    if mode_oct & 0o004:
        return "true-positive", f"mode: {mode_str} makes file world-readable; sensitive resource should use 0600 or 0640"

    return "uncertain", f"mode: {mode_str}; message indicates insecure but permission bits unclear: {msg[:60]}"


def label_default_credentials(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], row["line"])
    if fp is None:
        return "uncertain", "file not found"
    window = ctx_text(ctx)
    # FP: placeholder
    if re.search(r"(admin|root|password|default|changeme|test)\s*$", window, re.IGNORECASE):
        val_match = re.search(r"password\s*:\s*['\"]?(\S+)['\"]?", window, re.IGNORECASE)
        if val_match:
            val = val_match.group(1).strip("'\"")
            if PLACEHOLDER_VALUES_RE.match(val):
                return "false-positive", "default credential placeholder value; not a real deployed credential"
    return "true-positive", "default or well-known credential in use; should be replaced with a unique secure credential"


def label_missing_test_update(row: dict) -> tuple[str, str]:
    return "uncertain", "process rule — determines if tests were updated alongside code changes; requires git history context beyond file content"


def label_unexpected_task_location(row: dict) -> tuple[str, str]:
    return "true-positive", "task placed in an unexpected location within the role structure (e.g. tasks in defaults/); violates Ansible role conventions"


def label_unused_handler(row: dict) -> tuple[str, str]:
    return "true-positive", "handler defined but never notified by any task; dead code that adds confusion"


def label_missing_handler(row: dict) -> tuple[str, str]:
    return "uncertain", "task suggests a handler notification but no matching handler is defined; may be in another included file"


def label_complex_playbook(row: dict) -> tuple[str, str]:
    return "true-positive", "playbook has high structural complexity; consider simplification or decomposition into smaller playbooks"


def label_clean_file_review(row: dict) -> tuple[str, str]:
    fp, full_text, ctx = read_context(row["project"], row["path"], "1", window=50)
    if fp is None:
        return "uncertain", "file not found"
    # Quick scan for obvious issues the tool should have caught
    if PRIVATE_KEY_RE.search(full_text):
        return "false-positive", "file contains private key material; tool missed this hardcoded-secret finding"
    if re.search(r"password\s*:\s*['\"]?[A-Za-z0-9]{8,}['\"]?", full_text) and not SOPS_VALUE_RE.search(full_text):
        if not PLACEHOLDER_VALUES_RE.search(full_text):
            return "uncertain", "file contains possible plaintext password assignment; may be a missed finding"
    return "true-positive", "file correctly produced no findings; content is configuration/metadata without detectable quality issues"


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------
LABELERS = {
    "credential-log-exposure":          label_credential_log_exposure,
    "hardcoded-secret":                 label_hardcoded_secret,
    "plaintext-sensitive-variable":     label_plaintext_sensitive_variable,
    "missing-validate-certs":           label_missing_validate_certs,
    "non-idempotent-command":           label_non_idempotent_command,
    "invalid-task-attribute-type":      label_invalid_task_attribute_type,
    "unscoped-shell-variable":          label_unscoped_shell_variable,
    "unhandled-failure-suppression":    label_unhandled_failure_suppression,
    "shell-module-migration":           label_shell_module_migration,
    "missing-tags":                     label_missing_tags,
    "ansible-lint-issue":               label_ansible_lint_issue,
    "large-task":                       label_large_task,
    "undocumented-complex-task":        label_undocumented_complex_task,
    "complex-expression":               label_complex_expression,
    "long-yaml-line":                   label_long_yaml_line,
    "unguarded-variable":               label_unguarded_variable,
    "overriding-facts":                 label_overriding_facts,
    "variable-use-before-definition":   label_variable_use_before_definition,
    "duplicate-task-names":             label_duplicate_task_names,
    "unnamed-task":                     label_unnamed_task,
    "incomplete-task":                  label_incomplete_task,
    "unnecessary-set-fact":             label_unnecessary_set_fact,
    "redirected-module":                label_redirected_module,
    "unpinned-ansible-dependency":      label_unpinned_ansible_dependency,
    "missing-abstraction":              label_missing_abstraction,
    "large-playbook":                   label_large_playbook,
    "high-coupling":                    label_high_coupling,
    "module-deprecation":               label_module_deprecation,
    "duplicated-code":                  label_duplicated_code,
    "large-play":                       label_large_play,
    "unnecessary-abstraction":          label_unnecessary_abstraction,
    "unused-registered-variable":       label_unused_registered_variable,
    "unstructured-module":              label_unstructured_module,
    "insufficient-modularization":      label_insufficient_modularization,
    "incohesive-play":                  label_incohesive_play,
    "incohesive-playbook":              label_incohesive_playbook,
    "long-task-name":                   label_long_task_name,
    "unnamed-play":                     label_unnamed_play,
    "role-variable-precedence-collision": label_role_variable_precedence_collision,
    "broken-role-dependency":           label_broken_role_dependency,
    "duplicate-mapping-key":            label_duplicate_mapping_key,
    "insecure-permissions":             label_insecure_permissions,
    "default-credentials":              label_default_credentials,
    "missing-test-update":              label_missing_test_update,
    "unexpected-task-location":         label_unexpected_task_location,
    "unused-handler":                   label_unused_handler,
    "missing-handler":                  label_missing_handler,
    "complex-playbook":                 label_complex_playbook,
}


def label_row(row: dict) -> tuple[str, str]:
    if row["validation_unit"] == "clean-file-review":
        return label_clean_file_review(row)
    concept = row.get("concept_id", "")
    labeler = LABELERS.get(concept)
    if labeler:
        return labeler(row)
    return "uncertain", f"no labeler defined for concept '{concept}'"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Apply the deterministic FP/TP validation rules to a sample CSV."
    )
    parser.add_argument(
        "--input", "-i", type=Path, default=SAMPLE,
        help=f"sample CSV to label (default: {SAMPLE})",
    )
    parser.add_argument(
        "--output", "-o", type=Path,
        help="output CSV; defaults to overwriting --input for legacy compatibility",
    )
    args = parser.parse_args(argv)
    input_path = args.input
    output_path = args.output or input_path
    rows = list(csv.DictReader(input_path.open(newline="", encoding="utf-8")))
    total = len(rows)
    labeled = 0
    from collections import Counter
    label_counts = Counter()

    for i, row in enumerate(rows):
        label, reason = label_row(row)
        row["auto_label"] = label
        row["auto_reason"] = reason
        label_counts[label] += 1
        labeled += 1
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{total} labeled...", flush=True)

    # Write back
    fieldnames = list(rows[0].keys())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nLabeled {labeled}/{total} items -> {output_path}.")
    print("\nLabel distribution:")
    for lbl, n in label_counts.most_common():
        print(f"  {n:4d}  {lbl}")

    # Per-concept precision
    from collections import defaultdict
    by_concept = defaultdict(Counter)
    for row in rows:
        if row["validation_unit"] == "occurrence":
            by_concept[row["concept_id"]][row["auto_label"]] += 1

    print(f"\n{'Concept':<45} {'TP':>4} {'FP':>4} {'Unc':>4} {'OS':>4}  Prec")
    print("-" * 75)
    total_tp = total_fp = 0
    for concept in sorted(by_concept, key=lambda c: -sum(by_concept[c].values())):
        c = by_concept[concept]
        tp, fp, unc = c["true-positive"], c["false-positive"], c["uncertain"]
        os_ = c["out-of-scope"]
        total_tp += tp; total_fp += fp
        denom = tp + fp
        prec = f"{tp/denom:.0%}" if denom else "n/a"
        print(f"  {concept:<43} {tp:>4} {fp:>4} {unc:>4} {os_:>4}  {prec}")
    print("-" * 75)
    t = total_tp + total_fp
    print(f"  {'TOTAL (occurrences, excl uncertain/oos)':<43} {total_tp:>4} {total_fp:>4}            {total_tp/t:.0%}")


if __name__ == "__main__":
    main()

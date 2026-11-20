"""Check optional single-task suggestions in a disposable, offline directory."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap

import yaml


class _TaskDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def _task(text):
    value = yaml.safe_load(textwrap.dedent(text))
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
    if not isinstance(value, dict) or any(key in value for key in ("hosts", "tasks", "block", "rescue", "always")):
        raise ValueError("suggestion must replace one leaf task")
    return value


def validate_suggestion(packet, snippet, lines, *, timeout=15):
    """Return mechanical evidence, never a behavioral-preservation guarantee."""
    result = {"status": "withheld", "checks": [], "limitations": [
        "Static checks do not establish behavioral equivalence or deployment suitability."]}
    try:
        unit = packet.get("unit")
        if not unit or not packet.get("complete"):
            raise ValueError("complete task evidence required")
        if not snippet or len(snippet.encode()) > 20000:
            raise ValueError("one bounded YAML replacement is required")
        # compose/audit rejects duplicate keys and aliases before construction.
        from .llm_evidence import _audit
        _audit(yaml.compose(snippet))
        before = _task("\n".join(lines[unit["start"] - 1:unit["end"]]))
        after = _task(snippet)
        rule = packet["rule"]
        if rule == "missing-validate-certs":
            changed = []
            for key, value in before.items():
                if isinstance(value, dict) and value.get("validate_certs") is False:
                    expected = {**before, key: {**value, "validate_certs": True}}
                    if after == expected:
                        changed.append(key)
            if len(changed) != 1:
                raise ValueError("only validate_certs: false -> true is permitted")
            from ..detectors.missing_validate_certs import detect_missing_validate_certs
            detector = detect_missing_validate_certs
        elif rule in {"credential-log-exposure", "credentials-leaking-in-log"}:
            if after != {**before, "no_log": True} or after == before:
                raise ValueError("only task-local no_log: true is permitted")
            from ..detectors.credentials_leaking_in_log import detect_credentials_leaking_in_log
            detector = detect_credentials_leaking_in_log
        else:
            raise ValueError("this rule requires human deployment intent; code suggestion withheld")
        result["checks"].extend(["yaml-parses", "single-task-edit-boundary"])
        executable = shutil.which("ansible-lint")
        if not executable:
            sibling = Path(sys.executable).parent / "ansible-lint"
            executable = str(sibling) if sibling.is_file() else None
        if not executable:
            raise ValueError("ansible-lint unavailable")
        with tempfile.TemporaryDirectory(prefix="ansibleguard-suggestion-") as directory:
            root = Path(directory)
            target = root / "tasks.yml"
            target.write_text(yaml.dump([after], Dumper=_TaskDumper, sort_keys=False), encoding="utf-8")
            if detector(target)[0]:
                raise ValueError("targeted detector still reports the condition")
            result["checks"].append("targeted-detector-clear")
            (root / "lint.yml").write_text("offline: true\n", encoding="utf-8")
            env = {**os.environ, "ANSIBLE_HOME": str(root / "ansible"),
                   "ANSIBLE_LOCAL_TEMP": str(root / "ansible/tmp"), "ANSIBLE_CONFIG": str(root / "ansible.cfg")}
            # No repository config, plugins, playbook execution, or source edits.
            (root / "ansible.cfg").write_text("[defaults]\n", encoding="utf-8")
            run = subprocess.run([executable, "--offline", "--nocolor", "-f", "json",
                "-c", str(root / "lint.yml"), str(target)], cwd=root, env=env,
                capture_output=True, text=True, timeout=timeout)
            if run.returncode != 0:
                raise ValueError("offline lint did not pass on the replacement task")
            result["checks"].append("offline-lint-clear")
        result["status"] = "passed"
    except (ValueError, TypeError, OSError, yaml.YAMLError, RecursionError, subprocess.TimeoutExpired) as exc:
        result["reason"] = str(exc)
    return result

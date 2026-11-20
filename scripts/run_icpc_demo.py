#!/usr/bin/env python3
"""Build and scan a disposable two-commit demo; never downloads dependencies."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

SOURCE = """- name: Demonstrate Ansible review
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Fetch example artifact
      ansible.builtin.get_url:
        url: https://example.invalid/artifact
        dest: /tmp/ansibleguard-demo-artifact
        mode: '0644'
        validate_certs: true
"""
ADDITION = """    - name: Display runtime input
      ansible.builtin.debug:
        msg: "{{ inventory_service_port }}"
"""


def run(output, explain=False):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    repo = output / "repository"
    repo.mkdir()
    env = {**os.environ, "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
           "GIT_AUTHOR_DATE": "2026-11-10T10:00:00+00:00", "GIT_COMMITTER_DATE": "2026-11-10T10:00:00+00:00"}
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), "-c", "user.name=AnsibleGuard Demo",
            "-c", "user.email=demo@example.invalid", *args], env=env, text=True, capture_output=True, check=True).stdout.strip()
    git("init", "-q")
    (repo / "playbook.yml").write_text(SOURCE)
    git("add", "playbook.yml")
    git("commit", "-qm", "Add verified artifact download")
    base = git("rev-parse", "HEAD")
    (repo / "playbook.yml").write_text(SOURCE.replace("validate_certs: true", "validate_certs: false") + ADDITION)
    git("add", "playbook.yml")
    git("commit", "-qm", "Change TLS setting and consume runtime input")
    head = git("rev-parse", "HEAD")
    commands = [
        [sys.executable, "-m", "ansibleguard.cli", str(repo), "--profile", "pr", "--fail-on", "never", "-o", str(output / "scan")],
        [sys.executable, "-m", "ansibleguard.cli", "diff", str(repo), "--base", base, "--head", head,
         "--profile", "pr", "--policy", "ratchet", "-o", str(output / "comparison")],
    ]
    if explain:
        commands[1] += ["--explain", "--explain-max-items", "3", "--explain-timeout", "120",
                         "--explain-budget", "360", "--explain-checkpoint-dir", str(output / "llm-attempts")]
    results = []
    for number, command in enumerate(commands):
        completed = subprocess.run(command, env=env, capture_output=True, text=True, timeout=600)
        (output / f"command-{number}.log").write_text(completed.stdout + completed.stderr)
        results.append({"command": command, "exit_code": completed.returncode})
        if completed.returncode not in (0, 1):
            raise RuntimeError(f"demo command failed; inspect {output / f'command-{number}.log'}")
    if explain:
        from ansibleguard.report.llm_explain import explain_occurrence
        result = explain_occurrence({"file": "playbook.yml", "line": 12, "rule_id": "unguarded-variable",
            "semantic_subject": "variable:inventory_service_port",
            "message": "Variable 'inventory_service_port' has no visible input contract."}, repo)
        (output / "runtime-input-assessment.json").write_text(json.dumps(result, indent=2) + "\n")
    metadata = {"purpose": "illustrative controlled demonstration; not evaluation evidence", "base_sha": base,
                "head_sha": head, "commands": results, "llm_requested": explain,
                "source_clean": not git("status", "--porcelain")}
    (output / "demo.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--explain", action="store_true", help="Use an already-installed local model; never downloads it")
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.explain), indent=2))


if __name__ == "__main__":
    main()

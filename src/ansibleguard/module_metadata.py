"""Repository-scoped, batched Ansible module metadata discovery."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def ansible_doc_executable():
    if os.environ.get("ANSIBLEGUARD_DISABLE_ANSIBLE_DOC", "").lower() in {
        "1", "true", "yes",
    }:
        return None
    sibling = Path(sys.executable).with_name("ansible-doc")
    return str(sibling) if sibling.is_file() else shutil.which("ansible-doc")


def build_module_metadata_index(actions, *, chunk_size=128, timeout=120):
    """Resolve every unique module action with a bounded number of processes.

    ``ansible-doc -j`` accepts multiple plugin names.  Short builtin names are
    queried alongside their FQCN aliases and normalized back to both spellings.
    A failed chunk contributes no metadata; detectors retain curated fallbacks.
    """
    executable = ansible_doc_executable()
    if not executable:
        return {}, {"status": "not-available", "subprocesses": 0}
    requested = sorted({str(action) for action in actions if action})
    # Query each observed action exactly once. ansible-doc normally returns a
    # canonical FQCN key for a short input; the alias pass below maps that
    # result back to the observed task spelling.
    candidates = requested
    metadata = {}
    diagnostics = []
    subprocesses = 0
    env = os.environ.copy()
    with tempfile.TemporaryDirectory(
        prefix="ansibleguard-ansible-doc-"
    ) as local_temp:
        # Never share mutable Ansible scratch state between concurrent
        # repository workers, even if the parent environment configured one.
        env["ANSIBLE_LOCAL_TEMP"] = local_temp
        for offset in range(0, len(candidates), max(1, int(chunk_size))):
            chunk = candidates[offset: offset + max(1, int(chunk_size))]
            subprocesses += 1
            try:
                result = subprocess.run(
                    [executable, "-j", *chunk], capture_output=True, text=True,
                    env=env, timeout=timeout,
                )
                payload = json.loads(result.stdout or "{}")
                if isinstance(payload, dict):
                    metadata.update(
                        (str(name), value)
                        for name, value in payload.items()
                        if isinstance(value, dict)
                    )
                if result.returncode != 0:
                    diagnostics.append({
                        "returncode": result.returncode,
                        "modules": len(chunk),
                        "message": (result.stderr or "ansible-doc failed").strip()[:500],
                    })
            except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                diagnostics.append({
                    "modules": len(chunk),
                    "message": f"{type(exc).__name__}: {exc}",
                })
    for action in requested:
        if action in metadata:
            continue
        if "." not in action:
            matches = [
                value for name, value in metadata.items()
                if name.rsplit(".", 1)[-1] == action
            ]
            if len(matches) == 1:
                metadata[action] = matches[0]
    return metadata, {
        "status": "partial" if diagnostics else "completed",
        "requested_modules": len(requested),
        "resolved_modules": sum(action in metadata for action in requested),
        "subprocesses": subprocesses,
        "diagnostics": diagnostics,
    }

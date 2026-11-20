"""Local explanation identity, bounded source hashing and private checkpoints."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
import tempfile
import urllib.request


def source_identity(root, excluded=None):
    """Hash regular source bytes; refuse ambiguous/oversized trees for resume."""
    if root is None:
        return None
    root = Path(root).resolve()
    excluded = Path(excluded).resolve() if excluded else None
    total, entries = 0, []
    try:
        for parent, directories, files in os.walk(root):
            if any((Path(parent) / name).is_symlink() for name in directories if name != ".git"):
                return None
            directories[:] = sorted(name for name in directories if name not in {
                ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ansible",
                "ansibleguard-output", "node_modules"}
                and not (Path(parent) / name).is_symlink()
                and (Path(parent) / name).resolve() != excluded)
            for name in sorted(files):
                if name == ".git":
                    continue
                path = Path(parent) / name
                if path.is_symlink() or not path.is_file():
                    return None
                size = path.stat().st_size
                total += size
                if total > 64 * 1024 * 1024 or len(entries) >= 10000:
                    return None
                entries.append((path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
        return hashlib.sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest()
    except OSError:
        return None


def model_identity(host, model, opener, url_builder, timeout=5):
    try:
        url = url_builder(host).removesuffix("/api/chat") + "/api/tags"
        with opener(urllib.request.Request(url), timeout=timeout) as response:
            raw = response.read(256 * 1024 + 1)
        if len(raw) > 256 * 1024:
            return None
        entries = json.loads(raw)["models"]
        matches = [entry["digest"] for entry in entries if isinstance(entry, dict)
                   and entry.get("name") == model and isinstance(entry.get("digest"), str) and entry["digest"]]
        return matches[0] if len(matches) == 1 else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def write_checkpoint(directory, key, payload):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,160}", key):
        raise ValueError("unsafe explanation checkpoint key")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=directory, prefix=".attempt-", delete=False, encoding="utf-8") as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, sort_keys=True, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        history = directory / "history"
        history.mkdir(exist_ok=True, mode=0o700)
        history.chmod(0o700)
        # Keep every attempt, including failed retries, before updating latest.
        with tempfile.NamedTemporaryFile(mode="w", dir=history, prefix=f"{key}-", suffix=".json",
                                         delete=False, encoding="utf-8") as attempt:
            json.dump(payload, attempt, sort_keys=True, ensure_ascii=False, indent=2)
            attempt.flush()
            os.fsync(attempt.fileno())
        temporary.replace(directory / f"{key}.json")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_checkpoint(directory, key):
    try:
        path = Path(directory) / f"{key}.json"
        if path.is_symlink() or path.stat().st_size > 2 * 1024 * 1024:
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if (isinstance(value, dict) and value.get("key") == key
                         and isinstance(value.get("result"), dict)) else None
    except (OSError, ValueError, TypeError):
        return None

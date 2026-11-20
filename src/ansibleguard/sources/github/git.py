"""Temporary Git acquisition with tokenless remotes and ephemeral auth headers."""

from __future__ import annotations

import os
import configparser
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlparse

from ..errors import SourceError
from .auth import git_auth_environment, redact_secrets

LFS_POINTER_RE = re.compile(
    rb"^version https://git-lfs\.github\.com/spec/v1\n"
    rb"oid sha256:[0-9a-f]{64}\nsize [0-9]+(?:\n|$)"
)


def _run_git(arguments, *, cwd: Path, environment, token=None) -> str:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=cwd,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        detail = getattr(exc, "stderr", "") or type(exc).__name__
        raise SourceError(
            "GitHub Git acquisition failed: " + redact_secrets(detail.strip(), (token,))
        ) from exc
    return completed.stdout.strip()


def find_lfs_pointers(root: Path) -> tuple[str, ...]:
    pointers = []
    for current, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if name != ".git"]
        for name in filenames:
            path = Path(current) / name
            try:
                if path.stat().st_size > 1024:
                    continue
                payload = path.read_bytes()
            except OSError:
                continue
            if LFS_POINTER_RE.match(payload):
                pointers.append(path.relative_to(root).as_posix())
    return tuple(sorted(pointers))


def validate_submodules(root: Path, host: str) -> tuple[dict[str, str], ...]:
    """Reject credentialed, cross-host, executable, or escaping submodules."""

    path = Path(root) / ".gitmodules"
    if not path.is_file():
        return ()
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        parser.read(path, encoding="utf-8")
    except (OSError, configparser.Error) as exc:
        raise SourceError(".gitmodules is invalid") from exc
    rows = []
    for section in parser.sections():
        if not section.startswith('submodule "'):
            raise SourceError(".gitmodules contains an unsupported section")
        relative = Path(parser.get(section, "path", fallback=""))
        url = parser.get(section, "url", fallback="").strip()
        update = parser.get(section, "update", fallback="checkout").strip()
        if not relative.as_posix() or relative.is_absolute() or ".." in relative.parts:
            raise SourceError("submodule path escapes the repository")
        if not url or update.startswith("!"):
            raise SourceError("submodule configuration is unsafe")
        if "://" in url:
            parsed = urlparse(url)
            if (
                parsed.scheme != "https"
                or parsed.hostname != host
                or parsed.username
                or parsed.password
            ):
                raise SourceError(
                    "submodule URL must be credential-free HTTPS on the source host"
                )
        elif url.startswith(("/", "~")) or ":" in url or "@" in url:
            raise SourceError("submodule URL uses an unsupported transport")
        rows.append({"path": relative.as_posix(), "url": url})
    return tuple(sorted(rows, key=lambda row: row["path"]))


def materialize_git_checkout(
    *,
    repository: str,
    host: str,
    sha: str,
    destination: Path,
    token: str | None,
    include_submodules: bool = False,
    include_lfs: bool = False,
    auth_environment: dict[str, str] | None = None,
) -> dict:
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    environment = auth_environment or git_auth_environment(token, host)
    remote = f"https://{host}/{repository}.git"
    try:
        _run_git(
            ["init", "--quiet"], cwd=destination, environment=environment, token=token
        )
        _run_git(
            ["remote", "add", "origin", remote],
            cwd=destination,
            environment=environment,
            token=token,
        )
        _run_git(
            # Review metadata compares HEAD with its parent. Fetching two
            # commits preserves that behavior without cloning full history.
            ["fetch", "--quiet", "--depth=2", "origin", sha],
            cwd=destination,
            environment=environment,
            token=token,
        )
        _run_git(
            ["checkout", "--quiet", "--detach", "FETCH_HEAD"],
            cwd=destination,
            environment=environment,
            token=token,
        )
        submodules_present = (destination / ".gitmodules").is_file()
        submodules = (
            validate_submodules(destination, host) if submodules_present else ()
        )
        if include_submodules and submodules_present:
            _run_git(
                ["submodule", "update", "--init", "--recursive", "--depth=1"],
                cwd=destination,
                environment=environment,
                token=token,
            )
            enriched = []
            for row in submodules:
                submodule_root = destination / row["path"]
                submodule_sha = _run_git(
                    ["rev-parse", "HEAD"],
                    cwd=submodule_root,
                    environment=environment,
                    token=token,
                )
                from ..snapshot import fingerprint_tree

                submodule_tree_sha256, _ = fingerprint_tree(submodule_root)
                enriched.append(
                    {
                        **row,
                        "commit": submodule_sha,
                        "tree_sha256": submodule_tree_sha256,
                    }
                )
            submodules = tuple(enriched)
        lfs_before = find_lfs_pointers(destination)
        if include_lfs and lfs_before:
            if shutil.which("git-lfs") is None and shutil.which("git") is not None:
                try:
                    _run_git(
                        ["lfs", "version"],
                        cwd=destination,
                        environment=environment,
                        token=token,
                    )
                except SourceError as exc:
                    raise SourceError(
                        "Git LFS materialization was requested but git-lfs is unavailable"
                    ) from exc
            _run_git(
                ["lfs", "pull"],
                cwd=destination,
                environment=environment,
                token=token,
            )
        lfs_after = find_lfs_pointers(destination)
        return {
            "remote_url": remote,
            "shallow": True,
            "history_depth": 2,
            "submodules": {
                "present": submodules_present,
                "materialized": bool(include_submodules and submodules_present),
                "items": submodules,
            },
            "lfs": {
                "pointers_detected": len(lfs_before),
                "materialized": bool(include_lfs and lfs_before and not lfs_after),
                "remaining_pointers": len(lfs_after),
            },
        }
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def diff_against_remote(
    *,
    base_tree: Path,
    head_repository: str,
    head_sha: str,
    host: str,
    token: str | None,
) -> str:
    """Use real Git objects to diff a base checkout against any head repository."""

    environment = git_auth_environment(token, host)
    remote_name = "ansibleguard-head"
    remote = f"https://{host}/{head_repository}.git"
    ref = "refs/ansibleguard/head"
    _run_git(
        ["remote", "add", remote_name, remote],
        cwd=base_tree,
        environment=environment,
        token=token,
    )
    _run_git(
        ["fetch", "--quiet", "--depth=1", remote_name, f"{head_sha}:{ref}"],
        cwd=base_tree,
        environment=environment,
        token=token,
    )
    return _run_git(
        [
            "diff",
            "--unified=0",
            "--no-ext-diff",
            "HEAD",
            ref,
            "--",
            "*.yml",
            "*.yaml",
        ],
        cwd=base_tree,
        environment=environment,
        token=token,
    )


def verify_git_checkout(root: Path, expected_sha: str) -> bool:
    """Validate cached Git metadata and the exact checked-out commit."""

    try:
        actual = _run_git(
            ["rev-parse", "HEAD"],
            cwd=root,
            environment=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
        )
        _run_git(
            ["fsck", "--connectivity-only", "--no-dangling"],
            cwd=root,
            environment=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
        )
    except SourceError:
        return False
    return actual.lower() == expected_sha.lower()

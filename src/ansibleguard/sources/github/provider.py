"""GitHub repository/ref/commit materialization."""

from __future__ import annotations

from pathlib import Path
from contextlib import nullcontext
import shutil
import tempfile

from ..base import SourceProvider
from ..cache.base import CacheBackend
from ..cache.keys import SourceCacheKey
from ..errors import SourceError
from ..snapshot import (
    MaterializedSource,
    SourceCapabilities,
    SourceSnapshot,
    fingerprint_tree,
)
from .archive import DEFAULT_MAX_ARCHIVE_BYTES, secure_extract_tar
from .client import GitHubClient
from .git import find_lfs_pointers, materialize_git_checkout, verify_git_checkout
from .urls import GitHubTarget, parse_github_target


class GitHubSource(SourceProvider):
    def __init__(
        self,
        target: str | GitHubTarget,
        *,
        ref: str | None = None,
        commit: str | None = None,
        host: str | None = None,
        acquisition: str = "auto",
        history_required: bool = False,
        include_submodules: bool = False,
        include_lfs: bool = False,
        client: GitHubClient | None = None,
        cache: CacheBackend | None = None,
        cache_pinned: bool = False,
        max_archive_bytes: int = DEFAULT_MAX_ARCHIVE_BYTES,
    ) -> None:
        parsed = (
            target
            if isinstance(target, GitHubTarget)
            else parse_github_target(target, host=host)
        )
        if parsed.pull_request is not None:
            raise SourceError("use the github-pr workflow for pull request URLs")
        if ref and commit:
            raise SourceError("--ref and --commit are mutually exclusive")
        if parsed.ref and (ref or commit) or parsed.commit and (ref or commit):
            raise SourceError(
                "target URL and command options specify conflicting revisions"
            )
        if acquisition not in {"auto", "archive", "git"}:
            raise SourceError("GitHub acquisition must be auto, archive, or git")
        self.target = parsed
        self.ref = ref or parsed.ref
        self.commit = commit or parsed.commit
        self.acquisition = (
            "git"
            if acquisition == "auto" and history_required
            else ("archive" if acquisition == "auto" else acquisition)
        )
        self.include_submodules = include_submodules
        self.include_lfs = include_lfs
        self.client = client or GitHubClient(host=parsed.host)
        self.cache = cache
        self.cache_pinned = cache_pinned
        self.max_archive_bytes = max_archive_bytes

    def _resolve(self) -> tuple[str, str | None, str | None]:
        repository = self.target.full_name
        if self.commit:
            return self.client.resolve_ref(repository, self.commit), None, None
        if self.ref:
            return self.client.resolve_ref(repository, self.ref), self.ref, None
        metadata = self.client.get_repository(repository)
        default_branch = str(metadata.get("default_branch") or "")
        if not default_branch:
            raise SourceError("GitHub repository has no resolvable default branch")
        return (
            self.client.resolve_ref(repository, default_branch),
            default_branch,
            default_branch,
        )

    def materialize(self) -> MaterializedSource:
        sha, requested_ref, default_branch = self._resolve()
        temporary_root = Path(tempfile.mkdtemp(prefix="ansibleguard-github-"))
        tree = temporary_root / "repository"
        repository = self.target.full_name
        cache_key = SourceCacheKey(
            provider="github",
            host=self.target.host,
            repository=repository,
            commit=sha,
            acquisition=self.acquisition,
            include_submodules=self.include_submodules,
            include_lfs=self.include_lfs,
        )
        lock_context = (
            self.cache.lock(cache_key) if self.cache is not None else nullcontext()
        )
        try:
            lock_context.__enter__()
        except Exception:
            shutil.rmtree(temporary_root, ignore_errors=True)
            raise
        try:
            cached = self.cache.lookup(cache_key) if self.cache is not None else None
            if cached is not None:
                self.cache.materialize(cached, tree)
                if self.acquisition == "git" and not verify_git_checkout(tree, sha):
                    self.cache.invalidate(cache_key)
                    shutil.rmtree(tree, ignore_errors=True)
                    cached = None
            if cached is not None:
                acquisition_metadata = dict(
                    (cached.metadata or {}).get("acquisition", {})
                )
                capabilities = SourceCapabilities(
                    working_tree=True,
                    git_history=self.acquisition == "git",
                    diff=self.acquisition == "git",
                    pull_requests=False,
                )
                cache_metadata = {
                    "status": "hit",
                    "key": cache_key.digest,
                    "verified": cached.verified,
                }
            elif self.acquisition == "archive":
                if self.include_submodules or self.include_lfs:
                    raise SourceError(
                        "submodule/LFS materialization requires Git acquisition"
                    )
                archive = temporary_root / "source.tar.gz"
                self.client.download_archive(
                    repository,
                    sha,
                    archive,
                    max_bytes=self.max_archive_bytes,
                )
                secure_extract_tar(archive, tree)
                archive.unlink(missing_ok=True)
                acquisition_metadata = {
                    "submodules": {
                        "present": (tree / ".gitmodules").is_file(),
                        "materialized": False,
                        "items": [],
                    },
                    "lfs": {
                        "pointers_detected": len(find_lfs_pointers(tree)),
                        "materialized": False,
                    },
                }
                capabilities = SourceCapabilities(working_tree=True)
                cache_metadata = {"status": "miss", "key": cache_key.digest}
            else:
                acquisition_metadata = materialize_git_checkout(
                    repository=repository,
                    host=self.target.host,
                    sha=sha,
                    destination=tree,
                    token=self.client.token,
                    include_submodules=self.include_submodules,
                    include_lfs=self.include_lfs,
                )
                capabilities = SourceCapabilities(
                    working_tree=True,
                    git_history=True,
                    diff=True,
                    pull_requests=False,
                )
                cache_metadata = {"status": "miss", "key": cache_key.digest}
            tree_sha256, entries = fingerprint_tree(tree)
            if cached is None and self.cache is not None:
                self.cache.store(
                    cache_key,
                    tree,
                    tree_sha256,
                    metadata={"acquisition": acquisition_metadata},
                    pinned=self.cache_pinned,
                )
                cache_metadata["stored"] = True
            metadata = {
                "host": self.target.host,
                "default_branch": default_branch,
                "requested_commit": self.commit,
                "tree_entry_count": len(entries),
                "submodules": acquisition_metadata["submodules"],
                "lfs": acquisition_metadata["lfs"],
                "cache": (
                    cache_metadata
                    if self.cache is not None
                    else {"status": "not-configured"}
                ),
            }
            snapshot = SourceSnapshot(
                root=tree,
                provider="github",
                repository=repository,
                requested_ref=requested_ref,
                resolved_sha=sha,
                acquisition=self.acquisition,
                tree_sha256=tree_sha256,
                temporary=True,
                capabilities=capabilities,
                metadata=metadata,
            )
            return MaterializedSource.temporary_directory(snapshot, temporary_root)
        except Exception:
            shutil.rmtree(temporary_root, ignore_errors=True)
            raise
        finally:
            lock_context.__exit__(None, None, None)

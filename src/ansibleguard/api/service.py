"""Source-provider orchestration for CLI-independent workers and APIs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import uuid

from .jobs import InMemoryJobStore
from ..cli import analyze_path
from ..sources.errors import SourceError
from ..sources.capabilities import validate_profile_capabilities
from ..sources.github.client import GitHubClient
from ..sources.github.pr import resolve_pull_request
from ..sources.github.provider import GitHubSource
from ..sources.github.workflows import compare_github_snapshots
from ..sources.gitlab.provider import GitLabSource
from ..sources.local import LocalSource


def _now():
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AnalysisRequest:
    provider: str
    repository: str
    ref: str | None = None
    commit: str | None = None
    pull_request: int | None = None
    profile: str = "technical-full"
    host: str | None = None
    include_submodules: bool = False
    include_lfs: bool = False


class AnalysisService:
    def __init__(
        self,
        output_root,
        *,
        cache=None,
        jobs=None,
        allow_local=False,
        local_roots=(),
    ):
        self.output_root = Path(output_root).resolve()
        self.output_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.output_root, 0o700)
        self.cache = cache
        self.jobs = jobs or InMemoryJobStore()
        self.allow_local = bool(allow_local)
        self.local_roots = tuple(Path(path).resolve() for path in local_roots)

    def submit(self, request: AnalysisRequest) -> str:
        if request.provider not in {"local", "github", "gitlab", "github-pr"}:
            raise SourceError("unsupported analysis provider")
        if request.ref and request.commit:
            raise SourceError("ref and commit are mutually exclusive")
        if not request.repository.strip():
            raise SourceError("analysis repository/path is empty")
        if request.provider == "github-pr" and (
            request.pull_request is None or request.pull_request <= 0
        ):
            raise SourceError(
                "GitHub PR analysis requires a positive pull request number"
            )
        job_id = uuid.uuid4().hex
        self.jobs.put(
            job_id,
            {
                "schema_version": 1,
                "id": job_id,
                "status": "queued",
                "created_at": _now(),
                "updated_at": _now(),
                "request": asdict(request),
                "output": str(self.output_root / job_id),
                "error": None,
                "result": None,
            },
        )
        return job_id

    def _update(self, job_id, **values):
        job = self.jobs.get(job_id)
        if job is None:
            raise SourceError("analysis job does not exist")
        job.update(values, updated_at=_now())
        self.jobs.put(job_id, job)
        return job

    def _local_source(self, value):
        if not self.allow_local:
            raise SourceError("server-side local analysis is disabled")
        path = Path(value).resolve()
        if self.local_roots:
            allowed = False
            for root in self.local_roots:
                try:
                    path.relative_to(root)
                except ValueError:
                    continue
                allowed = True
                break
            if not allowed:
                raise SourceError("local path is outside the configured roots")
        return LocalSource(path)

    def execute(self, job_id: str) -> dict:
        job = self._update(job_id, status="acquiring")
        request = AnalysisRequest(**job["request"])
        output = Path(job["output"])
        try:
            if request.provider == "github-pr":
                client = GitHubClient(host=request.host or "github.com")
                pull = resolve_pull_request(
                    client, request.repository, int(request.pull_request or 0)
                )
                common = {
                    "host": request.host,
                    "acquisition": "git",
                    "include_submodules": request.include_submodules,
                    "include_lfs": request.include_lfs,
                    "client": client,
                    "cache": self.cache,
                }
                self._update(job_id, status="analyzing")
                result = compare_github_snapshots(
                    base_source=GitHubSource(
                        pull.base_repository, commit=pull.base_sha, **common
                    ),
                    head_source=GitHubSource(
                        pull.head_repository, commit=pull.head_sha, **common
                    ),
                    output=output,
                    profile=request.profile,
                )
            else:
                if request.provider == "local":
                    source = self._local_source(request.repository)
                elif request.provider == "github":
                    source = GitHubSource(
                        request.repository,
                        ref=request.ref,
                        commit=request.commit,
                        host=request.host,
                        history_required=request.profile
                        in {"technical-full", "pr", "review-range"},
                        include_submodules=request.include_submodules,
                        include_lfs=request.include_lfs,
                        cache=self.cache,
                    )
                else:
                    source = GitLabSource(
                        request.repository,
                        ref=request.ref,
                        commit=request.commit,
                        host=request.host,
                        history_required=request.profile
                        in {"technical-full", "pr", "review-range"},
                        include_submodules=request.include_submodules,
                        include_lfs=request.include_lfs,
                        cache=self.cache,
                    )
                with source.materialize() as snapshot:
                    validate_profile_capabilities(snapshot, request.profile)
                    self._update(job_id, status="analyzing")
                    result = analyze_path(
                        snapshot.root,
                        output,
                        profile=request.profile,
                        source_snapshot=snapshot,
                    )
            safe_result = {
                key: value for key, value in result.items() if key != "findings"
            }
            return self._update(job_id, status="completed", result=safe_result)
        except Exception as exc:
            # Source/client errors are deliberately credential-free. Store only
            # the exception type and safe public message, never request headers.
            self._update(
                job_id,
                status="failed",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise

    def get(self, job_id):
        job = self.jobs.get(job_id)
        if job is None:
            raise SourceError("analysis job does not exist")
        return job

    def findings(self, job_id):
        job = self.get(job_id)
        if job["status"] != "completed":
            return []
        output = Path(job["output"])
        candidates = (
            output / "canonical" / "occurrences.json",
            output / "head" / "canonical" / "occurrences.json",
        )
        for path in candidates:
            if path.is_file():
                payload = json.loads(path.read_text(encoding="utf-8"))
                return (
                    payload.get("items", payload)
                    if isinstance(payload, dict)
                    else payload
                )
        return []

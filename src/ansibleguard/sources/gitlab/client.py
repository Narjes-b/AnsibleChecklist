"""Small centralized GitLab REST client."""

from __future__ import annotations

from pathlib import Path
import time
from urllib.parse import quote

import requests

from ansibleguard import __version__

from ..errors import SourceError
from .auth import resolve_gitlab_token
from ..secrets import as_secret


class GitLabClient:
    def __init__(self, *, host="gitlab.com", token=None, session=None, retries=2):
        self.host = host.lower()
        self.api_root = f"https://{self.host}/api/v4"
        self.token = (
            as_secret(token) if token is not None else resolve_gitlab_token(self.host)
        )
        self.session = session or requests.Session()
        self.retries = retries

    def _headers(self):
        headers = {"User-Agent": f"AnsibleGuard/{__version__}"}
        if self.token:
            headers["PRIVATE-TOKEN"] = self.token.reveal()
        return headers

    def _request(self, endpoint, *, stream=False, **kwargs):
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(
                    f"{self.api_root}{endpoint}",
                    headers=self._headers(),
                    timeout=(10, 60),
                    stream=stream,
                    **kwargs,
                )
            except requests.RequestException as exc:
                if attempt < self.retries:
                    time.sleep(0.25 * (attempt + 1))
                    continue
                raise SourceError(
                    f"GitLab request failed: {type(exc).__name__}"
                ) from exc
            if response.status_code < 400:
                return response
            if (
                response.status_code in {429, 500, 502, 503, 504}
                and attempt < self.retries
            ):
                time.sleep(0.25 * (attempt + 1))
                continue
            if response.status_code in {401, 403, 404}:
                raise SourceError(
                    "GitLab authentication failed or project/ref is inaccessible "
                    f"(HTTP {response.status_code})"
                )
            raise SourceError(
                f"GitLab API request failed (HTTP {response.status_code})"
            )
        raise SourceError("GitLab request failed")

    @staticmethod
    def _json(response):
        try:
            payload = response.json()
        except ValueError as exc:
            raise SourceError("GitLab returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise SourceError("GitLab returned an unexpected response shape")
        return payload

    @staticmethod
    def _project(repository):
        return quote(repository, safe="")

    def get_project(self, repository):
        return self._json(self._request(f"/projects/{self._project(repository)}"))

    def resolve_ref(self, repository, ref):
        payload = self._json(
            self._request(
                f"/projects/{self._project(repository)}/repository/commits/"
                f"{quote(ref, safe='')}"
            )
        )
        sha = str(payload.get("id") or "")
        if len(sha) != 40:
            raise SourceError("GitLab did not resolve the ref to a full commit SHA")
        return sha

    def download_archive(self, repository, sha, destination: Path, *, max_bytes):
        response = self._request(
            f"/projects/{self._project(repository)}/repository/archive.tar.gz",
            stream=True,
            params={"sha": sha},
        )
        total = 0
        destination = Path(destination)
        try:
            with destination.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > max_bytes:
                        raise SourceError(
                            "GitLab archive exceeds the configured size limit"
                        )
                    output.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise

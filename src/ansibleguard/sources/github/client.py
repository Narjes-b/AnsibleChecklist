"""Central GitHub REST client with bounded retries and safe errors."""

from __future__ import annotations

from pathlib import Path
import time
from urllib.parse import quote

import requests

from ansibleguard import __version__

from ..errors import SourceError
from .auth import redact_secrets, resolve_github_token
from ..secrets import as_secret


class GitHubClient:
    def __init__(
        self,
        *,
        host: str = "github.com",
        token: str | None = None,
        session=None,
        timeout=(10, 60),
        retries: int = 2,
    ) -> None:
        self.host = host.lower()
        self.api_root = (
            "https://api.github.com"
            if self.host == "github.com"
            else f"https://{self.host}/api/v3"
        )
        self.token = (
            as_secret(token) if token is not None else resolve_github_token(self.host)
        )
        self.session = session or requests.Session()
        self.timeout = timeout
        self.retries = retries

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"AnsibleGuard/{__version__}",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token.reveal()}"
        return headers

    def _request(self, method: str, endpoint: str, *, stream=False, **kwargs):
        url = f"{self.api_root}{endpoint}"
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=self._headers(),
                    timeout=self.timeout,
                    stream=stream,
                    **kwargs,
                )
            except requests.RequestException as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.25 * (attempt + 1))
                    continue
                raise SourceError(
                    "GitHub request failed: "
                    + redact_secrets(type(exc).__name__, (self.token,))
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
                    "GitHub authentication failed or repository/ref is inaccessible "
                    f"(HTTP {response.status_code})"
                )
            raise SourceError(
                f"GitHub API request failed (HTTP {response.status_code})"
            )
        raise SourceError(
            "GitHub request failed: "
            + redact_secrets(type(last_error).__name__, (self.token,))
        )

    @staticmethod
    def _json(response) -> dict:
        try:
            payload = response.json()
        except (ValueError, requests.RequestException) as exc:
            raise SourceError("GitHub returned an invalid JSON response") from exc
        if not isinstance(payload, dict):
            raise SourceError("GitHub returned an unexpected response shape")
        return payload

    def get_repository(self, repository: str) -> dict:
        return self._json(self._request("GET", f"/repos/{repository}"))

    def resolve_ref(self, repository: str, ref: str) -> str:
        encoded = quote(ref, safe="")
        payload = self._json(
            self._request("GET", f"/repos/{repository}/commits/{encoded}")
        )
        sha = str(payload.get("sha") or "")
        if len(sha) != 40:
            raise SourceError("GitHub did not resolve the ref to a full commit SHA")
        return sha

    def get_commit(self, repository: str, commit: str) -> dict:
        encoded = quote(commit, safe="")
        return self._json(
            self._request("GET", f"/repos/{repository}/commits/{encoded}")
        )

    def get_pull_request(self, repository: str, number: int) -> dict:
        return self._json(
            self._request("GET", f"/repos/{repository}/pulls/{int(number)}")
        )

    def create_issue_comment(self, repository: str, number: int, body: str) -> dict:
        return self._json(
            self._request(
                "POST",
                f"/repos/{repository}/issues/{int(number)}/comments",
                json={"body": body},
            )
        )

    def compare(self, repository: str, base: str, head: str) -> dict:
        encoded = f"{quote(base, safe='')}...{quote(head, safe='')}"
        return self._json(
            self._request("GET", f"/repos/{repository}/compare/{encoded}")
        )

    def download_archive(
        self,
        repository: str,
        sha: str,
        destination: Path,
        *,
        max_bytes: int,
    ) -> Path:
        response = self._request(
            "GET", f"/repos/{repository}/tarball/{sha}", stream=True
        )
        total = 0
        destination = Path(destination)
        try:
            with destination.open("wb") as stream:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > max_bytes:
                        raise SourceError(
                            "GitHub archive exceeds the configured size limit"
                        )
                    stream.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return destination

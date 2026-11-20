"""Downstream GitHub PR comment publication."""

from __future__ import annotations

from .auth import redact_secrets
from .client import GitHubClient

COMMENT_MARKER = "<!-- ansibleguard-pr-summary -->"
MAX_COMMENT_CHARACTERS = 65_000


class GitHubCommentPublisher:
    def __init__(self, client: GitHubClient, repository: str) -> None:
        self.client = client
        self.repository = repository

    def publish(self, pull_request: int, summary: str) -> dict:
        safe_summary = redact_secrets(summary, (self.client.token,))
        body = f"{COMMENT_MARKER}\n{safe_summary.strip()}"
        if len(body) > MAX_COMMENT_CHARACTERS:
            body = body[: MAX_COMMENT_CHARACTERS - 20] + "\n\n… truncated"
        return self.client.create_issue_comment(
            self.repository, int(pull_request), body
        )

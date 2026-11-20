"""GitLab authentication without credentialed URLs or persistent config."""

from __future__ import annotations

import base64
import os
import subprocess

from ..secrets import RedactedEnvironment, SecretValue, as_secret


def resolve_gitlab_token(host: str = "gitlab.com") -> SecretValue | None:
    for name in ("GITLAB_TOKEN", "GL_TOKEN"):
        token = os.environ.get(name)
        if token:
            return SecretValue(token.strip())
    try:
        completed = subprocess.run(
            ["glab", "auth", "token", "--hostname", host],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = completed.stdout.strip()
    return SecretValue(value) if value else None


def gitlab_git_auth_environment(token, host: str) -> dict[str, str]:
    environment = RedactedEnvironment(os.environ)
    secret = as_secret(token)
    if not secret:
        return environment
    credential = base64.b64encode(f"oauth2:{secret.reveal()}".encode()).decode()
    environment.update(
        {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": f"http.https://{host}/.extraheader",
            "GIT_CONFIG_VALUE_0": f"Authorization: Basic {credential}",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return environment

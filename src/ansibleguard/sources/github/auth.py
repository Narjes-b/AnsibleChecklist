"""GitHub credential resolution and redaction."""

from __future__ import annotations

import os
import subprocess

from ..secrets import RedactedEnvironment, SecretValue, as_secret


def redact_secrets(value: object, secrets=()) -> str:
    text = str(value)
    for secret in secrets:
        if secret:
            raw = secret.reveal() if isinstance(secret, SecretValue) else str(secret)
            text = text.replace(raw, "<redacted>")
    return text


def resolve_github_token(host: str = "github.com") -> SecretValue | None:
    """Resolve credentials without persisting or printing them."""

    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        token = os.environ.get(name)
        if token:
            return SecretValue(token.strip())
    try:
        completed = subprocess.run(
            ["gh", "auth", "token", "--hostname", host],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = completed.stdout.strip()
    return SecretValue(value) if value else None


def git_auth_environment(token, host: str) -> dict[str, str]:
    """Pass an HTTP header to one Git process without writing Git config."""

    environment = RedactedEnvironment(os.environ)
    secret = as_secret(token)
    if not secret:
        return environment
    environment.update(
        {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": f"http.https://{host}/.extraheader",
            "GIT_CONFIG_VALUE_0": f"Authorization: Bearer {secret.reveal()}",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return environment

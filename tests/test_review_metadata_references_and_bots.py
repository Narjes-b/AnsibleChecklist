import subprocess

import pytest

from ansibleguard.detectors.review_metadata import BOT_AUTHOR_RE, BUG_REFERENCE_RE, _commit_messages


@pytest.mark.parametrize("message", [
    "Fix crash\n\nCloses-Bug: #12", "Fix crash\n\nFixes #34", "fix crash\n\nresolves owner/repo#5",
    "Fix crash\n\nSee https://github.com/o/r/issues/77", "Fix crash\n\nTracked in ABC-123",
    "Fix crash\n\nCloses: #9", "Fix crash (bug 4321)",
])
def test_reference_forms_are_recognised(message):
    assert BUG_REFERENCE_RE.search(message)


@pytest.mark.parametrize("message", [
    "Fix encoding, use UTF-8", "Fix the sha-256 digest", "Fix typo in README", "Fix issue with handlers",
    "Fix python-3 support",
])
def test_non_references_are_not_matched(message):
    assert not BUG_REFERENCE_RE.search(message)


def test_pull_request_number_alone_is_not_a_bug_reference():
    assert not BUG_REFERENCE_RE.search("Fix crash (#42)")


@pytest.mark.parametrize("author", ["dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>",
                                    "renovate <bot@renovateapp.com>", "github-actions <noreply@github.com>"])
def test_bots_are_recognised(author):
    assert BOT_AUTHOR_RE.search(author)


def test_commit_messages_skip_bot_authors(tmp_path):
    def run(*args, **env):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), **env})
    run("init", "-q")
    (tmp_path / "a").write_text("1")
    run("add", "-A")
    run("-c", "user.name=Person", "-c", "user.email=p@example.com", "commit", "-q", "-m", "Fix the thing")
    (tmp_path / "a").write_text("2")
    run("add", "-A")
    run("-c", "user.name=dependabot[bot]", "-c", "user.email=d@example.com", "commit", "-q", "-m", "Bump version")
    head = subprocess.run(["git", "-C", str(tmp_path), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    messages = _commit_messages(str(tmp_path), None, head)
    assert [m for _, m in messages] == ["Fix the thing"]

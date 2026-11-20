"""Git-aware checks for review criteria that cannot be inferred from YAML alone."""

from __future__ import annotations

import contextvars
from pathlib import Path
import os
import re
import subprocess

BUG_REFERENCE_RE = re.compile(
    r"(?:Closes|Related|Partial)-Bug:\s*#?\d+|\bbug\s*#?\d+\b"
    # Common tracker conventions: "Fixes #12", "Resolves owner/repo#12", issue URLs, tracker keys.
    r"|\b(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?)\s*:?\s+(?:[\w.-]+/[\w.-]+)?#\d+"
    r"|https?://\S+/(?:issues|bugs|bug|browse|tickets?)/\S+"
    r"|(?-i:\b(?!(?:UTF|SHA|ISO|RFC|CVE|MD|AES|TLS|SSL|PEP|X)-)[A-Z][A-Z0-9]{1,9}-\d+\b)",
    re.IGNORECASE,
)
# Authors that are automation, not people: message rules judge human-written commits.
BOT_AUTHOR_RE = re.compile(
    r"\[bot\]|dependabot|renovate|github-actions|pre-commit-ci|\bbot@|-bot\b|^bot$", re.IGNORECASE
)
DEPENDS_ON_RE = re.compile(r"^Depends-On:\s*(\S+)\s*$", re.MULTILINE | re.IGNORECASE)
VALID_DEPENDENCY_RE = re.compile(
    r"(?:https?://\S+/(?:\+/)?\d+/?$)|(?:^I[0-9a-f]{40}$)", re.IGNORECASE
)
BUG_WORD_RE = re.compile(r"\b(?:bug|fix|repair|regression|issue)\b", re.IGNORECASE)
COPYRIGHT_RE = re.compile(r"copyright", re.IGNORECASE)


def _git(cwd, *args):
    try:
        completed = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    return completed.stdout if completed.returncode == 0 else None


def _repository_root(target):
    target = Path(target).resolve()
    cwd = target if target.is_dir() else target.parent
    output = _git(cwd, "rev-parse", "--show-toplevel")
    return Path(output.strip()) if output else None


def _valid_commit(root, revision):
    return bool(
        revision
        and _git(root, "rev-parse", "--verify", f"{revision}^{{commit}}")
    )


# Set by ``ansibleguard diff`` for each base/head scan (per thread), so a local
# PR comparison reviews exactly ``base..head`` without process-wide variables.
REVIEW_RANGE_OVERRIDE = contextvars.ContextVar("ansibleguard_review_range", default=None)


def _review_range(root):
    override = REVIEW_RANGE_OVERRIDE.get()
    if override is not None:
        base, head = override
        if _valid_commit(root, head) and (base is None or _valid_commit(root, base)):
            return base, head
    head = os.environ.get("ANSIBLEGUARD_HEAD_SHA") or "HEAD"
    if not _valid_commit(root, head):
        head = "HEAD"
    requested_base = os.environ.get("ANSIBLEGUARD_BASE_SHA")
    if requested_base and _valid_commit(root, requested_base):
        base = requested_base
    else:
        parent = f"{head}^"
        base = parent if _valid_commit(root, parent) else None
    return base, head


def _has_unavailable_parent(root, head):
    """Return True when ``head`` records a parent commit that is not present.

    This is the shallow-snapshot case: the commit has history, but the clone
    stops at it. A genuine root commit has no ``parent`` header and returns
    False, so its full-tree diff remains a valid review range.
    """
    raw = _git(root, "cat-file", "-p", head) or ""
    for line in raw.splitlines():
        if not line:
            break
        if line.startswith("parent "):
            return True
    return False


# Changelog layouts recognized as a release note in the review range.
RELEASE_NOTE_DIRECTORIES = (
    "releasenotes/notes/",
    "release_notes/",
    "changelogs/fragments/",
    "changelog.d/",
    ".changes/",
    "newsfragments/",
)
# Top-level-style changelog documents; YAML names are excluded so that an
# ordinary configuration file such as ``changes.yml`` is not a release note.
RELEASE_NOTE_FILE_RE = re.compile(
    r"(?:^|/)(?:changelog|changes|news|history|release[-_]?notes)"
    r"(?:\.(?:md|rst|txt|adoc))?$|(?:^|/)changelogs/changelog\.ya?ml$",
    re.IGNORECASE,
)


def _is_release_note(path):
    normalized = path.replace("\\", "/").lower()
    return any(
        normalized.startswith(directory) or f"/{directory}" in normalized
        for directory in RELEASE_NOTE_DIRECTORIES
    ) or bool(RELEASE_NOTE_FILE_RE.search(normalized))


def _changed_files(root, base, head):
    if base:
        output = _git(root, "diff", "--name-status", f"{base}...{head}")
    else:
        output = _git(
            root,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-status",
            "-r",
            head,
        )
    changes = []
    for line in (output or "").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            changes.append((parts[0], parts[-1]))
    return changes


def _commit_messages(root, base, head):
    revision = f"{base}..{head}" if base else head
    # Merge commits carry Git-generated messages ("Merge branch ..."); message
    # rules judge only commits a person wrote.
    output = _git(root, "log", "--no-merges", "--format=%H%x1f%an <%ae>%x1f%B%x1e", revision) or ""
    messages = []
    for record in output.split("\x1e"):
        record = record.strip()
        if record.count("\x1f") < 2:
            continue
        commit, author, message = record.split("\x1f", 2)
        if BOT_AUTHOR_RE.search(author):
            continue
        messages.append((commit, message.rstrip()))
    return messages


# YAML files of other tools that commonly live in Ansible repositories.
NON_ANSIBLE_YAML_NAMES = {
    "kustomization.yaml", "kustomization.yml", "kustomizeconfig.yaml", "kustomizeconfig.yml",
    "chart.yaml", "chart.yml", "docker-compose.yml", "docker-compose.yaml", "compose.yml",
    "compose.yaml", ".gitlab-ci.yml", ".pre-commit-config.yaml", ".pre-commit-hooks.yaml",
    ".yamllint", ".yamllint.yml", ".yamllint.yaml", "mkdocs.yml", "mkdocs.yaml",
    ".readthedocs.yml", ".readthedocs.yaml", "codecov.yml", ".codecov.yml", "taskfile.yml",
    "taskfile.yaml", "renovate.yaml", ".zuul.yaml", "zuul.yaml",
}


def _is_configuration(path):
    normalized = path.replace("\\", "/").lower()
    if normalized.rsplit("/", 1)[-1] in NON_ANSIBLE_YAML_NAMES:
        return False
    return normalized.endswith((".yml", ".yaml")) and not _is_release_note(path) and not any(
        part in normalized.split("/")
        for part in (".github", "molecule", "test", "tests", "releasenotes", "changelogs")
    )


def _is_kubernetes_manifest(root, revision, path):
    """True for a YAML file whose documents are Kubernetes-style objects."""
    import yaml

    text = _git(root, "show", f"{revision}:{path}") if revision else None
    if not text:
        return False
    try:
        documents = [doc for doc in yaml.safe_load_all(text) if doc is not None]
    except yaml.YAMLError:
        return False
    return bool(documents) and all(
        isinstance(doc, dict) and "apiVersion" in doc and "kind" in doc
        for doc in documents
    )


def _is_test(path):
    parts = set(path.replace("\\", "/").lower().split("/"))
    return bool(parts & {"test", "tests", "molecule"})


def _detail(rule_file, issue, **metadata):
    return {"file": rule_file, "line": 1, "issue": issue, **metadata}


def detect_project_review_smells(target):
    root = _repository_root(target)
    if root is None:
        return {}

    base, head = _review_range(root)
    # Without the recorded parent the changed-file set is unknown. A root diff
    # would report every tracked file as added, so diff-dependent rules are
    # not evaluated; message-only rules still use the exact head message.
    range_unavailable = base is None and _has_unavailable_parent(root, head)
    changes = [] if range_unavailable else _changed_files(root, base, head)
    changed_paths = [path for _, path in changes]
    # Kubernetes manifests share the YAML extension but are not Ansible
    # configuration; AnsibleGuard does not analyze them either.
    configuration_changes = [
        path for status, path in changes
        if _is_configuration(path)
        and not _is_kubernetes_manifest(root, base if status.startswith("D") else head, path)
    ]
    test_changes = [path for path in changed_paths if _is_test(path)]
    messages = _commit_messages(root, base, head)
    results = {
        "missing_release_notes": [],
        "missing_bug_references": [],
        "invalid_depends_on_references": [],
        "commit_message_format_issues": [],
        "removed_copyright_notices": [],
        "missing_test_updates": [],
        "untested_override_changes": [],
    }

    if configuration_changes and not any(_is_release_note(path) for path in changed_paths):
        results["missing_release_notes"].append(
            _detail(
                configuration_changes[0],
                "The review range changes configuration without adding a release-note file.",
                base=base,
                head=head,
            )
        )

    for commit, message in messages:
        lines = message.splitlines()
        subject = lines[0] if lines else ""
        if BUG_WORD_RE.search(subject) and not BUG_REFERENCE_RE.search(message):
            results["missing_bug_references"].append(
                _detail(
                    ".",
                    "Bug/fix commit message has no Closes-Bug, Related-Bug, or bug-number reference.",
                    commit=commit,
                )
            )
        for reference in DEPENDS_ON_RE.findall(message):
            if not VALID_DEPENDENCY_RE.search(reference):
                results["invalid_depends_on_references"].append(
                    _detail(
                        ".",
                        f"Depends-On reference '{reference}' is not a review URL or Change-Id.",
                        commit=commit,
                    )
                )

        format_problems = []
        if len(subject) > 50:
            format_problems.append(f"subject is {len(subject)} characters (maximum 50)")
        if len(lines) > 1 and lines[1].strip():
            format_problems.append("subject is not followed by a blank line")
        long_body_lines = [
            number for number, line in enumerate(lines[2:], 3) if len(line) > 72
        ]
        if long_body_lines:
            format_problems.append(f"body lines exceed 72 characters: {long_body_lines}")
        if format_problems:
            results["commit_message_format_issues"].append(
                _detail(
                    ".",
                    "Commit message format: " + "; ".join(format_problems) + ".",
                    commit=commit,
                )
            )

    if base:
        for status, path in changes:
            if not status.startswith("M"):
                continue
            old_text = _git(root, "show", f"{base}:{path}")
            new_text = _git(root, "show", f"{head}:{path}")
            if new_text is None:
                continue
            old_header = "\n".join((old_text or "").splitlines()[:20])
            new_header = "\n".join(new_text.splitlines()[:20])
            if COPYRIGHT_RE.search(old_header) and not COPYRIGHT_RE.search(new_header):
                results["removed_copyright_notices"].append(
                    _detail(
                        path,
                        "A copyright notice present at the review base was removed.",
                        base=base,
                        head=head,
                    )
                )

    if configuration_changes and not test_changes:
        results["missing_test_updates"].append(
            _detail(
                configuration_changes[0],
                "Configuration files changed in the review range without a test or Molecule change.",
                base=base,
                head=head,
            )
        )

    override_changes = []
    for path in configuration_changes:
        normalized = "/" + path.replace("\\", "/").lower() + "/"
        if any(
            marker in normalized
            for marker in ("/defaults/", "/vars/", "/group_vars/", "/host_vars/")
        ):
            override_changes.append(path)
    if override_changes and not test_changes:
        results["untested_override_changes"].append(
            _detail(
                override_changes[0],
                "Defaults/vars changed in the review range without a corresponding override test.",
                base=base,
                head=head,
            )
        )

    output = {}
    if range_unavailable:
        output["review_range_unavailable"] = (
            f"commit {head} records a parent that is not present in this "
            "checkout; diff-dependent review rules (missing-release-note, "
            "missing-test-update, untested-override-change, "
            "removed-copyright-notice) were not evaluated"
        )
    for metric, details in results.items():
        output[metric] = len(details)
        output[f"{metric}_details"] = details
    return output

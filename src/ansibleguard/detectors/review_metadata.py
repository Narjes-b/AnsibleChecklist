"""Git-aware checks for review criteria that cannot be inferred from YAML alone."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

BUG_REFERENCE_RE = re.compile(
    r"(?:Closes|Related|Partial)-Bug:\s*#?\d+|\bbug\s*#?\d+\b", re.IGNORECASE
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


def _changed_files(root):
    output = _git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-status",
        "-r",
        "HEAD",
    )
    changes = []
    for line in (output or "").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            changes.append((parts[0], parts[-1]))
    return changes


def _is_configuration(path):
    normalized = path.replace("\\", "/").lower()
    return normalized.endswith((".yml", ".yaml")) and not any(
        part in normalized.split("/")
        for part in (".github", "molecule", "test", "tests", "releasenotes")
    )


def _is_test(path):
    parts = set(path.replace("\\", "/").lower().split("/"))
    return bool(parts & {"test", "tests", "molecule"})


def _detail(rule_file, issue):
    return {"file": rule_file, "line": 1, "issue": issue}


def detect_project_review_smells(target):
    root = _repository_root(target)
    if root is None:
        return {}

    changes = _changed_files(root)
    changed_paths = [path for _, path in changes]
    configuration_changes = [path for path in changed_paths if _is_configuration(path)]
    test_changes = [path for path in changed_paths if _is_test(path)]
    message = (_git(root, "show", "-s", "--format=%B", "HEAD") or "").rstrip()
    lines = message.splitlines()
    subject = lines[0] if lines else ""
    results = {
        "missing_release_notes": [],
        "missing_bug_references": [],
        "invalid_depends_on_references": [],
        "commit_message_format_issues": [],
        "removed_copyright_notices": [],
        "missing_test_updates": [],
        "untested_override_changes": [],
    }

    if configuration_changes and not any(
        "releasenotes/notes/" in path.replace("\\", "/").lower()
        or "release_notes/" in path.replace("\\", "/").lower()
        for path in changed_paths
    ):
        results["missing_release_notes"].append(
            _detail(
                configuration_changes[0],
                "The latest configuration change adds no release-note file.",
            )
        )

    if BUG_WORD_RE.search(subject) and not BUG_REFERENCE_RE.search(message):
        results["missing_bug_references"].append(
            _detail(
                ".",
                "Bug/fix commit message has no Closes-Bug, Related-Bug, or bug-number reference.",
            )
        )

    for reference in DEPENDS_ON_RE.findall(message):
        if not VALID_DEPENDENCY_RE.search(reference):
            results["invalid_depends_on_references"].append(
                _detail(
                    ".",
                    f"Depends-On reference '{reference}' is not a review URL or Change-Id.",
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
            _detail(".", "Commit message format: " + "; ".join(format_problems) + ".")
        )

    has_parent = _git(root, "rev-parse", "HEAD^") is not None
    if has_parent:
        for status, path in changes:
            if not status.startswith("M"):
                continue
            old_text = _git(root, "show", f"HEAD^:{path}")
            current_path = root / path
            try:
                new_text = current_path.read_text(encoding="utf-8")
            except OSError, UnicodeDecodeError:
                continue
            old_header = "\n".join((old_text or "").splitlines()[:20])
            new_header = "\n".join(new_text.splitlines()[:20])
            if COPYRIGHT_RE.search(old_header) and not COPYRIGHT_RE.search(new_header):
                results["removed_copyright_notices"].append(
                    _detail(
                        path,
                        "A copyright notice present in the parent revision was removed.",
                    )
                )

    if configuration_changes and not test_changes:
        results["missing_test_updates"].append(
            _detail(
                configuration_changes[0],
                "Configuration files changed in HEAD without a test or Molecule change.",
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
                "Defaults/vars changed without a corresponding test change for overrides.",
            )
        )

    output = {}
    for metric, details in results.items():
        output[metric] = len(details)
        output[f"{metric}_details"] = details
    return output

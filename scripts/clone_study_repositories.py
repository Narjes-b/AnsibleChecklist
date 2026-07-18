"""Clone selected study repositories and freeze an auditable manifest."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from ansibleguard.file_manifest import classify_repository, summarize_classification


DEFAULT_REPOS = Path("study/repositories")
DEFAULT_OUTPUT = Path("study/manifests/frozen.csv")
TRUE_VALUES = {"1", "true", "yes", "y"}
OUTPUT_FIELDS = (
    "project",
    "opendev_url",
    "repository_path",
    "default_branch",
    "commit_sha",
    "commit_date_utc",
    "collected_at_utc",
    "total_commits",
    "contributors",
    "yaml_files",
    "production_ansible_files",
    "test_ansible_files",
    "other_yaml_files",
    "invalid_yaml_files",
    "production_ansible_loc",
    "status",
    "error",
)


def _run(args, cwd=None):
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _truthy(value):
    return str(value or "").strip().lower() in TRUE_VALUES


def read_selected(manifest_path):
    with Path(manifest_path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    return [row for row in rows if _truthy(row.get("selected"))]


def _repo_path(repos_dir, project):
    return Path(repos_dir).joinpath(*project.split("/"))


def _clone_or_update(row, repos_dir, refresh=False):
    project = row["project"]
    url = row.get("opendev_url") or f"https://opendev.org/{project}.git"
    destination = _repo_path(repos_dir, project)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if (destination / ".git").is_dir():
        if refresh:
            _run(["git", "fetch", "--prune", "--tags", "origin"], destination)
    elif destination.exists():
        raise RuntimeError(f"Destination exists but is not a Git repository: {destination}")
    else:
        _run(["git", "clone", "--no-single-branch", url, destination])
    return destination, url


def _default_ref(repository):
    try:
        symbolic = _run(
            ["git", "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"],
            repository,
        )
        return symbolic.removeprefix("refs/remotes/origin/")
    except subprocess.CalledProcessError:
        return _run(["git", "branch", "--show-current"], repository) or "HEAD"


def _checkout_frozen(repository, revision):
    default_branch = _default_ref(repository)
    target = revision or f"origin/{default_branch}"
    try:
        sha = _run(["git", "rev-parse", f"{target}^{{commit}}"], repository)
    except subprocess.CalledProcessError:
        sha = _run(["git", "rev-parse", "HEAD^{commit}"], repository)
    _run(["git", "checkout", "--detach", sha], repository)
    return default_branch, sha


def classify_yaml(repository):
    """Backward-compatible aggregate backed by the row-level classifier."""
    return summarize_classification(classify_repository(Path(repository)))


def collect_row(row, repos_dir=DEFAULT_REPOS, refresh=False):
    project = row.get("project", "")
    base = {field: "" for field in OUTPUT_FIELDS}
    base["project"] = project
    try:
        repository, url = _clone_or_update(row, repos_dir, refresh)
        default_branch, sha = _checkout_frozen(repository, row.get("revision", ""))
        counts = classify_yaml(repository)
        base.update(
            {
                "opendev_url": url,
                "repository_path": str(repository.resolve()),
                "default_branch": default_branch,
                "commit_sha": sha,
                "commit_date_utc": _run(
                    ["git", "show", "-s", "--format=%cI", sha], repository
                ),
                "collected_at_utc": datetime.now(timezone.utc).isoformat(),
                "total_commits": _run(
                    ["git", "rev-list", "--count", sha], repository
                ),
                "contributors": len(
                    _run(["git", "shortlog", "-sne", sha], repository).splitlines()
                ),
                **counts,
                "status": "collected",
            }
        )
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        base["status"] = "failed"
        base["error"] = str(exc)
    return base


def write_rows(rows, output_path=DEFAULT_OUTPUT):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clone selected OpenStack study repositories and freeze SHAs."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repos-dir", type=Path, default=DEFAULT_REPOS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)
    selected = read_selected(args.manifest)
    if args.limit is not None:
        selected = selected[: args.limit]
    rows = []
    for index, row in enumerate(selected, 1):
        print(f"[{index}/{len(selected)}] collecting {row['project']}")
        result = collect_row(row, args.repos_dir, args.refresh)
        rows.append(result)
        print(f"  {result['status']} sha={result['commit_sha'] or '-'}")
    output = write_rows(rows, args.output)
    failures = sum(row["status"] != "collected" for row in rows)
    print(f"Wrote {len(rows)} frozen rows to {output}; failures={failures}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

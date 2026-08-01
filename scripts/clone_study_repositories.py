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
    "source_host",
    "source_url",
    "clone_url",
    "opendev_url",
    "github_url",
    "stars",
    "star_band",
    "forks",
    "license_spdx",
    "merged_prs_last_24_months",
    "preclone_eligible",
    "preclone_reasons",
    "repository_path",
    "default_branch",
    "commit_sha",
    "commit_date_utc",
    "collected_at_utc",
    "total_commits",
    "contributors",
    "recent_contributors_24_months",
    "yaml_files",
    "yaml_loc",
    "production_ansible_files",
    "test_ansible_files",
    "other_yaml_files",
    "invalid_yaml_files",
    "production_ansible_loc",
    "production_ansible_yaml_file_percent",
    "production_ansible_yaml_loc_percent",
    "ansible_touching_commits",
    "eligibility_status",
    "eligibility_reasons",
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
    return [
        row
        for row in rows
        if _truthy(row.get("selected"))
        or _truthy(row.get("collect_for_screening"))
    ]


def _repo_path(repos_dir, project):
    return Path(repos_dir).joinpath(*project.split("/"))


def _source_host(row):
    explicit = str(row.get("source_host") or "").strip().lower()
    if explicit:
        return explicit
    if row.get("clone_url") or row.get("github_url") or row.get("html_url"):
        return "github"
    return "opendev"


def _clone_or_update(row, repos_dir, refresh=False):
    project = row["project"]
    source_host = _source_host(row)
    if source_host == "github":
        url = (
            row.get("clone_url")
            or (f"{row['github_url']}.git" if row.get("github_url") else "")
            or f"https://github.com/{project}.git"
        )
    else:
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


def _percentage(numerator, denominator):
    return round((100 * numerator / denominator), 2) if denominator else 0.0


def _ansible_touching_commits(repository, sha, paths):
    if not paths:
        return 0
    commits = _run(
        ["git", "log", "--format=%H", sha, "--", *paths], repository
    ).splitlines()
    return len(set(commits))


def _eligibility(row, source_host, metrics):
    if source_host != "github":
        return "separate-non-github-stratum", ""
    reasons = []
    preclone_eligible = str(row.get("preclone_eligible") or "").strip().lower()
    if preclone_eligible and preclone_eligible != "true":
        detail = str(row.get("preclone_reasons") or "unspecified")
        reasons.append(f"preclone-ineligible:{detail}")
    if not str(row.get("license_spdx") or "").strip():
        reasons.append("license-needs-review")
    if int(metrics["total_commits"]) < 80:
        reasons.append("fewer-than-80-commits")
    if metrics["contributors"] < 2:
        reasons.append("fewer-than-2-contributors")
    if metrics["production_ansible_files"] < 10:
        reasons.append("fewer-than-10-production-ansible-files")
    if metrics["production_ansible_loc"] < 500:
        reasons.append("fewer-than-500-production-ansible-loc")
    if metrics["ansible_touching_commits"] < 20:
        reasons.append("fewer-than-20-ansible-touching-commits")
    if (
        metrics["production_ansible_yaml_file_percent"] < 20
        and metrics["production_ansible_loc"] < 2000
    ):
        reasons.append("insufficient-ansible-share-or-size")
    recent_prs = str(row.get("merged_prs_last_24_months") or "").strip()
    has_recent_pr_evidence = recent_prs.isdigit() and int(recent_prs) >= 5
    if not has_recent_pr_evidence and metrics["recent_contributors_24_months"] < 2:
        reasons.append("insufficient-recent-pr-or-contributor-activity")
    return ("eligible" if not reasons else "ineligible"), ";".join(reasons)


def collect_row(row, repos_dir=DEFAULT_REPOS, refresh=False):
    project = row.get("project", "")
    base = {field: "" for field in OUTPUT_FIELDS}
    base["project"] = project
    try:
        source_host = _source_host(row)
        repository, url = _clone_or_update(row, repos_dir, refresh)
        default_branch, sha = _checkout_frozen(repository, row.get("revision", ""))
        classified = classify_repository(repository)
        counts = summarize_classification(classified)
        yaml_loc = sum(int(item.get("loc") or 0) for item in classified)
        production_paths = [
            item["path"] for item in classified if item["included"] == "true"
        ]
        total_commits = _run(["git", "rev-list", "--count", sha], repository)
        contributor_lines = _run(
            ["git", "shortlog", "-sne", sha], repository
        ).splitlines()
        recent_contributor_lines = _run(
            ["git", "shortlog", "-sne", "--since=24 months ago", sha], repository
        ).splitlines()
        metrics = {
            **counts,
            "yaml_loc": yaml_loc,
            "total_commits": total_commits,
            "contributors": len(contributor_lines),
            "recent_contributors_24_months": len(recent_contributor_lines),
            "production_ansible_yaml_file_percent": _percentage(
                counts["production_ansible_files"], counts["yaml_files"]
            ),
            "production_ansible_yaml_loc_percent": _percentage(
                counts["production_ansible_loc"], yaml_loc
            ),
            "ansible_touching_commits": _ansible_touching_commits(
                repository, sha, production_paths
            ),
        }
        eligibility_status, eligibility_reasons = _eligibility(
            row, source_host, metrics
        )
        base.update(
            {
                "source_host": source_host,
                "source_url": row.get("source_url") or url,
                "clone_url": row.get("clone_url") or url,
                "opendev_url": url if source_host == "opendev" else "",
                "github_url": row.get("github_url") or (
                    row.get("html_url") if source_host == "github" else ""
                ),
                "stars": row.get("stars", ""),
                "star_band": row.get("star_band", ""),
                "forks": row.get("forks", ""),
                "license_spdx": row.get("license_spdx", ""),
                "merged_prs_last_24_months": row.get(
                    "merged_prs_last_24_months", ""
                ),
                "preclone_eligible": row.get("preclone_eligible", ""),
                "preclone_reasons": row.get("preclone_reasons", ""),
                "repository_path": str(repository.resolve()),
                "default_branch": default_branch,
                "commit_sha": sha,
                "commit_date_utc": _run(
                    ["git", "show", "-s", "--format=%cI", sha], repository
                ),
                "collected_at_utc": datetime.now(timezone.utc).isoformat(),
                **metrics,
                "eligibility_status": eligibility_status,
                "eligibility_reasons": eligibility_reasons,
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
        writer = csv.DictWriter(
            stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clone selected study repositories and freeze auditable SHAs."
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

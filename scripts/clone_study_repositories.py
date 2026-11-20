"""Clone selected study repositories and freeze an auditable manifest."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
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
    "total_prs",
    "merged_prs",
    "merged_prs_last_24_months",
    "merged_ansible_changing_prs",
    "ansible_pr_scan_status",
    "preclone_eligible",
    "preclone_reasons",
    "repository_path",
    "default_branch",
    "commit_sha",
    "commit_date_utc",
    "collected_at_utc",
    "total_commits",
    "total_commits_source",
    "preclone_total_commits",
    "preclone_total_commits_source",
    "contributors",
    "recent_contributors_24_months",
    "yaml_files",
    "yaml_loc",
    "production_ansible_files",
    "test_ansible_files",
    "other_yaml_files",
    "invalid_yaml_files",
    "production_ansible_loc",
    "primary_ansibleguard_files",
    "paper_comparable_files",
    "import_only_ansible_files",
    "production_ansible_yaml_file_percent",
    "production_ansible_yaml_loc_percent",
    "ansible_touching_commits",
    "first_ansible_commit_date_utc",
    "latest_ansible_commit_date_utc",
    "ansible_history_span_days",
    "repository_total_files",
    "production_ansible_repository_file_percent",
    "production_playbook_files",
    "production_task_files",
    "production_vars_files",
    "production_metadata_files",
    "production_other_document_files",
    "repository_owner",
    "repository_family",
    "ecosystem_cluster",
    "project_purpose_auto",
    "project_purpose_auto_confidence",
    "project_purpose_evidence",
    "project_purpose_manual",
    "project_purpose_manual_reason",
    "ansible_content_fingerprint",
    "exact_ansible_duplicate_group",
    "independence_review_status",
    "descriptive_evidence_used_for_selection",
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


def _force_remove_readonly(func, path, exc_info):
    """shutil.rmtree onerror handler for Windows: git marks some
    object-database files read-only, which plain rmtree can't remove.
    Clear the bit and retry."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_partial_clone(path):
    """Best-effort cleanup of a failed clone's partial directory.

    Never raises: a directory that stubbornly won't delete (e.g. a file
    locked by another process) should degrade to "leave it, let the
    next attempt fail with a clear git error" rather than crash the
    whole collection run over one repository's cleanup.
    """
    try:
        shutil.rmtree(path, onerror=_force_remove_readonly)
    except OSError:
        pass


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
        # -c core.longpaths=true is a one-off, per-invocation override
        # (not a persistent/global git config change) that avoids
        # Windows MAX_PATH failures on repositories with deeply nested
        # files -- confirmed to occur in practice against large,
        # real-world Ansible repositories. On failure, the partial
        # destination is removed so a retry actually retries instead of
        # failing with "destination exists and is not empty".
        try:
            _run(
                ["git", "-c", "core.longpaths=true", "clone", "--no-single-branch",
                 url, destination],
            )
        except subprocess.CalledProcessError:
            _remove_partial_clone(destination)
            raise
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


def _ansible_history(repository, sha, paths):
    if not paths:
        return "", "", ""
    dates = _run(
        ["git", "log", "--format=%cI", sha, "--", *paths], repository
    ).splitlines()
    if not dates:
        return "", "", ""
    latest, first = dates[0], dates[-1]
    latest_date = datetime.fromisoformat(latest.replace("Z", "+00:00"))
    first_date = datetime.fromisoformat(first.replace("Z", "+00:00"))
    return first, latest, str((latest_date - first_date).days)


def _content_fingerprint(repository, paths):
    digest = hashlib.sha256()
    for relative in sorted(paths):
        path = repository / relative
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest() if paths else ""


def _family_name(project):
    name = project.split("/", 1)[-1].lower()
    name = re.sub(r"^(ansible[-_]?|collection[-_]?|role[-_]?)", "", name)
    name = re.sub(r"[-_](ansible|collection|role)$", "", name)
    return name or project.split("/", 1)[-1].lower()


def _purpose(project, row, repository, classified):
    text = " ".join(
        [project, str(row.get("description") or ""), str(row.get("topics") or "")]
    ).lower()
    paths = {item["path"].lower() for item in classified}
    if any(word in text for word in ("tutorial", "workshop", "training", "example")):
        return "example-or-training-candidate", "medium", "metadata-keyword;manual-confirmation-required"
    if any(path in paths for path in ("galaxy.yml", "galaxy.yaml")) or (repository / "plugins").is_dir():
        return "ansible-collection", "high", "galaxy-metadata-or-plugins-layout"
    if (
        any(path.endswith("/tasks/main.yml") or path == "tasks/main.yml" for path in paths)
        and any(path.endswith("/meta/main.yml") or path == "meta/main.yml" for path in paths)
    ):
        return "ansible-role", "high", "role-tasks-and-metadata-layout"
    return "infrastructure-or-mixed-ansible-project", "low", "production-ansible-present;manual-classification-required"


def _composition(classified):
    production = [item for item in classified if item["included"] == "true"]
    counts = {
        "playbook": 0,
        "tasks": 0,
        "vars": 0,
        "metadata": 0,
        "other": 0,
    }
    for item in production:
        kind = item.get("document_type", "")
        counts[kind if kind in counts else "other"] += 1
    return counts


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
    if int(metrics["total_commits"]) < 1000:
        reasons.append("fewer-than-1000-commits")
    if metrics["production_ansible_files"] < 1:
        reasons.append("no-production-ansible-files")
    total_prs = str(row.get("total_prs") or "").strip()
    if not total_prs.isdigit():
        reasons.append("total-prs-not-evaluated")
    elif int(total_prs) <= 50:
        reasons.append("not-more-than-50-total-prs")
    ansible_prs = str(row.get("merged_ansible_changing_prs") or "").strip()
    if not ansible_prs.isdigit():
        reasons.append("ansible-changing-prs-not-evaluated")
    elif int(ansible_prs) < 50:
        reasons.append("fewer-than-50-merged-ansible-changing-prs")
    known_failures = [reason for reason in reasons if not reason.endswith("not-evaluated")]
    return (
        "eligible" if not reasons
        else "ineligible" if known_failures
        else "pending"
    ), ";".join(reasons)


def collect_row(row, repos_dir=DEFAULT_REPOS, refresh=False):
    project = row.get("project", "")
    base = {field: "" for field in OUTPUT_FIELDS}
    base["project"] = project
    repository = None
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
        tracked_files = _run(["git", "ls-tree", "-r", "--name-only", sha], repository).splitlines()
        first_ansible, latest_ansible, history_days = _ansible_history(
            repository, sha, production_paths
        )
        composition = _composition(classified)
        purpose, purpose_confidence, purpose_evidence = _purpose(
            project, row, repository, classified
        )
        owner = project.split("/", 1)[0] if "/" in project else ""
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
            "total_commits_source": "frozen-git-rev-list",
            "preclone_total_commits": row.get("total_commits", ""),
            "preclone_total_commits_source": row.get("total_commits_source", ""),
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
            "first_ansible_commit_date_utc": first_ansible,
            "latest_ansible_commit_date_utc": latest_ansible,
            "ansible_history_span_days": history_days,
            "repository_total_files": len(tracked_files),
            "production_ansible_repository_file_percent": _percentage(
                len(production_paths), len(tracked_files)
            ),
            "production_playbook_files": composition["playbook"],
            "production_task_files": composition["tasks"],
            "production_vars_files": composition["vars"],
            "production_metadata_files": composition["metadata"],
            "production_other_document_files": composition["other"],
            "repository_owner": owner,
            "repository_family": _family_name(project),
            "ecosystem_cluster": owner,
            "project_purpose_auto": purpose,
            "project_purpose_auto_confidence": purpose_confidence,
            "project_purpose_evidence": purpose_evidence,
            "project_purpose_manual": row.get("project_purpose_manual", ""),
            "project_purpose_manual_reason": row.get("project_purpose_manual_reason", ""),
            "ansible_content_fingerprint": _content_fingerprint(
                repository, production_paths
            ),
            "exact_ansible_duplicate_group": "",
            "independence_review_status": "not-evaluated",
            "descriptive_evidence_used_for_selection": "false",
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
                "total_prs": row.get("total_prs", ""),
                "merged_prs": row.get("merged_prs", ""),
                "merged_prs_last_24_months": row.get(
                    "merged_prs_last_24_months", ""
                ),
                "merged_ansible_changing_prs": row.get(
                    "merged_ansible_changing_prs", ""
                ),
                "ansible_pr_scan_status": row.get(
                    "ansible_pr_scan_status", "not-evaluated"
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
    except Exception as exc:
        # Collection is a batch study operation: preserve the failed project
        # as evidence and allow the remaining repositories to be processed.
        # KeyboardInterrupt and SystemExit still propagate because they do not
        # inherit from Exception.
        base["status"] = "failed"
        base["error"] = f"{type(exc).__name__}: {exc}"
        if repository is not None:
            # A failure after the clone step (checkout, branch detection,
            # classification, git log parsing) can leave the working
            # directory in a bad state -- e.g. an interrupted process
            # killed mid-`git checkout` leaves a stale index.lock that
            # makes every subsequent git command on this repo fail the
            # same way forever. _clone_or_update's ".git exists" fast path
            # would otherwise reuse that same broken directory on every
            # retry, so a repository is never actually re-cloned once it
            # first goes bad. Remove it so the next attempt starts clean.
            _remove_partial_clone(repository)
    return base


def write_rows(rows, output_path=DEFAULT_OUTPUT):
    rows = list(rows)
    fingerprints = {}
    for row in rows:
        fingerprint = row.get("ansible_content_fingerprint")
        if fingerprint:
            fingerprints.setdefault(fingerprint, []).append(row)
    duplicate_number = 0
    for group in fingerprints.values():
        if len(group) < 2:
            continue
        duplicate_number += 1
        label = f"exact-ansible-content-{duplicate_number}"
        for row in group:
            row["exact_ansible_duplicate_group"] = label
            row["independence_review_status"] = "exact-content-match-needs-review"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def _load_existing_collected(output_path):
    output_path = Path(output_path)
    if not output_path.is_file():
        return {}
    with output_path.open(newline="", encoding="utf-8") as stream:
        return {
            row["project"]: row
            for row in csv.DictReader(stream)
            if row.get("status") == "collected"
            and row.get("project")
            # A row can say "collected" from an earlier run while the clone
            # itself no longer exists -- e.g. a repository was eligible in
            # one pipeline attempt, pruned as disqualified, then became
            # eligible again in a later attempt once more PR evidence
            # accumulated. Trusting the CSV alone would skip re-cloning it
            # forever, silently leaving a "final eligible" repository with
            # no actual clone on disk.
            and row.get("repository_path")
            and Path(row["repository_path"]).is_dir()
        }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clone selected study repositories and freeze auditable SHAs."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repos-dir", type=Path, default=DEFAULT_REPOS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Resume from an existing --output file: reuse already-collected "
             "rows instead of re-cloning/re-analyzing them",
    )
    args = parser.parse_args(argv)
    selected = read_selected(args.manifest)
    if args.limit is not None:
        selected = selected[: args.limit]

    existing = _load_existing_collected(args.output) if args.skip_existing else {}
    rows = list(existing.values())
    pending = [row for row in selected if row.get("project") not in existing]
    if existing:
        print(f"Resuming: {len(existing)} already collected, {len(pending)} remaining")

    # Every repository's outcome is written to disk immediately (not just
    # kept in memory) so a process-level interruption (kill, crash, closed
    # terminal) loses at most the one repository in flight, not the whole
    # run -- collect_row already turns per-repository failures into a
    # "failed" status row rather than raising, so the remaining gap was
    # purely this batch-at-the-end write.
    for index, row in enumerate(pending, 1):
        print(f"[{index}/{len(pending)}] collecting {row['project']}")
        result = collect_row(row, args.repos_dir, args.refresh)
        rows.append(result)
        print(f"  {result['status']} sha={result['commit_sha'] or '-'}")
        # Checkpoint after every repository. A later interruption can no
        # longer erase the evidence already calculated during this run.
        write_rows(rows, args.output)
    output = write_rows(rows, args.output)
    failures = sum(row["status"] != "collected" for row in rows)
    print(f"Wrote {len(rows)} frozen rows to {output}; failures={failures}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

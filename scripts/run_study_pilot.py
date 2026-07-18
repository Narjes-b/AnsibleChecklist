"""Run AnsibleGuard against repositories pinned by a frozen manifest."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys

from ansibleguard.file_manifest import file_manifest_metadata
from ansibleguard.profiles import PROFILE_NAMES


def _git_head(repository):
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def load_collected(manifest):
    with Path(manifest).open(newline="", encoding="utf-8") as stream:
        return [row for row in csv.DictReader(stream) if row.get("status") == "collected"]


def output_path(root, project, sha, profile="technical-full"):
    destination = Path(root) / project.replace("/", "__") / sha
    return destination if profile == "technical-full" else destination / profile


def classification_manifest_path(root, project, sha):
    return Path(root) / f"{project.replace('/', '__')}__{sha}.csv"


def run_row(
    row,
    output_root,
    logs_dir,
    skip_existing=False,
    file_manifests_dir=None,
    profile="technical-full",
):
    repository = Path(row["repository_path"])
    expected = row["commit_sha"]
    actual = _git_head(repository)
    if actual != expected:
        raise RuntimeError(
            f"{row['project']} HEAD is {actual}, but frozen manifest requires {expected}"
        )
    classification = None
    if file_manifests_dir is not None:
        classification = classification_manifest_path(
            file_manifests_dir, row["project"], row["commit_sha"]
        )
        if not classification.is_file():
            raise RuntimeError(f"classification manifest not found: {classification}")

    destination = output_path(output_root, row["project"], expected, profile)
    if skip_existing and (destination / "findings.json").is_file():
        if classification is not None:
            selection_path = destination / "file_selection.json"
            if not selection_path.is_file():
                raise RuntimeError(
                    f"existing output has no file-selection provenance: {destination}"
                )
            existing = json.loads(selection_path.read_text(encoding="utf-8"))
            requested = file_manifest_metadata(classification)
            if existing.get("manifest_sha256") != requested["manifest_sha256"]:
                raise RuntimeError(
                    f"existing output used a different classification manifest: "
                    f"{destination}"
                )
        run_metadata_path = destination / "run_metadata.json"
        if run_metadata_path.is_file():
            run_metadata = json.loads(run_metadata_path.read_text(encoding="utf-8"))
            existing_profile = run_metadata.get("profile", {}).get("name")
            if existing_profile != profile:
                raise RuntimeError(
                    f"existing output used profile {existing_profile!r}, requested "
                    f"{profile!r}: {destination}"
                )
        elif profile != "technical-full":
            raise RuntimeError(f"existing output has no profile provenance: {destination}")
        return "skipped", destination

    destination.mkdir(parents=True, exist_ok=True)
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    profile_suffix = "" if profile == "technical-full" else f"__{profile}"
    log_path = logs_dir / (
        f"{row['project'].replace('/', '__')}__{expected[:12]}{profile_suffix}.log"
    )
    command = [
        sys.executable,
        "-m",
        "ansibleguard.cli",
        str(repository),
        "--output",
        str(destination),
        "--fail-on",
        "never",
        "--profile",
        profile,
    ]
    if classification is not None:
        command.extend(["--file-manifest", str(classification)])
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"AnsibleGuard failed for {row['project']}; see {log_path}")
    return "completed", destination


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run a reproducible technical pilot from frozen repository SHAs."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-root", type=Path, default=Path("study/snapshots"))
    parser.add_argument("--logs-dir", type=Path, default=Path("study/logs"))
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--file-manifests-dir",
        type=Path,
        help="Directory containing per-project classification manifests",
    )
    parser.add_argument(
        "--profile",
        choices=PROFILE_NAMES,
        default="technical-full",
        help="AnsibleGuard execution profile",
    )
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)
    rows = load_collected(args.manifest)
    if args.limit is not None:
        rows = rows[: args.limit]
    for index, row in enumerate(rows, 1):
        print(f"[{index}/{len(rows)}] scanning {row['project']}@{row['commit_sha'][:12]}")
        status, destination = run_row(
            row,
            args.output_root,
            args.logs_dir,
            args.skip_existing,
            args.file_manifests_dir,
            args.profile,
        )
        print(f"  {status}: {destination}")


if __name__ == "__main__":
    main()

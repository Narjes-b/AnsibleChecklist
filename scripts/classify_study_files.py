"""Generate row-level YAML classification manifests for frozen repositories."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import subprocess

from ansibleguard.file_manifest import classify_repository, write_file_manifest


DEFAULT_OUTPUT_DIR = Path("study/manifests/file-classification")


def load_collected(frozen_manifest: Path) -> list[dict[str, str]]:
    with Path(frozen_manifest).open(newline="", encoding="utf-8") as stream:
        return [
            row for row in csv.DictReader(stream) if row.get("status") == "collected"
        ]


def _git_head(repository: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def manifest_path(output_dir: Path, project: str, commit_sha: str) -> Path:
    name = f"{project.replace('/', '__')}__{commit_sha}.csv"
    return Path(output_dir) / name


def generate_for_row(row: dict[str, str], output_dir: Path) -> tuple[Path, list]:
    repository = Path(row["repository_path"])
    expected = row["commit_sha"]
    actual = _git_head(repository)
    if actual != expected:
        raise RuntimeError(
            f"{row['project']} HEAD is {actual}, but frozen manifest requires {expected}"
        )
    rows = classify_repository(repository, row["project"], expected)
    destination = manifest_path(output_dir, row["project"], expected)
    return write_file_manifest(rows, destination), rows


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Classify every YAML file in frozen study repositories."
    )
    parser.add_argument("frozen_manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)

    rows = load_collected(args.frozen_manifest)
    if args.limit is not None:
        rows = rows[: args.limit]
    for index, row in enumerate(rows, 1):
        print(f"[{index}/{len(rows)}] classifying {row['project']}")
        output, classified = generate_for_row(row, args.output_dir)
        included = sum(item["included"] == "true" for item in classified)
        print(f"  wrote {len(classified)} rows ({included} included) to {output}")


if __name__ == "__main__":
    main()

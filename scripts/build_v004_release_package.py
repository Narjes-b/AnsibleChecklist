#!/usr/bin/env python3
"""Build the compact, checksum-addressed v0.0.4 replication package."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()


def _portable_text(value):
    """Remove workstation-specific absolute prefixes from published evidence."""
    return value.replace(str(ROOT), "<repository-root>").replace(str(HOME), "<home>")


def _portable_bytes(value):
    text = value.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    trailing_newline = text.endswith("\n")
    text = "\n".join(line.rstrip() for line in text.splitlines())
    if trailing_newline:
        text += "\n"
    return _portable_text(text).encode("utf-8")


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy(source, target):
    if source.is_file():
        target.write_bytes(_portable_bytes(source.read_bytes()))
        return True
    return False


def _gzip_copy(source, target):
    if not source.is_file():
        return False
    with target.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as outgoing:
            outgoing.write(_portable_bytes(source.read_bytes()))
    return True


def _file_population(output):
    manifests = sorted((ROOT / "study/manifests/file-classification").glob("*.csv"))
    if not manifests:
        return False
    with output.open("wb") as raw:
        compressed = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
        stream = io.TextIOWrapper(compressed, encoding="utf-8", newline="")
        writer = None
        try:
            for manifest in manifests:
                with manifest.open(newline="", encoding="utf-8") as source:
                    reader = csv.DictReader(source)
                    if writer is None:
                        writer = csv.DictWriter(
                            stream,
                            fieldnames=["source_manifest", *(reader.fieldnames or ())],
                        )
                        writer.writeheader()
                    for row in reader:
                        writer.writerow(
                            {
                                "source_manifest": manifest.name,
                                **{key: _portable_text(value) for key, value in row.items()},
                            }
                        )
        finally:
            stream.close()
    return True


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=ROOT / "study/releases/v004"
    )
    args = parser.parse_args(argv)
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    sources = {
        "repository-manifest.csv": ROOT / "study/manifests/github-v2-final-frozen.csv",
        "calibration-report.md": ROOT / "study/validation-v6/VALIDATION_REPORT.md",
        "precision-summary.csv": ROOT / "study/validation-v6/results_report.csv",
        "synthetic-sensitivity-report.md": ROOT / "study/recall-v1/RECALL_STUDY.md",
        "injection-pr-report.md": ROOT / "study/pr-validation-v1/PR_VALIDATION_RESULTS.md",
        "injection-pr-labels.csv": ROOT / "study/pr-validation-v1/labels.csv",
    }
    status = {}
    for name, source in sources.items():
        status[name] = "included" if _copy(source, output / name) else "missing"
    sample = ROOT / "study/validation-v6/sample.csv"
    status["calibration-sample.csv.gz"] = (
        "included" if _gzip_copy(sample, output / "calibration-sample.csv.gz") else "missing"
    )
    status["file-population-manifest.csv.gz"] = (
        "included"
        if _file_population(output / "file-population-manifest.csv.gz")
        else "missing"
    )

    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        capture_output=True, check=False,
    ).stdout.strip() or None
    dirty = bool(
        subprocess.run(
            # Generated release files may be intentionally untracked while the
            # source commit is clean. Provenance is about source mutations.
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=ROOT, text=True,
            capture_output=True, check=False,
        ).stdout.strip()
    )
    provenance = {
        "schema_version": 1,
        "release": "v0.0.4-correctness-audit",
        "tool_commit": None if dirty else git_sha,
        "working_tree_base_commit": git_sha,
        "working_tree_dirty": dirty,
        "environment_files": {
            name: _sha256(ROOT / name)
            for name in ("requirements.txt", "Dockerfile.research", "collections.lock.yml")
            if (ROOT / name).is_file()
        },
        "evidence_status": status,
        "independent_human_labels": "not-yet-available",
        "natural_recall_reference": "not-yet-available",
        "natural_pr_validation": "not-yet-available",
        "archive_doi": None,
        "archive_sha256": None,
    }
    (output / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    artifacts = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name not in {"checksums.sha256", "artifact-manifest.json"}:
            artifacts.append(
                {"path": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)}
            )
    (output / "artifact-manifest.json").write_text(
        json.dumps({"schema_version": 1, "artifacts": artifacts}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    checksum_paths = [*sorted(output.iterdir())]
    with (output / "checksums.sha256").open("w", encoding="utf-8") as stream:
        for path in checksum_paths:
            if path.is_file() and path.name != "checksums.sha256":
                stream.write(f"{_sha256(path)}  {path.name}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

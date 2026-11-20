#!/usr/bin/env python3
"""Build and audit a stable, namespaced identity table for V007 validation.

This prepares the authoritative AnsibleGuard production-source population for
sampling. It does not select any sample or write reviewer labels.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
from collections import Counter, defaultdict
from typing import Iterable


EXPECTED_SOURCE_SHA256 = "7ea8943bf40a6b05f2e33c4140446757c45b6d218e81a75096591f046a81978b"
EXPECTED_SOURCE_ROWS = 265_434
EXPECTED_ANALYZABLE_REPOSITORIES = 206
IDENTITY_SCHEME = "v007-human-static-source-v1"

CANDIDATE_COLUMNS = [
    "occurrence_id",
    "source_occurrence_id",
    "identity_scheme",
    "run_id",
    "repository",
    "commit_sha",
    "provider",
    "canonical_rule_id",
    "concept_id",
    "resolution_status",
    "path",
    "line_start",
    "line_end",
    "span_kind",
    "object_kind",
    "object_id",
    "object_identity_basis",
    "semantic_subject",
    "semantic_key",
    "category",
    "severity",
    "certainty",
    "confidence",
    "actionability",
    "analysis_population",
    "source_population",
    "source_context_ref",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _id_hash(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def stable_occurrence_id(
    repository: str, commit_sha: str, provider: str, source_occurrence_id: str
) -> str:
    """Return a deterministic globally namespaced validation occurrence ID."""
    return _id_hash(
        IDENTITY_SCHEME, repository, commit_sha, provider, source_occurrence_id
    )


def stable_object_identity(
    repository: str,
    commit_sha: str,
    path: str,
    line: int,
    semantic_subject: str,
) -> tuple[str, str, str]:
    """Derive a reproducible object locator without claiming absent AST data.

    Semantic subjects with an explicit ``kind:value`` namespace keep that kind.
    The detector's untyped ``location`` subject is represented honestly as a
    source-location anchor. Its object ID is tied to the frozen path and line.
    """
    subject = semantic_subject.strip()
    if ":" in subject:
        object_kind, object_value = subject.split(":", 1)
        basis = "semantic_subject"
    elif subject == "location":
        object_kind, object_value = "source_location", f"{path}|{line}"
        basis = "reported_path_line"
    elif subject:
        object_kind, object_value = "semantic_subject_untyped", subject
        basis = "semantic_subject"
    else:
        object_kind, object_value = "source_location", f"{path}|{line}"
        basis = "reported_path_line"
    object_id = _id_hash(
        "v007-human-object-v1", repository, commit_sha, path, object_kind, object_value
    )
    return object_kind, object_id, basis


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _occurrence_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (
        row.get("occurrence_id", ""),
        row.get("semantic_key", ""),
        row.get("file", ""),
        str(row.get("line", "")),
        row.get("concept_id", ""),
    )


def _snapshot_items(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    raise ValueError(f"unsupported canonical occurrence snapshot: {path}")


def _line_count_from_batch(stdout, byte_size: int) -> int:
    remaining = byte_size
    newline_count = 0
    last_byte = b""
    while remaining:
        chunk = stdout.read(min(64 * 1024, remaining))
        if not chunk:
            raise RuntimeError("truncated `git cat-file --batch` object")
        newline_count += chunk.count(b"\n")
        last_byte = chunk[-1:]
        remaining -= len(chunk)
    if byte_size and last_byte != b"\n":
        newline_count += 1
    if stdout.read(1) != b"\n":
        raise RuntimeError("malformed `git cat-file --batch` record separator")
    return newline_count


def verify_frozen_blobs(
    repository_path: Path,
    commit_sha: str,
    path_lines: dict[str, set[int]],
) -> tuple[int, list[str], list[dict[str, int]]]:
    """Check source paths and referenced lines using commit objects, not worktrees."""
    paths = sorted(path_lines)
    if any("\n" in path or "\r" in path for path in paths):
        raise ValueError("source path contains a newline and cannot be batched safely")
    process = subprocess.Popen(
        ["git", "-C", str(repository_path), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    missing: list[str] = []
    out_of_bounds: list[dict[str, int]] = []
    verified = 0
    assert process.stdin is not None and process.stdout is not None
    for start in range(0, len(paths), 128):
        batch = paths[start : start + 128]
        refs = "".join(f"{commit_sha}:{path}\n" for path in batch)
        process.stdin.write(refs.encode("utf-8"))
        process.stdin.flush()
        for path in batch:
            header = process.stdout.readline().decode("utf-8", errors="replace").rstrip("\n")
            fields = header.split()
            if len(fields) == 2 and fields[1] == "missing":
                missing.append(path)
                continue
            if len(fields) != 3 or not fields[2].isdigit():
                process.kill()
                raise RuntimeError(f"unexpected git object response for {path!r}: {header!r}")
            _object_id, object_type, size_text = fields
            if object_type != "blob":
                process.kill()
                raise RuntimeError(f"source path is not a blob: {path!r} ({object_type})")
            line_count = _line_count_from_batch(process.stdout, int(size_text))
            verified += 1
            out_of_bounds.extend(
                {"line": line, "line_count": line_count}
                for line in sorted(path_lines[path])
                if line < 1 or line > line_count
            )
    process.stdin.close()
    stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
    return_code = process.wait()
    if return_code:
        raise RuntimeError(f"git cat-file failed ({return_code}): {stderr[:1000]}")
    return verified, missing, out_of_bounds


def _write_gzip_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="") as text:
                writer = csv.DictWriter(text, fieldnames=CANDIDATE_COLUMNS, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
    os.replace(temporary, path)


def build_source_identity_table(root: Path, output_dir: Path) -> dict:
    run_dir = root / "study/runs/v007-full-repro-2026"
    source_path = run_dir / "aggregate/all-internal-source-occurrences.csv"
    source_digest = sha256_file(source_path)
    if source_digest != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            f"unexpected authoritative source SHA-256: {source_digest}; stop for investigation"
        )

    statuses = {
        row["repository"]: row
        for row in _read_csv(run_dir / "tables/repository-execution-status.csv")
    }
    analyzable = {
        repository
        for repository, row in statuses.items()
        if row.get("ansibleguard_status") == "completed"
    }
    if len(statuses) != 207 or len(analyzable) != EXPECTED_ANALYZABLE_REPOSITORIES:
        raise RuntimeError(
            f"unexpected run population: repositories={len(statuses)}, analyzable={len(analyzable)}"
        )

    acquisition = {
        row["project"]: row
        for row in _read_csv(run_dir / "status/acquisition.csv")
    }
    snapshot_index = {
        row["repository"]: run_dir / row["canonical_occurrences"]
        for row in _read_csv(run_dir / "raw/raw-output-index.csv")
    }
    source_by_repository: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_occurrence_counts: Counter[str] = Counter()
    rule_ids: set[str] = set()
    path_lines: dict[str, dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))
    row_count = 0
    with source_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            row_count += 1
            if row.get("provider") != "ansibleguard" or row.get("source_population") != "production_ansible":
                raise RuntimeError("authoritative source contains a non-AnsibleGuard/non-production row")
            repository = row.get("project", "")
            if repository not in analyzable:
                raise RuntimeError(f"source row is not from an analyzable repository: {repository}")
            path = row.get("file", "")
            source_line = int(row.get("line") or 0)
            pure_path = PurePosixPath(path)
            if not path or pure_path.is_absolute() or ".." in pure_path.parts or source_line < 1:
                raise RuntimeError(f"invalid source locator: {repository}:{path}:{source_line}")
            source_by_repository[repository].append(row)
            source_occurrence_counts[row.get("occurrence_id", "")] += 1
            rule_ids.add(row.get("rule_id", ""))
            path_lines[repository][path].add(source_line)
    if row_count != EXPECTED_SOURCE_ROWS:
        raise RuntimeError(f"expected {EXPECTED_SOURCE_ROWS} source rows, found {row_count}")

    source_project_set = set(source_by_repository)
    if not source_project_set <= analyzable:
        raise RuntimeError("source population includes a repository outside the core population")
    if len(rule_ids) != 60:
        raise RuntimeError(f"expected 60 AnsibleGuard source rules, found {len(rule_ids)}")

    total_paths = 0
    verified_paths = 0
    missing_paths: list[dict[str, str]] = []
    out_of_bounds: list[dict[str, str | int]] = []
    for repository in sorted(path_lines):
        acquired = acquisition.get(repository, {})
        if acquired.get("status") != "complete":
            raise RuntimeError(f"frozen checkout unavailable for source repository: {repository}")
        commit_sha = acquired.get("commit_sha", "")
        source_commit = source_by_repository[repository][0].get("commit_sha", "")
        if commit_sha != source_commit:
            raise RuntimeError(f"checkout/source commit mismatch for {repository}")
        repo_path = Path(acquired["repository_path"])
        verified, missing, invalid = verify_frozen_blobs(
            repo_path, commit_sha, path_lines[repository]
        )
        total_paths += len(path_lines[repository])
        verified_paths += verified
        missing_paths.extend({"repository": repository, "path": path} for path in missing)
        out_of_bounds.extend(
            {"repository": repository, **item} for item in invalid
        )
    if missing_paths or out_of_bounds or verified_paths != total_paths:
        raise RuntimeError(
            f"frozen context audit failed: verified={verified_paths}/{total_paths}, "
            f"missing={len(missing_paths)}, out_of_bounds={len(out_of_bounds)}"
        )

    output_rows: list[dict[str, str]] = []
    validation_ids: set[str] = set()
    snapshot_matches = 0
    for repository in sorted(source_by_repository):
        source_rows = source_by_repository[repository]
        acquisition_row = acquisition[repository]
        if acquisition_row.get("commit_sha") != source_rows[0].get("commit_sha"):
            raise RuntimeError(f"source rows disagree on frozen commit for {repository}")
        index_path = snapshot_index.get(repository)
        if not index_path or not index_path.is_file():
            raise RuntimeError(f"canonical snapshot missing for {repository}")
        wanted: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
        for row in source_rows:
            key = _occurrence_key(row)
            if key in wanted:
                raise RuntimeError(f"duplicate source identity tuple within {repository}: {key}")
            wanted[key] = row
        matched: dict[tuple[str, str, str, str, str], dict] = {}
        for item in _snapshot_items(index_path):
            if item.get("canonical_provider") != "ansibleguard":
                continue
            if item.get("source_population") != "production_ansible":
                continue
            key = _occurrence_key({
                "occurrence_id": str(item.get("occurrence_id", "")),
                "semantic_key": str(item.get("semantic_key", "")),
                "file": str(item.get("file", "")),
                "line": str(item.get("line", "")),
                "concept_id": str(item.get("concept_id", "")),
            })
            if key in wanted:
                if key in matched:
                    raise RuntimeError(f"ambiguous snapshot match in {repository}: {key}")
                matched[key] = item
        if len(matched) != len(wanted):
            raise RuntimeError(
                f"snapshot/source mismatch in {repository}: matched={len(matched)}, expected={len(wanted)}"
            )
        snapshot_matches += len(matched)
        for key, row in wanted.items():
            item = matched[key]
            source_id = row.get("occurrence_id", "")
            commit_sha = row.get("commit_sha", "")
            provider = row.get("provider", "")
            candidate_id = stable_occurrence_id(repository, commit_sha, provider, source_id)
            if candidate_id in validation_ids:
                raise RuntimeError(f"namespaced validation occurrence ID collision: {candidate_id}")
            validation_ids.add(candidate_id)
            source_line = int(row["line"])
            semantic_subject = str(item.get("semantic_subject") or "")
            object_kind, object_id, object_basis = stable_object_identity(
                repository, commit_sha, row["file"], source_line, semantic_subject
            )
            output_rows.append({
                "occurrence_id": candidate_id,
                "source_occurrence_id": source_id,
                "identity_scheme": IDENTITY_SCHEME,
                "run_id": row.get("run_id", ""),
                "repository": repository,
                "commit_sha": commit_sha,
                "provider": provider,
                "canonical_rule_id": row.get("rule_id", ""),
                "concept_id": row.get("concept_id", ""),
                "resolution_status": row.get("resolution_status", ""),
                "path": row.get("file", ""),
                "line_start": str(source_line),
                "line_end": str(source_line),
                "span_kind": "reported_anchor_line",
                "object_kind": object_kind,
                "object_id": object_id,
                "object_identity_basis": object_basis,
                "semantic_subject": semantic_subject,
                "semantic_key": row.get("semantic_key", ""),
                "category": row.get("category", ""),
                "severity": row.get("severity", ""),
                "certainty": row.get("certainty", ""),
                "confidence": row.get("confidence", ""),
                "actionability": row.get("actionability", ""),
                "analysis_population": row.get("analysis_population", ""),
                "source_population": row.get("source_population", ""),
                "source_context_ref": f"{repository}@{commit_sha}:{row.get('file')}#{source_line}",
            })

    if len(output_rows) != row_count or len(validation_ids) != row_count:
        raise RuntimeError("candidate identity output does not reconcile to authoritative source")

    output_dir.mkdir(parents=True, exist_ok=True)
    identity_path = output_dir / "static-source-candidates.csv.gz"
    _write_gzip_csv(identity_path, output_rows)
    raw_id_groups = sum(count > 1 for count in source_occurrence_counts.values())
    raw_id_excess = sum(count - 1 for count in source_occurrence_counts.values())
    manifest = {
        "schema_version": 1,
        "identity_scheme": IDENTITY_SCHEME,
        "source_run": "v007-full-repro-2026",
        "source_file": str(source_path.relative_to(root)),
        "source_sha256": source_digest,
        "source_rows": row_count,
        "source_rules": len(rule_ids),
        "analyzable_repositories": len(analyzable),
        "repositories_with_source_occurrences": len(source_project_set),
        "analyzable_repositories_with_zero_source_occurrences": len(analyzable - source_project_set),
        "original_occurrence_id_duplicate_groups": raw_id_groups,
        "original_occurrence_id_excess_rows": raw_id_excess,
        "namespaced_validation_occurrence_ids": len(validation_ids),
        "snapshot_occurrence_matches": snapshot_matches,
        "frozen_git_blob_paths_checked": total_paths,
        "frozen_git_blob_paths_verified": verified_paths,
        "missing_frozen_paths": len(missing_paths),
        "out_of_bounds_source_lines": len(out_of_bounds),
        "line_end_policy": "line_end equals detector-reported anchor line; it is not asserted as a syntactic object span",
        "object_identity_policy": {
            "kind-prefixed semantic_subject": "object_kind is the prefix; object_id hashes repository, commit, path, kind, and subject value",
            "untyped location subject": "object_kind=source_location; object_id hashes repository, commit, path, and reported line",
        },
        "candidate_file": identity_path.name,
        "candidate_file_sha256": sha256_file(identity_path),
        "sampling_performed": False,
        "human_labels_created": False,
    }
    manifest_path = output_dir / "static-source-candidates.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("study/validation-v007-human/identities"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    manifest = build_source_identity_table(root, output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Create separate, blinded ZIP handoffs for the V0.0.7 agreement-pilot reviewers."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable

import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_validation_pilot import (
    FAMILY_CODEBOOKS,
    PILOT_CODEBOOK_INPUTS,
    REVIEWER_COLUMNS,
    REVIEWER_DECISION_COLUMNS,
    REVIEWER_VISIBLE_COLUMNS,
)


SHARED_FILES = (
    "codebooks/REVIEWER_INSTRUCTIONS.md",
    "codebooks/RULE_OVERRIDES.md",
    *sorted(set(FAMILY_CODEBOOKS.values())),
)
REVIEWER_INSTRUCTIONS = {
    "a": "reviewers/HUMAN_REVIEWER_A_INSTRUCTIONS.md",
    "b": "reviewers/HUMAN_REVIEWER_B_INSTRUCTIONS.md",
}
REVIEWER_LABELS = {"a": "Reviewer A", "b": "Reviewer B"}
CSV_RELATIVE_PATHS = {
    "a": "reviewers/reviewer-a/agreement-pilot.csv",
    "b": "reviewers/reviewer-b/agreement-pilot.csv",
}


class PacketError(ValueError):
    """A frozen reviewer input is unsuitable for a blinded packet."""


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            header = list(reader.fieldnames or [])
            if len(header) != len(set(header)):
                raise PacketError(f"duplicate CSV columns in {path}")
            rows = []
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise PacketError(f"extra CSV cells in {path} at line {line_number}")
                rows.append({key: value or "" for key, value in row.items() if key is not None})
            return header, rows
    except (OSError, UnicodeError, csv.Error) as error:
        raise PacketError(f"cannot read {path}: {error}") from error


def _safe_relative(value: str, *, field: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise PacketError(f"unsafe {field}: {value!r}")
    return path


def _validate_blank_template(validation_dir: Path, reviewer: str) -> list[tuple[str, bytes]]:
    assigned_csv = CSV_RELATIVE_PATHS[reviewer]
    template_path = validation_dir / assigned_csv
    header, rows = _read_csv(template_path)
    if header != REVIEWER_COLUMNS:
        raise PacketError(f"{REVIEWER_LABELS[reviewer]} template columns differ from the frozen schema")
    if not rows:
        raise PacketError(f"{REVIEWER_LABELS[reviewer]} template is empty")
    sample_ids = [row.get("sample_id", "") for row in rows]
    if any(not sample_id for sample_id in sample_ids) or len(sample_ids) != len(set(sample_ids)):
        raise PacketError(f"{REVIEWER_LABELS[reviewer]} template has missing or duplicate sample IDs")
    if any(row.get(column, "").strip() for row in rows for column in REVIEWER_DECISION_COLUMNS):
        raise PacketError(f"{REVIEWER_LABELS[reviewer]} template is not blank")

    master_path = validation_dir / "samples/agreement-pilot/agreement-pilot-master.csv"
    master_header, master_rows = _read_csv(master_path)
    if len(rows) != len(master_rows) or not master_rows:
        raise PacketError("reviewer template row count differs from the frozen master")
    master_ids = [row.get("sample_id", "") for row in master_rows]
    if sample_ids != master_ids:
        raise PacketError("reviewer template IDs/order differ from the frozen master")
    if any(row.get("eligible_for_performance_scoring") != "false" for row in master_rows):
        raise PacketError("pilot master contains rows eligible for performance scoring")
    if not set(REVIEWER_VISIBLE_COLUMNS).issubset(master_header):
        raise PacketError("pilot master is missing visible reviewer evidence columns")

    file_paths = [assigned_csv, REVIEWER_INSTRUCTIONS[reviewer], *SHARED_FILES]
    context_paths: list[str] = []
    for row in rows:
        for column in REVIEWER_VISIBLE_COLUMNS:
            if not row.get(column, "").strip():
                raise PacketError(f"missing reviewer evidence field {column} for {row['sample_id']}")
        context_rel = _safe_relative(row["context_bundle_path"], field="context bundle path").as_posix()
        codebook_rel = _safe_relative(row["codebook_path"], field="codebook path").as_posix()
        if codebook_rel not in FAMILY_CODEBOOKS.values():
            raise PacketError(f"unknown family codebook path: {codebook_rel}")
        context_paths.append(context_rel)
        master = master_rows[len(context_paths) - 1]
        for column in REVIEWER_VISIBLE_COLUMNS:
            if row.get(column, "") != master.get(column, ""):
                raise PacketError(f"reviewer evidence differs from master at {row['sample_id']} ({column})")
    if len(context_paths) != len(set(context_paths)):
        raise PacketError("multiple pilot items point to the same context bundle")
    file_paths.extend(context_paths)

    unique_paths = sorted(set(file_paths))
    payloads: list[tuple[str, bytes]] = []
    for relative in unique_paths:
        safe_path = _safe_relative(relative, field="packet input path")
        source = validation_dir.joinpath(*safe_path.parts)
        try:
            content = source.read_bytes()
        except OSError as error:
            raise PacketError(f"missing packet input {relative}: {error}") from error
        if not content:
            raise PacketError(f"empty packet input: {relative}")
        payloads.append((relative, content))

    manifest_path = validation_dir / "samples/agreement-pilot/agreement-pilot-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PacketError(f"cannot read frozen pilot manifest: {error}") from error
    if manifest.get("human_labels_created") is not False:
        raise PacketError("pilot manifest does not describe a blank human-review package")
    input_hashes = manifest.get("inputs", {}).get("pilot_codebooks_sha256", {})
    if set(input_hashes) != set(PILOT_CODEBOOK_INPUTS):
        raise PacketError("pilot manifest codebook/instruction inventory differs from the frozen schema")
    for relative, expected_hash in input_hashes.items():
        path = validation_dir / relative
        try:
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:
            raise PacketError(f"missing frozen codebook/instruction {relative}: {error}") from error
        if actual_hash != expected_hash:
            raise PacketError(f"frozen codebook/instruction changed since pilot creation: {relative}")

    output_hashes = manifest.get("files", {})
    hashes_to_check = {
        assigned_csv,
        "reviewers/reviewer-a/agreement-pilot.csv",
        "reviewers/reviewer-b/agreement-pilot.csv",
        "samples/agreement-pilot/agreement-pilot-master.csv",
        *context_paths,
    }
    payload_map = dict(payloads)
    for relative in hashes_to_check:
        record = output_hashes.get(relative, {})
        expected_hash = record.get("sha256")
        if not expected_hash:
            raise PacketError(f"pilot manifest is missing the frozen checksum for {relative}")
        if relative in payload_map:
            actual_hash = hashlib.sha256(payload_map[relative]).hexdigest()
        else:
            try:
                actual_hash = hashlib.sha256((validation_dir / relative).read_bytes()).hexdigest()
            except OSError as error:
                raise PacketError(f"missing frozen pilot output {relative}: {error}") from error
        if actual_hash != expected_hash:
            raise PacketError(f"pilot output differs from manifest checksum: {relative}")

    reviewer_hashes = {
        hashlib.sha256((validation_dir / CSV_RELATIVE_PATHS[key]).read_bytes()).hexdigest()
        for key in ("a", "b")
    }
    if len(reviewer_hashes) != 1 or manifest.get("reviewer_forms_identical_sha256") not in reviewer_hashes:
        raise PacketError("the two blank reviewer forms are no longer byte-identical")
    return payloads


def _readme(reviewer: str) -> bytes:
    label = REVIEWER_LABELS[reviewer]
    content = f"""# V0.0.7 agreement-pilot handoff — {label}

This packet is for **{label} only**. Keep your judgments independent; do not view or discuss another reviewer's answers or any AI output. Do not use web search, a current repository checkout, or fresh tool runs. Judge only the frozen evidence in this packet.

Start with `{REVIEWER_INSTRUCTIONS[reviewer]}` and `codebooks/REVIEWER_INSTRUCTIONS.md`. For each row, read the family codebook named in `codebook_path`, any applicable entry in `codebooks/RULE_OVERRIDES.md`, and the frozen context file named in `context_bundle_path` (relative to this packet's root).

Fill only these eight blank columns in `{CSV_RELATIVE_PATHS[reviewer]}`: `semantic_label`, `actionability_label`, `context_sufficient`, `requires_external_context`, `external_context_type`, `reason_code`, `evidence_notes`, and `reviewer_notes`. Preserve every other value, all rows, and row order. Save a completed copy separately; leave this blank template unchanged. Never put secrets in notes.

Return only your completed CSV to the study coordinator. This is an agreement/codebook pilot; pilot items are not used for performance scoring.
"""
    return content.encode("utf-8")


def _zip_bytes(payloads: Iterable[tuple[str, bytes]], reviewer: str) -> bytes:
    entries = dict(payloads)
    entries["README_FIRST.md"] = _readme(reviewer)
    checksums = "".join(
        f"{hashlib.sha256(content).hexdigest()}  {relative}\n"
        for relative, content in sorted(entries.items())
    )
    entries["SHA256SUMS.txt"] = checksums.encode("utf-8")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative, content in sorted(entries.items()):
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return buffer.getvalue()


def export_packets(validation_dir: Path, output_dir: Path, reviewers: Iterable[str] = ("a", "b")) -> dict[str, Path]:
    """Create immutable per-reviewer archives and matching SHA-256 sidecars."""
    results: dict[str, Path] = {}
    for reviewer in reviewers:
        if reviewer not in REVIEWER_LABELS:
            raise PacketError(f"unknown reviewer {reviewer!r}; use 'a' or 'b'")
        payloads = _validate_blank_template(validation_dir, reviewer)
        archive_bytes = _zip_bytes(payloads, reviewer)
        archive_sha = hashlib.sha256(archive_bytes).hexdigest()
        reviewer_dir = output_dir / f"reviewer-{reviewer}"
        reviewer_dir.mkdir(parents=True, exist_ok=True)
        archive_path = reviewer_dir / f"V007_AGREEMENT_PILOT_REVIEWER_{reviewer.upper()}_{archive_sha[:12]}.zip"
        sidecar_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
        sidecar = f"{archive_sha}  {archive_path.name}\n".encode("ascii")
        for path, content in ((archive_path, archive_bytes), (sidecar_path, sidecar)):
            if path.exists():
                if path.read_bytes() != content:
                    raise PacketError(f"refusing to overwrite an existing packet artifact: {path}")
            else:
                with path.open("xb") as stream:
                    stream.write(content)
        results[reviewer] = archive_path
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-dir", type=Path, default=Path("study/validation-v007-human"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--reviewer", choices=("a", "b", "both"), default="both")
    args = parser.parse_args()
    reviewers = ("a", "b") if args.reviewer == "both" else (args.reviewer,)
    results = export_packets(args.validation_dir.resolve(), args.output_dir.resolve(), reviewers)
    for reviewer, archive_path in results.items():
        print(f"{REVIEWER_LABELS[reviewer]}: {archive_path}")
        print(f"  SHA-256: {hashlib.sha256(archive_path.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

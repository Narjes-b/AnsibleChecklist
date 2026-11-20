import csv
import hashlib
import io
import json
import zipfile

import pytest

from scripts.export_v007_reviewer_packets import PacketError, export_packets
from scripts.v007_validation_pilot import (
    AI_SHADOW_COLUMNS,
    FAMILY_CODEBOOKS,
    MASTER_COLUMNS,
    PILOT_CODEBOOK_INPUTS,
    REVIEWER_COLUMNS,
    REVIEWER_DECISION_COLUMNS,
    REVIEWER_VISIBLE_COLUMNS,
)


def _write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _make_validation_package(validation_dir):
    for relative in (
        "codebooks/REVIEWER_INSTRUCTIONS.md",
        "codebooks/RULE_OVERRIDES.md",
        *FAMILY_CODEBOOKS.values(),
        "samples/agreement-pilot/PILOT_PROTOCOL.md",
        "reviewers/HUMAN_REVIEWER_A_INSTRUCTIONS.md",
        "reviewers/HUMAN_REVIEWER_B_INSTRUCTIONS.md",
    ):
        path = validation_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Instructions for {relative}\n", encoding="utf-8")

    master_rows = []
    reviewer_rows = []
    ai_rows = []
    for index, family in enumerate(FAMILY_CODEBOOKS, start=1):
        if index > 2:
            break
        sample_id = f"V007PILOT-TEST-{index:03d}"
        context_path = f"samples/agreement-pilot/context/{sample_id}.md"
        context_file = validation_dir / context_path
        context_file.parent.mkdir(parents=True, exist_ok=True)
        context_file.write_text(f"Frozen context for {sample_id}\n", encoding="utf-8")
        visible = {
            "sample_id": sample_id,
            "occurrence_id": f"occurrence-{index}",
            "panel": "static-source",
            "rule_id": f"ansibleguard/rule-{index}",
            "concept_id": f"concept-{index}",
            "review_family": f"Family {index}",
            "codebook_path": FAMILY_CODEBOOKS[family],
            "review_question": f"Question {index}?",
            "repository": f"org/repo-{index}",
            "commit_sha": f"{index:040d}",
            "path": f"tasks/{index}.yml",
            "line_start": str(index),
            "line_end": str(index),
            "object_kind": "source_location",
            "object_id": f"object-{index}",
            "source_context": f"line {index}: example",
            "context_bundle_path": context_path,
        }
        reviewer_rows.append({**visible, **{column: "" for column in REVIEWER_DECISION_COLUMNS}})
        master_rows.append(
            {
                **visible,
                "source_occurrence_id": f"source-{index}",
                "selection_rank_sha256": f"rank-{index}",
                "is_agreement_pilot": "true",
                "eligible_for_performance_scoring": "false",
                **{column: "" for column in REVIEWER_DECISION_COLUMNS},
            }
        )
        ai_rows.append({**visible, **{column: "" for column in AI_SHADOW_COLUMNS[len(REVIEWER_VISIBLE_COLUMNS):]}})

    _write_csv(
        validation_dir / "samples/agreement-pilot/agreement-pilot-master.csv",
        MASTER_COLUMNS,
        master_rows,
    )
    for reviewer in ("a", "b"):
        _write_csv(
            validation_dir / f"reviewers/reviewer-{reviewer}/agreement-pilot.csv",
            REVIEWER_COLUMNS,
            reviewer_rows,
        )
    _write_csv(
        validation_dir / "reviewers/ai-shadow/agreement-pilot.csv",
        AI_SHADOW_COLUMNS,
        ai_rows,
    )
    manifest_files = (
        "reviewers/reviewer-a/agreement-pilot.csv",
        "reviewers/reviewer-b/agreement-pilot.csv",
        "samples/agreement-pilot/agreement-pilot-master.csv",
        "samples/agreement-pilot/context/V007PILOT-TEST-001.md",
        "samples/agreement-pilot/context/V007PILOT-TEST-002.md",
    )
    manifest = {
        "human_labels_created": False,
        "ai_labels_created": False,
        "reviewer_forms_identical_sha256": hashlib.sha256(
            (validation_dir / "reviewers/reviewer-a/agreement-pilot.csv").read_bytes()
        ).hexdigest(),
        "inputs": {
            "pilot_codebooks_sha256": {
                relative: hashlib.sha256((validation_dir / relative).read_bytes()).hexdigest()
                for relative in PILOT_CODEBOOK_INPUTS
            }
        },
        "files": {
            relative: {
                "sha256": hashlib.sha256((validation_dir / relative).read_bytes()).hexdigest()
            }
            for relative in manifest_files
        },
    }
    manifest_path = validation_dir / "samples/agreement-pilot/agreement-pilot-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_export_packets_are_reproducible_and_each_contains_only_its_assigned_form(tmp_path):
    validation_dir = tmp_path / "validation"
    _make_validation_package(validation_dir)

    first = export_packets(validation_dir, tmp_path / "packets-one")
    second = export_packets(validation_dir, tmp_path / "packets-two")

    for reviewer, archive_path in first.items():
        archive_bytes = archive_path.read_bytes()
        assert archive_bytes == second[reviewer].read_bytes()
        assert archive_path.with_suffix(".zip.sha256").read_text().startswith(
            hashlib.sha256(archive_bytes).hexdigest()
        )
        with zipfile.ZipFile(archive_path) as archive:
            assert archive.testzip() is None
            names = set(archive.namelist())
            assert f"reviewers/reviewer-{reviewer}/agreement-pilot.csv" in names
            other = "b" if reviewer == "a" else "a"
            assert f"reviewers/reviewer-{other}/agreement-pilot.csv" not in names
            assert "reviewers/ai-shadow/agreement-pilot.csv" not in names
            assert "samples/agreement-pilot/agreement-pilot-master.csv" not in names
            assert "samples/agreement-pilot/agreement-pilot-manifest.json" not in names
            assert "README_FIRST.md" in names
            assert "SHA256SUMS.txt" in names
            assert "samples/agreement-pilot/context/V007PILOT-TEST-001.md" in names
            assert "codebooks/RULE_OVERRIDES.md" in names
            form = next(name for name in names if name.endswith("agreement-pilot.csv"))
            with archive.open(form, "r") as stream:
                rows = list(csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8", newline="")))
            assert len(rows) == 2
            assert list(rows[0]) == REVIEWER_COLUMNS
            assert not any(row[column] for row in rows for column in REVIEWER_DECISION_COLUMNS)


def test_export_refuses_nonblank_reviewer_template(tmp_path):
    validation_dir = tmp_path / "validation"
    _make_validation_package(validation_dir)
    reviewer_path = validation_dir / "reviewers/reviewer-a/agreement-pilot.csv"
    with reviewer_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows[0]["semantic_label"] = "positive"
    _write_csv(reviewer_path, REVIEWER_COLUMNS, rows)

    with pytest.raises(PacketError, match="not blank"):
        export_packets(validation_dir, tmp_path / "packets", ("a",))


def test_export_refuses_evidence_changed_from_master(tmp_path):
    validation_dir = tmp_path / "validation"
    _make_validation_package(validation_dir)
    reviewer_path = validation_dir / "reviewers/reviewer-a/agreement-pilot.csv"
    with reviewer_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    rows[0]["source_context"] = "altered evidence"
    _write_csv(reviewer_path, REVIEWER_COLUMNS, rows)

    with pytest.raises(PacketError, match="differs from master"):
        export_packets(validation_dir, tmp_path / "packets", ("a",))


def test_export_refuses_codebook_changes_since_the_pilot_was_frozen(tmp_path):
    validation_dir = tmp_path / "validation"
    _make_validation_package(validation_dir)
    codebook_path = validation_dir / "codebooks/FAMILY_SECURITY.md"
    codebook_path.write_text("changed after pilot freeze\n", encoding="utf-8")

    with pytest.raises(PacketError, match="changed since pilot creation"):
        export_packets(validation_dir, tmp_path / "packets", ("a",))


def test_export_refuses_context_changes_since_the_pilot_was_frozen(tmp_path):
    validation_dir = tmp_path / "validation"
    _make_validation_package(validation_dir)
    context_path = validation_dir / "samples/agreement-pilot/context/V007PILOT-TEST-001.md"
    context_path.write_text("changed after pilot freeze\n", encoding="utf-8")

    with pytest.raises(PacketError, match="differs from manifest checksum"):
        export_packets(validation_dir, tmp_path / "packets", ("a",))

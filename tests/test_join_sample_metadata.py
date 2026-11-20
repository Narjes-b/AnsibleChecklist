import copy
import hashlib
import io
import json
import tarfile

import pytest

from scripts import join_sample_metadata as join


def row(repository="owner/one", occurrence="shared-id"):
    return {"sample_id": "PROB-" + hashlib.sha256(repository.encode()).hexdigest(),
            "run_id": "run", "repository": repository, "commit_sha": "a" * 40,
            "occurrence_id": occurrence, "file": "tasks.yml", "line": "2",
            "rule_id": "ansibleguard/example", "policy": "required", "certainty": "CONFIRMED",
            "resolution_status": "DETECTOR_RESULT", "resolution_scope": "rule-static",
            "sampling_weight": "13.7", "label_status": "not-started"}


def item(selected=None):
    r = selected or row()
    return {"occurrence_id": r["occurrence_id"], "file": r["file"], "line": int(r["line"]),
            "canonical_provider": "ansibleguard", "native_rules": [r["rule_id"]],
            "policy": r["policy"], "semantic_status": r["certainty"],
            "resolution_status": r["resolution_status"], "resolution_scope": r["resolution_scope"],
            "semantic_subject": "variable:CaseSensitive|task:name", "message": "unverified detector claim"}


def archive(tmp_path, members):
    path = tmp_path / "frozen.tar.gz"
    with tarfile.open(path, "w:gz") as target:
        for name, value, kind in members:
            data = json.dumps(value).encode()
            info = tarfile.TarInfo(name)
            info.size = len(data) if kind == tarfile.REGTYPE else 0
            info.type = kind
            target.addfile(info, io.BytesIO(data) if info.size else None)
    return path


def test_same_occurrence_id_never_crosses_repository_boundary(tmp_path):
    a, b = row(), row("owner/two")
    ia, ib = item(a), item(b)
    ib["semantic_subject"] = "location"
    path = archive(tmp_path, [(join.member_name(a), {"items": [ia]}, tarfile.REGTYPE),
                              (join.member_name(b), {"items": [ib]}, tarfile.REGTYPE)])
    records, statuses, hashes = join.read_selected(path, [a, b])
    results = join.join_rows([a, b], records, statuses, hashes, tmp_path / "packets")
    assert [r["semantic_subject_kind"] for r in results] == ["variable", "location"]
    assert all(r["metadata_status"] == "metadata-joined" for r in results)
    assert all(r["sampling_weight"] == "13.7" and r["label_status"] == "not-started" for r in results)
    assert all(not r["subject_verified"] and not r["evidence_complete"] for r in results)
    assert results[0]["canonical_item_sha256"] != results[1]["canonical_item_sha256"]


@pytest.mark.parametrize("field,value,status", [
    ("line", 3, "source-identity-mismatch"), ("line", True, "source-identity-mismatch"),
    ("file", "other.yml", "source-identity-mismatch"),
    ("native_rules", ["ansibleguard/other"], "rule-identity-mismatch"),
    ("canonical_provider", "ansible-lint", "rule-identity-mismatch"),
    ("policy", "optional", "decision-cell-mismatch"),
    ("semantic_status", "UNCERTAIN", "decision-cell-mismatch"),
    ("resolution_scope", "cross-file", "decision-cell-mismatch"),
])
def test_identity_and_decision_cells_must_match(field, value, status):
    changed = item()
    changed[field] = value
    assert join.check_item(row(), changed) == status


def test_absent_ambiguous_and_missing_members_keep_selected_rows(tmp_path):
    a, b, c = row(), row("owner/two"), row("owner/three")
    path = archive(tmp_path, [(join.member_name(a), {"items": []}, tarfile.REGTYPE),
                              (join.member_name(b), [item(b), item(b)], tarfile.REGTYPE)])
    records, statuses, hashes = join.read_selected(path, [a, b, c])
    results = join.join_rows([a, b, c], records, statuses, hashes, tmp_path / "packets")
    assert [r["metadata_status"] for r in results] == ["occurrence-absent", "occurrence-ambiguous", "member-absent"]
    assert len(results) == 3 and not list((tmp_path / "packets").iterdir())


def test_duplicate_members_are_rejected_even_when_identical(tmp_path):
    member = (join.member_name(row()), [item()], tarfile.REGTYPE)
    path = archive(tmp_path, [member, member])
    with pytest.raises(ValueError, match="duplicate selected archive member"):
        join.read_selected(path, [row()])


def test_traversal_accepts_the_same_open_file_used_for_checksum(tmp_path):
    path = archive(tmp_path, [(join.member_name(row()), [item()], tarfile.REGTYPE)])
    with path.open("rb") as source:
        assert join.digest_open_file(source) == join.sha256(path)
        source.seek(0)
        records, _, _ = join.read_selected(source, [row()])
    assert records[join.member_name(row()), row()["occurrence_id"]][0] == item()


@pytest.mark.parametrize("kind,limit", [(tarfile.SYMTYPE, 1000), (tarfile.REGTYPE, 1)])
def test_never_follow_member_links_or_read_oversize_members(tmp_path, kind, limit):
    path = archive(tmp_path, [(join.member_name(row()), [item()], kind)])
    records, statuses, hashes = join.read_selected(path, [row()], max_member_bytes=limit)
    assert not records and not hashes
    assert statuses[join.member_name(row())] == "invalid-or-oversize-member"


def test_secret_scan_failure_blocks_packet_without_dropping_id(tmp_path, monkeypatch):
    monkeypatch.setattr(join, "scan_text", lambda text: ["synthetic failure"])
    r = row()
    results = join.join_rows([r], {(join.member_name(r), r["occurrence_id"]): (item(), "")}, {}, {}, tmp_path / "packets")
    assert results[0]["metadata_status"] == "metadata-redaction-scan-failed"
    assert not results[0]["metadata_packet_sha256"] and not list((tmp_path / "packets").iterdir())


def test_metadata_redaction_is_local_and_does_not_change_raw_item_hash(tmp_path, monkeypatch):
    original = item()
    original["message"] = "PRIVATE_VALUE"
    before = copy.deepcopy(original)
    monkeypatch.setattr(join, "redact_sensitive_text_v2", lambda text: text.replace("PRIVATE_VALUE", "[REDACTED]"))
    r = row()
    results = join.join_rows([r], {(join.member_name(r), r["occurrence_id"]): (original, "")}, {}, {}, tmp_path / "packets")
    result = results[0]
    assert result["metadata_redacted"] and original == before
    assert result["canonical_item_sha256"] == hashlib.sha256(join.canonical_bytes(original)).hexdigest()
    packet = (tmp_path / "packets" / result["metadata_packet_file"]).read_text()
    assert "PRIVATE_VALUE" not in packet and "[REDACTED]" in packet
    assert "message" not in result and "semantic_subject" not in result


def test_redacting_one_metadata_field_preserves_separate_subject_and_other_context(tmp_path):
    r, original = row(), item()
    original["secret_context"] = "private literal"
    results = join.join_rows([r], {(join.member_name(r), r["occurrence_id"]): (original, "")}, {}, {}, tmp_path / "packets")
    packet = json.loads((tmp_path / "packets" / results[0]["metadata_packet_file"]).read_text())
    assert packet["redacted_semantic_subject"] == original["semantic_subject"]
    assert not packet["semantic_subject_redacted"]
    assert "unverified detector claim" in packet["redacted_canonical_text"]
    assert "private literal" not in packet["redacted_canonical_text"]


def test_checksum_mismatch_produces_no_outputs(tmp_path, monkeypatch):
    path = archive(tmp_path, [])
    monkeypatch.setattr(join, "load_draw", lambda path: ([], {}))
    monkeypatch.setattr(join, "previous_report", lambda *a: {})
    monkeypatch.setattr(join, "sha256", lambda *a: "fixture")
    with pytest.raises(ValueError, match="checksum mismatch"):
        join.main(["--archive", str(path), "--archive-sha256", "0" * 64,
                   "--draw-root", str(tmp_path), "--retrieval-root", str(tmp_path), "--draw", "required",
                   "--packet-root", str(tmp_path / "packets"), "--report-root", str(tmp_path / "reports")])
    assert not (tmp_path / "packets").exists() and not (tmp_path / "reports").exists()


def test_main_hashes_traverses_and_records_a_successful_join(tmp_path, monkeypatch):
    r = row()
    path = archive(tmp_path, [(join.member_name(r), {"items": [item()]}, tarfile.REGTYPE)])
    monkeypatch.setattr(join, "load_draw", lambda path: ([r], {}))
    monkeypatch.setattr(join, "previous_report", lambda *a: {r["sample_id"]: {
        "retrieval_status": "source-retrieved", "source_sha256": "frozen-source",
        "git_blob_oid": "frozen-blob", "packet_sha256": "base-packet"}})
    original_hash = join.sha256
    monkeypatch.setattr(join, "sha256", lambda p: original_hash(p) if p.exists() else "fixture")
    assert join.main(["--archive", str(path), "--archive-sha256", original_hash(path),
                      "--draw-root", str(tmp_path), "--retrieval-root", str(tmp_path), "--draw", "required",
                      "--packet-root", str(tmp_path / "packets"), "--report-root", str(tmp_path / "reports")]) == 0
    report = tmp_path / "reports/required"
    manifest = json.loads((report / "metadata-manifest.json").read_text())
    assert manifest["archive_checksum_verified"]
    assert manifest["output_sha256"]["metadata-ledger.csv"] == original_hash(report / "metadata-ledger.csv")
    assert manifest["selected_rows"] == manifest["recorded_rows"] == 1
    assert manifest["status_counts"] == {"metadata-joined": 1}
    assert not manifest["eligible_for_performance_scoring"] and manifest["subject_verified"] == 0

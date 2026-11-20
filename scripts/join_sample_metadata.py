#!/usr/bin/env python3
"""Join calibration selections to the checksum-verified frozen canonical archive.

Never extract archive paths. Reports contain identities, hashes and controlled
statuses; redacted detector text stays in the ignored local packet directory.
This join establishes provenance, not the correctness of a detector claim.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import tarfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.retrieve_sample_evidence import load_draw, previous_report, safe_relative
from scripts.sample_partitioned_occurrences import sha256, write_csv
from scripts.v007_bundle_context_v2 import redact_sensitive_text_v2
from scripts.v007_bundle_redact_v2 import redact_text as second_pass
from scripts.v007_bundle_secret_scan import scan_text


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def digest_open_file(source):
    """Hash from the current position on Python 3.10 and later."""
    digest = hashlib.sha256()
    while chunk := source.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def member_name(row):
    run = row["run_id"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run):
        raise ValueError("unsafe run identity")
    safe_relative(row["repository"], repository=True)
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", row["commit_sha"]):
        raise ValueError("invalid commit identity")
    return f'{run}/repositories/{row["repository"].replace("/", "__")}/{row["commit_sha"]}/canonical/occurrences.json'


def check_item(row, item):
    """Keep the full occurrence identity and decision cell fixed across the join."""
    if not isinstance(item, dict):
        return "invalid-occurrence"
    if (item.get("occurrence_id") != row["occurrence_id"] or item.get("file") != row["file"]
            or type(item.get("line")) is not int or str(item["line"]) != row["line"]):
        return "source-identity-mismatch"
    rules = item.get("native_rules")
    if (item.get("canonical_provider") != "ansibleguard" or not isinstance(rules, list)
            or row["rule_id"] not in rules):
        return "rule-identity-mismatch"
    for selected, canonical in (("policy", "policy"), ("certainty", "semantic_status"),
                                ("resolution_status", "resolution_status"), ("resolution_scope", "resolution_scope")):
        if item.get(canonical) != row[selected]:
            return "decision-cell-mismatch"
    return "metadata-joined"


def read_selected(archive, rows, *, max_member_bytes=64 * 1024 * 1024):
    """Return selected records by (member, occurrence); reject ambiguous sources."""
    wanted = defaultdict(set)
    for row in rows:
        wanted[member_name(row)].add(row["occurrence_id"])
    found, statuses, member_hashes, seen = {}, {}, {}, set()
    arguments = {"fileobj": archive} if hasattr(archive, "read") else {"name": archive}
    with tarfile.open(mode="r|gz", **arguments) as source:
        for member in source:
            if member.name not in wanted:
                continue
            name = member.name
            if name in seen:
                raise ValueError("duplicate selected archive member")
            seen.add(name)
            if not member.isfile() or member.size > max_member_bytes:
                statuses[name] = "invalid-or-oversize-member"
                continue
            raw = source.extractfile(member).read(max_member_bytes + 1)
            member_hashes[name] = hashlib.sha256(raw).hexdigest()
            try:
                envelope = json.loads(raw)
                items = envelope["items"] if isinstance(envelope, dict) else envelope
                if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
                    raise ValueError("invalid canonical envelope")
            except (UnicodeDecodeError, ValueError, KeyError):
                statuses[name] = "invalid-canonical-json"
                continue
            selected = defaultdict(list)
            for item in items:
                occurrence = item.get("occurrence_id")
                if isinstance(occurrence, str) and occurrence in wanted[name]:
                    selected[occurrence].append(item)
            for occurrence in wanted[name]:
                matches = selected[occurrence]
                found[name, occurrence] = (matches[0] if len(matches) == 1 else None,
                                           "occurrence-absent" if not matches else "occurrence-ambiguous")
    return found, statuses, member_hashes


def subject_kind(item):
    subject = item.get("semantic_subject")
    if not isinstance(subject, str) or not subject:
        return "missing"
    if subject == "location":
        return "location"
    prefix = subject.partition(":")[0]
    return prefix if prefix in {"variable", "attribute", "module", "task", "semantic_subject"} else "other"


def join_rows(rows, records, statuses, member_hashes, packet_dir):
    packet_dir.mkdir(parents=True, exist_ok=False)
    results = []
    for row in rows:
        name = member_name(row)
        item, status = records.get((name, row["occurrence_id"]), (None, statuses.get(name, "member-absent")))
        info = {"metadata_status": status, "canonical_member_sha256": member_hashes.get(name, ""),
                "canonical_item_sha256": "", "semantic_subject_kind": "unavailable",
                "has_task_context": False, "metadata_redacted": False,
                "metadata_packet_file": "", "metadata_packet_sha256": "",
                "subject_verified": False, "evidence_complete": False}
        if item is not None:
            status = check_item(row, item)
            info["metadata_status"] = status
            if status == "metadata-joined":
                raw = canonical_bytes(item)
                # The inherited redactor is line based. Compact JSON would let
                # a sensitive key discard the rest of the entire occurrence.
                # Preserve fields on separate lines; this is display text,
                # deliberately not a JSON document to parse after redaction.
                text = json.dumps(item, sort_keys=True, ensure_ascii=False, indent=2)
                redacted = second_pass(redact_sensitive_text_v2(text))
                subject = str(item.get("semantic_subject") or "")
                redacted_subject = second_pass(redact_sensitive_text_v2(subject))
                info.update({"canonical_item_sha256": hashlib.sha256(raw).hexdigest(),
                             "semantic_subject_kind": subject_kind(item),
                             "has_task_context": "|task:" in str(item.get("semantic_subject", "")),
                             "metadata_redacted": redacted != text})
                if scan_text(redacted) or scan_text(redacted_subject):
                    info["metadata_status"] = "metadata-redaction-scan-failed"
                else:
                    packet = {"sample_id": row["sample_id"], "run_id": row["run_id"],
                              "repository": row["repository"], "commit_sha": row["commit_sha"],
                              "occurrence_id": row["occurrence_id"], **info,
                              "detector_claim_is_unverified": True,
                              "redacted_semantic_subject": redacted_subject,
                              "semantic_subject_redacted": redacted_subject != subject,
                              "redacted_canonical_text": redacted}
                    data = json.dumps(packet, indent=2, ensure_ascii=False).encode() + b"\n"
                    filename = row["sample_id"] + ".json"
                    (packet_dir / filename).write_bytes(data)
                    info.update(metadata_packet_file=filename, metadata_packet_sha256=hashlib.sha256(data).hexdigest())
        results.append({**row, **info})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--draw-root", type=Path, required=True)
    parser.add_argument("--retrieval-root", type=Path, required=True)
    parser.add_argument("--draw", action="append", required=True)
    parser.add_argument("--packet-root", type=Path, required=True)
    parser.add_argument("--report-root", type=Path, required=True)
    args = parser.parse_args(argv)
    if (len(set(args.draw)) != len(args.draw) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", d) for d in args.draw)
            or not re.fullmatch(r"[0-9a-f]{64}", args.archive_sha256)):
        parser.error("invalid draw names or archive checksum")
    packet_root, report_root = args.packet_root.resolve(), args.report_root.resolve()
    if (packet_root.exists() or report_root.exists() or packet_root.is_relative_to(report_root)
            or report_root.is_relative_to(packet_root)):
        parser.error("use new, separate local packet and report roots")
    # Complete all input checks before producing a report. Use the same open file
    # for hashing and traversal; reject concurrent edits using stat information.
    draws, all_rows, provenance = {}, [], {}
    for draw in args.draw:
        rows, _ = load_draw(args.draw_root / draw)
        draw_hash = sha256(args.draw_root / draw / "selection-manifest.json")
        retrieved = previous_report(args.retrieval_root / draw, draw_hash, rows)
        draws[draw] = [{**row, **{key: retrieved[row["sample_id"]][key]
                                for key in ("retrieval_status", "source_sha256", "git_blob_oid", "packet_sha256")}}
                       for row in rows]
        all_rows.extend(draws[draw])
        provenance[draw] = {"draw_manifest_sha256": draw_hash,
                            "retrieval_manifest_sha256": sha256(args.retrieval_root / draw / "retrieval-manifest.json")}
    with args.archive.open("rb") as archive:
        before = args.archive.stat()
        actual = digest_open_file(archive)
        if actual != args.archive_sha256:
            raise ValueError("frozen archive checksum mismatch")
        archive.seek(0)
        records, statuses, hashes = read_selected(archive, all_rows)
        after = args.archive.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError("archive changed while being read")
    for draw, rows in draws.items():
        results = join_rows(rows, records, statuses, hashes, packet_root / draw)
        report = report_root / draw
        report.mkdir(parents=True)
        write_csv(report / "metadata-ledger.csv", results)
        manifest = {"schema_version": 1, "purpose": "frozen metadata provenance; detector claims unverified",
                    "eligible_for_performance_scoring": False, "selected_rows": len(rows), "recorded_rows": len(results),
                    "archive_sha256": actual, "archive_checksum_verified": True, **provenance[draw],
                    "status_counts": dict(Counter(row["metadata_status"] for row in results)),
                    "subject_kind_counts": dict(Counter(row["semantic_subject_kind"] for row in results)),
                    "metadata_redacted": sum(row["metadata_redacted"] for row in results),
                    "subject_verified": 0, "complete_rule_evidence": 0, "labels_generated": 0, "model_calls": 0,
                    "implementation_sha256": sha256(Path(__file__)),
                    "dependency_sha256": {name: sha256(Path(__file__).with_name(name)) for name in
                                          ("retrieve_sample_evidence.py", "v007_bundle_context_v2.py",
                                           "v007_bundle_redact_v2.py", "v007_bundle_secret_scan.py", "v007_validation_pilot.py")},
                    "output_sha256": {"metadata-ledger.csv": sha256(report / "metadata-ledger.csv")},
                    "local_packet_directory": str(packet_root / draw),
                    "limits": ["A joined detector claim is not a verified semantic subject or true defect",
                               "Redaction can remove context; failures remain in the selected ledger",
                               "Required designs overlap; counts across draws are not additive"]}
        (report / "metadata-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"draw": draw, "statuses": manifest["status_counts"], "subjects": manifest["subject_kind_counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

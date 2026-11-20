#!/usr/bin/env python3
"""Retrieve base source evidence for calibration IDs from immutable Git blobs.

No checkout, fetch, model call or label generation. Every selected row survives
in the derived ledger, including failures. Redacted packets are local artifacts;
the tracked report contains hashes, statuses and explicit evidence limits.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sample_partitioned_occurrences import read_csv, sha256, stable_digest, write_csv
from scripts.v007_bundle_context_v2 import redact_sensitive_text_v2
from scripts.v007_bundle_redact_v2 import redact_text as second_pass
from scripts.v007_bundle_secret_scan import scan_text


SHA = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SAMPLE_ID = re.compile(r"PROB-[0-9a-f]{64}\Z")


class RetrievalFailure(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def safe_relative(value, *, repository=False):
    path = PurePosixPath(value)
    if (not value or value == "." or value != path.as_posix() or path.is_absolute()
            or any(part in {".", "..", ".git"} for part in path.parts)
            or "\\" in value or any(ord(char) < 32 for char in value)
            or (repository and len(path.parts) != 2)):
        raise RetrievalFailure("unsafe-path")
    return path


def git_environment():
    # Inherited Git overrides must not redirect an exact-source read.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_NO_LAZY_FETCH": "1", "GIT_NO_REPLACE_OBJECTS": "1",
                "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    return env


class FrozenGitReader:
    def __init__(self, root, *, max_bytes=1024 * 1024, timeout=10, trusted_roots=()):
        if max_bytes < 1 or timeout <= 0:
            raise ValueError("source byte limit and timeout must be positive")
        self.root = Path(root).resolve()
        self.trusted_roots = {self.root, *(Path(path).resolve() for path in trusted_roots)}
        self.max_bytes, self.timeout = max_bytes, timeout
        self.environment = git_environment()
        self.flags = ["--no-replace-objects", "--no-lazy-fetch", "--literal-pathspecs", "--no-optional-locks"]
        self.repositories, self.commits = {}, set()
        try:
            probe = subprocess.run(["git", *self.flags, "--version"], capture_output=True,
                                   timeout=timeout, env=self.environment, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError("Git with the required offline read flags is unavailable") from exc
        if probe.returncode:
            raise ValueError("Git does not support the required offline read flags")
        self.git_version = probe.stdout.decode("utf-8", errors="replace").strip()

    def command(self, repository, *args, reason="git-read-failed"):
        try:
            result = subprocess.run(
                ["git", *self.flags, "-C", str(repository), "-c", "protocol.allow=never", *args],
                capture_output=True, timeout=self.timeout, env=self.environment, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RetrievalFailure("git-timeout") from exc
        except OSError as exc:
            raise RetrievalFailure("git-unavailable") from exc
        if result.returncode:
            # Git stderr can contain local or repository-controlled text.
            # Reports use controlled failure codes, never raw stderr.
            raise RetrievalFailure(reason)
        return result.stdout

    def repository(self, project):
        safe_relative(project, repository=True)
        if project not in self.repositories:
            try:
                candidate = (self.root / project).resolve()
                if not any(candidate.is_relative_to(root) for root in self.trusted_roots):
                    raise ValueError("resolved repository outside configured source stores")
            except (OSError, ValueError) as exc:
                raise RetrievalFailure("repository-outside-root") from exc
            if not candidate.is_dir():
                raise RetrievalFailure("repository-unavailable")
            actual = self.command(candidate, "rev-parse", "--show-toplevel", reason="repository-unavailable")
            if Path(os.fsdecode(actual).strip()).resolve() != candidate:
                raise RetrievalFailure("repository-root-mismatch")
            self.repositories[project] = candidate
        return self.repositories[project]

    def read(self, project, commit, path):
        safe_relative(path)
        if not SHA.fullmatch(commit):
            raise RetrievalFailure("invalid-commit-id")
        repository = self.repository(project)
        if (project, commit) not in self.commits:
            kind = self.command(repository, "cat-file", "-t", commit, reason="commit-unavailable").strip()
            if kind != b"commit":
                raise RetrievalFailure("not-a-commit")
            self.commits.add((project, commit))
        tree = self.command(repository, "ls-tree", "-z", commit, "--", path, reason="tree-unavailable")
        entries = tree.split(b"\0")
        if len(entries) != 2 or not entries[0]:
            raise RetrievalFailure("path-unavailable")
        try:
            header, actual_path = entries[0].split(b"\t", 1)
            mode, kind, oid = header.decode("ascii").split()
        except (ValueError, UnicodeDecodeError) as exc:
            raise RetrievalFailure("invalid-tree-entry") from exc
        if actual_path != path.encode("utf-8"):
            raise RetrievalFailure("path-mismatch")
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise RetrievalFailure("not-a-regular-blob")
        try:
            size = int(self.command(repository, "cat-file", "-s", oid, reason="blob-unavailable").strip())
        except ValueError as exc:
            raise RetrievalFailure("invalid-blob-size") from exc
        if size > self.max_bytes:
            raise RetrievalFailure("source-too-large")
        raw = self.command(repository, "cat-file", "blob", oid, reason="blob-unavailable")
        digest = hashlib.sha1 if len(oid) == 40 else hashlib.sha256
        if len(raw) != size or digest(f"blob {size}\0".encode() + raw).hexdigest() != oid:
            raise RetrievalFailure("blob-integrity-mismatch")
        return raw, oid


class FrozenGitSources:
    """Try explicit local stores for the same immutable snapshot, never fetch."""

    RECOVERABLE = {
        "repository-unavailable", "repository-root-mismatch", "repository-outside-root",
        "commit-unavailable", "tree-unavailable", "blob-unavailable", "git-timeout",
        "blob-integrity-mismatch",
    }

    def __init__(self, roots, **options):
        roots = [Path(root).resolve() for root in roots]
        if not roots or len(set(roots)) != len(roots):
            raise ValueError("source store list must be nonempty and unique")
        self.readers = [FrozenGitReader(root, trusted_roots=roots, **options) for root in roots]
        self.git_version = self.readers[0].git_version
        self.last_read = {}

    def read(self, project, commit, path):
        attempts = []
        self.last_read = {"source_store_index": "", "resolved_repository": "", "source_attempts": "[]"}
        for index, reader in enumerate(self.readers):
            try:
                raw, oid = reader.read(project, commit, path)
            except RetrievalFailure as exc:
                attempts.append({"store_index": index, "status": exc.reason})
                self.last_read["source_attempts"] = json.dumps(attempts, separators=(",", ":"))
                if exc.reason not in self.RECOVERABLE:
                    raise
            else:
                attempts.append({"store_index": index, "status": "blob-read"})
                self.last_read = {
                    "source_store_index": index, "resolved_repository": str(reader.repository(project)),
                    "source_attempts": json.dumps(attempts, separators=(",", ":")),
                }
                return raw, oid
        raise RetrievalFailure("source-not-in-configured-stores")


def base_packet(row, raw, oid, *, max_lines=1500, window=80):
    info = {
        "source_sha256": hashlib.sha256(raw).hexdigest(), "git_blob_oid": oid,
        "source_bytes": len(raw), "source_line_count": "", "anchor_in_bounds": False,
        "source_scope": "", "truncated": False, "redacted_lines": 0,
        "redaction_affects_anchor": False, "subject_verified": False,
        "evidence_complete": False, "rule_evidence_status": "base-source-only",
    }
    try:
        if b"\0" in raw:
            raise RetrievalFailure("binary-source")
        text = raw.decode("utf-8")
        lines = text.splitlines()
        info["source_line_count"] = len(lines)
        if not lines:
            raise RetrievalFailure("empty-source")
        if lines[0].startswith("$ANSIBLE_VAULT;"):
            raise RetrievalFailure("encrypted-source")
        if not re.fullmatch(r"[1-9][0-9]*", row["line"]):
            raise RetrievalFailure("invalid-anchor")
        anchor = int(row["line"])
        if anchor > len(lines):
            raise RetrievalFailure("anchor-out-of-range")
        info["anchor_in_bounds"] = True
        # Redact the entire file before windowing, so a window cannot lose
        # the opening of a sensitive multiline block. Preserve line counts.
        try:
            safe = second_pass(redact_sensitive_text_v2("\n".join(lines)))
        except Exception as exc:  # preserve the selected row if redaction fails
            raise RetrievalFailure("redaction-failed") from exc
        safe_lines = safe.split("\n")
        if len(safe_lines) != len(lines):
            raise RetrievalFailure("redaction-line-count-mismatch")
        if scan_text(safe):
            raise RetrievalFailure("residual-secret-scan-blocked")
        info["redacted_lines"] = sum(a != b for a, b in zip(lines, safe_lines))
        info["redaction_affects_anchor"] = lines[anchor - 1] != safe_lines[anchor - 1]
        full = len(lines) <= max_lines
        start, end = (1, len(lines)) if full else (max(1, anchor - window), min(len(lines), anchor + window))
        info["source_scope"], info["truncated"] = ("full-file" if full else "anchor-window"), not full
        packet = {
            "schema_version": 1, "sample_id": row["sample_id"], "run_id": row["run_id"],
            "repository": row["repository"], "commit_sha": row["commit_sha"], "path": row["file"],
            "requested_line": anchor, "rule_id": row["rule_id"], **info,
            "display_line_start": start, "display_line_end": end,
            "numbered_source": "\n".join(f"{number:5d} | {safe_lines[number - 1]}" for number in range(start, end + 1)),
            "missing_evidence": ["semantic subject/construct not verified", "rule-specific evidence not assembled"]
                                + (["full file exceeds display limit"] if not full else []),
            "rendering": "UTF-8 source, line endings normalized, line-preserving redaction",
            "eligible_for_performance_scoring": False,
        }
        return packet, info, ""
    except UnicodeDecodeError:
        return None, info, "source-not-utf8"
    except RetrievalFailure as exc:
        return None, info, exc.reason


def load_draw(draw_dir):
    manifest = json.loads((draw_dir / "selection-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("eligible_for_performance_scoring") is not False:
        raise ValueError("expected a non-evaluation calibration draw")
    for name in ("selection-ledger.csv", "sampling-plan.csv"):
        if sha256(draw_dir / name) != manifest["output_sha256"][name]:
            raise ValueError(f"draw hash mismatch: {name}")
    rows = list(read_csv(draw_dir / "selection-ledger.csv"))
    if len(rows) != manifest["selected_occurrences"]:
        raise ValueError("selected row count disagrees with draw manifest")
    seen = set()
    for row in rows:
        expected = "PROB-" + stable_digest(row["instrument"], row["run_id"], row["repository"],
                                            row["commit_sha"], row["occurrence_id"])
        if (not SAMPLE_ID.fullmatch(row["sample_id"]) or row["sample_id"] != expected
                or row["sample_id"] in seen):
            raise ValueError("invalid or duplicate sample identity")
        if (row["dataset_role"] != "calibration" or row["eligible_for_performance_scoring"].lower() != "false"
                or row["run_id"] != manifest["run_id"] or row["instrument"] != manifest["instrument"]
                or row["retrieval_status"] != "pending" or row["label_status"] != "not-started"):
            raise ValueError("draw row scope/state disagrees with calibration manifest")
        seen.add(row["sample_id"])
    return rows, manifest


def retrieve_rows(rows, reader, packet_dir, *, max_lines=1500, window=80):
    if max_lines < 1 or window < 0:
        raise ValueError("display limit must be positive and window nonnegative")
    rows = list(rows)
    ids = [row["sample_id"] for row in rows]
    if not ids or len(set(ids)) != len(ids) or any(not SAMPLE_ID.fullmatch(value) for value in ids):
        raise ValueError("retrieval requires nonempty, unique, safe sample IDs")
    packet_dir.mkdir(parents=True, exist_ok=False)
    results = []
    # Cache immutable blobs, including controlled failures, across selected
    # occurrences. No source bytes are written to disk before redaction.
    sources = {}
    for row in rows:
        info = {"source_sha256": "", "git_blob_oid": "", "source_bytes": "", "source_line_count": "",
                "anchor_in_bounds": False, "source_scope": "", "truncated": False, "redacted_lines": 0,
                "redaction_affects_anchor": False, "subject_verified": False,
                "evidence_complete": False, "rule_evidence_status": "base-source-only"}
        key = (row["repository"], row["commit_sha"], row["file"])
        packet_path = packet_hash = failure = ""
        if key not in sources:
            try:
                raw, oid = reader.read(*key)
                sources[key] = (raw, oid, "", dict(getattr(reader, "last_read", {})))
            except RetrievalFailure as exc:
                sources[key] = (None, None, exc.reason, dict(getattr(reader, "last_read", {})))
        raw, oid, failure, source_info = sources[key]
        if not failure:
            packet, info, failure = base_packet(row, raw, oid, max_lines=max_lines, window=window)
            if packet is not None:
                packet_path = row["sample_id"] + ".json"
                data = (json.dumps(packet, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
                (packet_dir / packet_path).write_bytes(data)
                packet_hash = hashlib.sha256(data).hexdigest()
        results.append({**row, "retrieval_status": "unavailable" if failure else "source-retrieved",
                        **info, "failure_reason": failure, "packet_file": packet_path, "packet_sha256": packet_hash,
                        "source_store_index": source_info.get("source_store_index", ""),
                        "resolved_repository": source_info.get("resolved_repository", ""),
                        "source_attempts": source_info.get("source_attempts", "[]")})
    return results


def previous_report(report_dir, draw_hash, rows):
    if report_dir is None:
        return {}
    manifest = json.loads((report_dir / "retrieval-manifest.json").read_text(encoding="utf-8"))
    if manifest["draw_manifest_sha256"] != draw_hash:
        raise ValueError("previous report is from another selection draw")
    ledger = report_dir / "retrieval-ledger.csv"
    if sha256(ledger) != manifest["output_sha256"][ledger.name]:
        raise ValueError("previous retrieval ledger hash mismatch")
    previous_rows = list(read_csv(ledger))
    previous = {row["sample_id"]: row for row in previous_rows}
    if len(previous) != len(previous_rows) or previous.keys() != {row["sample_id"] for row in rows}:
        raise ValueError("previous report does not preserve the same selected IDs")
    for row in rows:
        for key in ("run_id", "repository", "commit_sha", "occurrence_id", "file", "line", "rule_id", "sampling_weight"):
            if previous[row["sample_id"]][key] != row[key]:
                raise ValueError("previous report changed a selected identity or weight")
    return previous


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draw-dir", type=Path, required=True)
    parser.add_argument("--repositories-root", type=Path, action="append", required=True,
                        help="local Git store; repeat in lookup order for exact-SHA cache recovery")
    parser.add_argument("--previous-report", type=Path,
                        help="optional prior retrieval report for the same draw; preserve its failure history")
    parser.add_argument("--packet-dir", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    parser.add_argument("--max-bytes", type=int, default=1024 * 1024)
    parser.add_argument("--max-lines", type=int, default=1500)
    parser.add_argument("--window", type=int, default=80)
    parser.add_argument("--git-timeout", type=float, default=10)
    args = parser.parse_args(argv)
    if args.packet_dir.exists() or args.report_dir.exists():
        parser.error("output directory exists; use new packet and report directories")
    packet_path, report_path = args.packet_dir.resolve(), args.report_dir.resolve()
    if packet_path.is_relative_to(report_path) or report_path.is_relative_to(packet_path):
        parser.error("packet and report directories must be separate")
    if any(packet_path.is_relative_to(root.resolve()) or report_path.is_relative_to(root.resolve())
           for root in args.repositories_root):
        parser.error("output directories must be outside the source repository root")
    rows, draw = load_draw(args.draw_dir)
    draw_hash = sha256(args.draw_dir / "selection-manifest.json")
    previous = previous_report(args.previous_report, draw_hash, rows)
    reader = FrozenGitSources(args.repositories_root, max_bytes=args.max_bytes, timeout=args.git_timeout)
    results = retrieve_rows(rows, reader, args.packet_dir, max_lines=args.max_lines, window=args.window)
    if previous:
        for result in results:
            before = previous[result["sample_id"]]
            result.update({"previous_retrieval_status": before["retrieval_status"],
                           "previous_failure_reason": before["failure_reason"],
                           "recovered_from_previous": before["retrieval_status"] == "unavailable"
                                                      and result["retrieval_status"] == "source-retrieved"})
    args.report_dir.mkdir(parents=True)
    write_csv(args.report_dir / "retrieval-ledger.csv", results)
    statuses = dict(Counter(row["retrieval_status"] for row in results))
    manifest = {
        "schema_version": 1, "purpose": "base source retrieval; rule-specific evidence still incomplete",
        "run_id": draw["run_id"], "instrument": draw["instrument"], "eligible_for_performance_scoring": False,
        "selected_rows": len(rows), "recorded_rows": len(results), "status_counts": statuses,
        "failure_counts": dict(Counter(row["failure_reason"] for row in results if row["failure_reason"])),
        "truncated_packets": sum(row["truncated"] for row in results),
        "subject_verified": 0, "complete_rule_evidence": 0, "labels_generated": 0, "model_calls": 0,
        "draw_manifest_sha256": draw_hash,
        "previous_report_manifest_sha256": sha256(args.previous_report / "retrieval-manifest.json") if previous else None,
        "recovered_from_previous": sum(result.get("recovered_from_previous", False) for result in results),
        "source_stores": [str(source.root) for source in reader.readers],
        "implementation_sha256": sha256(Path(__file__)),
        "redaction_sha256": {name: sha256(Path(__file__).with_name(name)) for name in
                             ("v007_validation_pilot.py", "v007_bundle_context_v2.py",
                              "v007_bundle_redact_v2.py", "v007_bundle_secret_scan.py")},
        "git_version": reader.git_version, "python_version": platform.python_version(),
        "source_method": "immutable Git objects; replacements and lazy fetching disabled",
        "limits": {"max_bytes": args.max_bytes, "max_lines": args.max_lines, "window": args.window,
                   "git_timeout": args.git_timeout},
        "local_packet_directory": str(args.packet_dir),
        "output_sha256": {"retrieval-ledger.csv": sha256(args.report_dir / "retrieval-ledger.csv")},
        "limits_to_interpretation": ["Line bounds do not verify semantic subjects", "Redaction can remove decisive evidence",
                                     "Windows are explicit truncation", "Rule-specific and cross-file evidence not built",
                                     "Residual-secret scan is a heuristic; packets are local artifacts"],
    }
    (args.report_dir / "retrieval-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected": len(rows), "status_counts": statuses, "failure_counts": manifest["failure_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Bounded complete-tree GitLeaks triage with no published source or secrets."""
from __future__ import annotations

import argparse
from collections import Counter
import cProfile
import faulthandler
import json
import os
from pathlib import Path
import pstats
import re
import signal
import subprocess
import sys
import time
from unittest.mock import patch

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.profile_frozen_context import materialize, write_json
from scripts.retrieve_sample_evidence import FrozenGitSources, SHA, safe_relative
from scripts.sample_partitioned_occurrences import sha256, write_csv


def worker(source, work, executable, native_timeout):
    from ansibleguard.external import gitleaks

    work.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    profile = cProfile.Profile()
    faulthandler.enable()
    faulthandler.dump_traceback_later(10, repeat=True)

    def emit(stage, state, **details):
        with (work / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"stage": stage, "state": state,
                                     "elapsed_seconds": time.monotonic() - started, **details}) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    native_run, native_filter = subprocess.run, gitleaks._filter_known_noise

    def timed_run(*args, **kwargs):
        emit("native-provider", "start")
        begin = time.monotonic()
        result = native_run(*args, **kwargs)
        emit("native-provider", "end", duration_seconds=time.monotonic() - begin, returncode=result.returncode)
        return result

    def timed_filter(findings, root):
        emit("noise-postprocessing", "start", findings=len(findings),
             distinct_files=len({f.get("File") or f.get("file") for f in findings}))
        begin = time.monotonic()
        result = native_filter(findings, root)
        emit("noise-postprocessing", "end", duration_seconds=time.monotonic() - begin,
             retained=len(result[0]), suppressed=len(result[1]))
        return result

    profile.enable()
    result = {"status": "error", "eligible_for_performance_scoring": False}
    try:
        emit("adapter", "start")
        with patch.object(gitleaks.subprocess, "run", timed_run), patch.object(gitleaks, "_filter_known_noise", timed_filter):
            value = gitleaks.scan_with_gitleaks(source, executable, timeout=native_timeout)
        result.update(status=value.status, findings=len(value.findings), suppressed=len(value.suppressed_findings),
                      metadata=value.metadata)
        emit("adapter", "end", status=value.status, duration_seconds=time.monotonic() - started)
    except Exception as exc:
        result["error_type"] = type(exc).__name__
        emit("adapter", "error", error_type=type(exc).__name__)
    finally:
        profile.disable()
        faulthandler.cancel_dump_traceback_later()
        profile.dump_stats(str(work / "profile.pstats"))
        write_json(work / "result.json", result)
    return 0 if result["status"] == "completed" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project")
    parser.add_argument("--commit")
    parser.add_argument("--repositories-root", action="append", type=Path)
    parser.add_argument("--local-dir", type=Path)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--gitleaks", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--native-timeout", type=float, default=30)
    parser.add_argument("--worker-root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--worker-dir", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not (0 < args.native_timeout < args.timeout):
        parser.error("positive native timeout below worker deadline required")
    if args.worker_root:
        if not args.worker_dir:
            parser.error("worker directory required")
        return worker(args.worker_root, args.worker_dir, args.gitleaks, args.native_timeout)
    if not all((args.project, args.commit, args.repositories_root, args.local_dir, args.report_dir)):
        parser.error("immutable source identity, stores and separate new outputs required")
    if not SHA.fullmatch(args.commit):
        parser.error("full source commit required")
    safe_relative(args.project, repository=True)
    local, report = args.local_dir.resolve(), args.report_dir.resolve()
    if (local.exists() or report.exists() or local.is_relative_to(report) or report.is_relative_to(local)
            or any(p.is_relative_to(r.resolve()) for p in (local, report) for r in args.repositories_root)):
        parser.error("new separate output directories outside source stores required")
    executable = args.gitleaks.resolve(strict=True)
    version = subprocess.run([str(executable), "version"], capture_output=True, text=True, check=True, timeout=10).stdout.strip()
    local.mkdir(parents=True)
    sources = FrozenGitSources(args.repositories_root, max_bytes=100 * 1024 * 1024)
    begin = time.monotonic()
    inventory = materialize(sources, args.project, args.commit, local / "source")
    acquisition_seconds = time.monotonic() - begin
    if any(row["status"] != "copied" for row in inventory):
        write_json(local / "incomplete-source.json", inventory)
        raise ValueError("complete regular source required for whole-tree probe")
    report.mkdir(parents=True)
    write_csv(report / "source-inventory.csv", inventory)
    command = [sys.executable, str(Path(__file__).resolve()), "--worker-root", str(local / "source"),
               "--worker-dir", str(local / "worker"), "--gitleaks", str(executable),
               "--native-timeout", str(args.native_timeout), "--timeout", str(args.timeout)]
    timed_out = False
    with (local / "stdout.log").open("wb") as stdout, (local / "stderr.log").open("wb") as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    work = local / "worker"
    events = [json.loads(line) for line in (work / "events.jsonl").read_text().splitlines()] if (work / "events.jsonl").exists() else []
    write_json(report / "stage-events.json", events)
    result = json.loads((work / "result.json").read_text()) if (work / "result.json").exists() else None
    trace = (local / "stderr.log").read_text(errors="replace")
    frames = Counter(re.findall(r'File "([^"\n]+)", line ([0-9]+) in ([^\n]+)', trace))
    if frames:
        write_csv(report / "stack-frames.csv", [{"file": f, "line": n, "function": name, "observations": count}
                                               for (f, n, name), count in frames.most_common()])
    if (work / "profile.pstats").exists():
        stats = pstats.Stats(str(work / "profile.pstats"))
        write_csv(report / "top-functions.csv", [{"file": f, "line": n, "function": name, "calls": values[1],
                                                  "self_seconds": values[2], "cumulative_seconds": values[3]}
                                                 for (f, n, name), values in sorted(stats.stats.items(), key=lambda item: -item[1][3])[:40]])
    manifest = {"purpose": "bounded current GitLeaks adapter triage on complete frozen tree; not archived rerun",
                "project": args.project, "commit_sha": args.commit, "source_blobs": len(inventory),
                "source_bytes": sum(r["bytes"] for r in inventory), "acquisition_seconds": acquisition_seconds,
                "max_source_blob_bytes": 100 * 1024 * 1024, "worker_timeout_seconds": args.timeout,
                "native_timeout_seconds": args.native_timeout, "status": "worker-timeout" if timed_out else (result or {}).get("status", "worker-error"),
                "worker_result": result, "returncode": process.returncode, "last_event": events[-1] if events else None,
                "gitleaks_version": version, "gitleaks_sha256": sha256(executable), "stack_dumps": trace.count("Timeout ("),
                "implementation_sha256": sha256(Path(__file__)), "dependency_sha256": {str(p): sha256(p) for p in (
                    Path("src/ansibleguard/external/gitleaks.py"), Path("scripts/profile_frozen_context.py"),
                    Path("scripts/retrieve_sample_evidence.py"))}, "eligible_for_performance_scoring": False,
                "model_calls": 0, "local_directory": str(local),
                "output_sha256": {p.name: sha256(p) for p in report.iterdir() if p.is_file()},
                "limits": ["Current adapter/binary, not archived environment", "Original executable bits/history/config not reproduced",
                           "Native and worker deadlines intentionally shorter than study", "No target programs executed",
                           "Raw source/logs remain local; source paths and counts published", "No repository completeness/accuracy claim"]}
    write_json(report / "probe-manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "source_blobs": len(inventory), "source_bytes": manifest["source_bytes"],
                      "last_event": manifest["last_event"], "worker_result": result}), flush=True)
    return 0 if manifest["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

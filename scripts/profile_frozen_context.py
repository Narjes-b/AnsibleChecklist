#!/usr/bin/env python3
"""Bounded offline context/symbol triage for one frozen repository snapshot.

Reads exact Git blobs into a new local mirror, never checks out/fetches or runs
target programs. Classification/context/symbol stages execute, with optional
file metric detectors. Module docs, external providers and LLM calls are excluded.
"""

from __future__ import annotations

import argparse
from collections import Counter
import cProfile
import faulthandler
import hashlib
import json
import os
from pathlib import Path
import platform
import pstats
import re
import resource
import subprocess
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.retrieve_sample_evidence import SHA, FrozenGitSources, RetrievalFailure, git_environment, safe_relative
from scripts.sample_partitioned_occurrences import sha256, write_csv


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def tree_entries(sources, project, commit):
    if not SHA.fullmatch(commit):
        raise ValueError("full commit SHA required")
    safe_relative(project, repository=True)
    for reader in sources.readers:
        try:
            repository = reader.repository(project)
            if reader.command(repository, "cat-file", "-t", commit, reason="commit-unavailable").strip() != b"commit":
                raise RetrievalFailure("not-a-commit")
            raw = reader.command(repository, "ls-tree", "-r", "-z", commit, reason="tree-unavailable")
        except RetrievalFailure as exc:
            if exc.reason not in FrozenGitSources.RECOVERABLE:
                raise
            continue
        result = []
        for entry in raw.split(b"\0"):
            if not entry:
                continue
            header, path = entry.split(b"\t", 1)
            mode, kind, oid = header.decode("ascii").split()
            relative = path.decode("utf-8")
            safe_relative(relative)
            result.append((mode, kind, oid, relative))
        return result
    raise RetrievalFailure("frozen-tree-unavailable")


def materialize(sources, project, commit, directory):
    directory.mkdir(parents=True, exist_ok=False)
    records = []
    for mode, kind, oid, relative in tree_entries(sources, project, commit):
        record = {"path": relative, "source_mode": mode, "git_blob_oid": oid, "status": "skipped-nonregular",
                  "sha256": "", "bytes": 0}
        if mode in {"100644", "100755"} and kind == "blob":
            try:
                raw, actual = sources.read(project, commit, relative)
                if actual != oid:
                    raise RetrievalFailure("tree-blob-mismatch")
                path = directory / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)  # Source scripts are data, not executable programs.
                path.chmod(0o600)
                record.update(status="copied", sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
            except RetrievalFailure as exc:
                record["status"] = exc.reason
        records.append(record)
    # A fresh Git boundary prevents inheritance of the agent workspace's
    # project config. No original hooks/config or checkout filters are used.
    template = directory.parent / "empty-git-template"
    template.mkdir()
    subprocess.run(["git", "-C", str(directory), "init", "-q", "--template=" + str(template)],
                   env=git_environment(), capture_output=True, check=True, timeout=10)
    return records


def worker(root, work, *, stack_seconds=15, memory_mib=2048, include_file_detectors=False):
    work.mkdir(parents=True, exist_ok=True)
    os.environ["ANSIBLEGUARD_DISABLE_ANSIBLE_DOC"] = "1"
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib * 1024 * 1024, memory_mib * 1024 * 1024))
    faulthandler.enable()
    faulthandler.dump_traceback_later(stack_seconds, repeat=True)
    started, profile = time.monotonic(), cProfile.Profile()
    events = work / "events.jsonl"
    result = {"status": "running", "stage": "imports", "eligible_for_performance_scoring": False}

    def emit(stage, state, **details):
        value = {"stage": stage, "state": state, "elapsed_seconds": time.monotonic() - started, **details}
        with events.open("a", encoding="utf-8") as target:
            target.write(json.dumps(value) + "\n")
            target.flush()
            os.fsync(target.fileno())

    def stage(name, operation, summarize=lambda value: {}):
        result["stage"] = name
        emit(name, "start")
        begin = time.monotonic()
        value = operation()
        emit(name, "end", duration_seconds=time.monotonic() - begin, **summarize(value))
        return value

    profile.enable()
    try:
        emit("imports", "start")
        from ansibleguard.cli import collect_yaml_files
        from ansibleguard.file_manifest import classify_repository, write_file_manifest
        from ansibleguard.runtime import build_repository_context_stage, build_symbol_index_stage, prepare_scan_context
        emit("imports", "end")
        rows = stage("classification", lambda: classify_repository(root),
                     lambda values: {"yaml_files": len(values), "included": sum(row["included"] == "true" for row in values)})
        manifest = write_file_manifest(rows, work / "classification.csv")
        context = stage("selection", lambda: prepare_scan_context(root, work / "scan", "snapshot-source", manifest, collect_yaml_files),
                        lambda value: {"selected_files": len(value.selected_files)})
        repository = stage("repository-context", lambda: build_repository_context_stage(context),
                           lambda value: {"parsed_documents": len(value.parsed_documents),
                                          "tasks": sum(len(tasks) for tasks in value.tasks_by_file.values())})
        symbols = stage("symbol-index", lambda: build_symbol_index_stage(context, repository),
                        lambda value: {"definitions": len(value.definitions), "edges": len(value.edges)})
        if include_file_detectors:
            from ansibleguard.parser import mainn

            repository = repository.with_symbol_graph(symbols)
            for path in context.source_files:
                relative = path.relative_to(context.scan_root).as_posix()
                stage("file-detectors:" + relative,
                      lambda path=path: mainn(path, symbol_index=symbols, enabled_rules=context.definition["rules"],
                                             parsed_document=repository.document_for(path), repository_context=repository),
                      lambda metrics: {"structurally_analyzed": metrics is not None,
                                       "detector_timings": metrics.get("_detector_timings", {}) if metrics else {},
                                       "detector_errors": len(metrics.get("_detector_diagnostics", [])) if metrics else 0})
        result.update(status="completed", selected_files=len(context.selected_files), definitions=len(symbols.definitions),
                      edges=len(symbols.edges), duration_seconds=time.monotonic() - started)
    except Exception as exc:
        emit(result["stage"], "error", error_type=type(exc).__name__)
        result.update(status="error", error_type=type(exc).__name__, duration_seconds=time.monotonic() - started)
    finally:
        profile.disable()
        faulthandler.cancel_dump_traceback_later()
        profile.dump_stats(str(work / "profile.pstats"))
        result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        write_json(work / "worker-result.json", result)
    return 0 if result["status"] == "completed" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project")
    parser.add_argument("--commit")
    parser.add_argument("--repositories-root", type=Path, action="append")
    parser.add_argument("--local-dir", type=Path)
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--timeout", type=float, default=75)
    parser.add_argument("--stack-seconds", type=int, default=15)
    parser.add_argument("--memory-mib", type=int, default=2048)
    parser.add_argument("--include-file-detectors", action="store_true",
                        help="also profile parser metric detectors; excludes threshold evaluation/reporting and CLI fallback checks")
    parser.add_argument("--worker-root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--worker-dir", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.timeout <= 0 or args.stack_seconds < 1 or args.memory_mib < 128:
        parser.error("positive deadline/stack period and at least 128 MiB required")
    if args.worker_root:
        if args.worker_dir is None:
            parser.error("worker directory required")
        return worker(args.worker_root, args.worker_dir, stack_seconds=args.stack_seconds, memory_mib=args.memory_mib,
                      include_file_detectors=args.include_file_detectors)
    if not all((args.project, args.commit, args.repositories_root, args.local_dir, args.report_dir)):
        parser.error("project, commit, source stores and local/report directories required")
    if not SHA.fullmatch(args.commit):
        parser.error("full immutable commit SHA required")
    try:
        safe_relative(args.project, repository=True)
    except RetrievalFailure:
        parser.error("safe owner/repository identity required")
    local, report = args.local_dir.resolve(), args.report_dir.resolve()
    if (local.exists() or report.exists() or local.is_relative_to(report) or report.is_relative_to(local)
            or any(output.is_relative_to(root.resolve()) for output in (local, report) for root in args.repositories_root)):
        parser.error("new separate output directories outside source stores required")
    reader = FrozenGitSources(args.repositories_root)
    local.mkdir(parents=True)
    begin = time.monotonic()
    source = materialize(reader, args.project, args.commit, local / "source")
    acquisition_seconds = time.monotonic() - begin
    write_json(local / "source-manifest.json", source)
    work = local / "worker"
    work.mkdir()
    command = [sys.executable, str(Path(__file__).resolve()), "--worker-root", str(local / "source"),
               "--worker-dir", str(work), "--stack-seconds", str(args.stack_seconds), "--memory-mib", str(args.memory_mib)]
    if args.include_file_detectors:
        command.append("--include-file-detectors")
    timed_out, returncode = False, None
    with (local / "stdout.log").open("wb") as stdout, (local / "stderr.log").open("wb") as stderr:
        try:
            result = subprocess.run(command, cwd=Path(__file__).resolve().parents[1], stdout=stdout, stderr=stderr,
                                    timeout=args.timeout, env={**os.environ, "PYTHONUNBUFFERED": "1"})
            returncode = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    report.mkdir(parents=True)
    events = []
    event_path = work / "events.jsonl"
    if event_path.exists():
        for line in event_path.read_text().splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
    write_json(report / "stage-events.json", events)
    worker_result = json.loads((work / "worker-result.json").read_text()) if (work / "worker-result.json").exists() else None
    trace = (local / "stderr.log").read_text(errors="replace")
    frames = Counter(re.findall(r'File "([^"\n]+)", line ([0-9]+) in ([^\n]+)', trace))
    if frames:
        write_csv(report / "stack-frames.csv", [{"file": file, "line": line, "function": function, "observations": count}
                                               for (file, line, function), count in frames.most_common()])
    if (work / "profile.pstats").exists():
        stats = pstats.Stats(str(work / "profile.pstats"))
        top = sorted(stats.stats.items(), key=lambda item: item[1][3], reverse=True)[:40]
        write_csv(report / "top-functions.csv", [{"file": file, "line": line, "function": function,
                                                  "primitive_calls": values[0], "calls": values[1],
                                                  "self_seconds": values[2], "cumulative_seconds": values[3]}
                                                 for (file, line, function), values in top])
    manifest = {"purpose": "bounded offline context/symbol and optional file-metric triage; not full study rerun",
                "project": args.project, "commit_sha": args.commit, "source_method": "verified immutable Git blobs; no checkout/fetch",
                "source_counts": dict(Counter(item["status"] for item in source)), "source_materialization_seconds": acquisition_seconds,
                "source_manifest_sha256": sha256(local / "source-manifest.json"), "worker_timeout_seconds": args.timeout,
                "memory_limit_mib": args.memory_mib, "stack_period_seconds": args.stack_seconds,
                "status": "timeout" if timed_out else (worker_result or {}).get("status", "worker-failed"),
                "returncode": returncode, "worker_result": worker_result,
                "last_event": events[-1] if events else None, "stack_dumps": trace.count("Timeout ("),
                "module_docs_disabled": True, "providers_run": False, "file_detectors_requested": args.include_file_detectors,
                "file_detector_completions": sum(e["state"] == "end" and e["stage"].startswith("file-detectors:") for e in events),
                "model_calls": 0,
                "eligible_for_performance_scoring": False, "local_directory": str(local),
                "implementation_sha256": sha256(Path(__file__)), "git_version": reader.git_version,
                "python_version": platform.python_version(),
                "dependency_sha256": {str(path): sha256(path) for path in (
                    Path("src/ansibleguard/analysis_context.py"), Path("src/ansibleguard/symbol_index.py"),
                    Path("src/ansibleguard/runtime.py"), Path("src/ansibleguard/document.py"),
                    Path("src/ansibleguard/file_manifest.py"), Path("src/ansibleguard/parser.py"),
                    Path("scripts/retrieve_sample_evidence.py"))},
                "local_log_sha256": {name: sha256(local / name) for name in ("stdout.log", "stderr.log")},
                "output_sha256": {path.name: sha256(path) for path in report.iterdir() if path.is_file()},
                "limits": ["Current implementation, not archived analyzer commit", "Fresh Git boundary, no original history/config",
                           "Source executable modes deliberately not applied", "Skipped nonregular/oversize blobs remain explicit",
                           "Worker deadline excludes acquisition; Git commands have their own bounds",
                           "Module docs/providers/threshold evaluation/reporting/CLI fallback detectors remain untested",
                           "File metric detectors run only when explicitly requested", "Original timeout attribution remains open"]}
    write_json(report / "probe-manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "source_counts": manifest["source_counts"],
                      "worker_result": worker_result, "last_event": manifest["last_event"]}), flush=True)
    return 0 if manifest["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

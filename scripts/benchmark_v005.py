#!/usr/bin/env python3
"""Run a reproducible v0.0.5 parse/index benchmark.

The benchmark intentionally measures the shared repository context rather
than provider wall time. It is safe to run against a fixture directory or a
small checked-out corpus and never modifies the source tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

from ansibleguard.analysis_context import build_repository_analysis_context


def peak_memory_mb() -> float | None:
    """Return process peak RSS where the platform exposes it."""
    try:
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return round(value / 1024, 3)
    except (ImportError, ValueError):
        return None


def collect_yaml(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )


def semantic_index_signature(context) -> str:
    """Stable signature for parse/index equivalence across cache execution."""
    payload = {
        "documents": [
            {
                "file": file_context.relative_path,
                "sha256": file_context.source_hash,
                "parse_status": file_context.parse_status,
                "document_type": file_context.document_type,
                "classification": file_context.classification,
            }
            for file_context in sorted(
                context.file_contexts.values(), key=lambda item: item.relative_path
            )
        ],
        "tasks": [
            {
                "file": context.file_context_for(path).relative_path,
                "ordinal": task.ordinal,
                "action": task.action,
                "name": task.name,
                "jinja_references": list(task.jinja_references),
            }
            for path in sorted(context.tasks_by_file)
            for task in context.tasks_for(path)
        ],
        "includes": [
            {
                "source": edge.source,
                "action": edge.action,
                "raw_target": edge.raw_target,
                "resolved_target": edge.resolved_target,
                "resolution": str(edge.resolution),
                "task_ordinal": edge.task_ordinal,
            }
            for edge in sorted(
                context.include_relationships,
                key=lambda item: (
                    item.source,
                    item.task_ordinal if item.task_ordinal is not None else -1,
                    item.action,
                    item.raw_target or "",
                    item.resolved_target or "",
                    str(item.resolution),
                ),
            )
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def run_benchmark(root: Path, cache_dir: Path | None = None, repeat: int = 1) -> dict:
    files = collect_yaml(root)
    runs = []
    for iteration in range(max(1, repeat)):
        started = time.perf_counter()
        context = build_repository_analysis_context(root, files, cache_dir=cache_dir)
        elapsed = time.perf_counter() - started
        runs.append({
            "iteration": iteration + 1,
            "seconds": round(elapsed, 6),
            "peak_memory_mb": peak_memory_mb(),
            "semantic_index_sha256": semantic_index_signature(context),
            "performance": dict(context.performance),
            "selected_population": list(context.selected_population),
        })
    return {
        "schema": "ansibleguard-v005-benchmark-v1",
        "root": str(root.resolve()),
        "yaml_files": len(files),
        "runs": runs,
        "min_seconds": min(run["seconds"] for run in runs),
        "max_seconds": max(run["seconds"] for run in runs),
    }


def run_benchmark_manifest(manifest_path: Path) -> dict:
    """Run named benchmark shapes declared in a portable JSON manifest.

    Each entry is ``{"name": str, "root": str, "repeat": int?}``; relative
    roots resolve against the manifest. The manifest is deliberately data-only
    so a frozen research corpus can be registered without code changes.
    """
    manifest_path = Path(manifest_path).resolve()
    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = loaded.get("benchmarks") if isinstance(loaded, dict) else None
    if not isinstance(entries, list):
        raise ValueError("benchmark manifest requires a 'benchmarks' list")
    results = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            raise ValueError("every benchmark manifest entry requires a name")
        root = entry.get("root")
        if not isinstance(root, str):
            raise ValueError(f"benchmark {entry['name']!r} requires a root")
        root_path = (manifest_path.parent / root).resolve()
        if not root_path.is_dir():
            raise ValueError(f"benchmark root does not exist: {root_path}")
        cache_dir = entry.get("cache_dir")
        results.append({
            "name": entry["name"],
            "result": run_benchmark(
                root_path,
                (manifest_path.parent / cache_dir).resolve()
                if isinstance(cache_dir, str) else None,
                int(entry.get("repeat", 1)),
            ),
        })
    return {"schema": "ansibleguard-v005-benchmark-manifest-v1", "benchmarks": results}


def validate_benchmark(
    candidate: dict, baseline: dict, max_slowdown: float = 1.25,
    max_memory_mb: float | None = None,
) -> list[str]:
    """Return deterministic gate failures without making timing a hard-coded fact.

    The baseline is intentionally explicit and belongs to the caller's
    controlled hardware/profile. Structural counters must match exactly;
    elapsed time may increase only by the configured factor.
    """
    errors = []
    if candidate.get("schema") != baseline.get("schema"):
        errors.append("benchmark schema differs from baseline")
    if candidate.get("yaml_files") != baseline.get("yaml_files"):
        errors.append("yaml file population differs from baseline")
    candidate_runs = candidate.get("runs", [])
    baseline_runs = baseline.get("runs", [])
    if not candidate_runs or not baseline_runs:
        return errors + ["benchmark data has no runs"]
    current = candidate_runs[-1].get("performance", {})
    reference = baseline_runs[-1].get("performance", {})
    for key in ("yaml_files_parsed", "yaml_parse_operations", "tasks_indexed"):
        if current.get(key) != reference.get(key):
            errors.append(f"performance counter differs: {key}")
    if current_run := candidate_runs[-1]:
        if current_run.get("semantic_index_sha256") != baseline_runs[-1].get(
            "semantic_index_sha256"
        ):
            errors.append("semantic index differs from baseline")
    baseline_seconds = float(baseline.get("min_seconds", 0.0))
    candidate_seconds = float(candidate.get("min_seconds", 0.0))
    if baseline_seconds > 0 and candidate_seconds > baseline_seconds * max_slowdown:
        errors.append(
            f"parse/index slowdown exceeds {max_slowdown:.2f}x baseline "
            f"({candidate_seconds:.6f}s > {baseline_seconds:.6f}s)"
        )
    if max_memory_mb is not None:
        peaks = [run.get("peak_memory_mb") for run in candidate_runs]
        known_peaks = [peak for peak in peaks if peak is not None]
        if known_peaks and max(known_peaks) > max_memory_mb:
            errors.append(
                f"peak memory exceeds budget ({max(known_peaks):.3f} MiB > "
                f"{max_memory_mb:.3f} MiB)"
            )
    return errors


def validate_benchmark_manifest(
    candidate: dict, baseline: dict, max_slowdown: float = 1.25,
    max_memory_mb: float | None = None,
) -> list[str]:
    """Validate named benchmark shapes independently and deterministically."""
    if candidate.get("schema") != "ansibleguard-v005-benchmark-manifest-v1":
        return ["candidate is not a benchmark manifest"]
    if baseline.get("schema") != candidate.get("schema"):
        return ["benchmark manifest schema differs from baseline"]
    candidate_items = {item.get("name"): item.get("result") for item in candidate.get("benchmarks", [])}
    baseline_items = {item.get("name"): item.get("result") for item in baseline.get("benchmarks", [])}
    if set(candidate_items) != set(baseline_items):
        return ["benchmark manifest shape names differ from baseline"]
    errors = []
    for name in sorted(candidate_items):
        errors.extend(
            f"{name}: {error}"
            for error in validate_benchmark(
                candidate_items[name], baseline_items[name], max_slowdown, max_memory_mb
            )
        )
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    parser.add_argument("--manifest", type=Path, help="named multi-shape benchmark manifest")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--json", type=Path, help="write benchmark JSON here")
    parser.add_argument("--baseline", type=Path, help="validate against benchmark JSON")
    parser.add_argument(
        "--max-slowdown", type=float, default=1.25,
        help="maximum allowed min-duration ratio against --baseline (default: 1.25)",
    )
    parser.add_argument(
        "--max-memory-mb", type=float,
        help="optional peak-RSS budget enforced with --baseline",
    )
    args = parser.parse_args(argv)
    if bool(args.root) == bool(args.manifest):
        parser.error("provide exactly one root or --manifest")
    result = (
        run_benchmark_manifest(args.manifest)
        if args.manifest else run_benchmark(args.root.resolve(), args.cache_dir, args.repeat)
    )
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    if args.baseline:
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        validator = (
            validate_benchmark_manifest
            if result.get("schema") == "ansibleguard-v005-benchmark-manifest-v1"
            else validate_benchmark
        )
        errors = validator(
            result, baseline, args.max_slowdown, args.max_memory_mb
        )
        if errors:
            for error in errors:
                print(f"benchmark gate failed: {error}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

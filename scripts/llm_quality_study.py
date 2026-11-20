#!/usr/bin/env python3
"""Frozen local LLM study, independent review, and offline participant instruments.

Never generates human labels, recruits participants, downloads models, or edits papers.
Raw inference and participant responses belong in private directories, not public artifacts.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import csv
import hashlib
import html
import itertools
import json
import math
from pathlib import Path
import random
import statistics
import sys
import tarfile
import tempfile
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import icpc_llm_evaluation as base
from ansibleguard.report import llm_explain as llm
from ansibleguard.report.llm_evidence import digest, build_packet
from ansibleguard.report.llm_runtime import write_checkpoint
from ansibleguard.symbol_index import build_repository_symbol_index

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261114
ARMS = ("ordinary", "evidence", "llm")
CONDITIONS = ("supported", "unsupported", "insufficient-evidence")
ACTIONABILITY = ("actionable", "not-actionable", "context-dependent", "not-assessed")


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    path.chmod(0o600)


def table(path, fields, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    path.chmod(0o600)


def load(path):
    return json.loads(Path(path).read_text())


def implementation():
    paths = sorted((ROOT / "src/ansibleguard").rglob("*.py"))
    paths += sorted((ROOT / "src/ansibleguard").rglob("*.csv"))
    paths += [ROOT / "pyproject.toml", Path(__file__), ROOT / "scripts/icpc_llm_evaluation.py",
              ROOT / "scripts/llm_behavior_checks.py", ROOT / "scripts/llm_participant_study.py",
              ROOT / "scripts/requested_repair.py", ROOT / "scripts/llm_v5_experiment.py",
              ROOT / "scripts/study_runtime/Dockerfile", ROOT / "docs/study/llm-quality-study-protocol.md"]
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def repair_cases():
    cases = []
    for family in ("missing-validate-certs", "credential-log-exposure"):
        for i in range(6):
            state = "eligible" if i < 4 else "already-correct" if i == 4 else "runtime-context"
            if family == "missing-validate-certs":
                value = "false" if i < 4 else "true" if i == 4 else "'{{ verify_tls }}'"
                task = {"name": f"Download internal deployment artifact {i}",
                        "ansible.builtin.get_url": {"url": "https://localhost:4443/artifact",
                        "dest": f"/tmp/artifact-{i}", "mode": "0644", "validate_certs": False}}
                intent = ("Endpoint authentication is required. The service has a correctly trusted certificate in production. "
                          "Fetching the same artifact and preserving destination/mode are required. "
                          "For unknown verify_tls, its runtime value is deliberately unavailable.")
            else:
                value = "false" if i < 4 else "true" if i == 4 else "'{{ hide_output }}'"
                task = {"name": f"Inspect synthetic deployment credential {i}",
                        "ansible.builtin.debug": {"msg": "{{ service_password }}"}, "no_log": False}
                intent = ("The task must execute and its registered result remain usable by later tasks, "
                          "but the credential must not appear in controller output, including failure output. "
                          "For unknown hide_output, its runtime value is deliberately unavailable.")
            import yaml
            source = yaml.safe_dump([task], sort_keys=False)
            if family == "missing-validate-certs":
                source = source.replace("validate_certs: false", "validate_certs: " + value)
            else:
                source = source.replace("no_log: false", "no_log: " + value)
            # Distinct leaf structures, not just renamed copies.
            if i == 1:
                source += "  tags: [deployment]\n"
            elif i == 2:
                source += "  changed_when: false\n"
            elif i == 3:
                source += "  register: deployment_result\n"
            cases.append({"case_id": f"repair-{family}-{i}", "family": family, "kind": "controlled",
                          "files": {"tasks.yml": source}, "intent": intent, "repair_stratum": state,
                          "occurrence": {"file": "tasks.yml", "line": 1, "rule_id": family,
                          "message": "Assess the flagged condition and explain whether an edit is justified. Deployment intent: " + intent},
                          "eligible_for_population_scoring": False})
    return cases


@contextmanager
def case_root(case, corpus):
    with tempfile.TemporaryDirectory(prefix="quality-source-") as temporary:
        if case["kind"] == "controlled":
            root = Path(temporary)
            for name, content in case["files"].items():
                target = (root / name).resolve()
                if not target.is_relative_to(root):
                    raise ValueError("unsafe controlled path")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
        else:
            corpus = Path(corpus).resolve()
            root = (corpus / case["repository"]).resolve()
            source = (root / case["occurrence"]["file"]).resolve()
            if root == corpus or not root.is_relative_to(corpus) or not source.is_relative_to(root):
                raise ValueError("unsafe repository path")
            if (base.git(root, "rev-parse", "HEAD") != case["sha"] or base.git(root, "status", "--porcelain")
                    or hashlib.sha256(source.read_bytes()).hexdigest() != case["source_sha256"]):
                raise ValueError("frozen source mismatch: " + case["case_id"])
        yield root


def packet_for(case, root):
    lines = (root / case["occurrence"]["file"]).read_text().splitlines()
    return build_packet(case["occurrence"], lines,
                        lambda name: (root / name).read_text().splitlines() if (root / name).is_file() else None,
                        lambda: build_repository_symbol_index(root))


def read_package(package):
    package = Path(package)
    manifest = load(package / "manifest.json")
    expected = manifest.pop("sha256")
    if digest(manifest) != expected:
        raise ValueError("study manifest checksum mismatch")
    manifest["sha256"] = expected
    return manifest


def review_identity(package, ids):
    """Bind approved per-case labels/rubrics without freezing other pending panels."""
    selected = set(ids)
    return {name: digest([row for key, row in sorted(keyed_rows(Path(package) / name, ("case_id",)).items())
                         if key[0] in selected])
            for name in ("source-reviewer-A.csv", "source-reviewer-B.csv", "source-adjudication.csv")}


def prepare(output, corpus=ROOT / "study/repositories"):
    output = Path(output)
    original = load(ROOT / "study/icpc2027-readiness-2026-11-10/evaluation/cases.json")
    if digest([original["development"], original["evaluation"]]) != original["cases_sha256"]:
        raise ValueError("original evaluation manifest checksum mismatch")
    comprehension = [case for case in base.controlled_cases("comprehension")
                     if int(case["case_id"].rsplit("-", 1)[1]) < 3]
    panels = {"explanation": original["evaluation"], "repair": repair_cases(),
              "comprehension": comprehension, "development": original["development"][:4]}
    manifest = {"version": 1, "seed": SEED, "original_cases_sha256": original["cases_sha256"],
                "panels": panels, "settings": {"model": llm.DEFAULT_MODEL, "temperature": 0.1,
                "num_ctx": llm.DEFAULT_NUM_CTX, "num_predict": llm.DEFAULT_NUM_PREDICT,
                "timeout_seconds": 120, "overall_budget_seconds": 14400},
                "human_review": "pending", "population_inference": False}
    manifest["sha256"] = digest(manifest)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    save(output / "manifest.json", manifest)
    source_ids = []
    for panel in ("explanation", "repair", "comprehension"):
        for case in panels[panel]:
            with case_root(case, corpus) as root:
                packet = packet_for(case, root)
                # Only supplied snippets and declared source, never engineering labels.
                source = {"case_id": case["case_id"], "family": case["family"],
                          "occurrence": case["occurrence"], "intent": case.get("intent"),
                          "snippets": packet.get("snippets", []), "missing": packet.get("missing", []),
                          "files": case.get("files", {case["occurrence"]["file"]:
                              (root / case["occurrence"]["file"]).read_text()})}
                save(output / "source-review" / f"{case['case_id']}.json", source)
                source_ids.append({"case_id": case["case_id"]})
    fields = ["case_id", "condition", "evidence_sufficient", "actionability", "acceptable_change",
              "condition_rubric", "evidence_rubric", "action_rubric", "notes"]
    for reviewer in ("A", "B"):
        table(output / f"source-reviewer-{reviewer}.csv", fields, source_ids)
    table(output / "source-adjudication.csv", fields, source_ids)
    permutations = list(itertools.permutations(ARMS))
    assignments = []
    for participant in range(18):
        order = permutations[participant % 6]
        tasks = []
        for block, arm in enumerate(order):
            # Three disjoint matched sets; each task is seen under every arm across schedules.
            variant = (block + participant // 6) % 3
            selected = [case for case in comprehension if case["case_id"].endswith(f"-{variant}")]
            random.Random(SEED + participant * 3 + block).shuffle(selected)
            tasks += [{"case_id": case["case_id"], "arm": arm} for case in selected]
        assignments.append({"participant_id": f"P{participant + 1:02d}", "sequence": participant % 6,
                            "tasks": tasks})
    save(output / "assignments-private.json", assignments)
    save(output / "recruitment.json", {"status": "draft-not-open", "target": 18, "minimum": 12,
         "closing_date": None, "institutional_review_determination": None, "consent_version": "1",
         "eligibility": "Adult developers with prior Ansible authoring or review experience; not gold reviewers"})
    return {"package": str(output), "panel_sizes": {k: len(v) for k, v in panels.items()}, "human_review": "pending"}


def validated_source(package, ids):
    package = Path(package)
    forms = []
    for name in ("source-reviewer-A.csv", "source-reviewer-B.csv", "source-adjudication.csv"):
        rows = keyed_rows(package / name, ("case_id",))
        for case_id in ids:
            row = rows.get((case_id,))
            if not row or row["condition"] not in CONDITIONS or row["evidence_sufficient"] not in ("yes", "no") \
                    or row["actionability"] not in ACTIONABILITY or not row["notes"].strip():
                raise ValueError(f"independent source review/adjudication incomplete: {name}: {case_id}")
        forms.append(rows)
    return {case_id: forms[-1][(case_id,)] for case_id in ids}


def freeze(package):
    package = Path(package)
    manifest = read_package(package)
    if (package / "freeze.json").exists():
        raise FileExistsError("freeze already exists; never replace an evaluated candidate")
    model = llm.llm_runtime.model_identity(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, llm._open_local, llm._local_chat_url)
    if not model:
        raise ValueError("installed local model unavailable; no download attempted")
    files = implementation()
    record = {"manifest_sha256": manifest["sha256"], "implementation": files, "model_digest": model,
              "prompt_version": llm.PROMPT_VERSION, "python": sys.version, "settings": manifest["settings"],
              "instrument_hashes": {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted((package / "source-review").glob("*.json"))},
              "assignments_sha256": hashlib.sha256((package / "assignments-private.json").read_bytes()).hexdigest()}
    record["sha256"] = digest(record)
    with tarfile.open(package / "implementation.tar.gz", "x:gz") as archive:
        for name in files:
            archive.add(ROOT / name, arcname=name)
    save(package / "freeze.json", record)
    return record


def schedule(cases, paired, seed=SEED):
    ordered = sorted(cases, key=lambda case: case["case_id"])
    random.Random(seed).shuffle(ordered)
    return [(case, mode) for i, case in enumerate(ordered)
            for mode in (("window", "scoped") if i % 2 == 0 else ("scoped", "window"))] if paired \
        else [(case, "scoped") for case in ordered]


def run(package, output, panel, corpus=ROOT / "study/repositories", resume=False):
    package, output = Path(package), Path(output)
    manifest, frozen = read_package(package), load(package / "freeze.json")
    check = dict(frozen)
    if digest({k: v for k, v in check.items() if k != "sha256"}) != check["sha256"]:
        raise ValueError("freeze checksum mismatch")
    if frozen["implementation"] != implementation() or frozen["manifest_sha256"] != manifest["sha256"]:
        raise ValueError("frozen implementation or manifest changed")
    if any(hashlib.sha256((package / name).read_bytes()).hexdigest() != value
           for name, value in frozen["instrument_hashes"].items()) \
            or hashlib.sha256((package / "assignments-private.json").read_bytes()).hexdigest() != frozen["assignments_sha256"]:
        raise ValueError("frozen source packets or participant assignments changed")
    model = llm.llm_runtime.model_identity(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, llm._open_local, llm._local_chat_url)
    if model != frozen["model_digest"]:
        raise ValueError("frozen model unavailable or changed")
    cases = manifest["panels"][panel]
    if panel in ("repair", "comprehension"):
        validated_source(package, [case["case_id"] for case in cases])
    # Preflight every source before any inference.
    for case in cases:
        with case_root(case, corpus):
            pass
    entries = schedule(cases, panel in ("explanation", "development"))
    identity = {"freeze_sha256": frozen["sha256"], "panel": panel,
                "schedule": [[case["case_id"], mode] for case, mode in entries]}
    if panel in ("repair", "comprehension"):
        identity["source_review_sha256"] = review_identity(package, [case["case_id"] for case in cases])
    if resume:
        progress = load(output / "run-manifest.json")
        if any(progress.get(k) != v for k, v in identity.items()):
            raise ValueError("resume identity mismatch")
        interrupted = progress.get("in_flight")
        if interrupted and not (output / f"{interrupted['key']}.json").exists():
            write_checkpoint(output, interrupted["key"], {**identity,
                "case_id": interrupted["case_id"], "mode": interrupted["mode"],
                "result": {"llm_status": "interrupted-unknown"}, "telemetry": {},
                "wall_seconds": None, "freeze_sha256": frozen["sha256"]})
            progress["elapsed_seconds"] += min(120, max(0, time.time() - interrupted["began_unix"]))
    else:
        output.mkdir(parents=True, exist_ok=False, mode=0o700)
        progress = {**identity, "elapsed_seconds": 0, "status": "in-progress", "completed": 0}
        write_checkpoint(output, "run-manifest", progress)
    started, previous = time.monotonic(), progress["elapsed_seconds"]
    for case, mode in entries:
        key = case["case_id"] + "-" + mode
        target = output / f"{key}.json"
        if target.exists():
            record = load(target)
            if record.get("freeze_sha256") != frozen["sha256"] or record.get("case_id") != case["case_id"] \
                    or record.get("mode") != mode:
                raise ValueError("existing attempt identity mismatch")
            continue  # Includes failures; never retry for a better result.
        remaining = manifest["settings"]["overall_budget_seconds"] - previous - (time.monotonic() - started)
        telemetry = {}
        began = time.monotonic()
        with case_root(case, corpus) as root:
            progress["in_flight"] = {"key": key, "case_id": case["case_id"], "mode": mode, "began_unix": time.time()}
            write_checkpoint(output, "run-manifest", progress)
            token = llm._CALL_RECORD.set(telemetry)
            try:
                if remaining <= 0:
                    result = {"llm_status": "budget-exhausted"}
                else:
                    result = llm.explain_occurrence(case["occurrence"], root, evidence_mode=mode,
                                                   timeout=min(120, remaining),
                                                   explanation_style=manifest["settings"].get("explanation_style", "free"))
            except Exception as exc:
                # Persist unexpected failures; interrupts still stop and resume explicitly.
                result = {"llm_status": "runner-error", "llm_error": f"{type(exc).__name__}: {exc}"}
            finally:
                llm._CALL_RECORD.reset(token)
            record = {**identity, "case_id": case["case_id"], "mode": mode, "result": result,
                      "wall_seconds": time.monotonic() - began, "telemetry": telemetry,
                      "source_sha256": digest(case.get("files", case.get("source_sha256"))),
                      "freeze_sha256": frozen["sha256"]}
        write_checkpoint(output, key, record)
        progress.update(elapsed_seconds=previous + time.monotonic() - started,
                        completed=sum((output / f"{c['case_id']}-{m}.json").exists() for c, m in entries), in_flight=None)
        write_checkpoint(output, "run-manifest", progress)
        print(json.dumps({"case_id": case["case_id"], "mode": mode, "status": result["llm_status"]}), flush=True)
    progress["status"] = "completed"
    write_checkpoint(output, "run-manifest", progress)
    return progress


def keyed_rows(path, keys):
    result = {}
    with Path(path).open(newline="") as stream:
        for row in csv.DictReader(stream):
            key = tuple(row.get(k, "") for k in keys)
            if not all(key) or key in result:
                raise ValueError("missing or duplicate key: " + str(path))
            result[key] = row
    return result


def records_for(package, run_dir):
    manifest, frozen = read_package(package), load(Path(package) / "freeze.json")
    run_dir = Path(run_dir)
    progress = load(run_dir / "run-manifest.json")
    if progress["freeze_sha256"] != frozen["sha256"] or progress["status"] != "completed":
        raise ValueError("completed frozen run required")
    cases = {case["case_id"]: case for case in manifest["panels"][progress["panel"]]}
    expected = [(case["case_id"], mode) for case, mode in schedule(list(cases.values()),
                progress["panel"] in ("explanation", "development"))]
    if progress["schedule"] != [list(pair) for pair in expected]:
        raise ValueError("run schedule differs from frozen panel")
    records = []
    for case_id, mode in expected:
        record = load(run_dir / f"{case_id}-{mode}.json")
        if record["freeze_sha256"] != frozen["sha256"] or (record["case_id"], record["mode"]) != (case_id, mode):
            raise ValueError("attempt identity mismatch")
        records.append(record)
    return cases, records


def export_review(package, run_dir, output):
    package, output = Path(package), Path(output)
    cases, records = records_for(package, run_dir)
    validated_source(package, list(cases))  # Never expose answers before independent source review.
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    random.Random(SEED + 1).shuffle(records)
    mapping, rows = [], []
    for i, record in enumerate(records):
        opaque = f"O{i + 1:03d}"
        mapping.append({"output_id": opaque, "case_id": record["case_id"], "mode": record["mode"]})
        source = load(package / "source-review" / f"{record['case_id']}.json")
        # Include the exact model input, not additional material represented as supplied evidence.
        save(output / "packets" / f"{opaque}.json", {"output_id": opaque,
             "source": source, "supplied_input": record["telemetry"].get("user_prompt"),
             "delivered_output": {k: v for k, v in record["result"].items()
                if k in ("llm_status", "llm_assessment", "llm_actionability", "llm_evidence",
                         "llm_explanation", "llm_why_in_this_context", "llm_limitations",
                         "llm_fixed_code_snippet", "llm_suggested_fix", "llm_missing_evidence")}})
        rows.append({"output_id": opaque})
    save(output / "mapping-private.json", mapping)
    fields = ["output_id", "factually_correct", "evidence_supported", "contradiction", "assessment_correct",
              "uncertainty_appropriate", "fix_judgment", "notes"]
    for name in ("reviewer-A", "reviewer-B", "adjudication"):
        table(output / f"{name}.csv", fields, rows)
    return {"outputs": len(records), "warning": "Give reviewers packets and their own form ONLY; retain mapping privately."}


def diagnostics(package, run_dir, output):
    cases, records = records_for(package, run_dir)
    rows = []
    for record in records:
        result = record["result"]
        packet = result.get("llm_evidence_packet") or record["telemetry"].get("evidence_packet") or {}
        try:
            raw = json.loads(record["telemetry"].get("raw_response", "{}"))
        except (ValueError, TypeError):
            raw = {}
        rows.append({"case_id": record["case_id"], "mode": record["mode"],
                     "kind": cases[record["case_id"]]["kind"], "status": result["llm_status"],
                     "assessment": result.get("llm_assessment"), "wall_seconds": record["wall_seconds"],
                     "required_abstention": bool(packet.get("missing")),
                     "backend_predicate": (packet.get("predicate_check") or {}).get("status") == "verified",
                     "raw_fix_proposed": bool(raw.get("fixed_code_snippet")) if isinstance(raw, dict) else False,
                     "returned_fix": bool(result.get("llm_fixed_code_snippet")),
                     "suggestion_validation": result.get("llm_suggestion_validation"),
                     "tokens": result.get("llm_token_usage") or record["telemetry"].get("token_usage")})
    result = {"scheduled": len(rows), "human_quality": "pending independent review", "rows": rows}
    save(output, result)
    return {"scheduled": len(rows), "statuses": dict(Counter(row["status"] for row in rows)),
            "returned_fixes": sum(row["returned_fix"] for row in rows), "human_quality": result["human_quality"]}


def quality_summary(package, run_dir, review, output):
    cases, records = records_for(package, run_dir)
    source_gold = validated_source(package, list(cases))
    mapping = load(Path(review) / "mapping-private.json")
    by_pair = {(r["case_id"], r["mode"]): r for r in records}
    if len(mapping) != len(records) or {(r["case_id"], r["mode"]) for r in mapping} != set(by_pair) \
            or len({r["output_id"] for r in mapping}) != len(mapping):
        raise ValueError("review mapping incomplete or duplicated")
    forms = [keyed_rows(Path(review) / f"{name}.csv", ("output_id",))
             for name in ("reviewer-A", "reviewer-B", "adjudication")]
    fields = ("factually_correct", "evidence_supported", "contradiction", "assessment_correct", "uncertainty_appropriate")
    rows, agreements = [], Counter()
    for entry in mapping:
        record = by_pair[entry["case_id"], entry["mode"]]
        judged = []
        for form in forms:
            row = form.get((entry["output_id"],))
            if not row or any(row[f] not in ("yes", "no", "not-assessable") for f in fields) \
                    or row["fix_judgment"] not in ("correct", "wrong-or-harmful", "indeterminate", "not-proposed") \
                    or not row["notes"].strip():
                raise ValueError("independent output review/adjudication incomplete")
            proposed = bool(record["result"].get("llm_fixed_code_snippet"))
            if proposed == (row["fix_judgment"] == "not-proposed"):
                raise ValueError("fix review disagrees with delivered suggestion availability")
            judged.append(row)
        for field in fields:
            agreements[field] += judged[0][field] == judged[1][field]
        final = judged[-1]
        expected = source_gold[entry["case_id"]]["condition"]
        available = record["result"]["llm_status"] == "ok"
        assessment_correct = available and record["result"].get("llm_assessment") == expected
        if available and (final["assessment_correct"] == "yes") != assessment_correct:
            raise ValueError("output adjudication contradicts independently adjudicated source condition")
        success = record["result"]["llm_status"] == "ok" and all(final[f] == "yes" for f in
                  ("factually_correct", "evidence_supported", "assessment_correct", "uncertainty_appropriate")) \
                  and final["contradiction"] == "no"
        rows.append({**entry, "kind": cases[entry["case_id"]]["kind"], "success": success,
                     "status": record["result"]["llm_status"], **{f: final[f] for f in fields},
                     "source_condition": expected, "returned_assessment": record["result"].get("llm_assessment"),
                     "evidence_sufficient": source_gold[entry["case_id"]]["evidence_sufficient"],
                     "fix_judgment": final["fix_judgment"]})
    groups = {}
    for kind in ("all", "controlled", "real"):
        for mode in sorted({row["mode"] for row in rows}):
            selected = [r for r in rows if r["mode"] == mode and
                        (kind == "all" or ("controlled" if r["kind"] == "controlled" else "real") == kind)]
            groups[f"{kind}/{mode}"] = {"scheduled": len(selected), "successful": sum(r["success"] for r in selected),
                "success_rate": sum(r["success"] for r in selected) / len(selected) if selected else None,
                "false_confirmations": sum(r["source_condition"] == "unsupported" and r["returned_assessment"] == "supported" for r in selected),
                "false_dismissals": sum(r["source_condition"] == "supported" and r["returned_assessment"] == "unsupported" for r in selected),
                "sufficient_context_abstentions": sum(r["evidence_sufficient"] == "yes" and r["returned_assessment"] == "insufficient-evidence" for r in selected),
                "failures": sum(r["status"] != "ok" for r in selected)}
    paired = Counter()
    for case_id in cases:
        outcomes = {r["mode"]: r["success"] for r in rows if r["case_id"] == case_id}
        if set(outcomes) == {"window", "scoped"}:
            paired[f"window={outcomes['window']},scoped={outcomes['scoped']}"] += 1
    differences = {}
    for kind in ("all", "controlled", "real"):
        window, scoped = groups.get(f"{kind}/window", {}).get("success_rate"), groups.get(f"{kind}/scoped", {}).get("success_rate")
        differences[kind] = 100 * (scoped - window) if window is not None and scoped is not None else None
    save(output, {"groups": groups, "paired_counts": dict(paired), "percentage_point_difference_scoped_minus_window": differences,
         "source_review_sha256": review_identity(package, list(cases)), "reviewer_agreement":
         {f: agreements[f] / len(rows) for f in fields}, "fix_judgments": dict(Counter(r["fix_judgment"] for r in rows)),
         "rows": rows, "interpretation": "Descriptive convenience/challenge case study; no population or developer benefit claim."})
    return {"reviewed_outputs": len(rows), "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--corpus", type=Path, default=ROOT / "study/repositories")
    for command in ("freeze", "run", "export-review", "diagnostics", "summarize", "participant-pages", "participant-import", "participant-summarize"):
        child = sub.add_parser(command)
        child.add_argument("--package", type=Path, required=True)
        if command in ("run", "export-review", "diagnostics", "summarize", "participant-pages"):
            child.add_argument("--run", type=Path, required=True)
        if command != "freeze":
            child.add_argument("--output", type=Path, required=True)
        if command == "run":
            child.add_argument("--panel", choices=("development", "explanation", "repair", "comprehension"), required=True)
            child.add_argument("--corpus", type=Path, default=ROOT / "study/repositories")
            child.add_argument("--resume", action="store_true")
        if command == "summarize":
            child.add_argument("--review", type=Path, required=True)
        if command == "participant-import":
            child.add_argument("--responses", type=Path, nargs="+", required=True)
            child.add_argument("--allow-partial", action="store_true")
        if command == "participant-summarize":
            child.add_argument("--responses", type=Path, required=True)
            child.add_argument("--grades", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.output, args.corpus)
    elif args.command == "freeze":
        result = freeze(args.package)
    elif args.command == "run":
        result = run(args.package, args.run, args.panel, args.corpus, args.resume)
        save(args.output, result)
    elif args.command == "export-review":
        result = export_review(args.package, args.run, args.output)
    elif args.command == "diagnostics":
        result = diagnostics(args.package, args.run, args.output)
    elif args.command == "summarize":
        result = quality_summary(args.package, args.run, args.review, args.output)
    else:
        from scripts import llm_participant_study as participants
        if args.command == "participant-pages":
            result = participants.pages(args.package, args.run, args.output)
        elif args.command == "participant-import":
            result = participants.import_responses(args.package, args.responses, args.output, args.allow_partial)
        else:
            result = participants.summarize(args.package, args.responses, args.grades, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

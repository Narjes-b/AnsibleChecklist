#!/usr/bin/env python3
"""Prepare blinded case-review forms and run a paired, local-only evaluation.

Controlled expectations are development diagnostics, never human gold labels.
Real examples are convenience-selected detector output, not a probability sample.
This command never downloads a model or modifies corpus checkouts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ansibleguard.report import llm_explain as llm
from ansibleguard.report.llm_evidence import digest
from ansibleguard.report.llm_runtime import write_checkpoint


RULES = ("missing-validate-certs", "insecure-permissions", "credential-log-exposure", "unguarded-variable")


def controlled_cases(panel):
    """Six explicit mechanisms per family, with separate dev/evaluation names."""
    cases = []
    for rule in RULES:
        for number in range(6):
            name = f"{panel}_{number}"
            occurrence = {"file": "tasks.yml", "line": 1, "rule_id": rule}
            files = {}
            if rule == "missing-validate-certs":
                value = ("false", "true", "'{{ verify_tls }}'", "false", "true", "'{{ verify_tls }}'")[number]
                source = f"- name: Fetch {name}\n  ansible.builtin.get_url:\n    url: https://example.invalid/{name}\n    dest: /tmp/{name}\n    mode: '0644'\n    validate_certs: {value}\n"
                expectation = ("supported", "unsupported", "insufficient-evidence")[number % 3]
                occurrence["message"] = "This task explicitly disables TLS certificate verification."
            elif rule == "insecure-permissions":
                mode = ("'0777'", "'0644'", "'{{ desired_mode }}'", "'2777'", "'2775'", "'{{ desired_mode }}'")[number]
                source = f"- name: Manage {name}\n  ansible.builtin.file:\n    path: /srv/{name}\n    state: {'directory' if number >= 3 else 'touch'}\n    group: developers\n    mode: {mode}\n"
                expectation = ("supported", "unsupported", "insufficient-evidence")[number % 3]
                occurrence["message"] = "This task grants unsafe permission bits."
            elif rule == "credential-log-exposure":
                value = ("false", "true", "'{{ hide_output }}'", "false", "true", "'{{ hide_output }}'")[number]
                source = f"- name: Show {name}\n  ansible.builtin.debug:\n    msg: '{{{{ service_password }}}}'\n  no_log: {value}\n"
                expectation = ("supported", "unsupported", "insufficient-evidence")[number % 3]
                occurrence["message"] = "This task displays a sensitive variable without effective no_log protection."
                if number >= 3:
                    source = "- name: Inherited logging control\n  no_log: " + value + "\n  block:\n" + "\n".join("    " + line for line in source.splitlines()[:3]) + "\n"
                    occurrence["line"] = 4
            else:
                source = f"- name: Show {name}\n  ansible.builtin.debug:\n    msg: '{{{{ ServicePort }}}}'\n"
                occurrence.update(line=3, semantic_subject="variable:ServicePort",
                                  message="Variable 'ServicePort' has no visible definition or runtime input contract.")
                expectation = "insufficient-evidence"
                if number in {1, 4}:
                    source += "  vars:\n    ServicePort: 8080\n"
                    expectation = "unsupported"
                if number in {2, 5}:
                    files["roles/unrelated/defaults/main.yml"] = "ServicePort: 9090\n"
            if number == 3 and rule == "missing-validate-certs":
                source += "  tags:\n" + "".join(f"    - diagnostic_{i}\n" for i in range(20)) + "  when: feature_enabled\n"
            if panel == "evaluation":
                # Exercise related mechanisms with different source structures;
                # these remain controlled challenges, not independent natural data.
                if rule == "missing-validate-certs":
                    source = source.replace("  ansible.builtin.get_url:", "  action:\n    module: ansible.builtin.get_url")
                elif rule == "insecure-permissions":
                    source = "- name: Permission wrapper\n  tags: [permissions]\n  block:\n" + "\n".join("    " + line for line in source.splitlines()) + "\n"
                    occurrence["line"] = 4
                elif rule == "credential-log-exposure" and number < 3:
                    source = "- name: Logging wrapper\n  tags: [logging]\n  block:\n" + "\n".join("    " + line for line in source.splitlines()) + "\n"
                    occurrence["line"] = 4
                elif rule == "unguarded-variable" and number in {1, 4}:
                    source = "- name: Produce runtime value\n  ansible.builtin.set_fact:\n    ServicePort: 8080\n" + source.split("  vars:", 1)[0]
                    occurrence["line"] = 6
            files["tasks.yml"] = source
            cases.append({"case_id": f"{panel}-{rule}-{number}", "family": rule,
                          "kind": "controlled", "files": files, "occurrence": occurrence,
                          "engineering_expectation": expectation, "eligible_for_population_scoring": False})
    return cases


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, check=True, timeout=30).stdout.strip()


def real_cases(root):
    from ansibleguard.detectors.missing_validate_certs import detect_missing_validate_certs
    from ansibleguard.detectors.review_checklist import detect_insecure_permissions
    from ansibleguard.detectors.credentials_leaking_in_log import detect_credentials_leaking_in_log
    from ansibleguard.detectors.paper_candidates import detect_unguarded_variables
    with (root / "study/manifests/github-v2-final-eligible.csv").open() as stream:
        population = sorted(csv.DictReader(stream), key=lambda row: row["project"])
    with (root / "study/validation-v007-human/splits/repository-split.csv").open() as stream:
        calibration = {row["repository"] for row in csv.DictReader(stream) if row["split"] == "calibration"}
    detectors = (detect_missing_validate_certs, detect_insecure_permissions,
                 detect_credentials_leaking_in_log, detect_unguarded_variables)
    counts, cases, ledger = Counter(), [], []
    for row in population:
        repository, sha = row["project"], row["commit_sha"]
        if repository not in calibration:
            continue
        source_root = root / "study/repositories" / repository
        record = {"repository": repository, "sha": sha, "selected": 0}
        ledger.append(record)
        try:
            if git(source_root, "rev-parse", "HEAD") != sha or git(source_root, "status", "--porcelain"):
                record["exclusion"] = "checkout is not clean at the frozen SHA"
                continue
            names = git(source_root, "ls-files").splitlines()
        except (subprocess.SubprocessError, OSError):
            record["exclusion"] = "frozen checkout unavailable"
            continue
        per_repo = Counter()
        for name in names:
            path = source_root / name
            if (not name.endswith((".yml", ".yaml")) or path.is_symlink()
                    or any(part in {"test", "tests", "molecule", ".github", "templates"} for part in Path(name).parts)
                    or not any(part in {"tasks", "handlers", "playbooks"} for part in Path(name).parts)
                    or not path.is_file() or path.stat().st_size > 1024 * 1024):
                continue
            for rule, detector in zip(RULES, detectors):
                if counts[rule] >= 6 or per_repo[rule] >= 2:
                    continue
                try:
                    result = detector(path)
                    details = result[-1]
                except Exception as exc:
                    record.setdefault("detector_errors", []).append(type(exc).__name__)
                    continue
                for detail in details:
                    if counts[rule] >= 6 or per_repo[rule] >= 2:
                        break
                    occurrence = {"file": name, "line": detail.get("line", 1), "rule_id": rule,
                                  "message": detail.get("message") or detail.get("issue") or rule}
                    if detail.get("variable"):
                        occurrence["semantic_subject"] = "variable:" + detail["variable"]
                    cases.append({"case_id": f"real-{rule}-{counts[rule]}", "family": rule, "kind": "real",
                        "repository": repository, "sha": sha,
                        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "occurrence": occurrence,
                        "exposure": "previous calibration corpus; not independent population evaluation",
                        "eligible_for_population_scoring": False})
                    counts[rule] += 1
                    per_repo[rule] += 1
                    record["selected"] += 1
        if all(counts[rule] == 6 for rule in RULES):
            break
    return cases, ledger


def prepare(root, output):
    output.mkdir(parents=True, exist_ok=False)
    natural, ledger = real_cases(root)
    development, evaluation = controlled_cases("development"), controlled_cases("evaluation") + natural
    manifest = {"version": 1, "purpose": "bounded tool-case evaluation; no population accuracy claim",
                "development": development, "evaluation": evaluation, "selection_ledger": ledger,
                "natural_counts": dict(Counter(case["family"] for case in natural)),
                "evaluation_complete": len(natural) == 24, "human_review": "pending"}
    manifest["cases_sha256"] = digest([development, evaluation])
    (output / "cases.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for reviewer in ("A", "B"):
        with (output / f"reviewer-{reviewer}.csv").open("w", newline="") as stream:
            fields = ["case_id", "condition", "evidence_sufficient", "actionability", "notes"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows({"case_id": case["case_id"]} for case in evaluation)
        with (output / f"output-reviewer-{reviewer}.csv").open("w", newline="") as stream:
            fields = ["case_id", "mode", "explanation_entailed", "assessment_correct", "harmful_or_wrong_fix", "notes"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows({"case_id": case["case_id"], "mode": mode}
                             for case in evaluation for mode in ("window", "scoped"))
    with (output / "adjudication.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["case_id", "reviewer_a", "reviewer_b", "adjudicated_condition", "reason"])
        writer.writeheader()
        writer.writerows({"case_id": case["case_id"]} for case in evaluation)
    (output / "REVIEW.md").write_text(
        "# Independent source review\n\nReview the frozen source before seeing model answers. "
        "Use condition supported / unsupported / insufficient-evidence, evidence_sufficient yes / no, "
        "and actionability actionable / not-actionable / context-dependent / not-assessed. "
        "Do not use engineering_expectation as a human label. Reviewer A and B work independently; "
        "preserve both forms and adjudicate disagreements in a separate file.\n\n"
        "Real examples come from previously exposed calibration repositories. The convenience selection "
        "does not estimate population precision, recall, or developer benefit. After source review, "
        "separately judge explanation entailment and harmful/wrong suggestions for each model output.\n")
    return manifest


def run(manifest_path, output, panel, timeout, budget, corpus_root=None):
    if not all(math.isfinite(value) and value > 0 for value in (timeout, budget)):
        raise ValueError("timeout and budget must be positive finite seconds")
    corpus_root = (corpus_root or Path(__file__).resolve().parents[1] / "study/repositories").resolve()
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("cases_sha256") != digest([manifest["development"], manifest["evaluation"]]):
        raise ValueError("case manifest checksum mismatch")
    model_digest = llm.llm_runtime.model_identity(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, llm._open_local, llm._local_chat_url)
    if not model_digest:
        raise ValueError("local model not installed; this command never downloads it")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    records = []
    pending = [case["case_id"] + "-" + mode for case in manifest[panel] for mode in ("window", "scoped")]
    progress = {"key": "run-manifest", "status": "in-progress", "panel": panel,
                "pending": pending.copy(), "completed": 0, "model_digest": model_digest,
                "cases_sha256": manifest["cases_sha256"], "python": sys.version,
                "timeout_seconds": timeout, "overall_budget_seconds": budget,
                "generation_settings": {"num_ctx": llm.DEFAULT_NUM_CTX, "num_predict": llm.DEFAULT_NUM_PREDICT, "temperature": 0.1},
                "implementation_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in [Path(__file__), Path(llm.__file__), Path(llm.__file__).with_name("llm_evidence.py"),
                                 Path(llm.__file__).with_name("llm_suggestions.py")]}}
    write_checkpoint(output, "run-manifest", progress)
    for case in manifest[panel]:
        with tempfile.TemporaryDirectory(prefix="ansibleguard-evaluation-") as temporary:
            root = Path(temporary) if case["kind"] == "controlled" else (corpus_root / case["repository"]).resolve()
            if case["kind"] == "controlled":
                for name, content in case["files"].items():
                    path = root / name
                    if not path.resolve().is_relative_to(root.resolve()):
                        raise ValueError("unsafe controlled source path")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
            else:
                if root == corpus_root or not root.is_relative_to(corpus_root):
                    raise ValueError("unsafe real repository path")
                source_file = (root / case["occurrence"]["file"]).resolve()
                if not source_file.is_relative_to(root):
                    raise ValueError("unsafe real source file path")
                if (git(root, "rev-parse", "HEAD") != case["sha"] or git(root, "status", "--porcelain")
                    or hashlib.sha256(source_file.read_bytes()).hexdigest() != case["source_sha256"]):
                    raise ValueError("real source no longer matches frozen case identity")
            for mode in ("window", "scoped"):
                record = {}
                token = llm._CALL_RECORD.set(record)
                try:
                    remaining = budget - (time.monotonic() - started)
                    result = ({"llm_status": "budget-exhausted"} if remaining <= 0 else
                        llm.explain_occurrence(case["occurrence"], root, timeout=min(timeout, remaining), evidence_mode=mode))
                finally:
                    llm._CALL_RECORD.reset(token)
                payload = {"case_id": case["case_id"], "family": case["family"], "mode": mode,
                           "model_digest": model_digest, "prompt_version": llm.PROMPT_VERSION,
                           "cases_sha256": manifest["cases_sha256"], "result": result, **record}
                write_checkpoint(output, case["case_id"] + "-" + mode, payload)
                records.append(payload)
                progress["pending"].remove(case["case_id"] + "-" + mode)
                progress["completed"] = len(records)
                write_checkpoint(output, "run-manifest", progress)
                print(json.dumps({"case_id": case["case_id"], "mode": mode, "status": result["llm_status"]}), flush=True)
    summary = {"model_digest": model_digest, "cases_sha256": manifest["cases_sha256"], "panel": panel,
               "counts": {mode: dict(Counter(row["result"]["llm_status"] for row in records if row["mode"] == mode)) for mode in ("window", "scoped")},
               "duration_seconds": round(time.monotonic() - started, 2), "human_quality_results": "pending independent review"}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    progress["status"] = "completed"
    write_checkpoint(output, "run-manifest", progress)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    prep.add_argument("--output", type=Path, required=True)
    execute = sub.add_parser("run")
    execute.add_argument("--manifest", type=Path, required=True)
    execute.add_argument("--output", type=Path, required=True)
    execute.add_argument("--panel", choices=("development", "evaluation"), default="development")
    execute.add_argument("--timeout", type=float, default=120)
    execute.add_argument("--budget", type=float, default=3600)
    execute.add_argument("--corpus-root", type=Path, help="Directory containing owner/repository frozen checkouts")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.root.resolve(), args.output)
        print(json.dumps({"development": len(result["development"]), "evaluation": len(result["evaluation"]),
                          "natural_counts": result["natural_counts"], "evaluation_complete": result["evaluation_complete"]}))
    else:
        if not all(math.isfinite(value) and value > 0 for value in (args.timeout, args.budget)):
            parser.error("timeout and budget must be positive finite seconds")
        print(json.dumps(run(args.manifest, args.output, args.panel, args.timeout, args.budget, args.corpus_root)))


if __name__ == "__main__":
    main()

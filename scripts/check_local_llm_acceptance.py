#!/usr/bin/env python3
"""Record production-path local LLM behavior on explicit synthetic contracts.

These engineering expectations are not human labels or population accuracy.
One attempt per case; no retry/selection of favorable answers. Actual prompts,
raw model text and per-case results are persisted for review.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch
import urllib.request

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ansibleguard.report import llm_explain as llm
from scripts.sample_partitioned_occurrences import sha256


TLS_SOURCE = """- name: Download artifact
  ansible.builtin.get_url:
    url: https://example.invalid/artifact
    dest: /tmp/artifact
    validate_certs: {value}
"""
CASES = [
    {"case_id": "explicit-false", "source": TLS_SOURCE.replace("{value}", "false"), "line": 5,
     "rule_id": "missing-validate-certs", "finding_category": "security",
     "message": "This task explicitly sets validate_certs: false.", "expected_assessment": "supported"},
    {"case_id": "contradicted-boolean", "source": TLS_SOURCE.replace("{value}", "true"), "line": 5,
     "rule_id": "missing-validate-certs", "finding_category": "security",
     "message": "This task explicitly sets validate_certs: false.", "expected_assessment": "unsupported"},
    {"case_id": "missing-runtime-input", "source": '- name: Show inventory setting\n  ansible.builtin.debug:\n    msg: "{{ inventory_service_port }}"\n',
     "line": 3, "rule_id": "unguarded-variable", "finding_category": "correctness",
     "semantic_subject": "variable:inventory_service_port",
     "message": "Variable 'inventory_service_port' is undefined. No inventory or runtime input contract is provided in this evidence.",
     "expected_assessment": "insufficient-evidence"},
    {"case_id": "invalid-anchor", "source": "- ansible.builtin.debug: {msg: hello}\n", "line": 999,
     "rule_id": "example", "finding_category": "correctness", "message": "Stale source anchor.",
     "expected_status": "insufficient-context"},
]


def write_json(path, value):
    data = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(data, encoding="utf-8")
    temporary.replace(path)


def local_model_identity(host, model):
    url = llm._local_chat_url(host).removesuffix("/api/chat") + "/api/tags"
    with llm._open_local(urllib.request.Request(url), timeout=5) as response:
        raw = response.read(llm.MAX_ENVELOPE_BYTES + 1)
    if len(raw) > llm.MAX_ENVELOPE_BYTES:
        raise ValueError("local model inventory exceeds limit")
    matches = [item for item in json.loads(raw).get("models", []) if item.get("name") == model]
    if len(matches) != 1 or not matches[0].get("digest"):
        raise ValueError("requested model is not installed locally with an identifiable digest")
    return {key: matches[0].get(key) for key in ("name", "digest", "size", "details")}


def run_cases(output, *, model, host, timeout, budget, model_identity, cases=CASES):
    if timeout <= 0 or budget <= 0:
        raise ValueError("timeout and total budget must be positive")
    llm._local_chat_url(host)
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"purpose": "synthetic contract acceptance; not human labels or measured real-project accuracy",
                "eligible_for_performance_scoring": False, "started_utc": datetime.now(timezone.utc).isoformat(),
                "status": "running", "case_count": len(cases), "completed_cases": 0, "model_calls": 0,
                "pending_case_ids": [case["case_id"] for case in cases],
                "model": model_identity, "response_schema_version": llm.RESPONSE_SCHEMA_VERSION,
                "prompt_version": llm.PROMPT_VERSION, "timeout_per_call": timeout, "overall_budget_seconds": budget,
                "generation_options": {"num_ctx": llm.DEFAULT_NUM_CTX, "num_predict": llm.DEFAULT_NUM_PREDICT, "temperature": 0.1},
                "implementation_sha256": sha256(Path(__file__)), "backend_sha256": sha256(Path(llm.__file__)),
                "system_prompt_sha256": hashlib.sha256(llm.SYSTEM_PROMPT.encode()).hexdigest(),
                "response_schema_sha256": hashlib.sha256(json.dumps(llm.RESPONSE_SCHEMA, sort_keys=True).encode()).hexdigest(),
                "generation_schema_sha256": hashlib.sha256(json.dumps(llm.GENERATION_SCHEMA, sort_keys=True).encode()).hexdigest(),
                "cases_sha256": hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest(),
                "attempts_per_case": 1, "output_sha256": {}}
    records, original_call = [], llm._call_ollama
    start = time.monotonic()
    write_json(output / "acceptance-manifest.json", manifest)
    try:
        for case in cases:
            calls = []
            remaining = budget - (time.monotonic() - start)
            with tempfile.TemporaryDirectory(prefix="ansibleguard-synthetic-") as root:
                root = Path(root)
                (root / "tasks.yml").write_text(case["source"], encoding="utf-8")
                occurrence = {key: value for key, value in case.items()
                              if key in {"line", "rule_id", "finding_category", "message", "semantic_subject"}}
                occurrence["file"] = "tasks.yml"

                def capture(host, model, system, user, call_timeout):
                    raw, duration, error = original_call(host, model, system, user, call_timeout)
                    calls.append({"system_prompt": system, "user_prompt": user,
                                  "raw_response": raw, "duration_seconds": duration, "transport_error": error,
                                  "generation_schema_sha256": (llm._CALL_RECORD.get() or {}).get("generation_schema_sha256")})
                    return raw, duration, error

                if remaining <= 0:
                    result = {"llm_status": "budget-exhausted"}
                else:
                    # A separate single-threaded diagnostic process observes
                    # the real production call without changing its behavior.
                    with patch.object(llm, "_call_ollama", capture):
                        result = llm.explain_occurrence(occurrence, root, model=model, host=host,
                                                        timeout=min(timeout, remaining))
            expected_status = case.get("expected_status", "ok")
            matches = result["llm_status"] == expected_status and (
                "expected_assessment" not in case or result.get("llm_assessment") == case["expected_assessment"])
            # The anchor gate must abstain without even making a model request.
            if case.get("expected_status") == "insufficient-context":
                matches = matches and not calls
            record = {"case": case, "occurrence": occurrence, "result": result,
                      "model_calls": len(calls), "call_records": calls, "contract_expectation_met": matches}
            records.append(record)
            name = case["case_id"] + ".json"
            write_json(output / name, record)
            manifest["output_sha256"][name] = sha256(output / name)
            manifest.update(completed_cases=len(records), model_calls=sum(r["model_calls"] for r in records),
                            pending_case_ids=[item["case_id"] for item in cases[len(records):]],
                            expectation_matches=sum(r["contract_expectation_met"] for r in records),
                            status_counts=dict(Counter(r["result"]["llm_status"] for r in records)))
            write_json(output / "acceptance-manifest.json", manifest)
            print(json.dumps({"case": case["case_id"], "status": result["llm_status"],
                              "assessment": result.get("llm_assessment"), "expectation_met": matches}), flush=True)
    finally:
        manifest["status"] = "completed" if len(records) == len(cases) else "interrupted"
        manifest["duration_seconds"] = round(time.monotonic() - start, 3)
        write_json(output / "acceptance-manifest.json", manifest)
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", default=llm.DEFAULT_HOST)
    parser.add_argument("--model", default=llm.DEFAULT_MODEL)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--budget", type=float, default=180)
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("output exists; use a new diagnostic directory")
    identity = local_model_identity(args.host, args.model)
    records = run_cases(args.output, model=args.model, host=args.host, timeout=args.timeout,
                        budget=args.budget, model_identity=identity)
    after = local_model_identity(args.host, args.model)
    manifest_path = args.output / "acceptance-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["model_identity_after"] = after
    manifest["model_digest_stable"] = identity["digest"] == after["digest"]
    write_json(manifest_path, manifest)
    return 0 if all(r["contract_expectation_met"] for r in records) and manifest["model_digest_stable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

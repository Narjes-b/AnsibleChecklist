# -*- coding: utf-8 -*-
"""Task 2.4 MVP: send detected Ansible issues to a local Ollama model and record
a structured, auditable explanation for each one.

This script is READ-ONLY with respect to the project's Ansible/annotation data:
it never modifies the input CSV, never writes into an analyzed repository, and
never overwrites an existing agent's label. It only writes new files under
local-llm/outputs/.

Usage:
    python explain.py --input ../annotation-comparison/consolidated-comparison.csv \
        --id-col issue_id --limit 10 --model qwen2.5-coder:7b

Each issue produces exactly one audit record at
local-llm/outputs/<issue_id>.json, matching the fields required by Task 2 Section 5.
"""
import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prompt_template import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"
REQUIRED_KEYS = [
    "what_is_wrong", "why_it_is_wrong", "why_in_this_context",
    "potential_consequences", "recommended_fix", "fixed_code_snippet",
    "why_fix_works", "trade_offs_and_assumptions", "confidence", "limitations",
]
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "what_is_wrong": {"type": "string"},
        "why_it_is_wrong": {"type": "string"},
        "why_in_this_context": {"type": "string"},
        "potential_consequences": {"type": "string"},
        "recommended_fix": {"type": "string"},
        "fixed_code_snippet": {"type": ["string", "null"]},
        "why_fix_works": {"type": "string"},
        "trade_offs_and_assumptions": {"type": "string"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "limitations": {"type": ["string", "null"]},
    },
    "required": REQUIRED_KEYS,
}


def call_ollama(host: str, model: str, system: str, user: str, timeout: float, options: dict):
    """Calls Ollama's /api/chat with a schema-constrained format. Returns (raw_text, duration_s, error)."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "format": RESPONSE_SCHEMA,
        "stream": False,
        "options": options,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/api/chat", data=data, headers={"Content-Type": "application/json"}
    )
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        duration = time.monotonic() - start
        return body.get("message", {}).get("content", ""), duration, None
    except urllib.error.URLError as e:
        return None, time.monotonic() - start, f"connection error: {e}"
    except TimeoutError:
        return None, time.monotonic() - start, "timeout"
    except Exception as e:  # noqa: BLE001 - this is a best-effort integration script
        return None, time.monotonic() - start, f"unexpected error: {type(e).__name__}: {e}"


def validate_explanation(raw_text: str):
    """Returns (parsed_dict_or_None, warnings_list)."""
    warnings = []
    if raw_text is None:
        return None, ["no response body"]
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        return None, [f"malformed JSON: {e}"]
    if not isinstance(parsed, dict):
        return None, ["response was valid JSON but not a JSON object"]
    missing = [k for k in REQUIRED_KEYS if k not in parsed]
    if missing:
        warnings.append(f"missing keys: {missing}")
    if parsed.get("confidence") not in ("high", "medium", "low", None):
        warnings.append(f"unexpected confidence value: {parsed.get('confidence')!r}")
    return parsed, warnings


def build_audit_record(issue: dict, issue_id: str, model: str, options: dict,
                        raw_text, duration, call_error, parsed, warnings):
    return {
        "issue_id": issue_id,
        "source_location": {
            "repository": issue.get("repository", ""),
            "path": issue.get("path", ""),
            "line_start": issue.get("line_start", ""),
            "line_end": issue.get("line_end", issue.get("line_start", "")),
            "rule_id": issue.get("rule_id", ""),
            "review_family": issue.get("review_family", ""),
        },
        "context_supplied_to_model": {
            "source_context": issue.get("source_context") or issue.get("original_code_or_issue", ""),
            "detector_message": issue.get("message", issue.get("review_question", "")),
        },
        "original_detector_annotation": {
            "my_label_semantic": issue.get("my_label_semantic", issue.get("ai_semantic_label", "")),
            "my_label_actionability": issue.get("my_label_actionability", issue.get("ai_actionability_label", "")),
            "my_explanation": issue.get("my_explanation", issue.get("ai_notes", "")),
            "teammate_label_semantic": issue.get("teammate_label_semantic", ""),
            "teammate_explanation": issue.get("teammate_explanation", ""),
            "note": "preserved exactly as found in the input file; never overwritten by this script",
        },
        "model": {"name": model, "inference_options": options},
        "prompt_version": PROMPT_VERSION,
        "execution": {
            "status": "ok" if (call_error is None and parsed is not None and not warnings) else
                      ("error" if call_error else "completed_with_warnings"),
            "error": call_error,
            "warnings": warnings,
            "duration_seconds": round(duration, 3) if duration is not None else None,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "raw_response": raw_text,
        "explanation": parsed,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="CSV of issues (e.g. consolidated-comparison.csv or any CSV with the same column names)")
    ap.add_argument("--id-col", default="issue_id", help="column to use as the stable issue ID")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--out-dir", default=str(Path(__file__).parent.parent / "outputs"))
    ap.add_argument("--limit", type=int, default=None, help="only process the first N rows (for smoke-testing)")
    ap.add_argument("--timeout", type=float, default=120.0, help="per-request timeout in seconds")
    ap.add_argument("--temperature", type=float, default=0.1, help="low temperature: we want grounded, repeatable explanations, not creative variation")
    ap.add_argument("--skip-existing", action="store_true", help="skip issues that already have an audit record")
    ap.add_argument(
        "--num-ctx", type=int, default=8192,
        help=(
            "Ollama context window in tokens. Ollama's own server default is 4096 "
            "regardless of the model's advertised max context length (measured: "
            "qwen2.5-coder:7b reports context_length=32768 in /api/tags, but the "
            "running server log showed n_ctx_slot=4096 until this was set explicitly). "
            "A prompt that exceeds the active context window is silently truncated, "
            "which produced both a malformed-schema response and a request-level 500 "
            "error during evaluation of large source-context issues. 8192 is a "
            "practical default for the ~8-12GB VRAM budget this model was selected "
            "for; raise it only if VRAM allows."
        ),
    )
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]

    options = {"temperature": args.temperature, "num_ctx": args.num_ctx}

    ok, errored, warned = 0, 0, 0
    for i, issue in enumerate(rows, 1):
        issue_id = issue.get(args.id_col) or f"row-{i}"
        out_path = out_dir / f"{issue_id}.json"
        if args.skip_existing and out_path.is_file():
            continue

        user_prompt = build_user_prompt(issue)
        raw_text, duration, call_error = call_ollama(
            args.host, args.model, SYSTEM_PROMPT, user_prompt, args.timeout, options
        )
        parsed, warnings = (None, [call_error]) if call_error else validate_explanation(raw_text)

        record = build_audit_record(issue, issue_id, args.model, options,
                                     raw_text, duration, call_error, parsed, warnings)
        out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

        status = record["execution"]["status"]
        if status == "ok":
            ok += 1
        elif status == "error":
            errored += 1
        else:
            warned += 1
        print(f"[{i}/{len(rows)}] {issue_id}: {status}"
              + (f" ({duration:.1f}s)" if duration else ""))

    print(f"\nDone. ok={ok} completed_with_warnings={warned} error={errored} "
          f"(total={len(rows)}, audit records in {out_dir})")


if __name__ == "__main__":
    main()

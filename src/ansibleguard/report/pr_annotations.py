"""Publish introduced canonical occurrences as GitHub PR annotations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath

from .findings import developer_priority_key, finding_category, is_optional_finding
from .llm_explain import assessment_text


_COMMAND_LEVEL = {"error": "error", "warning": "warning", "note": "notice"}


def _escape_data(value: object) -> str:
    return (
        str(value)
        .replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
    )


def _escape_property(value: object) -> str:
    return _escape_data(value).replace(":", "%3A").replace(",", "%2C")


def _location(item: dict) -> tuple[str, int]:
    file = str(item.get("file", "")).replace("\\", "/")
    while file.startswith("./"):
        file = file[2:]
    path = PurePosixPath(file)
    if not file or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"invalid repository-relative annotation path: {file!r}")
    try:
        line = int(item.get("line", 1))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid annotation line for {file!r}") from exc
    if line < 1:
        raise ValueError(f"invalid annotation line for {file!r}: {line}")
    return file, line


def _fix_suggestion_text(item: dict) -> str:
    """Prefer the per-occurrence LLM explanation (ansibleguard diff --explain)
    over the generic per-rule remediation string, when one was produced
    successfully -- but always carry its disclaimer along, since the model
    has a measured blind spot for false positives (see llm_explain.py)."""
    assessment = assessment_text(item)
    if assessment:
        return assessment
    if item.get("llm_status") == "ok" and item.get("llm_suggested_fix"):
        text = f"AI suggestion (unverified): {item['llm_suggested_fix']}"
        if item.get("llm_why_in_this_context"):
            text = f"{text} Why: {item['llm_why_in_this_context']}"
        if item.get("llm_disclaimer"):
            text = f"{text} ({item['llm_disclaimer']})"
        return text
    if item.get("remediation"):
        return f"Suggested fix: {item['remediation']}"
    return ""


def annotation_command(item: dict) -> str:
    """Return one injection-safe GitHub workflow annotation command."""
    file, line = _location(item)
    severity = str(item.get("severity", "warning")).lower()
    level = _COMMAND_LEVEL.get(severity, "warning")
    concept = item.get("concept_id") or "finding"
    category = finding_category(item)
    title = f"AnsibleGuard [{category}]: {concept}"
    message = item.get("message") or "AnsibleGuard detected an introduced finding."
    fix_text = _fix_suggestion_text(item)
    if fix_text:
        message = f"{message} {fix_text}"
    return (
        f"::{level} file={_escape_property(file)},line={line},"
        f"title={_escape_property(title)}::{_escape_data(message)}"
    )


def introduced_occurrences(payload: dict) -> list[dict]:
    if payload.get("kind") != "pr-comparison":
        raise ValueError("decision is not an AnsibleGuard pr-comparison document")
    comparison = payload.get("comparison")
    if not isinstance(comparison, dict):
        raise ValueError("decision has no comparison object")
    introduced = comparison.get("introduced")
    if not isinstance(introduced, list):
        raise ValueError("decision has no introduced occurrence list")
    if not all(isinstance(item, dict) for item in introduced):
        raise ValueError("introduced occurrences must be JSON objects")
    return introduced


def render_markdown(items: list[dict], total: int) -> str:
    """Render the introduced findings for the GitHub job summary."""
    items = sorted(items, key=developer_priority_key)
    actionable = [item for item in items if not is_optional_finding(item)]
    optional = [item for item in items if is_optional_finding(item)]
    lines = [
        "### Introduced findings",
        "",
        f"AnsibleGuard found **{total}** introduced canonical occurrence(s).",
        f"**{len(actionable)} actionable** and **{len(optional)} optional policy** finding(s) are shown below.",
        "",
    ]
    if not items:
        lines.append("No introduced findings were found.")
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "| Category | Severity | Confidence | Rule | Location | Message and suggested fix |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in actionable:
        file, line = _location(item)
        values = (
            finding_category(item),
            item.get("severity", "warning"),
            item.get("confidence", "medium"),
            item.get("concept_id", "finding"),
            f"`{file}:{line}`",
            " ".join(
                value for value in (
                    item.get("message", "AnsibleGuard detected an introduced finding."),
                    _fix_suggestion_text(item),
                ) if value
            ),
        )
        escaped = [str(value).replace("|", "\\|").replace("\n", " ") for value in values]
        lines.append("| " + " | ".join(escaped) + " |")
    if optional:
        lines.extend(
            [
                "",
                "<details>",
                f"<summary>Optional policy findings ({len(optional)})</summary>",
                "",
                "| Category | Severity | Confidence | Rule | Location | Message and suggested fix |",
                "|---|---|---|---|---|---|",
            ]
        )
        for item in optional:
            file, line = _location(item)
            values = (
                finding_category(item),
                item.get("severity", "warning"),
                item.get("confidence", "medium"),
                item.get("concept_id", "finding"),
                f"`{file}:{line}`",
                " ".join(
                    value for value in (
                        item.get("message", "AnsibleGuard detected an introduced finding."),
                        _fix_suggestion_text(item),
                    ) if value
                ),
            )
            escaped = [
                str(value).replace("|", "\\|").replace("\n", " ")
                for value in values
            ]
            lines.append("| " + " | ".join(escaped) + " |")
        lines.extend(["", "</details>"])
    if len(items) < total:
        lines.extend(["", f"Showing the first {len(items)} of {total} occurrences."])
    return "\n".join(lines) + "\n"


def publish(
    payload: dict,
    *,
    limit: int = 50,
    stream=None,
    summary=None,
    include_optional: bool = False,
) -> int:
    """Emit introduced annotations and optionally append a Markdown summary."""
    if limit < 1:
        raise ValueError("annotation limit must be at least 1")
    stream = stream or sys.stdout
    introduced = introduced_occurrences(payload)
    candidates = [
        item
        for item in introduced
        if include_optional or not is_optional_finding(item)
    ]
    candidates = sorted(candidates, key=developer_priority_key)
    selected = candidates[:limit]
    for item in selected:
        print(annotation_command(item), file=stream)
    if len(candidates) > limit:
        print(
            "::notice title=AnsibleGuard annotation limit::"
            f"Showing {limit} of {len(candidates)} actionable introduced occurrences. "
            "See the job summary and artifact for the complete report.",
            file=stream,
        )
    optional_count = sum(is_optional_finding(item) for item in introduced)
    if optional_count and not include_optional:
        print(
            "::notice title=AnsibleGuard optional policy findings::"
            f"Collapsed {optional_count} optional finding(s). "
            "See the job summary and artifact for details.",
            file=stream,
        )
    if summary is not None:
        summary.write(render_markdown(introduced, len(introduced)))
    return len(selected)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish introduced AnsibleGuard findings as GitHub annotations."
    )
    parser.add_argument("decision", type=Path)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--include-optional",
        action="store_true",
        help="also emit inline workflow annotations for optional policy findings",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="append an introduced-findings table to a Markdown job summary",
    )
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.decision.read_text(encoding="utf-8"))
        if args.summary:
            with args.summary.open("a", encoding="utf-8") as summary:
                publish(
                    payload,
                    limit=args.limit,
                    summary=summary,
                    include_optional=args.include_optional,
                )
        else:
            publish(
                payload,
                limit=args.limit,
                include_optional=args.include_optional,
            )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"AnsibleGuard annotation publishing failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

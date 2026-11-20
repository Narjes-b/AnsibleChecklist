#!/usr/bin/env python3
"""Reviewer context bundles v2 (codebooks-v2 section C7, "generator contract").

Drop-in replacements for ``v007_validation_pilot._static_context`` and ``_review_context``
(same arguments, same ``(bundle_text, inline_excerpt)`` result) that fix the defects found
while labelling the 350-item pilot. The frozen v1 generator is unchanged.

Differences from v1:
- the header names the flagged construct (kind, id, asserted variable/attribute); if the
  finding names nothing, the bundle says so explicitly so reviewers can mark it a bundle defect;
- the tracked-path listing is complete up to ``TREE_LIMIT`` paths and otherwise reports, per
  directory, how many paths exist, so nothing is silently cut; deterministic presence checks
  (README, tasks/main, molecule, meta) are always shown;
- very large files get a wider anchor window (+-``WINDOW`` lines) and the bundle states it;
- variable searches use whole-word matching, are grouped by file and cap at ``SEARCH_LIMIT``
  with the exact number cut;
- handler rules include every file under the role's ``handlers/`` directory;
- review diffs include EVERY changed path (YAML and non-YAML); each file diff is capped at
  ``FILE_DIFF_LINES`` lines and the bundle states what was cut; binary files are named;
- every bundle is passed through the v1 redaction and then the second-pass redactor.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path, PurePosixPath
import re
import sys

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_bundle_redact_v2 import redact_text as second_pass  # noqa: E402
from scripts.v007_validation_pilot import (  # noqa: E402
    REVIEW_MESSAGE_ONLY_RULE_IDS, _BLOCK_SCALAR, _PUBLIC_DEFAULTS, _SENSITIVE_ASSIGNMENT, _TEMPLATE_PREFIXES,
    _TOKEN_PATTERNS, _changed_file_rows, _git, _role_root, _safe_source_path,
)

TREE_LIMIT = 400
WINDOW = 100
SEARCH_LIMIT = 200
FILE_DIFF_LINES = 400
HANDLER_FILE_LINES = 300
HANDLER_RULES = {"ansibleguard/missing-handler", "ansibleguard/unused-handler"}


SAFE_LITERALS = {"true", "false", "yes", "no", "on", "off", "null", "none", "~"}
SIZE_KEY = re.compile(r"(len|length|size|count|port|age|days|ttl|timeout|min|max|expir|interval|retries|attempts|rounds|bits|history|digits)", re.IGNORECASE)


IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+")
NESTED_ITEM = re.compile(r"^(\s*(?:[-+] )?\s*(?:-\s+)?)(?:([\"']?[\w.-]+[\"']?)\s*:\s*)?(.*)$")


def _identifier_list(value: str) -> bool:
    """A flow list of variable-style names, e.g. ``[vault_token_ro, vault_token_rw]`` (names, not secrets)."""
    plain = value.strip()
    if not (plain.startswith("[") and plain.endswith("]")):
        return False
    items = [i.strip().strip("\"'") for i in plain[1:-1].split(",") if i.strip()]
    return bool(items) and all(IDENTIFIER.fullmatch(i) or i.startswith(_TEMPLATE_PREFIXES) for i in items)


def _safe_nested_leaf(key: str, value: str) -> bool:
    """A value that may stay visible inside the structure under a secret-named key."""
    plain = value.strip().strip("\"'")
    if not plain or plain.casefold() in SAFE_LITERALS or plain.startswith(_TEMPLATE_PREFIXES) or plain.startswith("[REDACTED"):
        return True
    if key and re.fullmatch(r"\d{1,6}", plain) and SIZE_KEY.search(key):
        return True
    if IDENTIFIER.fullmatch(plain):
        return True
    if plain.startswith("[") and plain.endswith("]"):
        items = [i.strip().strip("\"'") for i in plain[1:-1].split(",") if i.strip()]
        return bool(items) and all(IDENTIFIER.fullmatch(i) or i.startswith(_TEMPLATE_PREFIXES) for i in items)
    return False


def _redact_lines_v2(text: str) -> str:
    """The v1 key-based redaction with three corrections found while labelling pilot 2.

    Kept visible: boolean/null literals (``sudo_requires_password: false``), small integers under size-like keys
    (``password_min_length: 12``), and an empty value that only introduces nested structure (v1 hid the whole
    nested block, including the anchor). Still redacted: every other literal, block scalars and vault blocks,
    private-key blocks, provider tokens. Secrets are never kept visible by this function.
    """
    output: list[str] = []
    in_private_key = False
    in_block_indent: int | None = None
    in_struct_indent: int | None = None
    for line in text.split("\n"):
        if in_private_key:
            if "-----END " in line and "PRIVATE KEY-----" in line:
                output.append("[REDACTED PRIVATE KEY END]")
                in_private_key = False
            else:
                output.append("[REDACTED PRIVATE KEY CONTENT]")
            continue
        if "-----BEGIN " in line and "PRIVATE KEY-----" in line:
            output.append("[REDACTED PRIVATE KEY BLOCK]")
            in_private_key = True
            continue
        content_line = line[1:] if line.startswith(("+", "-")) else line
        indent = len(content_line) - len(content_line.lstrip())
        if in_block_indent is not None:
            if line.strip() and indent > in_block_indent:
                marker = line[:1] if line.startswith(("+", "-")) else ""
                output.append(marker + " " * indent + "[REDACTED ENCRYPTED VALUE]")
                continue
            in_block_indent = None
        if in_struct_indent is not None and line.strip() and indent <= in_struct_indent:
            in_struct_indent = None
        assignment = _SENSITIVE_ASSIGNMENT.search(line)
        if assignment is None and in_struct_indent is not None and line.strip() and not line.strip().startswith("#"):
            item = NESTED_ITEM.match(line)
            if item and item.group(3).strip() and not _safe_nested_leaf((item.group(2) or "").strip("\"'"), item.group(3)):
                output.append(item.group(1) + (f"{item.group(2)}: " if item.group(2) else "") + "[REDACTED_LITERAL]")
                continue
        if assignment:
            key = assignment.group(1)
            value = assignment.group(2).strip().strip("\"'")
            prefix = line[: assignment.start(1)]
            folded = value.casefold()
            if value.startswith("[REDACTED") or value.startswith(_TEMPLATE_PREFIXES) or folded in _PUBLIC_DEFAULTS:
                output.append(line)
            elif not value:
                output.append(line)
                in_struct_indent = indent  # structure below stays visible, nested literals are screened
            elif folded in SAFE_LITERALS or _identifier_list(value):
                output.append(line)
            elif re.fullmatch(r"\d{1,6}", value) and SIZE_KEY.search(key):
                output.append(line)
            elif _BLOCK_SCALAR.fullmatch(value):
                output.append(prefix + key + "[REDACTED VALUE BLOCK]")
                in_block_indent = indent
            else:
                output.append(prefix + key + "[REDACTED_LITERAL]")
            continue
        redacted = line
        for pattern in _TOKEN_PATTERNS:
            redacted = pattern.sub("[REDACTED_TOKEN]", redacted)
        output.append(redacted)
    return "\n".join(output)


GUTTER_PREFIX = re.compile(r"^(\s*\d+ \| ?)")


def redact_sensitive_text_v2(text: str) -> str:
    """Apply ``_redact_lines_v2`` to the content of the bundle, ignoring the ``  123 | `` line-number gutter.

    Indentation logic (nested secret blocks) must see the real YAML indentation, so the gutter is split off first.
    Lines without a gutter (headers, commit messages, diffs) are processed as they are, in consecutive runs.
    """
    lines = text.split("\n")
    out: list[str] = []
    run: list[str] = []
    run_prefixes: list[str] = []
    gutter_run = False

    def flush() -> None:
        if not run:
            return
        redacted = _redact_lines_v2("\n".join(run)).split("\n")
        if len(redacted) != len(run):  # a redaction must never change the line count
            raise RuntimeError("redaction changed the number of lines")
        out.extend(prefix + line for prefix, line in zip(run_prefixes, redacted))
        run.clear()
        run_prefixes.clear()

    for line in lines:
        match = GUTTER_PREFIX.match(line)
        if match:
            if not gutter_run:
                flush()
                gutter_run = True
            run_prefixes.append(match.group(1))
            run.append(line[len(match.group(1)):])
        else:
            if gutter_run:
                flush()
                gutter_run = False
            run_prefixes.append("")
            run.append(line)
    flush()
    return "\n".join(out)


MARKER_LINE = re.compile(r"^(\s*\d+ \| )?\s*\[REDACTED[^\]]*\]\s*$")


def collapse_redaction_runs(text: str) -> str:
    """Replace 3+ consecutive identical redaction-marker lines by the first line and a count."""
    out, run = [], []

    def flush() -> None:
        if len(run) >= 3:
            out.append(run[0])
            out.append(f"      [... {len(run) - 1} further identical redacted lines, through {run[-1].split('|')[0].strip() or 'the last'}]")
        else:
            out.extend(run)
        run.clear()

    for line in text.split("\n"):
        body = MARKER_LINE.match(line)
        if body and (not run or MARKER_LINE.match(run[0]).group(0).split("|")[-1].strip() == line.split("|")[-1].strip()):
            run.append(line)
            continue
        flush()
        if body:
            run.append(line)
        else:
            out.append(line)
    flush()
    return "\n".join(out)


def _numbered_excerpt(lines: list[str], start: int, end: int) -> str:
    """Numbered excerpt WITHOUT redaction; every bundle part is redacted once by ``redact`` at the end.

    (The v1 helper of the same name redacts internally with the v1 rules, which would pre-empt the v2 rules.)
    """
    if not lines:
        return "[empty source file]"
    start, end = max(1, start), min(len(lines), end)
    return "\n".join(f"{number:5d} | {lines[number - 1]}" for number in range(start, end + 1))


def redact(text: str) -> str:
    return collapse_redaction_runs(second_pass(redact_sensitive_text_v2(text)))


TASK_START = re.compile(r"^(\s*)-\s+(?:name:\s*(.*)|\S.*)$")
TOP_KEY = re.compile(r"^([A-Za-z_][\w.-]*):")
PLAY_RULES = {"become-scope-too-broad", "unnamed-play", "large-play"}
PLACEHOLDER_SUBJECT = re.compile(r"^(location|file|none|n/a)\b", re.IGNORECASE)


def _unquote(value: str) -> str:
    return value.strip().strip("'\"")


def enclosing_construct(lines: list[str], anchor: int) -> str:
    """Describe the nearest task/play list item at or above the anchor, else the top-level mapping key."""
    for number in range(min(anchor, len(lines)), 0, -1):
        match = TASK_START.match(lines[number - 1])
        if match:
            indent = len(match.group(1))
            name = _unquote(match.group(2) or "")
            is_play = False
            for follow in lines[number:number + 60]:
                stripped = follow.strip()
                if not stripped:
                    continue
                if len(follow) - len(follow.lstrip()) <= indent and stripped.startswith("-"):
                    break
                if not name:
                    named = re.match(r"^\s+name:\s*(.*)$", follow)
                    if named:
                        name = _unquote(named.group(1))
                if re.match(r"^\s+hosts:", follow):
                    is_play = True
            kind = "play" if is_play else "task"
            return f"the {kind} at line {number}" + (f", name `{name}`" if name else ", unnamed")
    for number in range(min(anchor, len(lines)), 0, -1):
        key = TOP_KEY.match(lines[number - 1])
        if key:
            return f"the top-level key `{key.group(1)}` (line {number})"
    return ""


def subject_lines(candidate: dict[str, str], lines: list[str] | None = None) -> list[str]:
    """Name the flagged construct from the finding's own subject, else from the source, never from a hash.

    ``object_id`` is a hash and is never shown. A kind-prefixed ``semantic_subject`` ("task: Restart web",
    "variable: x") is the finding's own name for the construct; otherwise the enclosing task/play/key of the
    anchor line is reported, or the finding is declared file-level. A placeholder subject ("location") is ignored.
    """
    subject = (candidate.get("semantic_subject") or "").strip()
    anchor = int(candidate.get("line_start") or "1")
    rule = (candidate.get("rule_id") or "").split("/")[-1]
    if ":" in subject and subject.split(":", 1)[0].strip() in {"task", "variable", "attribute", "play", "handler", "role", "block"}:
        kind, value = (part.strip() for part in subject.split(":", 1))
        where = enclosing_construct(lines, anchor) if lines is not None and kind == "task" else ""
        if where.startswith("the play"):
            return [f"- Flagged construct: {where} (the finding calls it a task; the source shows a play)"]
        return [f"- Flagged construct: {kind} `{value}`"]
    out = []
    if lines is not None and (anchor > 1 or rule in PLAY_RULES):
        where = enclosing_construct(lines, anchor)
        out.append(f"- Flagged construct: not named by the finding; the anchor line {anchor} lies in {where or 'no enclosing list item or key'}.")
    else:
        out.append(f"- Flagged construct: file-level finding about the whole file or role (`{candidate.get('path', '')}`); it names no single task.")
    if subject and not PLACEHOLDER_SUBJECT.match(subject):
        out.append(f"- Asserted subject (variable/attribute/value): `{subject}`")
    return out


ABSTRACTION_KEYS = {"include_tasks", "import_tasks", "include_role", "import_role",
                    "ansible.builtin.include_tasks", "ansible.builtin.import_tasks",
                    "ansible.builtin.include_role", "ansible.builtin.import_role"}
JUSTIFYING_KEYS = {"rescue", "always", "when", "tags", "become", "become_user", "no_log", "environment", "loop", "with_items", "vars"}
NESTED = ("block", "rescue", "always")
TASK_SECTIONS = ("tasks", "pre_tasks", "post_tasks", "handlers")


def _pairs(node):
    return {k.value: v for k, v in node.value} if isinstance(node, yaml.MappingNode) else {}


def computed_facts(rule_id: str, text: str) -> str:
    """Parser facts for rules whose predicate names a block or a count (not a detector label)."""
    name = rule_id.split("/")[-1]
    if name not in {"unnecessary-abstraction", "missing-abstraction"}:
        return ""
    try:
        root = yaml.compose(text)
    except yaml.YAMLError:
        return "[computed facts unavailable: the file does not parse as YAML]"
    blocks, leaves, has_abstraction = [], 0, False

    def walk_tasks(sequence):
        nonlocal leaves, has_abstraction
        if not isinstance(sequence, yaml.SequenceNode):
            return
        for item in sequence.value:
            pairs = _pairs(item)
            if not pairs:
                continue
            if ABSTRACTION_KEYS & set(pairs):
                has_abstraction = True
            nested = [pairs[k] for k in NESTED if isinstance(pairs.get(k), yaml.SequenceNode)]
            if "block" in pairs and isinstance(pairs["block"], yaml.SequenceNode):
                keys = sorted(set(pairs) - {"block"})
                blocks.append((item.start_mark.line + 1, len(pairs["block"].value), keys))
            if nested:
                for child in nested:
                    walk_tasks(child)
            else:
                leaves += 1

    if isinstance(root, yaml.SequenceNode):
        items = [_pairs(i) for i in root.value]
        if any("hosts" in p for p in items):
            for item in root.value:
                pairs = _pairs(item)
                if pairs.get("roles") is not None:
                    has_abstraction = True
                for section in TASK_SECTIONS:
                    walk_tasks(pairs.get(section))
        else:
            walk_tasks(root)
    out = ["Computed facts (from the parsed file, independent of the detector):"]
    if name == "unnecessary-abstraction":
        single = [b for b in blocks if b[1] == 1]
        out.append(f"- blocks in file: {len(blocks)}; blocks containing exactly one task: {len(single)}")
        for line, _, keys in single:
            justifying = sorted(set(keys) & JUSTIFYING_KEYS)
            out.append(f"  - block at line {line}: block-level keys {keys or 'none'}; justifying keys {justifying or 'none'}")
    else:
        out.append(f"- leaf tasks (not counting block containers): {leaves} (the rule needs more than 10)")
        out.append(f"- include/import task or role, or play-level roles, present: {'yes' if has_abstraction else 'no'}")
    return "\n".join(out)


def tree_context(repo_path: Path, commit_sha: str, source_path: str) -> str:
    role_root = _role_root(source_path)
    target = role_root or "."
    result = _git(repo_path, "ls-tree", "-r", "--name-only", commit_sha, "--", target, check=False)
    if result.returncode:
        return "[tracked-path listing unavailable]"
    paths = result.stdout.splitlines()
    if not paths:
        return "[no tracked paths under this scope]"
    base = role_root or ""
    present = lambda pattern: any(re.fullmatch(pattern, p[len(base) + 1 if base else 0:], re.IGNORECASE) for p in paths)  # noqa: E731
    checks = [
        ("tasks/main.yml or tasks/main.yaml", present(r"tasks/main\.ya?ml")),
        ("README at the scope root", present(r"readme(\.[a-z]+)?")),
        ("meta/main.yml or meta/main.yaml", present(r"meta/main\.ya?ml")),
        ("molecule/ directory", any("/molecule/" in "/" + p or p.startswith("molecule/") for p in paths)),
    ]
    out = [f"Scope: `{target}`; {len(paths)} tracked paths.", "Presence checks (computed from the complete listing):"]
    out += [f"- {name}: {'yes' if ok else 'no'}" for name, ok in checks]
    out.append("")
    anchor = str(PurePosixPath(source_path).parent)
    nearby = [p for p in paths if anchor == "." or p.startswith(anchor + "/")]
    if len(paths) <= TREE_LIMIT:
        out += paths
    else:
        directories = Counter(str(PurePosixPath(p).parent) for p in paths)
        out.append(f"Listing exceeds {TREE_LIMIT}: paths beside the cited file, then a per-directory count of ALL paths.")
        out += nearby[:TREE_LIMIT]
        if len(nearby) > TREE_LIMIT:
            out.append(f"[{len(nearby) - TREE_LIMIT} further paths beside the cited file not listed]")
        out += ["", "Per-directory path counts:"] + [f"{d}: {n}" for d, n in sorted(directories.items())]
    return "\n".join(out)


def reference_context(repo_path: Path, commit_sha: str, subject: str) -> str:
    if not subject.startswith("variable:"):
        return ""
    symbol = subject.split(":", 1)[1].strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", symbol):
        return "[symbol not a simple variable identifier; inspect supplied repository context]"
    result = _git(repo_path, "grep", "-n", "-I", "-w", "-F", "-e", symbol, commit_sha, "--", "*.yml", "*.yaml", "*.j2", check=False)
    if result.returncode not in (0, 1):
        return "[frozen-commit reference search unavailable]"
    matches = [line.split(":", 1)[1] if ":" in line else line for line in result.stdout.splitlines()]
    if not matches:
        return "[no whole-word matches in searched YAML/Jinja files]"
    by_file = Counter(m.split(":", 1)[0] for m in matches)
    name = re.escape(symbol)
    definition = re.compile(rf"^[^:]*:\d+:\s*(?:-\s+)?{name}\s*:|register:\s*[\"']?{name}\b|set_fact")
    likely = [m for m in matches if definition.search(m)]
    others = [m for m in matches if m not in set(likely)]
    shown = (likely[:SEARCH_LIMIT] + others)[:SEARCH_LIMIT]
    out = [f"Whole-word search for `{symbol}`: {len(matches)} matches in {len(by_file)} files; {len(likely)} look like definitions "
           f"(key assignment, register, set_fact) and are listed first."]
    out += ["Likely definitions:"] + [m for m in shown if m in set(likely)] if likely else ["No definition-like match (key assignment, register, set_fact) found."]
    out += ["", "Other references:"] + [m for m in shown if m not in set(likely)]
    if len(matches) > len(shown):
        out.append(f"[{len(matches) - len(shown)} further matches not shown; files: " + ", ".join(f"{f}={n}" for f, n in by_file.most_common(10)) + "]")
    return "\n".join(out)


def handler_context(repo_path: Path, commit_sha: str, source_path: str) -> str:
    role_root = _role_root(source_path)
    target = f"{role_root}/handlers" if role_root else "handlers"
    listing = _git(repo_path, "ls-tree", "-r", "--name-only", commit_sha, "--", target, check=False)
    files = [p for p in listing.stdout.splitlines() if p.endswith((".yml", ".yaml"))]
    if not files:
        return f"[no handler files under `{target}`]"
    out = []
    for path in files:
        text = _git(repo_path, "show", f"{commit_sha}:{path}", check=False).stdout.splitlines()
        shown = text[:HANDLER_FILE_LINES]
        out.append(f"### {path} ({len(text)} lines)")
        out.append(_numbered_excerpt(shown, 1, len(shown)))
        if len(text) > HANDLER_FILE_LINES:
            out.append(f"[{len(text) - HANDLER_FILE_LINES} further lines not shown]")
    return "\n".join(out)


def static_context(candidate: dict[str, str], family_name: str, codebook_path: str, repo_path: Path) -> tuple[str, str]:
    relative = _safe_source_path(candidate["path"])
    blob = _git(repo_path, "show", f"{candidate['commit_sha']}:{relative.as_posix()}").stdout
    if "\x00" in blob:
        raise RuntimeError(f"binary source cannot be reviewed: {candidate['source_context_ref']}")
    lines = blob.splitlines()
    anchor = max(1, int(candidate["line_start"] or "1"))
    if len(lines) <= 500 and len(blob) <= 120_000:
        first, last = 1, len(lines)
    else:
        first, last = max(1, anchor - WINDOW), min(len(lines), anchor + WINDOW)
    excerpt = _numbered_excerpt(lines, first, last)
    parts = [
        f"# Frozen source context: {candidate['sample_id']}", "",
        f"- Repository: `{candidate['repository']}`", f"- Commit: `{candidate['commit_sha']}`",
        f"- Family: {family_name}", f"- Rule: `{candidate['rule_id']}`", f"- Codebook: `{codebook_path}`",
        f"- Source: `{candidate['path']}` (reported anchor line {anchor})",
        *subject_lines(candidate, lines),
        "- Evidence source: Git blob at the frozen commit; no current worktree content was used.",
        "- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.",
        "", "## Source excerpt", "", f"Lines {first}–{last} of {len(lines)}:", "", "```text", excerpt, "```",
    ]
    if candidate["family_id"] == "structure_reuse":
        parts += ["", "## Frozen tracked paths in the relevant role/scope", "", "```text",
                  tree_context(repo_path, candidate["commit_sha"], candidate["path"]), "```"]
    if candidate["family_id"] == "variable_reference_reasoning":
        references = reference_context(repo_path, candidate["commit_sha"], candidate.get("semantic_subject", ""))
        if references:
            parts += ["", "## Visible variable references", "", "```text", references, "```"]
    facts_text = computed_facts(candidate["rule_id"], blob)
    if facts_text:
        parts += ["", "## Computed facts", "", "```text", facts_text, "```"]
    if candidate["rule_id"] in HANDLER_RULES:
        parts += ["", "## Handler files of the role (all, including imported)", "", "```text",
                  handler_context(repo_path, candidate["commit_sha"], candidate["path"]), "```"]
    if first != 1 or last != len(lines):
        parts += ["", f"The file is larger than the inline limit; only a window of ±{WINDOW} lines around the anchor is included. "
                      "If that prevents a defensible decision, label the item unreviewable (bundle-defect)."]
    return redact("\n".join(parts) + "\n"), redact(excerpt)


def review_context(candidate: dict[str, str], family_name: str, codebook_path: str, repo_path: Path) -> tuple[str, str]:
    parent_sha, commit_sha, rule_id = candidate["_parent_sha"], candidate["commit_sha"], candidate["rule_id"]
    message_only = rule_id in REVIEW_MESSAGE_ONLY_RULE_IDS
    message = _git(repo_path, "show", "-s", "--format=%B", commit_sha).stdout.rstrip()
    changed: list[tuple[str, str]] = []
    if not message_only:
        if not parent_sha:
            raise RuntimeError(f"diff-dependent review item lacks its actual first parent: {candidate['sample_id']}")
        changed = _changed_file_rows(repo_path, parent_sha, commit_sha)
    parts = [
        f"# Frozen Git review context: {candidate['sample_id']}", "",
        f"- Repository: `{candidate['repository']}`", f"- Target commit: `{commit_sha}`",
        f"- Actual first parent: `{parent_sha}`" if parent_sha else "- Actual first parent: unavailable (not required for message-only rules)",
        f"- Evidence type: {'exact target commit message only' if message_only else 'actual first-parent diff, all changed paths'}",
        f"- Family: {family_name}", f"- Rule: `{rule_id}`", f"- Codebook: `{codebook_path}`",
        "- Author and committer identities are not part of the evidence and are not included.", "",
        "## Exact target commit message", "", "```text", redact(message) or "[empty commit message]", "```", "",
        f"## Changed paths ({len(changed)})" if not message_only else "## Changed paths (not required for message-only evidence)", "",
    ]
    parts += [f"- `{status}` `{path}`" for status, path in changed]
    if not message_only:
        if not changed:
            parts.append("- [no changed paths in this first-parent diff]")
        parts += ["", "## First-parent diff (every changed path)", ""]
        for status, path in changed:
            result = _git(repo_path, "diff", "--no-ext-diff", "--no-color", "--unified=5", parent_sha, commit_sha, "--", path)
            diff_lines = result.stdout.splitlines()
            if any(line.startswith("Binary files") for line in diff_lines):
                parts += [f"### `{path}`", "[binary file changed; content not shown]", ""]
                continue
            shown = diff_lines[:FILE_DIFF_LINES]
            parts += [f"### `{path}`", "```diff", *shown, "```"]
            if len(diff_lines) > FILE_DIFF_LINES:
                parts.append(f"[{len(diff_lines) - FILE_DIFF_LINES} further diff lines for this file not shown]")
            parts.append("")
    else:
        parts += ["", "The rule is evaluated only on the exact target commit message above."]
    inline = f"Commit `{commit_sha}`. Message:\n{redact(message)}\n" + (
        "See the exact target-message context bundle." if message_only else f"First-parent diff changes {len(changed)} paths; see the linked bundle.")
    return redact("\n".join(parts) + "\n"), inline

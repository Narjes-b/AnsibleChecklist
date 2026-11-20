#!/usr/bin/env python3
"""Locate frozen YAML constructs for calibration packets without deciding labels.

Representation nodes are composed, never constructed/executed. Candidate units
and lexical subject matches are not proof of Ansible applicability or a defect.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter, OrderedDict
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import platform
import re
import sys

import yaml
from jinja2 import Environment, TemplateSyntaxError, nodes
from yaml.events import AliasEvent, CollectionEndEvent, CollectionStartEvent
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ansibleguard.task_traversal import PLAY_TASK_SECTIONS, iter_leaf_tasks
from scripts.retrieve_sample_evidence import SAMPLE_ID, FrozenGitSources, RetrievalFailure, base_packet, load_draw
from scripts.sample_partitioned_occurrences import read_csv, sha256, write_csv
from scripts.v007_bundle_secret_scan import scan_text

STANDARD_TAGS = {"tag:yaml.org,2002:" + name for name in
                 ("str", "int", "float", "bool", "null", "seq", "map", "timestamp", "binary", "set", "omap", "pairs", "merge")}


def mapping(node):
    return {key.value: value for key, value in node.value if isinstance(key, ScalarNode)} if isinstance(node, MappingNode) else {}


def compose_bounded(text, *, max_events=100_000, max_depth=64):
    depth = aliases = events = tagged = 0
    try:
        for event in yaml.parse(text, Loader=yaml.SafeLoader):
            events += 1
            depth += isinstance(event, CollectionStartEvent)
            depth -= isinstance(event, CollectionEndEvent)
            aliases += isinstance(event, AliasEvent)
            tag = getattr(event, "tag", None)
            tagged += bool(tag and tag not in STANDARD_TAGS)
            if events > max_events or depth > max_depth:
                raise RetrievalFailure("yaml-structure-limit")
        if aliases:
            raise RetrievalFailure("yaml-aliases-require-resolution")
        roots = [node for node in yaml.compose_all(text, Loader=yaml.SafeLoader) if node is not None]
        stack = list(roots)
        while stack:
            node = stack.pop()
            if isinstance(node, MappingNode):
                seen = set()
                for key, value in node.value:
                    if not isinstance(key, ScalarNode):
                        raise RetrievalFailure("yaml-complex-keys-require-review")
                    identity = key.tag, key.value
                    if identity in seen:
                        raise RetrievalFailure("yaml-duplicate-keys-require-review")
                    seen.add(identity)
                    stack.append(value)
            elif isinstance(node, SequenceNode):
                stack.extend(node.value)
    except (yaml.YAMLError, RecursionError) as exc:
        raise RetrievalFailure("yaml-parse-failed") from exc
    return roots, {"yaml_events": events, "custom_tag_events": tagged, "documents": len(roots)}


def line_starts(text):
    starts, offset = [0], 0
    for line in text.splitlines(keepends=True):
        offset += len(line)
        starts.append(offset)
    return starts


def span(node, text, starts):
    start = node.start_mark.line + 1
    if bisect_right(starts, node.start_mark.index) != start:
        raise RetrievalFailure("source-line-map-mismatch")
    end = node.end_mark.index
    while end > node.start_mark.index and text[end - 1].isspace():
        end -= 1
    return start, max(start, bisect_right(starts, max(node.start_mark.index, end - 1)))


def index_source(row, raw, oid):
    full, info, failure = base_packet(row, raw, oid, max_lines=len(raw) + 1)
    if failure:
        raise RetrievalFailure(failure)
    text = raw.decode("utf-8")
    safe_lines = [line.split(" | ", 1)[1] for line in full["numbered_source"].splitlines()]
    roots, parse_info = compose_bounded(text)
    starts = line_starts(text)
    mappings, plays, tasks = [], [], []
    for root in roots:
        stack = [root]
        while stack:
            node = stack.pop()
            if isinstance(node, MappingNode):
                mappings.append(node)
                stack.extend(child for pair in node.value for child in pair)
            elif isinstance(node, SequenceNode):
                stack.extend(node.value)
        if isinstance(root, SequenceNode):
            play_nodes = [node for node in root.value if isinstance(node, MappingNode)
                          and ({"hosts", *PLAY_TASK_SECTIONS} & mapping(node).keys())]
            plays.extend(play_nodes)
            globals_ = [node for node in root.value if node not in play_nodes]
            tasks.extend(iter_leaf_tasks(SequenceNode("tag:yaml.org,2002:seq", globals_)))
            for play in play_nodes:
                for section in (*PLAY_TASK_SECTIONS, "block", "rescue", "always"):
                    tasks.extend(iter_leaf_tasks(mapping(play).get(section)))
    units = [(kind, node, span(node, text, starts)) for kind, values in
             (("task-candidate", tasks), ("play-candidate", plays), ("mapping", mappings)) for node in values]
    return {"text": text, "safe_lines": safe_lines, "original_lines": text.splitlines(), "units": units,
            "info": info, "parse_info": parse_info}


def enclosing_units(index, anchor):
    # Keep the smallest enclosing mapping and candidate task/play separately.
    # Never substitute a nearby node when the anchor is in a comment/directive.
    result = []
    for kind in ("task-candidate", "play-candidate", "mapping"):
        candidates = [(node, bounds) for k, node, bounds in index["units"]
                      if k == kind and bounds[0] <= anchor <= bounds[1]]
        if not candidates:
            continue
        width = min(end - start for _, (start, end) in candidates)
        smallest = [(node, bounds) for node, bounds in candidates if bounds[1] - bounds[0] == width]
        if len(smallest) != 1:
            raise RetrievalFailure("ambiguous-enclosing-construct")
        node, bounds = smallest[0]
        result.append((kind, node, bounds))
    return result


def lexical_subject(subject, subject_redacted, units):
    if subject_redacted:
        return "redacted-subject"
    if subject == "location" or not subject:
        return "no-named-subject"
    kind, separator, value = subject.partition(":")
    if not separator or "|task:" in subject or kind not in {"task", "variable", "attribute", "module"}:
        return "unsupported-subject-shape"
    if kind == "variable" and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        return "unsupported-subject-shape"
    tokens = set()
    # Prefer the anchored task/mapping over scanning unrelated plays/files.
    chosen = next((node for k, node, _ in units if k == "task-candidate"),
                  next((node for k, node, _ in units if k == "mapping"), None))
    if chosen is None:
        return "no-anchored-construct"
    if kind == "task":
        name = mapping(chosen).get("name")
        if isinstance(name, ScalarNode):
            tokens.add(name.value.strip())  # Canonical display names strip their surrounding whitespace.
    else:
        stack, environment, template_error = [chosen], Environment(), False
        while stack:
            node = stack.pop()
            if isinstance(node, MappingNode):
                tokens.update(key.value for key, _ in node.value if isinstance(key, ScalarNode))
                if kind == "variable":
                    tokens.update(child.value for key, child in node.value
                                  if isinstance(key, ScalarNode) and key.value in {"register", "loop_var"}
                                  and isinstance(child, ScalarNode) and child.tag == "tag:yaml.org,2002:str")
                stack.extend(child for _, child in node.value)
            elif isinstance(node, SequenceNode):
                stack.extend(node.value)
            elif isinstance(node, ScalarNode) and ("{{" in node.value or "{%" in node.value):
                try:
                    tree = environment.parse(node.value)
                    tokens.update(item.name for item in tree.find_all(nodes.Name))
                    if kind == "attribute":
                        tokens.update(item.attr for item in tree.find_all(nodes.Getattr))
                except (TemplateSyntaxError, RecursionError):
                    template_error = True
    if value in tokens:
        return "exact-token-located"
    if value.casefold() in {token.casefold() for token in tokens}:
        return "casefold-token-only"
    if kind == "task" and value.casefold() in {"unknown", "unnamed", "unnamed task"}:
        return "placeholder-subject"
    if kind != "task" and template_error:
        return "template-parse-incomplete"
    return "token-not-located"


def render_units(index, units, anchor, *, max_lines=600, window=80):
    if not units:
        units = [("file-only-no-enclosing-node", None, (1, len(index["safe_lines"])))]
    result = []
    for kind, _, (start, end) in units:
        truncated = end - start + 1 > max_lines
        shown_start, shown_end = start, end
        if truncated:
            count = min(max_lines, 2 * window + 1)
            shown_start = max(start, min(anchor - count // 2, end - count + 1))
            shown_end = min(end, shown_start + count - 1)
        result.append({"kind": kind, "parser_line_start": start, "parser_line_end": end,
                       "display_line_start": shown_start, "display_line_end": shown_end, "truncated": truncated,
                       "redaction_affects_unit": any(a != b for a, b in zip(
                           index["original_lines"][start - 1:end], index["safe_lines"][start - 1:end])),
                       "numbered_source": "\n".join(f"{n:5d} | {index['safe_lines'][n - 1]}" for n in range(shown_start, shown_end + 1))})
    return result


def load_inputs(draw_dir, metadata_dir):
    selected, _ = load_draw(draw_dir)
    manifest = json.loads((metadata_dir / "metadata-manifest.json").read_text())
    if (manifest["draw_manifest_sha256"] != sha256(draw_dir / "selection-manifest.json")
            or manifest["eligible_for_performance_scoring"] is not False
            or manifest["output_sha256"]["metadata-ledger.csv"] != sha256(metadata_dir / "metadata-ledger.csv")):
        raise ValueError("metadata provenance mismatch")
    rows = list(read_csv(metadata_dir / "metadata-ledger.csv"))
    by_id = {row["sample_id"]: row for row in rows}
    if len(by_id) != len(rows) or by_id.keys() != {row["sample_id"] for row in selected}:
        raise ValueError("metadata selection mismatch")
    for row in selected:
        if any(by_id[row["sample_id"]].get(key) != value for key, value in row.items() if key != "retrieval_status"):
            raise ValueError("metadata changed a selection identity/probability/state")
    return rows, manifest


def ground_rows(rows, reader, metadata_packet_dir, packet_dir, *, max_lines=600, window=80):
    if max_lines < 1 or window < 0:
        raise ValueError("invalid source display bounds")
    ids = [row["sample_id"] for row in rows]
    if not ids or len(set(ids)) != len(ids) or any(not SAMPLE_ID.fullmatch(value) for value in ids):
        raise ValueError("nonempty unique safe sample IDs required")
    packet_dir.mkdir(parents=True, exist_ok=False)
    results, cache = [], OrderedDict()
    for row in rows:
        info = {"construct_status": "not-checked", "task_candidate": False, "play_candidate": False,
                "mapping_candidate": False, "lexical_subject_status": "not-checked", "truncated_units": 0,
                "redacted_units": 0, "custom_tag_events": 0, "subject_verified": False,
                "construct_applicability_verified": False, "evidence_complete": False,
                "rule_evidence_status": "structural-context-only"}
        packet = {"sample_id": row["sample_id"], "run_id": row["run_id"], "repository": row["repository"],
                  "commit_sha": row["commit_sha"], "file": row["file"], "line": row["line"], "units": [],
                  "eligible_for_performance_scoring": False,
                  "missing_evidence": ["Ansible applicability and semantic subject not certified",
                                       "rule-specific predicate/dependencies not evaluated"]}
        try:
            if row["metadata_status"] != "metadata-joined" or row["retrieval_status"] != "source-retrieved":
                raise RetrievalFailure("upstream-evidence-unavailable")
            if row["metadata_packet_file"] != row["sample_id"] + ".json":
                raise RetrievalFailure("invalid-metadata-packet-name")
            path = metadata_packet_dir / row["metadata_packet_file"]
            if sha256(path) != row["metadata_packet_sha256"]:
                raise RetrievalFailure("metadata-packet-hash-mismatch")
            metadata = json.loads(path.read_text())
            if any(metadata.get(key) != row[key] for key in
                   ("sample_id", "run_id", "repository", "commit_sha", "occurrence_id", "canonical_item_sha256")):
                raise RetrievalFailure("metadata-packet-identity-mismatch")
            subject = metadata["redacted_semantic_subject"]
            if scan_text(subject):
                raise RetrievalFailure("subject-secret-scan-blocked")
            key = row["repository"], row["commit_sha"], row["file"]
            if key not in cache:
                try:
                    raw, oid = reader.read(*key)
                    if hashlib.sha256(raw).hexdigest() != row["source_sha256"] or oid != row["git_blob_oid"]:
                        raise RetrievalFailure("source-integrity-mismatch")
                    cache[key] = (index_source(row, raw, oid), "")
                except RetrievalFailure as exc:
                    cache[key] = (None, exc.reason)
                if len(cache) > 64:
                    cache.popitem(last=False)
            index, failure = cache[key]
            cache.move_to_end(key)
            if failure:
                raise RetrievalFailure(failure)
            if index["info"]["source_sha256"] != row["source_sha256"] or index["info"]["git_blob_oid"] != row["git_blob_oid"]:
                raise RetrievalFailure("source-integrity-mismatch")
            anchor = int(row["line"])
            if not 1 <= anchor <= len(index["safe_lines"]):
                raise RetrievalFailure("anchor-out-of-range")
            units = enclosing_units(index, anchor)
            rendered = render_units(index, units, anchor, max_lines=max_lines, window=window)
            info.update(construct_status="constructs-located" if units else "file-only-no-enclosing-node",
                        task_candidate=any(k == "task-candidate" for k, _, _ in units),
                        play_candidate=any(k == "play-candidate" for k, _, _ in units),
                        mapping_candidate=any(k == "mapping" for k, _, _ in units),
                        lexical_subject_status=lexical_subject(subject, metadata["semantic_subject_redacted"], units),
                        truncated_units=sum(unit["truncated"] for unit in rendered),
                        redacted_units=sum(unit["redaction_affects_unit"] for unit in rendered),
                        custom_tag_events=index["parse_info"]["custom_tag_events"])
            packet.update(units=rendered, redacted_semantic_subject=subject, **index["parse_info"])
        except (OSError, ValueError, KeyError, RetrievalFailure) as exc:
            info["construct_status"] = exc.reason if isinstance(exc, RetrievalFailure) else "input-or-source-unavailable"
        packet.update(info)
        data = json.dumps(packet, indent=2, ensure_ascii=False).encode() + b"\n"
        filename = row["sample_id"] + ".json"
        (packet_dir / filename).write_bytes(data)
        results.append({**row, **info, "construct_packet_file": filename,
                        "construct_packet_sha256": hashlib.sha256(data).hexdigest()})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draw-root", type=Path, required=True)
    parser.add_argument("--metadata-root", type=Path, required=True)
    parser.add_argument("--draw", action="append", required=True)
    parser.add_argument("--repositories-root", type=Path, action="append", required=True)
    parser.add_argument("--packet-root", type=Path, required=True)
    parser.add_argument("--report-root", type=Path, required=True)
    parser.add_argument("--max-lines", type=int, default=600)
    parser.add_argument("--window", type=int, default=80)
    args = parser.parse_args(argv)
    if (len(set(args.draw)) != len(args.draw) or any(not re.fullmatch(r"[A-Za-z0-9_-]+", draw) for draw in args.draw)
            or args.max_lines < 1 or args.window < 0):
        parser.error("invalid draws or source display bounds")
    packet_root, report_root = args.packet_root.resolve(), args.report_root.resolve()
    if (packet_root.exists() or report_root.exists() or packet_root.is_relative_to(report_root)
            or report_root.is_relative_to(packet_root)
            or any(output.is_relative_to(root.resolve()) for output in (packet_root, report_root) for root in args.repositories_root)):
        parser.error("use new separate outputs outside source stores")
    inputs = {draw: load_inputs(args.draw_root / draw, args.metadata_root / draw) for draw in args.draw}
    reader = FrozenGitSources(args.repositories_root)
    for draw, (rows, previous) in inputs.items():
        results = ground_rows(rows, reader, Path(previous["local_packet_directory"]), packet_root / draw,
                              max_lines=args.max_lines, window=args.window)
        report = report_root / draw
        report.mkdir(parents=True)
        write_csv(report / "construct-ledger.csv", results)
        cells = {}
        cell_fields = ("dataset_role", "instrument", "rule_id", "policy", "certainty", "resolution_status",
                       "resolution_scope", "size_quartile", "construct_status", "lexical_subject_status")
        for row in results:
            key = tuple(row[field] for field in cell_fields)
            cells.setdefault(key, []).append(row)
        cell_rows = [{**dict(zip(cell_fields, key)), "selected_ids": len(members),
                      "repositories": len({row["repository"] for row in members}),
                      "repository_groups": len({row["repository_group"] for row in members})}
                     for key, members in sorted(cells.items())]
        write_csv(report / "construct-cells.csv", cell_rows)
        manifest = {"purpose": "structural context and lexical audit; no semantic certification",
                    "eligible_for_performance_scoring": False, "selected_rows": len(rows), "recorded_rows": len(results),
                    "metadata_manifest_sha256": sha256(args.metadata_root / draw / "metadata-manifest.json"),
                    "status_counts": dict(Counter(row["construct_status"] for row in results)),
                    "lexical_subject_counts": dict(Counter(row["lexical_subject_status"] for row in results)),
                    "task_candidates": sum(row["task_candidate"] for row in results),
                    "play_candidates": sum(row["play_candidate"] for row in results),
                    "truncated_units": sum(row["truncated_units"] for row in results),
                    "redacted_units": sum(row["redacted_units"] for row in results),
                    "subject_verified": 0, "complete_rule_evidence": 0, "labels_generated": 0, "model_calls": 0,
                    "implementation_sha256": sha256(Path(__file__)),
                    "dependency_sha256": {str(path): sha256(path) for path in
                                          (Path("src/ansibleguard/task_traversal.py"),
                                           *(Path("scripts") / name for name in ("retrieve_sample_evidence.py", "v007_bundle_context_v2.py",
                                                                               "v007_bundle_redact_v2.py", "v007_bundle_secret_scan.py", "v007_validation_pilot.py")))},
                    "source_stores": [str(source.root) for source in reader.readers],
                    "git_version": reader.git_version, "python_version": platform.python_version(),
                    "pyyaml_version": yaml.__version__, "jinja_version": version("Jinja2"),
                    "limits": {"max_unit_display_lines": args.max_lines, "window": args.window, "max_cached_files": 64,
                               "yaml_max_events": 100_000, "yaml_max_depth": 64},
                    "local_packet_directory": str(packet_root / draw),
                    "output_sha256": {name: sha256(report / name) for name in ("construct-ledger.csv", "construct-cells.csv")}}
        (report / "construct-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"draw": draw, "statuses": manifest["status_counts"], "lexical": manifest["lexical_subject_counts"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

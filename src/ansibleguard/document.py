"""Ansible-aware YAML parsing and document classification.

This module is the single filesystem parsing boundary for the v0.0.5 semantic
engine.  Callers should retain :class:`ParsedDocument` instances and pass the
parsed value to detectors instead of reopening the source file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import base64
import binascii
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


PARSER_CACHE_VERSION = "v006-parser-json-1"


class SourceMapping(dict):
    """Plain mapping that retains safe, cacheable YAML source coordinates."""

    def __init__(self, *args, source_line=None, key_lines=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_line = source_line
        self.key_lines = dict(key_lines or {})


class AnsibleSafeLoader(yaml.SafeLoader):
    """Safe loader that preserves, but never executes, Ansible/custom tags.

    Unknown tags are represented by a small mapping for backward compatibility
    with v0.0.4.  The loader also records tag and duplicate-key evidence without
    making otherwise parseable Ansible input fail.
    """

    def __init__(self, stream):
        super().__init__(stream)
        self.ansible_tags: list[dict[str, Any]] = []
        self.duplicate_keys: list[dict[str, Any]] = []

    def construct_mapping(self, node, deep=False):
        seen: dict[Any, yaml.Node] = {}
        for key_node, _value_node in node.value:
            try:
                key = self.construct_object(key_node, deep=False)
                hash(key)
            except (TypeError, yaml.YAMLError):
                continue
            if key in seen:
                self.duplicate_keys.append(
                    {
                        "key": str(key),
                        "line": key_node.start_mark.line + 1,
                        "column": key_node.start_mark.column + 1,
                    }
                )
            else:
                seen[key] = key_node
        mapping = super().construct_mapping(node, deep=deep)
        key_lines = {}
        for key_node, _value_node in node.value:
            try:
                key = self.construct_object(key_node, deep=False)
                hash(key)
            except (TypeError, yaml.YAMLError):
                continue
            key_lines[key] = key_node.start_mark.line + 1
        return SourceMapping(
            mapping,
            source_line=node.start_mark.line + 1,
            key_lines=key_lines,
        )

    def construct_yaml_map(self, node):
        data = SourceMapping(source_line=node.start_mark.line + 1)
        yield data
        value = self.construct_mapping(node)
        data.update(value)
        data.source_line = value.source_line
        data.key_lines = value.key_lines


def _construct_unknown(loader, tag_suffix, node):
    tag = f"!{tag_suffix}"
    loader.ansible_tags.append(
        {
            "tag": tag,
            "line": node.start_mark.line + 1,
            "column": node.start_mark.column + 1,
        }
    )
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_mapping(node)
    return {"__ansible_tag__": tag, "value": value}


AnsibleSafeLoader.add_multi_constructor("!", _construct_unknown)
AnsibleSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    AnsibleSafeLoader.construct_yaml_map,
)


@dataclass(frozen=True)
class SourceLineMap:
    """Stable source coordinates available even to non-round-trip detectors."""

    line_count: int
    line_starts: tuple[int, ...]

    @classmethod
    def from_text(cls, text: str) -> "SourceLineMap":
        starts = [0]
        starts.extend(index + 1 for index, char in enumerate(text) if char == "\n")
        return cls(len(text.splitlines()), tuple(starts))


@dataclass
class ParsedDocument:
    path: Path
    parse_status: str
    document_type: str
    document: Any = None
    diagnostics: list[str] = field(default_factory=list)
    source_text: str = ""
    documents: tuple[Any, ...] = ()
    tags: tuple[dict[str, Any], ...] = ()
    duplicate_keys: tuple[dict[str, Any], ...] = ()
    source_line_map: SourceLineMap | None = None
    content_sha256: str | None = None
    fault_category: str | None = None
    failure_nature: str | None = None

    @property
    def structurally_analyzable(self) -> bool:
        return self.parse_status == "parsed" and self.document_type in {
            "playbook",
            "tasks",
        }

    @property
    def parse_operations(self) -> int:
        return 1 if self.source_text else 0


# Compatibility name retained while v0.0.4 callers migrate.
DocumentInfo = ParsedDocument


def _cache_encode(value):
    """Encode SafeLoader values as non-executable JSON primitives."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value or value in {float("inf"), float("-inf")}:
            raise TypeError("non-finite floats are not parse-cache serializable")
        return value
    if isinstance(value, bytes):
        return {
            "__ansibleguard_cache_type__": "bytes",
            "value": base64.b64encode(value).decode("ascii"),
        }
    if isinstance(value, datetime):
        return {
            "__ansibleguard_cache_type__": "datetime",
            "value": value.isoformat(),
        }
    if isinstance(value, date):
        return {
            "__ansibleguard_cache_type__": "date",
            "value": value.isoformat(),
        }
    if isinstance(value, list):
        return [_cache_encode(item) for item in value]
    if isinstance(value, tuple):
        return {
            "__ansibleguard_cache_type__": "tuple",
            "items": [_cache_encode(item) for item in value],
        }
    if isinstance(value, set):
        return {
            "__ansibleguard_cache_type__": "set",
            "items": [_cache_encode(item) for item in sorted(value, key=repr)],
        }
    if isinstance(value, SourceMapping):
        return {
            "__ansibleguard_cache_type__": "source-mapping",
            "source_line": value.source_line,
            "key_lines": [
                [_cache_encode(key), line]
                for key, line in value.key_lines.items()
            ],
            "items": [
                [_cache_encode(key), _cache_encode(item)]
                for key, item in value.items()
            ],
        }
    if isinstance(value, dict):
        return {
            "__ansibleguard_cache_type__": "mapping",
            "items": [
                [_cache_encode(key), _cache_encode(item)]
                for key, item in value.items()
            ],
        }
    raise TypeError(f"unsupported parse-cache value: {type(value).__name__}")


def _cache_decode(value):
    if isinstance(value, list):
        return [_cache_decode(item) for item in value]
    if not isinstance(value, dict):
        return value
    kind = value.get("__ansibleguard_cache_type__")
    if kind == "bytes":
        return base64.b64decode(value["value"], validate=True)
    if kind == "date":
        return date.fromisoformat(value["value"])
    if kind == "datetime":
        return datetime.fromisoformat(value["value"])
    if kind == "tuple":
        return tuple(_cache_decode(item) for item in value["items"])
    if kind == "set":
        return set(_cache_decode(item) for item in value["items"])
    if kind == "mapping":
        return {
            _cache_decode(key): _cache_decode(item)
            for key, item in value["items"]
        }
    if kind == "source-mapping":
        return SourceMapping(
            {
                _cache_decode(key): _cache_decode(item)
                for key, item in value["items"]
            },
            source_line=value.get("source_line"),
            key_lines={
                _cache_decode(key): line
                for key, line in value.get("key_lines", [])
            },
        )
    raise ValueError("unknown parse-cache value type")


def _cache_payload(document: ParsedDocument) -> dict:
    return {
        "cache_version": PARSER_CACHE_VERSION,
        "content_sha256": document.content_sha256,
        "parse_status": document.parse_status,
        "document_type": document.document_type,
        "document": _cache_encode(document.document),
        "documents": _cache_encode(document.documents),
        "diagnostics": list(document.diagnostics),
        "tags": _cache_encode(document.tags),
        "duplicate_keys": _cache_encode(document.duplicate_keys),
        "fault_category": document.fault_category,
        "failure_nature": document.failure_nature,
    }


def _document_from_cache(payload, path, common):
    if not isinstance(payload, dict) or payload.get("cache_version") != PARSER_CACHE_VERSION:
        raise ValueError("unsupported parse-cache payload")
    if payload.get("content_sha256") != common["content_sha256"]:
        raise ValueError("parse-cache content hash mismatch")
    return ParsedDocument(
        path=path,
        parse_status=payload["parse_status"],
        document_type=payload["document_type"],
        document=_cache_decode(payload.get("document")),
        diagnostics=list(payload.get("diagnostics") or []),
        documents=tuple(
            _cache_decode(
                payload.get("documents")
                or {"__ansibleguard_cache_type__": "tuple", "items": []}
            )
        ),
        tags=tuple(
            _cache_decode(
                payload.get("tags")
                or {"__ansibleguard_cache_type__": "tuple", "items": []}
            )
        ),
        duplicate_keys=tuple(
            _cache_decode(
                payload.get("duplicate_keys")
                or {"__ansibleguard_cache_type__": "tuple", "items": []}
            )
        ),
        fault_category=payload.get("fault_category"),
        failure_nature=payload.get("failure_nature"),
        **common,
    )


def _classify(path: Path, document: Any) -> str:
    parent = path.parent.name.lower()

    if document is None:
        return "empty"
    if parent in {"vars", "defaults", "group_vars", "host_vars", "env_vars"}:
        return "vars"
    if parent == "meta" or path.name.lower() in {"requirements.yml", "requirements.yaml"}:
        return "metadata"
    if parent in {"tasks", "handlers"}:
        return "tasks"
    if isinstance(document, list):
        if any(
            isinstance(item, dict) and ("hosts" in item or "tasks" in item)
            for item in document
        ):
            return "playbook"
        if all(isinstance(item, dict) for item in document):
            return "tasks"
    if isinstance(document, dict):
        if "hosts" in document or "tasks" in document:
            return "playbook"
        if "galaxy_info" in document or "dependencies" in document or "collections" in document:
            return "metadata"
        return "vars"
    if "$ANSIBLE_VAULT" in str(document):
        return "vault-encrypted"
    return "unknown"


def _load_all_with_evidence(text: str):
    loader = AnsibleSafeLoader(text)
    documents = []
    try:
        while loader.check_data():
            documents.append(loader.get_data())
        return tuple(documents), tuple(loader.ansible_tags), tuple(loader.duplicate_keys)
    finally:
        loader.dispose()


def inspect_document(path, *, cache_dir=None, cache_stats=None) -> ParsedDocument:
    """Read and parse one YAML file exactly once, retaining parse evidence."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return ParsedDocument(path, "invalid-encoding", "unknown", diagnostics=[str(exc)])
    except OSError as exc:
        return ParsedDocument(
            path,
            "read-error",
            "unknown",
            diagnostics=[str(exc)],
            fault_category=(
                "FILESYSTEM_PERMISSION_ERROR"
                if isinstance(exc, PermissionError) else "PARSER_ERROR"
            ),
            failure_nature=(
                "ENVIRONMENT"
                if isinstance(exc, PermissionError) else "DETERMINISTIC_INPUT"
            ),
        )

    common = {
        "source_text": text,
        "source_line_map": SourceLineMap.from_text(text),
        "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    cache_path = None
    if cache_dir is not None:
        cache_key = hashlib.sha256(
            f"{PARSER_CACHE_VERSION}:{path.resolve()}:{common['content_sha256']}".encode()
        ).hexdigest()
        cache_path = Path(cache_dir) / f"{cache_key}.json"
        try:
            cached = (
                _document_from_cache(
                    json.loads(cache_path.read_text(encoding="utf-8")),
                    path,
                    common,
                )
                if cache_path.is_file() else None
            )
            if cached is not None:
                if cache_stats is not None:
                    cache_stats["cache_hits"] = cache_stats.get("cache_hits", 0) + 1
                return cached
        except (
            OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError,
            ValueError, binascii.Error,
        ):
            if cache_stats is not None:
                cache_stats["cache_errors"] = cache_stats.get("cache_errors", 0) + 1
        if cache_stats is not None:
            cache_stats["cache_misses"] = cache_stats.get("cache_misses", 0) + 1

    def finish(result):
        if cache_path is not None:
            try:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = cache_path.with_suffix(".tmp")
                temporary.write_text(
                    json.dumps(
                        _cache_payload(result),
                        sort_keys=True,
                        separators=(",", ":"),
                        allow_nan=False,
                    ),
                    encoding="utf-8",
                )
                temporary.replace(cache_path)
            except (OSError, TypeError, ValueError):
                if cache_stats is not None:
                    cache_stats["cache_errors"] = cache_stats.get("cache_errors", 0) + 1
        return result

    if not text.strip():
        return finish(ParsedDocument(path, "empty", "empty", **common))
    if text.lstrip().startswith("$ANSIBLE_VAULT"):
        return finish(ParsedDocument(path, "unsupported", "vault-encrypted", **common))

    try:
        documents, tags, duplicate_keys = _load_all_with_evidence(text)
    except yaml.YAMLError as exc:
        return finish(ParsedDocument(
            path, "invalid", "unknown", diagnostics=[str(exc)], **common
        ))

    diagnostics = [
        f"Duplicate key {item['key']!r} at line {item['line']}, column {item['column']}."
        for item in duplicate_keys
    ]
    evidence = {
        **common,
        "documents": documents,
        "tags": tags,
        "duplicate_keys": duplicate_keys,
        "diagnostics": diagnostics,
    }
    if not documents:
        return finish(ParsedDocument(path, "empty", "empty", **evidence))
    if len(documents) != 1:
        # Multi-document input is parsed successfully and retained. Structural
        # detector migration is explicit: no detector receives an ambiguous
        # merged value in the meantime.
        return finish(ParsedDocument(
            path,
            "parsed",
            "multi-document",
            documents,
            **evidence,
        ))
    document = documents[0]
    return finish(ParsedDocument(path, "parsed", _classify(path, document), document, **evidence))

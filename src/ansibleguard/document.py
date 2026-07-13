"""Safe YAML loading and lightweight Ansible document classification."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class AnsibleSafeLoader(yaml.SafeLoader):
    """Safe loader that preserves, but never executes, unknown Ansible tags."""


def _construct_unknown(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_mapping(node)
    return {"__ansible_tag__": f"!{tag_suffix}", "value": value}


AnsibleSafeLoader.add_multi_constructor("!", _construct_unknown)


@dataclass
class DocumentInfo:
    path: Path
    parse_status: str
    document_type: str
    document: Any = None
    diagnostics: list[str] = field(default_factory=list)

    @property
    def structurally_analyzable(self) -> bool:
        return self.parse_status == "parsed" and self.document_type in {
            "playbook",
            "tasks",
        }


def _classify(path: Path, document: Any) -> str:
    parts = {part.lower() for part in path.parts}
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


def inspect_document(path) -> DocumentInfo:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return DocumentInfo(path, "read-error", "unknown", diagnostics=[str(exc)])

    if not text.strip():
        return DocumentInfo(path, "empty", "empty")
    if text.lstrip().startswith("$ANSIBLE_VAULT"):
        return DocumentInfo(path, "unsupported", "vault-encrypted")

    try:
        documents = list(yaml.load_all(text, Loader=AnsibleSafeLoader))
    except yaml.YAMLError as exc:
        return DocumentInfo(path, "invalid", "unknown", diagnostics=[str(exc)])

    if len(documents) != 1:
        return DocumentInfo(
            path,
            "unsupported",
            "multi-document",
            documents,
            ["Multiple YAML documents are not structurally analyzed yet."],
        )
    document = documents[0]
    return DocumentInfo(path, "parsed", _classify(path, document), document)

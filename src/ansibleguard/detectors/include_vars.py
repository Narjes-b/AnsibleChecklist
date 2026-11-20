"""Conservative repository-aware validation of static include_vars tasks."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re

import yaml

from ansibleguard.include_vars_semantics import (
    expand_include_vars_target,
    static_include_vars_target,
)


INCLUDE_KEYS = {"include_vars", "ansible.builtin.include_vars"}
REFERENCE_KEYS = {"when", "changed_when", "failed_when", "until"}
EXCLUDED_DIRECTORIES = {".git", ".venv", "venv", "ansibleguard-output"}


def _scan_root(path: Path) -> Path:
    """Choose a bounded local root when no repository index was supplied."""
    parts = path.resolve().parts
    indexes = [index for index, part in enumerate(parts) if part == "roles"]
    if indexes and indexes[-1] + 1 < len(parts):
        return Path(*parts[: indexes[-1] + 2])
    if path.parent.name in {"tasks", "handlers", "playbooks"}:
        return path.parent.parent
    return path.parent


def _tasks(value):
    if not isinstance(value, list):
        return
    for item in value:
        if not isinstance(item, dict):
            continue
        if "hosts" in item:
            for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                yield from _tasks(item.get(section)) or []
            continue
        yield item
        for section in ("block", "rescue", "always"):
            yield from _tasks(item.get(section)) or []


def _static_include(task, source: Path):
    for key in INCLUDE_KEYS:
        if key not in task:
            continue
        return static_include_vars_target(task[key], source)
    return None


def _expand_include_target(path, repository_context=None):
    """Expand a static include_vars directory without leaving the population."""
    selected = (
        repository_context.parsed_documents
        if repository_context is not None else None
    )
    return expand_include_vars_target(path, selected)


def _referenced_names(document, names, namespace=None):
    referenced = set()

    def walk(value, parent_key=None):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in INCLUDE_KEYS or key in {"name", "register"}:
                    continue
                walk(child, key)
        elif isinstance(value, list):
            for child in value:
                walk(child, parent_key)
        elif isinstance(value, str):
            # A dynamic variable lookup can address any included key.  Static
            # analysis cannot prove a particular definition unused in this
            # case, so preserve the entire include rather than reporting a
            # false unused-include finding.
            dynamic_lookup = re.search(r"\b(?:vars|hostvars)\s*\[\s*(?!['\"])", value) or re.search(
                r"\b(?:lookup|query)\s*\(\s*(['\"])vars\1\s*,\s*(?!['\"])",
                value,
            )
            if namespace:
                dynamic_lookup = dynamic_lookup or re.search(
                    rf"\b(?:vars\s*\[\s*(['\"]){re.escape(namespace)}\1\s*\]|"
                    rf"{re.escape(namespace)})\s*\[\s*(?!['\"])",
                    value,
                )
            if dynamic_lookup:
                referenced.update(names)
            else:
                for name in names:
                    target = f"{namespace}.{name}" if namespace else name
                    if re.search(rf"{{{{[^}}]*\b{re.escape(target)}\b", value) or (
                        parent_key in REFERENCE_KEYS
                        and re.search(rf"(?<![\w.]){re.escape(target)}\b", value)
                    ) or re.search(
                        rf"\bvars\s*\[\s*(['\"]){re.escape(target)}\1\s*\]",
                        value,
                    ) or re.search(
                        rf"\b(?:lookup|query)\s*\(\s*(['\"])vars\1\s*,\s*(['\"]){re.escape(target)}\2",
                        value,
                    ):
                        referenced.add(name)

    walk(document)
    return referenced


@lru_cache(maxsize=32)
def _repository_documents(root_text):
    """Parse repository YAML once per scan root for predictable scan cost."""
    root = Path(root_text)
    documents = []
    for pattern in ("*.yml", "*.yaml"):
        for candidate in root.rglob(pattern):
            if any(part in EXCLUDED_DIRECTORIES for part in candidate.parts):
                continue
            try:
                documents.append(
                    (candidate.resolve(), yaml.safe_load(candidate.read_text(encoding="utf-8")))
                )
            except (OSError, UnicodeError, yaml.YAMLError):
                continue
    return tuple(documents)


def detect_unused_include_vars(
    playbook_file,
    vars_folder=None,
    symbol_index=None,
    repository_context=None,
    parsed_document=None,
):
    """Report only a statically resolved vars file with zero repository uses.

    Dynamic includes, missing files, non-mapping vars files, and partially used
    files are deliberately not classified.  Those cases do not prove that the
    include itself is unnecessary.
    """
    source = Path(playbook_file).resolve()
    if parsed_document is None and repository_context is not None:
        parsed_document = repository_context.parsed_documents.get(source)
    if parsed_document is not None:
        if not parsed_document.structurally_analyzable:
            return 0, []
        document = parsed_document.document
    else:
        try:
            document = yaml.safe_load(source.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            return 0, []
    includes = []
    for task in _tasks(document) or []:
        resolved = _static_include(task, source)
        if resolved:
            path, namespace = resolved
            if vars_folder and not path.is_absolute():
                path = (Path(vars_folder) / path).resolve()
            includes.extend(
                (candidate, namespace, path.is_dir())
                for candidate in _expand_include_target(path, repository_context)
            )
    if not includes:
        return 0, []

    root = (
        Path(symbol_index.root).resolve()
        if symbol_index is not None
        else _scan_root(source)
    )
    if repository_context is not None:
        repository_documents = tuple(
            (candidate, parsed.document)
            for candidate, parsed in repository_context.parsed_documents.items()
            if parsed.structurally_analyzable
        )
    else:
        repository_documents = _repository_documents(str(root.resolve()))

    warnings = []
    for included_path, namespace, from_directory in includes:
        included_document = (
            repository_context.parsed_documents.get(included_path)
            if repository_context is not None else None
        )
        if included_document is not None:
            if not included_document.structurally_analyzable:
                continue
            variables = included_document.document
        else:
            # A shared-context scan deliberately abstains when the target is
            # outside its selected population. Standalone calls retain the
            # bounded compatibility fallback.
            if repository_context is not None or not included_path.is_file():
                continue
            try:
                variables = yaml.safe_load(included_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, yaml.YAMLError):
                continue
        if not isinstance(variables, dict) or not variables:
            continue
        names = {str(name) for name in variables}
        used = set()
        for candidate, candidate_document in repository_documents:
            if candidate == included_path:
                continue
            used.update(_referenced_names(candidate_document, names, namespace))
        if not used:
            relative = included_path
            try:
                relative = included_path.relative_to(root)
            except ValueError:
                pass
            target_kind = "directory" if from_directory else "file"
            warnings.append(
                f"Static include_vars {target_kind} '{relative}' defines {len(names)} variable(s), none referenced elsewhere in the repository."
            )
    return len(warnings), warnings

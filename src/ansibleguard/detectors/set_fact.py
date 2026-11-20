import re
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path

import yaml

from ansibleguard.document import AnsibleSafeLoader
from ansibleguard.detectors.source_lines import source_line


EXCLUDED_DIRECTORIES = {".git", ".venv", "venv", "ansibleguard-output"}
SET_FACT_KEYS = {"set_fact", "ansible.builtin.set_fact"}


@lru_cache(maxsize=32)
def _repository_documents(root_text):
    """Parse a checkout once instead of once for every analyzed YAML file."""
    root = Path(root_text)
    documents = []
    for pattern in ("*.yml", "*.yaml"):
        for candidate in root.rglob(pattern):
            if any(part in EXCLUDED_DIRECTORIES for part in candidate.parts):
                continue
            try:
                documents.append(
                    (
                        candidate.resolve(),
                        yaml.load(
                            candidate.read_text(encoding="utf-8"),
                            Loader=AnsibleSafeLoader,
                        ),
                    )
                )
            except (OSError, UnicodeError, yaml.YAMLError):
                continue
    return tuple(documents)


def _is_jinja_reference(value, fact_name):
    """Return whether value contains a Jinja reference to fact_name.

    Ordinary prose containing the same word is not a variable use. Attribute
    access and filter chains are valid uses.
    """
    return bool(
        re.search(
            rf"{{\{{\s*{re.escape(fact_name)}\s*(?:\||}}|\.)",
            value,
        )
    )


def _is_condition_reference(value, fact_name):
    """Recognize bare variables in Ansible conditional expressions."""
    return bool(re.search(rf"(?<![\w.]){re.escape(fact_name)}\b", value))


def _is_indirect_reference(value, fact_name):
    """Recognize common explicit dynamic access to a statically named fact."""
    quoted = rf"(['\"]){re.escape(fact_name)}\1"
    return bool(
        re.search(rf"\bvars\s*\[\s*{quoted}\s*\]", value)
        or re.search(rf"\bhostvars\s*\[[^]]+\]\s*\[\s*{quoted}\s*\]", value)
        or re.search(
            rf"\b(?:lookup|query)\s*\(\s*(['\"])vars\1\s*,\s*{quoted}",
            value,
        )
    )


def _has_dynamic_variable_access(value):
    """Detect vars/hostvars lookups whose key is not a quoted literal."""
    if not isinstance(value, str):
        return False
    return bool(
        re.search(r"\bvars\s*\[\s*(?!['\"])[^\]]+\]", value)
        or re.search(
            r"\bhostvars\s*\[[^]]+\]\s*\[\s*(?!['\"])[^\]]+\]", value
        )
    )


def _referenced_fact_names(value, parent_key=None):
    """Extract possible fact references once per string.

    The former implementation tested every string against every set-fact
    definition, which made a file with N assignments approach O(N²).  These
    bounded extractors preserve the supported direct/indirect forms and let
    the caller intersect them with the known assignment names.
    """
    if not isinstance(value, str):
        return set()
    names = set(re.findall(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\||}|\.)", value))
    names.update(
        match[1]
        for match in re.findall(
            r"\b(?:vars|hostvars\s*\[[^]]+\])\s*\[\s*(['\"])([A-Za-z_][A-Za-z0-9_]*)\1\s*\]",
            value,
        )
    )
    for match in re.finditer(
        r"\b(?:lookup|query)\s*\(\s*(['\"])vars\1\s*,\s*(['\"])([A-Za-z_][A-Za-z0-9_]*)\2",
        value,
    ):
        names.add(match.group(3))
    if parent_key in {"when", "changed_when", "failed_when", "until", "that"}:
        names.update(re.findall(r"(?<![.])\b([A-Za-z_][A-Za-z0-9_]*)\b", value))
    return names


def find_unnecessary_set_facts(yaml_content, additional_documents=()):
    try:
        data = yaml.load(yaml_content, Loader=AnsibleSafeLoader)
    except yaml.YAMLError as e:
        print("Error parsing YAML:", e)
        return

    set_facts = set()
    used_facts = set()
    dynamic_access = False

    def find_facts_in_data(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in SET_FACT_KEYS:
                    if isinstance(value, dict):
                        for fact_name in value.keys():
                            if fact_name == "cacheable":
                                continue
                            if isinstance(fact_name, str) and not re.search(
                                r"{{|{%", fact_name
                            ):
                                set_facts.add(fact_name)
                else:
                    find_facts_in_data(value)
        elif isinstance(data, list):
            for item in data:
                find_facts_in_data(item)

    find_facts_in_data(data)

    def find_used_facts(data, parent_key=None):
        nonlocal dynamic_access
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    dynamic_access = dynamic_access or _has_dynamic_variable_access(value)
                    used_facts.update(
                        set_facts.intersection(_referenced_fact_names(value, key))
                    )
                else:
                    find_used_facts(value, key)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    dynamic_access = dynamic_access or _has_dynamic_variable_access(item)
                    used_facts.update(
                        set_facts.intersection(
                            _referenced_fact_names(item, parent_key)
                        )
                    )
                else:
                    find_used_facts(item, parent_key)

    find_used_facts(data)
    for document in additional_documents:
        find_used_facts(document)
    if dynamic_access:
        # A dynamic key may resolve to any fact name; static analysis cannot
        # prove one of the assignments is dead.
        used_facts.update(set_facts)
    # print("Set facts:", set_facts)
    # print("Used facts:", used_facts)
    unused_facts = set_facts - used_facts
    return unused_facts


def unnecessary_set_fact_details(
    file_path,
    symbol_index=None,
    repository_context=None,
    parsed_document=None,
):
    try:
        path = Path(file_path).resolve()
        if parsed_document is None and repository_context is not None:
            parsed_document = repository_context.parsed_documents.get(path)
        if parsed_document is not None:
            if not parsed_document.structurally_analyzable:
                return None
            yaml_content = parsed_document.source_text
            parsed_data = parsed_document.document
        else:
            with open(path, "r", encoding="utf-8") as f:
                yaml_content = f.read()
            parsed_data = yaml.load(yaml_content, Loader=AnsibleSafeLoader)
        if repository_context is not None:
            unused_assignments = set()
            for task in repository_context.tasks_for(path):
                action = (task.action or "").rsplit(".", 1)[-1]
                if action != "set_fact":
                    continue
                payload = task.raw.get(task.action)
                if payload is None:
                    payload = task.raw.get("set_fact")
                if not isinstance(payload, Mapping):
                    continue
                # Cacheable facts intentionally persist into the fact cache;
                # lack of a static consumer is not evidence they are useless.
                if payload.get("cacheable") is True:
                    continue
                for fact in task.set_fact_definitions:
                    if not repository_context.variable_used_after(
                        fact, path, task.ordinal
                    ):
                        unused_assignments.add((
                            fact, source_line(payload, fact, fallback=None)
                        ))
        elif symbol_index is not None:
            additional_documents = [
                document
                for candidate, document in _repository_documents(
                    str(symbol_index.root.resolve())
                )
                if candidate != path
            ]
            unused_facts = find_unnecessary_set_facts(
                yaml_content, additional_documents=additional_documents
            )
        else:
            # Legacy single-file API retains its behavior, but the repository
            # engine never reparses a ParsedDocument here.
            set_facts = set()
            used_facts = set()
            dynamic_access = False

            def collect(value, parent_key=None):
                nonlocal dynamic_access
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key in SET_FACT_KEYS and isinstance(child, dict):
                            set_facts.update(
                                str(name) for name in child
                                if name != "cacheable"
                                and not re.search(r"{{|{%", str(name))
                            )
                        collect(child, key)
                elif isinstance(value, list):
                    for child in value:
                        collect(child, parent_key)
                elif isinstance(value, str):
                    dynamic_access = dynamic_access or _has_dynamic_variable_access(value)
                    used_facts.update(_referenced_fact_names(value, parent_key))

            collect(parsed_data)
            unused_facts = set() if dynamic_access else set_facts - used_facts
        if repository_context is None and unused_facts is None:
            return None
        lines = yaml_content.splitlines()
        details = []
        assignments = (
            sorted(unused_assignments, key=lambda item: (item[0], item[1] or 0))
            if repository_context is not None
            else [(fact_name, None) for fact_name in sorted(unused_facts)]
        )
        for fact_name, located_line in assignments:
            line = located_line or next(
                (
                    index
                    for index, value in enumerate(lines, 1)
                    if re.match(rf"^\s*{re.escape(fact_name)}\s*:", value)
                ),
                1,
            )
            details.append(
                {
                    "line": line,
                    "variable": fact_name,
                    "issue": f"set_fact variable '{fact_name}' is never used.",
                    "semantic_status": "UNCERTAIN",
                    "resolution_status": "BOUNDED_GRAPH_UNKNOWN",
                    "resolution_scope": "repository-static",
                    "uncertainty_sources": [
                        "bounded_execution_graph_cannot_prove_dead_assignment"
                    ],
                    "resolution_evidence": {
                        "proved": ["no_use_in_bounded_execution_graph"],
                        "blockers": [
                            "bounded_execution_graph_cannot_prove_dead_assignment"
                        ],
                    },
                    "confidence": "low",
                }
            )
        return details
    except Exception as e:
        print(f"Could not read file {file_path}. Error: {e}")
        return None


def set_fact(
    file_path,
    symbol_index=None,
    repository_context=None,
    parsed_document=None,
):
    details = unnecessary_set_fact_details(
        file_path,
        symbol_index=symbol_index,
        repository_context=repository_context,
        parsed_document=parsed_document,
    )
    return len(details) if details is not None else None


if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    result = set_fact(TEST_PLAYBOOK)
    if result is not None:
        print("unused facts=", result)

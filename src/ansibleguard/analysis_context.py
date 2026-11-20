"""Shared immutable repository semantics for the analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Mapping

from jinja2 import Environment, TemplateSyntaxError, meta, nodes

from .document import ParsedDocument, inspect_document
from .compat import StrEnum
from .file_manifest import DEPENDENCY_MANIFEST_FILENAMES, classify_source_file
from .role_context import resolve_role_context
from .task_semantics import task_action


_JINJA_REFERENCE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)")
_JINJA_ENVIRONMENT = Environment()
_ROLE_PATH_INCLUDE = re.compile(r"^\s*{{\s*role_path\s*}}/(.+?)\s*$")
_TASK_SECTIONS = ("pre_tasks", "tasks", "post_tasks", "handlers")
_BUILTIN_FACT_ACTIONS = frozenset({"package_facts", "service_facts"})
_INCLUDE_ACTIONS = (
    "include_vars", "ansible.builtin.include_vars",
    "include_tasks", "ansible.builtin.include_tasks",
    "import_tasks", "ansible.builtin.import_tasks",
    "import_playbook", "ansible.builtin.import_playbook",
    "include_role", "ansible.builtin.include_role",
    "import_role", "ansible.builtin.import_role",
)


def _jinja_placeholder(value=None, *args, **kwargs):
    return value


def _freeze_value(value):
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_value(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)
    return value


class IncludeResolution(StrEnum):
    STATIC_RESOLVED = "STATIC_RESOLVED"
    STATIC_MISSING = "STATIC_MISSING"
    DYNAMIC = "DYNAMIC"
    RUNTIME_GENERATED = "RUNTIME_GENERATED"
    EXTERNAL = "EXTERNAL"
    INACCESSIBLE = "INACCESSIBLE"
    STATIC_ROLE = "STATIC_ROLE"
    DYNAMIC_ROLE = "DYNAMIC_ROLE"


@dataclass(frozen=True)
class IncludeRelationship:
    source: str
    action: str
    raw_target: str | None
    resolved_target: str | None
    resolution: IncludeResolution
    task_ordinal: int | None = None


@dataclass(frozen=True)
class FileContext:
    path: Path
    relative_path: str
    project_root: Path
    role: str | None
    role_section: str | None
    classification: str
    classification_confidence: str
    source_hash: str | None
    parse_status: str
    document_type: str


@dataclass(frozen=True)
class TaskInfo:
    file: str
    ordinal: int
    play: int
    task_path: tuple[int, ...]
    raw: Mapping[str, Any]
    name: str | None
    action: str | None
    jinja_references: tuple[str, ...]
    register_definitions: tuple[str, ...]
    set_fact_definitions: tuple[str, ...]
    conditions: tuple[str, ...]
    tags: tuple[str, ...]
    no_log: Any
    includes: tuple[IncludeRelationship, ...]


@dataclass(frozen=True)
class DependencyModel:
    declared_roles: tuple[str, ...]
    declared_collections: tuple[str, ...]
    local_collections: tuple[str, ...]
    execution_environment_dependencies: tuple[str, ...]
    declared_variable_prefixes: tuple[str, ...]
    source_files: tuple[str, ...]


@dataclass(frozen=True)
class ProjectModel:
    types: tuple[str, ...]
    ansible_roots: tuple[str, ...]
    configs: Mapping[str, str]
    requirements: tuple[str, ...]
    molecule: bool
    inventory_sources: tuple[str, ...]
    configs_by_root: Mapping[str, Mapping[str, str]]
    dependencies: DependencyModel
    dependencies_by_root: Mapping[str, DependencyModel]


@dataclass(frozen=True)
class RepositoryAnalysisContext:
    root: Path
    parsed_documents: Mapping[Path, ParsedDocument]
    file_contexts: Mapping[Path, FileContext]
    tasks_by_file: Mapping[Path, tuple[TaskInfo, ...]]
    include_relationships: tuple[IncludeRelationship, ...]
    project_model: ProjectModel
    selected_population: tuple[str, ...]
    performance: Mapping[str, Any]
    variable_usage: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: MappingProxyType({}), compare=False
    )
    dynamic_variable_access: bool = field(default=False, compare=False)
    dynamic_variable_access_files: tuple[str, ...] = field(
        default=(), compare=False
    )
    execution_components: Mapping[str, int] = field(
        default_factory=lambda: MappingProxyType({}), compare=False
    )
    runtime_uncertainty: Mapping[Path, tuple[tuple[str, ...], ...]] = field(
        default_factory=lambda: MappingProxyType({}), compare=False
    )
    role_roots: Mapping[str, Path] = field(
        default_factory=lambda: MappingProxyType({}), compare=False
    )
    role_analysis_anchor: Path | None = field(default=None, compare=False)
    module_metadata: Mapping[str, Mapping[str, Any]] = field(
        default_factory=lambda: MappingProxyType({}), compare=False
    )
    symbol_graph: Any = field(default=None, compare=False)

    def document_for(self, path) -> ParsedDocument:
        return self.parsed_documents[Path(path).resolve()]

    def file_context_for(self, path) -> FileContext:
        return self.file_contexts[Path(path).resolve()]

    def tasks_for(self, path) -> tuple[TaskInfo, ...]:
        return self.tasks_by_file.get(Path(path).resolve(), ())

    def uncertainty_for(self, path, task_ordinal: int) -> tuple[str, ...]:
        by_task = self.runtime_uncertainty.get(Path(path).resolve(), ())
        if not by_task:
            return ()
        index = max(0, min(int(task_ordinal), len(by_task) - 1))
        return by_task[index]

    def external_dependency_may_define(self, name: str) -> bool:
        """Return whether a declared external role plausibly owns *name*."""
        return any(
            name.startswith(prefix)
            for prefix in self.project_model.dependencies.declared_variable_prefixes
        )

    def variable_used_after(self, name, path, task_ordinal) -> bool:
        """Return whether a fact has a reachable static consumer.

        Same-file consumers must follow the definition. Cross-file consumers
        must share a statically connected execution component; unrelated roles
        and examples cannot keep a fact alive merely by reusing its name.
        """
        path = Path(path).resolve()
        relative = _relative(path, self.root)
        for task in self.tasks_for(path):
            if task.ordinal > task_ordinal and name in task.jinja_references:
                return True
        component = self.execution_components.get(relative)
        producer_role = resolve_role_context(path, self.root)
        for consumer in self.variable_usage.get(name, ()):
            if consumer != relative and component is not None and (
                self.execution_components.get(consumer) == component
            ):
                return True
            if consumer != relative and producer_role is not None:
                consumer_role = resolve_role_context(
                    self.root / consumer, self.root
                )
                if (
                    consumer_role is not None
                    and consumer_role.identifier == producer_role.identifier
                ):
                    return True
        if relative in self.dynamic_variable_access_files:
            # The index is file-scoped rather than task-scoped; conservatively
            # retain facts when dynamic access occurs in their own file.
            return True
        return component is not None and any(
            self.execution_components.get(candidate) == component
            for candidate in self.dynamic_variable_access_files
            if candidate != relative
        )

    def with_symbol_graph(self, graph) -> "RepositoryAnalysisContext":
        return RepositoryAnalysisContext(
            root=self.root,
            parsed_documents=self.parsed_documents,
            file_contexts=self.file_contexts,
            tasks_by_file=self.tasks_by_file,
            include_relationships=self.include_relationships,
            project_model=self.project_model,
            selected_population=self.selected_population,
            performance=self.performance,
            variable_usage=self.variable_usage,
            dynamic_variable_access=self.dynamic_variable_access,
            dynamic_variable_access_files=self.dynamic_variable_access_files,
            execution_components=self.execution_components,
            runtime_uncertainty=self.runtime_uncertainty,
            role_roots=self.role_roots,
            role_analysis_anchor=self.role_analysis_anchor,
            module_metadata=self.module_metadata,
            symbol_graph=graph,
        )

    def with_module_metadata(self, metadata, telemetry=None) -> "RepositoryAnalysisContext":
        performance = dict(self.performance)
        if telemetry:
            performance.update({
                f"module_metadata_{key}": value
                for key, value in telemetry.items()
                if isinstance(value, (int, float, str))
            })
        return RepositoryAnalysisContext(
            root=self.root,
            parsed_documents=self.parsed_documents,
            file_contexts=self.file_contexts,
            tasks_by_file=self.tasks_by_file,
            include_relationships=self.include_relationships,
            project_model=self.project_model,
            selected_population=self.selected_population,
            performance=MappingProxyType(performance),
            variable_usage=self.variable_usage,
            dynamic_variable_access=self.dynamic_variable_access,
            dynamic_variable_access_files=self.dynamic_variable_access_files,
            execution_components=self.execution_components,
            runtime_uncertainty=self.runtime_uncertainty,
            role_roots=self.role_roots,
            role_analysis_anchor=self.role_analysis_anchor,
            module_metadata=_freeze_value(metadata or {}),
            symbol_graph=self.symbol_graph,
        )


_REFERENCE_PATTERNS = (
    re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\||}|\.)"),
    re.compile(
        r"\b(?:vars|hostvars\s*\[[^]]+\])\s*\[\s*(['\"])([A-Za-z_][A-Za-z0-9_]*)\1\s*\]"
    ),
    re.compile(
        r"\b(?:lookup|query)\s*\(\s*(['\"])vars\1\s*,\s*"
        r"(['\"])([A-Za-z_][A-Za-z0-9_]*)\2"
    ),
)
_DYNAMIC_VARIABLE_ACCESS = re.compile(
    r"\bvars\s*\[\s*(?!['\"])[^\]]+\]"
    r"|\bhostvars\s*\[[^]]+\]\s*\[\s*(?!['\"])[^\]]+\]"
)
_CONDITION_KEYWORDS = {
    "and", "or", "not", "in", "is", "defined", "undefined",
    "true", "false", "none", "null",
}


def _condition_names(value):
    without_literals = re.sub(r"(['\"]).*?\1", "", value)
    return {
        name
        for name in re.findall(
            r"(?<![.])\b([A-Za-z_][A-Za-z0-9_]*)\b", without_literals
        )
        if name.lower() not in _CONDITION_KEYWORDS
    }


def _jinja_names(value, *, expression=False):
    """Extract undeclared Jinja names from any position in a string."""
    if not isinstance(value, str):
        return set()
    source = value
    if expression and "{{" not in source and "{%" not in source:
        source = "{{ " + source + " }}"
    try:
        syntax_tree = _JINJA_ENVIRONMENT.parse(source)
        filter_names = {
            node.name for node in syntax_tree.find_all(nodes.Filter)
        }
        test_names = {node.name for node in syntax_tree.find_all(nodes.Test)}
        analysis_environment = _JINJA_ENVIRONMENT.overlay()
        for name in filter_names:
            analysis_environment.filters.setdefault(name, _jinja_placeholder)
        for name in test_names:
            analysis_environment.tests.setdefault(name, _jinja_placeholder)
        return set(meta.find_undeclared_variables(
            analysis_environment.parse(source)
        ))
    except TemplateSyntaxError:
        return set(_JINJA_REFERENCE.findall(value))


def _build_variable_usage_index(documents, root):
    usage = {}
    dynamic_files = set()
    condition_keys = {"when", "changed_when", "failed_when", "until", "that"}

    def walk(value, relative, parent_key=None):
        if isinstance(value, Mapping):
            for key, child in value.items():
                if key == "register":
                    continue
                walk(child, relative, str(key))
        elif isinstance(value, (list, tuple)):
            for child in value:
                walk(child, relative, parent_key)
        elif isinstance(value, str):
            if _DYNAMIC_VARIABLE_ACCESS.search(value):
                dynamic_files.add(relative)
            names = _jinja_names(value, expression=parent_key in condition_keys)
            names.update(match[1] for match in _REFERENCE_PATTERNS[1].findall(value))
            names.update(match[2] for match in _REFERENCE_PATTERNS[2].findall(value))
            if parent_key in condition_keys:
                names.update(_condition_names(value))
            for name in names:
                usage.setdefault(name, set()).add(relative)

    for path, parsed in documents.items():
        if parsed.structurally_analyzable:
            walk(parsed.document, _relative(path, root))
    for template in sorted(Path(root).rglob("*.j2")):
        if any(part in {".git", ".venv", "venv", "ansibleguard-output"} for part in template.parts):
            continue
        try:
            text = template.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        relative = _relative(template, root)
        if _DYNAMIC_VARIABLE_ACCESS.search(text):
            dynamic_files.add(relative)
        for name in _jinja_names(text):
            usage.setdefault(name, set()).add(relative)
    return (
        MappingProxyType({
            name: tuple(sorted(paths)) for name, paths in usage.items()
        }),
        tuple(sorted(dynamic_files)),
    )


def _build_execution_components(root, documents, relationships):
    """Index statically connected files without inventing execution edges."""
    relatives = {_relative(path, root) for path in documents}
    adjacency = {relative: set() for relative in relatives}
    for edge in relationships:
        if edge.resolution not in {
            IncludeResolution.STATIC_RESOLVED,
            IncludeResolution.STATIC_ROLE,
        } or not edge.resolved_target:
            continue
        target = edge.resolved_target
        if target not in relatives:
            for suffix in ("tasks/main.yml", "tasks/main.yaml", "main.yml", "main.yaml"):
                candidate = (Path(target) / suffix).as_posix()
                if candidate in relatives:
                    target = candidate
                    break
        if edge.source in adjacency and target in adjacency:
            adjacency[edge.source].add(target)
            adjacency[target].add(edge.source)
    components = {}
    component_id = 0
    for relative in sorted(relatives):
        if relative in components:
            continue
        pending = [relative]
        while pending:
            current = pending.pop()
            if current in components:
                continue
            components[current] = component_id
            pending.extend(adjacency[current] - components.keys())
        component_id += 1
    return MappingProxyType(components)


def _build_runtime_uncertainty_index(
    root, documents, tasks_by_file, relationships, project_model
):
    selected = set(documents)
    edges_by_source = {}
    for edge in relationships:
        edges_by_source.setdefault(edge.source, []).append(edge)
    dynamic_inventory = False
    inventory_roots = tuple(root / relative for relative in project_model.inventory_sources)
    for path, parsed in documents.items():
        if any(path == base or base in path.parents for base in inventory_roots):
            if isinstance(parsed.document, Mapping) and isinstance(
                parsed.document.get("plugin"), str
            ):
                dynamic_inventory = True
                break
    labels = {
        IncludeResolution.DYNAMIC: "dynamic_include",
        IncludeResolution.RUNTIME_GENERATED: "runtime_generated_include",
        IncludeResolution.EXTERNAL: "external_include",
        IncludeResolution.INACCESSIBLE: "inaccessible_include",
        IncludeResolution.DYNAMIC_ROLE: "dynamic_role",
    }
    result = {}
    for path, tasks in tasks_by_file.items():
        relative = _relative(path, root)
        edges = sorted(
            edges_by_source.get(relative, ()),
            key=lambda edge: edge.task_ordinal if edge.task_ordinal is not None else -1,
        )
        base = set()
        parsed = documents[path].document
        entries = parsed if isinstance(parsed, list) else ()
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            references = entry.get("vars_files") or ()
            if isinstance(references, str):
                references = (references,)
            if any(
                isinstance(reference, str)
                and ("{{" in reference or "{%" in reference)
                for reference in references
            ):
                base.add("dynamic_vars_files")
        if dynamic_inventory:
            base.add("possible_dynamic_inventory_definition")
        cumulative = set(base)
        by_task = []
        edge_index = 0
        for ordinal in range(max(1, len(tasks))):
            while edge_index < len(edges):
                edge = edges[edge_index]
                edge_ordinal = edge.task_ordinal
                if edge_ordinal is not None and edge_ordinal > ordinal:
                    break
                if edge.resolution in labels:
                    cumulative.add(labels[edge.resolution])
                elif (
                    edge.action.rsplit(".", 1)[-1] == "include_vars"
                    and edge.resolution == IncludeResolution.STATIC_RESOLVED
                    and edge.resolved_target
                ):
                    target = (root / edge.resolved_target).resolve()
                    represented = target in selected or any(
                        target in candidate.parents for candidate in selected
                    )
                    if not represented:
                        cumulative.add("static_include_vars_outside_population")
                edge_index += 1
            if ordinal < len(tasks):
                task = tasks[ordinal]
                action = (task.action or "").lower()
                short_action = action.rsplit(".", 1)[-1]
                if (
                    action
                    and short_action not in _BUILTIN_FACT_ACTIONS
                    and not action.startswith(
                        ("ansible.builtin.", "ansible.legacy.")
                    )
                    and (action.endswith("_facts") or action.endswith(".facts"))
                ):
                    cumulative.add("custom_module_fact")
            by_task.append(tuple(sorted(cumulative)))
        result[path] = tuple(by_task)
    return MappingProxyType(result)


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _strings(item)


def _include_target(action: str, value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        for key in ("file", "name", "dir", "_raw_params"):
            if isinstance(value.get(key), str):
                return value[key]
    return None


def classify_include(source: Path, root: Path, action: str, value: Any, ordinal=None):
    raw = _include_target(action, value)
    relative_source = _relative(source, root)
    if action.rsplit(".", 1)[-1] in {"include_role", "import_role"}:
        resolution = (
            IncludeResolution.DYNAMIC_ROLE
            if raw is None or "{{" in raw or "{%" in raw
            else IncludeResolution.STATIC_ROLE
        )
        return IncludeRelationship(
            relative_source,
            action,
            raw,
            f"roles/{raw}" if resolution == IncludeResolution.STATIC_ROLE else None,
            resolution,
            ordinal,
        )
    if raw is None:
        return IncludeRelationship(relative_source, action, raw, None, IncludeResolution.DYNAMIC, ordinal)
    role_path_match = _ROLE_PATH_INCLUDE.fullmatch(raw)
    if role_path_match and not re.search(r"{{|{%", role_path_match.group(1)):
        role_context = resolve_role_context(source, root)
        if role_context is None:
            return IncludeRelationship(
                relative_source, action, raw, None,
                IncludeResolution.DYNAMIC, ordinal,
            )
        candidate = (role_context.root / role_path_match.group(1)).resolve()
    elif "{{" in raw or "{%" in raw:
        return IncludeRelationship(
            relative_source, action, raw, None,
            IncludeResolution.DYNAMIC, ordinal,
        )
    else:
        candidate = Path(raw)
    if candidate.is_absolute():
        try:
            candidate.resolve().relative_to(root.resolve())
        except ValueError:
            kind = IncludeResolution.RUNTIME_GENERATED if str(candidate).startswith(("/tmp/", "/var/tmp/")) else IncludeResolution.EXTERNAL
            return IncludeRelationship(relative_source, action, raw, str(candidate), kind, ordinal)
    else:
        candidate = (source.parent / candidate).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return IncludeRelationship(relative_source, action, raw, str(candidate), IncludeResolution.EXTERNAL, ordinal)
    try:
        exists = candidate.is_file() or candidate.is_dir()
    except OSError:
        return IncludeRelationship(relative_source, action, raw, _relative(candidate, root), IncludeResolution.INACCESSIBLE, ordinal)
    resolution = IncludeResolution.STATIC_RESOLVED if exists else IncludeResolution.STATIC_MISSING
    return IncludeRelationship(relative_source, action, raw, _relative(candidate, root), resolution, ordinal)


def _walk_tasks(value, prefix=()):
    if not isinstance(value, list):
        return
    for position, task in enumerate(value):
        if not isinstance(task, Mapping):
            continue
        path = (*prefix, position)
        yield task, path
        for section_index, section in enumerate(("block", "rescue", "always")):
            yield from _walk_tasks(task.get(section), (*path, section_index)) or ()


def _extract_tasks(path: Path, root: Path, parsed: ParsedDocument):
    document = parsed.document
    if not isinstance(document, list):
        return ()
    is_playbook = any(isinstance(item, Mapping) and "hosts" in item for item in document)
    sources = []
    if is_playbook:
        for play_index, play in enumerate(document):
            if not isinstance(play, Mapping):
                continue
            for section in _TASK_SECTIONS:
                sources.append((play_index, play.get(section)))
    else:
        sources.append((0, document))
    result = []
    for play_index, task_list in sources:
        for task, task_path in _walk_tasks(task_list) or ():
            ordinal = len(result)
            action = task_action(task)
            includes = tuple(
                classify_include(path, root, key, task[key], ordinal)
                for key in _INCLUDE_ACTIONS if key in task
            )
            references = set()
            for text in _strings(task):
                references.update(_jinja_names(text))
                references.update(
                    match[1] for match in _REFERENCE_PATTERNS[1].findall(text)
                )
                references.update(
                    match[2] for match in _REFERENCE_PATTERNS[2].findall(text)
                )
            set_fact = task.get("set_fact") or task.get("ansible.builtin.set_fact")
            set_facts = tuple(sorted(
                str(key) for key in set_fact
                if key != "cacheable" and not re.search(r"{{|{%", str(key))
            )) if isinstance(set_fact, Mapping) else ()
            conditions_value = task.get("when")
            conditions = tuple(_strings(conditions_value))
            for condition in conditions:
                references.update(_condition_names(condition))
            references = tuple(sorted(references))
            tags_value = task.get("tags")
            tags = (tags_value,) if isinstance(tags_value, str) else tuple(str(item) for item in tags_value or ())
            register = task.get("register")
            result.append(TaskInfo(
                file=_relative(path, root), ordinal=ordinal, play=play_index,
                task_path=task_path, raw=MappingProxyType(dict(task)),
                name=task.get("name") if isinstance(task.get("name"), str) else None,
                action=action, jinja_references=references,
                register_definitions=(register,) if isinstance(register, str) else (),
                set_fact_definitions=set_facts, conditions=conditions, tags=tags,
                no_log=task.get("no_log"), includes=includes,
            ))
    return tuple(result)


def _root_anchor(relative: str, parsed: ParsedDocument, root: Path) -> str | None:
    parts = Path(relative).parts
    if not parts:
        return "."
    if "ansible_collections" in parts:
        index = parts.index("ansible_collections")
        if index + 2 < len(parts):
            return Path(*parts[: index + 3]).as_posix()
    for index, part in enumerate(parts[:-1]):
        if part.lower() == "ansible":
            return Path(*parts[: index + 1]).as_posix()
    project_markers = {
        "roles", "playbooks", "group_vars", "host_vars", "inventory",
        "inventories",
    }
    for index, part in enumerate(parts[:-1]):
        if part.lower() in project_markers:
            return Path(*parts[:index]).as_posix() if index else "."
    parent = Path(relative).parent
    if parent != Path(".") and any(
        (root / parent / name).is_file()
        for name in ("ansible.cfg", ".ansible-lint", "galaxy.yml")
    ):
        return parent.as_posix()
    if parsed.document_type in {"playbook", "tasks"} and len(parts) == 1:
        return "."
    return None


def _dependency_name(entry):
    if isinstance(entry, str):
        return entry
    if isinstance(entry, Mapping):
        return entry.get("name") or entry.get("role") or entry.get("src")
    return None


def _dependency_variable_prefixes(entry):
    if not isinstance(entry, Mapping):
        entry = {"name": entry} if isinstance(entry, str) else {}
    values = set()
    activation = entry.get("activation_prefix")
    if isinstance(activation, str) and activation:
        values.add(activation)
    name = entry.get("name") or entry.get("role")
    if isinstance(name, str) and name:
        normalized = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
        if normalized:
            values.add(f"{normalized}_")
    source = entry.get("src")
    if isinstance(source, str) and source:
        stem = source.rstrip("/").rsplit("/", 1)[-1]
        stem = re.sub(r"\.git$", "", stem)
        stem = re.sub(r"^ansible[-_.]role[-_.]", "", stem)
        tokens = [token for token in re.split(r"[.-]+", stem) if token]
        if "role" in tokens:
            position = len(tokens) - 1 - tokens[::-1].index("role")
            role_name = "_".join(tokens[position + 1:])
            if role_name:
                values.add(f"{role_name}_")
                namespace = next(
                    (
                        token for token in reversed(tokens[:position])
                        if token not in {"com", "org", "ansible"}
                    ),
                    None,
                )
                if namespace:
                    values.add(f"{namespace}_{role_name}_")
        elif tokens:
            values.add(f"{'_'.join(tokens)}_")
    return values


def _dependency_model(root, files, parsed_documents):
    roles = set()
    collections = set()
    local_collections = set()
    environment_dependencies = set()
    variable_prefixes = set()
    source_files = set()
    candidates = {Path(path).resolve() for path in files}
    search_roots = {Path(root).resolve()}
    for path in tuple(candidates):
        for parent in path.parents:
            if parent == Path(root).resolve() or Path(root).resolve() in parent.parents:
                search_roots.add(parent)
            if parent == Path(root).resolve():
                break
    for base in search_roots:
        for name in DEPENDENCY_MANIFEST_FILENAMES | {"galaxy.yml", "execution-environment.yml"}:
            candidate = base / name
            if candidate.is_file():
                candidates.add(candidate.resolve())
    for path in sorted(candidates):
        path = Path(path).resolve()
        relative = _relative(path, root)
        name = path.name.lower()
        parsed = (parsed_documents or {}).get(path)
        if parsed is None and path.is_file():
            parsed = inspect_document(path)
        document = parsed.document if parsed is not None else None
        if name in DEPENDENCY_MANIFEST_FILENAMES and isinstance(
            document, (Mapping, list)
        ):
            source_files.add(relative)
            role_entries = (
                document.get("roles") or ()
                if isinstance(document, Mapping)
                else document
            )
            collection_entries = (
                document.get("collections") or ()
                if isinstance(document, Mapping)
                else ()
            )
            if isinstance(document, list) and "collection" in name:
                role_entries, collection_entries = (), document
            for entry in role_entries:
                dependency = _dependency_name(entry)
                if dependency:
                    roles.add(str(dependency))
                    variable_prefixes.update(_dependency_variable_prefixes(entry))
            for entry in collection_entries:
                dependency = _dependency_name(entry)
                if dependency:
                    collections.add(str(dependency))
        if path.parent.name == "meta" and name in {"main.yml", "main.yaml"} and isinstance(document, Mapping):
            entries = document.get("dependencies") or ()
            if entries:
                source_files.add(relative)
            for entry in entries:
                dependency = _dependency_name(entry)
                if dependency:
                    roles.add(str(dependency))
                    variable_prefixes.update(_dependency_variable_prefixes(entry))
        if name == "galaxy.yml" and isinstance(document, Mapping):
            source_files.add(relative)
            namespace = document.get("namespace")
            collection_name = document.get("name")
            if namespace and collection_name:
                local_collections.add(f"{namespace}.{collection_name}")
        if name == "execution-environment.yml" and isinstance(document, Mapping):
            source_files.add(relative)
            dependencies = document.get("dependencies") or {}
            if isinstance(dependencies, Mapping):
                for kind, value in dependencies.items():
                    if isinstance(value, str):
                        environment_dependencies.add(f"{kind}:{value}")
                    elif value:
                        environment_dependencies.add(f"{kind}:inline")
    return DependencyModel(
        declared_roles=tuple(sorted(roles)),
        declared_collections=tuple(sorted(collections)),
        local_collections=tuple(sorted(local_collections)),
        execution_environment_dependencies=tuple(sorted(environment_dependencies)),
        declared_variable_prefixes=tuple(sorted(variable_prefixes)),
        source_files=tuple(sorted(source_files)),
    )


def discover_project_model(root: Path, files, parsed_documents=None) -> ProjectModel:
    relative_files = {_relative(Path(path), root) for path in files}
    types = set()
    if "galaxy.yml" in relative_files or any("/galaxy.yml" in f for f in relative_files):
        types.add("collection")
    if any("/roles/" in f"/{name}" or name.startswith("roles/") for name in relative_files):
        types.add("role")
    if any(name.endswith((".yml", ".yaml")) for name in relative_files):
        types.add("playbook_project")
    roots = set()
    for path in files:
        resolved = Path(path).resolve()
        parsed = (parsed_documents or {}).get(resolved)
        if parsed is None:
            parsed = inspect_document(resolved)
        anchor = _root_anchor(_relative(resolved, root), parsed, root)
        if anchor is not None:
            roots.add(anchor)
    if not roots:
        roots.add(".")
    boundary_names = {
        "ansible.cfg", ".ansible-lint", ".ansible-lint.yml",
        ".ansible-lint.yaml", "galaxy.yml",
    }

    def independent_boundary(relative_root):
        parts = Path(relative_root).parts
        project_root = root / relative_root
        return (
            "ansible_collections" in parts
            or (parts and parts[-1].lower() == "ansible")
            or any((project_root / name).is_file() for name in boundary_names)
        )

    collapsed_roots = set(roots)
    for candidate in sorted(roots, key=lambda value: len(Path(value).parts)):
        if candidate == "." or independent_boundary(candidate):
            continue
        candidate_path = Path(candidate)
        if any(
            parent != candidate
            and (
                parent == "."
                or Path(parent) in candidate_path.parents
            )
            for parent in roots
        ):
            collapsed_roots.discard(candidate)
    roots = collapsed_roots
    config_names = {
        "ansible_cfg": "ansible.cfg",
        "ansible_lint_config": ".ansible-lint",
    }
    config_roots = sorted(roots)
    configs_by_root = {}
    for relative_root in config_roots:
        project_root = root if relative_root == "." else root / relative_root
        discovered = {
            key: _relative(project_root / name, root)
            for key, name in config_names.items()
            if (project_root / name).is_file()
        }
        if discovered:
            configs_by_root[relative_root] = MappingProxyType(discovered)
    configs = dict(configs_by_root.get(".", {}))
    if not configs and len(configs_by_root) == 1:
        configs = dict(next(iter(configs_by_root.values())))
    requirements = tuple(sorted(
        name for name in relative_files
        if Path(name).name in DEPENDENCY_MANIFEST_FILENAMES | {
            "galaxy.yml", "execution-environment.yml",
        }
    ))
    inventory_sources = {
        str(Path(name).parent)
        for name in relative_files
        if {"inventory", "inventories", "group_vars", "host_vars"}
        & set(Path(name).parts)
    }
    # Inventory context is an explicit, auditable project input. Discover
    # conventional roots and literal ansible.cfg declarations instead of
    # letting the symbol graph search every INI file in the checkout.
    for relative_root in roots:
        project_root = root if relative_root == "." else root / relative_root
        for name in ("inventory", "inventories"):
            candidate = project_root / name
            if candidate.exists():
                inventory_sources.add(_relative(candidate, root))
        config = project_root / "ansible.cfg"
        if config.is_file():
            try:
                config_text = config.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                config_text = ""
            match = re.search(
                r"(?im)^\s*inventory\s*=\s*([^#;\n]+)", config_text
            )
            if match:
                for value in match.group(1).split(","):
                    value = value.strip()
                    if value and "{{" not in value and "{%" not in value:
                        candidate = (config.parent / value).resolve()
                        try:
                            inventory_sources.add(_relative(candidate, root))
                        except ValueError:
                            continue
    inventory = tuple(sorted(inventory_sources))
    resolved_roots = {
        relative_root: (
            root.resolve()
            if relative_root == "." else (root / relative_root).resolve()
        )
        for relative_root in roots
    }
    files_by_root = {relative_root: [] for relative_root in roots}
    for source in files:
        source = Path(source).resolve()
        owners = [
            (relative_root, project_root)
            for relative_root, project_root in resolved_roots.items()
            if source == project_root or project_root in source.parents
        ]
        if owners:
            owner, _project_root = max(
                owners, key=lambda item: len(item[1].parts)
            )
            files_by_root[owner].append(source)
    dependencies_by_root = {
        relative_root: _dependency_model(
            root, root_files, parsed_documents
        )
        for relative_root, root_files in files_by_root.items()
    }
    return ProjectModel(
        types=tuple(sorted(types)),
        ansible_roots=tuple(sorted(roots)),
        configs=MappingProxyType(configs),
        requirements=requirements,
        molecule=any("molecule" in Path(name).parts for name in relative_files),
        inventory_sources=inventory,
        configs_by_root=MappingProxyType(configs_by_root),
        dependencies=_dependency_model(root, files, parsed_documents),
        dependencies_by_root=MappingProxyType(dependencies_by_root),
    )


def build_repository_analysis_context(
    root, files, *, module_metadata: Mapping[str, Mapping[str, Any]] | None = None,
    cache_dir=None,
) -> RepositoryAnalysisContext:
    """Build the parse-once repository context from an explicit population."""
    root = Path(root).resolve()
    scan_root = root if root.is_dir() else root.parent
    selected = tuple(sorted({Path(path).resolve() for path in files}))
    cache_stats = {}
    documents = {
        path: inspect_document(path, cache_dir=cache_dir, cache_stats=cache_stats)
        for path in selected
    }
    file_contexts = {}
    tasks_by_file = {}
    relationships = []
    populations = set()
    for path, parsed in documents.items():
        role = resolve_role_context(path, scan_root)
        classification = classify_source_file(
            path, scan_root, parsed_document=parsed
        )
        population = classification.source_population
        confidence = classification.confidence
        populations.add(population)
        file_contexts[path] = FileContext(
            path=path, relative_path=_relative(path, scan_root), project_root=scan_root,
            role=role.identifier if role else None,
            role_section=role.section if role else None,
            classification=population, classification_confidence=confidence,
            source_hash=parsed.content_sha256, parse_status=parsed.parse_status,
            document_type=parsed.document_type,
        )
        tasks = _extract_tasks(path, scan_root, parsed)
        tasks_by_file[path] = tasks
        relationships.extend(edge for task in tasks for edge in task.includes)
    project_model = discover_project_model(scan_root, selected, documents)
    role_roots = {
        context.role.rsplit("/", 1)[-1]: scan_root / context.role
        for context in file_contexts.values()
        if context.role and context.role != "."
    }
    role_anchors = []
    for role_root in role_roots.values():
        selected_in_role = sorted(
            path for path in selected
            if path == role_root or role_root in path.parents
        )
        preferred = next(
            (
                role_root / "tasks" / name
                for name in ("main.yml", "main.yaml")
                if (role_root / "tasks" / name).resolve() in documents
            ),
            None,
        )
        anchor = preferred or (selected_in_role[0] if selected_in_role else None)
        if anchor is not None:
            role_anchors.append(anchor.resolve())
    variable_usage, dynamic_variable_access_files = _build_variable_usage_index(
        documents, scan_root
    )
    execution_components = _build_execution_components(
        scan_root, documents, relationships
    )
    runtime_uncertainty = _build_runtime_uncertainty_index(
        scan_root, documents, tasks_by_file, relationships, project_model
    )
    performance = MappingProxyType({
        "yaml_files_parsed": len(documents),
        "yaml_parse_operations": sum(item.parse_operations for item in documents.values()),
        "tasks_indexed": sum(len(items) for items in tasks_by_file.values()),
        "include_relationships": len(relationships),
        "variable_usage_names": len(variable_usage),
        "runtime_uncertainty_files": len(runtime_uncertainty),
        "cache_hits": cache_stats.get("cache_hits", 0),
        "cache_misses": cache_stats.get("cache_misses", 0),
        "cache_errors": cache_stats.get("cache_errors", 0),
    })
    return RepositoryAnalysisContext(
        root=scan_root,
        parsed_documents=MappingProxyType(documents),
        file_contexts=MappingProxyType(file_contexts),
        tasks_by_file=MappingProxyType(tasks_by_file),
        include_relationships=tuple(relationships),
        project_model=project_model,
        selected_population=tuple(sorted(populations)),
        performance=performance,
        variable_usage=variable_usage,
        dynamic_variable_access=bool(dynamic_variable_access_files),
        dynamic_variable_access_files=dynamic_variable_access_files,
        execution_components=execution_components,
        runtime_uncertainty=runtime_uncertainty,
        role_roots=MappingProxyType(role_roots),
        role_analysis_anchor=min(role_anchors) if role_anchors else None,
        module_metadata=_freeze_value(module_metadata or {}),
    )

"""Repository-wide Ansible variable definitions with deterministic provenance."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import re
from threading import Lock

import yaml

from .analysis_context import IncludeResolution, classify_include
from .document import AnsibleSafeLoader
from .include_vars_semantics import (
    expand_include_vars_target,
    static_include_vars_target,
)
from .role_context import (
    is_automatically_loaded_role_vars,
    resolve_role_context,
)
from .task_semantics import task_action


VARIABLE_DIRECTORIES = {"defaults", "vars", "group_vars", "host_vars", "env_vars"}
EXCLUDED_DIRECTORIES = {".git", ".ansible", ".venv", "venv", "ansibleguard-output"}
RUNTIME_DEFINITION_KINDS = frozenset({
    "register", "set-fact", "loop-var", "index-var", "included-vars",
    "included-vars-namespace", "custom-module-fact",
})
PERSISTENT_RUNTIME_DEFINITION_KINDS = frozenset({
    "register", "set-fact", "included-vars", "included-vars-namespace",
    "custom-module-fact",
})
INVENTORY_DEFINITION_KINDS = frozenset({
    "group_vars-file", "host_vars-file", "env_vars-file",
    "inventory-group-var", "inventory-host-var",
})


@dataclass(frozen=True, order=True)
class VariableDefinition:
    name: str
    kind: str
    file: str
    line: int = 1
    role: str | None = None
    play: int | None = None
    task: int | None = None
    host_scope: str = "unknown"
    precedence: int | None = None
    source: str | None = None
    scope: str = "unknown"
    task_path: tuple[int, ...] | None = None
    conditional: bool = False


@dataclass(frozen=True, order=True)
class SymbolEdge:
    kind: str
    source: str
    target: str
    play: int | None = None
    task: int | float | None = None
    conditional: bool = False
    context_must: tuple[str, ...] = ()
    context_may: tuple[str, ...] = ()
    public: bool = False
    dynamic: bool = False


@dataclass(frozen=True)
class RepositorySymbolGraph:
    root: Path
    definitions: tuple[VariableDefinition, ...]
    input_files: tuple[str, ...] = ()
    edges: tuple[SymbolEdge, ...] = ()
    play_hosts_by_file: dict = field(default_factory=dict, compare=False)
    inventory_group_ancestors: dict = field(default_factory=dict, compare=False)
    _definitions_by_file: dict = field(init=False, repr=False, compare=False)
    _definitions_by_role: dict = field(init=False, repr=False, compare=False)
    _definitions_by_name: dict = field(init=False, repr=False, compare=False)
    _definitions_by_kind: dict = field(init=False, repr=False, compare=False)
    _definitions_by_play: dict = field(init=False, repr=False, compare=False)
    _definitions_by_task: dict = field(init=False, repr=False, compare=False)
    _definitions_by_host_scope: dict = field(init=False, repr=False, compare=False)
    _global_definitions: tuple = field(init=False, repr=False, compare=False)
    _definition_order: dict = field(init=False, repr=False, compare=False)
    _role_context_by_file: dict = field(init=False, repr=False, compare=False)
    _path_identity_by_absolute: dict = field(
        init=False, repr=False, compare=False
    )
    _execution_entry_must_by_file: dict = field(
        init=False, repr=False, compare=False
    )
    _execution_entry_may_by_file: dict = field(
        init=False, repr=False, compare=False
    )
    _execution_output_must_by_file: dict = field(
        init=False, repr=False, compare=False
    )
    _execution_output_may_by_file: dict = field(
        init=False, repr=False, compare=False
    )
    _execution_edges_by_source: dict = field(
        init=False, repr=False, compare=False
    )
    _execution_edges_by_target: dict = field(
        init=False, repr=False, compare=False
    )
    _cyclic_execution_edges: frozenset = field(
        init=False, repr=False, compare=False
    )
    _task_connection_files_by_file: dict = field(
        init=False, repr=False, compare=False
    )
    _query_counter: list = field(
        default_factory=lambda: [0], repr=False, compare=False
    )
    _query_lock: Lock = field(default_factory=Lock, repr=False, compare=False)

    def __post_init__(self):
        by_file = {}
        by_role = {}
        by_name = {}
        by_kind = {}
        by_play = {}
        by_task = {}
        by_host_scope = {}
        global_definitions = []
        global_kinds = INVENTORY_DEFINITION_KINDS
        for item in self.definitions:
            by_file.setdefault(item.file, []).append(item)
            by_name.setdefault(item.name, []).append(item)
            by_kind.setdefault(item.kind, []).append(item)
            by_play.setdefault(item.play, []).append(item)
            by_task.setdefault(item.task, []).append(item)
            by_host_scope.setdefault(item.host_scope, []).append(item)
            if item.role:
                by_role.setdefault(item.role, []).append(item)
            if item.kind in global_kinds or (
                item.kind == "configured-known" and item.file == ".ansibleguard.yml"
            ):
                global_definitions.append(item)
        role_contexts = {}
        for relative in self.input_files:
            context = resolve_role_context(self.root / relative, self.root)
            role_contexts[relative] = context.identifier if context else None
        object.__setattr__(
            self, "_definitions_by_file",
            {key: tuple(value) for key, value in by_file.items()},
        )
        object.__setattr__(
            self, "_definitions_by_role",
            {key: tuple(value) for key, value in by_role.items()},
        )
        object.__setattr__(
            self, "_definitions_by_name",
            {key: tuple(value) for key, value in by_name.items()},
        )
        object.__setattr__(
            self, "_definitions_by_kind",
            {key: tuple(value) for key, value in by_kind.items()},
        )
        object.__setattr__(
            self, "_definitions_by_play",
            {key: tuple(value) for key, value in by_play.items()},
        )
        object.__setattr__(
            self, "_definitions_by_task",
            {key: tuple(value) for key, value in by_task.items()},
        )
        object.__setattr__(
            self, "_definitions_by_host_scope",
            {key: tuple(value) for key, value in by_host_scope.items()},
        )
        object.__setattr__(self, "_global_definitions", tuple(global_definitions))
        object.__setattr__(
            self, "_definition_order",
            {definition: index for index, definition in enumerate(self.definitions)},
        )
        object.__setattr__(self, "_role_context_by_file", role_contexts)
        object.__setattr__(self, "_path_identity_by_absolute", {
            (self.root / relative).resolve(): (relative, role)
            for relative, role in role_contexts.items()
        })
        execution_edges = tuple(sorted(
            edge for edge in self.edges
            if edge.kind in {
                "include_tasks", "import_tasks", "role", "include_role",
                "import_role", "role_dependency",
            }
            and edge.task is not None
            and edge.target in self.input_files
        ))
        edges_by_source = {}
        edges_by_target = {}
        for edge in execution_edges:
            edges_by_source.setdefault(edge.source, []).append(edge)
            edges_by_target.setdefault(edge.target, []).append(edge)
        object.__setattr__(
            self, "_execution_edges_by_source",
            {key: tuple(value) for key, value in edges_by_source.items()},
        )
        object.__setattr__(
            self, "_execution_edges_by_target",
            {key: tuple(value) for key, value in edges_by_target.items()},
        )

        def reaches(start, target):
            pending = [start]
            visited = set()
            while pending:
                current = pending.pop()
                if current == target:
                    return True
                if current in visited:
                    continue
                visited.add(current)
                pending.extend(
                    edge.target
                    for edge in edges_by_source.get(current, ())
                )
            return False

        cyclic_edges = frozenset(
            edge for edge in execution_edges
            if reaches(edge.target, edge.source)
        )
        object.__setattr__(self, "_cyclic_execution_edges", cyclic_edges)

        adjacency = {relative: set() for relative in self.input_files}
        for edge in execution_edges:
            if edge.kind not in {"include_tasks", "import_tasks"}:
                continue
            adjacency.setdefault(edge.source, set()).add(edge.target)
            adjacency.setdefault(edge.target, set()).add(edge.source)
        handlers_by_role = {}
        for relative, role in role_contexts.items():
            context = resolve_role_context(self.root / relative, self.root)
            if role and context is not None and context.section == "handlers":
                handlers_by_role.setdefault(role, set()).add(relative)
        connections = {}
        for relative in self.input_files:
            pending = [relative]
            connected = set()
            while pending:
                current = pending.pop()
                if current in connected:
                    continue
                connected.add(current)
                pending.extend(adjacency.get(current, ()))
            role = role_contexts.get(relative)
            if role:
                connected.update(handlers_by_role.get(role, ()))
            connections[relative] = tuple(sorted(connected))
        object.__setattr__(self, "_task_connection_files_by_file", connections)

        def local_names_for_edge(edge):
            must = set(edge.context_must)
            may = set(edge.context_may)
            for item in by_file.get(edge.source, ()):
                if (
                    edge.play is not None
                    and item.play is not None
                    and item.play != edge.play
                ):
                    continue
                if (
                    item.kind in PERSISTENT_RUNTIME_DEFINITION_KINDS
                    and item.task is not None
                    and item.task < edge.task
                ):
                    may.add(item.name)
                    if not item.conditional:
                        must.add(item.name)
                elif item.kind == "play-vars":
                    must.add(item.name)
                    may.add(item.name)
                elif (
                    item.kind in {"task-vars", "loop-var", "index-var"}
                    and item.task == edge.task
                ):
                    must.add(item.name)
                    may.add(item.name)
            return must, may

        entry_must = {relative: set() for relative in self.input_files}
        entry_may = {relative: set() for relative in self.input_files}
        output_must = {relative: set() for relative in self.input_files}
        output_may = {relative: set() for relative in self.input_files}

        def edge_context(edge):
            must = set(entry_must.get(edge.source, ()))
            may = set(entry_may.get(edge.source, ()))
            local_must, local_may = local_names_for_edge(edge)
            must.update(local_must)
            may.update(local_may)
            for prior in edges_by_source.get(edge.source, ()):
                if (
                    prior.task is None
                    or prior.task >= edge.task
                    or (
                        edge.play is not None
                        and prior.play is not None
                        and prior.play != edge.play
                    )
                ):
                    continue
                prior_must = output_must.get(prior.target, set())
                prior_may = output_may.get(prior.target, set())
                if prior.public and prior.kind in {
                    "role", "include_role", "import_role", "role_dependency",
                }:
                    target_role = role_contexts.get(prior.target)
                    public_names = {
                        item.name for item in by_role.get(target_role, ())
                        if item.kind in {"defaults-file", "role-vars-file"}
                    } if target_role else set()
                    prior_must = set(prior_must) | public_names
                    prior_may = set(prior_may) | public_names
                may.update(prior_must)
                may.update(prior_may)
                if not prior.conditional and prior not in cyclic_edges:
                    must.update(prior_must)
            may.update(must)
            if edge.dynamic or edge in cyclic_edges:
                must.clear()
            return must, may

        changed = True
        while changed:
            changed = False
            for target, incoming in edges_by_target.items():
                contexts = [edge_context(edge) for edge in incoming]
                next_must = (
                    set.intersection(*(must for must, _may in contexts))
                    if contexts else set()
                )
                next_may = set().union(*(may for _must, may in contexts))
                if next_must != entry_must.get(target, set()):
                    entry_must[target] = next_must
                    changed = True
                if next_may != entry_may.get(target, set()):
                    entry_may[target] = next_may
                    changed = True

            for relative in self.input_files:
                local_must = {
                    item.name for item in by_file.get(relative, ())
                    if item.kind in PERSISTENT_RUNTIME_DEFINITION_KINDS
                    and not item.conditional
                }
                local_may = {
                    item.name for item in by_file.get(relative, ())
                    if item.kind in PERSISTENT_RUNTIME_DEFINITION_KINDS
                }
                next_must = set(entry_must.get(relative, ())) | local_must
                next_may = set(entry_may.get(relative, ())) | local_may
                for edge in edges_by_source.get(relative, ()):
                    child_must = output_must.get(edge.target, set())
                    child_may = output_may.get(edge.target, set())
                    next_may.update(child_must)
                    next_may.update(child_may)
                    if not edge.conditional and edge not in cyclic_edges:
                        next_must.update(child_must)
                next_may.update(next_must)
                if next_must != output_must.get(relative, set()):
                    output_must[relative] = next_must
                    changed = True
                if next_may != output_may.get(relative, set()):
                    output_may[relative] = next_may
                    changed = True

        for attribute, values in (
            ("_execution_entry_must_by_file", entry_must),
            ("_execution_entry_may_by_file", entry_may),
            ("_execution_output_must_by_file", output_must),
            ("_execution_output_may_by_file", output_may),
        ):
            object.__setattr__(
                self, attribute,
                {key: frozenset(value) for key, value in values.items()},
            )

    @property
    def names(self) -> frozenset[str]:
        return frozenset(self._definitions_by_name)

    def connected_task_files(self, path) -> tuple[str, ...]:
        relative, _role = self._path_identity(path)
        return self._task_connection_files_by_file.get(relative, (relative,))

    def _path_identity(self, path):
        candidate = Path(path)
        cached = self._path_identity_by_absolute.get(candidate)
        if cached is not None:
            return cached
        relative = _relative(path, self.root)
        role = self._role_context_by_file.get(relative)
        if relative not in self._role_context_by_file:
            context = resolve_role_context(path, self.root)
            role = context.identifier if context else None
        return relative, role

    def _candidate_definitions(self, path):
        """Return only definitions that can possibly be visible at *path*."""
        with self._query_lock:
            self._query_counter[0] += 1
        relative, role = self._path_identity(path)
        candidates = {
            *self._global_definitions,
            *self._definitions_by_file.get(relative, ()),
        }
        if role:
            candidates.update(self._definitions_by_role.get(role, ()))
        # Preserve the graph's deterministic definition order without falling
        # back to an O(all repository definitions) scan for every visibility
        # query.  This is the hot path on variable-heavy repositories.
        return tuple(sorted(candidates, key=self._definition_order.__getitem__))

    @property
    def query_count(self) -> int:
        """Number of indexed visibility queries served in this process."""
        with self._query_lock:
            return self._query_counter[0]

    def _visible_definition(
        self, item, path, task_index=None, play_index=None, task_path=None,
        _identity=None,
    ):
        relative, target_role = _identity or self._path_identity(path)
        same_file = item.file == relative
        same_role = bool(target_role and item.role == target_role)
        if item.kind in INVENTORY_DEFINITION_KINDS:
            return self._inventory_definition_may_apply(item, relative, play_index)
        if item.kind == "configured-known":
            return same_file or item.file == ".ansibleguard.yml"
        if item.kind in {"defaults-file", "role-vars-file"}:
            return same_role
        if item.kind == "role-parameter":
            # Invocation parameters are carried by execution edges. Treating a
            # parameter from one caller as role-global contaminates other calls.
            return False
        if (
            item.kind in {
                "register", "set-fact", "included-vars", "included-vars-namespace",
                "custom-module-fact",
            }
            and same_role
            and task_index is None
        ):
            return True
        if not same_file:
            return False
        if play_index is not None and item.play is not None and item.play != play_index:
            return False
        if item.kind == "task-vars":
            if task_index is None:
                return False
            if item.scope == "block" and item.task_path and task_path:
                return task_path[: len(item.task_path)] == item.task_path
            return item.task == task_index
        if item.kind in {"loop-var", "index-var"}:
            return task_index is not None and item.task == task_index
        if item.kind in {
            "register", "set-fact", "included-vars", "included-vars-namespace",
            "custom-module-fact",
        }:
            return task_index is None or item.task is None or item.task < task_index
        return True

    def _inventory_definition_may_apply(self, item, relative, play_index):
        """Use literal play hosts when possible; dynamic patterns remain visible."""
        hosts = self.play_hosts_by_file.get(relative, {}).get(play_index)
        if not hosts:
            return True
        if item.kind == "inventory-group-var":
            scope_name = item.scope
            directory = "group_vars"
        elif item.kind == "inventory-host-var":
            scope_name = item.scope
            directory = "host_vars"
        else:
            directory = "host_vars" if item.kind == "host_vars-file" else "group_vars"
            parts = Path(item.file).parts
            try:
                index = parts.index(directory)
                scope_name = parts[index + 1] if len(parts) > index + 2 else Path(parts[-1]).stem
            except (ValueError, IndexError):
                return True
            scope_name = Path(scope_name).stem
        if directory == "group_vars" and scope_name == "all":
            return True
        literals = set()
        for value in hosts:
            if "{{" in value or "{%" in value:
                return True
            literals.update(part for part in re.split(r"[:,]", value) if part)
        if scope_name in literals:
            return True
        # An INI inventory can explicitly declare a child group under a parent
        # group.  Vars associated with the parent apply to plays selecting that
        # literal child group.  Only statically parsed ``:children`` edges are
        # used here; unknown/dynamic inventory remains conservative above.
        return any(
            scope_name in self.inventory_group_ancestors.get(group, ())
            for group in literals
        )

    def names_for(self, path=None) -> frozenset[str]:
        """Return statically visible repository names.

        Inventory/configured names are repository-visible. File-local names are
        visible only in their defining file, while role defaults, vars, facts,
        registers, and included vars are shared only inside the same role. Role
        parameters remain conservative because their destination role is not
        represented in the current index format.
        """
        if path is None:
            return self.names
        identity = self._path_identity(path)
        visible = {
            item.name for item in self._candidate_definitions(path)
            if self._visible_definition(item, path, _identity=identity)
        }
        must, _may = self._execution_names_at(path)
        return frozenset(visible | must)

    def _execution_names_at(self, path, task_index=None, play_index=None):
        """Return MUST/MAY names from static include execution contexts."""
        relative, _role = self._path_identity(path)
        must = set(self._execution_entry_must_by_file.get(relative, ()))
        may = set(self._execution_entry_may_by_file.get(relative, ()))
        if task_index is not None:
            for edge in self._execution_edges_by_source.get(relative, ()):
                edge_not_executed = (
                    edge.task > task_index
                    if edge.kind == "role"
                    else edge.task >= task_index
                )
                if (
                    edge.task is None
                    or edge_not_executed
                    or (
                        play_index is not None
                        and edge.play is not None
                        and edge.play != play_index
                    )
                ):
                    continue
                child_must = self._execution_output_must_by_file.get(
                    edge.target, frozenset()
                )
                child_may = self._execution_output_may_by_file.get(
                    edge.target, frozenset()
                )
                if edge.public and edge.kind in {
                    "role", "include_role", "import_role", "role_dependency",
                }:
                    target_role = self._role_context_by_file.get(edge.target)
                    public_names = {
                        item.name
                        for item in self._definitions_by_role.get(target_role, ())
                        if item.kind in {"defaults-file", "role-vars-file"}
                    }
                    child_must = set(child_must) | public_names
                    child_may = set(child_may) | public_names
                may.update(child_must)
                may.update(child_may)
                if (
                    not edge.conditional
                    and edge not in self._cyclic_execution_edges
                ):
                    must.update(child_must)
        may.update(must)
        return must, may

    def definition_visibility(
        self, name, file, task_index=None, play_index=None, task_path=None
    ) -> str:
        """Classify a name as MUST-defined, MAY-defined, or unresolved."""
        visible = self._visible_definitions_named(
            name, file, task_index, play_index, task_path
        )
        if any(not item.conditional for item in visible):
            return "must"
        must, may = self._execution_names_at(file, task_index, play_index)
        if name in must:
            return "must"
        if visible or name in may:
            return "may"
        return "none"

    def definition_uncertainty_sources(
        self, name, file, task_index=None, play_index=None, task_path=None
    ) -> frozenset[str]:
        """Explain why a definition is MAY-visible at a source location."""
        visible = self._visible_definitions_named(
            name, file, task_index, play_index, task_path
        )
        must, may = self._execution_names_at(file, task_index, play_index)
        if (
            any(not item.conditional for item in visible)
            or name in must
            or not (visible or name in may)
        ):
            return frozenset()
        sources = set()
        if any(item.conditional for item in visible):
            sources.add("conditional_runtime_definition")
        relative, _role = self._path_identity(file)
        incoming = self._execution_edges_by_target.get(relative, ())
        if incoming and not any(edge.dynamic for edge in incoming):
            sources.add("static_include_execution_context")
        if any(edge.dynamic for edge in incoming):
            sources.add("dynamic_include")
        if len(incoming) > 1:
            sources.add("multiple_include_call_sites")
        if any(
            item.name == name
            and item.conditional
            and item.task is not None
            and edge.task is not None
            and item.task < edge.task
            and (
                edge.play is None
                or item.play is None
                or item.play == edge.play
            )
            for edge in incoming
            for item in self._definitions_by_file.get(edge.source, ())
        ):
            sources.add("conditional_runtime_definition")
        if not sources:
            sources.add("runtime_definition_uncertainty")
        return frozenset(sources)

    def _visible_definitions_named(
        self, name, file, task_index=None, play_index=None, task_path=None
    ):
        """Return visible definitions for one name without a broad scan."""
        with self._query_lock:
            self._query_counter[0] += 1
        identity = self._path_identity(file)
        return tuple(
            item for item in self._definitions_by_name.get(name, ())
            if self._visible_definition(
                item, file, task_index, play_index, task_path,
                _identity=identity,
            )
        )

    def has_visible_definition(
        self, name, file, task_index=None, play_index=None, task_path=None
    ) -> bool:
        return self.definition_visibility(
            name, file, task_index, play_index, task_path
        ) == "must"

    def has_visible_static_definition(
        self, name, file, task_index=None, play_index=None, task_path=None
    ) -> bool:
        return any(
            item.kind not in RUNTIME_DEFINITION_KINDS
            for item in self._visible_definitions_named(
                name, file, task_index, play_index, task_path
            )
        )

    def visible_names_at(
        self, file, task_index=None, play_index=None, task_path=None
    ) -> frozenset[str]:
        """Return conservatively visible names at a source location.

        Runtime task definitions are included only when their recorded task
        ordinal precedes ``task_index``. Definitions without a safely modeled
        execution edge are never imported from unrelated roles.
        """
        identity = self._path_identity(file)
        visible = {
            item.name for item in self._candidate_definitions(file)
            if not item.conditional
            if self._visible_definition(
                item, file, task_index, play_index, task_path,
                _identity=identity,
            )
        }
        must, _may = self._execution_names_at(file, task_index, play_index)
        return frozenset(visible | must)

    def static_definitions_at(
        self, file, task_index=None, play_index=None, task_path=None
    ):
        identity = self._path_identity(file)
        return tuple(
            item for item in self._candidate_definitions(file)
            if item.kind not in RUNTIME_DEFINITION_KINDS
            and self._visible_definition(
                item, file, task_index, play_index, task_path,
                _identity=identity,
            )
        )

    def possible_definitions_of(self, reference, file=None, task_index=None):
        if file is None:
            return self._definitions_by_name.get(reference, ())
        return self._visible_definitions_named(reference, file, task_index)

    def definitions_visible_at(self, reference, file, task_index=None,
                               play_index=None, task_path=None):
        """Return candidate definitions using the complete source-unit identity.

        Visibility is static and conservative; callers must retain MAY and
        runtime-input uncertainty rather than infer runtime values.
        """
        return self._visible_definitions_named(
            reference, file, task_index, play_index, task_path
        )

    def host_scoped_definitions_at(self, file, task_index=None):
        return tuple(
            item for item in self.possible_definitions_of_names(file, task_index)
            if item.host_scope in {"host", "group", "all-hosts"}
        )

    def possible_definitions_of_names(self, file, task_index=None):
        names = self.visible_names_at(file, task_index)
        return tuple(
            item for name in sorted(names)
            for item in self._definitions_by_name.get(name, ())
        )

    def static_names_for(
        self, path=None, task_index=None, play_index=None, task_path=None
    ) -> frozenset[str]:
        """Return visible inputs while excluding values created by tasks.

        Registers, set facts, loop variables, and task-level include-vars are
        ordered runtime definitions. Treating them as static inputs hides real
        use-before-definition findings merely because a later task creates the
        same name.
        """
        identity = self._path_identity(path) if path is not None else None
        return frozenset(
            item.name for item in (
                self._candidate_definitions(path) if path is not None else self.definitions
            )
            if item.kind not in RUNTIME_DEFINITION_KINDS
            and self._visible_definition(
                item, path, task_index, play_index, task_path,
                _identity=identity,
            )
        )

    def metadata(self) -> dict:
        rows = [asdict(item) for item in self.definitions]
        edge_rows = [asdict(item) for item in self.edges]
        encoded = json.dumps(rows, sort_keys=True, separators=(",", ":"))
        input_encoded = json.dumps(self.input_files, separators=(",", ":"))
        return {
            "status": "completed",
            "definition_count": len(rows),
            "variable_count": len(self.names),
            "query_count": self.query_count,
            "sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
            "graph_input_count": len(self.input_files),
            "graph_input_sha256": hashlib.sha256(
                input_encoded.encode("utf-8")
            ).hexdigest(),
            "edge_count": len(edge_rows),
            "cyclic_execution_edge_count": len(self._cyclic_execution_edges),
            "edge_sha256": hashlib.sha256(
                json.dumps(edge_rows, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "kinds": {
                kind: sum(item.kind == kind for item in self.definitions)
                for kind in sorted({item.kind for item in self.definitions})
            },
            "indexes": {
                "files": len(self._definitions_by_file),
                "roles": len(self._definitions_by_role),
                "names": len(self._definitions_by_name),
                "kinds": len(self._definitions_by_kind),
                "plays": len(self._definitions_by_play),
                "tasks": len(self._definitions_by_task),
                "host_scopes": len(self._definitions_by_host_scope),
                "global_definitions": len(self._global_definitions),
            },
        }


# Backward-compatible public name while callers migrate to the graph API.
RepositorySymbolIndex = RepositorySymbolGraph


def _yaml_files(root: Path):
    if root.is_file():
        return [root] if root.suffix.lower() in {".yml", ".yaml"} else []
    return sorted(
        path
        for pattern in ("*.yml", "*.yaml")
        for path in root.rglob(pattern)
        if not any(part in EXCLUDED_DIRECTORIES for part in path.parts)
    )


def _load(path: Path, parsed_documents=None):
    if parsed_documents is not None:
        parsed = parsed_documents.get(Path(path).resolve())
        if parsed is not None:
            return parsed.document
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=AnsibleSafeLoader)
    except (OSError, yaml.YAMLError):
        return None


def _tasks(
    value, prefix=(), inherited_conditional=False,
    inherited_control_optional=False,
):
    if not isinstance(value, list):
        return
    for position, task in enumerate(value):
        if not isinstance(task, dict):
            continue
        task_path = (*prefix, position)
        task_conditional = inherited_conditional or bool(task.get("when"))
        yield task, task_path, task_conditional, inherited_control_optional
        for section_position, section in enumerate(("block", "rescue", "always")):
            yield from _tasks(
                task.get(section), (*task_path, section_position),
                task_conditional or section in {"rescue", "always"},
                inherited_control_optional or section == "rescue",
            ) or []


def _add_mapping(
    definitions, mapping, kind, file, root, *, play=None, task=None,
    scope=None, task_path=None, excluded_names=(), conditional=False,
):
    if not isinstance(mapping, dict):
        return
    relative = _relative(file, root)
    role_context = resolve_role_context(file, root)
    role = role_context.identifier if role_context else None
    host_scope = (
        "group" if kind == "group_vars-file"
        else "host" if kind == "host_vars-file"
        else "all-hosts" if kind in {"env_vars-file", "configured-known"}
        else "play" if kind == "play-vars"
        else "role" if role else "file"
    )
    precedence = {
        "defaults-file": 10,
        "group_vars-file": 20,
        "host_vars-file": 30,
        "play-vars": 50,
        "role-vars": 60,
        "task-vars": 80,
        "role-parameter": 90,
    }.get(kind)
    excluded_names = set(excluded_names)
    for name in mapping:
        if name in excluded_names:
            continue
        if isinstance(name, str):
            definitions.add(
                VariableDefinition(
                    name,
                    kind,
                    relative,
                    1,
                    role=role,
                    play=play,
                    task=task,
                    host_scope=host_scope,
                    precedence=precedence,
                    source=relative,
                    scope=scope or host_scope,
                    task_path=task_path,
                    conditional=conditional,
                )
            )


def _relative(path, root):
    try:
        return Path(path).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return Path(path).name


def _role_from_relative(value, root=None):
    if root is not None:
        context = resolve_role_context(Path(root) / value, root)
        return context.identifier if context else None
    parts = Path(value).parts
    if "roles" in parts:
        index = parts.index("roles")
        return f"roles/{parts[index + 1]}" if index + 1 < len(parts) else None
    return None


def _inventory_variable_kind(path, root):
    try:
        parts = Path(path).resolve().relative_to(Path(root).resolve()).parts
    except ValueError:
        return None
    for directory in ("group_vars", "host_vars", "env_vars"):
        if directory in parts and parts[-1].lower().endswith((".yml", ".yaml")):
            return f"{directory}-file"
    return None


def _literal_play_hosts(document):
    """Return play-indexed literal host patterns without inventory execution."""
    result = {}
    if not isinstance(document, list):
        return result
    for index, entry in enumerate(document):
        if not isinstance(entry, dict) or "hosts" not in entry:
            continue
        hosts = entry.get("hosts")
        if isinstance(hosts, str):
            result[index] = (hosts,)
        elif isinstance(hosts, list) and all(isinstance(value, str) for value in hosts):
            result[index] = tuple(hosts)
    return result


def _inventory_source_paths(root, inventory_sources=None):
    root = Path(root)
    if inventory_sources is None:
        return tuple(sorted(root.rglob("*.ini")))
    paths = set()
    for relative in inventory_sources:
        source = (root / relative).resolve()
        candidates = source.rglob("*") if source.is_dir() else (source,)
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix.lower() in {"", ".ini"}:
                paths.add(candidate)
    return tuple(sorted(paths))


def _add_ini_inventory_definitions(definitions, root, inventory_sources):
    """Index literal group and host variables from declared INI inventories."""
    for path in _inventory_source_paths(root, inventory_sources):
        if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        section = None
        section_kind = None
        for number, raw in enumerate(lines, 1):
            line = raw.strip()
            header = re.match(r"^\[([^\]\s:]+)(?::([^\]\s]+))?\]$", line)
            if header:
                section, qualifier = header.groups()
                section_kind = "vars" if qualifier == "vars" else "hosts" if qualifier is None else None
                continue
            if not line or line.startswith(("#", ";")) or section_kind is None:
                continue
            assignments = []
            if section_kind == "vars":
                match = re.match(r"^([A-Za-z_][\w]*)\s*=", line)
                if match:
                    assignments.append((match.group(1), "inventory-group-var", section))
            else:
                tokens = line.split()
                host = tokens[0] if tokens else None
                for token in tokens[1:]:
                    match = re.match(r"^([A-Za-z_][\w]*)=", token)
                    if match and host:
                        assignments.append((match.group(1), "inventory-host-var", host))
            for name, kind, scope in assignments:
                definitions.add(VariableDefinition(
                    name, kind, _relative(path, root), number,
                    host_scope="group" if kind == "inventory-group-var" else "host",
                    precedence=20 if kind == "inventory-group-var" else 30,
                    source=_relative(path, root), scope=scope,
                ))


def _static_inventory_group_ancestors(root, inventory_sources=None):
    """Read literal INI group/host relationships without execution.

    This intentionally ignores ranges, plugins, and YAML inventory.  Those
    need runtime/environment semantics and must not be
    guessed by a static visibility filter.  The returned map is transitive so
    ``[production:children] web`` and ``[web:children] api`` makes production
    visible for a play whose literal target is ``api``.
    """
    children_by_parent = {}
    for path in _inventory_source_paths(root, inventory_sources):
        if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        parent = None
        host_group = None
        for raw in lines:
            line = raw.strip()
            match = re.match(r"^\[([^\]\s:]+):children\]$", line)
            if match:
                parent = match.group(1)
                host_group = None
                children_by_parent.setdefault(parent, set())
                continue
            group_match = re.match(r"^\[([^\]\s:]+)\]$", line)
            if group_match:
                parent = None
                host_group = group_match.group(1)
                continue
            if line.startswith("[") and line.endswith("]"):
                parent = None
                host_group = None
                continue
            if parent and line and not line.startswith(("#", ";")):
                child = line.split()[0]
                if re.match(r"^[A-Za-z_][\w.-]*$", child):
                    children_by_parent[parent].add(child)
            elif host_group and line and not line.startswith(("#", ";")):
                host = line.split()[0]
                if re.match(r"^[A-Za-z_][\w.-]*$", host):
                    children_by_parent.setdefault(host_group, set()).add(host)

    return _transitive_inventory_ancestors(children_by_parent)


def _transitive_inventory_ancestors(children_by_parent):
    """Return child/host -> all statically known ancestor groups."""
    ancestors = {}
    for parent, children in children_by_parent.items():
        for child in children:
            ancestors.setdefault(child, set()).add(parent)
    changed = True
    while changed:
        changed = False
        for child, direct in tuple(ancestors.items()):
            expanded = set(direct)
            for parent in direct:
                expanded.update(ancestors.get(parent, ()))
            if not expanded.issubset(direct):
                ancestors[child].update(expanded)
                changed = True
    return {
        child: tuple(sorted(parents))
        for child, parents in sorted(ancestors.items())
    }


def _yaml_inventory_group_ancestors(documents):
    """Extract literal group and host relationships from YAML inventory maps.

    Only the standard ``all -> children/hosts`` tree is recognized.  A YAML
    document that merely happens to contain an ``all`` key is ignored unless
    that node contains inventory-shaped ``children`` or ``hosts`` mappings.
    """
    children_by_parent = {}

    def add_child(parent, child):
        if isinstance(parent, str) and isinstance(child, str):
            children_by_parent.setdefault(parent, set()).add(child)

    def visit(group, node):
        if not isinstance(group, str) or not isinstance(node, dict):
            return
        children = node.get("children")
        hosts = node.get("hosts")
        if isinstance(hosts, dict):
            for host in hosts:
                add_child(group, host)
        elif isinstance(hosts, list):
            for host in hosts:
                add_child(group, host)
        if isinstance(children, dict):
            for child, child_node in children.items():
                add_child(group, child)
                visit(child, child_node)

    for document in documents:
        if not isinstance(document, dict) or not isinstance(document.get("all"), dict):
            continue
        all_node = document["all"]
        if not any(key in all_node for key in ("children", "hosts")):
            continue
        visit("all", all_node)
    return _transitive_inventory_ancestors(children_by_parent)


def _configured_facts_for_action(module_facts, action):
    """Resolve exact and unambiguous short/FQCN custom module aliases."""
    if not action:
        return ()
    exact = module_facts.get(action)
    if exact is not None:
        return exact
    short = action.rsplit(".", 1)[-1]
    matches = [
        facts for module, facts in module_facts.items()
        if module.rsplit(".", 1)[-1] == short
    ]
    return matches[0] if len(matches) == 1 else ()


def _static_reference(value):
    if isinstance(value, str) and "{{" not in value and "{%" not in value:
        return value
    if isinstance(value, dict):
        candidate = value.get("file") or value.get("name")
        if isinstance(candidate, str) and "{{" not in candidate:
            return candidate
    return None


def _dynamic_task_include_targets(value, source, scan_root, allowed_files):
    """Resolve only the statically bounded candidates of a dynamic task include."""
    if isinstance(value, str):
        raw = value
    elif isinstance(value, dict):
        raw = value.get("file") or value.get("name")
    else:
        return ()
    if not isinstance(raw, str) or "{%" in raw or "{{" not in raw:
        return ()
    role_path = re.fullmatch(r"\s*{{\s*role_path\s*}}/(.+?)\s*", raw)
    if role_path:
        role = resolve_role_context(source, scan_root)
        if role is None:
            return ()
        base = role.root
        pattern = role_path.group(1)
    else:
        base = source.parent
        pattern = raw
    pattern = re.sub(r"{{[^{}]*}}", "*", pattern)
    if "{{" in pattern or "}}" in pattern:
        return ()
    candidate_path = Path(pattern)
    if candidate_path.is_absolute() or ".." in candidate_path.parts:
        return ()
    # A bare variable (``{{ task_file }}``) can name anything and is not a
    # bounded candidate set. Require a literal filename stem in addition to
    # an extension before connecting selected files.
    literal_stem = candidate_path.stem.replace("*", "").replace("?", "")
    if not literal_stem:
        return ()
    try:
        matches = {
            candidate.resolve()
            for candidate in base.glob(pattern)
            if candidate.is_file() and candidate.resolve() in allowed_files
        }
    except (OSError, ValueError, NotImplementedError):
        # A dynamic include's pattern is task-controlled content, not a
        # trusted glob -- pathlib (3.13+) raises NotImplementedError for
        # some patterns it considers "non-relative" even when the earlier
        # is_absolute()/".." checks above didn't already reject it.
        # Confirmed in practice on a real repository (novateams/nova.core)
        # crashing the entire scan; treat it the same as an unresolvable
        # pattern (empty result) rather than letting it propagate.
        return ()
    return tuple(sorted(matches))


def _role_task_target(role_name, scan_root, allowed_files):
    """Resolve a literal role invocation to one selected tasks/main file."""
    role_parts = str(role_name).split(".")
    local_name = re.split(r"[./]", str(role_name))[-1]
    matches = [
        path for path in allowed_files
        if path.name in {"main.yml", "main.yaml"}
        and len(path.parts) >= 3
        and path.parent.name == "tasks"
        and path.parent.parent.name == local_name
    ]
    direct = [
        scan_root / "roles" / local_name / "tasks" / name
        for name in ("main.yml", "main.yaml")
    ]
    for candidate in direct:
        if candidate.resolve() in allowed_files:
            return candidate.resolve()
    if len(role_parts) >= 3:
        namespace, collection, role = role_parts[-3:]
        fqcn_matches = [
            path for path in matches
            if (
                "ansible_collections", namespace, collection, "roles", role
            ) == tuple(path.parts[-7:-2])
        ]
        if len(fqcn_matches) == 1:
            return fqcn_matches[0]
    return matches[0] if len(matches) == 1 else None


def _private_role_vars_enabled(scan_root):
    """Read only the stable defaults/private_role_vars boolean setting."""
    candidates = [scan_root / "ansible.cfg"]
    for candidate in candidates:
        try:
            text = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        match = re.search(
            r"(?im)^\s*private_role_vars\s*=\s*(true|yes|1|false|no|0)\s*$",
            text,
        )
        if match:
            return match.group(1).lower() in {"true", "yes", "1"}
    return False


def build_repository_symbol_index(
    root, known_variables=(), files=None, known_variables_by_file=None,
    parsed_documents=None, custom_module_facts_by_file=None,
    inventory_sources=None,
):
    """Build a symbol index from an explicit, auditable file population.

    ``files`` is deliberately separate from ``root``: research profiles can
    use the repository as the path anchor while preventing unselected tests,
    fixtures, and examples from influencing findings. When omitted, the
    historical whole-target behaviour remains available to direct callers.
    """
    root = Path(root).resolve()
    scan_root = root if root.is_dir() else root.parent
    definitions = {
        VariableDefinition(
            str(name), "configured-known", ".ansibleguard.yml", 1,
            host_scope="all-hosts", precedence=100, source="configuration",
        )
        for name in known_variables
    }
    private_role_vars = _private_role_vars_enabled(scan_root)
    for configured_file, names in (known_variables_by_file or {}).items():
        relative = _relative(configured_file, scan_root)
        for name in names:
            definitions.add(
                VariableDefinition(
                    str(name), "configured-known", relative, 1,
                    host_scope="all-hosts", precedence=100,
                    source="nearest-configuration", scope="file",
                )
            )
    edges = set()
    referenced_files = {}
    play_hosts_by_file = {}
    inventory_group_ancestors = _static_inventory_group_ancestors(
        scan_root, inventory_sources
    )
    _add_ini_inventory_definitions(
        definitions, scan_root, inventory_sources
    )
    inventory_documents = []

    candidates = _yaml_files(root) if files is None else sorted(
        {
            Path(path).resolve()
            for path in files
            if Path(path).suffix.lower() in {".yml", ".yaml"}
        }
    )
    allowed_files = set(candidates)
    custom_facts_by_path = {
        Path(configured_path).resolve(): module_facts
        for configured_path, module_facts in (custom_module_facts_by_file or {}).items()
    }
    for path in candidates:
        document = _load(path, parsed_documents)
        inventory_documents.append(document)
        play_hosts_by_file[_relative(path, scan_root)] = _literal_play_hosts(document)
        inventory_kind = _inventory_variable_kind(path, scan_root)
        automatic_role_vars = is_automatically_loaded_role_vars(path, scan_root)
        if inventory_kind:
            _add_mapping(definitions, document, inventory_kind, path, scan_root)
        elif automatic_role_vars:
            _add_mapping(
                definitions, document, automatic_role_vars[0], path, scan_root,
                scope="role",
            )

        entries = document if isinstance(document, list) else [document]
        is_playbook = bool(
            isinstance(document, list)
            and any(
                isinstance(entry, dict)
                and any(key in entry for key in ("hosts", "tasks", "pre_tasks", "post_tasks"))
                for entry in document
            )
        )
        task_ordinal = 0
        configured_facts = custom_facts_by_path.get(path, {})
        processing_entries = entries if is_playbook else [{"tasks": document}]
        for play_index, entry in enumerate(processing_entries):
            if not isinstance(entry, dict):
                continue
            if is_playbook:
                _add_mapping(
                    definitions, entry.get("vars"), "play-vars", path, scan_root,
                    play=play_index, scope="play",
                )
            roles = entry.get("roles") if is_playbook else None
            pre_task_count = len(list(_tasks(entry.get("pre_tasks")) or ()))
            for role_position, role in enumerate(
                roles if isinstance(roles, list) else []
            ):
                role_mapping = role if isinstance(role, dict) else {}
                role_name = (
                    role if isinstance(role, str)
                    else role_mapping.get("role") or role_mapping.get("name")
                )
                _add_mapping(
                    definitions, role_mapping.get("vars"), "role-vars", path, scan_root,
                    play=play_index,
                )
                role_parameters = {
                    key: value
                    for key, value in role_mapping.items()
                    if key not in {"role", "name", "vars", "when", "tags", "become"}
                }
                parameter_scope = path
                if isinstance(role_name, str) and "{{" not in role_name:
                    local_name = re.split(r"[./]", role_name)[-1]
                    parameter_scope = scan_root / "roles" / local_name / "__parameters__.yml"
                    role_target = _role_task_target(
                        role_name, scan_root, allowed_files
                    )
                    if role_target is not None:
                        role_names = set(role_parameters)
                        if isinstance(role_mapping.get("vars"), dict):
                            role_names.update(str(name) for name in role_mapping["vars"])
                        role_conditional = bool(role_mapping.get("when"))
                        edges.add(SymbolEdge(
                            "role", _relative(path, scan_root),
                            _relative(role_target, scan_root), play_index,
                            task_ordinal + pre_task_count
                            - (1 / (role_position + 2)),
                            role_conditional,
                            tuple(sorted(role_names)),
                            tuple(sorted(role_names)),
                            not private_role_vars,
                        ))
                _add_mapping(
                    definitions, role_parameters, "role-parameter",
                    parameter_scope, scan_root, play=play_index,
                )
            vars_files = entry.get("vars_files") if is_playbook else None
            for reference in vars_files if isinstance(vars_files, list) else []:
                static = _static_reference(reference)
                if static:
                    target = (path.parent / static).resolve()
                    referenced_files.setdefault(target, set()).add(
                        (path, "vars-file-reference", play_index, None, None, False)
                    )
                    edges.add(SymbolEdge("vars-file", _relative(path, scan_root), _relative(target, scan_root)))
            effective_play_index = play_index if is_playbook else 0
            if is_playbook:
                task_source = [
                    task
                    for section in ("pre_tasks", "tasks", "post_tasks", "handlers")
                    for task in (
                        entry.get(section)
                        if isinstance(entry.get(section), list) else []
                    )
                ]
            else:
                task_source = (
                    entry.get("tasks")
                    if isinstance(entry.get("tasks"), list) else [entry]
                )
            for (
                task, task_path, task_conditional, task_control_optional
            ) in _tasks(task_source) or []:
                task_index = task_ordinal
                task_ordinal += 1
                action = task_action(task)
                if action and action.rsplit(".", 1)[-1] in {
                    "include_role", "import_role",
                }:
                    role_value = task.get(action)
                    if role_value is None:
                        role_value = task.get(action.rsplit(".", 1)[-1])
                    role_name = _static_reference(role_value)
                    if role_name:
                        role_target = _role_task_target(
                            role_name, scan_root, allowed_files
                        )
                        if role_target is not None:
                            edges.add(SymbolEdge(
                                action.rsplit(".", 1)[-1],
                                _relative(path, scan_root),
                                _relative(role_target, scan_root),
                                effective_play_index,
                                task_index,
                                task_conditional,
                                (),
                                (),
                                bool(
                                    isinstance(role_value, dict)
                                    and role_value.get("public") is True
                                ) or (
                                    action.rsplit(".", 1)[-1] == "import_role"
                                    and not private_role_vars
                                ),
                            ))
                for fact_name in _configured_facts_for_action(configured_facts, action):
                    definitions.add(
                        VariableDefinition(
                            fact_name, "custom-module-fact", _relative(path, scan_root), 1,
                            role=_role_from_relative(_relative(path, scan_root), scan_root),
                            play=effective_play_index, task=task_index,
                            host_scope="host", precedence=70, source="configuration",
                            scope="following-tasks", task_path=task_path,
                            conditional=task_conditional,
                        )
                    )
                _add_mapping(
                    definitions, task.get("vars"), "task-vars", path, scan_root,
                    play=effective_play_index, task=task_index,
                    scope=(
                        "block"
                        if any(isinstance(task.get(key), list) for key in ("block", "rescue", "always"))
                        else "task"
                    ),
                    task_path=task_path,
                )
                register = task.get("register")
                if isinstance(register, str):
                    definitions.add(
                        VariableDefinition(
                            register, "register", _relative(path, scan_root), 1,
                            role=_role_from_relative(_relative(path, scan_root), scan_root),
                            play=effective_play_index, task=task_index,
                            host_scope="host", precedence=70, source="task",
                            scope="following-tasks", task_path=task_path,
                            conditional=task_control_optional,
                        )
                    )
                for key in ("set_fact", "ansible.builtin.set_fact"):
                    _add_mapping(
                        definitions, task.get(key), "set-fact", path, scan_root,
                        play=effective_play_index, task=task_index,
                        scope="following-tasks", task_path=task_path,
                        excluded_names={"cacheable"},
                        conditional=task_conditional,
                    )
                loop_control = task.get("loop_control")
                if isinstance(loop_control, dict):
                    for variable_key in ("loop_var", "index_var"):
                        if isinstance(loop_control.get(variable_key), str):
                            definitions.add(
                                VariableDefinition(
                                    loop_control[variable_key],
                                    variable_key.replace("_", "-"),
                                    _relative(path, scan_root),
                                    1,
                                    role=_role_from_relative(_relative(path, scan_root), scan_root),
                                    play=effective_play_index,
                                    task=task_index,
                                    host_scope="task",
                                    precedence=80,
                                    source="loop-control",
                                    scope="task", task_path=task_path,
                                )
                            )
                custom_loop_var = (
                    loop_control.get("loop_var")
                    if isinstance(loop_control, dict) else None
                )
                if (
                    not isinstance(custom_loop_var, str)
                    and any(
                        key == "loop" or key.startswith("with_")
                        for key in task
                    )
                ):
                    definitions.add(
                        VariableDefinition(
                            "item", "loop-var", _relative(path, scan_root), 1,
                            role=_role_from_relative(
                                _relative(path, scan_root), scan_root
                            ),
                            play=effective_play_index, task=task_index,
                            host_scope="task", precedence=80,
                            source="implicit-loop", scope="task",
                            task_path=task_path,
                        )
                    )
                for key in ("include_vars", "ansible.builtin.include_vars"):
                    include_vars = task.get(key)
                    if isinstance(include_vars, dict) and isinstance(
                        include_vars.get("name"), str
                    ):
                        definitions.add(
                            VariableDefinition(
                                include_vars["name"],
                                "included-vars-namespace",
                                _relative(path, scan_root),
                                1,
                                role=_role_from_relative(_relative(path, scan_root), scan_root),
                                play=effective_play_index,
                                task=task_index,
                                host_scope="host",
                                precedence=70,
                                source="include-vars",
                                scope="following-tasks", task_path=task_path,
                                conditional=task_conditional,
                            )
                        )
                    static_include = static_include_vars_target(
                        task.get(key), path
                    )
                    if static_include:
                        target, namespace = static_include
                        targets = expand_include_vars_target(
                            target, allowed_files if files is not None else None
                        )
                        for target in targets:
                            referenced_files.setdefault(target, set()).add(
                                (
                                    path,
                                    None if namespace is not None else "included-vars",
                                    effective_play_index,
                                    task_index, task_path, task_conditional,
                                )
                            )
                            edges.add(SymbolEdge(
                                "include-vars", _relative(path, scan_root),
                                _relative(target, scan_root)
                            ))
                for key in (
                    "include_tasks", "import_tasks",
                    "ansible.builtin.include_tasks", "ansible.builtin.import_tasks",
                ):
                    relationship = classify_include(
                        path, scan_root, key, task.get(key), task_path
                    )
                    if relationship.resolution == IncludeResolution.STATIC_RESOLVED:
                        edges.add(SymbolEdge(
                            key.split(".")[-1],
                            _relative(path, scan_root),
                            relationship.resolved_target,
                            effective_play_index,
                            task_index,
                            bool(
                                task_conditional
                                or any(
                                    loop_key == "loop"
                                    or loop_key.startswith("with_")
                                    for loop_key in task
                                )
                                ),
                            ))
                    elif relationship.resolution == IncludeResolution.DYNAMIC:
                        for target in _dynamic_task_include_targets(
                            task.get(key), path, scan_root, allowed_files
                        ):
                            edges.add(SymbolEdge(
                                key.split(".")[-1],
                                _relative(path, scan_root),
                                _relative(target, scan_root),
                                effective_play_index,
                                task_index,
                                True,
                                (),
                                (),
                                False,
                                True,
                            ))

    for path, references in sorted(referenced_files.items()):
        if files is not None and path not in allowed_files:
            continue
        mapping = _load(path, parsed_documents)
        _add_mapping(
            definitions, mapping, "referenced-vars-source", path, scan_root,
            scope="source",
        )
        for referring_file, kind, play, task, task_path, conditional in references:
            # ``include_vars: {name: namespace}`` exposes only the namespace.
            # The namespace definition is added at the task above; importing
            # the mapping keys as bare variables would create false MUST
            # definitions and hide genuine missing-variable findings.
            if kind is not None:
                _add_mapping(
                    definitions,
                    mapping,
                    kind,
                    referring_file,
                    scan_root,
                    play=play,
                    task=task,
                    scope="play" if task is None else "following-tasks",
                    task_path=task_path,
                    conditional=conditional,
                )

    # Role dependencies execute before the depending role's task entrypoint.
    # Model only literal local roles and keep conditional dependencies as MAY.
    for path in candidates:
        role_context = resolve_role_context(path, scan_root)
        if (
            role_context is None or role_context.section != "meta"
            or path.name not in {"main.yml", "main.yaml"}
        ):
            continue
        document = _load(path, parsed_documents)
        dependencies = (
            document.get("dependencies", ()) if isinstance(document, dict) else ()
        )
        source_target = _role_task_target(
            role_context.identifier.rsplit("/", 1)[-1], scan_root, allowed_files
        )
        if source_target is None:
            continue
        for position, dependency in enumerate(
            dependencies if isinstance(dependencies, list) else ()
        ):
            mapping = dependency if isinstance(dependency, dict) else {}
            name = (
                dependency if isinstance(dependency, str)
                else mapping.get("role") or mapping.get("name")
            )
            if not isinstance(name, str) or "{{" in name or "{%" in name:
                continue
            target = _role_task_target(name, scan_root, allowed_files)
            if target is None:
                continue
            parameters = {
                str(key) for key in mapping
                if key not in {"role", "name", "when", "tags"}
            }
            edges.add(SymbolEdge(
                "role_dependency", _relative(source_target, scan_root),
                _relative(target, scan_root), None,
                -1 - (1 / (position + 2)), bool(mapping.get("when")),
                tuple(sorted(parameters)), tuple(sorted(parameters)), True,
            ))

    yaml_inventory_ancestors = _yaml_inventory_group_ancestors(inventory_documents)
    for child, ancestors in yaml_inventory_ancestors.items():
        inventory_group_ancestors[child] = tuple(sorted(
            set(inventory_group_ancestors.get(child, ())) | set(ancestors)
        ))

    input_files = tuple(sorted(_relative(path, scan_root) for path in candidates))
    definition_order = lambda item: (
        item.name, item.kind, item.file, item.line, item.role or "",
        -1 if item.play is None else item.play,
        -1 if item.task is None else item.task,
        item.conditional,
    )
    return RepositorySymbolGraph(
        scan_root,
        tuple(sorted(definitions, key=definition_order)),
        input_files,
        tuple(sorted(edges)),
        play_hosts_by_file,
        inventory_group_ancestors,
    )

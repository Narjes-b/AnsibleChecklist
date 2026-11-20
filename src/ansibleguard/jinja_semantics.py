"""Bounded, non-executing interpretation of pure Jinja expressions."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import re

from .compat import StrEnum


class EvaluationState(StrEnum):
    STATIC = "STATIC"
    RUNTIME_UNKNOWN = "RUNTIME_UNKNOWN"
    NOT_TEMPLATE = "NOT_TEMPLATE"


@dataclass(frozen=True)
class EvaluationResult:
    state: EvaluationState
    value: object = None
    reason: str | None = None


_PURE_TEMPLATE = re.compile(r"^\s*{{\s*(.*?)\s*}}\s*$", re.DOTALL)
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_LITERALS = {"true": True, "false": False, "none": None, "null": None}
_DEFAULT_FILTER = re.compile(r"^default\s*\((.*)\)\s*$", re.DOTALL)
_DEFINED_GUARD = re.compile(
    r"([A-Za-z_][\w]*)(?:\.[A-Za-z_][\w]*)*\s+"
    r"is\s+(?:defined|not\s+undefined)\b"
)


def conjunctive_defined_guards(condition) -> frozenset[str]:
    """Return variables proven defined whenever the condition permits execution."""
    conditions = condition if isinstance(condition, list) else [condition]
    guarded = set()
    for item in conditions:
        if not isinstance(item, str) or re.search(r"\bor\b", item):
            continue
        guarded.update(_DEFINED_GUARD.findall(item))
    return frozenset(guarded)


def _literal(expression):
    lowered = expression.strip().lower()
    if lowered in _LITERALS:
        return True, _LITERALS[lowered]
    try:
        return True, ast.literal_eval(expression)
    except (ValueError, SyntaxError):
        return False, None


def evaluate_pure_template(value, visible_values=None) -> EvaluationResult:
    """Evaluate literals and direct static variables; execute no Jinja code."""
    if not isinstance(value, str):
        return EvaluationResult(EvaluationState.STATIC, value, "literal-yaml-value")
    match = _PURE_TEMPLATE.match(value)
    if not match:
        return EvaluationResult(EvaluationState.NOT_TEMPLATE, value, "not-pure-template")
    expression = match.group(1).strip()
    literal, result = _literal(expression)
    if literal:
        return EvaluationResult(EvaluationState.STATIC, result, "jinja-literal")
    # A standard default filter cannot make an unknown runtime variable static:
    # inventory or another runtime source may supply it.  It *can* preserve a
    # value already proven static, including a safely chained default form.
    # This deliberately excludes qualified/custom filters and default's
    # optional boolean mode, whose plugin/version semantics are not modeled.
    parts = [part.strip() for part in expression.split("|")]
    if len(parts) > 1 and all(_DEFAULT_FILTER.fullmatch(part) for part in parts[1:]):
        source = parts[0]
        source_literal, source_value = _literal(source)
        if source_literal:
            return EvaluationResult(
                EvaluationState.STATIC, source_value, "literal-through-default-filter"
            )
        if _IDENTIFIER.fullmatch(source) and visible_values is not None and source in visible_values:
            resolved = visible_values[source]
            if not (isinstance(resolved, str) and _PURE_TEMPLATE.match(resolved)):
                return EvaluationResult(
                    EvaluationState.STATIC, resolved, "visible-static-variable-through-default-filter"
                )
        return EvaluationResult(
            EvaluationState.RUNTIME_UNKNOWN,
            reason="runtime-variable-with-default-filter",
        )
    if _IDENTIFIER.fullmatch(expression):
        if visible_values is not None and expression in visible_values:
            resolved = visible_values[expression]
            if isinstance(resolved, str) and _PURE_TEMPLATE.match(resolved):
                return EvaluationResult(
                    EvaluationState.RUNTIME_UNKNOWN,
                    reason="chained-template-not-executed",
                )
            return EvaluationResult(
                EvaluationState.STATIC, resolved, "visible-static-variable"
            )
        return EvaluationResult(
            EvaluationState.RUNTIME_UNKNOWN, reason="runtime-variable"
        )
    return EvaluationResult(
        EvaluationState.RUNTIME_UNKNOWN,
        reason="expression-outside-bounded-subset",
    )

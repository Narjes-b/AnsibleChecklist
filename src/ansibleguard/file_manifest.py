"""Auditable repository-level YAML classification manifests.

The research scanner must count and scan the same file population.  This
module owns both sides of that contract: it classifies every YAML candidate
and validates the manifest before returning the explicitly included files.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

from .document import inspect_document


YAML_SUFFIXES = {".yml", ".yaml"}
TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}
TEST_PARTS = {"molecule", "test", "tests"}
CI_PARTS = {".circleci", ".github", ".gitlab", "ci", "zuul.d"}
DOCUMENTATION_PARTS = {
    "doc",
    "docs",
    "documentation",
    "example",
    "examples",
    "releasenotes",
}
GENERATED_PARTS = {
    ".tox",
    ".venv",
    "build",
    "dist",
    "generated",
    "node_modules",
    "vendor",
    "venv",
}
ANSIBLE_PARTS = {
    "defaults",
    "env_vars",
    "group_vars",
    "handlers",
    "host_vars",
    "inventory",
    "meta",
    "playbooks",
    "tasks",
    "vars",
}
ANSIBLE_DATA_PARTS = {"files", "templates"}
ANSIBLE_CONFIGURATION_PREFIXES = {
    ("etc", "kayobe"),
    ("etc", "kolla"),
    ("etc", "openstack_deploy"),
}
DEPENDENCY_MANIFEST_FILENAMES = {
    "ansible-collection-requirements.yml",
    "ansible-collection-requirements.yaml",
    "ansible-role-requirements.yml",
    "ansible-role-requirements.yaml",
    "requirements-core.yml",
    "requirements-core.yaml",
    "requirements.yml",
    "requirements.yaml",
}
CI_FILENAMES = {
    ".gitlab-ci.yml",
    ".gitlab-ci.yaml",
    ".zuul.yaml",
    ".zuul.yml",
    "zuul.yaml",
    "zuul.yml",
}
MANIFEST_FIELDS = (
    "project",
    "commit_sha",
    "path",
    "file_class",
    "document_type",
    "parse_status",
    "classification_reason",
    "loc",
    "included",
    "exclusion_reason",
)
FILE_CLASSES = {
    "production_ansible",
    "test_ansible",
    "ci_yaml",
    "documentation_example",
    "generated_or_vendor",
    "other_yaml",
    "invalid_yaml",
    "vault_encrypted",
    "unclear",
}


class FileManifestError(ValueError):
    """Raised when a classification manifest is unsafe or inconsistent."""


def _physical_loc(path: Path) -> int:
    try:
        return sum(
            1
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    except OSError:
        return 0


def yaml_candidates(repository: Path) -> list[Path]:
    """Return every YAML path under a repository except Git internals."""
    repository = Path(repository)
    candidates = []
    for path in repository.rglob("*"):
        if path.suffix.lower() not in YAML_SUFFIXES or not (
            path.is_file() or path.is_symlink()
        ):
            continue
        relative = path.relative_to(repository)
        if ".git" in {part.lower() for part in relative.parts}:
            continue
        candidates.append(path)
    return sorted(candidates)


def classify_yaml_file(path: Path, repository: Path) -> dict[str, str]:
    """Classify one YAML candidate and explain the exact decision rule."""
    path = Path(path)
    repository = Path(repository)
    relative = path.relative_to(repository)
    normalized_parts = tuple(part.strip().lower() for part in relative.parts)
    parts = set(normalized_parts)
    name = relative.name.strip().lower()

    if path.is_symlink():
        parse_status = "not-inspected"
        document_type = "symlink"
        loc = 0
        try:
            target = path.resolve(strict=True)
            target.relative_to(repository.resolve())
        except (OSError, ValueError):
            file_class = "unclear"
            reason = "broken_or_external_symlink_not_followed"
        else:
            file_class = "other_yaml"
            reason = "symlink_alias_to_repository_file"
    else:
        info = inspect_document(path)
        parse_status = info.parse_status
        document_type = info.document_type
        loc = _physical_loc(path)

        top_level = normalized_parts[0]
        if parts & GENERATED_PARTS:
            file_class = "generated_or_vendor"
            reason = "generated_or_vendor_path"
        elif (
            parts & (CI_PARTS - {"ci"})
            or top_level == "ci"
            or name in CI_FILENAMES
        ):
            file_class = "ci_yaml"
            reason = "ci_or_zuul_path"
        elif parts & DOCUMENTATION_PARTS:
            file_class = "documentation_example"
            reason = "documentation_or_example_path"
        elif parts & ANSIBLE_DATA_PARTS:
            file_class = "other_yaml"
            reason = "ansible_data_or_template_path"
        elif info.parse_status in {"invalid", "read-error"}:
            file_class = "invalid_yaml"
            reason = f"parse_status_{info.parse_status}"
        elif info.document_type == "vault-encrypted":
            file_class = "vault_encrypted"
            reason = "fully_encrypted_ansible_vault"
        elif parts & TEST_PARTS:
            file_class = "test_ansible"
            reason = "ansible_test_path"
        elif name in DEPENDENCY_MANIFEST_FILENAMES:
            file_class = "other_yaml"
            reason = "ansible_dependency_manifest"
        elif (
            normalized_parts[:2] in ANSIBLE_CONFIGURATION_PREFIXES
            and info.document_type in {"empty", "vars"}
        ):
            file_class = "production_ansible"
            reason = "ansible_deployment_configuration_path"
        elif info.document_type in {"playbook", "tasks"}:
            file_class = "production_ansible"
            reason = "ansible_playbook_or_task_shape"
        elif parts & ANSIBLE_PARTS and info.document_type in {
            "empty",
            "metadata",
            "vars",
        }:
            file_class = "production_ansible"
            reason = "ansible_role_or_inventory_path"
        elif info.parse_status == "unsupported":
            file_class = "unclear"
            reason = f"unsupported_{info.document_type}"
        else:
            file_class = "other_yaml"
            reason = "no_ansible_shape_or_path_context"

    included = file_class == "production_ansible"
    return {
        "path": relative.as_posix(),
        "file_class": file_class,
        "document_type": document_type,
        "parse_status": parse_status,
        "classification_reason": reason,
        "loc": str(loc),
        "included": "true" if included else "false",
        "exclusion_reason": "" if included else reason,
    }


def classify_repository(
    repository: Path, project: str = "", commit_sha: str = ""
) -> list[dict[str, str]]:
    """Create one deterministic manifest row for every YAML candidate."""
    rows = []
    for path in yaml_candidates(repository):
        row = classify_yaml_file(path, repository)
        rows.append({"project": project, "commit_sha": commit_sha, **row})
    return rows


def write_file_manifest(rows, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def summarize_classification(rows) -> dict[str, int]:
    rows = list(rows)
    counts = Counter(row["file_class"] for row in rows)
    return {
        "yaml_files": len(rows),
        "production_ansible_files": counts["production_ansible"],
        "test_ansible_files": counts["test_ansible"],
        "other_yaml_files": len(rows)
        - counts["production_ansible"]
        - counts["test_ansible"]
        - counts["invalid_yaml"],
        "invalid_yaml_files": counts["invalid_yaml"],
        "production_ansible_loc": sum(
            int(row["loc"] or 0)
            for row in rows
            if row["file_class"] == "production_ansible"
        ),
    }


def _parse_included(value: str, row_number: int) -> bool:
    normalized = str(value or "").strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise FileManifestError(
        f"row {row_number}: included must be true or false, got {value!r}"
    )


def read_file_manifest(manifest_path: Path) -> list[dict[str, str]]:
    manifest_path = Path(manifest_path)
    try:
        with manifest_path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            missing = set(MANIFEST_FIELDS) - set(reader.fieldnames or ())
            if missing:
                raise FileManifestError(
                    "classification manifest is missing columns: "
                    + ", ".join(sorted(missing))
                )
            return list(reader)
    except OSError as exc:
        raise FileManifestError(f"cannot read classification manifest: {exc}") from exc


def included_files_from_manifest(target: Path, manifest_path: Path) -> list[Path]:
    """Validate manifest completeness and return only explicitly included files."""
    target = Path(target)
    if not target.is_dir():
        raise FileManifestError("--file-manifest requires a directory scan target")

    rows = read_file_manifest(manifest_path)
    declared: dict[str, tuple[Path, bool]] = {}
    root = target.resolve()
    for row_number, row in enumerate(rows, 2):
        raw_path = str(row.get("path") or "")
        relative = Path(raw_path)
        if not raw_path.strip() or relative.is_absolute() or ".." in relative.parts:
            raise FileManifestError(
                f"row {row_number}: path must be a safe repository-relative path"
            )
        normalized = relative.as_posix()
        if normalized in declared:
            raise FileManifestError(f"row {row_number}: duplicate path {normalized}")
        candidate = (target / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise FileManifestError(
                f"row {row_number}: path escapes the scan target: {normalized}"
            ) from exc
        included = _parse_included(row.get("included", ""), row_number)
        file_class = str(row.get("file_class") or "").strip()
        reason = str(row.get("classification_reason") or "").strip()
        exclusion = str(row.get("exclusion_reason") or "").strip()
        if file_class not in FILE_CLASSES:
            raise FileManifestError(
                f"row {row_number}: unknown file_class {file_class!r}"
            )
        if not reason:
            raise FileManifestError(
                f"row {row_number}: classification_reason is required"
            )
        if not included and not exclusion:
            raise FileManifestError(
                f"row {row_number}: excluded rows require exclusion_reason"
            )
        declared[normalized] = (candidate, included)

    discovered = {
        path.relative_to(target).as_posix(): path.resolve()
        for path in yaml_candidates(target)
    }
    missing_rows = sorted(set(discovered) - set(declared))
    stale_rows = sorted(set(declared) - set(discovered))
    if missing_rows or stale_rows:
        details = []
        if missing_rows:
            details.append("unclassified YAML: " + ", ".join(missing_rows[:5]))
        if stale_rows:
            details.append("manifest paths not found: " + ", ".join(stale_rows[:5]))
        raise FileManifestError("manifest does not match target; " + "; ".join(details))

    included_paths = []
    for normalized, (candidate, included) in declared.items():
        if not included:
            continue
        if candidate.suffix.lower() not in YAML_SUFFIXES or not candidate.is_file():
            raise FileManifestError(f"included path is not a YAML file: {normalized}")
        included_paths.append(candidate)
    return sorted(included_paths)


def file_manifest_metadata(manifest_path: Path) -> dict:
    """Return selection provenance suitable for a scan output directory."""
    manifest_path = Path(manifest_path)
    rows = read_file_manifest(manifest_path)
    classes = Counter(row["file_class"] for row in rows)
    included = sum(
        _parse_included(row.get("included", ""), index)
        for index, row in enumerate(rows, 2)
    )
    return {
        "mode": "classification-manifest",
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "candidate_rows": len(rows),
        "included_files": included,
        "file_classes": dict(sorted(classes.items())),
        "projects": sorted({row["project"] for row in rows if row["project"]}),
        "commit_shas": sorted(
            {row["commit_sha"] for row in rows if row["commit_sha"]}
        ),
    }

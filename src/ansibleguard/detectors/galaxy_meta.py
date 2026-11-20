"""Detect Ansible roles with incomplete galaxy_info in meta/main.yml (C2)."""

from __future__ import annotations

from pathlib import Path

import yaml

_REQUIRED_FIELDS = ("author", "description", "min_ansible_version")


def detect_galaxy_meta_incomplete(yaml_file_path, parsed_document=None):
    """Flag meta/main.yml files missing required galaxy_info fields.

    Only fires when the file IS meta/main.yml, so the finding location is stable.

    Returns:
        (count, details)
    """
    path = Path(yaml_file_path)
    if path.name not in ("main.yml", "main.yaml") or path.parent.name != "meta":
        return 0, []

    if parsed_document is not None:
        loaded = parsed_document.document or {}
    else:
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            return 0, []

    if not isinstance(loaded, dict):
        return 0, []

    galaxy_info = loaded.get("galaxy_info")
    if not isinstance(galaxy_info, dict):
        return 1, [
            {
                "task_name": str(path),
                "line": 1,
                "message": "meta/main.yml has no galaxy_info mapping.",
            }
        ]

    missing = [f for f in _REQUIRED_FIELDS if not galaxy_info.get(f)]
    if not missing:
        return 0, []

    return 1, [
        {
            "task_name": str(path),
            "line": 1,
            "message": (
                f"meta/main.yml is missing required galaxy_info field(s): "
                f"{', '.join(missing)}."
            ),
        }
    ]

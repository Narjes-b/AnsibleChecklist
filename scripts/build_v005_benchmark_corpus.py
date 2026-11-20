#!/usr/bin/env python3
"""Generate the deterministic multi-shape v0.0.5 benchmark corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SHAPES = (
    "small-role",
    "medium-project",
    "many-small-files",
    "heavy-variable-project",
    "pathological-large-task-file",
)


def _write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_corpus(
    output: Path,
    *,
    many_files: int = 500,
    variable_count: int = 3000,
    large_task_count: int = 4000,
    target_lines: int = 44000,
):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError(f"benchmark corpus destination is not empty: {output}")

    _write(
        output / "small-role/roles/web/defaults/main.yml",
        "web_port: 8080\nweb_enabled: true\n",
    )
    _write(
        output / "small-role/roles/web/tasks/main.yml",
        "- name: Configure web service\n"
        "  debug:\n"
        "    msg: '{{ web_port }}'\n",
    )

    for role in ("database", "web", "worker"):
        _write(
            output / f"medium-project/roles/{role}/defaults/main.yml",
            f"{role}_enabled: true\n{role}_port: 8000\n",
        )
        _write(
            output / f"medium-project/roles/{role}/tasks/main.yml",
            f"- name: Configure {role}\n"
            f"  debug: {{msg: '{{{{ {role}_port }}}}'}}\n",
        )
    _write(
        output / "medium-project/site.yml",
        "- name: Benchmark project\n"
        "  hosts: all\n"
        "  roles: [database, web, worker]\n",
    )

    for index in range(many_files):
        _write(
            output / f"many-small-files/tasks/task-{index:05d}.yml",
            f"- name: Small task {index}\n  debug: {{msg: ready-{index}}}\n",
        )

    _write(
        output / "heavy-variable-project/group_vars/all.yml",
        "".join(f"benchmark_variable_{index}: {index}\n" for index in range(variable_count)),
    )
    _write(
        output / "heavy-variable-project/tasks.yml",
        "".join(
            f"- name: Use variable {index}\n"
            f"  debug: {{msg: '{{{{ benchmark_variable_{index} }}}}'}}\n"
            for index in range(variable_count)
        ),
    )

    large_lines = []
    for index in range(large_task_count):
        large_lines.extend((
            f"- name: Pathological task {index}",
            "  ansible.builtin.set_fact:",
            f"    staged_value_{index}: '{{{{ source_value_{index} | default({index}) }}}}'",
            f"  register: benchmark_result_{index}",
            f"  when: source_value_{index} is defined",
        ))
    large_lines.extend(
        f"# deterministic padding line {index}"
        for index in range(max(0, target_lines - len(large_lines)))
    )
    _write(
        output / "pathological-large-task-file/tasks.yml",
        "\n".join(large_lines) + "\n",
    )

    manifest = {
        "schema": "ansibleguard-v005-generated-corpus-v1",
        "parameters": {
            "many_files": many_files,
            "variable_count": variable_count,
            "large_task_count": large_task_count,
            "target_lines": target_lines,
        },
        "benchmarks": [
            {"name": name, "root": name, "repeat": 1}
            for name in SHAPES
        ],
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--many-files", type=int, default=500)
    parser.add_argument("--variable-count", type=int, default=3000)
    parser.add_argument("--large-task-count", type=int, default=4000)
    parser.add_argument("--target-lines", type=int, default=44000)
    args = parser.parse_args(argv)
    manifest = build_corpus(
        args.output,
        many_files=args.many_files,
        variable_count=args.variable_count,
        large_task_count=args.large_task_count,
        target_lines=args.target_lines,
    )
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

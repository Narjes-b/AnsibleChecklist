import yaml
import pytest

from ansibleguard.document import inspect_document
from ansibleguard.detectors.large_task import calculate_metrics_task, count_tasks_in_playbook
from ansibleguard.detectors.detect_large_play import calculate_metrics_play
from ansibleguard.detectors.detect_large_playbook import calculate_metrics_playbook
from ansibleguard.detectors.unnamed_tasks import unnamed_tasks
from ansibleguard.detectors.duplicate_task_names import repeated_task_names
from ansibleguard.report.playbook_summary import _changed_task_nodes, build_playbook_summary
from ansibleguard.task_traversal import iter_leaf_tasks


ALL_SECTIONS = """- hosts: all
  pre_tasks:
    - name: prepare
      debug: {msg: pre}
  tasks:
    - name: wrapper
      block:
        - name: main
          debug: {msg: main}
        - name: nested_wrapper
          block:
            - name: nested
              debug: {msg: nested}
      rescue:
        - name: recover
          debug: {msg: rescue}
      always:
        - name: cleanup
          debug: {msg: always}
    - debug: {msg: unnamed}
  post_tasks:
    - name: close
      debug: {msg: post}
  handlers:
    - name: restart
      debug: {msg: handler}
"""


@pytest.mark.parametrize("parsed", [False, True])
def test_task_play_playbook_and_summary_share_all_sections(tmp_path, parsed):
    path = tmp_path / "site.yml"
    path.write_text(ALL_SECTIONS)
    doc = inspect_document(path) if parsed else None
    tasks, _ = calculate_metrics_task(path, parsed_document=doc)
    play = calculate_metrics_play(path, parsed_document=doc)["Plays"][0]
    book = calculate_metrics_playbook(path, parsed_document=doc)
    assert [t["task_name"] for t in tasks] == ["prepare", "main", "nested", "recover", "cleanup", "Unknown", "close", "restart"]
    assert play["num_tasks_in_play"] == len(tasks) == 8
    assert play["tasks_names"] == [t["task_name"] for t in tasks if t["task_name"] != "Unknown"]
    assert book["num_nested_tasks_playbook"] == book["num_global_tasks_playbook"] == 8
    assert count_tasks_in_playbook(yaml.safe_load(ALL_SECTIONS)) == 8
    assert unnamed_tasks(path, parsed_document=doc)[0] == 1
    assert all(t["play_id"] == 0 and t["line"] > 0 for t in tasks)
    summaries = build_playbook_summary(tmp_path, {"introduced": [], "fixed": [], "unchanged": []})
    assert summaries[0]["tasks_analyzed"] == 8


@pytest.mark.parametrize("parsed", [False, True])
def test_task_only_file_never_counts_wrappers(tmp_path, parsed):
    path = tmp_path / "tasks.yml"
    path.write_text("""- name: wrapper
  block:
    - debug: {msg: main}
  rescue:
    - debug: {msg: rescue}
  always:
    - debug: {msg: always}
- block: []
""")
    doc = inspect_document(path) if parsed else None
    tasks, raw = calculate_metrics_task(path, parsed_document=doc)
    assert len(raw) == 2  # Preserve the existing raw top-level return contract.
    assert len(tasks) == 3 and all(t["play_id"] == -1 for t in tasks)
    assert unnamed_tasks(path, parsed_document=doc)[0] == 3


@pytest.mark.parametrize("node_mode", [False, True])
def test_aliases_at_distinct_declarations_are_not_globally_deduplicated(node_mode):
    text = "- &shared {name: leaf, debug: {msg: x}}\n- *shared\n"
    value = yaml.compose(text) if node_mode else yaml.safe_load(text)
    leaves = list(iter_leaf_tasks(value))
    assert len(leaves) == 2 and leaves[0] is leaves[1]


@pytest.mark.parametrize("node_mode", [False, True])
def test_cycles_fail_instead_of_looping_or_emitting_partial_counts(node_mode):
    text = "&cycle\n- block: *cycle\n"
    value = yaml.compose(text) if node_mode else yaml.safe_load(text)
    with pytest.raises(ValueError, match="cyclic task container"):
        list(iter_leaf_tasks(value))


def test_deep_task_nesting_does_not_use_python_recursion():
    value = [{"name": "leaf", "debug": {"msg": "x"}}]
    for _ in range(5000):
        value = [{"block": value}]
    assert [t["name"] for t in iter_leaf_tasks(value)] == ["leaf"]


def test_non_mapping_entries_and_invalid_empty_branches_are_not_tasks():
    assert list(iter_leaf_tasks([None, "text", 4, {"block": []}, {"always": None}, {"rescue": "invalid"}])) == []


def test_changed_task_spans_exclude_wrappers_and_next_task_indentation():
    text = "- block:\n    - debug: {msg: first}\n    - debug: {msg: second}\n"
    node = yaml.compose(text)
    assert _changed_task_nodes(node, {1}, text.splitlines()) == 0
    assert _changed_task_nodes(node, {2}, text.splitlines()) == 1
    assert _changed_task_nodes(node, {3}, text.splitlines()) == 1
    assert _changed_task_nodes(node, {2, 3}, text.splitlines()) == 2


def test_changed_task_span_includes_a_multiline_flow_closing_line():
    text = "- {name: flow,\n   debug: {msg: x}}\n"
    assert _changed_task_nodes(yaml.compose(text), {2}, text.splitlines()) == 1


@pytest.mark.parametrize("parsed", [False, True])
@pytest.mark.parametrize("as_play", [False, True])
def test_literal_unknown_names_are_named_and_participate_in_duplicates(tmp_path, parsed, as_play):
    text = """- name: Unknown
  debug: {msg: first}
- name: Unknown
  debug: {msg: second}
- debug: {msg: no name}
- name:
  debug: {msg: null name}
- name: '   '
  debug: {msg: blank name}
- name: 42
  debug: {msg: non-string name}
"""
    if as_play:
        text = "- hosts: all\n  tasks:\n" + "\n".join("    " + line for line in text.splitlines()) + "\n"
    path = tmp_path / "tasks.yml"
    path.write_text(text)
    doc = inspect_document(path) if parsed else None
    tasks, _ = calculate_metrics_task(path, parsed_document=doc)
    assert [t["has_name"] for t in tasks] == [True, True, False, False, False, False]
    assert [t["task_name_len"] for t in tasks] == [7, 7, 0, 0, 0, 0]
    assert unnamed_tasks(path, parsed_document=doc)[0] == 4
    assert repeated_task_names(path, parsed_document=doc) == 1

import hashlib
import json

import pytest
import yaml

from scripts import ground_sample_constructs as ground
from scripts.sample_partitioned_occurrences import sha256, write_csv


SOURCE = """- hosts: all
  tasks:
    - name: Main task
      block:
        - name: Inner task
          debug:
            msg: "{{ ActualVar }}"
      rescue:
        - name: Recover
          debug: {msg: recovered}
      always:
        - name: Finish
          debug: {msg: done}
"""


def selected(raw, *, line="5", subject="task:inner task"):
    identity = hashlib.sha256((line + subject).encode()).hexdigest()
    return {"sample_id": "PROB-" + identity, "run_id": "run", "repository": "owner/repo", "commit_sha": "a" * 40,
            "file": "tasks.yml", "line": line, "rule_id": "ansibleguard/example", "occurrence_id": identity,
            "metadata_status": "metadata-joined", "retrieval_status": "source-retrieved", "label_status": "not-started",
            "source_sha256": hashlib.sha256(raw).hexdigest(), "git_blob_oid": "b" * 40,
            "canonical_item_sha256": "c" * 64, "sampling_weight": "17.5", "dataset_role": "calibration",
            "eligible_for_performance_scoring": "False", "metadata_packet_file": "PROB-" + identity + ".json"}


def metadata_packet(directory, row, subject, *, redacted=False):
    directory.mkdir(exist_ok=True)
    packet = {key: row[key] for key in ("sample_id", "run_id", "repository", "commit_sha", "occurrence_id", "canonical_item_sha256")}
    packet.update(redacted_semantic_subject=subject, semantic_subject_redacted=redacted)
    path = directory / row["metadata_packet_file"]
    path.write_text(json.dumps(packet))
    row["metadata_packet_sha256"] = sha256(path)


class Reader:
    def __init__(self, raw):
        self.raw, self.calls = raw, []

    def read(self, *key):
        self.calls.append(key)
        return self.raw, "b" * 40


def indexed(text=SOURCE, line="5"):
    raw = text.encode()
    return ground.index_source(selected(raw, line=line), raw, "b" * 40)


def test_all_branches_and_parser_boundaries_are_located_without_nearby_substitution():
    index = indexed()
    for anchor, expected in ((5, "Inner task"), (9, "Recover"), (12, "Finish")):
        units = ground.enclosing_units(index, anchor)
        task = next(node for kind, node, _ in units if kind == "task-candidate")
        assert ground.mapping(task)["name"].value == expected
        assert any(kind == "play-candidate" for kind, _, _ in units)
    before = indexed("# unrelated comment\n" + SOURCE, "1")
    assert ground.enclosing_units(before, 1) == []
    assert ground.render_units(before, [], 1)[0]["kind"] == "file-only-no-enclosing-node"


def test_task_names_and_variable_case_are_lexical_only():
    units = ground.enclosing_units(indexed(), 5)
    assert ground.lexical_subject("task:Inner task", False, units) == "exact-token-located"
    assert ground.lexical_subject("task:inner task", False, units) == "casefold-token-only"
    assert ground.lexical_subject("variable:ActualVar", False, units) == "exact-token-located"
    assert ground.lexical_subject("variable:actualvar", False, units) == "casefold-token-only"
    assert ground.lexical_subject("variable:Other", False, units) == "token-not-located"
    assert ground.lexical_subject("task:Inner task|task:unknown", False, units) == "unsupported-subject-shape"
    assert ground.lexical_subject("location", False, units) == "no-named-subject"
    assert ground.lexical_subject("variable:ActualVar", True, units) == "redacted-subject"


def test_register_and_loop_variable_literals_are_located_without_scope_certification():
    index = indexed("- debug: {msg: x}\n  register: CapturedResult\n  loop_control: {loop_var: CustomItem}\n", "1")
    units = ground.enclosing_units(index, 2)
    assert ground.lexical_subject("variable:CapturedResult", False, units) == "exact-token-located"
    assert ground.lexical_subject("variable:capturedresult", False, units) == "casefold-token-only"
    assert ground.lexical_subject("variable:CustomItem", False, units) == "exact-token-located"
    assert ground.lexical_subject("task:unknown", False, units) == "placeholder-subject"


def test_task_display_name_surrounding_whitespace_matches_canonical_display_normalization():
    index = indexed("- name: >\n    A folded name\n  debug: {msg: x}\n", "1")
    units = ground.enclosing_units(index, 1)
    assert ground.lexical_subject("task:A folded name", False, units) == "exact-token-located"


@pytest.mark.parametrize("text,reason", [
    ("- &task {debug: {msg: x}}\n- *task\n", "yaml-aliases-require-resolution"),
    ("a: [invalid\n", "yaml-parse-failed"),
    ("- block: [{debug: {msg: first}}]\n  block: [{debug: {msg: second}}]\n", "yaml-duplicate-keys-require-review"),
    ("? [complex, key]\n: value\n", "yaml-complex-keys-require-review"),
])
def test_aliases_and_invalid_yaml_fail_explicitly(text, reason):
    with pytest.raises(ground.RetrievalFailure, match=reason):
        indexed(text, "1")


@pytest.mark.parametrize("options", [{"max_events": 2}, {"max_depth": 1}])
def test_yaml_budget_is_checked_before_composition(options):
    with pytest.raises(ground.RetrievalFailure, match="yaml-structure-limit"):
        ground.compose_bounded("a:\n  b:\n    c: d\n", **options)


def test_compose_does_not_construct_or_execute_custom_tags(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("YAML construction was invoked")
    monkeypatch.setattr(yaml.SafeLoader, "construct_object", forbidden)
    index = indexed("- name: tagged\n  debug: !custom {msg: safe}\n", "1")
    assert index["parse_info"]["custom_tag_events"] == 1
    assert ground.enclosing_units(index, 1)


def test_flow_tasks_on_same_line_are_ambiguous_not_arbitrarily_selected():
    index = indexed("[{debug: {msg: a}}, {debug: {msg: b}}]\n", "1")
    with pytest.raises(ground.RetrievalFailure, match="ambiguous-enclosing-construct"):
        ground.enclosing_units(index, 1)


def test_full_source_redaction_precedes_small_unit_window():
    text = "- name: private block\n  debug:\n    password: |\n" + "      OPAQUE_PRIVATE_LITERAL\n" * 30
    index = indexed(text, "18")
    units = ground.enclosing_units(index, 18)
    rendered = ground.render_units(index, units, 18, max_lines=5, window=80)
    assert rendered and all(unit["truncated"] and unit["redaction_affects_unit"] for unit in rendered)
    assert all(len(unit["numbered_source"].splitlines()) <= 5 for unit in rendered)
    assert all(unit["display_line_start"] <= 18 <= unit["display_line_end"] for unit in rendered)
    assert "OPAQUE_PRIVATE_LITERAL" not in json.dumps(rendered)


def test_derived_ledger_preserves_all_ids_weights_and_never_certifies(tmp_path):
    raw, metadata = SOURCE.encode(), tmp_path / "metadata"
    rows = [selected(raw), selected(raw, line="9", subject="task:Recover")]
    for row, subject in zip(rows, ("task:inner task", "task:Recover")):
        metadata_packet(metadata, row, subject)
    reader = Reader(raw)
    results = ground.ground_rows(rows, reader, metadata, tmp_path / "packets")
    assert len(reader.calls) == 1
    assert [r["sample_id"] for r in results] == [r["sample_id"] for r in rows]
    assert all(r["sampling_weight"] == "17.5" and r["label_status"] == "not-started" for r in results)
    assert all(r["construct_status"] == "constructs-located" and r["task_candidate"] for r in results)
    assert [r["lexical_subject_status"] for r in results] == ["casefold-token-only", "exact-token-located"]
    assert all(not r["subject_verified"] and not r["evidence_complete"] and not r["construct_applicability_verified"] for r in results)
    for row in results:
        assert sha256(tmp_path / "packets" / row["construct_packet_file"]) == row["construct_packet_sha256"]


@pytest.mark.parametrize("failure", ["metadata", "source"])
def test_hash_failure_is_a_recorded_row_not_a_replacement_or_silent_success(tmp_path, failure):
    raw, metadata = SOURCE.encode(), tmp_path / "metadata"
    row = selected(raw)
    metadata_packet(metadata, row, "task:Inner task")
    if failure == "metadata":
        (metadata / row["metadata_packet_file"]).write_text("changed")
    else:
        row["source_sha256"] = "0" * 64
    results = ground.ground_rows([row], Reader(raw), metadata, tmp_path / "packets")
    assert len(results) == 1 and results[0]["construct_status"] == ("metadata-packet-hash-mismatch" if failure == "metadata" else "source-integrity-mismatch")
    assert results[0]["sampling_weight"] == "17.5"


def test_input_chain_rejects_reweighted_selection_even_with_new_ledger_hash(tmp_path, monkeypatch):
    draw, metadata = tmp_path / "draw", tmp_path / "metadata"
    draw.mkdir()
    metadata.mkdir()
    (draw / "selection-manifest.json").write_text("{}")
    selected_row = {"sample_id": "fixture", "sampling_weight": "17.5", "retrieval_status": "pending"}
    monkeypatch.setattr(ground, "load_draw", lambda path: ([selected_row], {}))
    write_csv(metadata / "metadata-ledger.csv", [{**selected_row, "sampling_weight": "18", "retrieval_status": "source-retrieved"}])
    (metadata / "metadata-manifest.json").write_text(json.dumps({
        "draw_manifest_sha256": sha256(draw / "selection-manifest.json"), "eligible_for_performance_scoring": False,
        "output_sha256": {"metadata-ledger.csv": sha256(metadata / "metadata-ledger.csv")}}))
    with pytest.raises(ValueError, match="changed a selection"):
        ground.load_inputs(draw, metadata)


def test_unsafe_or_duplicate_packet_ids_are_rejected_before_writes(tmp_path):
    row = selected(SOURCE.encode())
    row["sample_id"] = "../escape"
    with pytest.raises(ValueError, match="safe sample IDs"):
        ground.ground_rows([row], Reader(SOURCE.encode()), tmp_path, tmp_path / "packets")
    assert not (tmp_path / "packets").exists()

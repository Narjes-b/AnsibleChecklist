from scripts.v007_validation_source import (
    stable_object_identity,
    stable_occurrence_id,
)


def test_validation_occurrence_identity_namespaces_reused_source_ids():
    source_id = "detector-fingerprint"
    first = stable_occurrence_id(
        "org-a/repo", "a" * 40, "ansibleguard", source_id
    )
    assert first == stable_occurrence_id(
        "org-a/repo", "a" * 40, "ansibleguard", source_id
    )
    assert first != stable_occurrence_id(
        "org-b/repo", "b" * 40, "ansibleguard", source_id
    )


def test_object_identity_distinguishes_semantic_objects_and_location_anchors():
    task = stable_object_identity(
        "org/repo", "a" * 40, "tasks/main.yml", 12, "task:configure service"
    )
    assert task[0] == "task"
    assert task[2] == "semantic_subject"
    assert task == stable_object_identity(
        "org/repo", "a" * 40, "tasks/main.yml", 12, "task:configure service"
    )

    location = stable_object_identity(
        "org/repo", "a" * 40, "defaults/main.yml", 12, "location"
    )
    other_location = stable_object_identity(
        "org/repo", "a" * 40, "defaults/main.yml", 13, "location"
    )
    assert location[0] == "source_location"
    assert location[2] == "reported_path_line"
    assert location[1] != other_location[1]

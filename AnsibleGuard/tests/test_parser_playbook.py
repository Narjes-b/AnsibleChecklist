from parser_playbook import mainn


def test_mainn_pairs_each_play_with_its_own_tasks(fixtures_dir):
    """End-to-end regression test for the play_id desync bug: detect_large_task.py
    and detect_large_play.py used to disagree on what counts as a "play"
    boundary (whether a top-level task-with-a-block counts), silently pairing
    every real play with a DIFFERENT play's tasks throughout the pipeline.
    This fixture has two top-level task-with-block entries preceding the real
    plays — exactly the shape that used to desync the numbering."""
    fixture = fixtures_dir / "parser_playbook_main3.yml"
    result = mainn(str(fixture))

    plays_by_name = {
        p["play_metrics"]["Play_name"]: p
        for p in result["plays"]
        if p["play_metrics"] is not None
    }

    example_playbook_tasks = {
        t["task_name"] for t in plays_by_name["Example Playbook"]["task_metrics"]
    }
    assert example_playbook_tasks == {
        "Include some vars from a file (used)",
        "Include some vars from another file (unused)",
        "Use a variable from the first included file",
    }

    # play1 must have its real nested block tasks (task4/5/6), NOT the
    # block-wrapper names (Notconsideredtask3/4) and NOT another play's tasks
    play1_tasks = {t["task_name"] for t in plays_by_name["play1"]["task_metrics"]}
    assert play1_tasks == {"task4", "task5", "task6"}

    play2_tasks = {t["task_name"] for t in plays_by_name["play2"]["task_metrics"]}
    assert play2_tasks == {"task7"}

    # The Global group (tasks outside any play) must contain only genuinely
    # top-level tasks, never a real play's tasks
    global_group = next(p for p in result["plays"] if p["play_metrics"] is None)
    global_task_names = {t["task_name"] for t in global_group["task_metrics"]}
    assert "Notconsideredtask1" in global_task_names
    assert "task1" in global_task_names
    assert "task20" in global_task_names
    assert "task4" not in global_task_names
    assert "Include some vars from a file (used)" not in global_task_names


def test_mainn_task_only_playbook_single_global_entry(fixtures_dir):
    """A role-style tasks/main.yml file (no hosts:/tasks: anywhere) must take
    the is_task_only_playbook branch: metrics_play stays None, and 'plays'
    ends up with exactly one entry covering every task in the file."""
    fixture = fixtures_dir / "parser_playbook_task_only.yml"
    result = mainn(str(fixture))

    assert len(result["plays"]) == 1
    assert result["plays"][0]["play_metrics"] is None
    task_names = {t["task_name"] for t in result["plays"][0]["task_metrics"]}
    assert task_names == {"task1", "task2"}

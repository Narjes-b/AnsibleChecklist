import subprocess

from scripts.v007_bundle_context_v2 import FILE_DIFF_LINES, review_context, static_context, tree_context
from scripts.v007_bundle_secret_scan import scan_text


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def make_repo(tmp_path, files):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo, git(repo, "rev-parse", "HEAD")


def candidate(sha, **over):
    base = {"sample_id": "S-1", "repository": "o/r", "commit_sha": sha, "rule_id": "ansibleguard/missing-handler",
            "path": "roles/web/tasks/main.yml", "line_start": "1", "object_kind": "task", "object_id": "Restart web",
            "family_id": "structure_reuse", "semantic_subject": "", "source_context_ref": "x", "_parent_sha": ""}
    base.update(over)
    return base


def test_tree_lists_everything_below_limit_and_has_presence_checks(tmp_path):
    files = {f"roles/web/tasks/t{i}.yml": "---\n" for i in range(150)}
    files["roles/web/tasks/main.yml"] = "---\n"
    files["roles/web/README.md"] = "x\n"
    repo, sha = make_repo(tmp_path, files)
    text = tree_context(repo, sha, "roles/web/tasks/main.yml")
    assert "listing truncated" not in text and "roles/web/tasks/t149.yml" in text
    assert "- README at the scope root: yes" in text and "- molecule/ directory: no" in text


def test_large_tree_reports_directory_counts(tmp_path):
    files = {f"roles/web/files/f{i}.txt": "x\n" for i in range(450)}
    files["roles/web/tasks/main.yml"] = "---\n"
    repo, sha = make_repo(tmp_path, files)
    text = tree_context(repo, sha, "roles/web/tasks/main.yml")
    assert "Per-directory path counts" in text and "roles/web/files: 450" in text


def test_static_bundle_names_construct_and_includes_handlers(tmp_path):
    repo, sha = make_repo(tmp_path, {"roles/web/tasks/main.yml": "- name: a\n  notify: restart web\n",
                                     "roles/web/handlers/main.yml": "- name: restart web\n  debug: {msg: hi}\n",
                                     "roles/web/handlers/extra.yml": "- name: extra\n  debug: {msg: x}\n"})
    text, inline = static_context(candidate(sha, semantic_subject="task: Restart web"), "Structure", "codebooks-v2/FAMILY_STRUCTURE_V2.md", repo)
    assert "Flagged construct: task `Restart web`" in text and "9" not in text.split("Flagged construct")[1].split("\n")[0]
    assert "roles/web/handlers/extra.yml" in text and "restart web" in text


def test_location_only_findings_name_the_enclosing_task_or_say_file_level(tmp_path):
    repo, sha = make_repo(tmp_path, {"roles/web/tasks/main.yml": "---\n- name: First\n  debug: {msg: a}\n- name: Second one\n  ansible.builtin.shell: ls\n"})
    located, _ = static_context(candidate(sha, object_kind="source_location", object_id="x:5", line_start="5"), "S", "c", repo)
    assert "anchor line 5 lies in the task at line 4, name `Second one`" in located
    filelevel, _ = static_context(candidate(sha, object_kind="source_location", object_id="x:1", line_start="1"), "S", "c", repo)
    assert "file-level finding" in filelevel


def test_review_bundle_has_non_yaml_diffs_and_no_identities(tmp_path):
    repo, parent = make_repo(tmp_path, {"a.yml": "x: 1\n"})
    (repo / "CHANGELOG.md").write_text("- change by dev@corp.io\n", encoding="utf-8")
    (repo / "big.txt").write_text("\n".join(f"line {i}" for i in range(FILE_DIFF_LINES + 50)), encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Add changelog")
    sha = git(repo, "rev-parse", "HEAD")
    text, _ = review_context(candidate(sha, rule_id="ansibleguard/missing-release-note", _parent_sha=parent,
                                       family_id="review_history"), "Review", "c", repo)
    assert "### `CHANGELOG.md`" in text and "### `big.txt`" in text
    assert "further diff lines for this file not shown" in text
    assert scan_text(text) == []


def test_bundle_validator_accepts_generated_and_flags_defects(tmp_path):
    from scripts.v007_bundle_validate_v2 import check_bundle
    repo, sha = make_repo(tmp_path, {"roles/web/tasks/main.yml": "---\n- name: a\n  debug: {msg: x}\n"})
    text, _ = static_context(candidate(sha, object_kind="task", object_id="a", line_start="2"), "S", "c", repo)
    assert check_bundle(text) == []
    assert "no 'Flagged construct' line" in check_bundle(text.replace("- Flagged construct", "- Other"))
    assert any("scan" in p for p in check_bundle(text + "\ncontact: dev@corp.io\n"))
    assert check_bundle("nothing here") == ["neither a source excerpt nor a commit message"]


def test_bundle_validator_checks_review_diff_sections(tmp_path):
    from scripts.v007_bundle_validate_v2 import check_bundle
    repo, parent = make_repo(tmp_path, {"a.yml": "x: 1\n"})
    (repo / "b.txt").write_text("hello\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Add b")
    sha = git(repo, "rev-parse", "HEAD")
    text, _ = review_context(candidate(sha, rule_id="ansibleguard/missing-test-update", _parent_sha=parent), "R", "c", repo)
    assert check_bundle(text) == []
    assert any("diff sections" in p for p in check_bundle(text.replace("### `b.txt`", "### b")))


def test_hashed_object_id_is_never_shown(tmp_path):
    repo, sha = make_repo(tmp_path, {"roles/web/tasks/main.yml": "---\n- name: a\n  debug: {msg: x}\n"})
    text, _ = static_context(candidate(sha, object_id="deadbeef" * 8, line_start="3"), "S", "c", repo)
    assert "deadbeef" not in text and "lies in the task at line 2, name `a`" in text


def test_computed_facts_for_blocks_and_leaf_counts():
    from scripts.v007_bundle_context_v2 import computed_facts
    text = """---
- hosts: all
  tasks:
    - block:
        - name: only
          debug: {msg: a}
    - block:
        - debug: {msg: b}
      when: x
"""
    facts = computed_facts("ansibleguard/unnecessary-abstraction", text)
    assert "blocks in file: 2; blocks containing exactly one task: 2" in facts
    assert "block at line 4: block-level keys none; justifying keys none" in facts
    assert "block at line 7: block-level keys ['when']; justifying keys ['when']" in facts
    many = "---\n" + "\n".join(f"- name: t{i}\n  debug: {{msg: {i}}}" for i in range(11)) + "\n"
    assert "leaf tasks (not counting block containers): 11" in computed_facts("ansibleguard/missing-abstraction", many)
    assert "present: no" in computed_facts("ansibleguard/missing-abstraction", many)
    assert computed_facts("ansibleguard/missing-tags", many) == ""


def test_enclosing_construct_names_play_and_mapping_key():
    from scripts.v007_bundle_context_v2 import enclosing_construct
    play = "- name: Web\n  hosts: all\n  become: true\n  tasks:\n    - debug: {msg: x}\n".splitlines()
    assert enclosing_construct(play, 3) == "the play at line 1, name `Web`"
    mapping = "app_port: 80\napp_users:\n  - bob\n".splitlines()
    assert enclosing_construct(mapping, 3).startswith("the top-level key `app_users`") or "the top-level key" in enclosing_construct(mapping, 2)


def test_placeholder_subject_is_not_printed(tmp_path):
    repo, sha = make_repo(tmp_path, {"roles/web/tasks/main.yml": "---\n- name: a\n  debug: {msg: x}\n"})
    text, _ = static_context(candidate(sha, semantic_subject="location: roles/web/tasks/main.yml", line_start="3"), "S", "c", repo)
    assert "Asserted subject" not in text


def test_redaction_runs_are_collapsed():
    from scripts.v007_bundle_context_v2 import collapse_redaction_runs
    lines = ["  10 | key: a"] + [f"  {n} | [REDACTED PRIVATE KEY CONTENT]" for n in range(11, 91)] + ["  91 | next: b"]
    out = collapse_redaction_runs("\n".join(lines))
    assert out.count("REDACTED PRIVATE KEY CONTENT") == 1 and "79 further identical redacted lines" in out and "91 | next: b" in out


def test_reference_search_lists_definitions_first(tmp_path):
    from scripts.v007_bundle_context_v2 import reference_context
    files = {"a.yml": "- debug: {msg: '{{ net }}'}\n" * 3, "defs.yml": "net: 10.0.0.0\n"}
    repo, sha = make_repo(tmp_path, files)
    out = reference_context(repo, sha, "variable: net")
    assert out.index("Likely definitions") < out.index("Other references") and "defs.yml:1:net: 10.0.0.0" in out.split("Other references")[0]


def test_redaction_v2_keeps_non_secrets_visible_and_hides_secrets():
    from scripts.v007_bundle_context_v2 import redact_sensitive_text_v2 as r
    text = "\n".join([
        "sudo_requires_password: false", "password_min_length: 12", "db_password: hunter2hunter2", "api_token: {{ vault_token }}",
        "admin_password:", "  length: 20", "  secret_key: abcdef123456", "ssh_key_pass: |", "  line one", "  line two", "after: 1",
    ])
    out = r(text)
    assert "sudo_requires_password: false" in out and "password_min_length: 12" in out
    assert "hunter2" not in out and "abcdef123456" not in out and "line one" not in out
    assert "api_token: {{ vault_token }}" in out and "  length: 20" in out and "after: 1" in out
    assert "[REDACTED_LITERAL]" in out and "[REDACTED VALUE BLOCK]" in out


def test_play_anchor_is_called_a_play_even_when_the_subject_says_task(tmp_path):
    repo, sha = make_repo(tmp_path, {"site.yml": "---\n- name: Web\n  hosts: all\n  become: true\n  tasks:\n    - debug: {msg: x}\n"})
    text, _ = static_context(candidate(sha, path="site.yml", rule_id="ansibleguard/become-scope-too-broad",
                                       semantic_subject="task: Web", line_start="2", family_id="security"), "S", "c", repo)
    assert "Flagged construct: the play at line 2, name `Web`" in text and "source shows a play" in text


def test_static_bundle_redacts_secrets_but_keeps_booleans(tmp_path):
    body = "---\n- name: x\n  vars:\n    db_password: hunter2hunter2\n    sudo_requires_password: false\n    contact: ops.person@corp.io\n"
    repo, sha = make_repo(tmp_path, {"roles/web/tasks/main.yml": body})
    text, inline = static_context(candidate(sha, line_start="4"), "S", "c", repo)
    for out in (text, inline):
        assert "hunter2" not in out and "ops.person@corp.io" not in out
        assert "sudo_requires_password: false" in out


def test_redaction_v2_screens_nested_values_under_empty_secret_keys():
    from scripts.v007_bundle_context_v2 import redact_sensitive_text_v2 as r
    text = "\n".join([
        "app_secrets:", "  n8n_encryption_key: Zq8Tpx0LmN4vB7", "  token_ro: [vault_token_ro, vault_token_rw]", "  length: 20",
        "  name: \"{{ app_name }}\"", "  users:", "    - alice-the-admin", "    - vault_user_ref", "next_key: visible",
    ])
    out = r(text)
    assert "Zq8Tpx0LmN4vB7" not in out and "alice-the-admin" not in out
    assert "token_ro: [vault_token_ro, vault_token_rw]" in out and "length: 20" in out and "{{ app_name }}" in out
    assert "vault_user_ref" in out and "next_key: visible" in out and "app_secrets:" in out


def test_redaction_v2_sees_real_indentation_behind_the_gutter():
    from scripts.v007_bundle_context_v2 import redact_sensitive_text_v2 as r
    lines = ["app_secrets:", "  n8n_encryption_key: Zq8Tpx0LmN4vB7", "  other: Plain Words Here", "after: 1"]
    out = r("\n".join(f"{n:5d} | {line}" for n, line in enumerate(lines, 1)))
    assert "Zq8Tpx0LmN4vB7" not in out and "Plain Words Here" not in out
    assert "    4 | after: 1" in out and "    1 | app_secrets:" in out
    assert len(out.split("\n")) == 4

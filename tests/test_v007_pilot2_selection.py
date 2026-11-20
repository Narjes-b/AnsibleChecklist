from scripts.v007_pilot2_selection import exclusion_reason, select_pilot2


def row(i, repo="o/r", rule="ansibleguard/missing-tags", path="tasks/main.yml", family="style_policy", **extra):
    base = {"occurrence_id": f"occ{i}", "selection_rank_sha256": f"{i:04d}", "family_id": family, "rule_id": rule,
            "repository": repo, "path": path}
    base.update(extra)
    return base


def test_exclusions():
    assert exclusion_reason(row(1), {"occ1"}) == "pilot-1 item"
    assert exclusion_reason(row(2, path="roles/konstruktoid.hardening/tasks/a.yml"), set()) == "vendored third-party content"
    assert exclusion_reason(row(3, path="vendor/x/tasks/a.yml"), set()) == "vendored third-party content"
    assert exclusion_reason(row(4, author="dependabot[bot] <x@y>"), set()) == "bot-authored commit"
    assert exclusion_reason(row(5, object_kind="git_commit", is_merge="true"), set()) == "merge commit"
    assert exclusion_reason(row(6), set()) is None


def test_siblings_pilot1_and_repo_cap_are_enforced():
    rows = [row(i, repo="a/b", path=f"roles/r{i}/tasks/main.yml") for i in range(1, 6)]
    rows += [row(10, repo="a/b", path="roles/r1/tasks/other.yml")]  # sibling of occ1's directory
    rows += [row(11, repo="c/d", path="tasks/main.yml"), row(12, repo="e/f", path="tasks/main.yml")]
    selected, excluded = select_pilot2(rows, {"occ11"}, {"ansibleguard/missing-tags": 100}, per_family=8)
    ids = {r["occurrence_id"] for r in selected["style_policy"]}
    assert "occ11" not in ids and "occ10" not in ids
    assert sum(r["repository"] == "a/b" for r in selected["style_policy"]) == 2
    assert excluded["pilot-1 item"] == 1 and excluded["sibling of an earlier candidate"] == 1 and excluded["repository cap"] >= 1


def test_rare_rules_get_reserved_slots():
    rows = [row(i, repo=f"r{i}/x", path=f"d{i}/main.yml") for i in range(1, 9)]
    rows += [row(20 + k, repo=f"z{k}/z", rule=f"ansibleguard/rare-{k}", path="a/main.yml") for k in range(5)]
    population = {"ansibleguard/missing-tags": 100, **{f"ansibleguard/rare-{k}": 2 for k in range(5)}}
    selected, _ = select_pilot2(rows, set(), population, per_family=6)
    chosen = selected["style_policy"]
    assert len(chosen) == 6
    assert sum(r["rule_id"].startswith("ansibleguard/rare-") for r in chosen) == 3  # RARE_SLOTS


def test_merge_subjects_and_non_ansible_yaml_are_excluded():
    from scripts.v007_pilot2_selection import is_non_ansible_yaml
    assert exclusion_reason(row(1, object_kind="git_commit", subject="Merge pull request #5 from a/b"), set()) == "merge commit"
    assert exclusion_reason(row(2, object_kind="git_commit", subject="Merge branch 'main' into feature"), set()) == "merge commit"
    assert exclusion_reason(row(3, object_kind="git_commit", subject="Merger of the two plans"), set()) is None
    assert exclusion_reason(row(4, non_ansible_yaml="true"), set()) == "non-Ansible YAML"
    assert is_non_ansible_yaml("patches/x.yaml", "- op: replace\n  path: /spec/a\n  value: 1\n")
    assert is_non_ansible_yaml("k8s/deploy.yaml", "apiVersion: v1\nkind: Pod\n")
    assert is_non_ansible_yaml("kustomization.yaml", "resources: []\n")
    assert not is_non_ansible_yaml("tasks/main.yml", "- name: a\n  debug: {msg: x}\n")

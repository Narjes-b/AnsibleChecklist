"""Tests for module-domain entropy cohesion detectors.

All tests are deterministic — no spaCy, no NLP, no FakeDoc mocking.
The entropy maths is exact; floating-point comparisons use pytest.approx.
"""

import math
import pytest

from ansibleguard.detectors.module_domain import (
    cohesion_evidence,
    domain_entropy,
    _module_domain,
    _strip_fqcn,
    _task_module,
)


# ---------------------------------------------------------------------------
# module_domain helpers
# ---------------------------------------------------------------------------

def test_strip_fqcn_removes_namespace_and_collection():
    assert _strip_fqcn("ansible.builtin.apt") == "apt"
    assert _strip_fqcn("community.general.timezone") == "timezone"
    assert _strip_fqcn("amazon.aws.ec2_instance") == "ec2_instance"


def test_strip_fqcn_leaves_bare_module_name_unchanged():
    assert _strip_fqcn("apt") == "apt"
    assert _strip_fqcn("service") == "service"


def test_module_domain_known_modules():
    assert _module_domain("apt") == "package"
    assert _module_domain("yum") == "package"
    assert _module_domain("service") == "service"
    assert _module_domain("systemd") == "service"
    assert _module_domain("file") == "file"
    assert _module_domain("copy") == "file"
    assert _module_domain("user") == "user"
    assert _module_domain("command") == "command"
    assert _module_domain("shell") == "command"
    assert _module_domain("git") == "source_control"
    assert _module_domain("debug") == "control"
    assert _module_domain("set_fact") == "control"


def test_module_domain_fqcn_maps_correctly():
    assert _module_domain("ansible.builtin.apt") == "package"
    assert _module_domain("ansible.builtin.copy") == "file"
    assert _module_domain("community.general.timezone") == "system_config"
    assert _module_domain("community.general.alternatives") == "system_config"
    assert _module_domain("ansible.posix.synchronize") == "file"


def test_module_domain_unknown_module_returns_other():
    assert _module_domain("custom_internal_module") == "other"
    assert _module_domain("my_org.stuff.mystery") == "other"


def test_task_module_extracts_module_key():
    task = {"name": "Install nginx", "apt": {"name": "nginx"}}
    assert _task_module(task) == "apt"


def test_task_module_returns_none_for_block_task():
    task = {"name": "Some block", "block": [], "rescue": [], "always": []}
    assert _task_module(task) is None


def test_task_module_works_without_name_key():
    task = {"shell": "echo hello"}
    assert _task_module(task) == "shell"


# ---------------------------------------------------------------------------
# domain_entropy
# ---------------------------------------------------------------------------

def test_empty_module_list_returns_full_cohesion():
    similarity, counts = domain_entropy([])
    assert similarity == 1.0
    assert counts == {}


def test_single_module_returns_full_cohesion():
    similarity, counts = domain_entropy(["apt"])
    assert similarity == 1.0
    assert counts == {"package": 1}


def test_all_same_domain_returns_full_cohesion():
    modules = ["apt", "yum", "dnf"]  # all → "package"
    similarity, counts = domain_entropy(modules)
    assert similarity == 1.0
    assert counts == {"package": 3}


def test_two_equal_domains_returns_zero_similarity():
    # 1 task package, 1 task service → H = log2(2) = 1 → normalised=1 → similarity=0
    modules = ["apt", "service"]
    similarity, _ = domain_entropy(modules)
    assert similarity == pytest.approx(0.0, abs=1e-9)


def test_three_equal_domains_returns_zero_similarity():
    modules = ["apt", "service", "git"]
    similarity, _ = domain_entropy(modules)
    assert similarity == pytest.approx(0.0, abs=1e-9)


def test_skewed_two_domain_similarity_is_between_zero_and_one():
    # 3 package tasks, 1 service task → not maximally diverse → 0 < similarity < 1
    modules = ["apt", "apt", "apt", "service"]
    similarity, _ = domain_entropy(modules)
    assert 0.0 < similarity < 1.0


def test_control_modules_do_not_affect_entropy():
    # debug and set_fact are control-flow scaffolding — excluded from entropy.
    # A package-only playbook with added debug/set_fact tasks must still score 1.0.
    modules = ["apt", "apt", "debug", "set_fact", "include_tasks"]
    similarity, counts = domain_entropy(modules)
    assert similarity == pytest.approx(1.0)
    assert "control" not in counts, "control domain must not appear in returned counts"


def test_control_does_not_split_two_domain_score():
    # Without control exclusion, ["apt", "service", "set_fact"] would have
    # N=3 domains, producing a different (higher) similarity than ["apt", "service"].
    # With exclusion both must give the same score (two equal domains → 0.0).
    without_control = domain_entropy(["apt", "service"])[0]
    with_control = domain_entropy(["apt", "service", "set_fact", "debug"])[0]
    assert without_control == pytest.approx(with_control, rel=1e-9)


def test_all_control_modules_returns_full_cohesion():
    # A playbook of only set_fact/debug/include_tasks has no functional domain
    # to measure — treat as trivially cohesive (1.0), not incohesive.
    modules = ["debug", "set_fact", "assert", "include_tasks"]
    similarity, counts = domain_entropy(modules)
    assert similarity == pytest.approx(1.0)
    assert counts == {}


def test_skewed_two_domain_exact_value():
    # p(package)=0.75, p(service)=0.25
    # H = -(0.75*log2(0.75) + 0.25*log2(0.25))
    # H_max = log2(2) = 1
    p1, p2 = 0.75, 0.25
    expected_h = -(p1 * math.log2(p1) + p2 * math.log2(p2))
    expected_similarity = 1.0 - expected_h / math.log2(2)
    modules = ["apt", "apt", "apt", "service"]
    similarity, _ = domain_entropy(modules)
    assert similarity == pytest.approx(expected_similarity, rel=1e-9)


def test_normal_service_lifecycle_is_not_incohesive():
    modules = [
        "apt", "apt", "template", "copy", "user", "systemd",
        "service", "sysctl", "command", "get_url",
    ]
    evidence = cohesion_evidence(modules)
    assert evidence["is_incohesive"] is False
    assert evidence["lifecycle_only"] is True


def test_small_diverse_play_is_not_enough_evidence():
    evidence = cohesion_evidence(
        ["ec2_instance", "docker_container", "mysql_user", "slack"]
    )
    assert evidence["functional_tasks"] == 4
    assert evidence["is_incohesive"] is False


def test_balanced_large_specialised_mix_is_a_candidate():
    evidence = cohesion_evidence(
        [
            "ec2_instance", "s3_bucket",
            "docker_container", "docker_image",
            "mysql_user", "postgresql_db",
            "slack", "mail",
        ]
    )
    assert evidence["functional_tasks"] == 8
    assert evidence["specialised_domains"] == [
        "cloud_infra", "container", "database", "notification"
    ]
    assert evidence["dominant_share"] == pytest.approx(0.25)
    assert evidence["is_incohesive"] is True


# ---------------------------------------------------------------------------
# sem_cohesion.calculate_similarity  (playbook-level, returns float | None)
# ---------------------------------------------------------------------------

def test_playbook_all_package_tasks_is_fully_cohesive(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    p = tmp_path / "pkgs.yml"
    p.write_text(
        "- name: Install packages\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: Install nginx\n"
        "      apt:\n"
        "        name: nginx\n"
        "    - name: Install curl\n"
        "      yum:\n"
        "        name: curl\n",
        encoding="utf-8",
    )
    result = calculate_similarity(str(p))
    assert result is not None
    assert result == pytest.approx(1.0)


def test_playbook_normal_two_domain_lifecycle_does_not_cross_finding_gate(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    p = tmp_path / "mixed.yml"
    p.write_text(
        "- name: Mixed play\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: Install\n"
        "      apt:\n"
        "        name: nginx\n"
        "    - name: Enable service\n"
        "      service:\n"
        "        name: nginx\n"
        "        state: started\n",
        encoding="utf-8",
    )
    result = calculate_similarity(str(p))
    assert result is not None
    assert result == pytest.approx(0.5)


def test_playbook_no_tasks_returns_none(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    p = tmp_path / "empty.yml"
    p.write_text(
        "- name: Empty play\n"
        "  hosts: all\n",
        encoding="utf-8",
    )
    result = calculate_similarity(str(p))
    assert result is None


def test_playbook_not_valid_yaml_returns_none(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    p = tmp_path / "broken.yml"
    p.write_text("{ not: valid: yaml: [\n", encoding="utf-8")
    result = calculate_similarity(str(p))
    assert result is None


def test_playbook_empty_file_returns_none(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    p = tmp_path / "null.yml"
    p.write_text("", encoding="utf-8")
    result = calculate_similarity(str(p))
    assert result is None


def test_playbook_fqcn_tasks_recognised_by_domain(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    p = tmp_path / "fqcn.yml"
    p.write_text(
        "- name: FQCN play\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: Install\n"
        "      ansible.builtin.apt:\n"
        "        name: nginx\n"
        "    - name: Install also\n"
        "      ansible.builtin.yum:\n"
        "        name: curl\n",
        encoding="utf-8",
    )
    result = calculate_similarity(str(p))
    # Both map to "package" → single domain → fully cohesive
    assert result == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# incohesive_plays.calculate_similarity  (play-level, returns int count)
# ---------------------------------------------------------------------------

def test_play_all_same_domain_not_counted(tmp_path):
    from ansibleguard.detectors.incohesive_plays import calculate_similarity

    p = tmp_path / "cohesive.yml"
    p.write_text(
        "- name: Package play\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: Install nginx\n"
        "      apt:\n"
        "        name: nginx\n"
        "    - name: Install curl\n"
        "      yum:\n"
        "        name: curl\n",
        encoding="utf-8",
    )
    count = calculate_similarity(str(p))
    assert count == 0


def test_play_two_equal_domains_not_flagged_as_micro_play(tmp_path):
    from ansibleguard.detectors.incohesive_plays import calculate_similarity

    p = tmp_path / "incohesive.yml"
    p.write_text(
        "- name: Mixed play\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: Install\n"
        "      apt:\n"
        "        name: nginx\n"
        "    - name: Start service\n"
        "      service:\n"
        "        name: nginx\n"
        "        state: started\n",
        encoding="utf-8",
    )
    # Fix B3: plays with fewer than 3 tasks are skipped — not enough tasks to
    # judge cohesion (2-task plays produce too many FPs for pkg+service pairs)
    count = calculate_similarity(str(p))
    assert count == 0


def test_multiple_plays_mixed_result(tmp_path):
    from ansibleguard.detectors.incohesive_plays import calculate_similarity

    p = tmp_path / "multi.yml"
    p.write_text(
        # play 1: all packages → cohesive
        "- name: Package play\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: Install nginx\n"
        "      apt:\n"
        "        name: nginx\n"
        "    - name: Install curl\n"
        "      apt:\n"
        "        name: curl\n"
        "    - name: Install htop\n"
        "      apt:\n"
        "        name: htop\n"
        # play 2: package + service + user (3 domains) → incohesive
        "- name: Mixed play\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: Install\n"
        "      apt:\n"
        "        name: nginx\n"
        "    - name: Enable\n"
        "      service:\n"
        "        name: nginx\n"
        "        state: started\n"
        "    - name: Add user\n"
        "      user:\n"
        "        name: deploy\n",
        encoding="utf-8",
    )
    # Package + service + user is a normal service lifecycle, not evidence of
    # unrelated responsibilities.
    count = calculate_similarity(str(p))
    assert count == 0


def test_large_balanced_specialised_mix_is_flagged(tmp_path):
    from ansibleguard.detectors.incohesive_plays import calculate_similarity

    p = tmp_path / "multi-responsibility.yml"
    p.write_text(
        "- name: Unrelated responsibilities\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - {name: Create VM, amazon.aws.ec2_instance: {name: app}}\n"
        "    - {name: Create bucket, amazon.aws.s3_bucket: {name: logs}}\n"
        "    - {name: Run container, community.docker.docker_container: {name: app}}\n"
        "    - {name: Build image, community.docker.docker_image: {name: app}}\n"
        "    - {name: Create mysql user, community.mysql.mysql_user: {name: app}}\n"
        "    - {name: Create postgres db, community.postgresql.postgresql_db: {name: app}}\n"
        "    - {name: Notify Slack, community.general.slack: {msg: done}}\n"
        "    - {name: Send mail, community.general.mail: {subject: done}}\n",
        encoding="utf-8",
    )
    assert calculate_similarity(str(p)) == 1


def test_separate_cohesive_plays_are_not_pooled_into_false_positive(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    p = tmp_path / "separated.yml"
    p.write_text(
        "- name: Cloud provisioning\n"
        "  hosts: localhost\n"
        "  tasks:\n"
        "    - {name: VM one, amazon.aws.ec2_instance: {name: one}}\n"
        "    - {name: VM two, amazon.aws.ec2_instance: {name: two}}\n"
        "- name: Database setup\n"
        "  hosts: databases\n"
        "  tasks:\n"
        "    - {name: User one, community.mysql.mysql_user: {name: one}}\n"
        "    - {name: User two, community.mysql.mysql_user: {name: two}}\n",
        encoding="utf-8",
    )
    assert calculate_similarity(str(p)) == pytest.approx(1.0)


def test_playbook_level_requires_two_strong_candidate_plays(tmp_path):
    from ansibleguard.detectors.sem_cohesion import calculate_similarity

    task_block = (
        "    - {name: VM, amazon.aws.ec2_instance: {name: app}}\n"
        "    - {name: Bucket, amazon.aws.s3_bucket: {name: logs}}\n"
        "    - {name: Container, community.docker.docker_container: {name: app}}\n"
        "    - {name: Image, community.docker.docker_image: {name: app}}\n"
        "    - {name: Mysql, community.mysql.mysql_user: {name: app}}\n"
        "    - {name: Postgres, community.postgresql.postgresql_db: {name: app}}\n"
        "    - {name: Slack, community.general.slack: {msg: done}}\n"
        "    - {name: Mail, community.general.mail: {subject: done}}\n"
    )
    p = tmp_path / "two-candidates.yml"
    p.write_text(
        "- name: Candidate one\n  hosts: one\n  tasks:\n" + task_block
        + "- name: Candidate two\n  hosts: two\n  tasks:\n" + task_block,
        encoding="utf-8",
    )
    assert calculate_similarity(str(p)) == pytest.approx(0.0)


def test_play_with_no_tasks_not_counted(tmp_path):
    from ansibleguard.detectors.incohesive_plays import calculate_similarity

    p = tmp_path / "notasks.yml"
    p.write_text(
        "- name: Play without tasks\n"
        "  hosts: all\n",
        encoding="utf-8",
    )
    count = calculate_similarity(str(p))
    assert count == 0


def test_invalid_file_returns_zero(tmp_path):
    from ansibleguard.detectors.incohesive_plays import calculate_similarity

    p = tmp_path / "bad.yml"
    p.write_text("not: yaml: content: [\n", encoding="utf-8")
    count = calculate_similarity(str(p))
    assert count == 0

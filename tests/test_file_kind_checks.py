from ansibleguard.detectors.file_kinds import (
    detect_file_kind_smells,
    detect_plaintext_sensitive_variables,
    detect_role_variable_precedence_collisions,
    detect_unpinned_ansible_dependencies,
)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_plaintext_sensitive_vars_are_reported_without_persisting_value(tmp_path):
    variables = _write(
        tmp_path / "group_vars" / "all.yml",
        "database_password: super-secret-canary\npassword_expire_days: 30\n",
    )
    count, details = detect_plaintext_sensitive_variables(variables)
    assert count == 1
    assert details[0]["variable"] == "database_password"
    assert "super-secret-canary" not in details[0]["issue"]


def test_vault_and_jinja_sensitive_vars_are_not_plaintext_findings(tmp_path):
    variables = _write(
        tmp_path / "vars" / "main.yml",
        "api_token: '{{ vault_api_token }}'\n"
        "database_password: !vault |\n"
        "  $ANSIBLE_VAULT;1.1;AES256\n"
        "  deadbeef\n",
    )
    assert detect_plaintext_sensitive_variables(variables)[0] == 0


def test_unpinned_requirements_are_file_kind_specific(tmp_path):
    requirements = _write(
        tmp_path / "requirements.yml",
        "- name: community.mysql\n- name: community.crypto\n  version: 3.0.0\n",
    )
    count, details = detect_unpinned_ansible_dependencies(requirements)
    assert count == 1
    assert details[0]["dependency"] == "community.mysql"
    assert detect_file_kind_smells(requirements)["unpinned_ansible_dependencies"] == 1


def test_external_role_meta_dependency_is_checked_but_local_role_is_not(tmp_path):
    metadata = _write(
        tmp_path / "roles" / "web" / "meta" / "main.yml",
        "dependencies:\n  - role: common\n  - src: geerlingguy.git\n",
    )
    count, details = detect_unpinned_ansible_dependencies(metadata)
    assert count == 1
    assert details[0]["dependency"] == "geerlingguy.git"


def test_role_defaults_vars_collision_is_project_level(tmp_path):
    _write(tmp_path / "roles" / "web" / "defaults" / "main.yml", "web_port: 80\n")
    vars_path = _write(
        tmp_path / "roles" / "web" / "vars" / "main.yml", "web_port: 8080\n"
    )
    metrics = detect_role_variable_precedence_collisions(tmp_path)
    assert metrics["role_variable_precedence_collisions"] == 1
    assert metrics["role_variable_precedence_collisions_details"][0]["file"] == str(
        vars_path
    )

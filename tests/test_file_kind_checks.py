from ansibleguard.detectors.file_kinds import (
    SensitiveValueClass,
    classify_sensitive_entry,
    detect_file_kind_smells,
    detect_plaintext_sensitive_variables,
    detect_role_variable_precedence_collisions,
    detect_unpinned_ansible_dependencies,
)
from ansibleguard.symbol_index import build_repository_symbol_index
from ansibleguard.analysis_context import build_repository_analysis_context


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
    assert details[0]["sensitive_class"] == "SECRET_VALUE"
    assert details[0]["evidence_level"] == "KEY_VALUE_CONTEXT"
    assert details[0]["confidence"] == "high"


def test_sensitive_key_context_classes_distinguish_values_from_configuration():
    assert classify_sensitive_entry("database_password", "literal") == (
        SensitiveValueClass.SECRET_VALUE
    )
    assert classify_sensitive_entry("password_fail_msg", "Authentication failed") == (
        SensitiveValueClass.SECRET_MESSAGE
    )
    assert classify_sensitive_entry("passwd_complex_option", "minlen=12") == (
        SensitiveValueClass.SECRET_CONFIGURATION
    )
    assert classify_sensitive_entry("credential_endpoint", "https://example.invalid") == (
        SensitiveValueClass.SECRET_PATH
    )
    assert classify_sensitive_entry("secret_backend", "vault") == (
        SensitiveValueClass.SECRET_CONFIGURATION
    )
    assert classify_sensitive_entry("token_store_configuration", "external") == (
        SensitiveValueClass.SECRET_CONFIGURATION
    )


def test_sensitive_configuration_and_messages_are_not_strong_secret_findings(
    tmp_path,
):
    variables = _write(
        tmp_path / "vars" / "main.yml",
        "password_fail_msg: Authentication failed\n"
        "passwd_complex_option: minlen=12\n"
        "credential_endpoint: https://example.invalid/credentials\n"
        "secret_backend: vault\n"
        "token_store_configuration: external\n",
    )

    assert detect_plaintext_sensitive_variables(variables) == (0, [])


def test_vault_and_jinja_sensitive_vars_are_not_plaintext_findings(tmp_path):
    variables = _write(
        tmp_path / "vars" / "main.yml",
        "api_token: '{{ vault_api_token }}'\n"
        "database_password: !vault |\n"
        "  $ANSIBLE_VAULT;1.1;AES256\n"
        "  deadbeef\n",
    )
    assert detect_plaintext_sensitive_variables(variables)[0] == 0


def test_sensitive_looking_identifiers_and_locations_are_not_secrets(tmp_path):
    variables = _write(
        tmp_path / "vars" / "main.yml",
        "token_name: Added by automation\n"
        "remote_token_url: https://example.invalid/token\n"
        "smtp_sasl_password_maps: hash:/etc/postfix/sasl_passwd\n",
    )
    assert detect_plaintext_sensitive_variables(variables) == (0, [])


def test_numeric_sensitive_looking_configuration_is_not_plaintext_secret(tmp_path):
    variables = _write(
        tmp_path / "defaults" / "main.yml",
        "api_token_ttl: 3600\nsecret_timeout: 30\npassword_limit: 5\n",
    )
    assert detect_plaintext_sensitive_variables(variables) == (0, [])


def test_real_string_secret_still_fires_after_numeric_suppression(tmp_path):
    variables = _write(
        tmp_path / "defaults" / "main.yml",
        "api_token: live-secret-material-123\n",
    )
    count, details = detect_plaintext_sensitive_variables(variables)
    assert count == 1
    assert details[0]["variable"] == "api_token"


def test_password_provider_and_reset_links_are_not_plaintext_secrets(tmp_path):
    variables = _write(
        tmp_path / "roles" / "app" / "defaults" / "main.yml",
        "external_password_provider: Example SSO\n"
        "external_password_reset_link_en: https://example.invalid/reset\n",
    )

    assert detect_plaintext_sensitive_variables(variables) == (0, [])


def test_legacy_pass_suffixes_and_nested_pass_values_are_sensitive(tmp_path):
    variables = _write(
        tmp_path / "vars" / "legacy.yml",
        "api_db_userpass: synthetic-secret\n"
        "dbpassword: synthetic-secret\n"
        "dbapwd: synthetic-secret\n"
        "users:\n"
        "  service:\n"
        "    pass: synthetic-secret\n",
    )

    count, details = detect_plaintext_sensitive_variables(variables)

    assert count == 4
    assert {detail["variable"] for detail in details} == {
        "api_db_userpass",
        "dbpassword",
        "dbapwd",
        "users.service.pass",
    }


def test_explicit_vars_filename_is_checked_outside_a_vars_directory(tmp_path):
    variables = _write(
        tmp_path / "deployment" / "devel-vars.yml",
        "api_db_userpass: synthetic-secret\n",
    )

    count, details = detect_plaintext_sensitive_variables(variables)

    assert count == 1
    assert details[0]["variable"] == "api_db_userpass"


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


def test_precedence_collision_ignores_excluded_role_var_files(tmp_path):
    defaults = _write(
        tmp_path / "roles" / "web" / "defaults" / "main.yml", "web_port: 80\n"
    )
    _write(tmp_path / "roles" / "web" / "vars" / "main.yml", "web_port: 8080\n")
    tasks = _write(
        tmp_path / "roles" / "web" / "tasks" / "main.yml",
        "- debug: {msg: ready}\n",
    )

    graph = build_repository_symbol_index(tmp_path, files=[defaults, tasks])

    assert detect_role_variable_precedence_collisions(
        tmp_path, symbol_index=graph
    )["role_variable_precedence_collisions"] == 0


def test_precedence_collision_reuses_shared_source_text(tmp_path, monkeypatch):
    defaults = _write(
        tmp_path / "roles/web/defaults/main.yml", "web_port: 80\n"
    )
    variables = _write(
        tmp_path / "roles/web/vars/main.yml", "web_port: 8080\n"
    )
    context = build_repository_analysis_context(tmp_path, [defaults, variables])
    graph = build_repository_symbol_index(
        tmp_path,
        files=[defaults, variables],
        parsed_documents=context.parsed_documents,
    )
    monkeypatch.setattr(
        type(variables),
        "read_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("vars source reread")
        ),
    )

    metrics = detect_role_variable_precedence_collisions(
        tmp_path, symbol_index=graph, repository_context=context
    )
    assert metrics["role_variable_precedence_collisions"] == 1

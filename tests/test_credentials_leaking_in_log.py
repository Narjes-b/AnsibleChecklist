from ansibleguard.detectors.credentials_leaking_in_log import (
    detect_credentials_leaking_in_log,
)


def test_credential_in_normal_play_detected(fixtures_dir):
    """Regression test for the highest-severity bug this session: the old
    code read top_level_tasks (only tasks outside any play — rare) instead
    of the full recursive task list, so it was silently blind to
    credentials sitting in ordinary hosts:/tasks: plays, the vast majority
    of real playbooks."""
    fixture = fixtures_dir / "credentials_nested_in_play.yml"
    warnings, count, _details = detect_credentials_leaking_in_log(str(fixture))
    assert count == 1


def test_no_log_true_suppresses_warning(fixtures_dir):
    """Confirms the detector isn't just flagging every set_fact — a task
    that correctly uses no_log: true must NOT be flagged."""
    fixture = fixtures_dir / "credentials_with_no_log.yml"
    warnings, count, _details = detect_credentials_leaking_in_log(str(fixture))
    assert count == 0


def test_credential_nested_in_block_detected(fixtures_dir):
    """Confirms detection still works when the sensitive task is nested
    inside a block:, not just a direct child of tasks:."""
    fixture = fixtures_dir / "credentials_nested_in_block.yml"
    warnings, count, _details = detect_credentials_leaking_in_log(str(fixture))
    assert count == 1


def test_sensitive_task_name_alone_does_not_trigger(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Check password policy\n  debug:\n    msg: policy is enabled\n",
        encoding="utf-8",
    )
    assert detect_credentials_leaking_in_log(playbook)[1] == 0


def test_non_loop_sensitive_argument_is_detected(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Configure user\n"
        "  user:\n"
        "    name: service\n"
        "    password: '{{ service_password }}'\n",
        encoding="utf-8",
    )
    assert detect_credentials_leaking_in_log(playbook)[1] == 1


def test_sensitive_argument_has_possible_log_evidence(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Configure user\n"
        "  user:\n"
        "    name: service\n"
        "    password: '{{ service_password }}'\n",
        encoding="utf-8",
    )

    _, count, details = detect_credentials_leaking_in_log(playbook)

    assert count == 1
    assert details[0]["evidence_level"] == "SENSITIVE_ARGUMENT_POSSIBLE_LOG"
    assert details[0]["semantic_status"] == "EXPOSED"
    assert details[0]["resolution_status"] == "PROVEN_EXPOSED"
    assert details[0]["confidence"] == "medium"


def test_direct_sensitive_display_has_high_confidence_evidence(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Print token\n  debug:\n    var: slack_token\n",
        encoding="utf-8",
    )

    _, count, details = detect_credentials_leaking_in_log(playbook)

    assert count == 1
    assert details[0]["evidence_level"] == "DIRECT_DISPLAY"
    assert details[0]["confidence"] == "high"


def test_dynamic_no_log_abstains_with_low_confidence(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Configure user\n"
        "  user:\n"
        "    password: '{{ service_password }}'\n"
        "  no_log: '{{ protect_credentials }}'\n",
        encoding="utf-8",
    )

    _, count, details = detect_credentials_leaking_in_log(playbook)

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["resolution_status"] == "DYNAMIC_PROTECTION_UNKNOWN"
    assert details[0]["uncertainty_sources"] == ["dynamic_no_log"]
    assert details[0]["confidence"] == "low"
    assert "dynamic_no_log" in details[0]["confidence_factors"]["negative"]


def test_module_no_log_metadata_suppresses_argument_only_finding(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Configure user\n"
        "  user:\n"
        "    name: service\n"
        "    password: '{{ service_password }}'\n",
        encoding="utf-8",
    )
    module_metadata = {
        "user": {"options": {"password": {"no_log": True}}},
    }

    assert detect_credentials_leaking_in_log(
        playbook, module_metadata=module_metadata
    )[1] == 0


def test_module_metadata_does_not_suppress_direct_display(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Print token\n  debug:\n    var: slack_token\n",
        encoding="utf-8",
    )
    module_metadata = {
        "debug": {"options": {"var": {"no_log": True}}},
    }

    _, count, details = detect_credentials_leaking_in_log(
        playbook, module_metadata=module_metadata
    )

    assert count == 1
    assert details[0]["evidence_level"] == "DIRECT_DISPLAY"


def test_injected_repository_module_metadata_is_used(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Configure user\n"
        "  user:\n"
        "    password: '{{ service_password }}'\n",
        encoding="utf-8",
    )
    module_metadata = {
        "user": {"options": {"password": {"no_log": True}}}
    }

    assert detect_credentials_leaking_in_log(
        playbook, module_metadata=module_metadata
    )[1] == 0


def test_inherited_block_no_log_protects_children(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Protected operations\n"
        "  no_log: true\n"
        "  block:\n"
        "    - name: Configure user\n"
        "      user:\n"
        "        password: '{{ service_password }}'\n",
        encoding="utf-8",
    )
    assert detect_credentials_leaking_in_log(playbook)[1] == 0


def test_locked_password_and_password_controls_are_not_credentials(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Lock account\n"
        "  user:\n"
        "    name: service\n"
        "    password: '!'\n"
        "    update_password: on_create\n",
        encoding="utf-8",
    )

    assert detect_credentials_leaking_in_log(playbook)[1] == 0


def test_private_key_format_is_not_secret_material(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Generate key\n"
        "  community.crypto.openssh_keypair:\n"
        "    path: /tmp/key\n"
        "    private_key_format: auto\n",
        encoding="utf-8",
    )

    assert detect_credentials_leaking_in_log(playbook)[1] == 0


def test_posix_pwd_environment_lookup_is_not_a_password(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Locate certificate\n"
        "  command: openssl x509 -in {{ lookup('env', 'PWD') }}/cert.pem\n",
        encoding="utf-8",
    )

    assert detect_credentials_leaking_in_log(playbook)[1] == 0


def test_debug_var_with_camel_case_password_is_detected(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Print generated password\n"
        "  debug:\n"
        "    var: newhost.openstack.adminPass\n",
        encoding="utf-8",
    )

    warnings, count, details = detect_credentials_leaking_in_log(playbook)

    assert count == 1
    assert "adminPass" in warnings[0]
    assert details[0]["line"] == 1


def test_debug_var_with_plain_sensitive_name_is_detected(tmp_path):
    playbook = tmp_path / "task.yml"
    playbook.write_text(
        "- name: Print token\n  debug:\n    var: slack_token\n",
        encoding="utf-8",
    )

    assert detect_credentials_leaking_in_log(playbook)[1] == 1


# --- register+debug chain tests ---
# These cover the bypass pattern where no_log:true protects the source task
# but the registered result (with a non-sensitive name) is later displayed.


def test_register_debug_chain_via_var_is_flagged(tmp_path):
    """debug: var: result where result was registered from a sensitive task."""
    playbook = tmp_path / "chain.yml"
    playbook.write_text(
        "- name: Create user with password\n"
        "  user:\n"
        "    name: admin\n"
        "    password: '{{ vault_password }}'\n"
        "  register: result\n"
        "- name: Show result\n"
        "  debug:\n"
        "    var: result\n",
        encoding="utf-8",
    )
    _, count, details = detect_credentials_leaking_in_log(playbook)
    assert count >= 1
    chain_detail = next(
        (d for d in details if "registered variable" in d["message"]), None
    )
    assert chain_detail is not None, "expected register+debug chain finding"
    assert "result" in chain_detail["message"]
    assert "Create user with password" in chain_detail["message"]


def test_register_debug_chain_via_msg_jinja_is_flagged(tmp_path):
    """debug: msg: '{{ result }}' also exposes the registered sensitive var."""
    playbook = tmp_path / "chain_msg.yml"
    playbook.write_text(
        "- name: Set API key\n"
        "  uri:\n"
        "    url: https://example.com/login\n"
        "    body:\n"
        "      api_key: '{{ api_key }}'\n"
        "  register: auth_response\n"
        "- name: Print response\n"
        "  debug:\n"
        "    msg: 'Auth result: {{ auth_response }}'\n",
        encoding="utf-8",
    )
    _, count, _ = detect_credentials_leaking_in_log(playbook)
    assert count >= 1


def test_register_debug_chain_source_has_no_log_chain_still_flagged(tmp_path):
    """no_log:true on the source task protects it but does NOT protect the debug task
    that exposes the registered result — the chain finding must still appear."""
    playbook = tmp_path / "chain_nolog_source.yml"
    playbook.write_text(
        "- name: Fetch secret\n"
        "  user:\n"
        "    name: svc\n"
        "    password: '{{ service_password }}'\n"
        "  register: user_result\n"
        "  no_log: true\n"
        "- name: Debug the result anyway\n"
        "  debug:\n"
        "    var: user_result\n",
        encoding="utf-8",
    )
    _, count, details = detect_credentials_leaking_in_log(playbook)
    # Source task is protected; debug task is NOT — chain finding must appear.
    chain = next((d for d in details if "registered variable" in d["message"]), None)
    assert chain is not None, "chain finding must fire even when source has no_log:true"


def test_register_debug_chain_debug_has_no_log_suppresses(tmp_path):
    """If both tasks carry no_log:true the chain finding must be suppressed.

    Source task: protected by no_log:true → no regular finding.
    Debug task: no_log:true → chain finding suppressed.
    Result: zero findings total.
    """
    playbook = tmp_path / "chain_nolog_debug.yml"
    playbook.write_text(
        "- name: Create user\n"
        "  user:\n"
        "    name: admin\n"
        "    password: '{{ vault_password }}'\n"
        "  register: result\n"
        "  no_log: true\n"
        "- name: Show result\n"
        "  debug:\n"
        "    var: result\n"
        "  no_log: true\n",
        encoding="utf-8",
    )
    _, count, _ = detect_credentials_leaking_in_log(playbook)
    assert count == 0


def test_register_debug_chain_non_sensitive_source_not_flagged(tmp_path):
    """register from a file/copy task (no sensitive args) must not trigger the chain."""
    playbook = tmp_path / "chain_safe.yml"
    playbook.write_text(
        "- name: Copy config\n"
        "  copy:\n"
        "    src: config.j2\n"
        "    dest: /etc/config\n"
        "  register: result\n"
        "- name: Show result\n"
        "  debug:\n"
        "    var: result\n",
        encoding="utf-8",
    )
    _, count, _ = detect_credentials_leaking_in_log(playbook)
    assert count == 0


def test_set_fact_laundering_then_debug_is_flagged(tmp_path):
    """set_fact assigns {{ vault_password }} to a non-sensitive name; debug logs it.
    Both tasks fire: the set_fact via sensitive_references (it touches vault_password),
    and the debug via the chain detection (connection_info is a laundered var)."""
    playbook = tmp_path / "launder.yml"
    playbook.write_text(
        "- name: Cache credentials\n"
        "  set_fact:\n"
        "    connection_info: \"{{ vault_password }}\"\n"
        "- name: Log connection\n"
        "  debug:\n"
        "    msg: \"{{ connection_info }}\"\n",
        encoding="utf-8",
    )
    _, count, details = detect_credentials_leaking_in_log(playbook)
    assert count == 2
    task_names = [d["task_name"] for d in details]
    assert "Cache credentials" in task_names   # set_fact fires
    assert "Log connection" in task_names       # debug chain fires


def test_set_fact_laundering_no_log_on_set_fact_does_not_suppress_debug_chain(tmp_path):
    """no_log on the set_fact task protects that task but the debug chain is still caught."""
    playbook = tmp_path / "launder_nolog_sf.yml"
    playbook.write_text(
        "- name: Cache credentials\n"
        "  set_fact:\n"
        "    connection_info: \"{{ vault_password }}\"\n"
        "  no_log: true\n"
        "- name: Log connection\n"
        "  debug:\n"
        "    msg: \"{{ connection_info }}\"\n",
        encoding="utf-8",
    )
    _, count, details = detect_credentials_leaking_in_log(playbook)
    # set_fact is protected; debug is not — debug chain must still fire
    assert count == 1
    assert details[0]["task_name"] == "Log connection"


def test_set_fact_with_sensitive_name_fires_for_both_tasks(tmp_path):
    """set_fact assigns to db_password (sensitive name → sensitive_paths fires) and debug
    logs {{ db_password }} (display_references fires). The laundering branch is skipped
    for sensitive-named keys, so we get exactly two findings, not three."""
    playbook = tmp_path / "sensitive_fact.yml"
    playbook.write_text(
        "- name: Store password\n"
        "  set_fact:\n"
        "    db_password: \"{{ vault_db_pass }}\"\n"
        "- name: Log it\n"
        "  debug:\n"
        "    msg: \"{{ db_password }}\"\n",
        encoding="utf-8",
    )
    _, count, details = detect_credentials_leaking_in_log(playbook)
    assert count == 2  # one for set_fact (sensitive_paths), one for debug (display_references)
    task_names = [d["task_name"] for d in details]
    assert "Store password" in task_names
    assert "Log it" in task_names


def test_set_fact_laundering_non_sensitive_value_not_flagged(tmp_path):
    """set_fact assigning a plain string (no sensitive Jinja ref) must not fire."""
    playbook = tmp_path / "safe_fact.yml"
    playbook.write_text(
        "- name: Store config\n"
        "  set_fact:\n"
        "    app_config: \"localhost:8080\"\n"
        "- name: Show config\n"
        "  debug:\n"
        "    msg: \"{{ app_config }}\"\n",
        encoding="utf-8",
    )
    _, count, _ = detect_credentials_leaking_in_log(playbook)
    assert count == 0

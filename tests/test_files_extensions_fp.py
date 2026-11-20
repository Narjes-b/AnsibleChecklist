from ansibleguard.detectors.files_extensions import check_missing_extension


def test_collection_playbook_and_json_vars_are_valid():
    assert check_missing_extension({"import_playbook": "azimuth_cloud.azimuth_ops.deploy"}) == 0
    assert check_missing_extension({"ansible.builtin.include_vars": {"file": "settings.json"}}) == 0
    assert check_missing_extension({"ansible.builtin.include_vars": "vars/"}) == 0


def test_free_form_arguments_do_not_hide_the_extension():
    assert check_missing_extension({"include_tasks": "setup.yml tags=x"}) == 0
    assert check_missing_extension({"include_tasks": "setup tags=x"}) == 1


def test_real_missing_extensions_are_still_reported():
    assert check_missing_extension({"include_tasks": "setup"}) == 1
    assert check_missing_extension({"import_playbook": "playbooks/site"}) == 1
    assert check_missing_extension({"import_tasks": "common.json"}) == 1

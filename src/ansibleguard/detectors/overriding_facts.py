import yaml


SET_FACT_KEYS = {"set_fact", "ansible.builtin.set_fact"}
SET_FACT_ARGUMENT_KEYS = {"cacheable"}


def detect_overriding_set_fact(yaml_content):
    if isinstance(yaml_content, str):
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            print("Error parsing YAML:", e)
            return set()
    else:
        data = yaml_content

    # Each entry: (fact_name, fact_value, when_condition, play_scope)
    # when_condition is None when there is no `when:` on the enclosing task.
    set_facts = []

    def find_facts_in_data(data, parent_when=None, play_scope=None):
        if isinstance(data, dict):
            when = data.get("when", parent_when)
            for key, value in data.items():
                if key in SET_FACT_KEYS:
                    if isinstance(value, dict):
                        for fact_name, fact_value in value.items():
                            if fact_name in SET_FACT_ARGUMENT_KEYS:
                                continue
                            set_facts.append((fact_name, fact_value, when, play_scope))
                else:
                    find_facts_in_data(value, when, play_scope)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                find_facts_in_data(item, parent_when, play_scope if play_scope is not None else index)

    def detect_overridden_facts():
        detected_issues = set()
        values_by_fact = {}
        for fact_name, value, when, play in set_facts:
            if when is not None or (
                isinstance(value, str) and ("{{" in value or "{%" in value)
            ):
                continue
            identity = (play, fact_name)
            values = values_by_fact.setdefault(identity, [])
            if all(value != prior for prior in values):
                values.append(value)
            if len(values) > 1:
                detected_issues.add(fact_name)
        return detected_issues

    task_only = isinstance(data, list) and not any(
        isinstance(item, dict) and "hosts" in item for item in data
    )
    find_facts_in_data(data, play_scope=0 if task_only else None)
    detected_issues = detect_overridden_facts()
    return detected_issues


def overriding_facts(file_path, parsed_document=None):
    try:
        if parsed_document is not None:
            yaml_content = parsed_document.document
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml_content = f.read()

        smelly_facts = detect_overriding_set_fact(yaml_content)
        return len(smelly_facts)

    except Exception as e:
        print(f"Could not read file {file_path}. Error: {e}")
        return None


if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    result = overriding_facts(TEST_PLAYBOOK)
    if result is not None:
        print(result)

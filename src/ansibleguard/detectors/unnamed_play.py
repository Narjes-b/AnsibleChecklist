from ruamel.yaml import YAML

_ruamel_yaml = YAML(typ="rt")
_ruamel_yaml.allow_duplicate_keys = True


def _line_of(node):
    """Real 1-indexed source line, or None if unavailable. Falls back to
    the first key's tracked line -- see detect_large_task.py's _line_of
    for why."""
    lc = getattr(node, "lc", None)
    if lc is None:
        return None
    if lc.line is not None:
        return lc.line + 1
    data = getattr(lc, "data", None)
    if data:
        try:
            first_key = next(iter(node.keys()))
            return data[first_key][0] + 1
        except Exception:
            pass
    return None


def unnamed_play(file_path):
    """
    Returns (count, details) where details is a list of
    {"line": <real line or None>} dicts, one per unnamed play -- mirrors
    credentials_leaking_in_log.py's (warnings, count) pattern.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = _ruamel_yaml.load(f)
    except Exception as e:
        print("Erreur lors de l'analyse du fichier YAML ou fichier non trouvé :", e)
        return None, []

    details = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and ("hosts" in item or "tasks" in item):
                play_name = item.get("name", None)
                if play_name is None or (
                    isinstance(play_name, str) and not play_name.strip()
                ):
                    details.append({"line": _line_of(item)})

    return len(details), details


# Tester la fonction
if __name__ == "__main__":
    from config import TEST_PLAYBOOK

    result, details = unnamed_play(TEST_PLAYBOOK)
    if result is not None:
        print(result, details)


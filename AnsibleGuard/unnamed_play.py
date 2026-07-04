import yaml


def unnamed_play(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print("Erreur lors de l'analyse du fichier YAML ou fichier non trouvé :", e)
        return None

    unnamed_plays = []

    if isinstance(data, list):
        for item in data:
            # print("item:", item)
            if isinstance(item, dict) and ("hosts" in item or "tasks" in item):
                play_name = item.get("name", None)
                if play_name is None or (
                    isinstance(play_name, str) and not play_name.strip()
                ):
                    unnamed_plays.append(item)

    return len(unnamed_plays)
    if unnamed_plays:
        return 1
    else:
        return 0


# Tester la fonction
if __name__ == "__main__":
    from config import TEST_PLAYBOOK

    result = unnamed_play(TEST_PLAYBOOK)
    if result is not None:
        print(result)

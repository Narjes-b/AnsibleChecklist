import yaml
import nltk
import spacy
import pandas as pd
from nltk.stem import WordNetLemmatizer


lemmatizer = WordNetLemmatizer()
nlp = spacy.load("en_core_web_lg")


def _collect_task_names(tasks):
    """Recursively collect named tasks, including those nested in block/rescue/always."""
    names = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("name") is not None:
            names.append(task["name"])
        for section in ("block", "rescue", "always"):
            if section in task and isinstance(task[section], list):
                names.extend(_collect_task_names(task[section]))
    return names


def calculate_similarity(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

            if not yaml_data or not isinstance(yaml_data, list):
                print("File is not a valid YAML or is empty.")
                return None

            sum_similarity = 0
            num_pairs = 0
            total_names = 0
            names_with_vector = 0

            # plays names without unnamed plays — guard against non-dict/None entries
            play_names = [
                play["name"]
                for play in yaml_data
                if isinstance(play, dict) and play.get("name") is not None
            ]

            preprocessed_play_names = [
                lemmatizer.lemmatize(name.lower()) for name in play_names
            ]

            for i in range(len(preprocessed_play_names)):
                total_names += 1
                doc_i = nlp(preprocessed_play_names[i])
                if not doc_i.has_vector:
                    continue  # Skip if no vector
                names_with_vector += 1

                for j in range(i + 1, len(preprocessed_play_names)):
                    doc_j = nlp(preprocessed_play_names[j])
                    if not doc_j.has_vector:
                        continue  # Skip if no vector

                    similarity_p = doc_i.similarity(doc_j)
                    sum_similarity += similarity_p
                    num_pairs += 1

            # tasks names without unnamed tasks — now recurses into block/rescue/always,
            # and guards against non-dict play entries
            tasks = []
            for play in yaml_data:
                if isinstance(play, dict) and isinstance(play.get("tasks"), list):
                    tasks.extend(_collect_task_names(play["tasks"]))
            task_names = tasks
            preprocessed_task_names = [
                lemmatizer.lemmatize(name.lower()) for name in task_names
            ]

            for i in range(len(preprocessed_task_names)):
                total_names += 1
                doc_i = nlp(preprocessed_task_names[i])
                if not doc_i.has_vector:
                    continue  # Skip if no vector
                names_with_vector += 1

                for j in range(i + 1, len(preprocessed_task_names)):
                    doc_j = nlp(preprocessed_task_names[j])
                    if not doc_j.has_vector:
                        continue  # Skip if no vector

                    similarity_t = doc_i.similarity(doc_j)
                    sum_similarity += similarity_t
                    num_pairs += 1

            if num_pairs > 0:
                average_similarity = sum_similarity / num_pairs
            elif total_names >= 2 and names_with_vector == 0:
                # Every name was outside the model's vocabulary (e.g. non-English
                # task/play names) — we measured nothing, so don't report "perfectly
                # cohesive". Distinct from the genuinely-too-small-to-judge case below.
                print(
                    f"Warning: {total_names} play/task name(s) found in {file_path}, "
                    "but none had a usable word vector (likely non-English or "
                    "otherwise out-of-vocabulary names). Cohesion could not be "
                    "measured for this file."
                )
                average_similarity = None
            else:
                # Genuinely too few names to form any pair (0 or 1 total) — nothing
                # to disagree about, so treat as trivially cohesive.
                average_similarity = 1

            return average_similarity

    except Exception as e:
        print(f"Impossible to read {file_path}. Error: {e}")
        return None


# Tester la fonction
if __name__ == "__main__":
    from config import TEST_PLAYBOOK

    average_similarity = calculate_similarity(str(TEST_PLAYBOOK))

    if average_similarity is not None:
        print(f"La similarité moyenne est : {average_similarity}")
    else:
        print("Pas de métriques disponibles.")


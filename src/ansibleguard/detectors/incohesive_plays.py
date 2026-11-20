"""Conservative play-level multi-responsibility detector.

Entropy is retained as diagnostic evidence, but diversity alone no longer
fires the rule.  Normal service lifecycles commonly span package, file and
service domains.  A finding now requires a large, balanced mix containing at
least three specialised responsibility domains.

API contract (unchanged): calculate_similarity(file_path) -> int
  Returns the number of incohesive plays found in the file.
"""

import yaml

from .module_domain import _collect_modules_from_tasks, cohesion_evidence


def calculate_similarity(file_path, parsed_document=None):
    if parsed_document is not None:
        yaml_data = parsed_document.document
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
        except Exception:
            return 0

    if not yaml_data or not isinstance(yaml_data, list):
        return 0

    candidates = 0
    for play in yaml_data:
        if not isinstance(play, dict) or not isinstance(play.get("tasks"), list):
            continue
        modules = _collect_modules_from_tasks(play["tasks"])
        if cohesion_evidence(modules)["is_incohesive"]:
            candidates += 1
    return candidates

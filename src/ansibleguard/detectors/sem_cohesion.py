"""Conservative playbook-level cohesion evidence.

The playbook result is based on the least-cohesive individual play, rather
than pooling unrelated-but-properly-separated plays.  Entropy remains a
diagnostic score, while the actual finding gate is handled by
``cohesion_evidence``.

API contract (unchanged): calculate_similarity(file_path) -> float | None
  1.0 = all tasks share one module domain (fully cohesive)
  0.0 = tasks spread evenly across all domains (maximally diverse)
  None = file could not be parsed or contains no tasks
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
            return None

    if not yaml_data or not isinstance(yaml_data, list):
        return None

    assessments = []
    for play in yaml_data:
        if isinstance(play, dict) and isinstance(play.get("tasks"), list):
            modules = _collect_modules_from_tasks(play["tasks"])
            if modules:
                assessments.append(cohesion_evidence(modules))

    if not assessments:
        return None
    # Preserve the historic float API.  Only a conservatively gated candidate
    # returns 0.0 and crosses the legacy threshold in smells.py.  Other plays
    # return at least 0.5 so ordinary module diversity cannot emit a finding.
    # The play-level rule reports an isolated candidate.  The playbook-level
    # rule is intentionally stricter and requires the pattern in at least two
    # plays, avoiding a duplicate file-level warning for one anomalous play.
    if sum(bool(item["is_incohesive"]) for item in assessments) >= 2:
        return 0.0
    return max(0.5, min(item["similarity"] for item in assessments))

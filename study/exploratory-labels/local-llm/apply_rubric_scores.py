# -*- coding: utf-8 -*-
"""Applies the Task 3 rubric scores to task3-comparison.csv. These scores are
a documented human(-equivalent) scoring pass against the 6-dimension rubric
(technical_correctness, contextual_grounding, diagnostic_clarity,
remediation_quality, uncertainty_calibration, actionability), each 1-5, plus
a free-text labels_agree judgment and unsupported_claims_or_errors note.
This is the scoring pass build_task3_comparison.py's docstring says is a
separate, documented step — it does not change existing_agent_label,
teammate_agent_label, or any Task 1 annotation.
"""
import csv
from pathlib import Path

SCORES = {
    "V007PILOT-MAINTAINABILITY_COMPLEXITY-005": dict(
        technical_correctness=4, contextual_grounding=3, diagnostic_clarity=4,
        remediation_quality=3, uncertainty_calibration=1, actionability=3,
        labels_agree="Reasonable — both existing reviewers called this 'uncertain'; the model's narrative treats it as a clear positive finding.",
        unsupported_claims_or_errors="States confidence=high and limitations=None on a case both independent reviewers found ambiguous enough to mark uncertain; no hedge offered.",
    ),
    "V007PILOT-MAINTAINABILITY_COMPLEXITY-011": dict(
        technical_correctness=3, contextual_grounding=4, diagnostic_clarity=4,
        remediation_quality=4, uncertainty_calibration=1, actionability=4,
        labels_agree="Sides with Reviewer A (positive); existing reviewers disagree with each other (A=positive, B/C=negative) — model does not resolve or even note the conflict.",
        unsupported_claims_or_errors="None found in the explanation text itself, but confidence=high on a case where the two existing reviewers actively disagree.",
    ),
    "V007PILOT-MAINTAINABILITY_COMPLEXITY-012": dict(
        technical_correctness=2, contextual_grounding=2, diagnostic_clarity=3,
        remediation_quality=3, uncertainty_calibration=1, actionability=3,
        labels_agree="Agrees with both existing reviewers' 'uncertain' call in substance (flags it as a real-but-minor issue) but states it with unwarranted certainty.",
        unsupported_claims_or_errors="Asserts the handler is unused 'anywhere in the playbook' — not verifiable from a single-file excerpt; the system prompt explicitly instructs against this exact kind of unverifiable claim, yet confidence=high, limitations=None.",
    ),
    "V007PILOT-MAINTAINABILITY_COMPLEXITY-016": dict(
        technical_correctness=3, contextual_grounding=1, diagnostic_clarity=2,
        remediation_quality=2, uncertainty_calibration=1, actionability=2,
        labels_agree="Sides with Reviewer A (positive); existing reviewers disagree with each other (A=positive, B/C=negative).",
        unsupported_claims_or_errors="Explanation is generic boilerplate about nesting in general; never references the actual task names visible in the supplied context (Hardware Configuration / Raspberry Pi Configuration / Device Trim), despite the system prompt explicitly requiring concrete line content, not just the detector's message restated.",
    ),
    "V007PILOT-OBJECTIVE_CORRECTNESS-001": dict(
        technical_correctness=1, contextual_grounding=4, diagnostic_clarity=3,
        remediation_quality=1, uncertainty_calibration=1, actionability=1,
        labels_agree="Sides with Reviewer B/C (positive) against Reviewer A (uncertain) — but on an incorrect technical basis.",
        unsupported_claims_or_errors="Factually wrong: claims ignore_errors 'requires a direct boolean value' and that a templated Jinja2 expression is 'not allowed'. Ansible explicitly supports ignore_errors: \"{{ some_condition }}\" as idiomatic usage. This is confidently stated, specific, well-grounded in the literal code — and incorrect. The recommended fix (hardcode a boolean) would remove working, intentional version-gating logic.",
    ),
    "V007PILOT-OBJECTIVE_CORRECTNESS-004": dict(
        technical_correctness=3, contextual_grounding=4, diagnostic_clarity=4,
        remediation_quality=4, uncertainty_calibration=2, actionability=4,
        labels_agree="Disagrees with BOTH existing reviewers (both say negative/not-a-real-issue); the model argues the chown non-idempotency concern is real. Genuinely substantive disagreement, correctly flagged here rather than resolved.",
        unsupported_claims_or_errors="None confirmed false, but worth independent verification: whether the task uses a raw chown shell invocation (genuinely non-idempotent) vs. the ansible.builtin.file module (idempotent) determines whether this claim is correct; the excerpt available doesn't settle it conclusively either way.",
    ),
    "V007PILOT-VARIABLE_REFERENCE_REASONING-002": dict(
        technical_correctness=3, contextual_grounding=4, diagnostic_clarity=3,
        remediation_quality=3, uncertainty_calibration=2, actionability=3,
        labels_agree="Both existing reviewers say negative (not a real issue); the model's narrative leans toward treating the re-assignment as a potential problem without clearly concluding either way.",
        unsupported_claims_or_errors="None found; reasonably hedged relative to other cases (lower confidence language in places), though the output schema still reports confidence=high.",
    ),
    "V007PILOT-VARIABLE_REFERENCE_REASONING-004": dict(
        technical_correctness=1, contextual_grounding=1, diagnostic_clarity=1,
        remediation_quality=2, uncertainty_calibration=1, actionability=2,
        labels_agree="Not comparable — the explanation addresses a different defect (an unused variable) than the rule being evaluated (role-variable-precedence-collision, i.e. the same variable set from two different precedence levels). This is a rule misdiagnosis, not a disagreement.",
        unsupported_claims_or_errors="The entire explanation is about the wrong problem. Whatever the model saw in the context, it did not engage with variable precedence collision at all.",
    ),
    "V007PILOT-VARIABLE_REFERENCE_REASONING-005": dict(
        technical_correctness=2, contextual_grounding=4, diagnostic_clarity=4,
        remediation_quality=3, uncertainty_calibration=1, actionability=4,
        labels_agree="Disagrees with both existing reviewers (both say negative). Model confidently asserts the variable is undefined; both independent reviewers judged it's not a real issue, most plausibly because the variable is defined elsewhere (group_vars/defaults) outside the single-file snippet.",
        unsupported_claims_or_errors="Violates its own system-prompt instruction not to assume a variable is undefined unless that is visible in the supplied context — the correct, cautious answer given a single-file excerpt is to flag this as unverifiable, not assert undefined-ness with confidence=high.",
    ),
    "V007PILOT-VARIABLE_REFERENCE_REASONING-007": dict(
        technical_correctness=2, contextual_grounding=4, diagnostic_clarity=4,
        remediation_quality=3, uncertainty_calibration=1, actionability=4,
        labels_agree="Disagrees with both existing reviewers (both say negative). Same pattern as -005/-014: confidently asserts undefined-ness from a partial-file view.",
        unsupported_claims_or_errors="Same systematic issue as -005 and -014 — treats 'not visible in this excerpt' as equivalent to 'undefined', which the system prompt explicitly warns against.",
    ),
    "V007PILOT-VARIABLE_REFERENCE_REASONING-014": dict(
        technical_correctness=2, contextual_grounding=4, diagnostic_clarity=4,
        remediation_quality=3, uncertainty_calibration=1, actionability=4,
        labels_agree="Disagrees with both existing reviewers (both say negative). Same systematic pattern as -005/-007 — the third case of three in this eval set.",
        unsupported_claims_or_errors="Same systematic issue: asserts the variable is undefined purely because it isn't visible in this file, with confidence=high and no limitation noted, despite the system prompt's explicit instruction against this.",
    ),
}

NOT_RUN_NOTES = {
    "V007PILOT-VARIABLE_REFERENCE_REASONING-001": (
        "0/4 reproducible success across repeated attempts on this exact case: one request "
        "returned an Ollama-side HTTP 500 (server log shows the task being cancelled "
        "mid-generation) and three repeats produced truncated/malformed JSON that degenerates "
        "into repeated whitespace padding mid-string instead of completing. The prompt itself "
        "(2.8KB) is smaller than several cases that succeeded cleanly, so this is not a context-"
        "length issue — it is a reproducible, case-specific model/server generation failure with "
        "no clear root cause identified. Documented as a hard failure rather than retried further."
    ),
}


def main():
    path = Path("task3-comparison.csv")
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    scored = 0
    for r in rows:
        iid = r["issue_id"]
        if iid in SCORES:
            r.update({k: str(v) for k, v in SCORES[iid].items()})
            scored += 1
        elif iid in NOT_RUN_NOTES:
            r["human_review_notes"] = NOT_RUN_NOTES[iid]

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"scored {scored}/{len(rows)} rows; {len(rows) - scored} left as not-run / unscored")


if __name__ == "__main__":
    main()

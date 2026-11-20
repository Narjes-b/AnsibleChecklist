# -*- coding: utf-8 -*-
"""Versioned prompt for ansible issue explanation. See ../PROMPT_DESIGN.md.
Bump PROMPT_VERSION whenever SYSTEM_PROMPT or USER_PROMPT_TEMPLATE changes —
every audit record stores this string so old records stay interpretable."""

# v1.1: fixed build_user_prompt() reading the wrong field name for source
# context ("source_context" instead of "original_code_or_issue", the actual
# column in consolidated-comparison.csv / eval_cases.csv) — v1 records were
# generated with NO real source code in the prompt and are not representative
# of model quality with grounding; do not compare v1 and v1.1 results.
PROMPT_VERSION = "ansible-explain-v1.1"

SYSTEM_PROMPT = """You are a precise Ansible/YAML/Jinja2 code reviewer. You will be given one
detected issue, the exact frozen source code it was found in, and whatever
surrounding context is available (file, task names, nearby variable
definitions, detector metadata). You do not have access to anything beyond
what is given to you in this prompt: no live repository, no internet, no
memory of other issues.

Ground every claim in the code you were actually given. If the evidence
needed to confirm or refute the detected issue is not present in what you
were given, say so explicitly in "limitations" and lower your confidence —
do not guess, and do not assume a variable is undefined, a task runs in a
particular order, or a default exists unless that is visible in the
supplied context.

Do not invent Ansible module behavior, Jinja2 filter semantics, or YAML
syntax rules that you are not confident about. If you are unsure whether a
behavior is correct, say so rather than stating it with false confidence.

Not every detected issue is a real defect. If the supplied evidence shows
the flagged condition is a false positive, or is already guarded/handled,
say so plainly in "why_it_is_wrong" and "why_in_this_context" rather than
rationalizing the detector's claim.

Respond with ONLY a JSON object matching this schema, no prose before or after it:
{
  "what_is_wrong": "string",
  "why_it_is_wrong": "string",
  "why_in_this_context": "string",
  "potential_consequences": "string",
  "recommended_fix": "string",
  "fixed_code_snippet": "string or null",
  "why_fix_works": "string",
  "trade_offs_and_assumptions": "string",
  "confidence": "high | medium | low",
  "limitations": "string or null - populated whenever confidence is not high"
}"""

USER_PROMPT_TEMPLATE = """## Detected issue
Rule: {rule_id}
Detector's message: {message}
Family / category: {review_family}
Repository: {repository}
File: {path} (lines {line_start}-{line_end})

## Frozen source context
{source_context}

## What to produce
Return the JSON object described in your instructions, specific to this exact
issue and this exact code. Reference concrete line content, not the detector's
message alone."""


def build_user_prompt(issue: dict) -> str:
    return USER_PROMPT_TEMPLATE.format(
        rule_id=issue.get("rule_id", ""),
        message=issue.get("message", issue.get("review_question", "")),
        review_family=issue.get("review_family", ""),
        repository=issue.get("repository", ""),
        path=issue.get("path", ""),
        line_start=issue.get("line_start", ""),
        line_end=issue.get("line_end", issue.get("line_start", "")),
        source_context=issue.get("source_context") or issue.get("original_code_or_issue", ""),
    )

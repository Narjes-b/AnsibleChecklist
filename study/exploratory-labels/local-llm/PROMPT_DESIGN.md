# Prompt design — `ansible-explain-v1`

## Why a separate, versioned prompt file

`explain.py` imports the prompt text from this document's companion
`scripts/prompt_template.py` rather than inlining it, and every audit record
(`local-llm/outputs/*.json`) stores the exact `prompt_version` string used. If the
prompt is edited, bump the version string — old audit records stay interpretable
against the prompt version they actually used, per Task 2.5's reproducibility
requirement.

## Required output schema

The model is asked to return **only** a JSON object (Ollama's `format: "json"`
constrains this at the decoding level, not just via instruction) with these keys,
directly mirroring Task 2 §3's eight explanation fields:

```json
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
  "limitations": "string or null — populated whenever confidence is not high"
}
```

## System prompt (fixed, versioned)

```
You are a precise Ansible/YAML/Jinja2 code reviewer. You will be given one
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

Respond with ONLY the JSON object described by the schema. No prose before
or after it.
```

## User prompt template (per issue)

```
## Detected issue
Rule: {rule_id}
Detector's message: {message}
Family / category: {review_family}
Repository: {repository}
File: {path} (lines {line_start}-{line_end})

## Frozen source context
{source_context}

## What to produce
Return the JSON object described in your instructions, specific to this
exact issue and this exact code. Reference concrete line content, not the
detector's message alone.
```

Nothing else is sent — no credentials, no inventory, no host_vars. The
`source_context` field is identical to what already exists in this project's
AI-shadow/stratified annotation pipelines (frozen file excerpt, numbered lines),
reused here rather than re-extracted, per the "identify existing tools or
components that should be reused" instruction in Task 2 §1.

## Known prompt-level risk

A 7B model given an explicit 8-field JSON schema can produce verbose,
template-filling prose that technically satisfies the schema without adding real
diagnostic value (e.g. restating the detector's message instead of explaining root
cause). This is exactly what the evaluation suite's "diagnostic clarity" and
"actionability" rubric dimensions (Task 3) are for — it's flagged here as an
expected failure mode to watch for, not asserted as solved by the prompt wording
alone.

# Family codebook: style/policy

## Review question

Is the stated style/policy predicate true in the frozen source, and separately, is following that policy useful or actionable for this repository?

## Two independent judgments

First label whether the documented predicate is present. Then label actionability using the shared actionability scale. A true style/policy predicate is not automatically a defect or a required change.

## Semantic labels

- `positive`: the rule’s stated syntactic or repository-policy condition is present.
- `negative`: the condition is absent, inherited tags/names/metadata satisfy it, or the detector’s cited target is wrong.
- `uncertain`: the relevant repository convention/policy cannot be established, or the source evidence is incomplete.
- `unreviewable`: the cited source or required policy evidence is unavailable/corrupt.

## Family-specific cautions

- For missing tags, check inherited play/block tags before deciding.
- For names, distinguish a true naming/length/special-character predicate from whether the name is unclear or harmful.
- For line length and file-extension rules, verify the exact cited line/path and project conventions; the cutoff alone does not prove poor quality.
- Optional Molecule/Galaxy/documentation practices require context about whether the role is tested or published that way. File absence alone is not proof the practice is required.
- A repository-specific policy should be cited if it is present in the frozen bundle; do not invent one.

## Reason codes

`predicate-present`, `predicate-absent`, `inherited-policy-satisfies`, `optional-practice`, `repository-policy-evidence`, `policy-not-in-scope`, `source-anchor-mismatch`, `insufficient-source-context`, `other`.

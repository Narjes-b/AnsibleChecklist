# Construct and lexical evidence diagnostic — 2026-10-23

All selected IDs/weights survive. **Zero subjects, Ansible applicability decisions or complete rule-evidence packets are certified. Zero labels or model calls.** These are calibration/development results, not measured accuracy. The required designs are overlapping alternatives; counts across draws are not additive.

| Draw | Selected | Candidate constructs located | File context only | Alias resolution needed | Duplicate-key review needed |
|---|---:|---:|---:|---:|---:|
| Required | 861 | 661 | 185 | 8 | 7 |
| Required, more groups | 1,266 | 963 | 283 | 11 | 9 |
| Uncertainty | 88 | 86 | 0 | 2 | 0 |
| Optional policy | 116 | 59 | 57 | 0 | 0 |

File-only context is not inherently failed retrieval: a file-level rule may need exactly that scope. A task-level rule with a file-only anchor needs independent identity repair. The builder does not choose the nearest task or clamp the line.

## What the source/metadata join reveals

| Lexical subject outcome | Required | More groups | Uncertainty | Optional |
|---|---:|---:|---:|---:|
| Exact token located | 142 | 184 | 72 | 25 |
| Case-fold match only | 119 | 185 | 14 | 19 |
| Placeholder subject | 22 | 35 | 0 | 2 |
| No named subject (`location`) | 546 | 811 | 0 | 68 |
| Token not located by this checker | 6 | 15 | 0 | 0 |
| No anchored construct for named subject | 4 | 4 | 0 | 2 |
| Unsupported subject shape | 4 | 5 | 0 | 0 |
| Template parsing incomplete | 3 | 7 | 0 | 0 |
| Not checked because YAML needs review | 15 | 20 | 2 | 0 |

An exact token is evidence of text identity, **not** proof of variable binding, scope, execution, applicability, a defect or a useful edit. Key names, register/loop-variable literals, Jinja names/attributes and task display names are checked; this is not a complete Ansible variable resolver. A missing lexical match must not become a true/false label. All 119 case-fold-only outcomes in the required draw are task subjects; no variable case-fold match was observed in that draw. Message-derived canonicalization can still lose identifier case, and handler references need case-sensitive treatment.

Placeholders such as `task:unknown` or `task:unnamed task` are identity gaps when the source has no matching literal name. A real task literally named `Unknown` remains a name. This distinction exposed a separate detector bug: the unnamed-task/duplicate-name consumers used the display sentinel rather than a typed name-presence flag. The subsequent [V3 name-presence repair](../../docs/study/structural-metrics-repair-2026-10-23.md) fixes it; this frozen diagnostic and its V2 dependency hashes remain unchanged.

## Implementation and integrity

[ground_sample_constructs.py](../../scripts/ground_sample_constructs.py) verifies the selection/metadata hash chain and local metadata packet identities. It rereads the exact Git blob and verifies both raw SHA-256 and blob OID before parsing. Immutable Git reading retains the previous offline/no-replacement/trusted-store controls.

- Compose representation nodes without constructing YAML objects or executing tags. Preflight limits: 100,000 events, depth 64, source 1 MiB. Aliases, exact duplicate representation keys, complex keys, parse failures and ambiguous enclosing units have explicit review/failure statuses. Do not use last-key-wins loading to claim complete evidence.
- Use shared task traversal for every play section and nested branch. Preserve enclosing task/play candidates and the smallest mapping separately. Plain YAML mappings may resemble Ansible tasks; structural candidates do not certify Ansible applicability.
- Source ranges come from parser marks; trimming trailing whitespace avoids assigning the next task's indentation to the previous unit. Comment attachment and semantic execution boundaries are not independently established by these parser ranges.
- Redact the full file before windowing, then scan it. Display a full unit up to 600 lines; larger units get a bounded, explicit window. Keep full parser bounds, displayed bounds, truncation and redaction flags. Neither hidden text nor a redacted decisive value becomes complete evidence.
- The 64-file cache is bounded and keyed by repository/commit/path. Every row is retained with its original identity, policy/certainty/resolution cell, stage probabilities, inverse weight and pending label state. No sampling replacement or eligibility promotion.
- Packets remain under ignored `study/evidence-local/constructs-2026-10-23/`. Tracked ledgers hold identities/statuses/hashes, not subject values or source code. Verified all **2,331** packet hashes, output hashes, unchanged input columns/weights, line ranges, display limits and residual scans. Implementation/dependency/runtime versions are recorded.

| Draw | Task candidates | Play candidates | Packets with truncated units | Packets with redacted units |
|---|---:|---:|---:|---:|
| Required | 468 | 186 | 3 | 93 |
| More groups | 683 | 276 | 8 | 149 |
| Uncertainty | 81 | 20 | 0 | 5 |
| Optional | 33 | 1 | 0 | 11 |

Candidate kinds and redaction/truncation scopes overlap within packets. Redaction flags describe the enclosing unit, not necessarily the decisive line. Tagged scalar events occur in 4 / 4 / 1 / 0 packets respectively; tags are not executed or semantically validated.

Each draw has `construct-ledger.csv`, `construct-cells.csv` and `construct-manifest.json`. Cells cross **role/instrument × rule × policy × certainty × resolution status/scope × size quartile × construct/lexical outcome**, and report selected IDs plus distinct repositories/groups. Cell counts reconcile to every selected row. They are unweighted development counts, not estimated population proportions or confidence intervals.

Validation: **109 focused tests passed** across construct grounding, shared traversal, metadata join, frozen Git retrieval, redaction/scanning and probability sampling. Coverage includes aliases/duplicates/complex keys, structure budgets, non-executing tags, ambiguous flow tasks, full-file-before-window redaction, case-sensitive tokens/registers, placeholder vs. literal names, source/packet hash rejection and retained identities/weights.

## Next retrieval methodology

1. **Route by the rule's verification unit and decision cell.** A file-level anchor, a named task, a threshold unit and a runtime-input reference need different packets. Category alone cannot decide scope or completeness.
2. **Give anonymous units stable source identities.** Use repository/commit/path plus parsed position/path, with a versioned definition. Preserve exact identifier case separately from normalized display names. Keep old occurrence IDs frozen rather than silently changing joins.
3. **Resolve hard YAML cases explicitly.** Alias use-site coordinates, ordered duplicate pairs and tag semantics need specialized/manual evidence; source text is already available in the earlier packets. Retain these rows and report insufficiency within their original partitions, not substitute easier samples.
4. **Attach complete predicates/dependencies.** Thresholds need a whole source unit and versioned normalized-LOC definition; variables/handlers need include/role/scope/precedence and external-input contracts. The local LLM's retained missing-input failure shows why a visible name alone cannot settle scope.
5. **Add source-first controls for recall.** These selected detector occurrences cannot reveal missed defects. Build a separate blind source-unit frame and probability draw, keeping nonresponse/parse/applicability outcomes explicit. Do not label unflagged units as clean without independent review.
6. **Run a fresh instrument pilot.** Verify subject/construct/dependency sufficiency by these partitions, then independent human agreement. No current packet is promoted to final evaluation or complete evidence by this diagnostic.

## Reproduce

From the project root, using new output directories:

```sh
.venv/bin/python scripts/ground_sample_constructs.py \
  --draw-root study/sampling-draws-2026-10-23 \
  --metadata-root study/evidence-metadata-2026-10-23 \
  --draw required --draw required-more-groups --draw uncertainty --draw optional-policy \
  --repositories-root study/repositories \
  --repositories-root study/cache/v0071-rerun-2026-10-22/repositories \
  --packet-root study/evidence-local/constructs-REPLAY \
  --report-root /tmp/ansibleguard-constructs-REPLAY
```

See the [sampling methodology](../../docs/study/sampling-methodology-2026-10-23.md), [metric definition](../../docs/study/structural-metrics-repair-2026-10-23.md), and [running log](../../docs/study/recovery-progress.md).

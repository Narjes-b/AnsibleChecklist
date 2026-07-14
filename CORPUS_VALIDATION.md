# Detector corpus validation

I validated the source-level detector bundles against the repository corpus with:

```bash
.venv/bin/python scripts/validate_detector_corpus.py TestData/projects
```

The run processed all 56 discovered YAML files. The final baseline was:

| Metric | Findings | Affected files |
|---|---:|---:|
| complex expressions | 1 | 1 |
| deprecated modules/FQCN aliases | 9 | 3 |
| empty abstractions | 2 | 2 |
| insecure permissions | 1 | 1 |
| long statements | 1 | 1 |
| missing abstractions | 2 | 2 |
| missing tags | 55 | 13 |
| non-idempotent commands | 2 | 2 |
| shell instead of module | 2 | 2 |
| undocumented complex tasks | 5 | 2 |
| unguarded variables | 20 | 6 |

## Corrections made from the corpus results

I found two measurable false-positive sources and corrected both:

- Empty files under `defaults`, `vars`, `group_vars`, and `host_vars` were
  incorrectly treated as empty task abstractions. This produced 20 findings;
  after limiting the rule to task/play abstractions, only two empty handler
  files remain.
- The unguarded-variable rule did not load repository `group_vars`/`host_vars`
  and treated normal `ansible_*` fact variables as undefined. Loading visible
  inventory variables and recognizing Ansible facts reduced the result from 42
  to 20 findings.

The remaining unguarded-variable results can include variables supplied at
runtime through inventory plugins, CI, or `--extra-vars`. Those definitions are
not statically observable. I therefore added `rules.known_variables` and stable
rule-ID suppressions to `.ansibleguard.yml` instead of silently ignoring them.

## Validation boundary

This is a candidate-rate and manual-sample validation, not a statistical
precision/recall claim. The bundled corpus has no labeled ground truth for all
57 rules, so an exact false-positive percentage cannot be calculated honestly.
The reproducible script prints counts and up to five source-located samples per
active metric so the corpus can be labeled in a later research pass.

# Provider-overlap comparison: 2026-10-22 frozen run

`rule-pairs.csv` is the historical comparison produced on 2026-10-22.
Use **`rule-pairs-corrected-2026-10-23.csv`** for the corrected accounting.

The correction reuses the frozen run's aggregate files and its 171
provider-complete repositories. It fixes occurrence-ID collisions across
repositories, deduplicates repeated canonical evidence, and matches remaining
same-line evidence one to one after reserving canonical shared matches.
Run and source revision are part of matching identity.

| Pair | Field | Historical | Corrected |
|---|---|---:|---:|
| non-idempotent-command / no-changed-when | ansible-lint only | 3,188 | 3,187 |
| unnamed-task / name[missing] | ansible-lint only | 751 | 736 |

All other CSV values agree with the historical file. Both tools' totals now
reconcile as matched plus unmatched for every pair.

## Counting and interpretation

Totals count canonical occurrences carrying each native rule's evidence,
including evidence assigned to another canonical provider. This differs
from the main run report's allocation by canonical provider. For example,
the 983 non-idempotent-command occurrences here include 453 internally
assigned rows and 530 rows carrying that native evidence under ansible-lint.

The nine pairs are related predicates with differing scopes and policies.
Canonical shared evidence or a shared file/line does not establish that
two tools implement equivalent rules. Unmatched evidence is not a measured
false negative. Rule activation also matters: `no-log-password` is opt-in,
so its zero count cannot establish zero detection capability.

## Reproduction

Extract `aggregate/repository-summary.csv`,
`aggregate/all-internal-source-occurrences.csv` and
`aggregate/all-ansible-lint-occurrences.csv` from the frozen run archive,
then run from the project root:

```sh
.venv/bin/python scripts/compare_with_ansible_lint.py \
  --aggregate /path/to/extracted-run/aggregate \
  --output /tmp/rule-pairs-corrected.csv
```

[The correction manifest](comparison-repair-manifest-2026-10-23.json)
records hashes of the exact aggregate inputs, implementation and corrected
CSV, plus the source archive's recorded checksum. The archive was read for
this correction; its recorded checksum was not independently recomputed.

Validation: 16 focused comparison/RQ tests passed, and all nine real-data
rows satisfy both reconciliation identities. See the
[recovery log](../../docs/study/recovery-progress.md) for the ongoing repair sequence.

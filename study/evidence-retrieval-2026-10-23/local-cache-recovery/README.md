# Exact-source retrieval with explicit local cache recovery

The current pass checks the primary clones, then the existing
`v0071-rerun-2026-10-22` source cache for the **same selected commit, path and
ID**. It makes no network requests and creates no substitute examples.

| Draw | Selected | Exact source retrieved | Recovered after primary failure | Explicit windows |
|---|---:|---:|---:|---:|
| Required | 861 | 861 | 27 | 0 |
| Required, more groups | 1,266 | 1,266 | 36 | 1 |
| Uncertainty | 88 | 88 | 2 | 0 |
| Optional policy | 116 | 116 | 0 | 0 |

The required draws are alternatives and overlap. Row totals across those
reports must not be interpreted as independent observations or pooled into
one estimate.

## Recovery provenance

The missing primary commits were available in the existing local run cache
for `osism/ansible-collection-services`, `stackhpc/ansible-slurm-appliance`
and `UtrechtUniversity/yoda`. Each restored blob was verified against the
selected full commit, literal path, regular-file mode and Git object ID,
then hashed with SHA-256. No checkout or fetch was used.

Reports record:

- The ordered configured source stores and resolved repository path.
- A controlled result code for every store attempted, including the original
  primary-clone `commit-unavailable` failure before a successful cache read.
- The selected source identity, unchanged probabilities/weights and the
  successful source-store index.
- The previous report's status, failure reason and manifest hash, plus an
  explicit `recovered_from_previous` flag.

Source-cache links can resolve only into explicitly configured trusted local
roots. Other symlinks stay blocked. The source reader does not relax size,
file-mode, path or revision checks when attempting another store.

The [primary reports](../README.md) remain unchanged. For all 2,266 previously
successful report rows, the new redacted packet hash matches the primary
packet byte for byte. Every selected ID and weight is retained, including
the rows whose source was initially unavailable.

## Evidence limits remain

This pass has **zero complete rule-specific packets** and generates no labels
or model responses. Successful source retrieval does not confirm that a
reported smell exists. The semantic subject and relevant construct have not
yet been independently verified; cross-file relationships, module/version
facts and threshold predicates require the next packet layer.

Thirteen required anchors, 22 alternative anchors and two uncertainty anchors
are affected by redaction. One alternative source packet exceeds 1,500 lines
and has an explicitly marked anchor window. These cases remain selected and
are flagged for evidence-quality review.

Line-preserving redaction runs on the complete file before display windowing.
An independent residual scan gates packet writing. All 2,331 current packet
files pass the residual scan; the scan is heuristic and does not certify
perfect redaction. Packets stay in the ignored local evidence directory.
Only statuses, hashes and provenance are tracked here.

## Reproduction

From the project root, use new output directories:

```sh
.venv/bin/python scripts/retrieve_sample_evidence.py \
  --draw-dir study/sampling-draws-2026-10-23/required \
  --repositories-root study/repositories \
  --repositories-root study/cache/v0071-rerun-2026-10-22/repositories \
  --previous-report study/evidence-retrieval-2026-10-23/required \
  --packet-dir /tmp/new-required-cache-packets \
  --report-dir /tmp/new-required-cache-report
```

The reader checks prior report hashes, the exact selection draw, IDs and
weights before recording recovery. Existing output directories are refused.
The manifests record script/redaction versions, Git/Python versions and all
limits. Reproducing source availability requires those local object stores;
source content and packet integrity are pinned by their recorded hashes.

## Validation

- 95 focused tests pass across retrieval, redaction, sampling, simulation,
  partition and report-accounting checks.
- Explicit tests cover cache recovery from a missing primary commit, trusted
  cache symlinks, attempts across unavailable stores, no fallback around the
  size limit, and previous-report identity checks.
- Verified all 2,331 current packet hashes and residual scans, all unchanged
  primary-success hashes, report/source/implementation hashes and every
  selected ID/probability/weight.
- Verified all 4,597 local packet files from the primary and recovery passes
  are ignored by Git. This count includes overlapping alternative draws and
  both retrieval attempts.

Next: join the frozen canonical occurrence's subject and predicate evidence,
verify complete constructs, then add the rule-specific dependency context.

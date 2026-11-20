# Exact-source retrieval: primary clone pass — 2026-10-23

This first pass reads `study/repositories/<owner>/<repo>` at each selected
commit. It creates one derived ledger row per selected ID. Source packets
are redacted, independently scanned and stored locally under the ignored
`study/evidence-local/retrieval-2026-10-23/` directory. Tracked reports contain
source/packet hashes and statuses, not source excerpts.

**Current retrieval results:** the [local-cache recovery pass](local-cache-recovery/README.md)
subsequently retrieved all selected sources using the original IDs. This
primary-pass report and its failures remain historical evidence.

| Draw | Selected | Source retrieved | Commit absent in primary clone | Explicit windows |
|---|---:|---:|---:|---:|
| Required | 861 | 834 | 27 | 0 |
| Required, more groups | 1,266 | 1,230 | 36 | 1 |
| Uncertainty | 88 | 86 | 2 | 0 |
| Optional policy | 116 | 116 | 0 | 0 |

The required draws are alternative workloads. Missing source commits are in
three projects: `osism/ansible-collection-services`,
`stackhpc/ansible-slurm-appliance` and `UtrechtUniversity/yoda`. These statuses
describe this primary object store; they do not establish absence from every
local cache. The selected IDs and their weights remain in the reports.

## What is verified

- Selection ledger and plan hashes, namespaced IDs and calibration-only scope.
- Full commit identity, exact tracked path, regular-file mode and Git blob ID.
- Raw blob hash and size; strict UTF-8 and source line bounds.
- No worktree substitution, line clamping, symlink following or hidden fetch.
- Full-file redaction before optional display windowing, line-count
  preservation, and an independent residual-secret scan before packet writing.
- Explicit failures for unavailable commits/paths/blobs, invalid anchors,
  oversized/non-text/encrypted source, redaction errors and residual findings.

Git replacement objects, lazy fetching and optional locks are disabled. The
reader requires Git supporting these explicit read flags. Inherited Git
overrides are removed. It does not checkout, reset, fetch or execute target
repository code. Output directories must be separate and outside source
clones; existing output directories are refused.

## What remains incomplete

`source-retrieved` means that exact, redacted base source is available. It
does not verify the semantic subject, rule applicability, complete construct,
threshold meaning or cross-file dependencies. Those fields remain false or
incomplete in every packet. The existing aggregate selection CSV does not
carry the full semantic-subject evidence needed for that next layer.

Redaction changed the anchor line for 13 of the 834 retrieved required IDs,
22 of 1,230 in the alternative draw, two of 86 uncertainty IDs, and none in
the optional-policy draw. Those are evidence-quality flags, not corrected
defects or automatic reasons to discard an example. A single alternative
packet exceeds the full-file display limit and carries an explicit window.

The residual scan is heuristic; packets remain local. No labels or model
responses were generated. Every report remains excluded from performance
scoring and has zero complete rule-specific evidence packets.

## Reproduction

From the project root, use fresh output directories. Commit `8e9a71e` contains
the exact implementation of this primary pass; later versions add explicit
source-store attempt history and recovery provenance:

```sh
.venv/bin/python scripts/retrieve_sample_evidence.py \
  --draw-dir study/sampling-draws-2026-10-23/required \
  --repositories-root study/repositories \
  --packet-dir /tmp/new-required-packets \
  --report-dir /tmp/new-required-retrieval-report
```

The manifests record implementation/redaction hashes, Git/Python versions,
selection provenance, limits and ledger hashes. Each successful row records
the exact raw source and redacted packet hashes; failures retain their IDs,
weights and controlled reason codes. Source availability may change if local
object stores are moved or removed; source content is always pinned by SHA.

The [recovery pass](local-cache-recovery/README.md) preserves this attempt and
documents how the same IDs were recovered locally. Joining canonical
subject/predicate metadata and constructing rule-specific evidence remain
pending. Context completeness requires its own QA before reviewer or
local-model use.

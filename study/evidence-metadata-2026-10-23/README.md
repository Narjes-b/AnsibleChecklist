# Frozen metadata join — 2026-10-23

Calibration/development only. This joins selected IDs to detector records; it does **not** certify a subject, a true defect, a useful fix, or complete rule evidence. No labels or model calls were generated.

| Draw | Selected / joined | Location only | Task | Variable | Attribute |
|---|---:|---:|---:|---:|---:|
| Required | 861 / 861 | 553 | 170 | 113 | 25 |
| Required, more groups | 1,266 / 1,266 | 820 | 264 | 157 | 25 |
| Uncertainty | 88 / 88 | 0 | 14 | 74 | 0 |
| Optional policy | 116 / 116 | 68 | 24 | 24 | 0 |

The two required draws are alternatives and overlap. Do not add their counts as independent samples. These unweighted counts describe the selected packets, not estimated population proportions.

## Integrity and privacy

- Independently recomputed the full 1,049,572,621-byte archive's SHA-256 and matched the recorded checksum `b89d10f7c37f7093a66162323b68f6e34ae5c76599360d759607003347fc8c66` before reading canonical records. The manifest records the actual digest.
- Read archive members as streams, without extracting paths or following archived links. Duplicate selected members are rejected. Missing, ambiguous, non-regular, oversized or invalid records retain an explicit failure in the selected ledger.
- Match the full run/repository/commit/occurrence identity, then check file, line, internal provider, native rule membership, policy, certainty and resolution cell. An occurrence ID alone is insufficient across repositories.
- Verify selection and prior retrieval manifest/ledger hashes. Preserve all selection columns and weights. Original draw and retrieval files remain unchanged.
- Record canonical member and normalized original item hashes. Tracked ledgers contain controlled statuses and subject **kinds**, not detector messages or subject values.
- Store redacted detector context under ignored `study/evidence-local/metadata-2026-10-23/`. Display context places each JSON field on separate lines before line-based redaction; it is display text, not a post-redaction JSON contract. A separate redacted subject field supports later grounding checks.
- All 2,331 packet hashes and residual scans were checked. No selected subject was changed by redaction. Generic sensitive-key/token screening changes display text in every metadata packet; this is **not** a count of real secrets. Source redaction/truncation flags remain in the earlier retrieval reports.
- Every row still has `subject_verified=false` and `evidence_complete=false`. Detector wording is an unverified claim, even when source provenance matches.

## What these results change

1. A `location` subject is not a failed retrieval: it is missing semantic identity. Resolve the enclosing task/play/file construct from the frozen YAML structure and the rule contract. Do not invent a task by clamping the line or selecting a nearby name.
2. Named tasks, variables and attributes need independent source matching. Preserve identifier case. The current canonicalizer lowercases names inferred from detector messages; a case-insensitive match cannot prove a case-sensitive variable identity. Preserve historical IDs and audit this limitation before changing canonicalization.
3. Evidence collection must follow the verification mode within each partition: exact predicate for deterministic rules; the complete measured unit and metric definition for thresholds; scope/include/precedence or history evidence for semantic rules. A category or a fixed line window cannot supply all three.
4. Join failures, ambiguous subjects, redacted decisive evidence and missing dependencies must stay in denominators as recorded evidence outcomes. Do not replace difficult IDs with easy ones. Assess evidence failure separately by rule, policy, certainty, resolution, size and repository group before a human pilot.
5. These draws are development instruments. Exposure, grouping, estimator/interval coverage and independent human agreement gates remain pending in the [methodology](../../docs/study/sampling-methodology-2026-10-23.md).

## Reproduce

From the project root, with the frozen archive and local clone stores available:

```sh
.venv/bin/python scripts/join_sample_metadata.py \
  --archive /home/aymmzn/Documents/AnsibleChecklist-results-2026-10-22/v0071-rerun-2026-10-22-results.tar.gz \
  --archive-sha256 b89d10f7c37f7093a66162323b68f6e34ae5c76599360d759607003347fc8c66 \
  --draw-root study/sampling-draws-2026-10-23 \
  --retrieval-root study/evidence-retrieval-2026-10-23/local-cache-recovery \
  --draw required --draw required-more-groups --draw uncertainty --draw optional-policy \
  --packet-root study/evidence-local/metadata-REPLAY \
  --report-root /tmp/ansibleguard-metadata-REPLAY
```

Use new output directories. Each draw directory here contains `metadata-ledger.csv` and `metadata-manifest.json`, including input/output/implementation hashes and interpretation limits. Validation: **114 focused tests passed**, covering the metadata join and preceding sampling/retrieval/comparison fixes.

# Automated evaluation status

Paper files are unchanged. Developer recruitment is deferred by the owner.

Frozen comparison: 96/96 scheduled records; execution completed.

These are output availability and operational counts, not explanation correctness or model accuracy.

| Condition | Scheduled | Available output | Failed/missing | Code suggestions delivered |
|---|---:|---:|---:|---:|
| window | 48 | 38 | 10 | 0 |
| scoped | 48 | 45 | 3 | 0 |

See explanation-operational-summary.csv for real/controlled breakdowns, bounded backend checks, latency and tokens.

## Repair controls

Eight authored reference edits pass the bounded behavioral scenarios; six pass the existing mechanical gate.
The other two are withheld because the validator reserializes task tag lists with indentation rejected by ansible-lint.
Keep this limitation; do not tune the frozen candidate on evaluation outputs.

The first two harness runs are retained under study/runs/. They exposed temporary-directory, inline-secret error-excerpt,
and TLS trust-configuration problems before the final successful reference-control run.

Authored-control success is not model-generated repair correctness. The 12-case repair inference remains gated on human source/intent review.

## Remaining human work

Use the separate reviewer A/B source ZIPs (60 active cases each). Reviewers judge independently before seeing outputs.
After source adjudication, export shuffled output packets, obtain both independent output reviews and adjudicate separately.
Repair sources need approved intent before inference; proposed edits then need behavioral checks and independent semantic review.
No independent explanation correctness, generated-fix semantic correctness, or developer benefit has yet been established.

## Runtime interruption

The execution service restarted during the comparison. Completed outputs were retained; the one unknown in-flight outcome
was recorded as interrupted-unknown and was not retried. The installed model digest and frozen implementation remained unchanged.

# V0.0.7 blinded AI-shadow protocol

## Timing and separation

Blank AI-shadow templates may be generated alongside each frozen reviewer sample. Do not create formal AI labels until the corresponding independent human labels and human adjudication are frozen. AI answers never become human labels or adjudication, and AI-shadow files remain separate from Reviewer A/B files.

For the agreement pilot, the existing AI-shadow template is blank. Keep it blank until the relevant human gold/codebook state is frozen; agreement-pilot items are permanently excluded from performance scoring. For calibration and heldout panels, generate AI files with exactly the same sample IDs and visible evidence as the frozen human items, but only AI-specific decision columns.

## Blinding procedure

Before formal AI review, create a blind input containing only the frozen row evidence, the final applicable human codebook, and the AI-specific blank fields. Hide human labels, adjudication, human-human agreement, AI precheck answers, hidden sampling metadata/weights, and any prior reviewer files. Freeze and checksum the exact AI input before review. The AI reviewer must inspect the supplied frozen evidence independently and enter only AI labels, reason, confidence, model identity, and protocol version.

Any AI output used earlier to debug schema or source context belongs under `ai-precheck/`, must be separately labeled as precheck, and cannot enter AI-vs-human estimates. Do not perform a substantive AI judgment on a panel before gold is frozen.

## Comparison

After both human labels and adjudication are frozen and the AI file is independently completed, compare the AI decision with adjudicated human gold. Produce `results/ai-vs-human-agreement.csv` and `results/ai-vs-human-summary.md`; report raw agreement, Cohen's kappa, Gwet's AC1, positive/negative/uncertain agreement, and per-rule/per-family agreement. Preserve AI and human outputs and their hashes separately. Never merge AI into a human vote or use agreement as a substitute for semantic validity.

# Review and execution notes

The previous case-specific AI source judgments remain fixed. The new source,
model, and generation settings match the earlier experiment. The source-binding,
prompting, static-fact summaries, citation selection and consistency guards differ.
All model outputs are judged again; previous adequate-output tables are not reused.

The V5.2 summary text is backend-authored and copied under the generation schema.
It is labeled as such in reporting and packet `prose_origin`. The model's free
reasoning is still reviewed, and any substantive error makes the complete output
inadequate even when its factual summary is right. This prevents summary templates
from masking wrong model reasoning in the quality score.

Known examples in the current reviewed outputs include:

- The unquoted decimal mode 2750 is correctly summarized as octal 5276, but model
  reasoning still interprets it as octal 2750 and calls it safe. Count as inadequate.
- Several custom/legacy module cases mention use of no_log even though no such
  explicit control is supplied. Count those actual assertions as inadequate.
- Mode-omission cases now acknowledge unknown actual permissions and preservation
  of an existing destination's mode, rather than asserting a default 0644. Their
  citations may still identify only a path, which does not establish mode absence.
- The JDBC source task is now bound correctly and credential-bearing body lines
  are cited, fixing the old wrong-sibling selection.

Three generic credential cases conservatively abstain because module redaction
and sensitive-value flow are not certified. The unchanged original AI reference
treated their static risk pattern as supported. These are counted as reference
disagreements in the primary score, with the semantic ambiguity made explicit;
they are not all false factual claims. Do not change source labels to favor the
new pipeline.

The full V5 prompt assumes a backend fact summary and evidence contract. The
fixed-window branch omits those by definition. Its new results are a whole-pipeline
ablation, not a fair isolated retrieval comparison or evidence that the standalone
model improved. The primary before/after claim concerns the earlier scoped
pipeline versus the new scoped pipeline, and remains a development-case result.
Report the fixed-window rerun as well; do not hide regressions in that condition.

The execution service restarted after 78 recorded outcomes. The one unknown
in-flight protected-output case was recorded as interrupted-unknown and not
retried. Completed records remain intact. The original baseline independently
had one interrupted-unknown outcome in its window condition. Both remain in their
respective denominators. Model digest and frozen implementation were unchanged.

No developer recruitment is performed. Human source/output forms and manuscripts
remain untouched. AI judgments and operational results must not be described as
independent human validation or population estimates.

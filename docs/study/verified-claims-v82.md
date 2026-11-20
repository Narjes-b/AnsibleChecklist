# Verified source explanations

Add `--explain --explain-style verified-facts` to an existing scan or diff command. The existing `--explain-style free` remains available; free prose is still the compatibility default. Model transport stays local and optional.

The verified style uses the same public `llm_*` assessment/evidence fields, with additive `llm_explanation_contract` and `llm_prose_origin` provenance. The local model selects claim IDs from a backend-certified menu. The backend supplies all factual text, bounded static decisions and citations; this is a different pipeline from unrestricted model reasoning. A deterministic primary-claim selector has the same classification and primary explanation, and any relevance benefit of model selection remains unmeasured.

Task/module binding, typed YAML permissions, inherited output controls and scope-visible definitions are verified before claims are offered. Fixed-window facts require visible proof spans; unseen values are withheld and exact supplied-window spans accompany unknown answers. A source change, invented claim ID, missing primary claim, duplicate selection or extra free prose rejects the response. No verified explanation automatically applies or proposes a code edit. Explicit requested editing remains a separate feature.

The smaller grammar avoids the previous context-budget failures. Cache keys distinguish free and verified styles. Provenance is retained in CSV, SARIF and PR annotations.

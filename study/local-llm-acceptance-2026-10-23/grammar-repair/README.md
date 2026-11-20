# Generation grammar repair — second live pass

The grammar compatibility fix works: all three local requests produced JSON answers; no HTTP errors. **Model acceptance still fails.** Preserve this pass as a development diagnostic, not accuracy evidence.

| Case | Raw assessment | Integrated result | Finding |
|---|---|---|---|
| Explicit false setting | unsupported, high confidence | error | Wrong condition assessment; source quote has one extra leading space |
| False claim contradicted by true setting | unsupported, low confidence | error | Outcome matches expectation, but source quote has one extra leading space; reasoning still invents a possible misconfiguration |
| Missing runtime input | insufficient-evidence, low confidence | schema accepted | No fix, but prose asserts the variable is undefined and the playbook **will fail**, despite acknowledging unseen definitions |
| Invalid anchor | no model request | insufficient-context | no-call gate passes |

Three requests, one attempt each, **28.406 seconds**, stable existing model digest. The manifest's **2/4 expectation matches** mean one accepted model state and one deterministic no-call gate; they are not semantic accuracy. In particular, the accepted insufficiency answer contains a material narrative contradiction.

## What changed

`GENERATION_SCHEMA` omits only `maxLength` recursively from the authoritative schema, avoiding excessive repetition in the local grammar compiler. Field/type/enum/array constraints stay in generation. The full runtime schema and validator retain character limits, byte/token bounds, citation checks and no-fix rules. The manifest now hashes both schemas. **137 focused tests passed.** Original first-pass failures remain in the parent directory.

## Required next changes

1. The model should cite file/line; the backend should attach the exact already-read source quote. Copying indentation is not a useful language-model task, and relaxing YAML whitespace indiscriminately would weaken evidence checks.
2. Replace the still-required `what_is_wrong` / `why_it_is_wrong` fields with neutral summary/reasoning. A nominal abstention must not force a definite runtime-failure narrative.
3. Separate evidence that the reported **condition exists** from whether a change is **actionable**. Here the model rejected a literal false setting because the URL uses an example domain. That does not contradict the reported source predicate.
4. Keep engineering expectations, narrative review, abstention/coverage and human final evaluation separate. Reusing these four fixtures after prompt changes is regression development, not independent validation.

Reproduction uses the parent README command with a new output directory. Full raw responses, actual prompts, schema/backend/fixture hashes and integrated results are retained in the adjacent case records.

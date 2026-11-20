# Sanity checks

Overall status: **failed**

| Check | Passed | Detail |
|---|---:|---|
| frozen_repository_count | False | found 127 |
| manifest_sha_present | True | each status row has an expected SHA |
| canonical_occurrence_identity_unique | True | 93412 occurrences |
| valid_provider | True | providers are constrained to modeled identities |
| raw_not_less_than_canonical | True | raw=96406, canonical=93412 |
| chart_source_data_present | True | found 15 source CSV files |
| chart_svgs_present | True | all required chart SVGs exist |
| provider_incompleteness_not_zeroed | True | incomplete providers remain explicit in status table |

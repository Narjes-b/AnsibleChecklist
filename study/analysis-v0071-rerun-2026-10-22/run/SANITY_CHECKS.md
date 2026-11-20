# Sanity checks

Overall status: **passed**

| Check | Passed | Detail |
|---|---:|---|
| frozen_repository_count | True | found 207 |
| manifest_sha_present | True | each status row has an expected SHA |
| canonical_occurrence_identity_unique | True | 373923 occurrences |
| valid_provider | True | providers are constrained to modeled identities |
| raw_not_less_than_canonical | True | raw=389924, canonical=373923 |
| chart_source_data_present | True | missing=[] |
| chart_svgs_present | True | verified 17 of 17 chart SVGs |
| repository_status_identity_unique | True | 207 repository status rows |
| execution_state_counts | True | overall={'complete': 171, 'partial': 35, 'failed': 1} scan={'completed': 206, 'timeout': 1} [observed; no frozen expectation for run v0071-rerun-2026-10-22] |
| analyzable_core_population | True | found 206 completed AnsibleGuard results [observed; no frozen expectation for run v0071-rerun-2026-10-22] |
| missing_core_result_not_zeroed | True | the timed-out repository retains missing counts |
| provider_completeness_is_exclusive | True | exclusive categories={'core and optional providers complete': 171, 'core complete; optional provider incomplete': 35, 'core result missing': 1} |
| internal_source_population | True | 264704 AnsibleGuard production-source occurrences |
| internal_source_sha256 | True | sha256=71be3560cfb8194aa50d63a0ce323737e35ca9aaec0d01004d114b3bd995cecd [observed; no frozen expectation for run v0071-rerun-2026-10-22] |
| internal_source_rule_count | True | 59 observed AnsibleGuard rules [observed; no frozen expectation for run v0071-rerun-2026-10-22] |
| validation_context_fields_present | True | every source occurrence has a relative file path and positive line |
| validation_stable_identity_unique | True | namespaced IDs are unique; raw occurrence_id collisions=1002 |
| internal_density_excludes_missing_repository | True | density includes only analyzable repositories |
| external_overlap_not_encoded_as_zero | True | unmodeled overlap estimate is blank |
| misleading_uncertain_actionable_chart_removed | True | certainty and actionability are reported separately |

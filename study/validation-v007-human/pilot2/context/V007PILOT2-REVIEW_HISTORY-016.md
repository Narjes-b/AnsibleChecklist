# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-016

- Repository: `ansible-collections/ibm_zos_core`
- Target commit: `f0cc9ddc4402424c1f91d920ca9455d4133c9d21`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
Fix failure handling for zos_job_query and zos_job_output v2.0.0 compatibility (#2582)

* send get job status parameters directly to zoau fetch_multiple

* add test for null id parameter passed to zos_job_query

* update zos_job_query docs and remove redundant test

* add changelog fragment

* add test for null and wildcard job id in zos_job_query

* fix failing sanity tests

* Update plugins/modules/zos_job_query.py

Co-authored-by: Ketan Kelkar <[REDACTED_EMAIL]>

* Update plugins/modules/zos_job_query.py

Co-authored-by: Ketan Kelkar <[REDACTED_EMAIL]>

* Update plugins/module_utils/job.py

Co-authored-by: Ketan Kelkar <[REDACTED_EMAIL]>

* Update tests/functional/modules/test_zos_job_query_func.py

Co-authored-by: Ketan Kelkar <[REDACTED_EMAIL]>

* Update plugins/modules/zos_job_query.py

Co-authored-by: Ketan Kelkar <[REDACTED_EMAIL]>

* Update plugins/modules/zos_job_query.py

Co-authored-by: Ketan Kelkar <[REDACTED_EMAIL]>

* update changelog fragment for job query bugfix

* add null job owner test for job query module

* update error messages for job not found

* fix failing sanity tests job_query bugfix

* fix lint issue job query changelog fragment

* update tests for job_query

* fix sanity tests, add test zos_job_query return only authorized jobs for user

* remove none default for job parameter returned parsed args

* bugfix for CEE dump issue and update test cases

* update docs and code quality for zos_job_query and tests

* update _job_not_found, ZOAU job fetch exception, and get user method

* sanity test updates, doc updates, default owner error handling

* set default owner to all, update test cases, and update job_status function

* update test cases for zos_job_query

* fix failing sanity test

* update test case names zos_job_query

* fix test case bug for ansible_tmp_dir creation

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update _job_not_found to handle all combinations of job vars with specific error message, update test case for _job_not_found

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update helper function to more descriptive name, fix rc bug for managed user creation, create variable for reused pds member name

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update query with owner and name only test case

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* Revert "update query with owner and name only test case"

This reverts commit 5e4f45318df0b6c2bf6c1ce5e0f19d9b75452380.

* update failure handling cases for zos_job_query

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update failure handling cases for zos_job_output

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* add test cases for invalid parameters for zos_job_query

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update zos_job_output job not found test cases with correct assertions

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* set job_name invalid as success when job not found for zos_job_output

* fix sanity tests

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update assertion for invalid job name test job_output

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* fix assertion invalid job name for job_output

* fix assertion invalid job name for job_output

* fix assertion job_not_found for job_output

* fix assertion job_not_found for job_output

* fix assertions job_not_found for job_output

* fix assertion job_name message job_not_found for job_output

* update logic for failure handling in zos_output if owner and name not found

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* fix incorrect failure handling scenarios

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update test cases with correct scenario outcomes

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update job_id and owner test case for job_output

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* update job_id and owner test case for job_output with correct outcome

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

* remove commented code

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>

---------

Signed-off-by: hmillersarah <[REDACTED_EMAIL]>
Co-authored-by: Ketan Kelkar <[REDACTED_EMAIL]>
Co-authored-by: surendrababuravella <39149274+surendrababuravella@users.noreply.github.com>
```

## Changed paths (not required for message-only evidence)


The rule is evaluated only on the exact target commit message above.

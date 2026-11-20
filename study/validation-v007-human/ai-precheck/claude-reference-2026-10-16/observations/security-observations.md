# Security family reference labels - observations (reviewer: AI reference, 50 rows)

## (a) Counts and hardest items
Semantic: positive 32, negative 15, uncertain 3, unreviewable 0.
Actionability: actionable 15, advisory 12, not-applicable 15, not-actionable 4, uncertain 3, blocking 1 (037).
bundle_issue != none: 8 rows (003, 013, 020, 022, 027, 039, 042, 045).

Per rule: become-scope-too-broad 0 positive, 7 negative (001,008,015,028,034,040,046), 1 uncertain (022); missing-validate-certs 8/8 positive; insecure-permissions 7 positive (004,011,025,031,037,043,049), 1 negative (018); unsafe-file-write 3/3 positive; credentials-leaking-in-log 2 positive (009,023), 5 negative (016,029,035,041,047), 1 uncertain (002); default-credentials 7 positive (003,010,017,024,030,036,048), 1 uncertain (042); plaintext-sensitive-variable positive 006,020,027,033,039; negative 013,045.

Five hardest items:
1. 017 / 036 / 020 / 039 (dummy or redacted literals in test, CI or vagrant fixtures). Predicate "default/plaintext credential literal present" is true, but the value is a stub and no real secret is exposed. I labelled positive + not-actionable (low/medium confidence). Two careful humans could equally say negative ("not sensitive").
2. 016 / 035 / 041 (credentials-leaking-in-log on uri / ipavault with no task-level no_log). I judged negative because the module argspec marks the password parameter no_log. That is outside knowledge, not bundle text; a strict human would say positive (no no_log on a task with a password).
3. 002 (cisco.dnac with dnac_log true, level DEBUG): whether module logging leaks the password depends on the collection; labelled uncertain.
4. 042 (admin/admin used to rotate Grafana password): redaction destroyed the oldPassword body and the when clause (l.91, l.93), so I could not decide; uncertain.
5. 001 / 008 / 028 / 040 (play-level become where most tasks do need root): "too broad" is a judgment; I used negative when nearly all tasks need privilege. 022 is the only one I could not judge (truncated).

## (b) Bundle defects
- 022: only lines 1-37 of 687 shown; the become scope cannot be judged. truncated-evidence.
- 003: anchor value (l.7) redacted; positive rests on l.27 (a different variable). 
- 013: anchor l.61 value redacted; I could not verify it is non-secret.
- 020, 027, 039, 045: anchor value redacted (by design) so the key judgment (real secret vs dummy; token vs expiry) is partly blind.
- 042: redaction mangled syntax: l.91 `body: '{ "oldPassword": [REDACTED_LITERAL]` swallowed the rest of the line and l.93 `when: grafana_password.status =[REDACTED_LITERAL]`; the evidence needed (guard) is hidden.
- 024 l.5 and 036 l.37: `key:[REDACTED VALUE BLOCK]` (missing space, a different token from [REDACTED_LITERAL]); inconsistent redaction markers.
- 006: only a 70-line window of a 3513-line file, sufficient here.
- 043: window 513-583 of 831; sufficient for the anchor but surrounding play unseen.
- 028 anchor line 1 is a comment, 034/040/046 anchors line 1/2 are play headers; become lines are elsewhere. Anchors for become rules point at play starts, which is fine, but 028 (l.1 vs play at l.8) is a mismatch.
- 016: anchor l.225 is a task whose only name interpolates send_key.json... the sensitive parameter is on l.233. Fine.
- 005, 013, 016 etc. include large files; entire file shown, good.

## (c) Codebook / override ambiguities
- default-credentials / plaintext-sensitive-variable: codebook says negative if "the value is not sensitive". Nothing says whether placeholder/stub literals (test, 123456, changeme, SECRET, PASSWORD) in role defaults vs test fixtures count. Suggested fix: add "A literal that is a documented placeholder or test stub in a test/CI/vagrant-only file is negative; a placeholder in role defaults or deployable inventory is positive because it becomes live if not overridden."
- credentials-leaking-in-log: codebook says "no_log omissions are evidence ... not proof"; it does not say whether module-level no_log (argspec) counts as a safeguard. Suggested fix: state whether reviewers may assume core/collection module argspec masking, or must treat missing task no_log as positive unless shown.
- unsafe-file-write: override says "inspect actual write safeguards and destination context" but the codebook has no criterion for unsafe_writes: true (014 documents a CI reason; 007, 021 give none). Suggested fix: define positive = unsafe_writes true on a non-scratch destination; justification only affects actionability.
- become-scope-too-broad: codebook says "inspect whether every task in scope needs it" but is silent on trivially local tasks (debug, fail, set_fact, assert). Suggested: ignore non-module-effect tasks when counting.
- missing-validate-certs: rule name implies the parameter is missing, but 8/8 samples have explicit validate_certs false. Codebook reason code tls-validation covers both; label meaning of "positive" should be spelled out (explicit disable counts).
- insecure-permissions: no threshold stated for 0644/0755 on files with private data (031 privkey 0644 with archive dir mode unseen; 018 0644 on public key). Suggested: tie to data sensitivity.
- Actionability scale: "blocking" vs "actionable" for credential files or world-writable executables is undefined; I used blocking only for 037.

## (d) Detector patterns
False-positive mechanisms:
- become-scope-too-broad: fires on any play-level become even when nearly all tasks are system-level (001, 008, 015, 028, 034, 040, 046). 0 of 8 clearly positive; 022 undecided.
- credentials-leaking-in-log: fires on missing task no_log for uri / ipavault / k8s-style calls where the module masks the parameter (016, 029 has no_log var, 035, 041), and on a debug of a list of template filenames (047).
- insecure-permissions: 018 flagged a public key file at 0644 and /tmp path.
- plaintext-sensitive-variable: 045 anchor is an expiry, 013 a database name (both name-matched).
True-positive patterns: validate_certs false (all 8), mode 0777/0766/0755 on credential files or dirs (004, 011, 025, 037, 043, 049), unsafe_writes true (007, 014, 021), command-line embedded password (009, 023), literal default credentials (003, 006, 010, 024, 030, 033, 048).

## (e) Sampling / evidence generation
- 4 of 7 rules in this family are skewed: all missing-validate-certs and unsafe-file-write rows positive, so the pilot barely tests specificity for them.
- Anchor mismatch between flagged line and the actual exposure for credentials-leaking-in-log (009, 023: leak via later task; 016: parameter on a different line than anchor).
- Redaction replaces non-default literals only for sensitive keys, so the exact thing a reviewer must assess for plaintext-sensitive-variable is hidden in 013, 020, 027, 039, 045. This makes those rows partly undecidable by design.
- Redaction marker inconsistency ([REDACTED VALUE BLOCK] vs [REDACTED_LITERAL]) and syntax damage (042).
- 037 bundle exposes a literal plex claim token (l.186, not redacted) and personal email addresses (l.17, 121) - suspected residual secret/PII, not repeated here.
- 013 contains a base64 private key block (l.219-227) not redacted; the file states it is an insecure development key.
- 032 bundle shows no residual secret; 003 l.28-29 shows a SHA-1 hash and salt of the demo admin password (seed data).

## (f) Rule definition vs codebook
- Rule names (missing-validate-certs, credentials-leaking-in-log) describe an absence of a safeguard; the codebook predicate is "unsafe security condition present", which covers explicit validate_certs: false. Rule definition was not consulted (not allowed); the sampled evidence shows this mismatch.
- unsafe-file-write is mapped to Security by override as "inspect actual write safeguards and destination context"; the evidence unit (unsafe_writes flag) has no codebook line.
- default-credentials/plaintext-sensitive-variable overlap strongly (030, 033, 048 fit both); codebook gives no way to distinguish.

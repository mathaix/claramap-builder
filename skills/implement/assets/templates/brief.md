# {{TASK_ID}} — {{TITLE}}

Role: {{CODING_VERIFICATION_QA_DIAGNOSIS_OR_REVIEW}}
Outcome / acceptance: {{CONCRETE_RESULT_AND_CRITERIA_LINK}}
Source / worktree / revision: {{PATH_AND_SHA}}
Relevant context: {{INSPECTED_PATHS_DECISIONS_DEPENDENCIES}}
Allowed writes/actions: {{OWNED_PATHS_OR_READ_ONLY_AND_TEST_ENVIRONMENT}}
Model / effort / reason: {{PERMITTED_SELECTION_AND_OWNER_PINS}}

Checks assigned to this executor: {{COMMANDS_AND_EXPECTED_RESULTS}}
Existing evidence to reuse: {{RECORD_PATHS_OR_NONE}}
Pending checks assigned elsewhere: {{EXECUTOR_AND_PREREQUISITES_OR_NONE}}
Stopping/reassessment condition: {{CONCRETE_FAILURE_OR_UNCERTAINTY}}

Preserve unrelated work and permissions. No Git/global config/remote changes unless
explicitly assigned and authorized. Verification/QA/review roles report defects and
write only permitted test artifacts; do not silently fix the product under test.
On a denied capability or contradicted premise, report evidence and retain partial
work. Do not emulate real tools to make a check pass.

Return: outcome, revision, changed paths (if any), check evidence, defects/pending work,
and next action. Coding completion means edits ready; only the coordinator accepts
integrated behavior. Read-only roles may return VERIFIED, FINDINGS, or BLOCKED with evidence.

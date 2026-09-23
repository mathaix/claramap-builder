# {{TASK_ID}} — {{TITLE}}

Role: {{PLANNER_CODER_TEST_RUNNER_QA_DIAGNOSIS_INTEGRATION_OR_REVIEW}}
Outcome / acceptance: {{CONCRETE_RESULT_AND_CRITERIA_LINK}}
Source / worktree / revision: {{PATH_AND_SHA}}
Relevant context: {{MINIMUM_INTENT_PATHS_DECISIONS_DEPENDENCIES}}
Task / requirement IDs: {{IDS_OR_ACCEPTANCE_REFERENCE}}
Report / trace destination: {{RUN_DIR_ARTIFACT_PATHS}}
Allowed writes/actions: {{OWNED_PATHS_OR_READ_ONLY_AND_TEST_ENVIRONMENT}}
Model / effort / dispatch route: {{EXACT_MODEL_EFFORT_OR_NOT_CONFIGURABLE_AND_ROUTE}}
Policy basis / owner pin: {{WORKER_ALLOWLIST_REVIEWER_OR_FALLBACK_AND_PIN}}
Selection reason: {{TASK_FACTS_AND_WHY_DEFAULT_OR_LIGHTER_ALLOWED_WORKER_IS_OR_IS_NOT_SUITABLE}}
Why not Codex (if bypassed): {{REVIEW_POLICY_OR_CAPABILITY_EVIDENCE_ELSE_NOT_APPLICABLE}}
Routing decision: {{EXECUTION_LEDGER_ENTRY}}

Checks assigned to this executor: {{COMMANDS_AND_EXPECTED_RESULTS}}
Existing evidence to reuse: {{RECORD_PATHS_OR_NONE}}
Pending checks assigned elsewhere: {{EXECUTOR_AND_PREREQUISITES_OR_NONE}}
Stopping/reassessment condition: {{CONCRETE_FAILURE_OR_UNCERTAINTY}}

Preserve unrelated work and permissions. No Git/global config/remote changes unless
explicitly assigned and authorized. Verification/QA/review roles report defects and
write only permitted test artifacts; do not silently fix the product under test.
On a denied capability or contradicted premise, report evidence and retain partial
work. Do not emulate real tools to make a check pass.

Return a compact report: outcome, input/result revision or checked tree, changed paths
(if any), check commands/outcomes and artifact paths, defects/pending work, actual
agent/session IDs when exposed, available trace paths/capture gaps, and next action.
Keep detailed available traces on disk; do not return a transcript dump or claim hidden
reasoning was captured. Coding completion means edits ready; only the coordinator accepts
integrated behavior. Read-only roles may return VERIFIED, FINDINGS, or BLOCKED with evidence.

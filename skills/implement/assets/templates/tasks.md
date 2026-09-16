# {{TITLE}} Tasks

Spec: [spec.md](spec.md) · Roadmap: [plan.md](plan.md)

## Phase 1 Tasks: {{PHASE_NAME}}

### T01: {{VERB_AND_OBJECT}} [{{AI_ASSISTED_OR_HUMAN}}]
Owner: {{WORKER_COORDINATOR_OR_USER}}
Acceptance: {{AC_IDS}}
Depends: {{TASK_IDS_OR_NONE}}
Files: {{EXACT_PATHS_INCLUDING_ADDITIONS_AND_DELETIONS}}
Evidence: {{SOURCE_PATHS_AND_PINNED_REVISIONS}}

Steps:
- {{SPECIFIC_CHANGE_AND_BOUNDARIES}}

Output: {{OBSERVABLE_ARTIFACT_OR_BEHAVIOR}}
Done when: {{ACCEPTANCE_AND_REQUIRED_VERIFICATION}}

| Check | Executor | Prerequisites | Expected result / allowed skips |
| --- | --- | --- | --- |
| {{RUNNABLE_COMMAND}} | {{WORKER_OR_COORDINATOR}} | {{ENVIRONMENT}} | {{EXPECTATION}} |

Integration / parallelism: {{ISOLATION_OR_SERIAL_REASON}}
Execution state: see recovery.md; review/check evidence: see status.md.

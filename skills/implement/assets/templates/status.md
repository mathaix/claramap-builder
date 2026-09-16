# {{TITLE}} Run Status

Approach / plan-review choice: {{COORDINATOR_DECISION_AND_REASON}}
Target / authorization: {{TARGET_AND_AUTHORIZED_ACTIONS}}
Baseline worktree / HEAD / base: {{PATH_AND_SHAS}}
Baseline status: {{STAGED_UNSTAGED_UNTRACKED_PATHS_AND_KNOWN_FAILURES}}
Current state and next action: [recovery.md](recovery.md), generated from recovery.json.
Refresh with scripts/run_state.py at transitions; preserve this file as evidence/history.

| Task | State | Review / tree | Commit | Checks / evidence | Remaining |
| --- | --- | --- | --- | --- | --- |
| T01 | planned | — | — | — | {{NEXT_ACTION}} |

## Acceptance Evidence
{{AC_IDS_MAPPED_TO_RESULTS}}

## Decisions and Refinement
{{LEARNINGS_AND_PLAN_REVISIONS}}

## Phase timings

Record actual start/end at transitions; report missing intervals as unknown.
Overlapping intervals are not additive wall time. Worker attempts already record elapsed time.

| Task / phase | Start UTC | End UTC | Elapsed | Evidence / wait reason |
| --- | --- | --- | --- | --- |
| {{TASK_AND_PHASE}} | {{START}} | {{END}} | {{DURATION_OR_UNKNOWN}} | {{LOG_OR_REASON}} |

## Usage
{{WORKER_REPORT_REVIEWER_AGENT_IDS_CUMULATIVE_SEMANTICS_UNKNOWNS}}

## Handoff
{{OWNER_CHOICES_EXTERNAL_STEPS_AND_UNFINISHED_CHECKS}}

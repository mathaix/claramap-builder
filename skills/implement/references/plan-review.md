# Optional design review

Use when the coordinator selects separate design review or the owner/repository requires
it. Routine implementation/test-command amendments do not automatically need this gate.
Review the affected design question; these document templates are optional aids.

Review the spec, roadmap and tasks against repository evidence. Read-only: do not
edit source, stage, fetch, merge, rebase, or reset environments.

Inputs: <REPO>, <SPEC>, <PLAN>, <TASKS>, their <PLAN_SNAPSHOT_JSON>, applicable repo rules,
<BASE_SHA>, <HEAD_SHA>, and source evidence paths. Verify the file hashes and combined artifact in that manifest yourself.

Check:
1. Intended behavior matches the user's target; every acceptance criterion has a task
   and observable proof. Preserve settled decisions.
2. Critical premises match actual code: base/conflicts, IDs/references, callers,
   schema/runtime dependencies. Name evidence contradicting a brief.
3. Tasks are coherent, independently verifiable, and dependency-ordered. A mechanical
   rename may span many files; do not split just to satisfy an arbitrary file limit.
4. Checks exist, distinguish success/failure, and run under the assigned executor's
   permissions and environment. Identify allowed skips explicitly.
5. Scope/actions comply with applicable repo and user constraints.

CHANGES is for concrete blocking defects. Wording preferences belong in SUGGESTIONS
and do not prevent APPROVE. Do not introduce new scope.

VERDICT: APPROVE | CHANGES
ARTIFACT: <combined artifact hash from verified plan-snapshot.json>
FINDINGS:
- <ID> [severity] <task/criterion> — defect, source evidence, smallest required fix
SUGGESTIONS:
- <optional, or none>

For revisions, check previous findings and affected changes; repeat broader investigation
only for a new reason. Record usage by agent ID with cumulative/per-call semantics.
Approval applies only to these hashes.

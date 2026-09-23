# Chief-of-staff execution contract

The chief keeps the goal, accepted decisions, task dependencies, and evidence summaries
in context. Specialists carry the source reads, tool output, and repair attempts in their
own contexts. This applies the context-isolation idea illustrated by the
[Claude chief-of-staff cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-01-the-chief-of-staff-agent).
The execution boundary below is this skill's policy; it does not require the Agent SDK.

## Boundary

The chief may read user intent, repository instructions, compact existing specs/reports,
run records, and Git status/revision metadata; write briefs and operational records outside
the product repository; dispatch agents; inspect bounded failure evidence; and reconcile
results. Authorized operational helpers, staging, commits, and publication are coordination
operations, subject to existing permissions and review gates. They do not permit silent
product edits. Have an assigned agent resolve conflicts, hooks that require fixes, and
integration defects. Delegate detailed source exploration, design/spec authorship, product
or test edits, test execution/interpretation, and independent review.

Use native subagents or the Codex wrapper with the existing model policy. A role is a
scope, not a mandatory extra stage: a small change can have one coder investigate,
implement, and run focused tests, then an independent reviewer. Add a planner, test-runner,
QA agent, or integrator when the uncertainty, workload, or isolation benefits justify it.
Do not bypass delegation because a task is short, cheap, or already understood.

Start specialists with only the task's necessary intent, revision, boundaries, decisions,
and evidence pointers. Avoid forwarding the entire coordinator conversation. Keep their
available transcripts, event logs, and artifacts on disk; return concise conclusions and
paths. Inspect a bounded excerpt or ask a targeted follow-up when evidence is missing.
Never invent agent/session IDs or claim access to hidden reasoning or unavailable traces.

## Execution ledger

Maintain `<run-dir>/execution.md` from first dispatch through completion, including small
runs that do not need a spec folder. This is an agent-maintained record, not generated or
enforced by the existing helpers. Record actual identities as they become available:

| Task / requirement | Role / route | Agent and session ID | Revision / owned paths | Result / status | Checks and evidence | Trace paths / capture gaps |
| --- | --- | --- | --- | --- | --- | --- |
| T1 / R1 | coder / native or Codex | actual IDs; unavailable if not exposed | input and resulting revision/tree; scope | pending, accepted, findings, blocked | commands, outcomes, log paths | available transcript/events/artifacts; missing capture |

Before dispatch, record each task's model, effort, route, task-specific selection reason,
authorizing policy entry, and evidence for any Codex bypass. Link the brief containing
the full decision; see [model routing](model-routing.md#explain-the-choice-before-dispatch).
Link briefs, output reports, review records, and resumed/replacement agent IDs. Record
failed dispatches and reassignment reasons. Native agents count as delegation even when
there is no Codex task directory. A process exit or worker's completion claim is not an
accepted result; tie acceptance to evidence for the relevant revision. Mutable worktree
results must identify their snapshot/tree or the exact state checked, not just HEAD.

SpecStory capture remains required. Verify what was captured for each route and record
missing or partial captures explicitly; missing logs do not prove that no agent ran.
Retain available traces according to repository data boundaries, and never copy secrets
or private transcripts into public specs. Keep ledger summaries compact and link artifacts.

## Direct-work exceptions

Direct product work is exceptional. A valid reason is an explicit user instruction to do
that work directly, evidence that permitted delegation routes are unavailable after checking
an authorized alternative, or a required capability that cannot be delegated. A failed
worker attempt, time savings, task size, or existing coordinator context is not enough.
A capability denial first follows the configured fallback policy; do not retry denied
commands or bypass restrictions. Higher-priority instructions and permissions still apply.

Before acting, announce the exception and add a scoped record to the ledger:

- Task, exact paths/actions, and stopping boundary.
- Reason and concrete evidence (user instruction, capability/dispatch error, or limitation).
- Alternatives considered/tried and why they cannot perform this work.
- Required checks, their assigned executor, and independent review route.

An exception within existing authorization does not require a redundant approval question.
It cannot authorize a forbidden operation or replace independent review. If there is no
authorized execution route, including a permitted scoped direct-work exception, report
the specific block and retain partial results. When the exception
ends, record actions, resulting revision, check outcomes, and any remaining gaps; return
to delegation for subsequent work. Disclose the exception and evidence path in the final
report. Do not silently broaden it to the rest of the task.

These are instructions and audit requirements. The current scripts check their documented
worker/review invariants; they do not mechanically prevent coordinator product edits.

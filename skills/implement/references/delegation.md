# Chief-of-staff delegation

Choose scoped agents for concrete results. The chief owns intent, allocation, acceptance,
and concise reporting; follow the [execution boundary and exception policy](chief-of-staff.md).

| Role | Useful when | Assigned result | Write boundary |
| --- | --- | --- | --- |
| Planner | Codebase facts or detailed design/tasks need discovery | Evidence-backed breakdown, specs, dependencies, open decisions | Read-only source; assigned spec files |
| Coder | A scoped product change is needed, including a small fix | Edits, focused checks, remaining risks | Owned paths in an isolated checkout, or one serialized writer |
| Test-runner | Checks need dedicated execution or diagnosis | Revision-specific commands, outcomes, failures and reproduction | Disposable copy, logs, test output; no product fixes unless reassigned |
| QA | Acceptance involves user-visible behavior or several services | Scenarios exercised, expected versus actual, artifacts, gaps | Authorized test environment and data; no deployment |
| Diagnosis | An uncertain cause needs investigation before choosing a fix | Reproduction, causal evidence, affected callers | Read-only source; isolated reproduction artifacts |
| Integration | Separate changes need combining or conflicts need repair | Integrated revision, conflict decisions, relevant rechecks | Assigned integration checkout; one writer |
| Independent review | The integrated change is ready, or an early design question warrants it | Findings and approval of the named tree or commit | Read-only exported copy; copy-local checks |

Roles need not be separate agents. A coder may inspect, implement, and run focused checks;
independent review remains separate. Delegate small edits with short briefs instead of
making them direct-work exceptions. Split roles when it protects context or enables useful
independent work, not to fill a pipeline.

## Dispatch

Choose the role's model from the existing policy before choosing a dispatch interface.
Ordinary workers use the allowlisted Codex models; a native interface is valid only if
it can dispatch that selected model. Otherwise use the bundled Codex wrapper. Native
Claude agents serve the configured independent-review and local-capability-fallback
roles; native availability alone does not authorize a different coding model. See
[model routing](model-routing.md). No policy change is needed for the shipped routes:

```sh
IMPLEMENT_MODEL=gpt-5.6-terra IMPLEMENT_EFFORT=medium \
  <skill>/codex_task.sh run <isolated-worktree> <run-slug>/task-01-code < code-brief.md
```

The wrapper intentionally cannot select Claude; the configured reviewer runs through the
native interface. Report a missing capability rather than claiming independence.

Use [brief.md](../assets/templates/brief.md) trimmed to the task: role, concrete output,
revision and paths, the requirement IDs it serves, allowed writes, existing evidence,
assigned checks, artifact destination, and stopping condition. Link `specs/<slug>/`
instead of pasting it. Pass only relevant context, not the entire parent conversation.
Verification, QA, and review agents report defects; they do not fix the product under test.

A test-runner can work while coding continues elsewhere, but its result covers only the
revision it saw; later changes invalidate it. Reserve shared database or service setup to
one executor. Never give simultaneous writers the same worktree.

Record every dispatch in `<run-dir>/execution.md`, including native agent/session IDs,
route, revision, result, check evidence, and available trace paths or capture gaps. Keep
Codex events and native transcripts where available; do not infer missing identities.

Require a compact return: outcome, revision/tree checked, changed paths, checks and
artifact paths, defects/pending work, trace references/gaps, and next action. Completion
is not acceptance; the chief reconciles the evidence. Request a bounded follow-up when
needed instead of importing full transcripts into the chief's context.

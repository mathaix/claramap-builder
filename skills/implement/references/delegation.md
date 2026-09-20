# Coordinator toolbox

Choose a role for a concrete result, not to fill a pipeline. The coordinator can perform
any role except independently reviewing its own implementation.

| Role | Useful when | Assigned result | Write boundary |
| --- | --- | --- | --- |
| Coding | A bounded change can run independently or needs specialist attention | Edits, focused checks, remaining risks | Owned paths in an isolated checkout, or one serialized writer |
| Verification | Test execution or diagnosis would otherwise block coding | Check evidence and failures with reproduction | Disposable copy, logs, test output; no product fixes unless reassigned |
| QA | Acceptance involves user-visible behavior or several services | Scenarios exercised, expected versus actual, artifacts, gaps | Authorized test environment and data; no deployment |
| Diagnosis | An uncertain cause needs investigation before choosing a fix | Reproduction, causal evidence, affected callers | Read-only source; isolated reproduction artifacts |
| Independent review | The integrated change is ready, or an early design question warrants it | Findings and approval of the named tree or commit | Read-only exported copy; copy-local checks |

## Dispatch

Use the native agent interface when available. Otherwise the wrapper runs coding,
verification, QA, or diagnosis Codex agents:

```sh
IMPLEMENT_MODEL=gpt-5.6-terra IMPLEMENT_EFFORT=medium \
  <skill>/codex_task.sh run <isolated-worktree> <run-slug>/task-01-code < code-brief.md
```

The wrapper intentionally cannot select Claude; the configured reviewer runs through the
native interface. Report a missing capability rather than claiming independence.

Use [brief.md](../assets/templates/brief.md) trimmed to the task: role, concrete output,
revision and paths, the requirement IDs it serves, allowed writes, existing evidence,
assigned checks, and stopping condition. Link `specs/<slug>/` instead of pasting it.
Verification and QA agents report defects; they do not fix the product under test.

A verification agent can run while coding continues elsewhere, but its result covers
only the revision it saw; later changes invalidate it. Reserve shared database or service
setup to one executor. A subagent is worthwhile when its result advances work the
coordinator can use, not to delegate a one-line edit.

Require a compact return: outcome, revision, changed files, evidence paths, actual
failures or pending checks, and next action. Completion is not acceptance; the
coordinator integrates the evidence and decides.

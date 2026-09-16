# Coordinator toolbox

Choose a role for a concrete result, not to fill a mandatory pipeline. The coordinator
can perform any role except independently reviewing its own implementation. Preserve
owner model restrictions and the runtime's actual capabilities.

| Role | Useful when | Assigned result | Write boundary |
| --- | --- | --- | --- |
| Coding | A bounded change can run independently or needs specialist attention | Edits, focused checks, remaining risks | Owned paths in an isolated checkout, or one serialized writer |
| Verification | Test execution or diagnosis would otherwise block coding | Check evidence and failures with reproduction | Disposable copy, logs, test outputs; no product fixes unless reassigned |
| QA | Acceptance involves user-visible behavior or multiple services | Scenarios exercised, expected/actual outcomes, artifacts and gaps | Authorized test environment/data; no deployment or unrelated configuration |
| Diagnosis | An uncertain cause needs investigation before choosing a fix | Reproduction, causal evidence, affected callers | Read-only source; isolated reproduction artifacts |
| Independent review | Integrated change is ready, or an early design question warrants it | Concrete findings and approval of the named tree | Read-only source via exported copy; copy-local checks |

## Dispatch

Use the native agent interface when it is available. Otherwise, the existing wrapper
can run coding, verification, QA, or diagnosis Codex agents. Role is assigned in the
brief; it does not grant permissions or create a new sandbox capability.

```sh
IMPLEMENT_MODEL=gpt-5.6-terra IMPLEMENT_EFFORT=medium \
  <skill>/codex_task.sh run <isolated-worktree> <run-slug>/task-01-code < code-brief.md
IMPLEMENT_MODEL=gpt-5.6-luna IMPLEMENT_EFFORT=medium \
  <skill>/codex_task.sh run <verification-copy> <run-slug>/task-02-verify < verify-brief.md
IMPLEMENT_MODEL=gpt-5.6-terra IMPLEMENT_EFFORT=medium \
  <skill>/codex_task.sh run <qa-copy> <run-slug>/task-03-qa < qa-brief.md
```

These are alternative examples, not three required dispatches. The coordinator chooses
models/effort from the routing reference. Opus review uses the native Claude agent
interface; the Codex wrapper intentionally does not select Claude. If that interface
is unavailable, report the missing review capability rather than claiming independence.

Use [brief.md](../assets/templates/brief.md), trimmed to the task: role, concrete output,
source revision and paths, acceptance criteria, allowed writes/actions, existing evidence,
selected checks and executor, relevant dependencies, and stopping condition. Link source
instead of pasting entire specs or transcripts. Verification/QA agents report defects;
they do not silently change the implementation they are evaluating.

Coding example: implement the input-save correction and run the affected regression.
Verification example: verify tenant isolation and rollback on the supplied revision in
the authorized local database; reuse the passing unit-test evidence.
QA example: exercise landing after an MCP interview in the authorized local stack;
check populated fields and reload behavior, capture actual outcomes, and report missing
access. Do not silently replace a real journey with mocked HTTP and call it passed.

## Coordination

No two writers share a worktree. Isolate concurrent code tasks and integrate before
final verification. A verification agent can run while coding continues elsewhere,
but its result only covers its fingerprinted inputs. The coordinator checks whether
subsequent changes invalidate it. Reserve shared DB/service setup to one executor;
independent read-only work may overlap. Limit concurrency when memory or services are
saturated. A subagent is worthwhile when its result advances work the coordinator can
use, not merely to delegate a one-line edit.

Use the wrapper's resume path for remaining work; preserve logs and valid evidence.
On a confirmed local capability restriction, use the authorized Sonnet fallback or
coordinator for that capability, without trying model after model. Reassignment does
not authorize missing secrets, production writes, or bypasses.

Require a compact return: outcome, revision, changed files (if coding), evidence paths,
actual failures/pending checks, and next action. Agent completion does not equal task
acceptance. The coordinator integrates evidence and decides whether more testing or
review would address a concrete remaining risk.

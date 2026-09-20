---
name: implement
description: "Take a feature, fix, or PR from request to checked, independently reviewed code. Claude coordinates direct work or scoped Codex workers. Use for /implement and implementation requests."
---

# Implement

Deliver the requested change, proof that its requirements are met, and an independent
final review. Claude coordinates; the bundled scripts help with workers, review snapshots,
and recovery. Nothing runs automatically. A small, settled task can be implemented directly.

## Establish the outcome

Inspect the request, relevant code, repository rules, Git state, and any existing spec or
run before asking questions. Verify critical premises (callers, schemas, dependencies)
before delegating. Preserve owner decisions, model pins, budgets, data boundaries, and
permissions. Transcripts are history, not authorization.

Product knowledge lives in the repository. For anything beyond a small, settled change:

```sh
python3 <skill>/scripts/scaffold.py <worktree> <slug> --title "<outcome>"
```

This creates `specs/<slug>/` with `requirements.md` (EARS statements, WHEN ... THE SYSTEM
SHALL ..., each with its proof), `design.md` (approach, decisions, open questions,
design-review status), and `tasks.md` (checkboxes citing requirement IDs, each naming
files, check, and executor). Fill them from what you inspected; link existing specs
instead of copying. They are committed and reviewed with the code. See
[spec format](references/spec-format.md).

Operational residue lives outside the repository at `~/.claude/implement/<repo>-<slug>/`:
worker records, review snapshots, verdicts, and `recovery.json`. Never commit those.

Separate design review is optional. Require it when the owner or repository does, or when
a consequential design question is still open. Record the choice and reason under
"Design review" in `design.md`. Approval names a commit; drift is `git diff`. See
[design review](references/plan-review.md).

## Execute and verify

Choose direct work or delegation, task grouping, and check depth to deliver a correct
result in minimal elapsed time. Routine choices within scope need no approval. Escalate
consequential choices outside scope, missing authorization, or serious unresolved risk,
and keep independent work moving.

Before dispatch read [model routing](references/model-routing.md) and
[model-policy.json](model-policy.json). Pins are binding; never silently substitute a
model. Brief workers with [delegation](references/delegation.md) and the
[brief template](assets/templates/brief.md). Roles are tools, not compulsory stages, and
a role grants no capability or permission.

No two writers share a worktree. Serialize shared database mutations. Integrate delegated
work before final verification. On a confirmed capability denial, keep partial work and
use the policy's fallback; do not retry the denied command, fake tools, or weaken checks.

Pick checks from plausible failures and the proofs in `requirements.md`, including affected
callers and shared contracts; see [verification](references/verification.md). Database
writers need real database evidence under the intended role. UI or cross-service journeys
need real QA. Mocks prove modeled behavior only. Run repository-required checks on the
integrated result. Tick a task in `tasks.md` only once its check has passed; record the
command and log path there or in `recovery.json`. Unproven work stays open.

## Review the integrated result

Independent final review is required before publishing or landing. Use the policy's
reviewer through the host's native agent interface; the Codex wrapper cannot launch
Claude. Report a missing capability rather than self-reviewing. An equivalent independent
repository review may satisfy this; keep mandated CI and remote gates.

```sh
git add -- <changed paths> specs/<slug>
python3 <skill>/scripts/review_gate.py snapshot <worktree> <review-dir> --base <base-commit>
python3 <skill>/scripts/review_copy.py <review-dir>/snapshot.json <temp-copy>
# Reviewer gets the copy, diff, specs, known findings, and check evidence.
# Save its exact reply as <review-dir>/verdict.md, then:
python3 <skill>/scripts/review_gate.py verify <worktree> <review-dir>
```

Follow [code review](references/code-review.md). Resolve P0/P1 before completion. Defer
lower findings only with rationale recorded in `tasks.md`. Approval names the exact tree;
changed content needs a delta review naming the new tree. The gate checks content and
verdict identity only. You verify reviewer independence, dispositions, and test results.

## Finish or recover

Refresh `recovery.json` at transitions with
`run_state.py <run-dir> <worktree> --next-action "..."`; it is an observed snapshot, not
a monitor. Read [recovery](references/recovery.md) before resuming: a stopped conversation
does not mean its worker stopped. Send a useful update within 60 seconds during long work.
After the final review passes, run `python3 <skill>/scripts/usage.py --run <run-dir>`.
It detects the current Claude session, sums tokens per model across Codex workers, the
coordinator, and subagents, prints the table, and saves it as `<run-dir>/usage.md`.
Include that table in the final response. Tokens are not dollars.

## Tools

| Need | Tool or reference |
| --- | --- |
| Create `specs/<slug>/` | `scripts/scaffold.py`; [spec format](references/spec-format.md) |
| Start/resume workers, inspect usage | `codex_task.sh run` / `resume` / `cost`; [delegation](references/delegation.md) |
| Snapshot, export, verify a review | `review_gate.py`, `review_copy.py`; [execution](references/execution.md) |
| Observe workers and Git | `run_state.py`; [recovery](references/recovery.md) |
| Tokens per model across workers, coordinator, and subagents | `scripts/usage.py --run <run-dir>` (session auto-detected) |
| See a complete small run | [Example](references/example-run.md) |
| Capture conversations | [SpecStory](references/specstory.md) |

Paths are relative to the installed skill; run helpers with `python3`. SpecStory capture
is required for coordinator and worker sessions. Validate helper changes with
`python3 -m unittest discover -s <skill>/tests -v`. Use the separate
[improve-workflow skill](https://github.com/mathaix/skills/tree/main/skills/improve-workflow)
only when asked to analyze runs.

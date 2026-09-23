# How Claramap Builder orchestrates development

[Claramap Builder](../README.md) · [Your first build](usage.md) · [Installation and configuration](installation.md)

`/implement` is Claramap Builder's primary command. It turns a goal into scoped work,
coordinates execution, and evaluates evidence for the integrated result. Claude Code
acts as chief of staff; Codex workers and native review/fallback agents take bounded
assignments in separate contexts under the configured model policy. Product work is delegated by default, including small fixes.

![Claude coordinates workers and integrates a verified result](../skills/implement/assets/claramap-builder-hero.png)

## Start a run

After [setup](installation.md#requirements), start Claude in your product repository:

```sh
specstory run claude --no-cloud-sync
```

Then give it a concrete outcome:

```text
/implement Fix the input-save bug. Reproduce it locally, preserve existing permissions,
and verify that the saved value survives a reload.
```

Include acceptance conditions, environment constraints, and any authorized external
steps. A request to fix code does not automatically authorize deployment or messages.
The [complete synthetic example](../skills/implement/references/example-run.md) shows a
request, run record, check evidence, review verdict, and final response.

## From goal to completed change

1. **Ground and break down the goal.** The chief establishes intent and constraints, then delegates codebase investigation to a planner. The planner returns findings, a task breakdown, and evidence references; the chief settles assignments and acceptance criteria.
2. **Delegate with context.** Each worker receives the relevant revision, code paths, requirements, allowed changes, and assigned checks. Independent coding work uses isolated worktrees.
3. **Verify and integrate.** Assigned workers exercise affected behavior and integrate changes. The chief reconciles their evidence, commissions independent review of the final content, and decides whether acceptance criteria are met. Integration conflicts and product repairs remain worker assignments.
4. **Iterate to completion.** Failed checks and blocking review findings return to the chief for assignment to a repair worker. After repeated failed repairs, it reassesses the cause and approach. Missing access or authorization is reported, and unproven work stays open.

## Match workers to the work

Model selection depends on uncertainty and interaction. A mechanical change with an
established example can use a lighter worker; ordinary integrations call for more
capability; subtle state, concurrency, or permission changes need stronger reasoning.
Each brief records the selected model, effort, and reason, within your model policy
and budget. Before dispatch, the chief explains the chosen model and effort, the task
facts behind the choice, and the policy entry permitting it. If it bypasses Codex,
it must explain why with the review-role policy or capability evidence. The decision
is saved in the brief and `execution.md`; the final report summarizes models and changes.
A plausible explanation cannot authorize an out-of-policy model. See [model routing](../skills/implement/references/model-routing.md).

A small fix can use one coder to investigate, implement, and run focused checks,
followed by independent review. Larger work can separate planning, coding,
test-running, diagnosis, and QA. These are responsibilities, not compulsory stages. Separate design review is used for consequential
open questions or when required by you or the repository. Independent final review
remains required.

## Keep the chief focused

The chief retains requirements, assignments, decisions, results, and unresolved risks.
Workers retain detailed source exploration, attempts, and tool output in their own
contexts. Their return includes a concise outcome, revision, checks, open issues,
agent/session identity, and paths to available traces. The chief follows those paths
for a specific uncertainty instead of ingesting every transcript. See
[the architecture and cookbook reference](architecture.md#chief-of-staff-responsibilities-and-context).

Direct product work is an exception. Before acting, the chief must state and record
why delegation cannot serve that action, evidence for the reason, alternatives
considered, scope, and the check/review plan. A user instruction, unavailable permitted
delegation routes, or a necessary capability that cannot be delegated may justify it;
"quick" or "already in context" does not. Normal authorization and independent review
still apply. The [skill policy](../skills/implement/references/chief-of-staff.md) defines
the boundary; no helper currently blocks coordinator edits mechanically.

## Keep the goal and progress recoverable

Beyond a small change, the spec lives in your repository at `specs/<slug>/`:
`requirements.md` in EARS form (WHEN ... THE SYSTEM SHALL ...), `design.md`, and a
checkbox `tasks.md` that cites requirement IDs. It is committed and reviewed with the
code. These bundled templates use [Kiro's feature-spec structure and EARS](../skills/implement/references/spec-format.md).
SpecFlow informs the surrounding workflow and worker context.
Execution records such as worker records,
review snapshots, verdicts, `execution.md`, and `recovery.json` stay under
`~/.claude/implement/<project>-<slug>/`. SpecStory conversation history lives under the
worktree's `.specstory/history/`. See [Where files live](architecture.md#where-files-live)
for the directory layout, who maintains each record, and what belongs in Git.
Every run, including one without a spec folder, keeps `execution.md` with task
assignments, actual agent identities, result/trace pointers, capture gaps, and
any direct-work exceptions. The coordinator maintains it; helpers do not generate it.

## What the tools establish

| Tool result | What it verifies | What Claude must still judge |
| --- | --- | --- |
| Worker exits successfully | The wrapper received completion output | Whether the requested work is correct and complete |
| Review gate passes | The captured Git state/content and approval naming its tree match | Reviewer independence, finding dispositions, and required test success |
| Recovery reports worker and Git state | Lock state, last attempt record, HEAD, and working-tree status at that moment | Whether the work is accepted, reviewed, and ready to land |

A copied review tree contains no `.git`, ignored files, or provisioned dependencies;
submodules and escaping symlinks are rejected, and Git LFS content is not fetched. Check
results are recorded beside their task; see [verification](../skills/implement/references/verification.md).

## Useful steering

```text
Resume the existing run. Reconcile Git and worker state with specs/<slug>/tasks.md,
preserve open findings, and rerun only checks whose inputs changed.
```

```text
Use a verification agent for the real database behavior. Keep shared database writes
serialized and report anything that could not be exercised.
```

The result is done when every requirement's proof passes, required checks pass, and independent
review approves the final integrated content. Claude reports delivered behavior, evidence,
and remaining limitations. Usage reports cover available recorded sessions; check
[coverage limits](architecture.md#usage-report-coverage) before treating them as run totals.
Ask [improve-workflow](improve-workflow.md) to analyze the run later.

For tool commands, see [execution](../skills/implement/references/execution.md),
[delegation](../skills/implement/references/delegation.md), and
[verification](../skills/implement/references/verification.md).
`IMPLEMENT_ROOT` changes the wrapper's run root; use the same root for other helpers' paths.
The [skill instructions](../skills/implement/SKILL.md) define coordinator behavior.

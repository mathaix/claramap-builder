# Your first build with Claramap Builder

[Claramap Builder](../README.md) · [Installation and configuration](installation.md) · [How orchestration works](implement.md)

Start with a small feature or bug fix in an existing Git repository. Give `/implement`
a concrete outcome and a way to recognize success.

See [architecture](architecture.md) for how Claude, Codex, and
SpecStory work together and what the AgentSkill package contains.

## 1. Install and check access

Follow [installation](installation.md#personal-installation) to install both skills in one command.
You need authenticated Claude Code, Python 3.11+, Git, SpecStory, and access to the
[configured independent reviewer](installation.md#model-policy). Codex CLI and an
allowed worker model are needed if Claude delegates work to Codex.

The installer copies the skills; it does not install or authenticate these dependencies.

## 2. Start in your project

```sh
cd /path/to/your/project
specstory run claude --no-cloud-sync
```

When using Codex workers, also keep background capture running in another terminal
in the relevant worktree:

```sh
specstory watch --no-cloud-sync
```

See the [capture setup](installation.md#run-claude-and-codex-through-specstory) for
separate worktrees and how to confirm worker sessions are captured.

## 3. Give it a goal

```text
/implement Fix the display-name setting: it appears saved but disappears after
reload. Reproduce the bug, preserve existing account permissions, and verify the fix.
```

Include known constraints and acceptance criteria. Claude acts as chief of staff:
it delegates investigation and planning, then assigns scoped implementation and checks.
Workers receive relevant context and a model selected for the task's complexity.
The chief reconciles their results, directs integration and repairs, and obtains an
independent review. A small fix can use one coder plus the independent reviewer.

The chief does not code by default. Any direct-work exception must be explained before
acting, recorded with evidence and alternatives, and disclosed in the final report.
See the [chief-of-staff architecture](architecture.md#chief-of-staff-responsibilities-and-context).

You can steer the work with existing specs, model preferences, budget constraints,
and environment access. Those constraints remain in force throughout the run.

## 4. Inspect the result

The final report explains the delivered behavior, checks performed, review outcome,
executor assignments, any direct-work exceptions, and remaining limitations.
A successful worker exit alone does not establish completion.
Required checks and independent review must pass; unavailable access or evidence stays
explicitly pending.

| Record | Where to find it |
| --- | --- |
| Requirements, design, and task progress for larger changes | `specs/<slug>/` in your project |
| Assignment identities, trace pointers, capture gaps, and exceptions | `<run-dir>/execution.md`, maintained by the chief |
| Worker attempts, review snapshots, and recovery state | `~/.claude/implement/<project>-<slug>/` by default |
| Captured conversation history | `.specstory/history/` in the relevant worktree |

For a concrete directory tree, file ownership, and what to commit, see
[Where files live](architecture.md#where-files-live).

The [illustrative walkthrough](../skills/implement/references/example-run.md) shows
these records using a synthetic example. Keep your real transcripts and execution
logs local.

## Resume interrupted work

In the project, ask:

```text
/implement Resume the existing run for the display-name fix. Reconcile Git and
worker state, preserve partial changes and open findings, and continue remaining work.
```

The coordinator checks whether workers are still active before dispatching more work
and reuses evidence that remains valid. See [recovery details](../skills/implement/references/recovery.md).

## Improve the next build

Use the included companion `improve-workflow` skill to investigate how a run
went. Ask it to explain repeated checks, slow handoffs, or missing verification, then
apply the changes you choose. Start with the [workflow improvement guide](improve-workflow.md).

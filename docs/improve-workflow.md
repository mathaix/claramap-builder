# Improve how the next build runs

[Claramap Builder](../README.md) · [Your first build](usage.md) · [Installation](installation.md) · [Implement guide](implement.md)

`/improve-workflow` is Claramap Builder's feedback loop. It examines completed work to
explain where time went, which work repeated, and what verification was missing.
It recommends changes and can update the relevant skills and tools when requested.

Use it to investigate concrete questions:

- Why did a small fix take an hour?
- Did multiple workers repeat the same checks on unchanged code?
- Where did handoffs or environment failures hold up the build?
- Did a shorter run leave important behavior unverified?

An implementation run does not automatically start an audit or rewrite a skill.

## Review a run

With [Claude Code and SpecStory set up](installation.md#requirements), open Claude Code through `specstory run claude --no-cloud-sync` in the product repository whose work you want to inspect. Reading existing evidence does not require launching Codex. Identify the runs or time window and ask a concrete question:

```text
/improve-workflow Review the last three runs in ~/.claude/implement and this project's
.specstory/history. Where is work getting held up? Recommend changes; do not edit yet.
```

The skill reads relevant summaries first, then checks attempts, test records, review results, and conversation excerpts where needed. It reports evidence-linked findings and distinguishes measured delays from inferred causes or missing information. Comparing similar tasks matters: one faster run does not establish a trend.

## What evidence it uses

| Source | What it contributes |
| --- | --- |
| `specs/<slug>/` in the product repository | Requirements, design decisions, tasks, and recorded progress |
| `~/.claude/implement/<project>-<task>/` | Run status, worker attempts, check evidence, review outcomes, and recovery state from implement |
| `.specstory/history/` in the product worktree | Captured conversation history: changed requests, handoffs, and waits |
| Relevant source and Git state | The instructions, tools, and revisions behind the reported behavior |

SpecStory is required by this setup and should capture the Claude and Codex sessions being reviewed. If an older run has no captured history, analyze the available evidence and state that limitation; missing history cannot be reconstructed from summary reports alone. Keep real reports and transcripts local. See the [SpecStory and evidence guide](../skills/improve-workflow/references/specstory.md) for capture commands, timing limits, and the feedback diagram.

## Apply an improvement

Name the maintained source and the changes you want made:

```text
/improve-workflow Apply the duplicate-check improvements from this review in
~/claramap-builder. Update the instructions and helpers, verify the affected behavior,
and report what must be measured in future runs.
```

The skill can use analyst, coding, or verification agents when useful. It targets the observed problem, preserves required checks and owner decisions, and verifies the changed behavior. A request to review alone leaves files unchanged.

If you also want publication and installation, include that in your request. The [update instructions](installation.md#update) explain replacement and backups. Existing coordinators must reread updated skills; running workers retain their original briefs.

## Return to implementation

Use [implement](implement.md) for the next product change. Later, ask improve-workflow to compare comparable runs against the intended signal—for example, fewer duplicate checks or shorter handoffs with required verification still covered. Passing helper tests alone does not establish that development is faster.

Read the [improve-workflow skill instructions](../skills/improve-workflow/SKILL.md) for the analysis and change workflow, or use its optional [review template](../skills/improve-workflow/assets/review-template.md) for a larger audit.

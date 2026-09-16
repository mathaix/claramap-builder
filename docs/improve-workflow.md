# Using improve-workflow

[All guides](usage.md) · [Installation](installation.md) · [Implement guide](implement.md)

Improve-workflow examines how code development ran: where time went, which work repeated, and what verification was missing. It can recommend changes or update the relevant skill and tools when you ask it to.

## Review a run

Open Claude Code in the product repository whose work you want to inspect. Identify the runs or time window and ask a concrete question:

```text
/improve-workflow Review the last three runs in ~/.claude/implement and this project's
.specstory/history. Where is work getting held up? Recommend changes; do not edit yet.
```

The skill reads relevant summaries first, then checks attempts, test records, review results, and conversation excerpts where needed. It reports evidence-linked findings and distinguishes measured delays from inferred causes or missing information. Comparing similar tasks matters: one faster run does not establish a trend.

## What evidence it uses

| Source | What it contributes |
| --- | --- |
| `~/.claude/implement/<project>-<task>/` | Run status, worker attempts, check evidence, review outcomes, and recovery state from implement |
| `.specstory/history/` in the product worktree | Optional conversation history: changed requests, handoffs, and waits |
| Relevant source and Git state | The instructions, tools, and revisions behind the reported behavior |

Neither implement nor SpecStory is required; equivalent execution records work too. Keep real reports and transcripts local. See the [SpecStory and evidence guide](../skills/improve-workflow/references/specstory.md) for capture commands, timing limits, and the feedback diagram.

## Apply an improvement

Name the maintained source and the changes you want made:

```text
/improve-workflow Apply the duplicate-check improvements from this review in
~/mathaix-skills. Update the instructions and helpers, verify the affected behavior,
and report what must be measured in future runs.
```

The skill can use analyst, coding, or verification agents when useful. It targets the observed problem, preserves required checks and owner decisions, and verifies the changed behavior. A request to review alone leaves files unchanged.

If you also want publication and installation, include that in your request. The [update instructions](installation.md#update) explain replacement and backups. Existing coordinators must reread updated skills; running workers retain their original briefs.

## Return to implementation

Use [implement](implement.md) for the next product change. Later, ask improve-workflow to compare comparable runs against the intended signal—for example, fewer duplicate checks or shorter handoffs with required verification still covered. Passing helper tests alone does not establish that development is faster.

Read the [improve-workflow skill instructions](../skills/improve-workflow/SKILL.md) for the analysis and change workflow, or use its optional [review template](../skills/improve-workflow/assets/review-template.md) for a larger audit.

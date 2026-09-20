# SpecStory and workflow improvement

The companion [improve-workflow skill](https://github.com/mathaix/claramap-builder/tree/main/skills/improve-workflow)
owns analysis of implementation reports and conversation history, bottleneck diagnosis,
and changes to the development workflow. Invoke it when you want to assess or improve
how work runs; implement continues to execute product development tasks.

## The workflow improvement loop

See the [diagram and SpecStory capture guide](https://github.com/mathaix/claramap-builder/blob/main/skills/improve-workflow/references/specstory.md#the-workflow-improvement-loop).
The guide covers installation, local capture, worktrees, timing comparisons, and privacy.

Keep specs in the product repository under `specs/<slug>/` and execution evidence in the run folder. Use SpecStory capture for Claude coordinator sessions and any delegated Codex sessions. Codex CLI is needed when launching those workers.
Historical transcripts do not override current code, owner decisions, or permissions.

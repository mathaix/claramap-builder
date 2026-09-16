# Using the skills

[Collection home](../README.md) · [Installation](installation.md)

Use **implement** to deliver a code change. Use **improve-workflow** to understand how development ran and improve the process. Each works independently; together they form a feedback loop.

| Your task | Start here | Agent instructions |
| --- | --- | --- |
| Build a feature, fix a bug, or finish a PR | [Implement guide](implement.md) | [implement/SKILL.md](../skills/implement/SKILL.md) |
| Find delays, compare runs, or improve orchestration and checks | [Improve-workflow guide](improve-workflow.md) | [improve-workflow/SKILL.md](../skills/improve-workflow/SKILL.md) |
| Install, update, or remove either skill | [Installation](installation.md) | — |
| Capture conversations and interpret execution records | [SpecStory and evidence guide](../skills/improve-workflow/references/specstory.md) | — |

## How they work together

1. **Implement** coordinates coding, verification, QA, and review in your product repository.
2. Its implementation folder records attempts, checks, and outcomes. Optional **SpecStory** history adds conversation context.
3. **Improve-workflow** reads that evidence to explain delays and verification gaps, then recommends changes or applies them when requested.
4. Use the updated skill on later work. Compare similar runs to see whether the change helped without losing verification coverage.

![The feedback loop from implementation to workflow improvement](../skills/improve-workflow/assets/workflow-feedback.png)

This loop is driven by your requests. Completing an implementation does not automatically start an audit or rewrite a skill.

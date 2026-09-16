# Template provenance

Reviewed 2026-09-12:
- https://www.specflow.com/getting-started.html publishes intent, roadmap, task-list,
  and prompt-context examples.
- https://www.specflow.com/reference/index.html says detailed reference templates
  are forthcoming. Do not claim an official downloadable pack was imported.
- https://www.specflow.com/reddit-wisdom/patterns/index.html supports focused tasks
  and context preservation. Its historical model examples are not our defaults.

These are original adaptations of the published structure:

| Published concept | Artifact | Fields preserved |
| --- | --- | --- |
| Intent | spec.md | Vision, Problem Statement, Success Criteria, Constraints, Non-Goals |
| Roadmap | plan.md | Phase, Goal, Deliverables, Dependencies |
| Task list | tasks.md | Phase tasks, title, Human/AI assignment, steps, Output |
| Prompt context | brief.md | Current Status, Intent Summary, Task Details |
| Refinement | status.md | Results against intent, lessons, next action |

Acceptance IDs, behavior/contracts, evidence, exact file scope, check executor,
Git fingerprints, review state, and usage provenance are local extensions, not
requirements attributed to SpecFlow. Preserve existing specs as authoritative sources.

These templates are optional aids, not required stages. Compact runs keep criteria and
evidence in status.md and link existing specifications. Expand only when useful.

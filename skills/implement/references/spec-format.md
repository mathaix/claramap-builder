# Spec format

Claramap Builder's feature-spec templates are based on Kiro's three-file structure:
requirements, design, and tasks, with requirements written in EARS. SpecFlow informs
the surrounding planning and refinement workflow and the context in worker briefs;
it is not the source of the feature-spec layout.
The templates live in `assets/templates/` and produce `specs/<slug>/` in the product
repository.

## Sources and adaptations

- [Kiro feature specs](https://kiro.dev/docs/specs/feature-specs/) inform the
  `requirements.md`, `design.md`, and `tasks.md` layout, requirements expressed in
  EARS, and task references back to requirement IDs. Specs are committed with the
  code, consistent with Kiro's [version-control guidance](https://kiro.dev/docs/specs/best-practices/).
- [EARS](https://alistairmavin.com/ears/) supplies the event-driven
  `WHEN … THE SYSTEM SHALL …` pattern. Alistair Mavin and colleagues first published
  EARS in 2009; the syntax predates Kiro and SpecFlow.
- [SpecFlow](https://github.com/specstoryai/specflow) supplies the five-phase framing:
  intent, roadmap, tasks, execute, refine. Its human/AI task assignments inform
  executor selection; its [prompt-context guidance](https://www.specflow.com/getting-started.html#step-41-prepare-your-ai-assistant)
  informs [brief.md](../assets/templates/brief.md). The companion `improve-workflow`
  skill applies refinement to the development process.
- [SpecStory](https://github.com/specstoryai/getspecstory) publishes SpecFlow and
  provides the conversation-capture CLI used alongside these records.

These are adapted templates, not an imported official template pack. Explicit check
commands and executors, evidence paths, review status, and deferred-finding fields
are Claramap Builder extensions. Kiro, EARS, and SpecFlow do not need installation;
SpecStory CLI is a capture dependency. Existing project specifications remain
authoritative inputs.

## Files

| File | Holds | Not here |
| --- | --- | --- |
| `requirements.md` | R-IDs, WHEN/SHALL statements, one proof per requirement, non-goals | Implementation detail |
| `design.md` | Baseline, inspected code, approach, decisions, open questions, design-review status | Task progress |
| `tasks.md` | Checkbox tasks citing R-IDs with files, check, and executor; deferred findings | Logs and evidence files |

Evidence stays under `~/.claude/implement/<repo>-<slug>/`: worker attempts, review
snapshots and verdicts, `recovery.json`. Use the same `<slug>` in both places.

A small, settled change needs no spec folder; state the criteria in the request and the
commit message. Delegation and `<run-dir>/execution.md` still apply when no spec folder
is needed. Delete a spec folder in the PR that makes it stale.

# Spec format

Claramap Builder uses [SpecFlow](https://www.specflow.com/getting-started.html) to
structure intent, planning, scoped tasks, contextual execution, and refinement.
The bundled templates apply those concepts in `specs/<slug>/`: requirements capture
intent and acceptance criteria, design records the approach and decisions, and tasks
break the work into assignments with observable checks. Worker briefs carry the
relevant intent and task context into execution.

These are Claramap Builder's own templates, committed with the code. Their filenames,
requirement IDs, EARS statements, and review/evidence fields are local conventions;
SpecFlow does not prescribe this exact file layout. No separate SpecFlow runtime
package is required.

| File | Holds | Not here |
| --- | --- | --- |
| `requirements.md` | R-IDs, WHEN/SHALL statements, one proof per requirement, non-goals | Implementation detail |
| `design.md` | Baseline, inspected code, approach, decisions, open questions, design-review status | Task progress |
| `tasks.md` | Checkbox tasks citing R-IDs with files, check, and executor; deferred findings | Logs and evidence files |

Evidence stays under `~/.claude/implement/<repo>-<slug>/`: worker attempts, review
snapshots and verdicts, `recovery.json`. Use the same `<slug>` in both places.

A small, settled change needs no spec folder; state the criteria in the request and the
commit message. Delete a spec folder in the PR that makes it stale.

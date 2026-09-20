# Spec format

`specs/<slug>/` follows the structure of [Kiro feature specs](https://kiro.dev/docs/specs/feature-specs/)
(checked 2026-09-20): requirements in EARS notation, a design document, and a task list
that cites requirement IDs, all committed with the code. The templates are original
adaptations; nothing is copied from Kiro.

| File | Holds | Not here |
| --- | --- | --- |
| `requirements.md` | R-IDs, WHEN/SHALL statements, one proof per requirement, non-goals | Implementation detail |
| `design.md` | Baseline, inspected code, approach, decisions, open questions, design-review status | Task progress |
| `tasks.md` | Checkbox tasks citing R-IDs with files, check, and executor; deferred findings | Logs and evidence files |

Evidence stays under `~/.claude/implement/<repo>-<slug>/`: worker attempts, review
snapshots and verdicts, `recovery.json`. Use the same `<slug>` in both places.

A small, settled change needs no spec folder; state the criteria in the request and the
commit message. Delete a spec folder in the PR that makes it stale.

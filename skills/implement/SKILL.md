---
name: implement
description: Complete a feature, fix, or existing PR with coordinator-selected coding, verification, QA, and independent review. Use for /implement and requests to plan or carry out implementation work.
---

# Implement

The coordinator owns the outcome and chooses the route: implement directly or delegate,
group and order tasks, select tests, reuse evidence, and decide when intermediate review
adds value. Optimize for a correct, reviewable result with minimal elapsed time. Routine
implementation choices do not require owner approval.

Preserve the owner's acceptance criteria, explicit decisions, model pins, budgets, data
boundaries, and permissions. Required repository/CI checks and independent final review
remain mandatory. Do not mark skipped or failed checks as passes. Escalate consequential
product/architecture choices outside accepted scope, missing authorization, or serious
unresolved risks; keep independent work moving.

## Establish the outcome

Recover the target, existing run, Git state, and relevant repository rules before asking
questions. Read current code and evidence; transcripts are history, not new authorization.
Use an isolated checkout for unrelated edits or concurrent writers. Verify critical
premises (callers, schemas, roles, dependencies) before handing work off.

Keep personal run records at `~/.claude/implement/<repo>-<slug>/`, outside the product repo.
Start with `scripts/scaffold.py <run-dir> --compact --title "<outcome>"`: one status file
with acceptance criteria, decisions, evidence, and next action. Link an existing spec
instead of copying it. Add spec/plan/tasks documents only when they clarify significant
scope or dependencies; scaffold without `--compact` retains the expanded templates.
Never overwrite existing runs, decisions, evidence, or review verdicts.

The coordinator decides whether separate design review is needed. Use it for unresolved
consequential design questions, competing contracts, or an owner/repository requirement.
A migration, auth fix, or concurrency change warrants stronger evidence, but does not
by itself require another planning ceremony when the design is settled. Record the
choice and short reason with `scripts/run_state.py --plan-review required|not-required
--reason "..."` (see [execution.md](references/execution.md)). Routine changes to commands,
paths, test selection, task order, or implementation detail do not need plan approval.
Revisit affected design when evidence changes a material premise.

Existing runs may adopt this owner-authorized workflow explicitly, preserving open
findings and evidence. Changing workflow never resolves a finding or overrides a
separate owner-mandated design approval. `plan_ready` records actual matching approval;
`execution_ready` reflects the separate coordinator decision about needing that gate.

## Choose the people and checks

Use the tools in [delegation.md](references/delegation.md) when delegation saves elapsed
time or supplies independent expertise. Available roles: coding, verification, QA,
diagnosis, and final review. These are options, not required stages. Combine related
changes; a small fix can be done by the coordinator with no coding agent.

Choose permitted models using [model-routing.md](references/model-routing.md). Preserve
the existing owner policy: Codex Luna/Terra/Sol workers, independent Claude Opus final
review, local Sonnet for capability restrictions; Astra excluded. Use native agent tools
when available, or `codex_task.sh` for recorded Codex work. Do not invent unavailable
tools or silently substitute a pinned model.

For each changed behavior, identify what could break and choose the smallest checks
that meaningfully detect it. Include affected callers and shared contracts when relevant.
Database writers need real database evidence under the intended role. End-to-end QA
is appropriate when the journey crosses services/UI or acceptance requires it. Mocked
unit tests prove their modeled behavior, not production integration.

Assign each check one executor. Use [verification.md](references/verification.md) and
`scripts/check_evidence.py` to capture commands, inputs, environment, results, and timing.
Accept valid evidence from another agent. Repeat only for changed relevant inputs,
changed environment, an interrupted/failed check, or a new concrete concern; record
why. Run required full checks on the integrated change, not automatically after each
task. Cheap relevant checks should fail early. Reviewers investigate distinct concerns
instead of replaying evidenced suites.

Parallelize independent coding in isolated worktrees, verification on fixed snapshots,
and environment preparation when resources permit. Serialize shared writers, staging,
and shared database mutations. On confirmed capability denial, preserve partial work
and hand remaining checks to a capable authorized executor; do not emulate system
tools, weaken tests, or keep retrying the same broken environment.

## Integrate and review

The coordinator can fix findings directly, revise briefs, and combine repair batches.
Intermediate reviews are optional. Keep unresolved correctness findings visible;
resolve P0/P1 before completion. The coordinator can fix or defer lower-priority issues
with a concrete rationale and impact, subject to stricter repository rules. Preferences
and speculative scope additions do not block delivery. After repeated failed repairs,
reassess the approach rather than cycling models or review rounds mechanically.

Require one independent review of the integrated change before publishing/landing.
A repository-required final `/code-review` can satisfy this requirement: do not add
another equivalent whole-branch review. Keep separately required CI/remote review gates.
Local checkpoint commits may precede final review unless repository rules prohibit it.
Use `review_gate.py snapshot <worktree> <review-dir> --base <base-commit>` to capture the
complete integrated diff, including committed and staged work. Give the reviewer the
exported copy, criteria, known findings, and existing check evidence. See
[code-review.md](references/code-review.md) and [execution.md](references/execution.md).

Review approval must name the exact final tree. If content changes, request a focused
review of the delta and affected interactions; carry forward the prior full review
rather than restart it. Never reuse an approval for unreviewed content. The deterministic
gate validates content and verdict, not test success. Verify both before publishing.
When a separate design review is selected, use [plan-review.md](references/plan-review.md);
strict plan snapshots remain available for that purpose, not universal dispatch gates.

## Finish and recover

Record acceptance results, remaining risks, and a concrete next action. Refresh
`recovery.json`/`recovery.md` at meaningful transitions using `scripts/run_state.py`;
[recovery.md](references/recovery.md) covers interrupted workers and stale state.
Keep records concise. Use wrapper/check timestamps; distinguish active work, review,
environment failures, and owner/queue waits. Overlapping intervals are not additive.
During long work, send a useful update within 60 seconds; do not dump transcripts.

Continue already-authorized Git/PR actions after refreshing current state. Sending
messages/comments and deploying retain their normal authorization requirements.
Do not add a permission stop for routine choices within the accepted task.

Report delivered behavior, evidence, limitations, and observed usage where available.
`codex_task.sh cost <repo>-<slug>` deduplicates session-cumulative worker counters;
reviewer counters also need per-agent deduplication. Unknown usage stays unknown;
tokens are not billed dollars. No paid model calls are needed to test these helpers.

Validate changes to this skill with `python3 -m unittest discover -s <skill>/tests -v`.
Use the external skill-creator validator when available; it is not a runtime dependency.
Test observable helper behavior, not matching prose.

## Installation and session history

This skill is published in [mathaix/skills](https://github.com/mathaix/skills), under
`skills/implement/`. See the repository's installation and usage documentation. For
optional session capture, recovery context, and timing audits, use
[SpecStory alongside implement](references/specstory.md). Keep real transcripts local.

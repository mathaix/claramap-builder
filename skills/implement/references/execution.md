# Execution and evidence

The coordinator chooses direct work or agents, test depth, intermediate review, and
task order. Product scope and permissions remain fixed. Use the role toolbox in
[delegation.md](delegation.md); assigning QA does not grant live-data permissions.

## Record the planning decision

```sh
python3 <skill>/scripts/run_state.py <run-dir> <worktree> \
  --plan-review not-required --reason "Accepted design; remaining work is implementation and verification" \
  --next-action "Implement the fix and run its regression"
```

Use `required` instead when separate design approval is necessary. `plan_ready` remains
a factual matching-approval signal; `execution_ready` expresses whether the selected
planning gate is satisfied. Neither proves tests or final review. Legacy runs default
to the conservative gate until explicitly reclassified with a reason. Preserve unresolved
findings and any separate owner/repository approval requirement when adapting a run.

Record routine plan adjustments without re-review. Strict `plan-snapshot`/`plan-verify`
remain useful for explicitly reviewed design documents; changed hashes invalidate that
particular approval but do not independently decide whether execution needs to stop.
The coordinator evaluates changed semantics and affected dependencies.

## Workers and permissions

Before writing, inspect HEAD/status and dependencies. Serialize writers in a shared
checkout. Put briefs outside task-NN/: the wrapper atomically creates the task directory.
Record selected model/effort and the reason; resumes preserve their settings unless
explicitly reassessed. Never edit global configuration or discard other agents' work.

The wrapper records prompts, events, session identity, timings, and exit status. A
process exit of zero means execution finished, not that acceptance criteria passed.
Inspect bounded events/stderr for failures rather than dumping full transcripts.
Locks survive coordinator loss through the worker process; do not launch a second
writer while one is held. Preserve unknown/interrupted outcomes.

A check requiring unavailable Docker, sockets, credentials, or process controls belongs
to a capable authorized executor. Fix prerequisites once. Do not fake system tools,
weaken product behavior, or repeatedly retry known denied commands. Use Sonnet fallback
where authorized; it must obey the same permissions. A broken Docker service requires
environment repair, not another model.

## Check once, reuse evidence

Select focused checks by the behavior and risk; consult [verification.md](verification.md).
Run required full checks on the integrated revision. Reuse passing evidence from other
roles when its declared inputs and environment still match. A newly found concern can
justify another check; record that reason. Record unavailable integration checks as
pending, with their executor and prerequisite. Tests in a fake environment do not
prove real database constraints or a deployed journey.

## Independent final review

Intermediate task approval is optional. Checkpoint commits may be unreviewed locally
unless repo rules forbid them. Final review covers the entire integrated change from
the pinned base, including earlier commits; never mistake an empty staged diff for a
review of the branch.

```sh
git add -- path/to/changed path/to/new
python3 <skill>/scripts/review_gate.py snapshot <worktree> <review-dir> --base <base-commit>
python3 <skill>/scripts/review_copy.py <review-dir>/snapshot.json <new-temp-dir>
# Independent reviewer receives source copy, complete diff, criteria and check evidence.
# Save its exact response as <review-dir>/verdict.md.
python3 <skill>/scripts/review_gate.py verify <worktree> <review-dir>
```

The manifest binds approval to content. Any product content change requires review of
that delta and its effects and approval naming the new tree. Reuse the previous full
review; do not mechanically repeat it. Provide known findings/dispositions. A repository's
required final code-review can be this independent review instead of an extra layer.
Keep mandated CI and remote review gates. The snapshot/verify helper checks tree and
verdict identity, not test success or finding disposition; the coordinator verifies those.

Snapshot refuses conflicts/unstaged tracked changes and records untracked files. Stage
new task files explicitly. Records stay outside product worktrees. Reviewers use the
exported copy, not the writer's index; copy-local caches/tests cannot disturb staged
content. `review_copy.py --baseline` exports the named review base. Avoid editable installs
that import from the writer's checkout. External database checks retain their assigned
executor. Revalidate the final reviewed tree after commit hooks/before publishing;
hook edits need delta review. If committing after snapshot, verify before commit and
compare `HEAD^{tree}` to the manifest afterward.

When a selected plan review or required code review returns CHANGES, address concrete
blocking defects. Coordinator repairs are allowed. Optional preferences do not block;
lower-priority findings may be deferred with rationale under repo policy. A workflow
change never turns a serious open finding into approval. Repeated unsuccessful fixes
call for reassessing cause, scope, or evidence, not automatic rounds or silent waiver.

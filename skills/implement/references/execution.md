# Workers and review commands

## Workers and permissions

Before writing, inspect HEAD, status, and dependencies. Serialize writers in a shared
checkout. Put briefs outside `task-NN/`; the wrapper creates the task directory itself.
Record the selected model, effort, and reason in the brief; resumes keep saved settings
unless explicitly overridden. Never edit global configuration or discard another agent's work.

The wrapper records prompts, events, session identity, timings, and exit status. Exit
zero means the process finished, not that the task passed. Inspect bounded events and
stderr rather than dumping transcripts. Locks survive coordinator loss through the worker
process; never launch a second writer while one is held. Preserve interrupted outcomes as unknown.

A check that needs unavailable Docker, sockets, credentials, or process control belongs
to a capable authorized executor. Fix prerequisites once. A broken service needs
environment repair, not another model.

## Independent final review

Intermediate task approval is optional. Checkpoint commits may precede review unless
repository rules forbid them. Final review covers the whole integrated change from the
pinned base, including earlier commits; an empty staged diff is not a branch review.

```sh
git add -- <changed paths> specs/<slug>
python3 <skill>/scripts/review_gate.py snapshot <worktree> <review-dir> --base <base-commit>
python3 <skill>/scripts/review_copy.py <review-dir>/snapshot.json <new-temp-dir>
# Reviewer receives the copy, complete diff, specs, known findings, and check evidence.
# Save its exact response as <review-dir>/verdict.md.
python3 <skill>/scripts/review_gate.py verify <worktree> <review-dir>
```

Snapshot refuses conflicts and unstaged tracked changes and records untracked files, so
stage new files explicitly. Review records stay outside the product worktree. Reviewers
work in the exported copy, never the writer's index; `review_copy.py --baseline` exports
the review base for comparison. Avoid editable installs that import from the writer's
checkout. Revalidate the reviewed tree after commit hooks and before publishing; if you
commit after the snapshot, verify first and compare `HEAD^{tree}` to the manifest after.

On CHANGES, assign the concrete blocking defects to a coder or integration agent.
Coordinator product repairs require the recorded [direct-work exception](chief-of-staff.md#direct-work-exceptions);
review findings do not themselves grant an exception. After two failed repairs, reassess
cause, scope, or evidence instead of another round. A workflow
change never turns an open finding into approval.

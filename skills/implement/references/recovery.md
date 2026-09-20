# Pause and resume

A conversation stop does not mean its worker stopped. Never start a second writer or
discard partial edits to make a resume look clean.

Pause by stopping dispatch and letting work finish, or interrupt via the task handle.
Confirm exit; preserve logs, Git state, and the next action. Do not auto-commit or roll
back. The wrapper forwards termination to its process group; force-killing can lose records.

On resume:
1. Refresh `scripts/run_state.py <run-dir> <worktree> --next-action "..."`. Completed
   commits must remain ancestors of HEAD. It is an observation, not a monitor.
2. Inspect worker locks before dispatch or resume. Missing final metadata means
   interrupted or unknown, not success.
3. Resume remaining work in the same task, keeping partial edits and valid evidence. The
   wrapper recovers session identity from events and rejects conflicting IDs. Without an
   identity, use a new task slug that references the partial work; never overwrite the
   old task. Preserve model pins and owner restrictions.
4. Reread `specs/<slug>/` for open tasks, deferred findings, and the recorded design-review
   status. Rerun interrupted, failed, or invalidated checks, not every check. Complete
   independent final review and required checks before publishing.

Worker discovery uses the wrapper's `workdir` metadata, including nested slugs; old
immediate `task-*` directories are still recognized. `recovery.json` is the observed
state and `recovery.md` its generated view; refresh both at transitions.

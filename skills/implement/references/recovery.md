# Pause and resume

A conversation stop does not mean its worker stopped. Never start a second writer
or discard partial edits to make a resume look clean.

Pause by stopping dispatch, letting work finish when practical or interrupting via
its task handle. Confirm exit; preserve logs, current Git state and next action. Do
not auto-commit or roll back. The wrapper forwards termination to its process group;
force-killing can lose final records.

On resume:
1. Refresh `scripts/run_state.py <run-dir> <worktree> --next-action "..."`. Completed
   commit records must remain ancestors of HEAD. This is an observation, not a live monitor.
2. Inspect worker locks before dispatch/resume. For legacy wrappers inspect processes
   too. Missing final metadata is interrupted/unknown, not success.
3. Resume remaining work in the same task, preserving partial edits and valid evidence.
   The wrapper recovers session identity from events and rejects conflicting IDs. If
   no identity was emitted, use a new task slug referencing the partial work; never
   overwrite the old task. Preserve explicit model pins and owner restrictions.
4. Read recorded planning policy and unresolved findings. `plan_ready` only reports
   matching approval; `execution_ready` also accounts for the coordinator's recorded
   choice that separate plan review is unnecessary. Legacy runs stay conservative
   until explicitly adapted with `--plan-review ... --reason ...`. Reclassification
   cannot waive owner-required approval or resolve a finding. Routine amendments
   need no new plan review; material unresolved design changes may warrant one.
5. Check evidence validity; rerun interrupted, failed, or invalidated checks, not
   every previous check. Complete independent final review and required checks before
   publishing. Local checkpoint commits may precede review unless repo rules forbid it.

`status.md` records acceptance, decisions and evidence. `recovery.json` is the observed
current state; `recovery.md` is its generated view. Refresh at transitions. Existing
spec/plan/task documents remain preserved; new compact runs can keep criteria in status.md.

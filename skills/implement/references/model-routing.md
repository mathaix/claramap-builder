# Worker model selection

Choose per task, not once per feature. Optimize the expected total cost of an accepted
task, including judgment and repair, within the required quality and owner budget.
[model-policy.json](../model-policy.json) holds the worker allowlist, default model and
effort, independent reviewer, and local capability fallback. The wrapper enforces the
allowlist; Claude selects the reviewer and fallback through its native interface.

Dispatch interface and model permission are separate. An ordinary planner, coder,
test-runner, or integrator uses an allowlisted worker model, whether dispatched through
the wrapper or a native interface capable of selecting that model. Native Claude
availability does not expand the worker allowlist: Claude Opus is the configured reviewer
and Claude Sonnet the local-capability fallback. Use those routes under their stated
conditions; do not silently replace a Codex worker with an arbitrary native model.

Only an explicit owner-authorized policy change may alter those settings: edit the file in
the maintained source, test, reinstall. Environment overrides select within the allowlist
and cannot expand it. A genuine user pin takes precedence within the permitted set; a pin
outside it needs a policy change. Never edit global model configuration.

| Task evidence | Starting choice | Effort |
| --- | --- | --- |
| Mechanical, clear acceptance, established example, narrow scope | Luna | low or medium |
| Ordinary feature or integration with understood interfaces across several files | Terra | medium |
| Ambiguous behavior, subtle state, concurrency, or authorization invariants, hard diagnosis | Sol | medium or high |

Complexity is uncertainty and interaction, not file count: a one-line authorization
change may need Sol, a rename across many files may suit Luna. Pick a stronger worker
up front when a costly failure is foreseeable. Use only combinations available in the
installed client; do not make paid probe calls to rank models. If the selected model is
unavailable, record it and choose another permitted model explicitly. Never silently fall back.

## Explain the choice before dispatch

Before every new assignment or model change, give the user a concise routing explanation
and save it in the brief and `<run-dir>/execution.md`. Several assignments may share one
short update, but each needs its own rationale. State:

- Task and role; exact model, effort (or not configurable), and native/wrapper route.
- The task facts that justify that model: uncertainty, interactions, required capability,
  and why the default/lightest suitable allowed worker is adequate or insufficient.
- The policy entry authorizing the choice: worker allowlist, independent reviewer, or
  capability fallback, with any explicit owner pin.
- If Codex is bypassed, why: the configured independent-review role, or the specific
  capability failure/limitation and evidence supporting the permitted fallback. Availability
  of a native agent and labels such as "judgment tier" are not sufficient reasons.
- The condition that would trigger reassessment or a different permitted selection.

Example for an ordinary worker: "T2 database verification: Codex Terra, medium, through
codex_task.sh. The task spans migrations and application writes, so it needs integration
judgment beyond a mechanical Luna task. Terra is allowlisted. A confirmed local-capability
restriction triggers the configured Sonnet fallback with the error recorded."

Example for review: "T4 final review: Claude Opus through the native interface, effort
not configurable here. The policy names Opus as independent reviewer; this is why this
assignment does not use Codex. It receives the integrated snapshot and existing checks."

If the choice has no valid policy basis, select a permitted route before dispatch.
An explanation does not authorize a model outside policy. Do not manufacture a failure
or make paid probe calls to justify a preferred model. Missing rationale from an older
run remains "not recorded"; do not invent it retrospectively.

Resume preserves the recorded settings unless explicitly changed via `IMPLEMENT_MODEL`
and `IMPLEMENT_EFFORT`; unchanged resumes reference the existing decision. Explain and
record any change before resuming. At completion, summarize models used and material
routing changes, linking the ledger. This is an instruction/audit requirement; native
dispatch is not mechanically guarded by the wrapper.

After two failed repair attempts, reassess before another dispatch:
- Codex local-capability denial: hand remaining local work to the configured fallback.
- Broken service or missing dependency: fix the prerequisite; a model change is not a fix.
- Contradictory brief or false premise: correct it; reopen design if consequential.
- Repeated reasoning failure: narrow the task, raise effort, or move to Terra or Sol.
Already on the strongest worker: reassess scope, evidence, and approach. Do not cycle models.

## Local capability fallback

On the first confirmed sandbox restriction that blocks required local execution (process
inspection, signalling, local integration checks), report it once and hand the remaining
task to the configured fallback agent if it has that capability. Do not retry the denied
command, build fake tools, or change product code to suit the restriction. Confirm the
Codex writer exited before handing over its worktree; pass partial changes, accepted
decisions, and still-valid results. Record the reason and the actual agent ID. The
fallback follows the same permissions and scope; independent final review still applies.

Model descriptions checked 2026-09-13 against installed Codex metadata and
[official guidance](https://learn.chatgpt.com/docs/models). The table is local policy,
not a provider guarantee. Token counts are not a dollar saving.

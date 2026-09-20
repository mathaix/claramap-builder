# Worker model selection

Choose per task, not once per feature. Optimize the expected total cost of an accepted
task, including judgment and repair, within the required quality and owner budget.
[model-policy.json](../model-policy.json) holds the worker allowlist, default model and
effort, independent reviewer, and local capability fallback. The wrapper enforces the
allowlist; Claude selects the reviewer and fallback through its native interface.

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

Record in each brief: complexity and risk in one sentence, the exact model and effort
with a short reason, and the reassessment trigger. Resume keeps the recorded settings
unless the coordinator overrides them via `IMPLEMENT_MODEL` and `IMPLEMENT_EFFORT`.

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

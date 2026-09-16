# Worker model selection

The coordinator chooses per task, not once for the entire feature. Optimize expected
total cost of an accepted task, including judgment and repair, subject to the required
quality and owner budget. For delegated work, OpenAI workers can code, verify, diagnose, or run QA; Claude Opus
performs independent final review; the owner authorizes local Sonnet for the capability fallback below. It is not proof of correctness or guaranteed savings.

Default Codex workers: `gpt-5.6-luna`, `gpt-5.6-terra`, `gpt-5.6-sol`.
Local-capability fallback: Claude Sonnet through the native local agent interface.
Astra is excluded by explicit owner instruction, including retries and recovery.
Do not alter global model configuration. A recorded old default is not a user pin;
a genuine explicit user model pin takes precedence over automatic routing within the
permitted set. A pin outside the permitted set needs an explicit owner policy change.

Starting guidance, adapted to the task and observed results:

| Task evidence | Starting choice | Effort |
| --- | --- | --- |
| Mechanical, clear acceptance, established example, narrow scope | Luna | low or medium |
| Ordinary feature or integration with understood interfaces and several interacting files | Terra | medium |
| Ambiguous behavior, subtle state/concurrency/authorization invariants, difficult diagnosis or broad semantic change | Sol | medium or high |

Complexity depends on uncertainty and interactions, not file count. A tiny change to
an authorization condition may need Sol; a rename across many files may suit Luna.
Choose a stronger worker initially when a costly failure is reasonably foreseeable.
Use only model/effort combinations available in the installed client/account. Do not
make paid probe calls simply to rank models. If the selected model is unavailable,
record the failure and explicitly choose another permitted model when owner pins and
budget allow; otherwise report the unavailable requirement. Never silently fall back.

Record in each dispatch/fix brief:
- Complexity and relevant uncertainty/risk, in one sentence.
- Exact model and reasoning effort, with a short reason.
- Reassessment trigger and, for a change, previous model and finding that prompted it.
The saved prompt plus attempt metadata preserve the choice; do not put mutable model
assignments in hashed product requirements. Resume keeps the recorded model/effort
unless the coordinator explicitly changes both via IMPLEMENT_MODEL/IMPLEMENT_EFFORT.
Before switching, confirm the previous worker stopped and keep partial edits/history.

After a substantive code repair fails again (two unsuccessful repair attempts),
reassess before another dispatch. Earlier reassessment is appropriate when a finding
reveals greater complexity than expected. Distinguish causes:
- Codex local-capability denial: hand remaining local work to Sonnet as described below.
- Broken service or missing dependency: coordinator resolves the prerequisite; changing
  models alone is not a fix.
- Contradictory brief or false schema premise: correct it; review any consequential unresolved design.
- Repeated implementation/reasoning failures: narrow the task, increase effort, or
  select Terra/Sol if that is likely to reduce further repair and review work.
Already on Sol: reassess scope, evidence, and approach; do not select Astra. Do not
cycle models indefinitely; reassess the cause and remaining risk. Preserve
user pins; explain when a different model would require changing an explicit pin.

Do not claim a dollar saving from token counts alone. Use observed attempts, usage,
duration, and findings to evaluate the choice; pricing requires current verified rates
and the actual billing mode. This routing change does not add a pricing collector.

Model descriptions and effort guidance checked 2026-09-13 against the installed
Codex model metadata and [official model guidance](https://learn.chatgpt.com/docs/models).
The routing table is local workflow policy, not a provider guarantee.

## Owner-authorized local Sonnet fallback

On the first confirmed restriction preventing required local execution in Codex,
report the failed capability once and use a local Sonnet agent that has it. This
includes process inspection/signalling and local integration checks blocked by the
worker sandbox. Do not retry the same denied command, construct fake system tools,
or alter product code solely to accommodate the worker's restrictions.

Confirm the Codex writer exited before handing over its existing worktree. Give Sonnet
the remaining task, partial changes, accepted decisions and still-valid check results;
continue from there without restarting completed work. Record the reason and actual
model/agent ID. Sonnet must follow normal permissions and existing scope; Git writes
and external actions retain their coordinator/user authorization rules. Keep independent final
Opus review, even though implementation now also uses Claude. If Sonnet lacks the
capability too, report the concrete prerequisite rather than cycling models.

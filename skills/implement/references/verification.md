# Select and record checks

Choose checks from plausible failures and the proof named on each requirement. This is
guidance, not a checklist to complete in full:

| Change | Useful proof |
| --- | --- |
| Documentation or mechanical rename | Affected references; syntax or build checks where relevant |
| Behavior fix | A regression that fails for the bug and passes when fixed; affected callers |
| Shared API, schema, or permission path | Contract and integration checks under the intended role |
| Concurrency, leases, or retries | Reproduction of the competing operations and the settlement invariant |
| User journey | Authorized end-to-end QA with real reads, writes, and rendered behavior |

Repository-required checks still apply. Broaden scope for shared dependencies or
unresolved uncertainty. Tests that mirror the implementation or re-prove unchanged
behavior add little. Assign each check to one executor by access and independence; do
not run each check once per role.

Record each check next to its task in `tasks.md` or in `recovery.json`: the command,
working directory, exit status, and log path. A passing check is reusable while the code,
dependencies, and environment it exercised are unchanged; rerun after any of those change,
after a failure or interruption, or for a new concrete concern, and say why. A green unit
test does not prove UI behavior or real database constraints; an old deployment check is
not current because the source matches. Keep QA artifacts such as screenshots with the
commands that produced them. Missing proof stays pending, never assumed.

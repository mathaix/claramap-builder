# Select and reuse checks

The coordinator chooses checks from plausible failures and acceptance criteria. Treat
this as guidance, not a checklist requiring every category:

| Change | Useful proof |
| --- | --- |
| Documentation or mechanical rename | Affected references, syntax/build checks where relevant |
| Behavior fix | Regression that fails for the bug and passes for the intended behavior; affected callers |
| Shared API/schema/permission path | Contract and integration checks under the intended role |
| Concurrency, leases or retry handling | Reproduction of the competing operations and settlement invariant |
| User journey | Authorized end-to-end QA with actual reads/writes and rendered behavior when relevant |

Repository-required checks still apply. Broaden scope for shared dependencies, failures,
or unresolved uncertainty. Tests that mirror an implementation or re-prove unchanged
behavior add little. Assign checks to coding, verification, QA, or the coordinator based
on access and independent work; do not run each check once per role.

## Evidence helper

```sh
python3 <skill>/scripts/check_evidence.py run \
  --store <run-dir>/checks --cwd <worktree> \
  --input agents --input tests --input pyproject.toml --input uv.lock \
  --environment local-python312-db-schema0190 --executor verification-agent \
  --timeout 600 -- python3 -m pytest tests/test_affected_behavior.py -q
```

Choose actual relevant inputs, including test/config/dependency files; the example's
paths and environment label are not defaults. Commands are argv after `--`, not shell
strings. Do not put credentials in the command, label, or output. Store records outside
the input directories. Existing commands/logs can remain evidence; the helper is useful
for checks where machine-verifiable reuse prevents repeated work.

Use the same invocation with `status` instead of `run` to check reuse. Executor identity
can change without invalidating a result. `status` exits zero only for a successful
matching result with its log content intact. `run` refuses to repeat an unchanged passing
check unless given `--reason "<new concern or requirement>"`. Failed/interrupted runs,
changed inputs or a different environment label require fresh evidence. Each attempt
keeps its own log/metadata with timing, exit status, before/after fingerprints and reason.
The timeout bounds a stuck command; timeout is a failed check, never a substitute pass.
SIGINT/SIGTERM cancellation stops the runner's own process group and records interruption.

## Limits and interpretation

Fingerprints cover declared files/directories (including new/deleted entries and
executable bits), not omitted dependencies or external services. Inspect input coverage
before trusting reuse. Standard Git/Python check-cache directories are ignored, and
symlink inputs must be replaced with explicitly declared real targets. An immutable
source copy prevents a change-and-revert during testing from escaping before/after
comparison. Environment labels are assertions by the executor, not automated DB or
runtime probes. Record actual runtime/role/schema evidence when relevant; change the
label or run a fresh check after a restart, migration, dependency/config change or
live-data change. Never treat an old deployment/DB check as current solely because
source fingerprints match.

Acceptance proof remains the coordinator's judgment: an exit code only describes the
command, and a green unit test cannot prove UI behavior or real database constraints.
Record pending checks precisely and preserve separate QA artifacts, such as screenshots
and redacted transcripts, alongside the commands that produced them.

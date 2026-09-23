# Example: trim a saved title

A synthetic walkthrough, not a real execution report. A real run obtains its own
evidence and independent verdict.

## Request

```text
/implement Trim leading and trailing whitespace from saved titles. Preserve internal
spaces and keep the existing behavior for an empty title. Verify the change locally.
```

The project has `titles.py` with `normalize_title(value)` and `tests/test_titles.py`.
The chief reads the request and repository instructions, records the base revision, and
assigns one coder to inspect the caller, preserve empty-title behavior, implement the fix,
and run focused checks. A separate planner and test-runner would add little here; an
independent reviewer still follows. A spec folder is optional for this small settled task;
the coder creates one here to illustrate the records. The execution ledger is required
either way. No direct-work exception is needed.

## Dispatch and spec

The chief sets the run location and base revision, writes a short brief outside the
product repository, and records the dispatch in `<run-dir>/execution.md`. Select the
coder using the [model policy](../model-policy.json); native or Codex workers are valid.
The brief assigns `titles.py`, its focused test file, and `specs/trim-title/` to one writer,
asks for baseline and changed-state evidence, and specifies a compact report with trace
paths. Record the actual agent/session ID returned by the interface.

The assigned coder runs the scaffold helper in its worktree:

```sh
skill_dir="$HOME/.claude/skills/implement"
run_dir="$HOME/.claude/implement/example-trim-title"
base_commit=$(git rev-parse HEAD)
python3 "$skill_dir/scripts/scaffold.py" "$PWD" trim-title --title "Trim saved titles"
```

The coder inspects the caller, confirms empty titles are valid, and fills `specs/trim-title/`:

```markdown
# requirements.md
## R1: Surrounding whitespace
WHEN a title is saved THE SYSTEM SHALL store it without leading or trailing whitespace
Proof: tests/test_titles.py::test_strips_surrounding_whitespace fails on baseline, passes after
## R2: Internal spaces and empty titles
WHEN a title contains internal spaces or is empty THE SYSTEM SHALL store it unchanged
Proof: tests/test_titles.py::test_preserves_internal_and_empty

# design.md
Baseline: main @ <base_commit>. Inspected: titles.py, its save caller, tests/test_titles.py.
Approach: normalize_title returns value.strip() (R1); strip preserves internal spaces and "" (R2).
Design review: not required; known behavior, no owner gate.

# tasks.md
- [ ] T1 Add regression cases (R1, R2) — files: tests/test_titles.py; check: python3 -m unittest tests.test_titles; executor: assigned coder (actual ID in run ledger)
- [ ] T2 Strip in normalize_title (R1) — files: titles.py; check: same; executor: assigned coder (actual ID in run ledger)
```

## Work and checks

The coder confirms the R1 regression fails on the baseline, implements the fix, and runs:

```sh
mkdir -p "$run_dir/checks"
python3 -m unittest tests.test_titles -v 2>&1 | tee "$run_dir/checks/test_titles.log"
```

All cases pass. The coder ticks T1 and T2 in `tasks.md` with the command and log path,
then returns the resulting revision/tree, changed paths, check outcomes, and evidence
locations. Its report stays compact; available event logs/transcripts remain on disk.

The chief checks that the report covers the original acceptance criteria and records
acceptance in `execution.md`, with input/result revision, actual agent/session IDs, check
log, trace pointers, and any capture gaps. A shared checkout has one serialized writer;
if the work needs integration, assign it to an integration agent and recheck the combined
result. The chief does not resolve product conflicts directly.

## Review

```sh
git add -- titles.py tests/test_titles.py specs/trim-title
python3 "$skill_dir/scripts/review_gate.py" snapshot "$PWD" "$run_dir/review-final" --base "$base_commit"
python3 "$skill_dir/scripts/review_copy.py" "$run_dir/review-final/snapshot.json" "$run_dir/review-source"
```

The chief runs these operational review helpers after the writer has finished. The
configured independent reviewer receives the copy, the diff, the specs, and the log.
Record its actual agent/session ID and trace pointers in the ledger too. An
illustrative verdict:

```text
VERDICT: APPROVE
TREE: <actual tree hash from the snapshot>
CHECKS: Accepted the regression run in checks/test_titles.log; none pending.
FINDINGS:
- None.
```

The chief saves the reviewer's real reply as `review-final/verdict.md`, never one it wrote, then:

```sh
python3 "$skill_dir/scripts/review_gate.py" verify "$PWD" "$run_dir/review-final"
python3 "$skill_dir/scripts/run_state.py" "$run_dir" "$PWD" --next-action "Complete; report the result"
```

The gate prints `APPROVED_UNCHANGED <tree>`. If code changes after that, take a new
snapshot and get explicit approval of the delta. Delegate any review repairs back to
a coder; a review finding is not permission for direct chief implementation. Record
the verified tree and review result in the ledger, then run `usage.py --run "$run_dir"`
and include its actual table in the final response.

## Final response

> Saved titles now trim surrounding whitespace while preserving internal spaces and
> empty titles. Both regression cases pass and independent review approved the final
> tree. Implementation and tests were delegated to the coder; a separate reviewer
> approved the result. No direct-work exceptions. Evidence: `<run-dir>/execution.md`.
> The change and its spec are committed locally; deployment was outside this request.
>
> [Include the actual usage table here.]

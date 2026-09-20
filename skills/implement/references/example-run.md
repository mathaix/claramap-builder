# Example: trim a saved title

A synthetic walkthrough, not a real execution report. A real run obtains its own
evidence and independent verdict.

## Request

```text
/implement Trim leading and trailing whitespace from saved titles. Preserve internal
spaces and keep the existing behavior for an empty title. Verify the change locally.
```

The project has `titles.py` with `normalize_title(value)` and `tests/test_titles.py`.
Claude inspects the save caller and confirms empty titles are already valid. This is
small and settled, so Claude implements directly with no worker and no design review.
Independent final review still applies. Because the change is trivial, Claude could
skip the spec folder; it creates one here to show the records.

## Spec

```sh
skill_dir="$HOME/.claude/skills/implement"
run_dir="$HOME/.claude/implement/example-trim-title"
base_commit=$(git rev-parse HEAD)
python3 "$skill_dir/scripts/scaffold.py" "$PWD" trim-title --title "Trim saved titles"
```

Claude fills `specs/trim-title/`:

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
- [ ] T1 Add regression cases (R1, R2) — files: tests/test_titles.py; check: python3 -m unittest tests.test_titles; executor: coordinator
- [ ] T2 Strip in normalize_title (R1) — files: titles.py; check: same; executor: coordinator
```

## Work and checks

Claude confirms the R1 regression fails on the baseline, implements the fix, and runs:

```sh
mkdir -p "$run_dir/checks"
python3 -m unittest tests.test_titles -v 2>&1 | tee "$run_dir/checks/test_titles.log"
```

All cases pass. Claude ticks T1 and T2 in `tasks.md` with the command and log path.

## Review

```sh
git add -- titles.py tests/test_titles.py specs/trim-title
python3 "$skill_dir/scripts/review_gate.py" snapshot "$PWD" "$run_dir/review-final" --base "$base_commit"
python3 "$skill_dir/scripts/review_copy.py" "$run_dir/review-final/snapshot.json" "$run_dir/review-source"
```

The configured reviewer receives the copy, the diff, the specs, and the log. An
illustrative verdict:

```text
VERDICT: APPROVE
TREE: <actual tree hash from the snapshot>
CHECKS: Accepted the regression run in checks/test_titles.log; none pending.
FINDINGS:
- None.
```

Claude saves the reviewer's real reply as `review-final/verdict.md`, never one it wrote, then:

```sh
python3 "$skill_dir/scripts/review_gate.py" verify "$PWD" "$run_dir/review-final"
python3 "$skill_dir/scripts/run_state.py" "$run_dir" "$PWD" --next-action "Complete; report the result"
```

The gate prints `APPROVED_UNCHANGED <tree>`. If code changes after that, take a new
snapshot and get explicit approval of the delta.

## Final response

> Saved titles now trim surrounding whitespace while preserving internal spaces and
> empty titles. Both regression cases pass and independent review approved the final
> tree. The change and its spec are committed locally; deployment was outside this request.

# Optional design review

Use only when selected: the owner or repository requires it, or a consequential design
question is still open. Routine amendments to commands, paths, or test selection never
need it. The reviewer is read-only: no edits, staging, fetching, or environment changes.

Inputs: repository path, `specs/<slug>/`, the commit SHA those specs are at, applicable
repository rules, and the base SHA.

Check:
1. Every requirement has a task and an observable proof; settled decisions are preserved.
2. Premises match the code: base and conflicts, callers, schemas, runtime dependencies.
3. Tasks are coherent, dependency-ordered, and independently checkable.
4. Each check distinguishes success from failure and runs under its executor's permissions.
5. Scope and actions comply with repository and user constraints.

CHANGES is for concrete blocking defects. Preferences go in SUGGESTIONS. Add no scope.

```text
VERDICT: APPROVE | CHANGES
COMMIT: <sha of the reviewed specs>
FINDINGS:
- <ID> [severity] <file:line or task> — defect, evidence, smallest required fix
SUGGESTIONS:
- <optional, or none>
```

Save the reply as `<run-dir>/review-design/verdict.md` and record the commit and verdict
path under "Design review" in `design.md`. Check drift against the working tree, not HEAD,
so staged and unstaged edits and new files count:

```sh
git diff <sha> -- specs/<slug>/
git ls-files --others --exclude-standard -- specs/<slug>/
```

Empty output from both means the approved specs are unchanged. A later spec change needs a
fresh verdict only when its semantics changed; the coordinator judges that and records the reason.

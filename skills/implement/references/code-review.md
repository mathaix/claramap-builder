# Independent review

Review the integrated change against `specs/<slug>/requirements.md`, independently of
its implementer. Do not edit product source, stage, commit, or touch external environments.

Inputs: exported review copy, the specs, repository rules, `snapshot.json`, the full diff
from its pinned base, existing check evidence, and prior findings. Verify source
provenance and inspect affected callers beyond the diff; for merges, inspect both parents.
A new concern warrants targeted investigation, not a new workflow tier.

Assess correctness, authorization and data boundaries, scope, and whether the checks
meaningfully cover likely failures in the intended environment and role. Accept valid
evidence from other executors; run targeted checks only in the disposable copy. Missing
integration evidence stays pending; fake-client tests do not establish real schema or
role behavior.

Findings need a concrete trigger, impact, location, and smallest required fix. Separate
defects from preferences. P0/P1 block approval; lower findings may be fixed or deferred by
the coordinator with recorded rationale. Do not force speculative scope.

For a revision, inspect the changed content, prior findings, and affected interactions;
carry prior coverage forward, but a new tree needs an explicit verdict. Never relabel
self-review as independent.

```text
VERDICT: APPROVE | CHANGES
TREE: <snapshot tree SHA>
CHECKS: <accepted evidence; distinct checks run; pending checks>
FINDINGS:
- <ID> [severity] <path:line> — trigger, impact, required fix, or documented disposition
SUGGESTIONS:
- <optional, or none>
```

Save the exact response as `verdict.md` beside `snapshot.json`. Approval covers this
tree only and does not assert pending checks passed.

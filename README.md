![Claude coordinates scoped workers, validates their results, and integrates the change](skills/implement/assets/claramap-builder-hero.png)

# Claramap Builder

**Agent Skills to Orchestrate Code Development.**

**Claramap Builder is an open-source AgentSkill for orchestrating code development.**
Install it in your coding harness and invoke `/implement` with a goal. It breaks the
goal into manageable tasks, gives each worker the context it needs, and selects
models based on task complexity. It validates what comes back, integrates the
changes, and iterates until the requested behavior is implemented and the required
checks pass.

The skill bundles instructions, references, spec templates, and executable helpers.
The current implementation uses **Claude Code, Codex, SpecStory, and SpecFlow**.
The AgentSkill format can be adapted to other coding harnesses; the shipped setup
uses Claude Code as its host. See [harness support](docs/dependencies.md#agent-skill-packaging-and-harness-support).

[Install the skill](docs/usage.md) · [How it works](docs/implement.md) · [Dependencies in detail](docs/dependencies.md)

## Dependencies and how they work together

| Component | What it does in Claramap Builder |
| --- | --- |
| **Claude Code — orchestration and review** | Hosts the skill, holds the goal and project context, scopes tasks, selects workers, validates their results, integrates changes, and coordinates repairs. A separate Claude agent performs independent final review. |
| **Codex — scoped workers** | Executes delegated coding, diagnosis, verification, and QA tasks. Each worker receives a contextual brief and a model selected for task complexity. Claude can handle small changes directly. |
| **SpecStory — session capture** | Captures coordinator and worker conversations so decisions, handoffs, and interruptions can be inspected. This history supports recovery and `/improve-workflow` analysis alongside execution records. |
| **SpecFlow — specifications and task planning** | Structures the work around intent, a plan, scoped tasks, contextual execution, and refinement. The bundled spec templates and worker briefs carry that structure into the build. |

Install and authenticate Claude Code and Codex CLI, and install SpecStory CLI for
session capture. SpecFlow's planning structure is incorporated in the skill's
[templates and instructions](skills/implement/references/spec-format.md); it does
not require a separate runtime package. Python 3.11+, Git, and a POSIX environment
run the helpers. See the [detailed dependency guide](docs/dependencies.md) for setup
responsibilities, capture records, and adapting the skill to another harness.

## From goal to built code

1. **Break down the goal.** Inspect the codebase, establish requirements, and identify scoped tasks.
2. **Delegate with context.** Match workers to task complexity and give them relevant code, constraints, and acceptance criteria.
3. **Validate and integrate.** Check returned work against the requirements, combine changes, and obtain independent review.
4. **Iterate to completion.** Address failed checks and review findings, preserving progress across interruptions.

Give it a concrete goal in your project:

```text
/implement Add a display-name setting. Save it using the existing profile API,
preserve account permissions, and verify that it survives a page reload.
```

You get code changes, recorded check results, independent review findings, and saved
progress for resuming the work. Larger changes also include requirements, design,
and tasks committed alongside the code. Missing access or unresolved requirements
are reported as blockers; unfinished work stays visible.

See the [illustrative walkthrough](skills/implement/references/example-run.md) for the
records and review process. It is a synthetic example, not a measured execution report.

## Get started

Use Claude Code with Python 3.11+, Git, SpecStory capture, and access to the configured
independent reviewer. Codex CLI is needed when delegating to Codex workers. Helpers
support macOS/Linux and Windows through WSL. See [setup and model access](docs/installation.md#requirements).

```sh
git clone https://github.com/mathaix/claramap-builder.git ~/claramap-builder
cd ~/claramap-builder
python3 scripts/install.py implement
```

Then start Claude in your product repository:

```sh
cd /path/to/your/project
specstory run claude --no-cloud-sync
```

Enter `/implement` followed by your goal. The [first-build guide](docs/usage.md) covers
worker capture, what to expect, and how to resume. The installer copies the skill into
`~/.claude/skills/implement`; it preserves existing installations unless you request replacement.

Claramap Builder is [MIT licensed](LICENSE). Model usage runs through your existing
accounts and is subject to their billing. Check the [model policy](docs/installation.md#model-policy)
before dispatching workers.

## Improve how the next build runs

The companion `/improve-workflow` skill examines completed runs to find repeated work,
slow handoffs, and verification gaps. Ask why a small fix took an hour, where checks
were duplicated, or what should change before the next build.

Install it from this repository:

```sh
python3 scripts/install.py improve-workflow
```

Then ask in your project:

```text
/improve-workflow Review the last three runs. Find repeated work and bottlenecks,
and recommend improvements without editing yet.
```

It connects findings to recorded evidence and can apply targeted improvements when
requested. Compare later runs to see whether those changes helped. See the
[workflow improvement guide](docs/improve-workflow.md).

## Documentation

| Guide | Purpose |
| --- | --- |
| [Your first build](docs/usage.md) | Install, give a goal, inspect the result, and resume |
| [How orchestration works](docs/implement.md) | Task scoping, worker selection, validation, and completion |
| [Dependencies and architecture](docs/dependencies.md) | Claude, Codex, SpecStory, SpecFlow, capture records, and harness support |
| [Installation and configuration](docs/installation.md) | Prerequisites, model policy, project setup, updates, and removal |
| [Improve the next build](docs/improve-workflow.md) | Investigate runs and apply evidence-based improvements |
| [Illustrative walkthrough](skills/implement/references/example-run.md) | Follow a request through specs, checks, and review |
| [Contributing](CONTRIBUTING.md) | Repository structure, tests, and contribution guidance |

The installed agent instructions live in [implement](skills/implement/SKILL.md) and
[improve-workflow](skills/improve-workflow/SKILL.md). The bundled templates apply
[SpecFlow planning concepts](skills/implement/references/spec-format.md).

Built by [mathaix](https://github.com/mathaix).

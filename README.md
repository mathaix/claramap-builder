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

These are separate projects used by the skill. **Set up the tools before your first
build; `scripts/install.py` only copies Claramap Builder's skill files.**

| Project | What it is and how we use it | Install beforehand? |
| --- | --- | --- |
| [Claude Code](https://github.com/anthropics/claude-code) | Anthropic's terminal coding agent. Hosts the skill, coordinates tasks and repairs, and runs a separate agent for independent review. | **Yes.** Install and authenticate; ensure access to the configured reviewer. [Setup](https://code.claude.com/docs/en/overview). |
| [Codex CLI](https://github.com/openai/codex) | OpenAI's terminal coding agent. Runs scoped workers with relevant context and a model selected for task complexity. | **Yes for delegated builds.** Install and authenticate before launching workers. Direct Claude tasks do not launch Codex. [Setup](https://github.com/openai/codex#quickstart). |
| [SpecStory CLI](https://github.com/specstoryai/getspecstory) | A tool that saves AI coding conversations as local Markdown. Captures coordinator and worker history for recovery and workflow analysis. | **Yes.** Install its CLI and enable capture before starting the documented workflow. [Setup](https://docs.specstory.com/integrations/terminal-coding-agents). |
| [SpecFlow](https://github.com/specstoryai/specflow) | SpecStory's methodology for building with software agents: intent, roadmap, tasks, execution, and refinement. Structures our specs and worker briefs. | **No.** Its planning approach is incorporated in the bundled templates and instructions. [Method guide](https://www.specflow.com/getting-started.html). |

Python 3.11+, Git, and macOS/Linux or WSL are also required for the helpers.
The [installation guide](docs/installation.md#requirements) gives the setup order and
checks. The [dependency guide](docs/dependencies.md) explains capture records and
how the components connect.

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

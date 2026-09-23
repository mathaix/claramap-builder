![Claude coordinates scoped workers, validates their results, and integrates the change](skills/implement/assets/claramap-builder-hero.png)

# Claramap Builder

**Agent Skills to Orchestrate Code Development.**

**Claramap Builder is an open-source AgentSkill that gives code development a chief of staff.**
Install it in your coding harness and invoke `/implement` with a goal. Claude Code
coordinates specialist subagents: they investigate, plan, code, test, and review.
The chief assigns scoped work, selects models for its complexity, reconciles results,
and directs integration and repairs until the required checks and review pass.

The skill bundles instructions, references, spec templates, and executable helpers.
The current implementation runs on **Claude Code, Codex, and SpecStory**, with
**Kiro-based feature-spec templates using EARS**. **SpecFlow** informs the broader
planning and refinement workflow. See [attribution](#attribution).
The AgentSkill format can be adapted to other coding harnesses; the shipped setup
uses Claude Code as its host. See [harness support](docs/architecture.md#agent-skill-packaging-and-harness-support).

[Install the skill](docs/usage.md) · [How it works](docs/implement.md) · [Architecture](docs/architecture.md)

## The chief-of-staff pattern

One agent doing everything accumulates source reads, tool output, test failures, and
abandoned attempts in the same context. As a task grows, that history can crowd out
the decisions that matter. Claramap separates coordination from execution: the chief
keeps the goal, constraints, decisions, and progress; specialists work in separate
contexts with only the instructions and evidence relevant to their assignments.

| Role | Responsibility |
| --- | --- |
| Chief of staff | Break down the goal with planner findings, assign work, reconcile evidence, and report the result |
| Planner | Inspect the codebase and produce a grounded plan and task breakdown |
| Coder | Implement a scoped change and return its revision and focused check evidence |
| Test-runner | Execute and interpret checks; report failures without silently fixing the product |
| Reviewer | Check the integrated diff against the original intent and identify defects and regression risks |

The chief delegates codebase investigation, product edits, and test execution by
default. Small fixes still use a scoped coder and independent review; every role
does not need a separate agent on every task. Any direct-work exception must be
explained before acting, recorded with evidence, and disclosed in the final report.

Workers return concise summaries and pointers to their available execution traces.
Tool events, transcripts, and check logs stay on disk; the chief reads relevant excerpts
when needed instead of loading every trace into its context. Capture gaps remain explicit.

This approach draws on Anthropic's [chief-of-staff cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-01-the-chief-of-staff-agent),
particularly specialist subagents and separate contexts. Claramap remains a skill
for an existing harness; it does not require the cookbook's SDK application. The
coordinator boundary is an instruction and audit requirement, not a tool-level
restriction enforced by the installer. See [Architecture](docs/architecture.md#chief-of-staff-responsibilities-and-context).

## Why I built this

I built Claramap Builder to make agent-driven development easier to coordinate,
inspect, and improve. Three goals shaped it:

1. **Orchestrate development across coding harnesses.** Package the workflow as an
   AgentSkill so its instructions, context, and development practices can travel with
   the tools I use. The current implementation connects Claude Code and Codex;
   adapting another harness means wiring its execution and review capabilities.

2. **Use a powerful orchestrator and delegate to specific subagents.** Keep the goal, constraints,
   and key decisions with a capable coordinator while isolating detailed execution context. Give each subagent a scoped
   task, the context it needs, and a model matched to the work's complexity. The
   orchestrator reconciles the evidence, directs integration, and drives the next iteration.

3. **Capture the work so I can improve the workflow.** Preserve conversations,
   worker attempts, check results, and review findings. Use those records to understand
   repeated work, slow handoffs, and verification gaps, then make targeted improvements
   and evaluate them on later runs.

### Where it fits

I wanted spec-driven development with a coordinator that owns the complete goal:
assigning contextual work, validating the integrated result, and preserving evidence
for the next run. Claramap Builder packages that workflow as an MIT-licensed agent
skill with inspectable helpers.

| Approach | Documents and structure | Workflow support |
| --- | --- | --- |
| [Kiro feature specs](https://kiro.dev/docs/specs/feature-specs/) | Requirements, design, and tasks; EARS acceptance criteria | Spec workflow integrated into Kiro |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | Specification, technical plan, and tasks | CLI setup, templates, and agent skills/commands for implementation and convergence |
| [Codex project instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | `AGENTS.md` carries project instructions; teams supply their own spec conventions | Codex loads instructions into agent context; project tools and checks implement additional gates |
| [Claude Code project instructions](https://code.claude.com/docs/en/memory) | `CLAUDE.md` carries project instructions; teams supply their own spec conventions | Claude loads instructions into agent context; project tools and checks implement additional gates |
| **Claramap Builder** | Kiro-style specs, EARS, scoped worker briefs, exact-tree review records, and token reports | Agent skill plus worker, review, usage, and recovery helpers; currently coordinates Claude Code and Codex |

These approaches operate at different layers and can be combined. A project's
`SPEC.md` and use of RFC 2119 words such as MUST or SHOULD are authoring choices;
this comparison does not treat them as a universal Codex or Claude Code spec format.

Claramap Builder's review helper checks that approval names the reviewed Git tree
and that the captured content remains unchanged. The coordinator still judges
reviewer independence, finding dispositions, and check results. Token reports show
observed usage, not verified billing. See [Architecture](docs/architecture.md) for
the boundaries of those guarantees.

## Architecture

[![Claramap Builder architecture: Kiro and EARS inform feature specs; SpecFlow informs the workflow; Claude coordinates Codex workers, validates their results, and obtains independent review. SpecStory and run records support workflow analysis.](docs/assets/architecture.png)](docs/architecture.md)

See the [Architecture guide](docs/architecture.md) for the full workflow, component
responsibilities, installation requirements, and where specs and run records live.

These are separate projects used by the skill. **Set up the tools before your first
build; `scripts/install.py` only copies Claramap Builder's skill files.**

| Project | What it is and how we use it | Install beforehand? |
| --- | --- | --- |
| [Claude Code](https://github.com/anthropics/claude-code) | Anthropic's terminal coding agent. Hosts the skill, coordinates tasks and repairs, and runs a separate agent for independent review. | **Yes.** Install and authenticate; ensure access to the configured reviewer. [Setup](https://code.claude.com/docs/en/overview). |
| [Codex CLI](https://github.com/openai/codex) | OpenAI's terminal coding agent. Runs scoped workers with relevant context and a model selected for task complexity. | **Yes for Codex workers.** Install and authenticate for Codex workers. Native Claude agents provide the configured review and capability fallback; the chief does not code by default. [Setup](https://github.com/openai/codex#quickstart). |
| [SpecStory CLI](https://github.com/specstoryai/getspecstory) | A tool that saves AI coding conversations as local Markdown. Captures coordinator and worker history for recovery and workflow analysis. | **Yes.** Install its CLI and enable capture before starting the documented workflow. [Setup](https://docs.specstory.com/integrations/terminal-coding-agents). |
| [SpecFlow](https://github.com/specstoryai/specflow) | SpecStory's methodology for building with software agents: intent, roadmap, tasks, execution, and refinement. Informs the workflow, task ownership, and context supplied to workers. | **No.** A workflow influence; the feature-spec templates are based on Kiro and EARS. [Method guide](https://www.specflow.com/getting-started.html). |

Python 3.11+, Git, and macOS/Linux or WSL are also required for the helpers.
The [installation guide](docs/installation.md#requirements) gives the setup order and
checks. The [architecture guide](docs/architecture.md) explains capture records and
how the components connect.

## Developer workflow

### One-time setup

Install and authenticate Claude Code, Codex CLI (for Codex workers), and SpecStory
as listed above. Ensure Git and Python 3.11+ (`python3` on PATH) are available.
Kiro/EARS inform the spec templates; SpecFlow informs the workflow. Neither needs installation.

With [uv installed](https://docs.astral.sh/uv/getting-started/installation/),
install both Claramap Builder skills in one command:

```sh
git clone https://github.com/mathaix/claramap-builder.git ~/claramap-builder
cd ~/claramap-builder
uv run scripts/install.py
```

This installs `/implement` and `/improve-workflow` under `~/.claude/skills/`,
available across your projects. You do not repeat installation for each build.
Without uv, use `python3 scripts/install.py`. uv can provide Python for the installer;
the runtime helpers still require `python3` 3.11+ on PATH. Neither command installs
or authenticates the external tools.
See [installation and updates](docs/installation.md) for model access, project-specific
installation, and upgrading the skill.

### For each development goal

1. **Start in your project.** Open Claude with session capture from the product repository:

   ```sh
   cd /path/to/your/project
   specstory run claude --no-cloud-sync
   ```

   When using Codex workers, keep `specstory watch --no-cloud-sync` running in another
   terminal in the relevant worktree. See [capture setup](docs/installation.md#run-claude-and-codex-through-specstory).
   An existing captured session can handle subsequent goals.

2. **Describe the outcome.** Give the skill a goal, constraints, and acceptance criteria:

   ```text
   /implement Add a display-name setting. Save it using the existing profile API,
   preserve account permissions, and verify that it survives a page reload.
   ```

3. **Delegate and iterate.** The chief uses a planner's findings to scope the work
   and commission specs where needed. Coders implement changes; assigned workers run
   checks; an independent reviewer examines the integrated result. The chief evaluates
   their summaries and evidence, directs integration, and assigns repairs. Missing
   access or unresolved requirements remain explicit blockers.

4. **Inspect the result.** Review the changed code, check results, independent review
   findings, and remaining gaps. Larger changes include requirements, design, and task
   progress in **your product repository at `specs/<slug>/`**. Run evidence stays in
   `~/.claude/implement/`, and conversations in the worktree's `.specstory/history/`.
   Each run's `execution.md` identifies executors, trace locations, and any direct-work
   exceptions. See [Where files live](docs/architecture.md#where-files-live).

5. **Commit and publish through your project workflow.** Have the coordinator perform
   authorized Git and PR actions, or handle them yourself. Commit product specs with
   the code, keep raw run records local, and satisfy your repository's review and CI
   requirements. Specify deployment separately when you want it.

6. **Resume or improve when needed.** If interrupted, ask `/implement` to resume the
   existing run, reconcile Git and worker state, and continue remaining work. After a
   build, use `/improve-workflow` to investigate bottlenecks and recommend improvements.

The [first-build guide](docs/usage.md) provides more detail. The
[illustrative walkthrough](skills/implement/references/example-run.md) shows the
records and review process using a synthetic example.

Claramap Builder is [MIT licensed](LICENSE). Model usage runs through your existing
accounts and is subject to their billing.

## Improve how the next build runs

The companion `/improve-workflow` skill examines completed runs to find repeated work,
slow handoffs, and verification gaps. Ask why a small fix took an hour, where checks
were duplicated, or what should change before the next build.

It is included in the default installation. Ask in your project:

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
| [Architecture](docs/architecture.md) | Claude, Codex, SpecStory, SpecFlow, capture records, and harness support |
| [Installation and configuration](docs/installation.md) | Prerequisites, model policy, project setup, updates, and removal |
| [Improve the next build](docs/improve-workflow.md) | Investigate runs and apply evidence-based improvements |
| [Illustrative walkthrough](skills/implement/references/example-run.md) | Follow a request through specs, checks, and review |
| [Contributing](CONTRIBUTING.md) | Repository structure, tests, and contribution guidance |

The installed agent instructions live in [implement](skills/implement/SKILL.md) and
[improve-workflow](skills/improve-workflow/SKILL.md). See the
[spec format and provenance](skills/implement/references/spec-format.md).

## Attribution

Claramap Builder combines existing ideas with its own orchestration and verification
helpers. Credit for the foundations belongs to:

- **[Anthropic's chief-of-staff cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-01-the-chief-of-staff-agent):**
  an example of specialist subagents with separate contexts. Claramap adopts the
  orchestration pattern through skills and existing harness tools, rather than
  bundling the SDK application. Its delegation-first boundary and exception records
  are Claramap policy.

- **[Kiro](https://kiro.dev/docs/specs/feature-specs/):** the three-file feature-spec
  layout (`requirements.md`, `design.md`, `tasks.md`), EARS-based requirements,
  tasks that cite requirement IDs, and keeping specs versioned with the code.
  See its [requirements-first workflow](https://kiro.dev/docs/specs/feature-specs/requirements-first/)
  and [version-control guidance](https://kiro.dev/docs/specs/best-practices/).
- **[EARS — Easy Approach to Requirements Syntax](https://alistairmavin.com/ears/):**
  the event-driven `WHEN … THE SYSTEM SHALL …` sentence form. Developed by Alistair
  Mavin and colleagues and first published in 2009, EARS predates both Kiro and SpecFlow.
- **[SpecFlow](https://github.com/specstoryai/specflow):** the five-phase framing of
  intent, roadmap, tasks, execute, and refine, including assigning tasks to humans or
  AI. Its [prompt-context concept](https://www.specflow.com/getting-started.html#step-41-prepare-your-ai-assistant)
  carries into our [worker briefs](skills/implement/assets/templates/brief.md).
  `/improve-workflow` applies the Refine phase to the development workflow itself.
- **[SpecStory](https://github.com/specstoryai/getspecstory):** the conversation-capture
  tooling used by the current implementation, and the publisher of SpecFlow. Its CLI
  is an installed dependency; its captured history supports recovery and workflow analysis.

The templates are our adaptations. Worker model routing, execution records, review
snapshots, and recovery helpers are Claramap Builder's implementation. Kiro, EARS,
and SpecFlow supply structure and methodology and require no separate installation
for this skill; SpecStory supplies a tool that must be installed for capture.

Built by [mathaix](https://github.com/mathaix).

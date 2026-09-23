# Architecture

[Claramap Builder](../README.md) · [Your first build](usage.md) · [Installation](installation.md)

Claramap Builder packages a chief-of-staff workflow as an AgentSkill: instructions,
references, templates, and helpers that a coding harness can load. The current
implementation uses Claude, Codex, and SpecStory. Feature-spec templates are based on
Kiro and EARS; SpecFlow informs the surrounding planning and refinement workflow. Each serves a different part of the development loop.

## What to install before starting

The linked repositories below are the upstream projects. Claramap Builder's installer
copies the skill files only; it does not install these tools, authenticate accounts,
or start session capture.

| Project | What it is | Required setup |
| --- | --- | --- |
| [Claude Code](https://github.com/anthropics/claude-code) | Anthropic's terminal coding agent, used here as coordinator and independent reviewer. | Install and authenticate before running the skill. Confirm access to the reviewer selected by the model policy. |
| [Codex CLI](https://github.com/openai/codex) | OpenAI's terminal coding agent, used here for delegated workers. | Install and authenticate for Codex workers. Native Claude agents provide configured review and capability fallback. Reading existing run evidence does not need a Codex worker. |
| [SpecStory CLI](https://github.com/specstoryai/getspecstory) | A conversation capture tool that exports coding-agent sessions to local Markdown. | Install before starting the documented workflow, then enable capture for the relevant sessions. |
| [SpecFlow](https://github.com/specstoryai/specflow) | SpecStory's structured methodology for development with software agents. | No installation. A workflow influence, not the source of the Kiro/EARS feature-spec templates. |

Use the [installation checklist](installation.md#requirements) to prepare the tools
before installing the skill. SpecFlow here refers to SpecStory's agent-development
methodology, not the unrelated .NET testing framework.

## How everything connects

[![Claramap Builder architecture: Kiro and EARS inform feature specs; SpecFlow informs the workflow; Claude delegates to Codex workers, validates their results, and obtains independent review. Failed checks return for repair. SpecStory history and run records feed requested workflow analysis.](assets/architecture.png)](assets/architecture.png)

Select the image to view it at full size.

The numbered row shows a delegated build: Claude scopes the goal, Codex workers
execute contextual tasks, the chief evaluates verification evidence and directs
integration, and an independent Claude agent reviews the result. Failed checks or
blocking findings return to a worker for repair. The validation/integration stage
denotes responsibility for acceptance; it does not assign product coding to the chief.
Native Claude agents provide independent review and the configured local-capability
fallback; ordinary workers use the policy's allowlisted models. A native dispatch
interface is valid when it supports the selected role/model.

The image's SpecFlow card represents a workflow influence. Kiro and EARS supply
the feature-spec structure; SpecFlow informs planning, task ownership, worker
context, and refinement. SpecStory captures conversations,
while the helpers and coordinator retain execution records. Both feed
`/improve-workflow` when requested. Capture must be configured for the relevant
sessions; improvements are applied only when requested. Completion requires passing
checks and approved content. Missing permissions, capabilities, or proof stay explicit.

## Chief-of-staff responsibilities and context

The chief owns the development goal, acceptance criteria, assignment decisions,
dependencies, and final report. Specialists own detailed execution. This reduces the
source reads, failed attempts, and raw tool output the chief must carry while making
cross-task decisions. It does not guarantee lower cost, faster completion, or better
results; those outcomes need evidence from comparable runs.

| Role | Works with | Returns to the chief |
| --- | --- | --- |
| Planner | Relevant code, repository rules, existing specs, and constraints | Findings, proposed design/task breakdown, risks, and source references |
| Coder | A scoped brief, owned paths, acceptance criteria, and an isolated or serialized checkout | Changed revision, focused checks, remaining issues, and trace pointers |
| Test-runner | Named revision, required scenarios, and an authorized test environment | Commands, outcomes, logs, and failures to assign for repair |
| Reviewer | Integrated diff, original intent/specs, and check evidence | Independent findings and a verdict identifying the reviewed content |
| Chief of staff | Compact plans, assignments, summaries, evidence references, and open decisions | Next assignments, acceptance decisions, progress, and final report |

Roles can be combined where useful: a coder can investigate a small fix and run its
focused tests. Independent review remains separate from implementation. Parallelism
is optional; separate context is useful even when workers execute sequentially.

### Summaries in context, traces on disk

Each assignment gets the minimum relevant context, not a copy of the chief's entire
conversation. Workers return a compact result and pointers to their available tool
traces, captured conversations, check logs, and artifacts. The chief retrieves bounded
evidence to resolve a question. Returning every full trace inline would defeat the
context boundary. "Trace" means observable execution records, not hidden model reasoning;
missing subagent exports must be reported, not represented as complete capture.

The coordinator maintains `<run-dir>/execution.md` for every run, identifying tasks,
roles, actual agent/session IDs, revisions, results, evidence/trace paths, and capture
gaps. Codex attempt files support that record; native-agent assignments need their own
identity and evidence pointers. An empty wrapper worker table does not establish
that no native agents ran.

### Direct-work exceptions

The chief delegates codebase investigation, spec authorship, product edits, tests,
and integration repairs. It can read governing instructions and concise reports,
maintain coordination records, and run orchestration helpers or authorized Git actions.
Those operations must not conceal product edits or conflict resolution.

Before any direct product work, state and record a concrete justification, evidence,
alternatives considered, the bounded action, and its check/review plan. An explicit
user direction or a demonstrated capability/delegation limitation may qualify; speed,
small scope, or existing context alone does not. Report exceptions at completion.
If no authorized route exists, report the blocker. Full policy and the record format
are in [chief-of-staff instructions](../skills/implement/references/chief-of-staff.md).

### Cookbook influence and enforcement limits

Anthropic's [chief-of-staff cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-01-the-chief-of-staff-agent)
demonstrates specialist subagents with separate conversation histories and tools,
and hooks for deterministic actions. Claramap applies those architectural ideas as
instructions in an existing harness. It does not copy the cookbook's application or
require the Claude Agent SDK. Its default prohibition on coordinator product work
is Claramap's policy; the cookbook also demonstrates direct tool use.

The skill and execution record establish an instruction and audit contract. The
installer does not configure hooks or remove coordinator tools; the existing review
gate checks reviewed content and verdict identity, not who authored every change.
Hard restrictions on coordinator writes, including shell-based edits, would require
additional harness-specific controls. Such enforcement is not shipped here.

## Where files live

**Feature specs live in the repository you are building, under `specs/<slug>/`.**
The Claramap Builder checkout contains reusable templates; the installed skill uses
those templates to create specs in your product worktree. You do not put your
product's feature specs in the Claramap Builder checkout or installed skill directory.

For example, building a display-name setting in a project called `my-app` uses a
feature slug such as `display-name`. The following is an illustrative layout;
worker, check-log, and review directory names are chosen per run.

```text
~/claramap-builder/                     # Maintained source of Claramap Builder
└── skills/implement/
    ├── SKILL.md                        # Reusable agent instructions
    └── assets/templates/               # Blank spec and worker-brief templates

~/.claude/skills/implement/              # Installed copy loaded by Claude Code
├── SKILL.md
├── model-policy.json
├── assets/templates/
└── scripts/

/path/to/my-app/                        # Your product repository / worktree
├── specs/display-name/                 # Feature-specific specs; commit with code
│   ├── requirements.md                 # Goal, constraints, acceptance criteria
│   ├── design.md                       # Approach, decisions, design-review status
│   └── tasks.md                        # Assignments, checks, progress, dispositions
├── .specstory/history/                  # Local captured conversations
└── ...                                 # Your product source and tests

~/.claude/implement/my-app-display-name/ # Local execution evidence for this run
├── execution.md                        # Coordinator-maintained assignments, traces, exceptions
├── task-01/                            # Example worker record directory
│   ├── workdir                         # Path to the worker's actual code checkout
│   ├── events-1.jsonl                  # Worker events
│   └── attempt-1.json                  # Exit, timing, model, and observed usage
├── checks/                             # Example location for saved check logs
├── review-final/                       # Example review record directory
│   ├── snapshot.json                   # Identity of the reviewed Git content
│   ├── diff.patch                      # Change submitted for review
│   └── verdict.md                      # Independent reviewer's response
├── recovery.json                       # Observed state and next action
└── recovery.md                         # Human-readable recovery summary
```

### What to commit

| Files | Who creates or updates them | Git treatment |
| --- | --- | --- |
| `specs/<slug>/requirements.md`, `design.md`, `tasks.md` | A planner or assigned worker writes them; the chief reconciles decisions and assigns updates. | Commit and review with the product code. Link existing specifications rather than duplicating them. |
| `execution.md` | The chief records assignments, identities, evidence pointers, capture gaps, and direct-work exceptions. | Keep in the local run folder, including runs without specs. |
| Worker records, check logs, review snapshots, and recovery files | The worker wrapper and review/recovery helpers create their records; the coordinator records checks and saves reviewer replies. | Keep in the local run folder outside the product worktree. |
| `.specstory/history/` | SpecStory, when capture is running for that worktree. | Keep raw conversations local; exclude `.specstory/` through the product's ignore or local exclude rules. |
| Installed skill files | `scripts/install.py` copies them from the maintained source. | Personal installations live outside the product repo. A project installation in `.claude/skills/` may be committed deliberately for the team. |

For small, settled changes, a spec folder is optional. The request and commit message
can carry the acceptance criteria. For larger changes, `tasks.md` is the place to
look for remaining work; keep bulky logs in the run folder and reference their paths.
A small task still uses delegation and an execution record even when no spec folder is needed.

### How the locations connect

Use the same feature slug in the spec path and run name: `specs/display-name/` pairs
with `my-app-display-name/`. This is a naming convention selected by the coordinator,
not automatic discovery between the folders. Worker records can be nested below that
run, such as `my-app-display-name/task-01`.

A worker's record directory is separate from its code checkout. Parallel coding
workers use isolated Git worktrees; the coordinator chooses their locations and
assigns integration into the product worktree to a worker, including conflict resolution. Capture conversations in each
worktree that hosts relevant activity.

`IMPLEMENT_ROOT` changes the wrapper's default `~/.claude/implement` root. Supply
matching explicit paths to the review and recovery helpers. The scaffold helper
always receives the target product worktree and feature slug. With a project skill
installation, reusable skill files live in `<project>/.claude/skills/implement/`;
feature specs still live in `<project>/specs/<slug>/`.

To resume, start with the product's specs, current Git state, and the run's recovery
records. Recovery files are snapshots, not live monitors; inspect worker locks and
actual results before continuing. SpecStory supplies conversation context and does
not by itself prove that a check passed or an interrupted worker stopped.

## Claude: chief of staff and independent specialists

[Claude Code](https://github.com/anthropics/claude-code) hosts `/implement` and holds the full development goal. The coordinator
establishes the outcome, delegates project investigation and detailed planning, and
uses returned findings to assign scoped tasks. It chooses models and reasoning effort
according to complexity, risk, and your policy.
It gives workers relevant context, allowed changes, and acceptance criteria.

When results return, the chief reconciles summaries and evidence, directs integration,
and routes failed checks or review findings to repair workers. Planning, coding,
diagnosis, verification, and QA are delegated responsibilities chosen for the task.
The chief does not silently take over implementation when a worker fails.

A separate Claude agent performs independent final review. The shipped
[model policy](../skills/implement/model-policy.json) selects Claude Opus for that
review and Claude Sonnet as the fallback for authorized local work a Codex worker
cannot perform. The host must provide those capabilities; the Python wrapper cannot
launch Claude. The coordinator cannot count its own review as independent.

Claude also hosts `/improve-workflow`, which analyzes run evidence and can update
instructions or helpers when asked. An audit is initiated by the user.

## Codex: execute scoped work

[Codex CLI](https://github.com/openai/codex) runs delegated workers. A worker gets a bounded brief with the goal it
serves, the relevant revision and files, constraints, allowed writes, and checks.
The coordinator selects an allowed model for the task's uncertainty and complexity;
the current choices and defaults are in `model-policy.json`.

The bundled `codex_task.sh` wrapper launches Codex and records prompts, session
identity, events, attempts, exit status, and observed usage. Saved settings and
session identity support resuming interrupted tasks. Locks help prevent a second
writer from starting on the same task while its worker is active.

A successful process exit means the worker finished running. Claude still needs to
validate the returned work and its checks before accepting it. Independent coding
work uses isolated worktrees and is integrated before final verification.

Codex is the bundled ordinary-worker execution path. Native Claude review and
capability fallback do not launch a Codex worker; neither does an audit of existing
records. Native delegation still requires scoped instructions, an actual agent
identity, and retained evidence. Changing an interface does not expand model permission. See
[worker dispatch](../skills/implement/references/delegation.md).

## SpecStory: capture the conversation

[SpecStory](https://github.com/specstoryai/getspecstory) preserves the conversation around the work: requests, decisions, handoffs,
interruptions, and changes in direction. This helps a resumed coordinator recover
context and lets `/improve-workflow` investigate why a run took time or repeated work.
It complements the wrapper's execution records and actual check output.

Capture is required by the documented workflow. The Python helpers can execute
without it, but that does not supply the missing conversation history. The installer
does not install or start SpecStory for you.

Launch the coordinator from the product worktree:

```sh
specstory run claude --no-cloud-sync
```

The wrapper starts delegated Codex workers directly. Keep background capture running
in another terminal in each relevant worktree:

```sh
specstory watch --no-cloud-sync
```

Verify that the relevant coordinator and worker sessions appear in the exported
history. Launching the coordinator through SpecStory does not establish that all
workers or subagents were captured. These commands request local capture; model
execution still uses the configured providers. See the
[SpecStory CLI reference](https://docs.specstory.com/integrations/terminal-coding-agents/usage)
and the [detailed capture guide](../skills/improve-workflow/references/specstory.md)
for existing-session exports, worktrees, and capture limits.

## Specification templates: Kiro and EARS

The feature-spec templates use **Kiro's `requirements.md`, `design.md`, and `tasks.md`
layout**, with **EARS requirements** and tasks that cite requirement IDs. These are
Claramap Builder adaptations, not an official template pack. Specs live alongside
the product code in `specs/<slug>/`.

### SpecFlow: workflow influence

Claramap Builder uses [SpecFlow](https://github.com/specstoryai/specflow) to
structure the work from intent through planning, task decomposition, contextual
execution, and refinement. This influences the workflow instructions and worker context, rather than
defining the feature-spec file layout.

| Planning concept | How the skill applies it |
| --- | --- |
| Intent | Requirements record the requested outcome, constraints, non-goals, and acceptance criteria. |
| Plan | The design records the approach, decisions, and open questions. |
| Scoped tasks | Tasks identify the requirement they serve, files, executor, and check. |
| Contextual execution | Worker briefs provide relevant project context, constraints, and expected results. |
| Refinement | The chief evaluates results, assigns defect repairs, and updates remaining work. |

The [bundled spec format](../skills/implement/references/spec-format.md) combines
this methodology with Kiro's three-file feature-spec layout and EARS requirements.
SpecFlow's human/AI task assignments inform executor selection, and its prompt-context
concept informs worker briefs. `/improve-workflow` applies the Refine phase to the
workflow itself. SpecStory is both SpecFlow's publisher and the provider of the
capture CLI used by this implementation.

### Kiro and EARS: the feature-spec structure

[Kiro feature specs](https://kiro.dev/docs/specs/feature-specs/) inform the
`requirements.md`, `design.md`, and `tasks.md` layout, task references to requirement
IDs, and versioning specs with code. Its use of EARS informs how the requirements
are written.

[EARS](https://alistairmavin.com/ears/) is the original source of the event-driven
`WHEN … THE SYSTEM SHALL …` syntax. Alistair Mavin and colleagues first published it
in 2009, before Kiro and SpecFlow. These are structural influences rather than
installed dependencies. Claramap Builder adds its own checks, execution records,
review snapshots, and recovery helpers. See the full [attribution](../README.md#attribution).
Existing project specifications remain authoritative inputs.

SpecFlow is used as the planning method within the skill. There is no separate
SpecFlow executable, imported package, or service to install for these helpers.

## Usage-report coverage

`usage.py --run <run-dir>` reports available recorded usage and writes `usage.md`.
It detects the Claude coordinator transcript only when the session environment variable
and expected project path match. Pass `--session <transcript.jsonl>` if detection fails;
that transcript's available subagent files are included. Missing records are coverage
gaps, not zero usage. Read the report's Sources and warnings before quoting totals.

Claude totals cover the full supplied session, which can contain multiple development
goals. Codex totals use recorded session-counter deltas attributed to each attempt's
model; first observations may include prior session usage, and counter resets or missing
attempt usage limit attribution. Reports describe observed tokens, not exact per-goal
cost or verified billing.

## Agent Skill packaging and harness support

[Agent Skills](https://agentskills.io/home) packages instructions and supporting
resources in a format that compatible agents can load. Claramap Builder's primary
skill is `skills/implement/`; `skills/improve-workflow/` is its companion for analyzing completed runs.
The default installer installs both; using the companion is optional.
Each includes a `SKILL.md` entrypoint and the resources needed for its role.

The format makes the workflow portable. The shipped execution integration is specific
to Claude Code and Codex CLI: the installer defaults to `~/.claude/skills`, worker
launches invoke Codex, and the review/fallback policy expects native Claude agents.
Copying the files into another harness does not automatically provide those capabilities.

To adapt another harness, configure its skill discovery path, map coordinator and
independent reviewer dispatch to its agent interface, preserve or replace the Codex
worker adapter, and configure model policy and session capture. Validate the full
request-to-review workflow in that host. This repository documents the Claude/Codex
setup; it does not establish tested compatibility with every coding harness.

Python 3.11+, Git, and macOS/Linux or WSL support the bundled helpers. Your product's
own dependencies, test services, and credentials are separate requirements. Follow
[installation and configuration](installation.md) to set up the current implementation.

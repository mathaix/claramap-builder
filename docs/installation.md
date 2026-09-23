# Install and configure Claramap Builder

[Claramap Builder](../README.md) · [Your first build](usage.md) · [Implement guide](implement.md) · [Improve-workflow guide](improve-workflow.md)

One installation includes both skills: `/implement` orchestrates code development,
and `/improve-workflow` analyzes completed runs. You can still select an individual
skill when needed.

For the first-run sequence, use [Your first build](usage.md). This page covers
prerequisites, capture, model configuration, installation options, and maintenance.

## Requirements

**To install the skill files:** you need Git and either
[uv](https://docs.astral.sh/uv/getting-started/installation/) or Python 3.11+.
The recommended `uv run scripts/install.py` command selects a compatible Python
interpreter (downloading one if needed); the installer has no Python package dependencies.

**To use the skills:** complete the following setup before your first build.
Using uv for installation does not put a compatible `python3` on your shell's PATH
or install the coding agents and capture tools for you.

**Install the external tools before your first build.** The Claramap Builder installer
only copies skill files; it does not install dependencies, authenticate accounts,
or start SpecStory capture.

1. Install **Python 3.11+ and Git** on macOS/Linux or WSL on Windows.
   Ensure `python3 --version` reports 3.11 or newer in the shell where workers run;
   the worker wrapper invokes `python3` directly.
2. Install and authenticate **[Claude Code](https://github.com/anthropics/claude-code)**,
   Anthropic's terminal coding agent, using its [setup guide](https://code.claude.com/docs/en/overview).
   It hosts the skill and coordinates work. Confirm access to the configured independent reviewer.
3. For Codex workers, install and authenticate **[Codex CLI](https://github.com/openai/codex)**,
   OpenAI's terminal coding agent, following its [quickstart](https://github.com/openai/codex#quickstart).
   It executes scoped worker tasks. Native Claude agents supply configured review and capability fallback. An audit of saved records does not need a Codex worker.
4. Install **[SpecStory CLI](https://github.com/specstoryai/getspecstory)**, which exports
   AI coding conversations as Markdown for recovery and analysis. Follow the
   [CLI installation guide](https://docs.specstory.com/integrations/terminal-coding-agents).
   On macOS with Homebrew:

   ```sh
   brew install specstoryai/tap/specstory
   ```

**[SpecFlow](https://github.com/specstoryai/specflow) needs no installation.** It is
SpecStory's planning methodology for development with agents. It informs
the intent-to-refinement workflow, task ownership, and worker context. The feature-spec
templates use Kiro's three-file structure and EARS requirements; they are not SpecFlow
templates. Kiro and EARS also need no installation. Read the [method guide](https://www.specflow.com/getting-started.html)
for background.

See [architecture](architecture.md) for each component's role and
the connections between planning, execution, review, and capture.

Check the setup (the `codex` check applies when using Codex workers):

```sh
python3 --version
git --version
claude --version
codex --version
specstory version
specstory check
```

Both skills are installed by default. Implement delegates product work, including
small changes, to scoped agents; it needs Codex when using the bundled worker wrapper.
The host must provide a permitted delegation route and independent review.
The chief must explain and record any direct-work exception; missing worker access
is not permission to silently implement the task itself. Improve-workflow can analyze
existing records without launching workers and adds no fixed model requirement of its own.

## Run Claude and Codex through SpecStory

From the product repository, launch Claude Code through SpecStory:

```sh
specstory run claude --no-cloud-sync
```

Enter `/implement <task>` or `/improve-workflow <question>` in that Claude session. For an interactive Codex session, launch it the same way:

```sh
specstory run codex --no-cloud-sync
```

These are separate interactive sessions; you do not need to open an extra Codex session for implement's delegated workers. Those workers are launched directly by `codex_task.sh`. Keep background capture running in another terminal in the relevant worktree:

```sh
specstory watch --no-cloud-sync
```

SpecStory saves exported conversation history under `.specstory/history/`; `--no-cloud-sync` keeps the exports local. Check that relevant sessions appear there. Worker attempt and review records remain under `~/.claude/implement/`; specs live in the product repository under `specs/<slug>/`; launching the coordinator through SpecStory alone does not prove every worker was captured. See the [capture guide](../skills/improve-workflow/references/specstory.md) for existing sessions, worktrees, and capture limits, and the [official CLI reference](https://docs.specstory.com/integrations/terminal-coding-agents/usage) for launch options.

## Personal installation

```sh
git clone https://github.com/mathaix/claramap-builder.git ~/claramap-builder
cd ~/claramap-builder
uv run scripts/install.py
```

This installs **both** skills and their supporting files under
`~/.claude/skills/implement/` and `~/.claude/skills/improve-workflow/`.
Invoke them with `/implement` and `/improve-workflow`.
See the [official skill documentation](https://code.claude.com/docs/en/skills).

Without uv, use `python3 scripts/install.py` with Python 3.11+.
To install only one skill, pass its name: `uv run scripts/install.py implement`
or `uv run scripts/install.py improve-workflow`. These are optional alternatives,
not additional setup steps. uv runs the checked-out installer; this is not a
Python package installed with `uv pip` or `uv tool install`.

Start a new Claude Code session after installing, or explicitly ask an existing coordinator to reread the updated skill. Already-running subagents retain their original briefs.

## Project installation

Use an explicit destination from the collection checkout:

```sh
uv run scripts/install.py --skills-dir /absolute/path/to/project/.claude/skills
```

This installs both skills into that project's skill directory. Review before committing the installed files to a project. Pick personal or project installation deliberately to avoid stale duplicate copies.

## Model policy

Implement's [model-policy.json](../skills/implement/model-policy.json) is the single source
for the worker allowlist, default worker/effort, independent reviewer, and capability
fallback. These are the author's configuration, not a promise of account access.

`IMPLEMENT_MODEL` and `IMPLEMENT_EFFORT` select a worker for a task. They do not bypass
the allowlist or grant access. Resumes preserve saved settings unless explicitly overridden;
changing a default does not change an existing worker's settings. Every launch rechecks
the selected model against the current allowlist.

For an explicitly authorized policy change, edit `model-policy.json` in the maintained
skill source, run its tests, and reinstall. No Python change is needed. Preserve explicit
user pins and budgets; do not substitute another reviewer silently. The wrapper enforces
worker settings, while Claude must select the configured reviewer/fallback through its
native interface. [Model routing](../skills/implement/references/model-routing.md) explains
task selection and capability handoffs.

An independently supplied review capability is necessary to complete this workflow. This collection does not bundle private review plugins, configure paid remote reviewers, or promise that a different host can dispatch Claude agents. Repository-required review integrations remain the repository's responsibility.

### Existing plugins and saved preferences

On skill reload, reconcile older plugin routing defaults and saved model preferences
with the current task's model policy. A generic preference for native Claude subagents
can otherwise keep a coordinator from using Codex even after these files are updated.
The chief must identify the conflict and apply the current authorized direction before
its next dispatch. Installing Claramap does not remove or rewrite other plugins.
A historical Codex capability failure only justifies fallback for the operation and
environment it actually covers; it does not disable Codex for all future work.

## Update

From your collection checkout:

```sh
git pull --ff-only
uv run scripts/install.py --replace
```

The default update replaces both skills. Add a skill name to update only that skill.
Without uv, use `python3 scripts/install.py --replace`.

Replacement moves each old installed skill to a timestamped backup under a sibling `.skill-backups/` directory, outside skill discovery. It installs the new copy and prints the backup path. If local changes matter, compare them before replacing. The installer refuses a symlink destination.

To restore, stop relevant agents, move the current `<skill-name>` directory aside, then move the printed backup back to `<skills-dir>/<skill-name>`. To uninstall either skill, move its directory out of the skills directory. Your separate run history under `~/.claude/implement/` remains intact.

## Validate

```sh
python3 -m unittest discover -s skills/implement/tests -v
python3 -m unittest discover -s tests -v
```

These checks use fake worker processes and temporary repositories; they do not spend model credits. The external skill-creator validator is optional when available. It is not required to install or use this collection.

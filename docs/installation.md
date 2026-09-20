# Install and configure Claramap Builder

[Claramap Builder](../README.md) · [Your first build](usage.md) · [Implement guide](implement.md) · [Improve-workflow guide](improve-workflow.md)

Install `implement` to orchestrate code development. Add `improve-workflow` when you
want to analyze completed runs. The skills can be installed independently; their
commands remain `/implement` and `/improve-workflow`.

For the first-run sequence, use [Your first build](usage.md). This page covers
prerequisites, capture, model configuration, installation options, and maintenance.

## Requirements

**Install the external tools before your first build.** The Claramap Builder installer
only copies skill files; it does not install dependencies, authenticate accounts,
or start SpecStory capture.

1. Install **Python 3.11+ and Git**. Helpers require macOS/Linux or WSL on Windows.
2. Install and authenticate **[Claude Code](https://github.com/anthropics/claude-code)**,
   Anthropic's terminal coding agent, using its [setup guide](https://code.claude.com/docs/en/overview).
   It hosts the skill and coordinates work. Confirm access to the configured independent reviewer.
3. For delegated builds, install and authenticate **[Codex CLI](https://github.com/openai/codex)**,
   OpenAI's terminal coding agent, following its [quickstart](https://github.com/openai/codex#quickstart).
   It executes scoped worker tasks. A direct Claude task or an audit of saved records does not need a Codex worker.
4. Install **[SpecStory CLI](https://github.com/specstoryai/getspecstory)**, which exports
   AI coding conversations as Markdown for recovery and analysis. Follow the
   [CLI installation guide](https://docs.specstory.com/integrations/terminal-coding-agents).
   On macOS with Homebrew:

   ```sh
   brew install specstoryai/tap/specstory
   ```

**[SpecFlow](https://github.com/specstoryai/specflow) needs no installation.** It is
SpecStory's planning methodology for development with agents. The skill incorporates
its intent, roadmap, tasks, execution, and refinement approach in the bundled
instructions and templates. Read the [method guide](https://www.specflow.com/getting-started.html)
for background.

See [dependencies and architecture](dependencies.md) for each component's role and
the connections between planning, execution, review, and capture.

Check the setup (the `codex` check applies when using delegated workers):

```sh
python3 --version
git --version
claude --version
codex --version
specstory version
specstory check
```

The skills can be installed separately. Implement can handle small changes directly in
Claude; it needs Codex only when delegating to Codex workers. Improve-workflow can analyze
existing records without launching workers and adds no fixed model requirement of its own.

The skill installer only copies skill files. It does not install these programs, authenticate them, or start SpecStory.

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
python3 scripts/install.py implement
python3 scripts/install.py improve-workflow
```

Each command installs only the named skill and its supporting files under `~/.claude/skills/<name>/`. Invoke them with `/implement` and `/improve-workflow`. Install either or both. See the [official skill documentation](https://code.claude.com/docs/en/skills).

Start a new Claude Code session after installing, or explicitly ask an existing coordinator to reread the updated skill. Already-running subagents retain their original briefs.

## Project installation

Use an explicit destination from the collection checkout:

```sh
python3 scripts/install.py implement --skills-dir /absolute/path/to/project/.claude/skills
```

This makes the skill part of that project's skill directory. Review before committing the installed files to a project. Pick personal or project installation deliberately to avoid stale duplicate copies.

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

## Update

From your collection checkout:

```sh
git pull --ff-only
python3 scripts/install.py implement --replace
python3 scripts/install.py improve-workflow --replace
```

Replacement moves the old installed skill to a timestamped backup under a sibling `.skill-backups/` directory, outside skill discovery. It installs the new copy and prints the backup path. If local changes matter, compare them before replacing. The installer refuses a symlink destination.

To restore, stop relevant agents, move the current `<skill-name>` directory aside, then move the printed backup back to `<skills-dir>/<skill-name>`. To uninstall either skill, move its directory out of the skills directory. Your separate run history under `~/.claude/implement/` remains intact.

## Validate

```sh
python3 -m unittest discover -s skills/implement/tests -v
python3 -m unittest discover -s tests -v
```

These checks use fake worker processes and temporary repositories; they do not spend model credits. The external skill-creator validator is optional when available. It is not required to install or use this collection.

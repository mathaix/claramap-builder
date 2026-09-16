# Installation

[All guides](usage.md) · [Implement guide](implement.md) · [Improve-workflow guide](improve-workflow.md)

## Requirements

This workflow assumes **SpecStory CLI, Claude Code, and Codex CLI are already installed**, with Claude and Codex authenticated. SpecStory is a required part of the documented setup: Claude and Codex sessions run with its capture enabled so improve-workflow can review their conversation history alongside implementation evidence.

- Install [Claude Code](https://code.claude.com/docs/en/overview) and Codex CLI, and complete their authentication setup.
- Install [SpecStory CLI](https://docs.specstory.com/integrations/terminal-coding-agents). On Homebrew: `brew install specstoryai/tap/specstory`.
- Install Python 3.11+ and Git. Implement's helpers use POSIX facilities on macOS/Linux; use WSL on Windows.

Check the setup:

```sh
python3 --version
git --version
claude --version
codex --version
specstory version
specstory check
```

The skills can be installed separately. Implement uses Claude for orchestration and independent review, and Codex for delegated workers; check its [model policy](#model-policy). Improve-workflow adds no fixed model requirement of its own.

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

SpecStory saves exported conversation history under `.specstory/history/`; `--no-cloud-sync` keeps the exports local. Check that relevant sessions appear there. Worker attempt and check records remain under `~/.claude/implement/`; launching the coordinator through SpecStory alone does not prove every worker was captured. See the [capture guide](../skills/improve-workflow/references/specstory.md) for existing sessions, worktrees, and capture limits, and the [official CLI reference](https://docs.specstory.com/integrations/terminal-coding-agents/usage) for launch options.

## Personal installation

```sh
git clone https://github.com/mathaix/skills.git ~/mathaix-skills
cd ~/mathaix-skills
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

This policy applies to **implement**. It is the author's working model configuration, not a promise that every account exposes the same IDs:

- Codex worker allowlist: `gpt-5.6-luna`, `gpt-5.6-terra`, `gpt-5.6-sol`.
- Independent final reviewer: Claude Opus through Claude Code's native agent interface.
- Capability fallback: local Claude Sonnet when it can perform an authorized check that the Codex sandbox cannot.
- Astra is excluded by the shipped policy.

`IMPLEMENT_MODEL` and `IMPLEMENT_EFFORT` select a worker within this policy; they do not bypass the allowlist or grant access. If your account lacks these models, adapt the policy explicitly before using the wrapper: update [model-routing.md](../skills/implement/references/model-routing.md), the corresponding statements in `SKILL.md`, and `allowed_models` in `scripts/codex_task.py`, then adjust and run its tests. Preserve your own explicit pins and budget. Do not silently substitute a different reviewer.

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

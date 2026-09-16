# Installation

[All guides](usage.md) · [Implement guide](implement.md) · [Improve-workflow guide](improve-workflow.md)

## Requirements

Both skills can be installed independently. The installer requires Python 3.11+ and Git; the examples below use [Claude Code](https://code.claude.com/docs/en/overview).

**Implement** uses POSIX helpers on macOS or Linux (WSL on Windows), authenticated Claude Code for the coordinator and independent Claude agents, and an authenticated Codex CLI for delegated Codex workers. Direct coordinator work and helper tests do not launch Codex. Check its [model policy](#model-policy) before dispatching workers.

**Improve-workflow** has no executable-helper or fixed model dependency. It works with the available host and evidence. SpecStory and implement-format logs are optional; see the [capture and review guide](../skills/improve-workflow/references/specstory.md).

Check the programs you intend to use:

```sh
python3 --version
git --version
claude --version
codex --version
```

No credentials belong in this repository. Authenticate through each application's normal setup. The installer does not install CLIs, change credentials, or alter tool permissions.

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

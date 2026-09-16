# Installation

## Requirements

- Python 3.11+ and Git for the helpers. They use the Python standard library.
- macOS or Linux; Windows users need WSL because task locks and process cleanup use POSIX facilities.
- [Claude Code](https://code.claude.com/docs/en/overview), authenticated, for the coordinator and independent Claude agents.
- An installed, authenticated Codex CLI for delegated Codex workers. Direct coordinator work and helper tests do not launch Codex.
- SpecStory is optional; see the [capture and review guide](../skills/improve-workflow/references/specstory.md).

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
git clone https://github.com/mathaix/skills.git
cd skills
python3 scripts/install.py implement
python3 scripts/install.py improve-workflow
```

The result is `~/.claude/skills/implement/SKILL.md` plus its supporting files. Claude Code discovers personal skills in that directory; invoke this one with `/implement`. See the [official skill documentation](https://code.claude.com/docs/en/skills).

Start a new Claude Code session after installing, or explicitly ask an existing coordinator to reread the updated skill. Already-running subagents retain their original briefs.

## Project installation

Use an explicit destination from the collection checkout:

```sh
python3 scripts/install.py implement --skills-dir /absolute/path/to/project/.claude/skills
```

This makes the skill part of that project's skill directory. Review before committing the installed files to a project. Pick personal or project installation deliberately to avoid stale duplicate copies.

## Choosing a skill

`implement` executes development work. `improve-workflow` analyzes how that work ran and,
when requested, improves the relevant skill or tooling. They can be installed separately.
The improvement skill has no executable-helper or fixed model dependency; it works with
the available host and evidence. SpecStory and implement-format logs are optional inputs.

Use `/improve-workflow <question or requested change>` in Claude Code after installation.
Update either skill by passing its name with `--replace` to the installer.

## Model policy

This is the author's working model configuration, not a promise that every account exposes the same IDs:

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
```

Replacement moves the old installed skill to a timestamped backup under a sibling `.skill-backups/` directory, outside skill discovery. It installs the new copy and prints the backup path. If local changes matter, compare them before replacing. The installer refuses a symlink destination.

To restore, stop relevant agents, move the current `implement` directory aside, then move the printed backup back to `<skills-dir>/implement`. To uninstall, move `implement` out of the skills directory. Your separate run history under `~/.claude/implement/` remains intact.

## Validate

```sh
python3 -m unittest discover -s skills/implement/tests -v
python3 -m unittest discover -s tests -v
```

These checks use fake worker processes and temporary repositories; they do not spend model credits. The external skill-creator validator is optional when available. It is not required to install or use this collection.

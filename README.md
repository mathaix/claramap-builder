# Skills

Reusable coding-agent skills by [mathaix](https://github.com/mathaix).

| Skill | What it does |
| --- | --- |
| [implement](skills/implement/SKILL.md) | Gives Claude a coordination workflow for a feature, fix, or PR: scope the work, delegate to Codex and Claude agents when useful, verify the integrated result, and obtain independent review. |
| [improve-workflow](skills/improve-workflow/SKILL.md) | Reviews execution reports and SpecStory history to find bottlenecks and improve the development workflow. |

## Install a skill

**Prerequisites:** install SpecStory CLI, Claude Code, and Codex CLI first, and authenticate Claude and Codex. This workflow assumes both coding agents run with SpecStory capture enabled. The skill installer does not install these programs. See [setup and launch commands](docs/installation.md#requirements).

Also requires Python 3.11+ and Git. The implement helpers support macOS and Linux; use WSL on Windows.

```sh
git clone https://github.com/mathaix/skills.git ~/mathaix-skills
cd ~/mathaix-skills
python3 scripts/install.py implement
python3 scripts/install.py improve-workflow
```

Each command installs only the named skill into `~/.claude/skills/<name>/`. You can install either skill independently. Existing installations are preserved unless you explicitly request replacement.

**Model access:** implement is a Claude Code workflow with a Codex worker wrapper. Its shipped policy uses Codex `gpt-5.6-luna`, `gpt-5.6-terra`, and `gpt-5.6-sol`, independent Claude Opus review, and a local Sonnet capability fallback. Those model IDs must be available to your account. See [installation and model policy](docs/installation.md) before dispatching workers.

## Use the skills together

**Implement delivers the code change. Improve-workflow improves how that work gets done.**

Start Claude Code through SpecStory in your product repository:

```sh
specstory run claude --no-cloud-sync
```

Then invoke the skill:

```text
/implement Fix the input-save bug. Reproduce it locally, implement the fix, and verify the affected flow.
```

After a run, inspect its implementation records and SpecStory history:

```text
/improve-workflow Review recent runs. Find repeated work and bottlenecks, and recommend improvements without editing yet.
```

Ask improve-workflow to apply the changes you want. Use the updated skill for later development and compare the results.

![How SpecStory and implementation evidence improve the workflow](skills/improve-workflow/assets/workflow-feedback.png)

## Documentation

| Guide | What you will find |
| --- | --- |
| [Start here: how the skills connect](docs/usage.md) | Choose a skill and understand the feedback loop |
| [Installation](docs/installation.md) | Requirements, personal/project setup, model policy, updates, and removal |
| [Using implement](docs/implement.md) | Requests, orchestrator and subagent roles, executable tools, and completion criteria |
| [Using improve-workflow](docs/improve-workflow.md) | Audit runs, apply improvements, and measure the next run |
| [SpecStory and implementation evidence](skills/improve-workflow/references/specstory.md) | Capture history, locate records, and interpret timings |

## Repository layout

```text
skills/
  implement/        # Code-development orchestrator and executable helpers
  improve-workflow/ # Workflow analysis, feedback loop, and improvement guidance
docs/              # Collection installation and usage
scripts/install.py # Install one selected skill
tests/             # Installer tests
```

Run checks without model calls or credentials:

```sh
python3 -m unittest discover -s skills/implement/tests -v
python3 -m unittest discover -s tests -v
```

Runtime reports and SpecStory transcripts belong in local run/project directories. This repository contains the reusable skill, not real interview transcripts or private implementation history.

[MIT license](LICENSE). Original template adaptations retain their [provenance](skills/implement/references/specflow.md).

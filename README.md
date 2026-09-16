# Skills

Reusable coding-agent skills by [mathaix](https://github.com/mathaix).

| Skill | What it does |
| --- | --- |
| [implement](skills/implement/SKILL.md) | Takes a feature, fix, or PR through implementation, verification, QA, and independent review. The coordinator chooses the work breakdown and checks. |

## Install a skill

Requires Python 3.11+ and Git. The implement helpers support macOS and Linux; use WSL on Windows.

```sh
git clone https://github.com/mathaix/skills.git
cd skills
python3 scripts/install.py implement
```

This copies only `skills/implement/` to `~/.claude/skills/implement/`. Existing installations are preserved unless you explicitly request replacement. Other skills are not changed.

**Model access:** implement is a Claude Code workflow with a Codex worker wrapper. Its shipped policy uses Codex `gpt-5.6-luna`, `gpt-5.6-terra`, and `gpt-5.6-sol`, independent Claude Opus review, and a local Sonnet capability fallback. Those model IDs must be available to your account. See [installation and model policy](docs/installation.md) before dispatching workers.

## Use implement

Open Claude Code in the project you want to work on:

```text
/implement Fix the input-save bug. Reproduce it locally, implement the fix, and verify the affected flow.
```

The coordinator can code directly or assign coding, verification, QA, and diagnosis agents. It selects checks based on risk and reuses valid evidence. One independent final review and repository-required checks remain part of completion.

You can also give a bounded instruction:

```text
/implement Address the remaining findings in this PR. Keep the accepted design, reuse valid test results, and report anything still unverified.
```

See [usage](docs/usage.md), [SpecStory workflow](skills/implement/references/specstory.md), and [installation, updates, and removal](docs/installation.md).

## Improving the workflow

I review SpecStory conversations alongside implementation timings, test evidence, and
review results, then use the findings to improve the skill and its tools. The next run
provides feedback on whether the changes helped.

[See the workflow improvement diagram](skills/implement/references/specstory.md#the-workflow-improvement-loop).

## Repository layout

```text
skills/
  implement/       # Self-contained installable skill, tools, references, and tests
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

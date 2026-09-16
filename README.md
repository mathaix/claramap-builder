# Skills

Reusable coding-agent skills by [mathaix](https://github.com/mathaix).

| Skill | What it does |
| --- | --- |
| [implement](skills/implement/SKILL.md) | Takes a feature, fix, or PR through implementation, verification, QA, and independent review. The coordinator chooses the work breakdown and checks. |
| [improve-workflow](skills/improve-workflow/SKILL.md) | Reviews execution reports and SpecStory history to find bottlenecks and improve the development workflow. |

## Install a skill

Requires Python 3.11+ and Git. The implement helpers support macOS and Linux; use WSL on Windows.

```sh
git clone https://github.com/mathaix/skills.git
cd skills
python3 scripts/install.py implement
python3 scripts/install.py improve-workflow
```

Each command installs only the named skill into `~/.claude/skills/<name>/`. You can install either skill independently. Existing installations are preserved unless you explicitly request replacement.

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

See [usage](docs/usage.md), [SpecStory workflow](skills/improve-workflow/references/specstory.md), and [installation, updates, and removal](docs/installation.md).

## Improving the workflow

Use the separate skill when you want to inspect or improve how development runs:

```text
/improve-workflow Review recent implementation reports and SpecStory history. Find repeated work and bottlenecks, and recommend improvements without editing yet.
```

To apply agreed changes, ask `/improve-workflow` to make and verify them in the skills repository. It uses the same records without automatically altering the development workflow after every run.

I review SpecStory conversations alongside implementation timings, test evidence, and
review results, then use the findings to improve the skill and its tools. The next run
provides feedback on whether the changes helped.

![How SpecStory and implementation evidence improve the workflow](skills/improve-workflow/assets/workflow-feedback.png)

[See the workflow improvement diagram](skills/improve-workflow/references/specstory.md#the-workflow-improvement-loop).

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

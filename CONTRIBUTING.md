# Contributing to Mathaix Build

[Mathaix Build](README.md) · [Installation and configuration](docs/installation.md)

Contributions can improve the agent instructions, helpers, examples, or documentation.
For a bug, include the expected behavior, what happened, and a minimal reproduction.
For a workflow change, explain the observed problem and how the change addresses it.
Keep reports free of credentials, private code, and real conversation transcripts.

## Repository structure

```text
skills/
  implement/        # Orchestration instructions, templates, helpers, and tests
  improve-workflow/ # Workflow analysis instructions and review template
docs/              # Human-facing setup and usage guides
scripts/install.py # Install one selected skill
tests/             # Installer tests
```

Keep instructions needed by installed agents inside their skill directory. Use `docs/`
for human-facing guides, and link to detailed agent references where useful. Preserve
existing command names and paths unless a change includes a migration explanation.

## Check your changes

Run helper and installer tests from the repository root:

```sh
python3 -m unittest discover -s skills/implement/tests -v
python3 -m unittest discover -s tests -v
```

These tests use fake workers and temporary repositories; they do not make paid model
calls or require model credentials. Add a focused regression for a helper bug. For
instruction changes, explain the scenario affected and what you verified; passing
helper tests alone does not establish improved agent behavior.

Check documentation links and keep examples consistent with the actual commands.
Label synthetic examples clearly. Keep runtime reports and SpecStory exports out of
contributions; use purpose-built public fixtures for reproducible examples.

## Submit a change

Describe the problem, the resulting behavior, and relevant validation in your pull
request. Call out changes to model policy, required checks, or installation behavior.
Test installation into a temporary skills directory when changing packaged files;
see [project installation](docs/installation.md#project-installation) for the destination option.

The project is distributed under the [MIT license](LICENSE).

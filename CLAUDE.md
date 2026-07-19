# Bio Run Crate — Claude Code Instructions

## Project purpose

Build a general-purpose Python command-line tool that validates biological
analysis-run metadata, produces structured validation reports, and creates or
enriches RO-Crate packages.

## Current milestone

Milestone 0: establish the repository, documentation, data model and a minimal
working CLI using entirely synthetic examples.

## MVP scope

The MVP must:

1. Read a YAML run manifest.
2. Validate it using explicit Python models and rules.
3. Return ERROR, WARNING and INFO findings.
4. Produce JSON and Markdown validation reports.
5. Create an RO-Crate 1.2 package using ro-crate-py.
6. Optionally accept an existing nf-prov RO-Crate for future enrichment.
7. Use only synthetic and public-safe examples.

## Non-goals

Do not currently implement:

- Benchling integration
- DataHub or OpenMetadata integration
- cloud access
- automatic ontology lookup
- a web interface
- LLM-based metadata generation
- real patient, research or company data

## Technology

- Python 3.12
- uv for environments and dependencies
- src package layout
- Typer for the CLI
- Pydantic for data models
- PyYAML for manifest input
- ro-crate-py targeting RO-Crate 1.2
- pytest for tests
- Ruff for linting and formatting
- mypy for static type checking

## Architecture rules

- Keep parsing, validation, reporting and RO-Crate generation separate.
- Validation rules must have stable identifiers.
- Findings must be serialisable to JSON.
- Core validation must not require network access.
- Modality-specific rules must be implemented as profiles or extensions.
- Prefer small, typed functions.
- Do not silently modify user input.
- Produce deterministic output where practical.

## Development workflow

- Begin non-trivial work in plan mode.
- Work on one GitHub issue or logical task at a time.
- Explain the proposed design before editing multiple files.
- Add tests for new behaviour.
- Update documentation when behaviour changes.
- Run all checks before declaring a task complete.
- Do not commit, push, create releases or change repository visibility unless
  the user explicitly requests it.

## Security and privacy

- Never inspect or display `.env`, credentials, private keys or token files.
- Never add real API keys, access tokens, passwords or private URLs.
- Never use company names, internal systems, bucket names or real sample IDs
  in examples.
- Use `example.org`, synthetic identifiers and generated data.
- Do not read files outside this repository.
- Flag anything that may reveal a personal email address.
- Keep all core functionality usable without credentials.

## Commands

Install and synchronise:

    uv sync

Run tests:

    uv run pytest

Run linting:

    uv run ruff check .

Run formatting:

    uv run ruff format --check .

Run type checking:

    uv run mypy src

Run all checks before completion.

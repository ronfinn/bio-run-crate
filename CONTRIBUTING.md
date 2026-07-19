# Contributing to bio-run-crate

Thanks for your interest in contributing. Bio Run Crate is an early-stage
(alpha), general-purpose tool for validating biological analysis-run metadata.
This guide covers how to set up a development environment, the checks your change
must pass, and the project's ground rules.

Please also read:

- [`docs/project-charter.md`](docs/project-charter.md) — purpose, scope, and
  non-goals. Contributions should fit the charter or propose an ADR if they
  change scope.
- [`docs/security-and-privacy.md`](docs/security-and-privacy.md) — the
  synthetic-data and no-secrets rules that all contributions must follow.
- [`SECURITY.md`](SECURITY.md) — how to report a vulnerability (privately, not
  as a normal issue or PR).

## Ground rules

- **Synthetic data only.** Never add real sample IDs, instrument serial numbers,
  organization names, internal system names, private URLs, cloud bucket names,
  credentials, or personal data — including in tests, fixtures, comments, and
  commit messages. Use invented identifiers and `example.org`-style domains.
- **Core stays offline.** Reading and validating a manifest must work with no
  network access and no credentials.
- **No silent mutation.** The tool must not rewrite or "fix" a user's source
  manifest.
- **Keep concerns separate.** Parsing, validation, reporting, and RO-Crate
  generation are distinct components with narrow interfaces (see
  [`docs/architecture.md`](docs/architecture.md)).
- **One logical change at a time.** Prefer small, focused pull requests tied to a
  single issue or task.

## Development setup

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```
uv sync
```

Run the CLI against the synthetic examples:

```
uv run bio-run-crate version
uv run bio-run-crate validate examples/synthetic/valid-run.yaml
uv run bio-run-crate validate examples/synthetic/invalid-run.yaml
```

## Required checks

Run all of these before opening a pull request; all must pass:

```
uv run pytest                    # tests
uv run ruff check .              # lint
uv run ruff format --check .     # formatting
uv run mypy src                  # type checking
```

Add or update tests for any behaviour you change, and update the relevant
documentation (including [`docs/`](docs/) and the [README](README.md)) when
behaviour changes.

## Pull request checklist

Before requesting review, confirm:

- [ ] No real identifiers, credentials, or personal data were introduced —
      including in fixtures and generated output.
- [ ] Any new example or fixture is clearly synthetic and uses
      `example.org`-style placeholders.
- [ ] All four checks above pass locally.
- [ ] New or changed behaviour has tests.
- [ ] Documentation is updated where behaviour changed.
- [ ] Any change to what data the tool reads, writes, or transmits is called out
      explicitly in the PR description.
- [ ] A user-facing change adds an entry under `## [Unreleased]` in
      [`CHANGELOG.md`](CHANGELOG.md).

## Reporting bugs and proposing features

- **Bugs and feature ideas:** open a GitHub issue. For bugs, include a
  **synthetic** manifest that reproduces the problem, the command you ran, and
  the output.
- **Security issues:** do not open a public issue — follow
  [`SECURITY.md`](SECURITY.md).
- **Scope or architecture changes:** propose an Architecture Decision Record in
  [`docs/decisions/`](docs/decisions/) so the rationale is recorded.

## Licensing of contributions

This project is licensed under the [Apache License 2.0](LICENSE). By submitting a
contribution, you agree that your contribution is provided under the same
license (inbound = outbound), as described in Section 5 of the Apache-2.0 text.
Whether a formal contributor sign-off (such as a DCO) will be required is still
an open question tracked in the [project charter](docs/project-charter.md#9-open-questions).

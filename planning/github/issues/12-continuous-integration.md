## Problem

The project defines required checks — tests, lint, format, and type checking —
but nothing enforces them automatically. Continuous integration runs those
checks on every push and pull request so regressions are caught before merge and
contributors get consistent feedback. Without CI, the `CLAUDE.md` "run all
checks before completion" rule relies entirely on manual discipline.

## Scope

- Add a CI workflow that runs on push and pull request.
- Use `uv` to install dependencies and run: `pytest`, `ruff check`,
  `ruff format --check`, and `mypy src`.
- Pin Python 3.12 to match the project.
- Fail the build if any check fails; keep the workflow free of secrets and
  network dependencies beyond dependency installation.

## Out of scope

- Secret scanning (separate issue).
- Release automation, publishing, or deployment.
- Coverage gates or additional third-party services.

## Acceptance criteria

- [ ] A CI workflow runs pytest, ruff check, ruff format --check, and mypy on push and PR.
- [ ] The workflow uses uv and Python 3.12 and fails on any failing check.
- [ ] The workflow requires no secrets to run the core checks.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

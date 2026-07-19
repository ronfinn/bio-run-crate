## Problem

The project needs a runnable entry point before any validation or packaging
logic is useful. A minimal, typed command-line interface establishes the src
package layout, the Typer application, and the command surface that later
issues build on. Without it there is no way to invoke the tool or to wire
parsing, validation, and reporting together.

## Scope

- Provide the `bio_run_crate` package under a src layout with `py.typed`.
- Expose a `bio-run-crate` console script entry point.
- Implement a Typer application with a `version` command and a `validate`
  command stub that accepts a manifest path.
- Ensure `uv run bio-run-crate version` and `uv run bio-run-crate validate
  <path>` run and exit with sensible status codes.

## Out of scope

- The full validation engine, findings model, and rule set (later issues).
- JSON and Markdown report generation.
- RO-Crate generation.
- Any network access.

## Acceptance criteria

- [ ] `uv run bio-run-crate version` prints the package version.
- [ ] `uv run bio-run-crate validate <path>` accepts a manifest path argument.
- [ ] The CLI is implemented with Typer and is fully type-annotated.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

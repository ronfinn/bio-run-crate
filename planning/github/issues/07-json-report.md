## Problem

Automated consumers — CI pipelines, audit tooling, downstream scripts — need
validation results in a stable, machine-readable form. A JSON report renders the
findings model into a documented, deterministic structure that can be diffed and
parsed reliably. Without it, the only output would be human-oriented text.

## Scope

- Render a run's findings into a JSON report with a stable, documented shape.
- Include run identification, per-finding rule ID, severity, message, and
  location, plus a summary count by severity.
- Emit deterministic output (stable key ordering) so reports are diffable.
- Expose the JSON report through the `validate` command (e.g. an output
  format/option).

## Out of scope

- The Markdown report (separate issue).
- The validation rules and findings model themselves (prior issues).
- RO-Crate generation.

## Acceptance criteria

- [ ] A JSON report is produced from findings with a documented, stable schema.
- [ ] Output is deterministic and includes a severity summary.
- [ ] The report is reachable from the `validate` command.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

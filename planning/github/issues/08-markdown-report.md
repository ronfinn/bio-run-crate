## Problem

People reviewing a run's metadata need a readable summary, not raw JSON. A
Markdown report renders the same findings model into a human-friendly document
suitable for pull-request comments, review notes, or archival alongside a crate.
It complements the JSON report, sharing the same underlying findings so the two
never disagree.

## Scope

- Render a run's findings into a Markdown report: a summary section with counts
  by severity, followed by grouped findings showing rule ID, severity, message,
  and location.
- Produce deterministic output so reports are diffable.
- Expose the Markdown report through the `validate` command (e.g. an output
  format/option), reusing the same findings as the JSON reporter.

## Out of scope

- The JSON report (separate issue).
- The validation rules and findings model themselves (prior issues).
- RO-Crate generation.
- Any rendering that requires network access or external services.

## Acceptance criteria

- [ ] A Markdown report is produced from findings with a summary and grouped detail.
- [ ] Output is deterministic and derived from the same findings as the JSON report.
- [ ] The report is reachable from the `validate` command.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

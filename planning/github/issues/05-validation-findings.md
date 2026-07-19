## Problem

Validation results must be structured, addressable, and serialisable so they
can drive both machine-readable and human-readable reports and be referenced in
external audit records. A shared findings model — with stable rule identifiers
and ERROR/WARNING/INFO severities — is the common currency between the rule
engine and the reporters. Without it, each reporter would invent its own ad hoc
result shape.

## Scope

- Define a typed `Finding` model with a stable rule identifier, severity
  (ERROR/WARNING/INFO), a human-readable message, and a location/context
  reference into the manifest.
- Define a result container aggregating findings for a run.
- Make findings fully JSON-serialisable and deterministically ordered.
- Establish the convention for stable, addressable rule IDs.

## Out of scope

- The concrete validation rules themselves (delivered via the YAML validation
  command and profile issues).
- Report formatting (JSON and Markdown reporters are separate issues).
- Any network access.

## Acceptance criteria

- [ ] A typed `Finding` model exists with a stable rule ID, severity, message, and location.
- [ ] Findings are JSON-serialisable and produced in deterministic order.
- [ ] Severities are limited to ERROR, WARNING, and INFO.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

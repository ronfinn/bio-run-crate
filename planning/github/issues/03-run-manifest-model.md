## Problem

Validation needs a precise, typed definition of what a run manifest contains.
A generic, modality-agnostic `RunManifest` model gives the tool an explicit
schema to parse YAML into and to validate against, and forms the foundation for
later modality profiles. Without typed models the rules would depend on
untyped dictionaries, which is fragile and hard to check with mypy.

## Scope

- Define Pydantic models for the generic run manifest (as in
  `docs/data-model.md` Part A): the run, its inputs, parameters, outputs, and
  associated agents/software.
- Keep the core model modality-agnostic; no sequencing- or imaging-specific
  fields in the core.
- Make models strictly typed and JSON-serialisable.
- Reject unknown fields or capture them explicitly, without silently mutating
  input.

## Out of scope

- Modality-specific profile fields (handled by profile issues).
- The YAML parsing command wiring (separate issue).
- Validation rules and findings (separate issue).
- Report generation and RO-Crate generation.

## Acceptance criteria

- [ ] A typed `RunManifest` model and its sub-models exist and match `docs/data-model.md` Part A.
- [ ] The core model contains no modality-specific fields.
- [ ] Models are JSON-serialisable and pass mypy under strict settings.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

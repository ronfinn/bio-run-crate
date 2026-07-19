## Problem

Tests, examples, and documentation all need manifest data to work against, but
the project must never contain real sample IDs, organisation names, or internal
URLs. A small library of clearly synthetic manifests — both valid and
deliberately invalid — gives every downstream feature (validation, findings,
reports, RO-Crate generation) stable fixtures to exercise, while keeping the
repository public-safe.

## Scope

- Add at least one valid synthetic manifest exercising the full generic model.
- Add several invalid synthetic manifests, each triggering a distinct failure
  (missing required field, wrong type, inconsistent references, etc.).
- Use `example.org` domains and invented identifiers throughout.
- Store example manifests where the CLI usage docs reference them, and any
  test-only fixtures alongside the tests.

## Out of scope

- The validation rules that consume these manifests (separate issue).
- Real or anonymised production data of any kind.
- Modality-profile-specific fixtures beyond the generic model.

## Acceptance criteria

- [ ] At least one valid and several distinct invalid synthetic manifests exist.
- [ ] Each invalid manifest targets a specific, documented failure mode.
- [ ] All identifiers, domains, and paths are synthetic (`example.org`, invented IDs).
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

## Problem

The core model is deliberately modality-agnostic, but real runs carry
modality-specific metadata that the core cannot check. Per ADR-0003, such
behaviour belongs in optional profiles. A spatial-transcriptomics profile
demonstrates the extension mechanism end to end: adding modality-specific fields
and rules without touching the modality-agnostic core.

## Scope

- Implement a spatial-transcriptomics profile as an optional extension
  registered through the profile mechanism (ADR-0003).
- Add profile-specific fields and validation rules with their own stable rule
  IDs, layered on top of the core validation.
- Provide synthetic valid and invalid spatial-transcriptomics manifests for
  tests.
- Document how to select and apply the profile.

## Out of scope

- Any other modality profile (sequencing, imaging, mass spec, etc.).
- Changes to the modality-agnostic core model or core rules beyond the extension
  hooks.
- Automatic ontology lookup or external term resolution.

## Acceptance criteria

- [ ] A spatial-transcriptomics profile is implemented via the profile mechanism (ADR-0003).
- [ ] Profile rules have stable IDs and run in addition to the core rules.
- [ ] Synthetic valid and invalid spatial manifests exercise the profile.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

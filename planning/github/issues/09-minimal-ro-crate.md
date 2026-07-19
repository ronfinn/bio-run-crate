## Problem

A validated run should be packageable in a portable, standards-based format for
archiving or sharing. Building a minimal RO-Crate 1.2 package from a manifest —
using `ro-crate-py`, per ADR-0002 — delivers the packaging half of the tool's
purpose. Without this, the tool only validates and never produces the crate that
gives the project its name.

## Scope

- Create a minimal RO-Crate 1.2 package from a validated `RunManifest` using
  `ro-crate-py`.
- Represent the run, its inputs, parameters, and outputs as crate entities with
  appropriate types.
- Write a well-formed `ro-crate-metadata.json` targeting RO-Crate 1.2.
- Produce deterministic crate contents where practical, and never fabricate
  metadata not present in the manifest.

## Out of scope

- Importing or enriching an existing nf-prov crate (separate issue).
- Modality-profile-specific crate entities (separate issue).
- Uploading, publishing, or any cloud/network operation.

## Acceptance criteria

- [ ] A minimal RO-Crate 1.2 package is generated from a synthetic manifest via `ro-crate-py`.
- [ ] `ro-crate-metadata.json` is well-formed and declares RO-Crate 1.2.
- [ ] Crate contents are deterministic where practical and contain no fabricated metadata.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes

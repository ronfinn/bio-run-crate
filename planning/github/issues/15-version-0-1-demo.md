## Problem

Milestone 0 succeeds only if the pieces work together as one coherent flow. A
version 0.1 demonstration ties validation, reporting, and RO-Crate generation
into a single reproducible scenario that proves the MVP's success criteria and
gives reviewers a concrete artifact to evaluate before tagging v0.1.0.

## Scope

- Assemble a reproducible demonstration that runs against a synthetic manifest
  end to end: validate, emit JSON and Markdown reports, and generate a minimal
  RO-Crate 1.2 package.
- Provide the exact commands and expected outputs so the demo is repeatable.
- Confirm all `CLAUDE.md` checks (tests, lint, format, type) pass for the
  demonstrated state.
- Summarise how the demo maps to the charter's Milestone 0 success criteria.

## Out of scope

- Publishing a release, tagging, or changing repository visibility (requires
  explicit maintainer action).
- nf-prov enrichment and modality profiles beyond what is demonstrated.
- Any real or non-synthetic data.

## Acceptance criteria

- [ ] A reproducible v0.1 demo runs validation, both reports, and crate generation on synthetic input.
- [ ] Exact commands and expected outputs are documented.
- [ ] The demo maps explicitly to the Milestone 0 success criteria.
- [ ] Expected behaviour is implemented
- [ ] Tests are present where relevant
- [ ] Documentation is updated
- [ ] Only synthetic or public-safe examples are included
- [ ] No private data, credentials, internal URLs or personal email addresses are included
- [ ] Ruff passes
- [ ] Mypy passes
- [ ] Pytest passes
